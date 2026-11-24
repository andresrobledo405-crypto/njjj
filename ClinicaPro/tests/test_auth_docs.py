from fastapi.testclient import TestClient

from app.main import app


def anon():
    return TestClient(app)


def test_api_exige_sesion(client):
    with anon() as c:
        assert c.get("/api/patients").status_code == 401
        assert c.get("/api/documents").status_code == 401
        assert c.get("/docs").status_code == 401
        assert c.get("/api/health").status_code == 200


def test_login_incorrecto_y_bloqueo(client):
    with anon() as c:
        for _ in range(5):
            assert c.post("/api/auth/login", json={"username": "admin", "password": "mala"}).status_code == 401
        assert c.post("/api/auth/login", json={"username": "admin", "password": "clave-de-prueba-123"}).status_code == 429
    from app.auth import throttle
    throttle.fails.clear()


def test_cookie_manipulada_rechazada(client):
    with anon() as c:
        c.cookies.set("clinicapro_session", client.cookies.get("clinicapro_session")[:-3] + "xxx")
        assert c.get("/api/auth/me").status_code == 401


def test_usuarios_y_roles(client):
    r = client.post("/api/users", json={"username": "pro0", "name": "Pro Cero", "password": "clave-larga-123", "role": "profesional"})
    assert r.status_code == 201
    with anon() as c:
        assert c.post("/api/auth/login", json={"username": "pro0", "password": "clave-larga-123"}).status_code == 200
        assert c.get("/api/documents").status_code == 200
        assert c.post("/api/documents", json={"category": "otro", "title": "x"}).status_code == 403
        assert c.get("/api/users").status_code == 403
    client.delete(f"/api/users/{r.json()['id']}")


def test_no_se_puede_dejar_sin_admin(client):
    me = client.get("/api/auth/me").json()
    assert client.delete(f"/api/users/{me['id']}").status_code == 409
    assert client.put(f"/api/users/{me['id']}", json={"username": "admin", "name": "A", "role": "profesional"}).status_code == 409


def test_documentos_sin_contenido_precargado(client):
    assert client.get("/api/documents").json() == []


def test_admin_gestiona_documentos_y_profesional_no(client):
    r = client.post("/api/documents", json={"category": "protocolo", "title": "Limpieza de boxes", "content": "Cada día"})
    assert r.status_code == 201
    doc_id = r.json()["id"]
    assert client.post("/api/documents", json={"category": "protocolo", "title": "Limpieza de boxes"}).status_code == 409
    assert client.post("/api/documents", json={"category": "otra", "title": "y"}).status_code == 422
    assert client.put(f"/api/documents/{doc_id}", json={"category": "tarifas", "title": "Limpieza de boxes", "content": "nuevo"}).json()["content"] == "nuevo"
    assert [d["title"] for d in client.get("/api/documents", params={"q": "limpieza"}).json()] == ["Limpieza de boxes"]
    assert client.get("/api/documents", params={"q": "zzzz"}).json() == []
    u = client.post("/api/users", json={"username": "pro1", "name": "Pro Uno", "password": "clave-larga-123", "role": "profesional"}).json()
    with anon() as c:
        c.post("/api/auth/login", json={"username": "pro1", "password": "clave-larga-123"})
        assert c.get(f"/api/documents/{doc_id}").status_code == 200
        assert c.put(f"/api/documents/{doc_id}", json={"title": "x"}).status_code == 403
        assert c.delete(f"/api/documents/{doc_id}").status_code == 403
    client.delete(f"/api/users/{u['id']}")
    assert client.delete(f"/api/documents/{doc_id}").status_code == 204
    assert client.get(f"/api/documents/{doc_id}").status_code == 404


def test_sin_rastro_de_kinesiologia(client):
    html = client.get("/").text
    assert "KinePro" not in html and "iblioteca" not in html
    assert client.get("/api/library").status_code == 404
    assert client.post("/api/library/ask", json={"question": "hola mundo"}).status_code == 404
    assert "ask_enabled" not in client.get("/api/meta").json()
