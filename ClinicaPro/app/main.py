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

import os
import time
import unicodedata

from fastapi.responses import JSONResponse, Response

from .auth import SESSION_COOKIE, SESSION_SECONDS, hash_password, make_token, read_token, throttle, verify_password
from .config import APP_NAME, DATA_DIR, MAX_UPLOAD_BYTES, UPLOAD_DIR
from .db import get_connection, get_db, init_db
from .exporters import CsvExporter

STATIC_DIR = Path(__file__).parent / "static"
STATUSES = {"scheduled", "arrived", "done", "cancelled", "no_show"}
METHODS = {"cash", "card", "transfer", "insurance"}
ACTIVE_STATUSES = ("scheduled", "arrived")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    connection = get_connection()
    try:
        bootstrap_admin(connection)
    finally:
        connection.close()
    yield


def bootstrap_admin(db: sqlite3.Connection) -> None:
    """Crea el administrador inicial si no hay usuarios. La clave sale del entorno o se genera."""
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        return
    username = os.getenv("CLINICAPRO_ADMIN_USER", "admin")
    password = os.getenv("CLINICAPRO_ADMIN_PASSWORD")
    if not password:
        password = secrets.token_urlsafe(12)
        (DATA_DIR / "admin_inicial.txt").write_text(f"usuario: {username}\nclave: {password}\n(cámbiela al ingresar y borre este archivo)\n")
    db.execute("INSERT INTO users (username, name, password_hash, role) VALUES (?, ?, ?, 'admin')",
               (username, "Administrador", hash_password(password)))
    db.commit()


app = FastAPI(title=f"{APP_NAME} - Gestión clínica", version="2.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "same-origin"
        return response


PUBLIC_PATHS = {"/api/auth/login", "/api/health", "/api/meta"}


class AuthMiddleware(BaseHTTPMiddleware):
    """Todo lo que cuelga de /api y la documentación exige sesión válida."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        protected = path.startswith(("/api", "/docs", "/redoc", "/openapi"))
        request.state.user = read_token(request.cookies.get(SESSION_COOKIE))
        if protected and path not in PUBLIC_PATHS and request.state.user is None:
            return JSONResponse({"detail": "Sesión requerida"}, status_code=401)
        return await call_next(request)


app.add_middleware(AuthMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


def admin_only(request: Request) -> dict:
    user = request.state.user
    if not user or user["r"] != "admin":
        raise HTTPException(403, "Solo el administrador puede hacer esto")
    return user


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/meta")
def meta() -> dict[str, Any]:
    return {"name": APP_NAME}


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=1, max_length=200)


@app.post("/api/auth/login")
def login(payload: LoginIn, request: Request, db: sqlite3.Connection = Depends(get_db)) -> Response:
    key = (payload.username.lower(), request.client.host if request.client else "-")
    if throttle.blocked(key):
        raise HTTPException(429, "Demasiados intentos; espere 5 minutos")
    row = db.execute("SELECT * FROM users WHERE username = ? AND active = 1", (payload.username,)).fetchone()
    if row is None or not verify_password(payload.password, row["password_hash"]):
        throttle.fail(key)
        raise HTTPException(401, "Usuario o clave incorrectos")
    throttle.reset(key)
    user = {"id": row["id"], "username": row["username"], "role": row["role"], "name": row["name"]}
    response = JSONResponse(user)
    response.set_cookie(SESSION_COOKIE, make_token(user), max_age=SESSION_SECONDS, httponly=True, samesite="strict",
                        secure=os.getenv("CLINICAPRO_COOKIE_SECURE") == "1")
    return response


@app.post("/api/auth/logout")
def logout() -> Response:
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/api/auth/me")
def me(request: Request, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    row = db.execute("SELECT id, username, name, role FROM users WHERE id = ? AND active = 1", (request.state.user["id"],)).fetchone()
    if row is None:
        raise HTTPException(401, "Sesión requerida")
    return dict(row)


class PasswordIn(BaseModel):
    current: str
    new: str = Field(min_length=10, max_length=200)


@app.post("/api/auth/password")
def change_password(payload: PasswordIn, request: Request, db: sqlite3.Connection = Depends(get_db)) -> dict[str, bool]:
    row = db.execute("SELECT * FROM users WHERE id = ?", (request.state.user["id"],)).fetchone()
    if row is None or not verify_password(payload.current, row["password_hash"]):
        raise HTTPException(403, "La clave actual no coincide")
    db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(payload.new), row["id"]))
    db.commit()
    return {"ok": True}


class UserIn(BaseModel):
    username: str = Field(min_length=3, max_length=60, pattern=r"^[A-Za-z0-9_.@-]+$")
    name: str = Field(min_length=1, max_length=120)
    password: str | None = Field(default=None, min_length=10, max_length=200)
    role: str = "profesional"
    active: bool = True


def _admins_left(db: sqlite3.Connection, excluding: int) -> int:
    return db.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND active=1 AND id != ?", (excluding,)).fetchone()[0]


@app.get("/api/users")
def list_users(request: Request, db: sqlite3.Connection = Depends(get_db)) -> list[dict[str, Any]]:
    admin_only(request)
    return [row_dict(r) for r in db.execute("SELECT id, username, name, role, active, created_at FROM users ORDER BY id")]


@app.post("/api/users", status_code=201)
def create_user(payload: UserIn, request: Request, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    admin_only(request)
    if payload.role not in ("admin", "profesional") or not payload.password:
        raise HTTPException(422, "Rol no válido o clave faltante (mínimo 10 caracteres)")
    try:
        cursor = db.execute("INSERT INTO users (username, name, password_hash, role, active) VALUES (?,?,?,?,?)",
                            (payload.username, payload.name, hash_password(payload.password), payload.role, int(payload.active)))
        db.commit()
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "Ese usuario ya existe") from error
    return row_dict(db.execute("SELECT id, username, name, role, active FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone())


@app.put("/api/users/{user_id}")
def update_user(user_id: int, payload: UserIn, request: Request, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    admin_only(request)
    if payload.role not in ("admin", "profesional"):
        raise HTTPException(422, "Rol no válido")
    if (payload.role != "admin" or not payload.active) and _admins_left(db, user_id) == 0:
        raise HTTPException(409, "Debe quedar al menos un administrador activo")
    sets, params = ["username=?", "name=?", "role=?", "active=?"], [payload.username, payload.name, payload.role, int(payload.active)]
    if payload.password:
        sets.append("password_hash=?")
        params.append(hash_password(payload.password))
    try:
        cursor = db.execute(f"UPDATE users SET {', '.join(sets)} WHERE id=?", (*params, user_id))
        db.commit()
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "Ese usuario ya existe") from error
    if cursor.rowcount == 0:
        raise HTTPException(404, "Usuario no encontrado")
    return row_dict(db.execute("SELECT id, username, name, role, active FROM users WHERE id = ?", (user_id,)).fetchone())


@app.delete("/api/users/{user_id}", status_code=204)
def delete_user(user_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)) -> None:
    admin_only(request)
    if _admins_left(db, user_id) == 0:
        raise HTTPException(409, "Debe quedar al menos un administrador activo")
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()


def fold(text: str | None) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", (text or "").lower()) if unicodedata.category(c) != "Mn")


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



# ---------- Documentos y protocolos de la clínica (módulo opcional, sin contenido precargado) ----------
DOC_CATEGORIES = {"protocolo": "Protocolo", "consentimiento": "Consentimiento", "tarifas": "Tarifas", "otro": "Otro"}


class DocumentIn(BaseModel):
    category: str = "protocolo"
    title: str = Field(min_length=1, max_length=160)
    content: str | None = Field(default=None, max_length=20000)


def _check_doc(payload: DocumentIn) -> None:
    if payload.category not in DOC_CATEGORIES:
        raise HTTPException(422, "Categoría no válida")


@app.get("/api/documents")
def documents_list(q: str | None = None, category: str | None = None, db: sqlite3.Connection = Depends(get_db)) -> list[dict[str, Any]]:
    sql, params = "SELECT * FROM documents WHERE 1=1", []
    if category:
        sql, params = sql + " AND category = ?", [category]
    rows = [dict(r) for r in db.execute(sql + " ORDER BY category, title", params)]
    if q:
        terms = fold(q).split()
        rows = [r for r in rows if all(t in fold(f"{r['title']} {r['content'] or ''}") for t in terms)]
    return rows


@app.get("/api/documents/{doc_id}")
def documents_get(doc_id: int, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    row = db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Documento no encontrado")
    return dict(row)


@app.post("/api/documents", status_code=201)
def documents_create(payload: DocumentIn, request: Request, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    admin_only(request)
    _check_doc(payload)
    try:
        cursor = db.execute("INSERT INTO documents (category, title, content) VALUES (?,?,?)", (payload.category, payload.title, payload.content))
        db.commit()
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "Ya existe un documento con ese título") from error
    return dict(db.execute("SELECT * FROM documents WHERE id = ?", (cursor.lastrowid,)).fetchone())


@app.put("/api/documents/{doc_id}")
def documents_update(doc_id: int, payload: DocumentIn, request: Request, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    admin_only(request)
    _check_doc(payload)
    try:
        cursor = db.execute("UPDATE documents SET category=?, title=?, content=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                            (payload.category, payload.title, payload.content, doc_id))
        db.commit()
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "Ya existe un documento con ese título") from error
    if cursor.rowcount == 0:
        raise HTTPException(404, "Documento no encontrado")
    return dict(db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone())


@app.delete("/api/documents/{doc_id}", status_code=204)
def documents_delete(doc_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)) -> None:
    admin_only(request)
    if db.execute("DELETE FROM documents WHERE id = ?", (doc_id,)).rowcount == 0:
        raise HTTPException(404, "Documento no encontrado")
    db.commit()


# ---------- Recordatorios de citas (solo genera el texto; la clínica lo envía a mano) ----------
def reminder_text(clinic: str, name: str, starts_at: str, professional: str) -> str:
    start = datetime.fromisoformat(starts_at)
    return (f"Hola {name.split()[0]}, le recordamos su cita en {clinic} el {start:%d-%m-%Y} a las {start:%H:%M} "
            f"con {professional}. Si no puede asistir, avísenos con anticipación. ¡Gracias!")


@app.get("/api/reminders")
def reminders(day: str | None = Query(default=None, description="AAAA-MM-DD; por defecto mañana"),
              db: sqlite3.Connection = Depends(get_db)) -> list[dict[str, Any]]:
    day = day or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    rows = db.execute(
        """SELECT a.id, a.starts_at, a.room, p.name AS patient_name, p.phone, pr.name AS professional_name
           FROM appointments a JOIN patients p ON p.id = a.patient_id JOIN professionals pr ON pr.id = a.professional_id
           WHERE date(a.starts_at) = date(?) AND a.status IN ('scheduled','arrived') ORDER BY a.starts_at""", (day,))
    out = []
    for r in rows:
        item = dict(r)
        item["message"] = reminder_text(APP_NAME, r["patient_name"], r["starts_at"], r["professional_name"])
        digits = "".join(ch for ch in (r["phone"] or "") if ch.isdigit())
        if digits.startswith("0"):
            digits = digits.lstrip("0")
        if digits and len(digits) <= 9:  # número local chileno sin código de país
            digits = "56" + digits
        item["whatsapp_url"] = f"https://wa.me/{digits}" if digits else None
        out.append(item)
    return out


# ---------- Ficha de paciente con historial ----------
@app.get("/api/patients/{patient_id}/history")
def patient_history(patient_id: int, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if patient is None:
        raise HTTPException(404, "Paciente no encontrado")
    appts = db.execute(
        """SELECT a.id, a.starts_at, a.status, a.reason, a.room, pr.name AS professional_name, pr.specialty
           FROM appointments a JOIN professionals pr ON pr.id = a.professional_id
           WHERE a.patient_id = ? ORDER BY a.starts_at DESC""", (patient_id,))
    cons = db.execute(CONSULTATION_SELECT + " WHERE c.patient_id = ? ORDER BY c.occurred_at DESC, c.id DESC", (patient_id,))
    pays = db.execute("SELECT id, concept, amount, method, paid_at FROM payments WHERE patient_id = ? ORDER BY paid_at DESC, id DESC", (patient_id,))
    payments = [dict(r) for r in pays]
    return {"patient": row_dict(patient), "appointments": [dict(r) for r in appts],
            "consultations": [row_dict(r) for r in cons], "payments": payments,
            "total_paid": sum(p["amount"] for p in payments)}


# ---------- Reporte de caja ----------
@app.get("/api/reports/cash")
def cash_report(period: str = Query(default="day", pattern="^(day|month)$"),
                date: str | None = Query(default=None, description="AAAA-MM-DD (día) o AAAA-MM (mes); por defecto hoy/este mes"),
                db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    now = datetime.now()
    if period == "day":
        date = date or now.strftime("%Y-%m-%d")
        fmt, value = "%Y-%m-%d", date
    else:
        date = (date or now.strftime("%Y-%m"))[:7]
        fmt, value = "%Y-%m", date
    try:
        datetime.strptime(value, fmt)
    except ValueError as error:
        raise HTTPException(422, "Fecha inválida") from error
    rows = db.execute(f"SELECT method, COUNT(*) AS n, SUM(amount) AS total FROM payments WHERE strftime('{fmt}', paid_at) = ? GROUP BY method", (value,))
    by_method = {r["method"]: {"count": r["n"], "total": r["total"]} for r in rows}
    items = db.execute(
        f"""SELECT y.id, y.paid_at, y.concept, y.amount, y.method, p.name AS patient_name FROM payments y
            JOIN patients p ON p.id = y.patient_id WHERE strftime('{fmt}', y.paid_at) = ? ORDER BY y.paid_at""", (value,))
    return {"period": period, "date": value, "total": sum(m["total"] for m in by_method.values()),
            "count": sum(m["count"] for m in by_method.values()), "by_method": by_method, "payments": [dict(r) for r in items]}


@app.get("/sw.js", include_in_schema=False)
def service_worker() -> FileResponse:
    return FileResponse(STATIC_DIR / "sw.js", media_type="application/javascript", headers={"Service-Worker-Allowed": "/"})


@app.get("/", response_class=HTMLResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
