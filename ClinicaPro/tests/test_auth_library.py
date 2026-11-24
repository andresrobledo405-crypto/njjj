from fastapi.testclient import TestClient

from app.main import app


def anon():
    return TestClient(app)


def test_api_exige_sesion(client):
    with anon() as c:
        assert c.get("/api/patients").status_code == 401
        assert c.get("/api/library").status_code == 401
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
    r = client.post("/api/users", json={"username": "kine1", "name": "Kine Uno", "password": "clave-larga-123", "role": "profesional"})
    assert r.status_code == 201
    with anon() as c:
        assert c.post("/api/auth/login", json={"username": "kine1", "password": "clave-larga-123"}).status_code == 200
        assert c.get("/api/library").status_code == 200
        assert c.post("/api/library", json={"category": "glosario", "title": "x"}).status_code == 403
        assert c.get("/api/users").status_code == 403
    client.delete(f"/api/users/{r.json()['id']}")


def test_no_se_puede_dejar_sin_admin(client):
    me = client.get("/api/auth/me").json()
    assert client.delete(f"/api/users/{me['id']}").status_code == 409
    assert client.put(f"/api/users/{me['id']}", json={"username": "admin", "name": "A", "role": "profesional"}).status_code == 409


def test_biblioteca_completa_y_busqueda(client):
    meta = client.get("/api/library/meta").json()
    assert meta["total"] >= 100
    assert all(c["count"] > 0 for c in meta["categories"])
    # búsqueda sin tildes y por sinónimo/tag
    titulos = [i["title"] for i in client.get("/api/library", params={"q": "ciatica"}).json()]
    assert any("Hernia discal" in t or "Lasègue" in t for t in titulos)
    assert client.get("/api/library", params={"category": "ejercicio", "region": "Hombro"}).json()
    assert client.get("/api/library", params={"q": "zzzz-no-existe"}).json() == []


def test_admin_edita_biblioteca(client):
    r = client.post("/api/library", json={"category": "glosario", "title": "Término de prueba", "content": "x"})
    assert r.status_code == 201
    assert client.post("/api/library", json={"category": "glosario", "title": "Término de prueba"}).status_code == 409
    assert client.post("/api/library", json={"category": "otra", "title": "y"}).status_code == 422
    assert client.put(f"/api/library/{r.json()['id']}", json={"category": "glosario", "title": "Término de prueba", "content": "nuevo"}).json()["content"] == "nuevo"
    assert client.delete(f"/api/library/{r.json()['id']}").status_code == 204


def test_seed_no_pisa_ediciones(client):
    from app.db import get_connection
    from app.library import seed_library
    item = client.get("/api/library", params={"q": "Lachman"}).json()[0]
    client.put(f"/api/library/{item['id']}", json={**item, "summary": "EDITADO"})
    conn = get_connection()
    assert seed_library(conn) == 0
    conn.close()
    assert client.get(f"/api/library/{item['id']}").json()["summary"] == "EDITADO"
