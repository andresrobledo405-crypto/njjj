def appt(patient, doctor, start="2030-05-10T09:00", **extra):
    return {"patient_id": patient["id"], "professional_id": doctor["id"], "starts_at": start, "duration_min": 30, **extra}


def test_rut_normalizado_y_unico(client):
    p = client.post("/api/patients", json={"name": "Ana", "rut": "12.345.678-5"}).json()
    assert p["rut"] == "12345678-5"
    assert client.post("/api/patients", json={"name": "Otra", "rut": "12345678-5"}).status_code == 409


def test_cita_ok_y_agenda(client, base):
    patient, _, doctor = base
    assert client.post("/api/appointments", json=appt(patient, doctor)).status_code == 201
    items = client.get("/api/agenda", params={"day": "2030-05-10"}).json()
    assert len(items) == 1 and items[0]["patient_name"] == "Ana Soto"


def test_choque_de_profesional(client, base):
    patient, other, doctor = base
    client.post("/api/appointments", json=appt(patient, doctor))
    r = client.post("/api/appointments", json=appt(other, doctor, "2030-05-10T09:15"))
    assert r.status_code == 409 and "profesional" in r.json()["detail"]


def test_choque_de_paciente_y_sala(client, base):
    patient, other, doctor = base
    doctor2 = client.post("/api/professionals", json={"name": "Dr. Vega", "specialty": "Cardiología"}).json()
    client.post("/api/appointments", json=appt(patient, doctor, room="Box 1"))
    assert "paciente" in client.post("/api/appointments", json=appt(patient, doctor2)).json()["detail"]
    assert "sala" in client.post("/api/appointments", json=appt(other, doctor2, room="Box 1")).json()["detail"]


def test_cita_contigua_no_choca_y_cancelada_libera(client, base):
    patient, other, doctor = base
    first = client.post("/api/appointments", json=appt(patient, doctor)).json()
    assert client.post("/api/appointments", json=appt(other, doctor, "2030-05-10T09:30")).status_code == 201
    client.post(f"/api/appointments/{first['id']}/status", data={"status": "cancelled"})
    assert client.post("/api/appointments", json=appt(other, doctor, "2030-05-10T09:00")).status_code == 201


def test_fecha_invalida_y_estado_invalido(client, base):
    patient, _, doctor = base
    assert client.post("/api/appointments", json=appt(patient, doctor, "no-es-fecha-valida")).status_code == 422
    assert client.post("/api/appointments", json=appt(patient, doctor, status="x")).status_code == 422


def test_consulta_con_adjunto_marca_cita_realizada(client, base):
    patient, _, doctor = base
    cita = client.post("/api/appointments", json=appt(patient, doctor)).json()
    r = client.post(
        "/api/consultations",
        data={"patient_id": patient["id"], "professional_id": doctor["id"], "appointment_id": cita["id"], "diagnosis": "Resfrío"},
        files={"attachment": ("examen.pdf", b"%PDF-1.4 demo", "application/pdf")},
    )
    assert r.status_code == 201
    assert client.get(f"/api/consultations/{r.json()['id']}/attachment").content.startswith(b"%PDF")
    assert client.get(f"/api/appointments/{cita['id']}").json()["status"] == "done"


def test_adjunto_con_extension_peligrosa_rechazado(client, base):
    patient, _, doctor = base
    r = client.post(
        "/api/consultations",
        data={"patient_id": patient["id"], "professional_id": doctor["id"]},
        files={"attachment": ("virus.exe", b"MZ", "application/octet-stream")},
    )
    assert r.status_code == 415


def test_pagos_dashboard_y_exportacion(client, base):
    patient, _, doctor = base
    assert client.post("/api/payments", json={"patient_id": patient["id"], "concept": "Consulta", "amount": 25000, "method": "card"}).status_code == 201
    assert client.post("/api/payments", json={"patient_id": patient["id"], "concept": "x", "amount": 1, "method": "bitcoin"}).status_code == 422
    assert client.get("/api/dashboard").json()["month_revenue"] == 25000
    csv = client.get("/api/export/payments.csv")
    assert csv.status_code == 200 and "Consulta" in csv.text and csv.text.startswith("﻿")


def test_no_se_borra_paciente_con_historial(client, base):
    patient, _, doctor = base
    client.post("/api/appointments", json=appt(patient, doctor))
    assert client.delete(f"/api/patients/{patient['id']}").status_code == 409
