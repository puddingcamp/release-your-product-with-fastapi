from typing import Annotated
from datetime import datetime, timezone, timedelta

from sqlmodel import select
from fastapi import Depends, Cookie, HTTPException, status

from db import DbSessionDep

from .models import User
from .utils import decode_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .exceptions import InvalidTokenError, ExpiredTokenError, UserNotFoundError

async def get_current_user(
    auth_token: Annotated[str, Cookie(...)],
    db_session: DbSessionDep,
):
    try:
        decoded = decode_token(auth_token)
    except Exception as e:
        raise InvalidTokenError() from e

    expires_at = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    if now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) < expires_at:
        raise ExpiredTokenError()

    stmt = select(User).where(User.username == decoded["sub"])
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UserNotFoundError()
    return user 


CurrentUserDep = Annotated[User, Depends(get_current_user)]

