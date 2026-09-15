from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user as user_crud
from app.schemas.user import UserRead, UserCreate
from app.db.session import get_db
from app.models.user import User

router = APIRouter(prefix="/users", tags=["user"])

@router.post("", response_model=UserRead)
async def create_user(payload: UserCreate,
                      db: AsyncSession = Depends(get_db)) -> User:
    user = await user_crud.create_user(db, name=payload.name, email=payload.email, age=payload.age)
    return user