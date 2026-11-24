from datetime import datetime, timedelta


def _when(days, hour=10):
    return (datetime.now() + timedelta(days=days)).replace(hour=hour, minute=0).strftime("%Y-%m-%dT%H:%M")


def test_recordatorios_citas_de_manana(client, base):
    patient, other, doctor = base
    client.put(f"/api/patients/{patient['id']}", json={"name": "Ana Soto", "rut": "12.345.678-5", "phone": "9 5555 0001"})
    manana = client.post("/api/appointments", json={"patient_id": patient["id"], "professional_id": doctor["id"], "starts_at": _when(1)}).json()
    client.post("/api/appointments", json={"patient_id": other["id"], "professional_id": doctor["id"], "starts_at": _when(1, 12), "status": "cancelled"})
    client.post("/api/appointments", json={"patient_id": other["id"], "professional_id": doctor["id"], "starts_at": _when(3)})
    r = client.get("/api/reminders").json()
    assert [x["id"] for x in r] == [manana["id"]]  # ni canceladas ni otros días
    assert "Ana" in r[0]["message"] and "Dra. Rojas" in r[0]["message"] and "10:00" in r[0]["message"]
    assert r[0]["whatsapp_url"] == "https://wa.me/56955550001"
    assert client.get("/api/reminders", params={"day": _when(3)[:10]}).json()[0]["patient_name"] == "Luis Pérez"


def test_ficha_paciente_con_historial(client, base):
    patient, other, doctor = base
    appt = client.post("/api/appointments", json={"patient_id": patient["id"], "professional_id": doctor["id"], "starts_at": _when(0)}).json()
    client.post("/api/consultations", data={"patient_id": patient["id"], "professional_id": doctor["id"], "appointment_id": appt["id"], "diagnosis": "Control"})
    client.post("/api/payments", json={"patient_id": patient["id"], "concept": "Consulta", "amount": 25000, "method": "card"})
    client.post("/api/payments", json={"patient_id": other["id"], "concept": "Otra", "amount": 9999})
    h = client.get(f"/api/patients/{patient['id']}/history").json()
    assert h["patient"]["name"] == "Ana Soto"
    assert len(h["appointments"]) == 1 and h["appointments"][0]["status"] == "done"
    assert len(h["consultations"]) == 1 and len(h["payments"]) == 1 and h["total_paid"] == 25000
    assert client.get("/api/patients/99999/history").status_code == 404


def test_reporte_de_caja_diario_y_mensual(client, base):
    patient, _, _ = base
    client.post("/api/payments", json={"patient_id": patient["id"], "concept": "A", "amount": 10000, "method": "cash"})
    client.post("/api/payments", json={"patient_id": patient["id"], "concept": "B", "amount": 5000, "method": "card"})
    client.post("/api/payments", json={"patient_id": patient["id"], "concept": "C", "amount": 2500, "method": "cash"})
    day = client.get("/api/reports/cash").json()
    assert day["total"] == 17500 and day["count"] == 3
    assert day["by_method"]["cash"] == {"count": 2, "total": 12500}
    month = client.get("/api/reports/cash", params={"period": "month"}).json()
    assert month["total"] == 17500 and len(month["payments"]) == 3
    assert client.get("/api/reports/cash", params={"date": "2000-01-01"}).json()["total"] == 0
    assert client.get("/api/reports/cash", params={"date": "basura"}).status_code == 422
    assert client.get("/api/reports/cash", params={"period": "year"}).status_code == 422


def test_nuevos_endpoints_exigen_sesion(client):
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        for url in ("/api/reminders", "/api/reports/cash", "/api/documents", "/api/patients/1/history", "/api/export/payments.csv"):
            assert c.get(url).status_code == 401, url


def test_solo_admin_borra_registros(client, base):
    from fastapi.testclient import TestClient
    from app.main import app
    patient, _, _ = base
    u = client.post("/api/users", json={"username": "pro2", "name": "Pro Dos", "password": "clave-larga-123", "role": "profesional"}).json()
    with TestClient(app) as c:
        c.post("/api/auth/login", json={"username": "pro2", "password": "clave-larga-123"})
        assert c.delete(f"/api/patients/{patient['id']}").status_code == 403
        assert c.get(f"/api/patients/{patient['id']}").status_code == 200
    client.delete(f"/api/users/{u['id']}")
    assert client.delete(f"/api/patients/{patient['id']}").status_code == 204
