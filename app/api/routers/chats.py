from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import chat as chat_crud
from app.crud import message as message_crud
from app.api.deps import pagination, get_llm_client
from app.db.session import get_db
from app.models.message import Message
from app.schemas.chat import MessageRead, MessageCreate
from app.services.llm_client import LLMClient
from app.core.config import settings

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("")                      # POST /chats — создать диалог
async def create_chat(user_id: int, db: AsyncSession = Depends(get_db)) -> int:
    chat = await chat_crud.create_chat(db, user_id=user_id)
    return chat.id

@router.get("/{chat_id}/messages", response_model=list[MessageRead])    # история с пагинацией
async def get_messages(chat_id: int,
                       db: AsyncSession = Depends(get_db),
                       pagination=Depends(pagination)) -> list[Message]:
    messages = await message_crud.get_messages(db, chat_id, pagination.limit, pagination.offset)
    return messages

@router.post("/{chat_id}/messages", response_model=MessageRead)   # сообщение в диалог (+ ответ LLM, + сохранение)
async def create_message_in_dialog(chat_id: int,
                                   payload: MessageCreate,
                                   llm_client: LLMClient = Depends(get_llm_client),
                                   db: AsyncSession = Depends(get_db)) -> Message:
    if not await chat_crud.get_chat(db, chat_id):
        raise HTTPException(404)
    await message_crud.add_message(db, chat_id, role='user', content=payload.content)
    history_messages = await message_crud.get_messages(db, chat_id, None, None)
    messages = []
    for history_message in history_messages:
        messages.append({"role": history_message.role, "content": history_message.content})
    response = await llm_client.complete(messages, settings.llm_temperature, settings.llm_max_tokens)
    message = await message_crud.add_message(db, chat_id, role='assistant', content=response.content)
    return message