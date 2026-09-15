from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat


async def create_chat(db: AsyncSession, user_id: int) -> Chat:
    chat = Chat(user_id=user_id)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat

async def get_chat(db: AsyncSession, chat_id: int) -> Chat | None:
    if chat_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    stmt = select(Chat).where(Chat.id == chat_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()