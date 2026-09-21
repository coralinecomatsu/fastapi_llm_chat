"""Первый тест — дымовой. Проверяет, что приложение вообще живо.
Запуск: pytest
"""
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.api.deps import get_llm_client
from app.services.llm_client import LLMResponse


class FakeLLM:
    async def complete(self, messages, temperature, max_tokens):
        return LLMResponse(content="фейковый ответ",
                           prompt_tokens=0, completion_tokens=0, finish_reason="stop")

@pytest.fixture
def client_with_fake_llm():
    app.dependency_overrides[get_llm_client] = lambda: FakeLLM()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_health(client_with_fake_llm) -> None:
    resp = client_with_fake_llm.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_echo_uppercases(client_with_fake_llm) -> None:
    resp = client_with_fake_llm.get("/echo/hello")
    assert resp.status_code == 200
    assert resp.json() == {"text": "HELLO"}


def test_chat_rejects_empty(client_with_fake_llm) -> None:
    # min_length=1 в MessageCreate должен дать 422
    resp = client_with_fake_llm.post("/chat", json={"content": ""})
    assert resp.status_code == 422
