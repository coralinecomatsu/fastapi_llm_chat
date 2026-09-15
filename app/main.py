"""Точка входа. main.py остаётся ТОНКИМ: только создание app и сборка роутеров.
Вся логика — в слоях (см. [F] Модуль 6).

Запуск: uvicorn app.main:app --reload
Docs:   http://localhost:8000/docs
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import chat, health
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: сюда позже — прогрев модели эмбеддингов, коннекты и т.п.
    yield
    # Shutdown: закрытие ресурсов.


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(health.router)
app.include_router(chat.router)
