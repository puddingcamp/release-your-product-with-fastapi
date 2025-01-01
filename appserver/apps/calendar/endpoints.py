import asyncio
import calendar
from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, File, UploadFile, status, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import select, and_, func, true, extract
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import selectinload

from appserver.apps.account.models import User
from appserver.apps.account.deps import CurrentUserDep, CurrentUserOptionalDep
from appserver.db import DbSessionDep
from appserver.libs.google.calendar.deps import GoogleCalendarServiceDep

from .enums import AttendanceStatus
from .exceptions import (
    BookingAlreadyExistsError,
    CalendarAlreadyExistsError,
    CalendarNotFoundError,
    GuestPermissionError,
    HostNotFoundError,
    PastBookingError,
    SelfBookingError,
    TimeSlotNotFoundError,
    TimeSlotOverlapError,
)

from .deps import UtcNow
from .models import Booking, BookingFile, Calendar, TimeSlot
from .schemas import (
    BookingCreateIn,
    BookingOut,
    CalendarCreateIn,
    CalendarDetailOut,
    CalendarOut,
    CalendarUpdateIn,
    GoogleCalendarEventOut,
    GuestBookingUpdateIn,
    HostBookingStatusUpdateIn,
    HostBookingUpdateIn,
    PaginatedBookingOut,
    SimpleBookingOut,
    TimeSlotCreateIn,
    TimeSlotOut,
)


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


@router.get(
    "/calendar/{host_username}/bookings",
    status_code=status.HTTP_200_OK,
    response_model=list[SimpleBookingOut | GoogleCalendarEventOut],
)
async def host_calendar_bookings(
    host_username: str,
    session: DbSessionDep,
    year: Annotated[int, Query(ge=2024, le=2025)],
    month: Annotated[int, Query(ge=1, le=12)],
    service: GoogleCalendarServiceDep,
) -> list[SimpleBookingOut | GoogleCalendarEventOut]:
    stmt = select(User).where(User.username == host_username)
    result = await session.execute(stmt)
    host = result.scalar_one_or_none()

    if host is None or host.calendar is None:
        raise HostNotFoundError()

    stmt = (
        select(Booking)
        .where(Booking.time_slot.has(TimeSlot.calendar_id == host.calendar.id))
        .where(extract('year', Booking.when) == year)
        .where(extract('month', Booking.when) == month)
        .order_by(Booking.when.desc())
    )
    result = await session.execute(stmt)
    bookings = result.scalars().all()

    last_day = calendar.monthrange(year, month)[1]
    events = await service.event_list(
        time_min=datetime(year, month, 1).astimezone(timezone.utc),
        time_max=datetime(year, month, last_day).astimezone(timezone.utc),
        google_calendar_id=host.calendar.google_calendar_id,
    )
    for event in events:
        bookings.append(GoogleCalendarEventOut.model_validate(event))

    return bookings


@router.get(
    "/calendar/{host_username}/bookings/stream",
    status_code=status.HTTP_200_OK,
)
async def host_calendar_bookings_stream(
    host_username: str,
    session: DbSessionDep,
    year: Annotated[int, Query(ge=2024, le=2025)],
    month: Annotated[int, Query(ge=1, le=12)],
    service: GoogleCalendarServiceDep,
) -> StreamingResponse:
    stmt = select(User).where(User.username == host_username)
    result = await session.execute(stmt)
    host = result.scalar_one_or_none()

    if host is None or host.calendar is None:
        raise HostNotFoundError()

    stmt = (
        select(Booking)
        .where(Booking.time_slot.has(TimeSlot.calendar_id == host.calendar.id))
        .where(extract('year', Booking.when) == year)
        .where(extract('month', Booking.when) == month)
        .order_by(Booking.when.desc())
    )
    result = await session.execute(stmt)
    bookings = result.scalars().all()
    async def _stream_bookings():
        for booking in bookings:
            yield f"{SimpleBookingOut.model_validate(booking).model_dump_json()}\n"

        await asyncio.sleep(3)
        last_day = calendar.monthrange(year, month)[1]
        events = await service.event_list(
            time_min=datetime(year, month, 1).astimezone(timezone.utc),
            time_max=datetime(year, month, last_day).astimezone(timezone.utc),
            google_calendar_id=host.calendar.google_calendar_id,
        )
        for event in events:
            yield f"{GoogleCalendarEventOut.model_validate(event).model_dump_json()}\n"

    return StreamingResponse(
        _stream_bookings(),
        media_type="application/x-ndjson",
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "/guest-calendar/bookings",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedBookingOut,
)
async def guest_calendar_bookings(
    user: CurrentUserDep,
    session: DbSessionDep,
    page: Annotated[int, Query(ge=1)],
    page_size: Annotated[int, Query(ge=1, le=50)],
) -> PaginatedBookingOut:
    stmt = (
        select(Booking)
        .options(selectinload(Booking.files))
        .where(Booking.guest_id == user.id)
        .order_by(Booking.when.desc(), Booking.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await session.execute(stmt)
    count_stmt = select(func.count()).select_from(Booking).where(Booking.guest_id == user.id)
    count_result = await session.execute(count_stmt)
    
    return PaginatedBookingOut(
        bookings=result.scalars().all(),
        total_count=count_result.scalar_one_or_none() or 0,
    )


@router.post(
    "/calendar",
    status_code=status.HTTP_201_CREATED,
    response_model=CalendarDetailOut,
)
async def create_calendar(
    user: CurrentUserDep,
    session: DbSessionDep,
    payload: CalendarCreateIn,
    service: GoogleCalendarServiceDep,
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


@router.post(
    "/bookings/{host_username}",
    status_code=status.HTTP_201_CREATED,
    response_model=BookingOut,
)
async def create_booking(
    host_username: str,
    user: CurrentUserDep,
    session: DbSessionDep,
    payload: BookingCreateIn,
    service: GoogleCalendarServiceDep,
    background_tasks: BackgroundTasks,
) -> BookingOut:
    stmt = (
        select(User)
        .where(User.username == host_username)
        .where(User.is_host.is_(true()))
    )
    result = await session.execute(stmt)
    host = result.scalar_one_or_none()
    if host is None or host.calendar is None:
        raise HostNotFoundError()

    if user.id == host.id:
        raise SelfBookingError()

    if payload.when < datetime.now(timezone.utc).date():
        raise PastBookingError()

    stmt = (
        select(TimeSlot)
        .where(TimeSlot.id == payload.time_slot_id)
        .where(TimeSlot.calendar_id == host.calendar.id)
    )
    result = await session.execute(stmt)
    time_slot = result.scalar_one_or_none()
    if time_slot is None:
        raise TimeSlotNotFoundError()
    if payload.when.weekday() not in time_slot.weekdays:
        raise TimeSlotNotFoundError()

    stmt = (
        select(func.count())
        .select_from(Booking)
        .where(Booking.guest_id == user.id)
        .where(Booking.when == payload.when)
        .where(Booking.time_slot_id == payload.time_slot_id)
    )
    result = await session.execute(stmt)
    exists = result.scalar_one_or_none()
    if exists:
        raise BookingAlreadyExistsError()
    booking = Booking(
        guest_id=user.id,
        when=payload.when,
        topic=payload.topic,
        description=payload.description,
        time_slot_id=payload.time_slot_id,
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking, ["files", "time_slot"])

    start_datetime = datetime.combine(booking.when, time_slot.start_time)
    end_datetime = datetime.combine(booking.when, time_slot.end_time)

    async def _apply_event_id():
        event = await service.create_event(
            start_datetime=start_datetime.astimezone(timezone.utc),
            end_datetime=end_datetime.astimezone(timezone.utc),
            summary=booking.topic,
            description=booking.description,
            google_calendar_id=host.calendar.google_calendar_id,
        )
        booking.google_event_id = event["id"]
        await session.commit()

    background_tasks.add_task(_apply_event_id)
    
    return booking


@router.get(
    "/bookings",
    status_code=status.HTTP_200_OK,
    response_model=list[BookingOut],
)
async def get_host_bookings_by_month(
    user: CurrentUserDep,
    session: DbSessionDep,
    page: Annotated[int, Query(ge=1)],
    page_size: Annotated[int, Query(ge=1, le=50)],
) -> list[BookingOut]:
    if not user.is_host or user.calendar is None:
        raise HostNotFoundError()
    
    stmt = (
        select(Booking)
        .where(Booking.time_slot.has(TimeSlot.calendar_id == user.calendar.id))
        .order_by(Booking.when.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await session.execute(stmt)

    return result.scalars().all()    


@router.get(
    "/bookings/{booking_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookingOut,
)
async def get_booking_by_id(
    user: CurrentUserDep,
    session: DbSessionDep,
    booking_id: int
) -> BookingOut:
    stmt = select(Booking).where(Booking.id == booking_id)
    if user.is_host and user.calendar is not None:
        stmt = (
            stmt
            .join(Booking.time_slot)
            .options(selectinload(Booking.files))
            .where((TimeSlot.calendar_id == user.calendar.id) | (Booking.guest_id == user.id))
        )
    else:
        stmt = stmt.where(Booking.guest_id == user.id).options(selectinload(Booking.files))

    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="예약 내역이 없습니다.")
    return booking


@router.patch(
    "/bookings/{booking_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookingOut,
)
async def host_update_booking(
    user: CurrentUserDep,
    session: DbSessionDep,
    booking_id: int,
    now: UtcNow,
    payload: HostBookingUpdateIn,
    service: GoogleCalendarServiceDep,
    background_tasks: BackgroundTasks,
) -> BookingOut:
    if not user.is_host or user.calendar is None:
        raise HostNotFoundError()

    stmt = (
        select(Booking)
        .join(Booking.time_slot)
        .where(Booking.id == booking_id)
        .where(TimeSlot.calendar_id == user.calendar.id)
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="예약 내역이 없습니다.")
    
    if booking.when < now.date():
        raise PastBookingError()
        
    if payload.time_slot_id is not None:
        stmt = (
            select(TimeSlot)
            .where(TimeSlot.id == payload.time_slot_id)
            .where(TimeSlot.calendar_id == user.calendar.id)
        )
        result = await session.execute(stmt)
        time_slot = result.scalar_one_or_none()
        if time_slot is None:
            raise TimeSlotNotFoundError()
        
        booking.time_slot_id = time_slot.id

    if payload.when is not None:
        if payload.when.weekday() not in booking.time_slot.weekdays:
            raise TimeSlotNotFoundError()
        booking.when = payload.when

    await session.commit()
    await session.refresh(booking)
 
    start_datetime = datetime.combine(booking.when, booking.time_slot.start_time)
    end_datetime = datetime.combine(booking.when, booking.time_slot.end_time)

    if booking.google_event_id:
        async def _update_google_calendar_event():
            await service.update_event(
                event_id=booking.google_event_id,
                start_datetime=start_datetime.astimezone(timezone.utc),
                end_datetime=end_datetime.astimezone(timezone.utc),
                summary=booking.topic,
                description=booking.description,
                google_calendar_id=user.calendar.google_calendar_id,
            )
            
        background_tasks.add_task(_update_google_calendar_event)
   
    return booking


@router.patch(
    "/guest-bookings/{booking_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookingOut,
)
async def guest_update_booking(
    user: CurrentUserDep,
    session: DbSessionDep,
    booking_id: int,
    now: UtcNow,
    payload: GuestBookingUpdateIn,
    service: GoogleCalendarServiceDep,
    background_tasks: BackgroundTasks,
) -> BookingOut:
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .where(Booking.guest_id == user.id)
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="예약 내역이 없습니다.")
    
    if booking.when <= now.date():
        raise PastBookingError()

    if payload.time_slot_id is not None:
        stmt = (
            select(TimeSlot)
            .where(TimeSlot.id == payload.time_slot_id)
            .where(TimeSlot.calendar_id == booking.time_slot.calendar_id)
        )
        result = await session.execute(stmt)
        time_slot = result.scalar_one_or_none()
        if time_slot is None:
            raise TimeSlotNotFoundError()
        booking.time_slot_id = time_slot.id

    if payload.topic is not None:
        booking.topic = payload.topic
    if payload.description is not None:
        booking.description = payload.description
    if payload.when is not None:
        if payload.when.weekday() not in booking.time_slot.weekdays:
            raise TimeSlotNotFoundError()
        booking.when = payload.when
    await session.commit()
    await session.refresh(booking)

    if booking.google_event_id:
        start_datetime = datetime.combine(booking.when, booking.time_slot.start_time)
        end_datetime = datetime.combine(booking.when, booking.time_slot.end_time)

        async def _update_google_calendar_event():
            await service.update_event(
                event_id=booking.google_event_id,
                start_datetime=start_datetime.astimezone(timezone.utc),
                end_datetime=end_datetime.astimezone(timezone.utc),
                summary=booking.topic,
                description=booking.description,
                google_calendar_id=booking.time_slot.calendar.google_calendar_id,
            )
            
        background_tasks.add_task(_update_google_calendar_event)
    
    return booking


@router.patch(
    "/bookings/{booking_id}/status",
    status_code=status.HTTP_200_OK,
    response_model=BookingOut,
)
async def update_booking_status(
    user: CurrentUserDep,
    session: DbSessionDep,
    booking_id: int,
    payload: HostBookingStatusUpdateIn,
    now: UtcNow,
) -> BookingOut:
    if not user.is_host or user.calendar is None:
        raise HostNotFoundError()

    stmt = (
        select(Booking)
        .join(Booking.time_slot)
        .where(Booking.id == booking_id)
        .where(TimeSlot.calendar_id == user.calendar.id)
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="예약 내역이 없습니다.")
    
    if booking.when < now.date():
        raise PastBookingError()
    
    booking.attendance_status = payload.attendance_status
    await session.commit()
    await session.refresh(booking)
    return booking


@router.delete(
    "/guest-bookings/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_guest_booking(
    user: CurrentUserDep,
    session: DbSessionDep,
    booking_id: int,
    now: UtcNow,
    service: GoogleCalendarServiceDep,
    background_tasks: BackgroundTasks,
) -> None:
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .where(Booking.guest_id == user.id)
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="예약 내역이 없습니다.")

    if booking.when <= now.date():
        raise PastBookingError()

    if booking.attendance_status != AttendanceStatus.CANCELLED.value:
        booking.attendance_status = AttendanceStatus.CANCELLED.value
        await session.commit()
        await session.refresh(booking)

    if booking.google_event_id:
        async def _cancel_google_calendar_event():
            await service.delete_event(booking.google_event_id, booking.time_slot.calendar.google_calendar_id)
            
        background_tasks.add_task(_cancel_google_calendar_event)
 
    return None


@router.post(
    "/bookings/{booking_id}/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=BookingOut,
)
async def upload_booking_files(
    user: CurrentUserDep,
    booking_id: int,
    files: Annotated[list[UploadFile], File(min_length=1, max_length=3)],
    session: DbSessionDep,
    now: UtcNow,
) -> BookingOut:
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .where(Booking.guest_id == user.id)
    )
    result = await session.execute(stmt)
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="예약 내역이 없습니다.")
    
    if booking.when <= now.date():
        raise PastBookingError()

    for file in files:
        session.add(BookingFile(booking_id=booking.id, file=file))
    await session.commit()
    await session.refresh(booking, ["files"])
    return booking


@router.get(
    "/time-slots/{host_username}",
    status_code=status.HTTP_200_OK,
    response_model=list[TimeSlotOut],
)
async def get_host_timeslots(
    host_username: str,
    session: DbSessionDep,
) -> list[TimeSlotOut]:
    stmt = (
        select(User)
        .where(User.username == host_username)
        .where(User.is_active.is_(true()))
        .where(User.is_host.is_(true()))
    )
    result = await session.execute(stmt)
    host = result.scalar_one_or_none()
    if host is None or host.calendar is None:
        raise HostNotFoundError()
    
    stmt = select(TimeSlot).where(TimeSlot.calendar_id == host.calendar.id)
    result = await session.execute(stmt)
    return result.scalars().all()
