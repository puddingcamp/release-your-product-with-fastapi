from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, SQLModel

from db import create_async_engine, create_session
from .models import User

router = APIRouter(prefix="/account")


@router.get("/users/{username}")
async def user_detail(username: str) -> User:
    dsn = "sqlite+aiosqlite:///./test.db"
    engine = create_async_engine(dsn)
    session_factory = create_session(engine)

    async with session_factory() as session:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

