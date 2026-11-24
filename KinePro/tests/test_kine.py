import json

from tests.test_kinepro import appt


def make_plan(client, patient, doctor, total=3, **extra):
    r = client.post("/api/plans", json={"patient_id": patient["id"], "professional_id": doctor["id"], "title": "Lumbalgia mecánica",
                                         "reason": "Dolor lumbar al agacharse", "total_sessions": total, **extra})
    assert r.status_code == 201, r.text
    return r.json()


def consult(client, patient, doctor, plan=None, **data):
    form = {"patient_id": patient["id"], "professional_id": doctor["id"], **data}
    if plan:
        form["plan_id"] = plan["id"]
    return client.post("/api/consultations", data=form)


def test_plan_progreso_y_estado(client, base):
    patient, _, doctor = base
    plan = make_plan(client, patient, doctor, total=2)
    assert plan["sessions_done"] == 0 and plan["status"] == "active" and plan["patient_name"] == "Ana Soto"
    consult(client, patient, doctor, plan, diagnosis="s1")
    mid = client.get(f"/api/plans/{plan['id']}").json()
    assert mid["sessions_done"] == 1 and mid["status"] == "active"
    consult(client, patient, doctor, plan, diagnosis="s2")
    assert client.get(f"/api/plans/{plan['id']}").json()["status"] == "completed"
    assert [p["id"] for p in client.get("/api/plans", params={"patient_id": patient["id"]}).json()] == [plan["id"]]


def test_plan_validaciones(client, base):
    patient, other, doctor = base
    bad = client.post("/api/plans", json={"patient_id": 9999, "title": "x", "total_sessions": 5})
    assert bad.status_code == 422
    assert client.post("/api/plans", json={"patient_id": patient["id"], "title": "x", "total_sessions": 0}).status_code == 422
    assert client.post("/api/plans", json={"patient_id": patient["id"], "title": "x", "status": "otro"}).status_code == 422
    plan = make_plan(client, patient, doctor)
    # el plan de un paciente no se usa con otro
    r = consult(client, other, doctor, plan)
    assert r.status_code == 422
    assert client.get("/api/plans/9999").status_code == 404


def test_serie_de_sesiones_omite_choques_y_respeta_el_tope(client, base):
    patient, other, doctor = base
    plan = make_plan(client, patient, doctor, total=4)
    client.post("/api/appointments", json=appt(other, doctor, "2030-05-12T09:00"))  # ocupa la 2.ª sesión
    r = client.post(f"/api/plans/{plan['id']}/schedule", json={"professional_id": doctor["id"], "starts_at": "2030-05-10T09:00",
                                                              "count": 10, "interval_days": 2, "duration_min": 30}).json()
    assert [c["starts_at"] for c in r["created"]] == ["2030-05-10T09:00", "2030-05-14T09:00", "2030-05-16T09:00"]
    assert len(r["skipped"]) == 1 and "profesional" in r["skipped"][0]["reason"]
    assert r["capped"] is True
    day = client.get("/api/agenda", params={"day": "2030-05-14"}).json()
    assert day[0]["plan_title"] == "Lumbalgia mecánica" and day[0]["plan_total"] == 4 and day[0]["session_no"] == 2
    assert client.get(f"/api/plans/{plan['id']}").json()["sessions_scheduled"] == 3


def test_serie_en_plan_cerrado(client, base):
    patient, _, doctor = base
    plan = make_plan(client, patient, doctor, total=1)
    consult(client, patient, doctor, plan)
    r = client.post(f"/api/plans/{plan['id']}/schedule", json={"professional_id": doctor["id"], "starts_at": "2030-05-10T09:00", "count": 1})
    assert r.status_code == 409


def test_cita_con_plan_hereda_en_la_atencion(client, base):
    patient, _, doctor = base
    plan = make_plan(client, patient, doctor)
    a = client.post("/api/appointments", json=appt(patient, doctor, plan_id=plan["id"])).json()
    c = client.post("/api/consultations", data={"patient_id": patient["id"], "professional_id": doctor["id"], "appointment_id": a["id"], "eva": 6}).json()
    assert c["plan_id"] == plan["id"] and c["eva"] == 6
    assert client.get(f"/api/plans/{plan['id']}").json()["sessions_done"] == 1


def test_cita_con_plan_ajeno_se_rechaza(client, base):
    patient, other, doctor = base
    plan = make_plan(client, patient, doctor)
    assert client.post("/api/appointments", json=appt(other, doctor, plan_id=plan["id"])).status_code == 422


def test_eva_mediciones_y_evolucion(client, base):
    patient, _, doctor = base
    plan = make_plan(client, patient, doctor, total=5)
    for eva, flex in ((7, 80), (5, 95), (3, 110)):
        r = consult(client, patient, doctor, plan, eva=eva, measurements=json.dumps([{"name": "Flexión de rodilla", "value": flex}]))
        assert r.status_code == 201, r.text
    ev = client.get(f"/api/plans/{plan['id']}").json()["evolution"]
    assert [p["value"] for p in ev["eva"]] == [7, 5, 3]
    assert [p["value"] for p in ev["measures"]["Flexión de rodilla"]] == [80, 95, 110]
    assert ev["measures"]["Flexión de rodilla"][0]["unit"] == "°"


def test_eva_y_mediciones_invalidas(client, base):
    patient, _, doctor = base
    assert consult(client, patient, doctor, eva=11).status_code == 422
    assert consult(client, patient, doctor, eva=-1).status_code == 422
    assert consult(client, patient, doctor, measurements="{no es json").status_code == 422
    assert consult(client, patient, doctor, measurements=json.dumps([{"name": "x"}])).status_code == 422
    assert consult(client, patient, doctor, measurements=json.dumps([{"name": "x", "value": 99999}])).status_code == 422
    assert client.get("/api/consultations").json() == []  # nada quedó guardado a medias


def test_enlaces_atencion_biblioteca(client, base):
    patient, _, doctor = base
    ids = [i["id"] for i in client.get("/api/library", params={"q": "Lachman"}).json()][:1]
    assert ids
    c = consult(client, patient, doctor, library_ids=",".join(map(str, ids))).json()
    assert [x["id"] for x in c["library"]] == ids
    assert [x["id"] for x in client.get("/api/consultations").json()[0]["library"]] == ids
    assert consult(client, patient, doctor, library_ids="999999").status_code == 422
    assert consult(client, patient, doctor, library_ids="abc").status_code == 422
    assert len(client.get("/api/consultations").json()) == 1  # la inválida no dejó atención huérfana


def exercise_ids(client, n=2):
    """Primero uno con precauciones, para comprobar que la hoja las imprime."""
    items = client.get("/api/library", params={"category": "ejercicio"}).json()
    items.sort(key=lambda i: not i["precautions"])
    assert items[0]["precautions"]
    return [i["id"] for i in items][:n]


def test_plantilla_ejercicios_crud_e_impresion(client, base):
    patient, _, _ = base
    ids = exercise_ids(client)
    t = client.post("/api/templates", json={"name": "Rodilla fase 1", "notes": "Dos veces al día",
                                            "items": [{"library_item_id": ids[0], "dosage": "3 x 10"},
                                                      {"library_item_id": ids[1], "notes": "Sin dolor"}]})
    assert t.status_code == 201, t.text
    t = t.json()
    assert [i["library_item_id"] for i in t["items"]] == ids and t["items"][0]["dosage"] == "3 x 10"
    page = client.get(f"/api/templates/{t['id']}/print", params={"patient_id": patient["id"]})
    assert page.status_code == 200 and "text/html" in page.headers["content-type"]
    assert "Ana Soto" in page.text and "Rodilla fase 1" in page.text and "3 x 10" in page.text and "Precauciones" in page.text
    assert "no está validado por un kinesiólogo" in page.text
    put = client.put(f"/api/templates/{t['id']}", json={"name": "Rodilla F1", "items": [{"library_item_id": ids[1]}]}).json()
    assert put["name"] == "Rodilla F1" and len(put["items"]) == 1
    assert len(client.get("/api/templates").json()) == 1 and client.get("/api/templates").json()[0]["item_count"] == 1
    assert client.delete(f"/api/templates/{t['id']}").status_code == 204
    assert client.get(f"/api/templates/{t['id']}").status_code == 404


def test_plantilla_escapa_html_y_valida(client):
    ids = exercise_ids(client, 1)
    t = client.post("/api/templates", json={"name": "<script>alert(1)</script>", "items": [{"library_item_id": ids[0], "notes": "<b>x</b>"}]}).json()
    html = client.get(f"/api/templates/{t['id']}/print").text
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;" in html and "&lt;b&gt;x&lt;/b&gt;" in html
    assert client.post("/api/templates", json={"name": "x", "items": [{"library_item_id": 999999}]}).status_code == 422
    assert len(client.get("/api/templates").json()) == 1  # la inválida se revirtió
    assert client.get(f"/api/templates/{t['id']}/print", params={"patient_id": 9999}).status_code == 404


def test_endpoints_nuevos_exigen_sesion(client):
    client.post("/api/auth/logout")
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as anon:
        for url in ("/api/plans", "/api/plans/1", "/api/templates", "/api/templates/1/print"):
            assert anon.get(url).status_code == 401, url
        assert anon.post("/api/plans/1/schedule", json={}).status_code == 401
