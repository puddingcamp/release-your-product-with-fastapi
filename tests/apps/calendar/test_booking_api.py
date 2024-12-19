import calendar
from datetime import date
import pytest

from fastapi import status
from fastapi.testclient import TestClient

from appserver.apps.account.models import User
from appserver.apps.calendar.models import TimeSlot
from appserver.libs.datetime.calendar import get_next_weekday


@pytest.fixture()
def valid_booking_payload(time_slot_tuesday: TimeSlot):
    return {
        "when": get_next_weekday(calendar.TUESDAY).isoformat(),
        "topic": "test",
        "description": "test",
        "time_slot_id": time_slot_tuesday.id,
    }


@pytest.mark.usefixtures("host_user_calendar")
async def test_유효한_예약_신청_내용으로_예약_생성을_요청하면_예약_내용을_담아_HTTP_201_응답한다(
    time_slot_tuesday: TimeSlot,
    host_user: User,
    client_with_guest_auth: TestClient,
    valid_booking_payload: dict,
):
    response = client_with_guest_auth.post(
        f"/bookings/{host_user.username}",
        json=valid_booking_payload,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["when"] == valid_booking_payload["when"]
    assert data["topic"] == valid_booking_payload["topic"]
    assert data["description"] == valid_booking_payload["description"]
    assert data["time_slot"]["start_time"] == time_slot_tuesday.start_time.isoformat()
    assert data["time_slot"]["end_time"] == time_slot_tuesday.end_time.isoformat()
    assert data["time_slot"]["weekdays"] == time_slot_tuesday.weekdays


async def test_호스트가_아닌_사용자에게_예약을_생성하면_HTTP_404_응답을_한다(
    cute_guest_user: User,
    client_with_guest_auth: TestClient,
    valid_booking_payload: dict,
):
    response = client_with_guest_auth.post(
        f"/bookings/{cute_guest_user.username}",
        json=valid_booking_payload,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "time_slot_id_add, target_date",
    [
        (100, date(2024, 12, 3)),
        (0, date(2024, 12, 4)),
        (0, date(2024, 12, 5)),
    ],
)
@pytest.mark.usefixtures("host_user_calendar")
async def test_존재하지_않는_시간대에_예약을_생성하면_HTTP_404_응답을_한다(
    host_user: User,
    client_with_guest_auth: TestClient,
    time_slot_tuesday: TimeSlot,
    time_slot_id_add: int,
    target_date: date,
):
    payload = {
        "when": target_date.isoformat(),
        "topic": "test",
        "description": "test",
        "time_slot_id": time_slot_tuesday.id + time_slot_id_add,
    }

    response = client_with_guest_auth.post(f"/bookings/{host_user.username}", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_자기_자신에겐_예약_못하게_하기(
    host_user: User,
    client_with_auth: TestClient,
    valid_booking_payload: dict,
):
    response = client_with_auth.post(
        f"/bookings/{host_user.username}",
        json=valid_booking_payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_과거_일자에_예약을_생성하면_HTTP_422_응답을_한다(
    host_user: User,
    client_with_auth: TestClient,
    valid_booking_payload: dict,
):
    response = client_with_auth.post(
        f"/bookings/{host_user.username}",
        json=valid_booking_payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
