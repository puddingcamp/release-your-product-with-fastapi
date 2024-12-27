from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import select, func, update, delete, true
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone

from appserver.db import DbSessionDep
from .models import User
from .exceptions import DuplicatedUsernameError, DuplicatedEmailError, PasswordMismatchError, UserNotFoundError
from .schemas import LoginPayload, SignupPayload, UpdateUserPayload, UserDetailOut, UserOut
from .utils import (
    verify_password, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from .deps import CurrentUserDep
from .constants import AUTH_TOKEN_COOKIE_NAME

router = APIRouter(prefix="/account")


@router.get("/users/{username}")
async def user_detail(username: str, session: DbSessionDep) -> User:
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserOut)
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


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(payload: LoginPayload, session: DbSessionDep) -> JSONResponse:
    stmt = select(User).where(User.username == payload.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UserNotFoundError()

    is_valid = verify_password(payload.password, user.hashed_password)
    if not is_valid:
        raise PasswordMismatchError()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "display_name": user.display_name,
            "is_host": user.is_host,
        },
        expires_delta=access_token_expires
    )

    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.model_dump(mode="json", exclude={"hashed_password", "email"})
    }

    now = datetime.now(timezone.utc)

    res = JSONResponse(response_data, status_code=status.HTTP_200_OK)
    res.set_cookie(
        key=AUTH_TOKEN_COOKIE_NAME,
        value=access_token,
        expires=now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        httponly=True,
        secure=True,
        samesite="strict"
    )
    return res


@router.get("/@me", response_model=UserDetailOut)
async def me(user: CurrentUserDep) -> User:
    return user


@router.patch("/@me", response_model=UserDetailOut)
async def update_user(
    user: CurrentUserDep,
    payload: UpdateUserPayload,
    session: DbSessionDep
) -> User:
    updated_data = payload.model_dump(exclude_none=True, exclude={"password", "password_again"})

    stmt = update(User).where(User.username == user.username).values(**updated_data)
    await session.execute(stmt)
    await session.commit()
    return user


@router.delete("/logout", status_code=status.HTTP_200_OK)
async def logout(user: CurrentUserDep) -> JSONResponse:
    res = JSONResponse({})
    res.delete_cookie(AUTH_TOKEN_COOKIE_NAME)
    return res


@router.delete("/unregister", status_code=status.HTTP_204_NO_CONTENT)
async def unregister(user: CurrentUserDep, session: DbSessionDep) -> None:
    stmt = delete(User).where(User.username == user.username)
    await session.execute(stmt)
    await session.commit()
    return None


@router.get(
    "/hosts",
    status_code=status.HTTP_200_OK,
    response_model=list[UserOut],
)
async def get_hosts(
    user: CurrentUserDep,
    session: DbSessionDep,
) -> list[User]:
    stmt = select(User).where(User.is_active.is_(true())).where(User.is_host.is_(true()))
    result = await session.execute(stmt)
    return result.scalars().all()
