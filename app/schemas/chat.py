"""Pydantic-схемы чата. Разделяем вход и выход (см. [F] Модуль 2).

На этапе 1 этого хватит; позже добавим MessageRead с id/created_at,
когда сообщения начнут жить в БД (этап 3).
"""
from datetime import datetime

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Что присылает клиент."""
    content: str = Field(min_length=1, max_length=8000)


class MessageRead(BaseModel):
    """Что отдаём наружу."""
    id: int
    role: str
    content: str
    chat_id: int
    created_at: datetime
    model_config = {"from_attributes": True}
