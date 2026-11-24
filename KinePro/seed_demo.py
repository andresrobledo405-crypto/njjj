"""Carga datos de ejemplo para una demostración. No borra datos existentes."""
from datetime import datetime, timedelta

from app.db import get_connection, init_db

init_db()
db = get_connection()
if db.execute("SELECT COUNT(*) FROM patients").fetchone()[0]:
    print("Ya existen datos; no se carga la demo.")
    raise SystemExit

pacientes = [
    ("María González", "12345678-5", "+56 9 5555 0001", "Fonasa", "Penicilina"),
    ("Pedro Araya", "9876543-2", "+56 9 5555 0002", "Isapre", None),
    ("Camila Fuentes", "20111222-3", "+56 9 5555 0003", "Fonasa", None),
    ("José Morales", "7654321-K", "+56 9 5555 0004", "Particular", "Látex"),
]
for n, r, t, s, a in pacientes:
    db.execute("INSERT INTO patients (name, rut, phone, insurance, allergies) VALUES (?,?,?,?,?)", (n, r, t, s, a))
for n, e in (("Dra. Valentina Rojas", "Medicina general"), ("Dr. Andrés Vega", "Cardiología"), ("Dra. Paula Núñez", "Pediatría")):
    db.execute("INSERT INTO professionals (name, specialty) VALUES (?,?)", (n, e))

base = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
citas = [(1, 1, 0, "Box 1", "Control anual", "done"), (2, 2, 1, "Box 2", "Dolor torácico", "arrived"),
         (3, 3, 2, "Box 3", "Control niño sano", "scheduled"), (4, 1, 3, "Box 1", "Resfrío", "scheduled")]
for pa, pr, k, sala, motivo, estado in citas:
    inicio = (base + timedelta(minutes=30 * k)).strftime("%Y-%m-%dT%H:%M")
    db.execute("INSERT INTO appointments (patient_id, professional_id, starts_at, room, reason, status) VALUES (?,?,?,?,?,?)",
               (pa, pr, inicio, sala, motivo, estado))
db.execute("INSERT INTO consultations (patient_id, professional_id, appointment_id, diagnosis, treatment) VALUES (1,1,1,'Sin hallazgos','Control en 12 meses')")
db.execute("INSERT INTO payments (patient_id, appointment_id, concept, amount, method) VALUES (1,1,'Consulta general',25000,'card')")
db.commit()
print("Datos de demostración cargados.")
