"""Чат-роутер. На этапе 1 свяжет MessageCreate -> LLMClient -> MessageRead.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_llm_client
from app.schemas.chat import MessageCreate, MessageRead
from app.services.llm_client import LLMClient
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=MessageRead)
async def create_message(payload: MessageCreate,
                         llm_client: LLMClient = Depends(get_llm_client),) -> MessageRead:
    messages = [
        {"role": "system", "content": "Ты мой крутой помощник!"},
        {"role": "user", "content": payload.content},
    ]
    response = await llm_client.complete(messages, settings.llm_temperature, settings.llm_max_tokens)
    return MessageRead(
        role="assistant",
        content=response.content,
    )

@router.post("/stream", response_class=StreamingResponse)
async def stream_message(payload: MessageCreate,
                         llm_client: LLMClient = Depends(get_llm_client),) -> StreamingResponse:
    messages = [
        {"role": "system", "content": "Ты мой крутой помощник!"},
        {"role": "user", "content": payload.content},
    ]
    generator = llm_client.stream_chat(messages, settings.llm_temperature, settings.llm_max_tokens)
    return StreamingResponse(generator, media_type="text/plain")
