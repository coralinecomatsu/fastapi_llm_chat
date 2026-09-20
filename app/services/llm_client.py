"""Клиент к OpenAI-совместимому LLM API."""
import json
import logging
from dataclasses import dataclass

import httpx

from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str


class LLMClient:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url
        self.model = model
        self._client = httpx.AsyncClient()

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> LLMResponse:
        body = {
            "model": self.model, "messages": messages,
            "temperature": temperature, "max_tokens": max_tokens,
            "stream": False,
        }
        try:
            response = await self._client.post(self.base_url, json=body)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise LLMError(f"HTTP error {exc.response.status_code}: {exc.response.text}") from exc
        except httpx.RequestError as exc:
            raise LLMError(f"Request failed: {exc}") from exc

        data = response.json()
        choice = data["choices"][0]
        if choice["finish_reason"] == "length":
            logger.warning(f'finish_reason is {choice["finish_reason"]}')

        return LLMResponse(
            content=choice["message"]["content"],
            prompt_tokens=data["usage"]["prompt_tokens"],
            completion_tokens=data["usage"]["completion_tokens"],
            finish_reason=choice["finish_reason"],
        )

    async def stream_chat(self, messages, temperature, max_tokens):
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with self._client.stream("POST", self.base_url, json=body) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue

                if line.startswith("data:"):
                    payload = line[len("data:"):].strip()
                    if payload == "[DONE]":
                        return

                    json_data = json.loads(payload)
                    delta = json_data["choices"][0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content

    async def aclose(self):
        await self._client.aclose()

class LLMClientExample:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url
        self.model = model
        self._client = httpx.AsyncClient()
        # клиент создан, но соединение ещё не открыто —
        # httpx открывает его лениво, при первом реальном запросе

    async def chat(self, model, messages, temperature, max_tokens) -> LLMResponse:
        body = {
            "model": model, "messages": messages,
            "temperature": temperature, "max_tokens": max_tokens,
            "stream": False,
        }
        try:
            response = await self._client.post(self.base_url, json=body)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise LLMError(f"HTTP error {exc.response.status_code}: {exc.response.text}") from exc
        except httpx.RequestError as exc:
            raise LLMError(f"Request failed: {exc}") from exc

        data = response.json()
        choice = data["choices"][0]
        if choice["finish_reason"] == "length":
            logger.warning(f'finish_reason is {choice["finish_reason"]}')

        return LLMResponse(
            content=choice["message"]["content"],
            prompt_tokens=data["usage"]["prompt_tokens"],
            completion_tokens=data["usage"]["completion_tokens"],
            finish_reason=choice["finish_reason"],
        )

    async def stream_chat(self, model, messages, temperature, max_tokens):
        body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with self._client.stream("POST", self.base_url, json=body) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue

                if line.startswith("data:"):
                    payload = line[len("data:"):].strip()
                    if payload == "[DONE]":
                        return

                    json_data = json.loads(payload)
                    delta = json_data["choices"][0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content

    async def aclose(self):
        await self._client.aclose()