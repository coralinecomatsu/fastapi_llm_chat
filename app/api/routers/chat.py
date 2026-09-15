"""Чат-роутер. На этапе 1 свяжет MessageCreate -> LLMClient -> MessageRead.

Сейчас — минимальная заглушка, чтобы структура была цельной и запускалась.
"""
from fastapi import APIRouter

from app.schemas.chat import MessageCreate, MessageRead
from app.services.llm_client import LLMClient, logger

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=MessageRead)
async def create_message(payload: MessageCreate) -> MessageRead:
    llm_client = LLMClient("http://localhost:11434/v1/chat/completions", "qwen2.5:3b")
    messages = [
        {"role": "assistant", "content": "Ты мой крутой помощник!"},
        {"role": "user", "content": payload.content},
    ]
    response = await llm_client.complete(messages, 0.7, 100)
    logger.info(response)
    return MessageRead(
        role="assistant",
        content=response.content,
    )
