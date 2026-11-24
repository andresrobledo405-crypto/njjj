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
import re
import time
import unicodedata

import httpx

from fastapi.responses import JSONResponse, Response

from .auth import SESSION_COOKIE, SESSION_SECONDS, hash_password, make_token, read_token, throttle, verify_password
from .config import APP_NAME, DATA_DIR, MAX_UPLOAD_BYTES, UPLOAD_DIR
from .db import get_connection, get_db, init_db
from .exporters import CsvExporter
from .kine import enrich_consultations, parse_ids, parse_measurements, refresh_plan_status, register as register_kine, save_consultation_extras
from .library import CATEGORIES, seed_library

STATIC_DIR = Path(__file__).parent / "static"
STATUSES = {"scheduled", "arrived", "done", "cancelled", "no_show"}
METHODS = {"cash", "card", "transfer", "insurance"}
ACTIVE_STATUSES = ("scheduled", "arrived")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    connection = get_connection()
    try:
        seed_library(connection)
        bootstrap_admin(connection)
    finally:
        connection.close()
    yield


def bootstrap_admin(db: sqlite3.Connection) -> None:
    """Crea el administrador inicial si no hay usuarios. La clave sale del entorno o se genera."""
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        return
    username = os.getenv("KINEPRO_ADMIN_USER", "admin")
    password = os.getenv("KINEPRO_ADMIN_PASSWORD")
    if not password:
        password = secrets.token_urlsafe(12)
        (DATA_DIR / "admin_inicial.txt").write_text(f"usuario: {username}\nclave: {password}\n(cámbiela al ingresar y borre este archivo)\n")
    db.execute("INSERT INTO users (username, name, password_hash, role) VALUES (?, ?, ?, 'admin')",
               (username, "Administrador", hash_password(password)))
    db.commit()


app = FastAPI(title=f"{APP_NAME} - Gestión para kinesiólogos", version="1.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "same-origin"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=15552000; includeSubDomains"
        response.headers["Content-Security-Policy"] = ("default-src 'self'; script-src 'self'; "
                                                       "style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'self'")
        return response


SENSITIVE_GET = re.compile(r"^/api/(patients/\d+|plans/\d+(/report)?|consultations(/\d+/attachment)?|export/[\w.]+|admin/backup|templates/\d+/print)$")


def audit(user: dict | None, method: str, path: str, status: int, username: str | None = None) -> None:
    """Registro de actividad (quién, qué, cuándo). No guarda contenido de fichas ni cuerpos de petición."""
    db = get_connection()
    try:
        db.execute("INSERT INTO audit_log (at, user_id, username, method, path, status) VALUES (?,?,?,?,?,?)",
                   (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user["id"] if user else None, (user or {}).get("u") or username, method, path, status))
        db.commit()
    finally:
        db.close()


PUBLIC_PATHS = {"/api/auth/login", "/api/health", "/api/meta"}


class AuthMiddleware(BaseHTTPMiddleware):
    """Todo lo que cuelga de /api y la documentación exige sesión válida."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        protected = path.startswith(("/api", "/docs", "/redoc", "/openapi"))
        user = read_token(request.cookies.get(SESSION_COOKIE))
        if user is not None:  # revalida contra la base: usuario desactivado o con otro rol pierde la sesión
            db = get_connection()
            try:
                row = db.execute("SELECT role FROM users WHERE id = ? AND active = 1", (user["id"],)).fetchone()
            finally:
                db.close()
            user = {**user, "r": row["role"]} if row else None
        request.state.user = user
        if protected and path not in PUBLIC_PATHS and request.state.user is None:
            return JSONResponse({"detail": "Sesión requerida"}, status_code=401)
        response = await call_next(request)
        if user is not None and path.startswith("/api") and path != "/api/admin/audit" and (
                request.method != "GET" or SENSITIVE_GET.match(path)):
            audit(user, request.method, path, response.status_code)
        return response


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
    return {"name": APP_NAME, "ask_enabled": bool(os.getenv("OPENAI_API_KEY"))}


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
        audit(None, "POST", "/api/auth/login", 401, payload.username[:60])
        raise HTTPException(401, "Usuario o clave incorrectos")
    throttle.reset(key)
    audit({"id": row["id"], "u": row["username"]}, "POST", "/api/auth/login", 200)
    user = {"id": row["id"], "username": row["username"], "role": row["role"], "name": row["name"]}
    response = JSONResponse(user)
    response.set_cookie(SESSION_COOKIE, make_token(user), max_age=SESSION_SECONDS, httponly=True, samesite="strict",
                        secure=os.getenv("KINEPRO_COOKIE_SECURE") == "1" or request.url.scheme == "https")
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


class LibraryIn(BaseModel):
    category: str
    region: str | None = Field(default=None, max_length=60)
    title: str = Field(min_length=1, max_length=160)
    summary: str | None = Field(default=None, max_length=400)
    content: str | None = Field(default=None, max_length=12000)
    precautions: str | None = Field(default=None, max_length=2000)
    tags: str | None = Field(default=None, max_length=300)


LIB_COLUMNS = ("category", "region", "title", "summary", "content", "precautions", "tags")


@app.get("/api/library/meta")
def library_meta(db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    counts = {r["category"]: r["n"] for r in db.execute("SELECT category, COUNT(*) AS n FROM library_items GROUP BY category")}
    regions = [r["region"] for r in db.execute("SELECT DISTINCT region FROM library_items WHERE region IS NOT NULL ORDER BY region")]
    return {"categories": [{"id": k, "label": v, "count": counts.get(k, 0)} for k, v in CATEGORIES.items()], "regions": regions,
            "total": sum(counts.values())}


@app.get("/api/library")
def library_search(q: str | None = None, category: str | None = None, region: str | None = None,
                   db: sqlite3.Connection = Depends(get_db)) -> list[dict[str, Any]]:
    sql, params = "SELECT * FROM library_items WHERE 1=1", []
    if category:
        sql, params = sql + " AND category = ?", [*params, category]
    if region:
        sql, params = sql + " AND region = ?", [*params, region]
    rows = [dict(r) for r in db.execute(sql + " ORDER BY category, title", params)]
    if q:
        terms = fold(q).split()
        def haystack(r): return fold(" ".join(str(r[c] or "") for c in ("title", "summary", "content", "tags", "region", "precautions")))
        def rank(r):
            title = fold(r["title"])
            return -sum(3 if t in title else 1 for t in terms)
        rows = sorted((r for r in rows if all(t in haystack(r) for t in terms)), key=rank)
    return rows


class AskIn(BaseModel):
    question: str = Field(min_length=5, max_length=500)


ASK_PROMPT = (
    "Eres un asistente de apoyo educativo para kinesiólogos. Responde en español, de forma breve y clara, "
    "usando EXCLUSIVAMENTE las entradas de la biblioteca entregadas como contexto. Si el contexto no alcanza "
    "para responder, dilo y sugiere consultar guías clínicas o a un especialista. No des diagnósticos ni "
    "indicaciones para un paciente concreto. Menciona siempre las precauciones y banderas rojas pertinentes. "
    "Cita las entradas usadas por su título entre corchetes."
)
ask_log: dict[int, list[float]] = {}
ASK_LIMIT_PER_HOUR = int(os.getenv("KINEPRO_ASK_LIMIT", "20"))


@app.post("/api/library/ask")
def library_ask(payload: AskIn, request: Request, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    """Pregunta a un modelo de OpenAI. Solo se envían la pregunta y entradas de la biblioteca; nunca datos de pacientes."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(503, "El asistente no está activado (falta OPENAI_API_KEY)")
    uid, now = request.state.user["id"], time.time()
    recent = [t for t in ask_log.get(uid, []) if now - t < 3600]
    if len(recent) >= ASK_LIMIT_PER_HOUR:
        raise HTTPException(429, "Límite de preguntas por hora alcanzado")
    ask_log[uid] = recent + [now]
    # recuperación: entradas que coinciden con más palabras de la pregunta
    words = [w for w in fold(payload.question).replace("?", " ").replace(",", " ").split() if len(w) > 3]
    scored = []
    for row in db.execute("SELECT * FROM library_items"):
        text = fold(" ".join(str(row[c] or "") for c in ("title", "summary", "content", "tags", "region")))
        title = fold(row["title"])
        score = sum((3 if w in title else 1) for w in words if w in text)
        if score:
            scored.append((score, dict(row)))
    top = [r for _, r in sorted(scored, key=lambda x: -x[0])[:6]]
    if not top:
        return {"answer": "No encontré información sobre eso en la biblioteca. Intente con otras palabras o consulte guías clínicas.", "sources": []}
    context = "\n\n".join(f"[{r['title']}]\n{r['summary'] or ''}\n{r['content'] or ''}\nPrecauciones: {r['precautions'] or '-'}" for r in top)
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"), "temperature": 0.2,
                  "messages": [{"role": "system", "content": ASK_PROMPT},
                               {"role": "user", "content": f"Contexto:\n{context}\n\nPregunta: {payload.question}"}]},
            timeout=40,
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as error:
        raise HTTPException(502, "El servicio de IA no respondió; intente más tarde") from error
    return {"answer": answer, "sources": [{"id": r["id"], "title": r["title"]} for r in top]}


@app.get("/api/library/{item_id}")
def library_get(item_id: int, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    row = db.execute("SELECT * FROM library_items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Entrada no encontrada")
    return dict(row)


def _check_category(payload: LibraryIn) -> None:
    if payload.category not in CATEGORIES:
        raise HTTPException(422, "Categoría no válida")


@app.post("/api/library", status_code=201)
def library_create(payload: LibraryIn, request: Request, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    admin_only(request)
    _check_category(payload)
    values = payload.model_dump()
    try:
        cursor = db.execute(f"INSERT INTO library_items ({', '.join(LIB_COLUMNS)}) VALUES ({', '.join('?' for _ in LIB_COLUMNS)})",
                            tuple(values[c] for c in LIB_COLUMNS))
        db.commit()
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "Ya existe una entrada con ese título en la categoría") from error
    return dict(db.execute("SELECT * FROM library_items WHERE id = ?", (cursor.lastrowid,)).fetchone())


@app.put("/api/library/{item_id}")
def library_update(item_id: int, payload: LibraryIn, request: Request, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
    admin_only(request)
    _check_category(payload)
    values = payload.model_dump()
    try:
        cursor = db.execute(f"UPDATE library_items SET {', '.join(f'{c}=?' for c in LIB_COLUMNS)} WHERE id=?",
                            (*(values[c] for c in LIB_COLUMNS), item_id))
        db.commit()
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "Ya existe una entrada con ese título en la categoría") from error
    if cursor.rowcount == 0:
        raise HTTPException(404, "Entrada no encontrada")
    return dict(db.execute("SELECT * FROM library_items WHERE id = ?", (item_id,)).fetchone())


@app.delete("/api/library/{item_id}", status_code=204)
def library_delete(item_id: int, request: Request, db: sqlite3.Connection = Depends(get_db)) -> None:
    admin_only(request)
    try:
        cursor = db.execute("DELETE FROM library_items WHERE id = ?", (item_id,))
        db.commit()
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "La entrada está enlazada a atenciones o plantillas; edítela en vez de borrarla") from error
    if cursor.rowcount == 0:
        raise HTTPException(404, "Entrada no encontrada")


class PatientIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    rut: str | None = Field(default=None, max_length=20)
    birth_date: str | None = Field(default=None, max_length=10)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=160)
    insurance: str | None = Field(default=None, max_length=80)
    allergies: str | None = Field(default=None, max_length=300)
    occupation: str | None = Field(default=None, max_length=120)
    history: str | None = Field(default=None, max_length=1500)  # antecedentes mórbidos, quirúrgicos, deportivos
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
    plan_id: int | None = None
    status: str = "scheduled"


MAGIC = {".pdf": (b"%PDF",), ".png": (b"\x89PNG\r\n\x1a\n",), ".jpg": (b"\xff\xd8\xff",), ".jpeg": (b"\xff\xd8\xff",)}


def looks_like(extension: str, content: bytes) -> bool:
    """Comprueba los primeros bytes (firma) para no aceptar otro tipo de archivo con extensión cambiada."""
    if extension == ".webp":
        return content[:4] == b"RIFF" and content[8:12] == b"WEBP"
    return content.startswith(MAGIC.get(extension, (b"",)))


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
    if values.get("plan_id") is not None:
        plan = db.execute("SELECT patient_id, status FROM treatment_plans WHERE id = ?", (values["plan_id"],)).fetchone()
        if plan is None or plan["patient_id"] != values["patient_id"]:
            raise HTTPException(422, "El plan no existe o pertenece a otro paciente")
        if plan["status"] != "active" and values["status"] in ("scheduled", "arrived"):
            raise HTTPException(409, "El plan no está activo")
    elif item_id is not None:  # PUT sin plan_id no debe desvincular la cita de su plan
        current = db.execute("SELECT plan_id FROM appointments WHERE id = ?", (item_id,)).fetchone()
        values["plan_id"] = current["plan_id"] if current else None
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


crud_router("patients", PatientIn, ("name", "rut", "birth_date", "phone", "email", "insurance", "allergies", "occupation", "history", "active"), patient_rules)
crud_router("professionals", ProfessionalIn, ("name", "specialty", "phone", "email", "active"))
crud_router("appointments", AppointmentIn, ("patient_id", "professional_id", "starts_at", "duration_min", "room", "reason", "plan_id", "status"), appointment_rules)
register_kine(app, appointment_rules)
crud_router("payments", PaymentIn, ("patient_id", "appointment_id", "concept", "amount", "method"), payment_rules)


@app.get("/api/agenda")
def agenda(
    day: str | None = Query(default=None, description="AAAA-MM-DD; por defecto hoy"),
    professional_id: int | None = None,
    db: sqlite3.Connection = Depends(get_db),
) -> list[dict[str, Any]]:
    day = day or datetime.now().strftime("%Y-%m-%d")
    sql = """SELECT a.*, p.name AS patient_name, p.allergies, pr.name AS professional_name, pr.specialty,
                    tp.title AS plan_title, tp.total_sessions AS plan_total,
                    CASE
                      WHEN a.plan_id IS NULL THEN NULL
                      WHEN a.status IN ('scheduled','arrived') THEN
                        (SELECT COUNT(*) FROM consultations c WHERE c.plan_id = a.plan_id)
                        + (SELECT COUNT(*) FROM appointments b WHERE b.plan_id = a.plan_id AND b.status IN ('scheduled','arrived')
                             AND (b.starts_at < a.starts_at OR (b.starts_at = a.starts_at AND b.id <= a.id)))
                      WHEN a.status = 'done' THEN
                        (SELECT COUNT(*) FROM consultations c WHERE c.plan_id = a.plan_id
                           AND c.id <= (SELECT MAX(x.id) FROM consultations x WHERE x.appointment_id = a.id))
                    END AS session_no
             FROM appointments a
             JOIN patients p ON p.id = a.patient_id
             JOIN professionals pr ON pr.id = a.professional_id
             LEFT JOIN treatment_plans tp ON tp.id = a.plan_id
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
    rows = [row_dict(r) for r in db.execute(sql + " ORDER BY c.occurred_at DESC, c.id DESC LIMIT ?", (*params, limit))]
    return enrich_consultations(db, rows)


@app.post("/api/consultations", status_code=201)
async def create_consultation(
    patient_id: int = Form(...),
    professional_id: int = Form(...),
    appointment_id: int | None = Form(None),
    diagnosis: str | None = Form(None),
    treatment: str | None = Form(None),
    notes: str | None = Form(None),
    plan_id: int | None = Form(None),
    eva: int | None = Form(None, ge=0, le=10),
    measurements: str | None = Form(None, description='JSON: [{"name":"Flexión rodilla","value":95,"unit":"°"}]'),
    library_ids: str | None = Form(None, description="IDs de entradas de biblioteca separados por coma"),
    attachment: UploadFile | None = File(None),
    db: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    marks, links = parse_measurements(measurements), parse_ids(library_ids)
    if appointment_id is not None:
        appt = db.execute("SELECT plan_id, status FROM appointments WHERE id = ?", (appointment_id,)).fetchone()
        if appt is not None:
            if appt["status"] == "done" or db.execute("SELECT 1 FROM consultations WHERE appointment_id = ?", (appointment_id,)).fetchone():
                raise HTTPException(409, "Esa cita ya tiene su atención registrada")
            if plan_id is None:
                plan_id = appt["plan_id"]
    if plan_id is not None:
        plan = db.execute("SELECT patient_id, status FROM treatment_plans WHERE id = ?", (plan_id,)).fetchone()
        if plan is None or plan["patient_id"] != patient_id:
            raise HTTPException(422, "El plan no existe o pertenece a otro paciente")
        if plan["status"] != "active":
            raise HTTPException(409, "El plan no está activo")
    stored: str | None = None
    if attachment and attachment.filename:
        extension = Path(attachment.filename).suffix.lower()
        if extension not in {".jpg", ".jpeg", ".png", ".webp", ".pdf"}:
            raise HTTPException(415, "Solo se aceptan JPG, PNG, WEBP o PDF")
        content = await attachment.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(413, "El archivo excede el tamaño máximo permitido")
        if not looks_like(extension, content):
            raise HTTPException(415, "El contenido del archivo no corresponde a su extensión")
        stored = f"{datetime.now(timezone.utc):%Y%m%d%H%M%S}_{secrets.token_hex(8)}{extension}"
        (UPLOAD_DIR / stored).write_bytes(content)
    try:
        cursor = db.execute(
            """INSERT INTO consultations (patient_id, professional_id, appointment_id, diagnosis, treatment, notes, attachment_path, plan_id, eva, occurred_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (patient_id, professional_id, appointment_id, diagnosis, treatment, notes, stored, plan_id, eva,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),  # hora local del servidor (fijar KINEPRO/TZ), no UTC
        )
        save_consultation_extras(db, cursor.lastrowid, marks, links)
        if appointment_id is not None:
            db.execute("UPDATE appointments SET status = 'done' WHERE id = ?", (appointment_id,))
        refresh_plan_status(db, plan_id)
        db.commit()
    except (sqlite3.IntegrityError, HTTPException) as error:
        db.rollback()
        if stored:
            (UPLOAD_DIR / stored).unlink(missing_ok=True)
        if isinstance(error, HTTPException):
            raise error
        raise HTTPException(409, f"Referencia inválida: {error}") from error
    return enrich_consultations(db, [row_dict(db.execute(CONSULTATION_SELECT + " WHERE c.id = ?", (cursor.lastrowid,)).fetchone())])[0]


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
        "month_sessions": count("SELECT COUNT(*) FROM consultations WHERE strftime('%Y-%m', occurred_at) = strftime('%Y-%m','now','localtime')"),
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


@app.get("/api/admin/audit")
def audit_list(request: Request, limit: int = Query(default=100, ge=1, le=500), db: sqlite3.Connection = Depends(get_db)) -> list[dict[str, Any]]:
    admin_only(request)
    return [dict(r) for r in db.execute("SELECT at, username, method, path, status FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))]


@app.get("/api/admin/backup")
def backup(request: Request) -> StreamingResponse:
    """Respaldo descargable (base + adjuntos) en .zip. Solo administrador."""
    admin_only(request)
    import io
    import zipfile
    import tempfile
    buffer = io.BytesIO()
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        copy = Path(tmp) / "kinepro.db"
        source, target = get_connection(), sqlite3.connect(copy)
        try:
            source.backup(target)  # copia consistente aunque haya escrituras
        finally:
            target.close()
            source.close()
        archive.write(copy, "kinepro.db")
        for path in UPLOAD_DIR.iterdir():
            if path.is_file() and path.name != ".gitkeep":
                archive.write(path, f"uploads/{path.name}")
    buffer.seek(0)
    name = f"respaldo-kinepro-{datetime.now():%Y%m%d-%H%M}.zip"
    return StreamingResponse(buffer, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={name}", "Cache-Control": "no-store"})


@app.get("/sw.js", include_in_schema=False)
def service_worker() -> FileResponse:
    return FileResponse(STATIC_DIR / "sw.js", media_type="application/javascript", headers={"Service-Worker-Allowed": "/"})


@app.get("/", response_class=HTMLResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
