"""Async-движок и сессия SQLAlchemy 2.x.

expire_on_commit=False — критично для async: иначе после commit объекты
"протухают" и обращение к атрибуту вне контекста даёт MissingGreenlet.
(см. [F] Модуль 4)
"""
from typing import Annotated
from collections.abc import AsyncGenerator
from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """DI-зависимость: сессия на время запроса, гарантированное закрытие."""
    async with SessionLocal() as session:
        yield session

def get_current_user(token: str, db = Depends(get_db)): # под-зависимость
    user = db.get_user_by_token(token)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    return user

db = Annotated[SessionLocal, Depends(get_db)]