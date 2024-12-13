from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, func
from sqlalchemy.exc import IntegrityError

from db import DbSessionDep
from .models import User
from .exceptions import DuplicatedUsernameError, DuplicatedEmailError
from .schemas import SignupPayload

router = APIRouter(prefix="/account")


@router.get("/users/{username}")
async def user_detail(username: str, session: DbSessionDep) -> User:
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupPayload, session: DbSessionDep) -> User:
    stmt = select(func.count()).select_from(User).where(User.username == payload.username)
    result = await session.execute(stmt)
    count = result.scalar_one()
    if count > 0:
        raise DuplicatedUsernameError()

    user = User.model_validate(payload, from_attributes=True)
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        raise DuplicatedEmailError()
    return user
