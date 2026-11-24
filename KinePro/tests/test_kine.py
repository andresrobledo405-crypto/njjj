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


def test_numero_de_sesion_cuenta_las_atenciones_ya_hechas(client, base):
    patient, _, doctor = base
    plan = make_plan(client, patient, doctor, total=5)
    consult(client, patient, doctor, plan)
    consult(client, patient, doctor, plan)
    a = client.post("/api/appointments", json=appt(patient, doctor, "2030-06-03T09:00", plan_id=plan["id"])).json()
    day = client.get("/api/agenda", params={"day": "2030-06-03"}).json()
    assert day[0]["session_no"] == 3 and day[0]["plan_total"] == 5
    client.post(f"/api/appointments/{a['id']}/status", data={"status": "cancelled"})
    assert client.get("/api/agenda", params={"day": "2030-06-03"}).json()[0]["session_no"] is None


def test_no_se_registra_dos_veces_la_misma_cita(client, base):
    patient, _, doctor = base
    plan = make_plan(client, patient, doctor, total=5)
    a = client.post("/api/appointments", json=appt(patient, doctor, plan_id=plan["id"])).json()
    form = {"patient_id": patient["id"], "professional_id": doctor["id"], "appointment_id": a["id"]}
    assert client.post("/api/consultations", data=form).status_code == 201
    assert client.post("/api/consultations", data=form).status_code == 409
    assert client.get(f"/api/plans/{plan['id']}").json()["sessions_done"] == 1


def test_plan_cerrado_no_acepta_sesiones_nuevas(client, base):
    patient, _, doctor = base
    plan = make_plan(client, patient, doctor, total=1)
    consult(client, patient, doctor, plan)  # lo completa
    assert consult(client, patient, doctor, plan).status_code == 409
    assert client.post("/api/appointments", json=appt(patient, doctor, plan_id=plan["id"])).status_code == 409


def test_bajar_el_total_cierra_el_plan(client, base):
    patient, _, doctor = base
    plan = make_plan(client, patient, doctor, total=5)
    consult(client, patient, doctor, plan)
    consult(client, patient, doctor, plan)
    body = {"patient_id": patient["id"], "professional_id": doctor["id"], "title": plan["title"], "total_sessions": 2}
    assert client.put(f"/api/plans/{plan['id']}", json=body).json()["status"] == "completed"


def test_put_de_cita_sin_plan_no_la_desvincula(client, base):
    patient, _, doctor = base
    plan = make_plan(client, patient, doctor)
    a = client.post("/api/appointments", json=appt(patient, doctor, plan_id=plan["id"])).json()
    r = client.put(f"/api/appointments/{a['id']}", json=appt(patient, doctor, "2030-05-10T11:00")).json()
    assert r["plan_id"] == plan["id"]


def test_no_se_borra_una_entrada_enlazada(client, base):
    patient, _, doctor = base
    ids = exercise_ids(client, 1)
    client.post("/api/templates", json={"name": "T", "items": [{"library_item_id": ids[0]}]})
    consult(client, patient, doctor, library_ids=str(ids[0]))
    assert client.delete(f"/api/library/{ids[0]}").status_code == 409
    assert client.get(f"/api/library/{ids[0]}").status_code == 200
    assert client.get("/api/consultations").json()[0]["library"][0]["id"] == ids[0]


def test_csv_neutraliza_formulas(client, base):
    client.post("/api/patients", json={"name": "=HYPERLINK(\"x\")"})
    csv = client.get("/api/export/payments.csv")
    patient = client.post("/api/patients", json={"name": "@cmd"}).json()
    client.post("/api/payments", json={"patient_id": patient["id"], "concept": "+1+1", "amount": 1000})
    body = client.get("/api/export/payments.csv").text
    assert "'@cmd" in body and "'+1+1" in body and csv.status_code == 200


def test_usuario_desactivado_pierde_la_sesion(client):
    u = client.post("/api/users", json={"username": "kine1", "name": "Kine", "password": "clave-larga-123", "role": "profesional"}).json()
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as other:
        assert other.post("/api/auth/login", json={"username": "kine1", "password": "clave-larga-123"}).status_code == 200
        assert other.get("/api/plans").status_code == 200
        client.put(f"/api/users/{u['id']}", json={"username": "kine1", "name": "Kine", "role": "profesional", "active": False})
        assert other.get("/api/plans").status_code == 401
    client.delete(f"/api/users/{u['id']}")


def test_interfaz_y_recursos_estaticos(client):
    page = client.get("/")
    assert page.status_code == 200 and "/static/app.js" in page.text and "/static/app.css" in page.text
    assert "default-src 'self'" in page.headers["content-security-policy"]
    for path in ("/static/app.js", "/static/app.css", "/static/icon.svg",
                 "/static/fonts/fraunces-latin-wght-normal.woff2", "/static/fonts/figtree-latin-wght-normal.woff2"):
        assert client.get(path).status_code == 200, path
    assert "http://" not in page.text.replace("http://www.w3.org", "") and "cdn" not in page.text.lower()  # sin recursos externos
