import httpx
import pytest

from app import main


class FakeResponse:
    def raise_for_status(self): pass
    def json(self): return {"choices": [{"message": {"content": "Respuesta de prueba [Test de Lachman]"}}]}


def test_sin_clave_responde_503(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert client.post("/api/library/ask", json={"question": "¿Qué es Lachman?"}).status_code == 503
    assert client.get("/api/meta").json()["ask_enabled"] is False


def test_con_clave_envia_solo_biblioteca(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    sent = {}
    def fake_post(url, headers, json, timeout):
        sent.update(url=url, body=json, auth=headers["Authorization"])
        return FakeResponse()
    monkeypatch.setattr(main.httpx, "post", fake_post)
    client.post("/api/patients", json={"name": "Paciente Secreto Gómez"})
    r = client.post("/api/library/ask", json={"question": "¿Cómo se hace la prueba de Lachman?"})
    assert r.status_code == 200 and r.json()["answer"].startswith("Respuesta")
    assert any("Lachman" in s["title"] for s in r.json()["sources"])
    assert "Paciente Secreto" not in str(sent["body"])
    assert sent["url"].startswith("https://api.openai.com/")


def test_sin_resultados_no_llama_a_openai(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(main.httpx, "post", lambda *a, **k: pytest.fail("no debía llamar"))
    r = client.post("/api/library/ask", json={"question": "xyzqwerty plmokn"})
    assert r.status_code == 200 and r.json()["sources"] == []


def test_error_upstream_da_502_y_limite(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    def boom(*a, **k): raise httpx.ConnectError("x")
    monkeypatch.setattr(main.httpx, "post", boom)
    assert client.post("/api/library/ask", json={"question": "¿Qué es Lachman?"}).status_code == 502
    monkeypatch.setattr(main, "ASK_LIMIT_PER_HOUR", 1)
    assert client.post("/api/library/ask", json={"question": "¿Qué es Lachman?"}).status_code == 429
    main.ask_log.clear()


def test_requiere_sesion():
    from fastapi.testclient import TestClient
    with TestClient(main.app) as c:
        assert c.post("/api/library/ask", json={"question": "¿Qué es Lachman?"}).status_code == 401
