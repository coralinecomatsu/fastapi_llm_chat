from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


async def add_message(db: AsyncSession, chat_id: int, role: str, content) -> Message:
    message = Message(chat_id=chat_id, role=role, content=content)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

async def get_messages(db: AsyncSession, chat_id: int,
                       limit: int|None = None, offset: int|None = None) -> list[Message]:
    stmt = select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()