"""Funciones propias de kinesiología: planes de tratamiento, evolución (EVA y rangos),
plantillas de ejercicios para el hogar (impresión/PDF) y enlaces atención ↔ biblioteca.

Nada de lo que hay aquí sale del servidor: la hoja para el paciente es HTML que el navegador imprime o guarda como PDF.
"""
import json
import sqlite3
from datetime import datetime, timedelta
from html import escape
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .config import APP_NAME
from .db import get_db

PLAN_STATUSES = {"active", "completed", "cancelled"}
LIVE = ("scheduled", "arrived")


def _d(row: sqlite3.Row | None) -> dict[str, Any]:
    return dict(row) if row is not None else {}


# ---------- datos de una atención (mediciones, enlaces) ----------

def parse_measurements(raw: str | None) -> list[dict[str, Any]]:
    """Convierte el JSON enviado por el formulario en filas válidas: [{name, value, unit}]."""
    if not raw or not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except ValueError as error:
        raise HTTPException(422, "Mediciones con formato inválido") from error
    if not isinstance(data, list) or len(data) > 20:
        raise HTTPException(422, "Mediciones inválidas (máximo 20)")
    result = []
    for entry in data:
        try:
            name = str(entry["name"]).strip()[:60]
            value = float(entry["value"])
        except (KeyError, TypeError, ValueError) as error:
            raise HTTPException(422, "Cada medición necesita nombre y valor numérico") from error
        if not name or not -1000 <= value <= 1000:
            raise HTTPException(422, "Medición fuera de rango")
        result.append({"name": name, "value": value, "unit": str(entry.get("unit") or "°")[:8]})
    return result


def parse_ids(raw: str | None) -> list[int]:
    if not raw or not raw.strip():
        return []
    try:
        ids = [int(part) for part in raw.replace("[", "").replace("]", "").split(",") if part.strip()]
    except ValueError as error:
        raise HTTPException(422, "Lista de entradas inválida") from error
    return list(dict.fromkeys(ids))[:30]


def save_consultation_extras(db: sqlite3.Connection, consultation_id: int, measurements: list[dict], library_ids: list[int]) -> None:
    for m in measurements:
        db.execute("INSERT INTO measurements (consultation_id, name, value, unit) VALUES (?,?,?,?)",
                   (consultation_id, m["name"], m["value"], m["unit"]))
    for item_id in library_ids:
        if db.execute("SELECT 1 FROM library_items WHERE id = ?", (item_id,)).fetchone() is None:
            raise HTTPException(422, f"La entrada de biblioteca {item_id} no existe")
        db.execute("INSERT OR IGNORE INTO consultation_library (consultation_id, library_item_id) VALUES (?,?)", (consultation_id, item_id))


def enrich_consultations(db: sqlite3.Connection, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Agrega `measurements` y `library` (enlaces a biblioteca) a cada atención."""
    if not rows:
        return rows
    ids = [r["id"] for r in rows]
    marks = ",".join("?" for _ in ids)
    by_c: dict[int, dict[str, list]] = {i: {"measurements": [], "library": []} for i in ids}
    for m in db.execute(f"SELECT consultation_id, name, value, unit FROM measurements WHERE consultation_id IN ({marks}) ORDER BY id", ids):
        by_c[m["consultation_id"]]["measurements"].append({"name": m["name"], "value": m["value"], "unit": m["unit"]})
    for link in db.execute(
        f"""SELECT cl.consultation_id, li.id, li.title, li.category FROM consultation_library cl
            JOIN library_items li ON li.id = cl.library_item_id WHERE cl.consultation_id IN ({marks}) ORDER BY li.title""", ids):
        by_c[link["consultation_id"]]["library"].append({"id": link["id"], "title": link["title"], "category": link["category"]})
    for r in rows:
        r.update(by_c[r["id"]])
    return rows


# ---------- planes de tratamiento ----------

class PlanIn(BaseModel):
    patient_id: int
    professional_id: int | None = None
    title: str = Field(min_length=1, max_length=120)
    reason: str | None = Field(default=None, max_length=500)          # motivo de consulta
    kine_diagnosis: str | None = Field(default=None, max_length=300)  # diagnóstico kinésico
    total_sessions: int = Field(default=10, ge=1, le=100)
    status: str = "active"


class SeriesIn(BaseModel):
    professional_id: int
    starts_at: str = Field(min_length=16, max_length=19)  # primera sesión AAAA-MM-DDTHH:MM
    count: int = Field(ge=1, le=100)
    interval_days: int = Field(default=2, ge=1, le=30)
    duration_min: int = Field(default=45, ge=5, le=480)
    room: str | None = Field(default=None, max_length=40)


PLAN_SELECT = """SELECT tp.*, pa.name AS patient_name,
    (SELECT COUNT(*) FROM consultations c WHERE c.plan_id = tp.id) AS sessions_done,
    (SELECT COUNT(*) FROM appointments a WHERE a.plan_id = tp.id AND a.status IN ('scheduled','arrived')) AS sessions_scheduled
    FROM treatment_plans tp JOIN patients pa ON pa.id = tp.patient_id"""


def evolution(db: sqlite3.Connection, plan_id: int) -> dict[str, Any]:
    """Serie temporal de EVA y de cada medición, en orden cronológico, lista para graficar."""
    eva, measures = [], {}
    for c in db.execute("SELECT id, occurred_at, eva FROM consultations WHERE plan_id = ? ORDER BY occurred_at, id", (plan_id,)):
        date = c["occurred_at"][:10]
        if c["eva"] is not None:
            eva.append({"date": date, "value": c["eva"]})
        for m in db.execute("SELECT name, value, unit FROM measurements WHERE consultation_id = ? ORDER BY id", (c["id"],)):
            measures.setdefault(m["name"], []).append({"date": date, "value": m["value"], "unit": m["unit"]})
    return {"eva": eva, "measures": measures}


def refresh_plan_status(db: sqlite3.Connection, plan_id: int | None) -> None:
    """Un plan activo pasa a 'completed' cuando se registran todas sus sesiones."""
    if plan_id is None:
        return
    db.execute(
        """UPDATE treatment_plans SET status = 'completed' WHERE id = ? AND status = 'active'
           AND (SELECT COUNT(*) FROM consultations WHERE plan_id = ?) >= total_sessions""", (plan_id, plan_id))


def register(app, appointment_rules) -> None:
    router = APIRouter()

    def _plan_or_404(db: sqlite3.Connection, plan_id: int) -> dict[str, Any]:
        row = db.execute(PLAN_SELECT + " WHERE tp.id = ?", (plan_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Plan no encontrado")
        return dict(row)

    def _validate_plan(payload: PlanIn, db: sqlite3.Connection) -> None:
        if payload.status not in PLAN_STATUSES:
            raise HTTPException(422, "Estado de plan no válido")
        if db.execute("SELECT 1 FROM patients WHERE id = ?", (payload.patient_id,)).fetchone() is None:
            raise HTTPException(422, "Paciente no existe")
        if payload.professional_id is not None and db.execute("SELECT 1 FROM professionals WHERE id = ?", (payload.professional_id,)).fetchone() is None:
            raise HTTPException(422, "Profesional no existe")

    @router.get("/api/plans")
    def list_plans(patient_id: int | None = None, status: str | None = None, db: sqlite3.Connection = Depends(get_db)) -> list[dict[str, Any]]:
        sql, params = PLAN_SELECT + " WHERE 1=1", []
        if patient_id is not None:
            sql, params = sql + " AND tp.patient_id = ?", [*params, patient_id]
        if status:
            sql, params = sql + " AND tp.status = ?", [*params, status]
        return [dict(r) for r in db.execute(sql + " ORDER BY tp.id DESC", params)]

    @router.post("/api/plans", status_code=201)
    def create_plan(payload: PlanIn, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
        _validate_plan(payload, db)
        cursor = db.execute(
            """INSERT INTO treatment_plans (patient_id, professional_id, title, reason, kine_diagnosis, total_sessions, status)
               VALUES (?,?,?,?,?,?,?)""",
            (payload.patient_id, payload.professional_id, payload.title, payload.reason, payload.kine_diagnosis,
             payload.total_sessions, payload.status))
        db.commit()
        return _plan_or_404(db, cursor.lastrowid)

    @router.put("/api/plans/{plan_id}")
    def update_plan(plan_id: int, payload: PlanIn, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
        _validate_plan(payload, db)
        current = _plan_or_404(db, plan_id)
        if payload.patient_id != current["patient_id"]:
            raise HTTPException(422, "No se puede cambiar el paciente de un plan")
        db.execute(
            """UPDATE treatment_plans SET professional_id=?, title=?, reason=?, kine_diagnosis=?, total_sessions=?, status=? WHERE id=?""",
            (payload.professional_id, payload.title, payload.reason, payload.kine_diagnosis, payload.total_sessions, payload.status, plan_id))
        refresh_plan_status(db, plan_id)
        db.commit()
        return _plan_or_404(db, plan_id)

    @router.get("/api/plans/{plan_id}")
    def get_plan(plan_id: int, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
        plan = _plan_or_404(db, plan_id)
        plan["appointments"] = [dict(r) for r in db.execute(
            "SELECT id, starts_at, duration_min, room, status FROM appointments WHERE plan_id = ? ORDER BY starts_at", (plan_id,))]
        consultations = [dict(r) for r in db.execute(
            """SELECT c.id, c.occurred_at, c.diagnosis, c.treatment, c.notes, c.eva, c.attachment_path, pr.name AS professional_name
               FROM consultations c JOIN professionals pr ON pr.id = c.professional_id
               WHERE c.plan_id = ? ORDER BY c.occurred_at, c.id""", (plan_id,))]
        plan["consultations"] = enrich_consultations(db, consultations)
        plan["evolution"] = evolution(db, plan_id)
        return plan

    @router.post("/api/plans/{plan_id}/schedule")
    def schedule_series(plan_id: int, payload: SeriesIn, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
        """Agenda varias sesiones del plan. Las que chocan se omiten y se informan; no se aborta toda la serie."""
        plan = _plan_or_404(db, plan_id)
        if plan["status"] != "active":
            raise HTTPException(409, "El plan no está activo")
        if db.execute("SELECT 1 FROM professionals WHERE id = ?", (payload.professional_id,)).fetchone() is None:
            raise HTTPException(422, "Profesional no existe")
        remaining = plan["total_sessions"] - plan["sessions_done"] - plan["sessions_scheduled"]
        if remaining <= 0:
            raise HTTPException(409, "El plan ya tiene todas sus sesiones agendadas o realizadas")
        try:
            first = datetime.fromisoformat(payload.starts_at)
        except ValueError as error:
            raise HTTPException(422, "Fecha/hora inválida (use AAAA-MM-DDTHH:MM)") from error
        created, skipped = [], []
        for n in range(min(payload.count, remaining)):
            start = (first + timedelta(days=payload.interval_days * n)).strftime("%Y-%m-%dT%H:%M")
            values = {"patient_id": plan["patient_id"], "professional_id": payload.professional_id, "starts_at": start,
                      "duration_min": payload.duration_min, "room": payload.room, "reason": plan["title"], "status": "scheduled"}
            try:
                appointment_rules(values, db, None)
            except HTTPException as error:
                skipped.append({"starts_at": start, "reason": error.detail})
                continue
            cursor = db.execute(
                """INSERT INTO appointments (patient_id, professional_id, starts_at, duration_min, room, reason, plan_id, status)
                   VALUES (?,?,?,?,?,?,?, 'scheduled')""",
                (values["patient_id"], values["professional_id"], values["starts_at"], values["duration_min"], values["room"], values["reason"], plan_id))
            created.append({"id": cursor.lastrowid, "starts_at": start})
        db.commit()
        return {"created": created, "skipped": skipped, "capped": payload.count > remaining}

    # ---------- plantillas de ejercicios para el hogar ----------

    class TemplateItemIn(BaseModel):
        library_item_id: int
        dosage: str | None = Field(default=None, max_length=80)   # ej.: "3 series x 10 repeticiones" (lo define el profesional)
        notes: str | None = Field(default=None, max_length=300)

    class TemplateIn(BaseModel):
        name: str = Field(min_length=1, max_length=120)
        notes: str | None = Field(default=None, max_length=600)
        items: list[TemplateItemIn] = Field(default_factory=list, max_length=30)

    def _template(db: sqlite3.Connection, template_id: int) -> dict[str, Any]:
        row = db.execute("SELECT * FROM exercise_templates WHERE id = ?", (template_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Plantilla no encontrada")
        template = dict(row)
        template["items"] = [dict(r) for r in db.execute(
            """SELECT ti.id, ti.library_item_id, ti.dosage, ti.notes, li.title, li.region, li.summary, li.content, li.precautions
               FROM exercise_template_items ti JOIN library_items li ON li.id = ti.library_item_id
               WHERE ti.template_id = ? ORDER BY ti.position, ti.id""", (template_id,))]
        return template

    def _save_items(db: sqlite3.Connection, template_id: int, items: list[TemplateItemIn]) -> None:
        db.execute("DELETE FROM exercise_template_items WHERE template_id = ?", (template_id,))
        for position, item in enumerate(items):
            row = db.execute("SELECT category FROM library_items WHERE id = ?", (item.library_item_id,)).fetchone()
            if row is None:
                raise HTTPException(422, f"La entrada de biblioteca {item.library_item_id} no existe")
            db.execute("INSERT INTO exercise_template_items (template_id, library_item_id, dosage, notes, position) VALUES (?,?,?,?,?)",
                       (template_id, item.library_item_id, item.dosage, item.notes, position))

    @router.get("/api/templates")
    def list_templates(db: sqlite3.Connection = Depends(get_db)) -> list[dict[str, Any]]:
        return [dict(r) for r in db.execute(
            """SELECT t.*, (SELECT COUNT(*) FROM exercise_template_items i WHERE i.template_id = t.id) AS item_count
               FROM exercise_templates t ORDER BY t.name""")]

    @router.post("/api/templates", status_code=201)
    def create_template(payload: TemplateIn, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
        cursor = db.execute("INSERT INTO exercise_templates (name, notes) VALUES (?,?)", (payload.name, payload.notes))
        try:
            _save_items(db, cursor.lastrowid, payload.items)
        except HTTPException:
            db.rollback()
            raise
        db.commit()
        return _template(db, cursor.lastrowid)

    @router.get("/api/templates/{template_id}")
    def get_template(template_id: int, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
        return _template(db, template_id)

    @router.put("/api/templates/{template_id}")
    def update_template(template_id: int, payload: TemplateIn, db: sqlite3.Connection = Depends(get_db)) -> dict[str, Any]:
        _template(db, template_id)
        db.execute("UPDATE exercise_templates SET name = ?, notes = ? WHERE id = ?", (payload.name, payload.notes, template_id))
        try:
            _save_items(db, template_id, payload.items)
        except HTTPException:
            db.rollback()
            raise
        db.commit()
        return _template(db, template_id)

    @router.delete("/api/templates/{template_id}", status_code=204)
    def delete_template(template_id: int, db: sqlite3.Connection = Depends(get_db)) -> None:
        _template(db, template_id)
        db.execute("DELETE FROM exercise_templates WHERE id = ?", (template_id,))
        db.commit()

    @router.get("/api/templates/{template_id}/print", response_class=HTMLResponse)
    def print_template(template_id: int, patient_id: int | None = None, db: sqlite3.Connection = Depends(get_db)) -> HTMLResponse:
        """Hoja de ejercicios para el hogar, lista para imprimir o 'Guardar como PDF' desde el navegador."""
        template = _template(db, template_id)
        patient_name = ""
        if patient_id is not None:
            row = db.execute("SELECT name FROM patients WHERE id = ?", (patient_id,)).fetchone()
            if row is None:
                raise HTTPException(404, "Paciente no encontrado")
            patient_name = row["name"]
        return HTMLResponse(render_sheet(template, patient_name), headers={"Cache-Control": "no-store"})

    app.include_router(router)


SHEET_CSS = """
body{font:15px/1.5 system-ui,Arial,sans-serif;color:#12302d;margin:0;padding:1.2rem;max-width:760px;margin-inline:auto}
h1{font-size:1.4rem;margin:.2rem 0}h2{font-size:1.1rem;margin:0 0 .2rem}.mute{color:#5d7471;font-size:.85rem}
.ex{border:1px solid #cfdad8;border-radius:10px;padding:.8rem;margin:.7rem 0;break-inside:avoid}
.dose{display:inline-block;background:#e6f2f0;border-radius:99px;padding:.1rem .7rem;font-weight:700;margin:.2rem 0}
.body{white-space:pre-wrap}.prec{border-left:3px solid #b45309;background:#fdf3e6;padding:.4rem .6rem;margin:.5rem 0}
.banner{background:#fff4d6;border:1px solid #e0b84a;border-radius:10px;padding:.6rem .8rem;margin-bottom:1rem;font-size:.9rem}
button{font:inherit;padding:.6rem 1rem;border-radius:10px;border:0;background:#0f766e;color:#fff;font-weight:700}
.foot{margin-top:1.2rem;font-size:.8rem;color:#5d7471;border-top:1px solid #cfdad8;padding-top:.6rem}
@media print{.no-print{display:none!important}body{padding:0}}
"""


def render_sheet(template: dict[str, Any], patient_name: str) -> str:
    e = escape
    today = datetime.now().strftime("%d-%m-%Y")
    exercises = []
    for n, item in enumerate(template["items"], 1):
        parts = [f'<div class="ex"><h2>{n}. {e(item["title"])}</h2>']
        if item["region"]:
            parts.append(f'<div class="mute">{e(item["region"])}</div>')
        if item["dosage"]:
            parts.append(f'<div class="dose">{e(item["dosage"])}</div>')
        if item["summary"]:
            parts.append(f'<p><b>{e(item["summary"])}</b></p>')
        if item["content"]:
            parts.append(f'<div class="body">{e(item["content"])}</div>')
        if item["notes"]:
            parts.append(f'<p><b>Indicación del kinesiólogo:</b> {e(item["notes"])}</p>')
        if item["precautions"]:
            parts.append(f'<div class="prec"><b>Precauciones</b><br>{e(item["precautions"])}</div>')
        parts.append("</div>")
        exercises.append("".join(parts))
    body = "".join(exercises) or '<p class="mute">Esta plantilla aún no tiene ejercicios.</p>'
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(template["name"])}</title><style>{SHEET_CSS}</style></head><body>
<div class="banner no-print"><b>Para el profesional:</b> el contenido de la biblioteca fue redactado con apoyo de IA y <b>aún no está validado por un kinesiólogo</b>.
Revise y adapte cada ejercicio antes de entregar esta hoja. <br><br><button onclick="window.print()">Imprimir o guardar como PDF</button></div>
<div class="mute">{e(APP_NAME)} · {today}</div>
<h1>{e(template["name"])}</h1>
{f'<p><b>Paciente:</b> {e(patient_name)}</p>' if patient_name else ''}
{f'<p class="body">{e(template["notes"])}</p>' if template["notes"] else ''}
{body}
<div class="foot">Realice solo los ejercicios indicados por su kinesiólogo. Si el dolor aumenta de forma importante o aparecen síntomas nuevos, deténgase y consulte a su kinesiólogo.</div>
</body></html>"""
