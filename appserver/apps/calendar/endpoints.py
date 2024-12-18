from fastapi import APIRouter, status
from sqlmodel import select, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine

from appserver.apps.account.models import User
from appserver.apps.calendar.models import Calendar, TimeSlot
from appserver.apps.account.deps import CurrentUserDep, CurrentUserOptionalDep
from db import DbSessionDep

from .exceptions import CalendarAlreadyExistsError, CalendarNotFoundError, GuestPermissionError, HostNotFoundError, TimeSlotOverlapError
from .schemas import CalendarCreateIn, CalendarDetailOut, CalendarOut, CalendarUpdateIn, TimeSlotCreateIn, TimeSlotOut

router = APIRouter()

def check_overlap_sqlite(existing_weekdays: list[int], new_weekdays: list[int]) -> bool:
    return any(day in existing_weekdays for day in new_weekdays)


@router.get("/calendar/{host_username}", status_code=status.HTTP_200_OK)
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


@router.post(
    "/calendar",
    status_code=status.HTTP_201_CREATED,
    response_model=CalendarDetailOut,
)
async def create_calendar(
    user: CurrentUserDep,
    session: DbSessionDep,
    payload: CalendarCreateIn
) -> CalendarDetailOut:
    if not user.is_host:
        raise GuestPermissionError()
    
    calendar = Calendar(
        host_id=user.id,
        topics=payload.topics,
        description=payload.description,
        google_calendar_id=payload.google_calendar_id,
    )
    session.add(calendar)
    try:
        await session.commit()
    except IntegrityError as exc:
        raise CalendarAlreadyExistsError() from exc
    return calendar


@router.patch(
    "/calendar",
    status_code=status.HTTP_200_OK,
    response_model=CalendarDetailOut,
)
async def update_calendar(
    user: CurrentUserDep,
    session: DbSessionDep,
    payload: CalendarUpdateIn
) -> CalendarDetailOut:
    # 호스트가 아니면 캘린더를 수정할 수 없다.
    if not user.is_host:
        raise GuestPermissionError()

    # 사용자에게 캘린더가 없으면 HTTP 404 응답을 한다.
    if user.calendar is None:
        raise CalendarNotFoundError()

    # topics 값이 있으면 변경하고
    if payload.topics is not None:
        user.calendar.topics = payload.topics
    # description 값이 있으면 변경하고
    if payload.description is not None:
        user.calendar.description = payload.description
    # 구글 캘린더 ID 값이 있으면 변경하고
    if payload.google_calendar_id is not None:
        user.calendar.google_calendar_id = payload.google_calendar_id

    # 데이터베이스에 반영한다.
    await session.commit()

    return user.calendar


@router.post(
    "/time-slots",
    status_code=status.HTTP_201_CREATED,
    response_model=TimeSlotOut,
)
async def create_time_slot(
    user: CurrentUserDep,
    session: DbSessionDep,
    payload: TimeSlotCreateIn
) -> TimeSlotOut:
    if not user.is_host:
        raise GuestPermissionError()

    # 데이터베이스 엔진 확인
    engine: Engine = session.bind
    is_sqlite = engine.dialect.name == "sqlite"

    if is_sqlite:
        # 이미 존재하는 타임슬롯과 겹치는지 확인
        stmt = select(TimeSlot).where(
            and_(
                TimeSlot.calendar_id == user.calendar.id,
                TimeSlot.start_time < payload.end_time,
                TimeSlot.end_time > payload.start_time
            )
        )
        result = await session.execute(stmt)
        existing_time_slots = result.scalars().all()

        for existing_time_slot in existing_time_slots:
            if any(day in existing_time_slot.weekdays for day in payload.weekdays):
                raise TimeSlotOverlapError()
    else:
        # PostgreSQL: SQL에서 교집합 확인
        stmt = select(TimeSlot).where(
            and_(
                TimeSlot.calendar_id == user.calendar.id,
                func.jsonb_array_elements_text(TimeSlot.weekdays).in_(payload.weekdays),
                TimeSlot.start_time < payload.end_time,
                TimeSlot.end_time > payload.start_time
            )
        )
        result = await session.execute(stmt)
        existing_time_slot = result.scalar_one_or_none()

        if existing_time_slot:
            raise TimeSlotOverlapError()

    time_slot = TimeSlot(
        calendar_id=user.calendar.id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        weekdays=payload.weekdays,
    )
    session.add(time_slot)
    await session.commit()
    return time_slot
