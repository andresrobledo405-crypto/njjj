from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import mimetypes
from pathlib import Path
import secrets
import sqlite3
from typing import Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .config import APP_NAME, MAX_UPLOAD_BYTES, UPLOAD_DIR
from .db import get_db, init_db
from .exporters import CsvExporter

STATIC_DIR = Path(__file__).parent / "static"
STATUSES = {"scheduled", "arrived", "done", "cancelled", "no_show"}
METHODS = {"cash", "card", "transfer", "insurance"}
ACTIVE_STATUSES = ("scheduled", "arrived")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=f"{APP_NAME} - Gestión clínica", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "same-origin"
        return response


app.add_middleware(SecurityHeadersMiddleware)


class PatientIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    rut: str | None = Field(default=None, max_length=20)
    birth_date: str | None = Field(default=None, max_length=10)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=160)
    insurance: str | None = Field(default=None, max_length=80)
    allergies: str | None = Field(default=None, max_length=300)
    active: bool = True


class ProfessionalIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    specialty: str = Field(min_length=1, max_length=80)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=160)
    active: bool = True


class PaymentIn(BaseModel):
    patient_id: int
    appointment_id: int | None = None
    concept: str = Field(min_length=1, max_length=160)
    amount: int = Field(ge=0)
    method: str = "cash"


class AppointmentIn(BaseModel):
    patient_id: int
    professional_id: int
    starts_at: str = Field(min_length=16, max_length=19)  # YYYY-MM-DDTHH:MM
    duration_min: int = Field(default=30, ge=5, le=480)
    room: str | None = Field(default=None, max_length=40)
    reason: str | None = Field(default=None, max_length=200)
    status: str = "scheduled"


def row_dict(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    if "active" in result:
        result["active"] = bool(result["active"])
    return result


def normalize_rut(rut: str | None) -> str | None:
    if rut is None:
        return None
    cleaned = "".join(ch for ch in rut.upper() if ch.isalnum())
    if not cleaned:
        return None
    return f"{cleaned[:-1]}-{cleaned[-1]}" if len(cleaned) > 1 else cleaned


def parse_start(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise HTTPException(422, "Fecha/hora inválida (use AAAA-MM-DDTHH:MM)") from error


def bind(values: dict[str, Any], columns: tuple[str, ...]) -> tuple:
    return tuple(int(values[c]) if isinstance(values[c], bool) else values[c] for c in columns)


def crud_router(table: str, model: type[BaseModel], columns: tuple[str, ...], before_save=None):
    """CRUD pequeño y consistente para una tabla. `before_save` puede validar/normalizar."""
    prefix = f"/api/{table}"

    def prepare(payload: BaseModel, db: sqlite3.Connection, item_id: int | None = None) -> dict:
        values = payload.model_dump()
        if before_save:
            before_save(values, db, item_id)
        return values

    @app.get(prefix)
    def list_items(db: sqlite3.Connection = Depends(get_db)) -> list[dict[str, Any]]:
        return [row_dict(r) for r in db.execute(f"SELECT * FROM {table} ORDER BY id DESC")]

    @app.get(f"{prefix}/{{item_id}}")
    def get_item(item_id: int, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
        row = db.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Registro no encontrado")
        return row_dict(row)

    @app.post(prefix, status_code=201)
    def create_item(payload: model, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:  # type: ignore[valid-type]
        values = prepare(payload, db)
        try:
            cursor = db.execute(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
                bind(values, columns),
            )
            db.commit()
        except sqlite3.IntegrityError as error:
            raise HTTPException(409, f"Registro duplicado o referencia inválida: {error}") from error
        return row_dict(db.execute(f"SELECT * FROM {table} WHERE id = ?", (cursor.lastrowid,)).fetchone())

    @app.put(f"{prefix}/{{item_id}}")
    def update_item(item_id: int, payload: model, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:  # type: ignore[valid-type]
        values = prepare(payload, db, item_id)
        assignments = ", ".join(f"{c} = ?" for c in columns)
        try:
            cursor = db.execute(
                f"UPDATE {table} SET {assignments} WHERE id = ?", bind(values, columns) + (item_id,)
            )
            db.commit()
        except sqlite3.IntegrityError as error:
            raise HTTPException(409, f"Registro duplicado o referencia inválida: {error}") from error
        if cursor.rowcount == 0:
            raise HTTPException(404, "Registro no encontrado")
        return row_dict(db.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone())

    @app.delete(f"{prefix}/{{item_id}}", status_code=204)
    def delete_item(item_id: int, db: sqlite3.Connection = Depends(get_db)) -> None:
        try:
            cursor = db.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
            db.commit()
        except sqlite3.IntegrityError as error:
            raise HTTPException(409, "Tiene registros asociados; desactívelo en vez de borrarlo") from error
        if cursor.rowcount == 0:
            raise HTTPException(404, "Registro no encontrado")


def patient_rules(values: dict, db: sqlite3.Connection, item_id: int | None) -> None:
    values["rut"] = normalize_rut(values["rut"])


def payment_rules(values: dict, db: sqlite3.Connection, item_id: int | None) -> None:
    if values["method"] not in METHODS:
        raise HTTPException(422, "Medio de pago no válido")


def appointment_rules(values: dict, db: sqlite3.Connection, item_id: int | None) -> None:
    if values["status"] not in STATUSES:
        raise HTTPException(422, "Estado no válido")
    start = parse_start(values["starts_at"])
    values["starts_at"] = start.strftime("%Y-%m-%dT%H:%M")
    if values["status"] in ("cancelled", "no_show"):
        return
    end = start + timedelta(minutes=values["duration_min"])
    rows = db.execute(
        """SELECT id, starts_at, duration_min, room, professional_id, patient_id FROM appointments
           WHERE status IN ('scheduled','arrived') AND date(starts_at) = date(?) AND id IS NOT ?""",
        (values["starts_at"], item_id),
    )
    for row in rows:
        other_start = datetime.fromisoformat(row["starts_at"])
        other_end = other_start + timedelta(minutes=row["duration_min"])
        if not (start < other_end and other_start < end):
            continue
        if row["professional_id"] == values["professional_id"]:
            raise HTTPException(409, "El profesional ya tiene una cita en ese horario")
        if row["patient_id"] == values["patient_id"]:
            raise HTTPException(409, "El paciente ya tiene una cita en ese horario")
        if values["room"] and row["room"] == values["room"]:
            raise HTTPException(409, "La sala ya está ocupada en ese horario")


crud_router("patients", PatientIn, ("name", "rut", "birth_date", "phone", "email", "insurance", "allergies", "active"), patient_rules)
crud_router("professionals", ProfessionalIn, ("name", "specialty", "phone", "email", "active"))
crud_router("appointments", AppointmentIn, ("patient_id", "professional_id", "starts_at", "duration_min", "room", "reason", "status"), appointment_rules)
crud_router("payments", PaymentIn, ("patient_id", "appointment_id", "concept", "amount", "method"), payment_rules)


@app.get("/api/agenda")
def agenda(
    day: str | None = Query(default=None, description="AAAA-MM-DD; por defecto hoy"),
    professional_id: int | None = None,
    db: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    day = day or datetime.now().strftime("%Y-%m-%d")
    sql = """SELECT a.*, p.name AS patient_name, p.allergies, pr.name AS professional_name, pr.specialty
             FROM appointments a
             JOIN patients p ON p.id = a.patient_id
             JOIN professionals pr ON pr.id = a.professional_id
             WHERE date(a.starts_at) = date(?)"""
    params: list[Any] = [day]
    if professional_id is not None:
        sql += " AND a.professional_id = ?"
        params.append(professional_id)
    return [row_dict(r) for r in db.execute(sql + " ORDER BY a.starts_at", params)]


@app.post("/api/appointments/{appointment_id}/status")
def set_status(appointment_id: int, status: str = Form(...), db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    if status not in STATUSES:
        raise HTTPException(422, "Estado no válido")
    cursor = db.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
    db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(404, "Cita no encontrada")
    return row_dict(db.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,)).fetchone())


CONSULTATION_SELECT = """SELECT c.*, p.name AS patient_name, pr.name AS professional_name
    FROM consultations c JOIN patients p ON p.id = c.patient_id
    JOIN professionals pr ON pr.id = c.professional_id"""


@app.get("/api/consultations")
def list_consultations(
    patient_id: int | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    db: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    sql, params = CONSULTATION_SELECT, []
    if patient_id is not None:
        sql += " WHERE c.patient_id = ?"
        params.append(patient_id)
    return [row_dict(r) for r in db.execute(sql + " ORDER BY c.occurred_at DESC, c.id DESC LIMIT ?", (*params, limit))]


@app.post("/api/consultations", status_code=201)
async def create_consultation(
    patient_id: int = Form(...),
    professional_id: int = Form(...),
    appointment_id: int | None = Form(None),
    diagnosis: str | None = Form(None),
    treatment: str | None = Form(None),
    notes: str | None = Form(None),
    attachment: UploadFile | None = File(None),
    db: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    stored: str | None = None
    if attachment and attachment.filename:
        extension = Path(attachment.filename).suffix.lower()
        if extension not in {".jpg", ".jpeg", ".png", ".webp", ".pdf"}:
            raise HTTPException(415, "Solo se aceptan JPG, PNG, WEBP o PDF")
        content = await attachment.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(413, "El archivo excede el tamaño máximo permitido")
        stored = f"{datetime.now(timezone.utc):%Y%m%d%H%M%S}_{secrets.token_hex(8)}{extension}"
        (UPLOAD_DIR / stored).write_bytes(content)
    try:
        cursor = db.execute(
            """INSERT INTO consultations (patient_id, professional_id, appointment_id, diagnosis, treatment, notes, attachment_path)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (patient_id, professional_id, appointment_id, diagnosis, treatment, notes, stored),
        )
        if appointment_id is not None:
            db.execute("UPDATE appointments SET status = 'done' WHERE id = ?", (appointment_id,))
        db.commit()
    except sqlite3.IntegrityError as error:
        if stored:
            (UPLOAD_DIR / stored).unlink(missing_ok=True)
        raise HTTPException(409, f"Referencia inválida: {error}") from error
    return row_dict(db.execute(CONSULTATION_SELECT + " WHERE c.id = ?", (cursor.lastrowid,)).fetchone())


@app.get("/api/consultations/{consultation_id}/attachment")
def get_attachment(consultation_id: int, db: sqlite3.Connection = Depends(get_db)) -> FileResponse:
    row = db.execute("SELECT attachment_path FROM consultations WHERE id = ?", (consultation_id,)).fetchone()
    if row is None or not row["attachment_path"]:
        raise HTTPException(404, "Adjunto no encontrado")
    path = (UPLOAD_DIR / row["attachment_path"]).resolve()
    if path.parent != UPLOAD_DIR.resolve() or not path.is_file():
        raise HTTPException(404, "Adjunto no encontrado")
    return FileResponse(path, media_type=mimetypes.guess_type(path.name)[0] or "application/octet-stream")


@app.get("/api/dashboard")
def dashboard(db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    def count(sql: str) -> int:
        return db.execute(sql).fetchone()[0]

    today = "date(starts_at) = date('now','localtime')"
    return {
        "patients": count("SELECT COUNT(*) FROM patients WHERE active = 1"),
        "professionals": count("SELECT COUNT(*) FROM professionals WHERE active = 1"),
        "today_appointments": count(f"SELECT COUNT(*) FROM appointments WHERE {today} AND status NOT IN ('cancelled','no_show')"),
        "today_done": count(f"SELECT COUNT(*) FROM appointments WHERE {today} AND status = 'done'"),
        "today_pending": count(f"SELECT COUNT(*) FROM appointments WHERE {today} AND status IN ('scheduled','arrived')"),
        "month_revenue": count(
            "SELECT COALESCE(SUM(amount),0) FROM payments WHERE strftime('%Y-%m', paid_at) = strftime('%Y-%m','now','localtime')"
        ),
    }


def csv_response(db: sqlite3.Connection, sql: str, filename: str) -> StreamingResponse:
    stream = CsvExporter().export(db.execute(sql))
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/api/export/appointments.csv")
def export_appointments(db: sqlite3.Connection = Depends(get_db)) -> StreamingResponse:
    return csv_response(
        db,
        """SELECT a.id, a.starts_at, a.duration_min, p.name AS paciente, p.rut, pr.name AS profesional,
                  pr.specialty AS especialidad, a.room AS sala, a.reason AS motivo, a.status AS estado
           FROM appointments a JOIN patients p ON p.id = a.patient_id
           JOIN professionals pr ON pr.id = a.professional_id ORDER BY a.starts_at DESC""",
        "citas.csv",
    )


@app.get("/api/export/payments.csv")
def export_payments(db: sqlite3.Connection = Depends(get_db)) -> StreamingResponse:
    return csv_response(
        db,
        """SELECT y.id, y.paid_at, p.name AS paciente, y.concept AS concepto, y.amount AS monto, y.method AS medio
           FROM payments y JOIN patients p ON p.id = y.patient_id ORDER BY y.paid_at DESC""",
        "pagos.csv",
    )


@app.get("/", response_class=HTMLResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
