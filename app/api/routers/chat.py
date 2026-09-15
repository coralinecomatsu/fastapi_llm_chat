"""Чат-роутер. На этапе 1 свяжет MessageCreate -> LLMClient -> MessageRead.

Сейчас — минимальная заглушка, чтобы структура была цельной и запускалась.
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_llm_client
from app.schemas.chat import MessageCreate, MessageRead
from app.services.llm_client import LLMClient

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=MessageRead)
async def create_message(payload: MessageCreate,
                         llm_client: LLMClient = Depends(get_llm_client),) -> MessageRead:
    messages = [
        {"role": "system", "content": "Ты мой крутой помощник!"},
        {"role": "user", "content": payload.content},
    ]
    response = await llm_client.complete(messages, 0.7, 100)
    return MessageRead(
        role="assistant",
        content=response.content,
    )
