"""Первый тест — дымовой. Проверяет, что приложение вообще живо.
Запуск: pytest
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_echo_uppercases() -> None:
    resp = client.get("/echo/hello")
    assert resp.status_code == 200
    assert resp.json() == {"text": "HELLO"}


def test_chat_stub_echoes() -> None:
    resp = client.post("/chat", json={"content": "привет"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "assistant"
    assert "привет" in body["content"]


def test_chat_rejects_empty() -> None:
    # min_length=1 в MessageCreate должен дать 422
    resp = client.post("/chat", json={"content": ""})
    assert resp.status_code == 422
