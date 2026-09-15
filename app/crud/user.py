from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


async def create_user(db: AsyncSession, email: str, name: str, age: int) -> User:
    user = User(name=name, email=email, age=age)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user