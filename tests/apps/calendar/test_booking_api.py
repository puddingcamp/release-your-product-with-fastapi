import calendar
from datetime import date
import os

import pytest
from pytest_lazy_fixtures import lf
from fastapi import status
from fastapi.testclient import TestClient

from appserver.apps.calendar.enums import AttendanceStatus
from appserver.apps.calendar.schemas import BookingOut
from appserver.apps.account.models import User
from appserver.apps.calendar.models import Booking, TimeSlot
from appserver.libs.datetime.calendar import get_next_weekday
from appserver.libs.google.calendar.services import GoogleCalendarService


@pytest.fixture()
def calendar_id() -> str:
    return os.getenv("GOOGLE_CALENDAR_ID")


@pytest.fixture()
def google_calendar_service(calendar_id: str) -> GoogleCalendarService:
    return GoogleCalendarService(default_google_calendar_id=calendar_id)


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


async def test_중복_신청을_하면_HTTP_422_응답을_한다(
    host_user: User,
    client_with_guest_auth: TestClient,
    valid_booking_payload: dict,
):
    response = client_with_guest_auth.post(
        f"/bookings/{host_user.username}",
        json=valid_booking_payload,
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = client_with_guest_auth.post(
        f"/bookings/{host_user.username}",
        json=valid_booking_payload,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("charming_host_bookings")
async def test_호스트는_페이지_단위로_자신에게_예약된_부킹_목록을_받는다(
    client_with_auth: TestClient,
    host_bookings: list[Booking],
):
    response = client_with_auth.get("/bookings", params={"page": 1, "page_size": 10})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == len(host_bookings)


@pytest.mark.parametrize(
    "year, month",
    [(2024, 12), (2025, 1)],
)
@pytest.mark.usefixtures("charming_host_bookings")
async def test_게스트는_호스트의_캘린더의_예약_내역을_월_단위로_받는다(
    client_with_guest_auth: TestClient,
    host_bookings: list[Booking],
    host_user: User,
    year: int,
    month: int,
):
    params = {
        "year": year,
        "month": month,
    }
    response = client_with_guest_auth.get(
        f"/calendar/{host_user.username}/bookings",
        params=params,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    booking_dates = frozenset([
        booking.when.isoformat()
        for booking in host_bookings
        if booking.when.year == params["year"] and booking.when.month == params["month"]
    ])
    assert not not data
    assert len(data) == len(booking_dates)
    assert all([item["when"] in booking_dates for item in data])
 

async def test_게스트는_자신의_캘린더의_예약_내역을_페이지_단위로_받는다(
    client_with_guest_auth: TestClient,
    host_bookings: list[Booking],
    charming_host_bookings: list[Booking],
):
    response = client_with_guest_auth.get("/guest-calendar/bookings", params={"page": 1, "page_size": 50})

    assert response.status_code == status.HTTP_200_OK

    id_set = frozenset([booking.id for booking in host_bookings] + [booking.id for booking in charming_host_bookings])
    data = response.json()
    assert len(data) == len(id_set)
    assert all([item["id"] in id_set for item in data])


@pytest.mark.parametrize(
    "client, expected_status_code",
    [
        (lf("client_with_guest_auth"), status.HTTP_200_OK),
        (lf("client_with_smart_guest_auth"), status.HTTP_404_NOT_FOUND),
    ],
)
async def test_사용자는_특정_예약_내역_데이터를_받는다(
    host_bookings: list[Booking],
    client: TestClient,
    expected_status_code: int,
):
    response = client.get(f"/bookings/{host_bookings[0].id}")

    assert response.status_code == expected_status_code

    data = response.json()
    if expected_status_code == status.HTTP_200_OK:
        assert data["id"] == host_bookings[0].id


@pytest.mark.parametrize(
    "payload",
    [
        {"when": "2025-01-01", "time_slot": lf("time_slot_tuesday")},
        {"when": "2025-01-02", "time_slot": lf("time_slot_monday")},
    ],
)
@pytest.mark.usefixtures("host_user_calendar")
async def test_호스트는_자신에게_신청한_부킹에_대해_일자_타임슬롯을_변경할_수_있다(
    payload: dict,
    client_with_auth: TestClient,
    host_bookings: list[Booking],
):
    hooking = host_bookings[0]
    time_slot: TimeSlot = payload["time_slot"]
    payload["time_slot_id"] = time_slot.id
    del payload["time_slot"]

    response = client_with_auth.patch(f"/bookings/{hooking.id}", json=payload)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["when"] == payload["when"]
    assert data["time_slot"]["start_time"] == time_slot.start_time.isoformat()
    assert data["time_slot"]["end_time"] == time_slot.end_time.isoformat()
    assert data["time_slot"]["weekdays"] == time_slot.weekdays


@pytest.mark.parametrize(
    "time_slot, expected_status_code",
    [
        (lf("time_slot_friday"), status.HTTP_404_NOT_FOUND),
        (lf("time_slot_tuesday"), status.HTTP_200_OK),
    ],
)
async def test_호스트는_다른_호스트의_타임슬롯으로_변경할_수_없다(
    client_with_auth: TestClient,
    host_bookings: list[Booking],
    time_slot: TimeSlot,
    expected_status_code: int,
):
    response = client_with_auth.patch(
        f"/bookings/{host_bookings[0].id}",
        json={"time_slot_id": time_slot.id},
    )
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "time_slot, expected_status_code",
    [
        (lf("time_slot_friday"), status.HTTP_404_NOT_FOUND),
        (lf("time_slot_tuesday"), status.HTTP_200_OK),
    ],
)
async def test_게스트는_다른_호스트의_타임슬롯으로_변경할_수_없다(
    client_with_guest_auth: TestClient,
    host_bookings: list[Booking],
    time_slot: TimeSlot,
    expected_status_code: int,
):
    response = client_with_guest_auth.patch(
        f"/guest-bookings/{host_bookings[0].id}",
        json={"time_slot_id": time_slot.id},
    )
    assert response.status_code == expected_status_code



@pytest.mark.parametrize(
    "payload",
    [
        {"topic": "test", "description": "test", "when": "2025-01-01", "time_slot": lf("time_slot_tuesday")},
        {"topic": "test", "description": "test", "when": "2025-01-02", "time_slot": lf("time_slot_monday")},
        {"description": "test", "when": "2025-01-12"},
    ],
)
async def test_게스트는_자신의_부킹에_대해_주제_설명_일자_타임슬롯을_변경할_수_있다(
    client_with_guest_auth: TestClient,
    host_bookings: list[Booking],
    payload: dict,
):
    booking = host_bookings[0]

    # 변경 전 데이터 추출
    before_booking = BookingOut.model_validate(booking, from_attributes=True).model_dump(mode="json")

    # 변경 가능한 필드 설정
    updatable_fields = set(["topic", "description", "when", "time_slot"])
    exceptable_fields = updatable_fields - set(payload.keys())

    # 타임슬롯 처리
    if time_slot := payload.pop("time_slot", None):
        time_slot: TimeSlot
        payload["time_slot_id"] = time_slot.id
    else:
        time_slot = None
        payload["time_slot_id"] = None

    # 요청 보내기
    response = client_with_guest_auth.patch(
        f"/guest-bookings/{booking.id}",
        json=payload,
    )

    # 응답 검증
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # 변경된 필드 검증
    for field, value in payload.items():
        if field == "time_slot_id" and time_slot:
            assert data["time_slot"]["start_time"] == time_slot.start_time.isoformat()
            assert data["time_slot"]["end_time"] == time_slot.end_time.isoformat()
            assert data["time_slot"]["weekdays"] == time_slot.weekdays
        else:
            assert payload[field] == value

    # 변경되지 않은 필드 검증
    for field_name in exceptable_fields:
        if field_name == "time_slot":
            assert before_booking["time_slot"]["start_time"] == data["time_slot"]["start_time"]
            assert before_booking["time_slot"]["end_time"] == data["time_slot"]["end_time"]
            assert before_booking["time_slot"]["weekdays"] == data["time_slot"]["weekdays"]
        else:
            assert before_booking[field_name] == data[field_name]


@pytest.mark.parametrize(
    "attendance_status",
    [
        (AttendanceStatus.SCHEDULED),
        (AttendanceStatus.ATTENDED),
        (AttendanceStatus.NO_SHOW),
        (AttendanceStatus.CANCELLED),
        (AttendanceStatus.SAME_DAY_CANCEL),
        (AttendanceStatus.LATE),
    ],
)
async def test_호스트는_자신에게_신청한_부킹의_참석_상태를_변경할_수_있다(
    client_with_auth: TestClient,
    host_bookings: list[Booking],
    attendance_status: AttendanceStatus,
):
    payload = {
        "attendance_status": attendance_status,
    }
    booking = host_bookings[-1]
    response = client_with_auth.patch(f"/bookings/{booking.id}/status", json=payload)

    assert response.status_code == status.HTTP_200_OK

    response = client_with_auth.get(f"/bookings/{booking.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["attendance_status"] == attendance_status.value


@pytest.mark.parametrize(
    "booking_index, expected_status_code",
    [
        (0, status.HTTP_422_UNPROCESSABLE_ENTITY),
        (-1, status.HTTP_204_NO_CONTENT),
    ],
)
async def test_게스트는_자신의_부킹을_취소만_할_수_있다(
    client_with_guest_auth: TestClient,
    host_bookings: list[Booking],
    booking_index: int,
    expected_status_code: int,
):
    booking = host_bookings[booking_index]
    response = client_with_guest_auth.delete(f"/guest-bookings/{booking.id}")
    assert response.status_code == expected_status_code


async def test_게스트는_자신이_신청한_부킹에_파일을_업로드할_수_있다(
    client_with_guest_auth: TestClient,
    host_bookings: list[Booking],
):
    booking = host_bookings[-1]

    file_content_1 = b"File content 1"
    file_content_2 = b"File content 2"
    file_content_3 = b"File content 3"

    files = [
        ("files", ("file1.txt", file_content_1, "text/plain")),
        ("files", ("file2.txt", file_content_2, "text/plain")),
        ("files", ("file3.txt", file_content_3, "text/plain")),
    ]

    response = client_with_guest_auth.post(f"/bookings/{booking.id}/upload", files=files)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert len(data["files"]) == 3

    file_names = [file_name["file"].split("/")[-1] for file_name in data["files"]]
    assert file_names == ["file1.txt", "file2.txt", "file3.txt"]


@pytest.mark.skipif(
    os.getenv("GOOGLE_CALENDAR_ID") is None,
    reason="GOOGLE_CALENDAR_ID is not set",
)
@pytest.mark.usefixtures("host_user_calendar")
async def test_부킹을_생성하면_호스트의_구글_캘린더에_일정을_생성한다(
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
    assert data["google_event_id"] is not None


@pytest.mark.skipif(
    os.getenv("GOOGLE_CALENDAR_ID") is None,
    reason="GOOGLE_CALENDAR_ID is not set",
)
@pytest.mark.usefixtures("host_user_calendar")
async def test_부킹을_변경하면_호스트의_구글_캘린더에_일정을_반영한다(
    host_user: User,
    client_with_guest_auth: TestClient,
    valid_booking_payload: dict,
    google_calendar_service: GoogleCalendarService,
):
    response = client_with_guest_auth.post(
        f"/bookings/{host_user.username}",
        json=valid_booking_payload,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["google_event_id"] is not None

    response = client_with_guest_auth.patch(
        f"/guest-bookings/{data['id']}",
        json={
            "description": "변경한 설명",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["google_event_id"] is not None

    event = await google_calendar_service.get_event(data["google_event_id"])
    assert event["description"] == "변경한 설명"


@pytest.mark.skipif(
    os.getenv("GOOGLE_CALENDAR_ID") is None,
    reason="GOOGLE_CALENDAR_ID is not set",
)
async def test_부킹을_삭제하면_호스트의_구글_캘린더에_일정을_삭제한다(
    host_user: User,
    client_with_guest_auth: TestClient,
    google_calendar_service: GoogleCalendarService,
    valid_booking_payload: dict,
):
    response = client_with_guest_auth.post(
        f"/bookings/{host_user.username}",
        json=valid_booking_payload,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["google_event_id"] is not None

    response = client_with_guest_auth.delete(f"/guest-bookings/{data['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    event = await google_calendar_service.get_event(data["google_event_id"])
    assert event["status"] == "cancelled"


