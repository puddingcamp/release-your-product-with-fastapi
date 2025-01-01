import calendar
from datetime import date, time
import os

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from appserver.db import create_engine, create_session, use_session
from appserver.app import include_routers
from appserver.apps.account import models as account_models
from appserver.apps.calendar import models as calendar_models
from appserver.apps.account.utils import hash_password
from appserver.apps.account.schemas import LoginPayload
from appserver.libs.datetime.datetime import utcnow


@pytest.fixture(autouse=True)
async def db_session():
    dsn = "sqlite+aiosqlite:///:memory:"
    engine = create_engine(dsn)
    async with engine.connect() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

        session_factory = create_session(conn)
        async with session_factory() as session:
            yield session

        await conn.run_sync(SQLModel.metadata.drop_all)

        await conn.rollback()

    await engine.dispose()


@pytest.fixture()
def fastapi_app(db_session: AsyncSession):
    app = FastAPI()
    include_routers(app)

    async def override_use_session():
        yield db_session

    def override_utcnow():
        return utcnow().replace(year=2024, month=12, day=5)

    app.dependency_overrides[use_session] = override_use_session
    app.dependency_overrides[utcnow] = override_utcnow
    return app


@pytest.fixture()
def client(fastapi_app: FastAPI):
    with TestClient(fastapi_app) as client:
        yield client


@pytest.fixture()
def client_with_auth(fastapi_app: FastAPI, host_user: account_models.User):
    payload = LoginPayload.model_validate({
        "username": host_user.username,
        "password": "testtest",
    })

    with TestClient(fastapi_app) as client:
        response = client.post("/account/login", json=payload.model_dump())
        assert response.status_code == status.HTTP_200_OK

        auth_token = response.cookies.get("auth_token")
        assert auth_token is not None

        client.cookies.set("auth_token", auth_token)
        yield client


@pytest.fixture()
def client_with_guest_auth(fastapi_app: FastAPI, guest_user: account_models.User):
    payload = LoginPayload.model_validate({
        "username": guest_user.username,
        "password": "testtest",
    })

    with TestClient(fastapi_app) as client:
        response = client.post("/account/login", json=payload.model_dump())
        assert response.status_code == status.HTTP_200_OK

        auth_token = response.cookies.get("auth_token")
        assert auth_token is not None

        client.cookies.set("auth_token", auth_token)
        yield client


@pytest.fixture()
def client_with_smart_guest_auth(fastapi_app: FastAPI, smart_guest_user: account_models.User):
    payload = LoginPayload.model_validate({
        "username": smart_guest_user.username,
        "password": "testtest",
    })

    with TestClient(fastapi_app) as client:
        response = client.post("/account/login", json=payload.model_dump())
        assert response.status_code == status.HTTP_200_OK

        auth_token = response.cookies.get("auth_token")
        assert auth_token is not None

        client.cookies.set("auth_token", auth_token)
        yield client


@pytest.fixture()
async def host_user(db_session: AsyncSession):
    user = account_models.User(
        username="puddingcamp",
        hashed_password=hash_password("testtest"),
        email="puddingcamp@example.com",
        display_name="푸딩캠프",
        is_host=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.flush()
    return user


@pytest.fixture()
async def charming_host_user(db_session: AsyncSession):
    user = account_models.User(
        username="charming_host",
        hashed_password=hash_password("testtest"),
        email="charming_host@example.com",
        display_name="매력있는 캠프",
        is_host=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.flush()
    return user


@pytest.fixture()
async def guest_user(db_session: AsyncSession):
    user = account_models.User(
        username="puddingcafe",
        hashed_password=hash_password("testtest"),
        email="puddingcafe@example.com",
        display_name="푸딩까페",
        is_host=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.flush()
    return user


@pytest.fixture()
async def smart_guest_user(db_session: AsyncSession):
    user = account_models.User(
        username="smart_guest",
        hashed_password=hash_password("testtest"),
        email="smart_guest@example.com",
        display_name="스마트 게스트",
        is_host=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.flush()
    return user


@pytest.fixture()
async def cute_guest_user(db_session: AsyncSession):
    user = account_models.User(
        username="cute_guest",
        hashed_password=hash_password("testtest"),
        email="cute_guest@example.com",
        display_name="귀여운 게스트",
        is_host=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.flush()
    return user


@pytest.fixture()
async def host_user_calendar(db_session: AsyncSession, host_user: account_models.User):
    calendar = calendar_models.Calendar(
        host_id=host_user.id,
        description="푸딩캠프 캘린더 입니다.",
        topics=["푸딩캠프", "푸딩캠프2"],
        google_calendar_id=os.getenv("GOOGLE_CALENDAR_ID"),
    )
    db_session.add(calendar)
    await db_session.commit()
    await db_session.refresh(host_user)
    return calendar


@pytest.fixture()
async def charming_host_user_calendar(db_session: AsyncSession, charming_host_user: account_models.User):
    calendar = calendar_models.Calendar(
        host_id=charming_host_user.id,
        description="매력있는 캠프 캘린더 입니다.",
        topics=["매력있는 캠프", "매력있는 캠프2"],
        google_calendar_id="0987654321",
    )
    db_session.add(calendar)
    await db_session.commit()
    await db_session.refresh(charming_host_user)
    return calendar


@pytest.fixture()
async def time_slot_tuesday(
    db_session: AsyncSession,
    host_user_calendar: calendar_models.Calendar,
):
    time_slot = calendar_models.TimeSlot(
        start_time=time(9, 0),
        end_time=time(10, 0),
        weekdays=[calendar.TUESDAY],
        calendar_id=host_user_calendar.id,
    )
    db_session.add(time_slot)
    await db_session.commit()
    return time_slot


@pytest.fixture()
async def time_slot_monday(
    db_session: AsyncSession,
    host_user_calendar: calendar_models.Calendar,
):
    time_slot = calendar_models.TimeSlot(
        start_time=time(9, 0),
        end_time=time(10, 0),
        weekdays=[calendar.MONDAY],
        calendar_id=host_user_calendar.id,
    )
    db_session.add(time_slot)
    await db_session.commit()
    return time_slot


@pytest.fixture()
async def time_slot_wednesday_thursday(
    db_session: AsyncSession,
    charming_host_user_calendar: calendar_models.Calendar,
):
    time_slot = calendar_models.TimeSlot(
        start_time=time(10, 0),
        end_time=time(11, 0),
        weekdays=[calendar.WEDNESDAY, calendar.THURSDAY],
        calendar_id=charming_host_user_calendar.id,
    )
    db_session.add(time_slot)
    await db_session.commit()
    return time_slot


@pytest.fixture()
async def time_slot_friday(
    db_session: AsyncSession,
    charming_host_user_calendar: calendar_models.Calendar,
):
    time_slot = calendar_models.TimeSlot(
        start_time=time(10, 0),
        end_time=time(11, 0),
        weekdays=[calendar.FRIDAY],
        calendar_id=charming_host_user_calendar.id,
    )
    db_session.add(time_slot)
    await db_session.commit()
    return time_slot



@pytest.fixture()
async def host_bookings(
    db_session: AsyncSession,
    guest_user: account_models.User,
    time_slot_tuesday: calendar_models.TimeSlot,
):
    bookings = []
    for when in [date(2024, 12, 3), date(2024, 12, 10), date(2024, 12, 17), date(2025, 1, 7)]:
        booking = calendar_models.Booking(
            when=when,
            topic="test",
            description="test",
            time_slot_id=time_slot_tuesday.id,
            guest_id=guest_user.id,
        )
        db_session.add(booking)
        bookings.append(booking)
    await db_session.commit()
    return bookings


@pytest.fixture()
async def charming_host_bookings(
    db_session: AsyncSession,
    guest_user: account_models.User,
    time_slot_wednesday_thursday: calendar_models.TimeSlot,
):
    bookings = []
    for when in [date(2024, 12, 4), date(2024, 12, 5), date(2024, 12, 11)]:
        booking = calendar_models.Booking(
            when=when,
            topic="test",
            description="test",
            time_slot_id=time_slot_wednesday_thursday.id,
            guest_id=guest_user.id,
        )
        db_session.add(booking)
        bookings.append(booking)

    await db_session.commit()
    return bookings
