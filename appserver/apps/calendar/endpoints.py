from fastapi import APIRouter, status
from sqlmodel import select

from appserver.apps.account.models import User
from appserver.apps.calendar.models import Calendar
from appserver.apps.account.deps import CurrentUserOptionalDep
from db import DbSessionDep

from .exceptions import CalendarNotFoundError, HostNotFoundError
from .schemas import CalendarDetailOut, CalendarOut

router = APIRouter()


async def host_calendar_detail(
    host_username: str,
    user: CurrentUserOptionalDep,
    session: DbSessionDep
) -> CalendarOut | CalendarDetailOut:
    stmt = select(User).where(User.username == host_username)
    result = await session.execute(stmt)
    host = result.scalar_one_or_none()
    if host is None:
        raise HostNotFoundError()
    
    stmt = select(Calendar).where(Calendar.host_id == host.id)
    result = await session.execute(stmt)
    calendar = result.scalar_one_or_none()
    if calendar is None:
        raise CalendarNotFoundError()

    if user is not None and user.id == host.id:
        return CalendarDetailOut.model_validate(calendar)

    return CalendarOut.model_validate(calendar)