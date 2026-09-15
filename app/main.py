"""Точка входа. main.py остаётся ТОНКИМ: только создание app и сборка роутеров.
Вся логика — в слоях (см. [F] Модуль 6).

Запуск: uvicorn app.main:app --reload
Docs:   http://localhost:8000/docs
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import chat, health, chats, users
from app.services.llm_client import LLMClient
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base
import app.models  # noqa: F401 — чтобы модели зарегистрировались в Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: сюда позже — прогрев модели эмбеддингов, коннекты и т.п.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.state.llm_client = LLMClient(settings.llm_base_url, settings.llm_model)
    yield
    # Shutdown: закрытие ресурсов.
    await app.state.llm_client.aclose()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(chats.router)
app.include_router(users.router)
