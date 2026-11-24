"""Carga datos FICTICIOS de demostración (kinesiología). No borra datos existentes."""
from datetime import datetime, timedelta

from app.db import get_connection, init_db
from app.library import seed_library

init_db()
db = get_connection()
seed_library(db)
if db.execute("SELECT COUNT(*) FROM patients").fetchone()[0]:
    print("Ya existen datos; no se carga la demo.")
    raise SystemExit

pacientes = [
    ("María González", "12345678-5", "+56 9 5555 0001", "Fonasa", "Hipertensión (en control)"),
    ("Pedro Araya", "9876543-2", "+56 9 5555 0002", "Isapre", None),
    ("Camila Fuentes", "20111222-3", "+56 9 5555 0003", "Fonasa", None),
]
for n, r, t, s, a in pacientes:
    db.execute("INSERT INTO patients (name, rut, phone, insurance, allergies) VALUES (?,?,?,?,?)", (n, r, t, s, a))
for n, e in (("Kgo. Valentina Rojas", "Kinesiología"), ("Kgo. Andrés Vega", "Kinesiología deportiva")):
    db.execute("INSERT INTO professionals (name, specialty) VALUES (?,?)", (n, e))

db.execute("""INSERT INTO treatment_plans (patient_id, professional_id, title, reason, kine_diagnosis, total_sessions)
              VALUES (1, 1, 'Lumbalgia mecánica', 'Dolor lumbar al agacharse y al estar sentada', 'Dolor lumbar de origen mecánico', 10)""")
today = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
# Tres sesiones ya realizadas (valores ficticios solo para mostrar el gráfico)
for k, (eva, flex) in enumerate(((7, 20), (6, 26), (4, 31))):
    when = (today - timedelta(days=(3 - k) * 3)).strftime("%Y-%m-%d %H:%M:%S")
    cur = db.execute("""INSERT INTO consultations (patient_id, professional_id, plan_id, eva, diagnosis, treatment, occurred_at)
                        VALUES (1, 1, 1, ?, 'Evolución según plan', 'Ejercicios y movilidad', ?)""", (eva, when))
    db.execute("INSERT INTO measurements (consultation_id, name, value, unit) VALUES (?, 'Flexión lumbar (dedos-suelo)', ?, 'cm')", (cur.lastrowid, flex))
for k in range(3):  # sesiones futuras del plan
    inicio = (today + timedelta(days=2 * (k + 1))).strftime("%Y-%m-%dT%H:%M")
    db.execute("INSERT INTO appointments (patient_id, professional_id, starts_at, duration_min, room, reason, plan_id) VALUES (1,1,?,45,'Box 1','Lumbalgia mecánica',1)", (inicio,))
db.execute("INSERT INTO appointments (patient_id, professional_id, starts_at, duration_min, room, reason, plan_id) VALUES (1,1,?,45,'Box 1','Lumbalgia mecánica',1)",
           (today.strftime("%Y-%m-%dT%H:%M"),))
db.execute("INSERT INTO appointments (patient_id, professional_id, starts_at, duration_min, room, reason) VALUES (2,2,?,45,'Box 2','Evaluación hombro')",
           ((today + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),))
db.execute("INSERT INTO payments (patient_id, concept, amount, method) VALUES (1,'Sesión kinesiología',20000,'card')")

# Plantilla de ejemplo con los primeros ejercicios de la biblioteca (dosis las define el profesional)
db.execute("INSERT INTO exercise_templates (name, notes) VALUES ('Ejemplo – programa para el hogar', 'Plantilla de demostración: complete la dosificación según el paciente.')")
for pos, row in enumerate(db.execute("SELECT id FROM library_items WHERE category='ejercicio' ORDER BY title LIMIT 3").fetchall()):
    db.execute("INSERT INTO exercise_template_items (template_id, library_item_id, position) VALUES (1, ?, ?)", (row["id"], pos))
db.commit()
print("Datos de demostración (ficticios) cargados.")
