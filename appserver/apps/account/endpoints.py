from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from db import DbSessionDep
from .models import User

router = APIRouter(prefix="/account")


@router.get("/users/{username}")
async def user_detail(username: str, session: DbSessionDep) -> User:
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

