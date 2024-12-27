from datetime import time

import pytest
from fastapi import status
from fastapi.testclient import TestClient
import calendar

from appserver.apps.calendar.models import TimeSlot
from appserver.apps.account.models import User


@pytest.mark.usefixtures("host_user_calendar")
async def test_호스트_사용자는_유효한_타임슬롯_정보를_제출하여_타임슬롯을_생성할_수_있다(
    client_with_auth: TestClient,
):
    payload = {
        "start_time": time(10, 0).isoformat(),
        "end_time": time(11, 0).isoformat(),
        "weekdays": [calendar.MONDAY, calendar.TUESDAY, calendar.WEDNESDAY],
    }

    response = client_with_auth.post(
        "/time-slots",
        json=payload,
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.usefixtures("host_user_calendar")
async def test_유효하지_않은_타임슬롯_정보로_생성하려_하면_HTTP_422_응답을_한다(
    client_with_auth: TestClient,
):
    payload = {
        "start_time": time(11, 0).isoformat(),
        "end_time": time(10, 0).isoformat(),
        "weekdays": [calendar.MONDAY, calendar.TUESDAY, calendar.WEDNESDAY],
    }

    response = client_with_auth.post("/time-slots", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("weekdays", [
    [-1, 0, 1, 2, 3, 4, 5, 6],
    [1, 2, 3, 4, 5, 6, 7],
])
@pytest.mark.usefixtures("host_user_calendar")
async def test_요일_값은_월_화_수_목_금_토_일_순이며_각_요일_값은_0부터_시작한다(
    client_with_auth: TestClient,
    weekdays: list[int],
):
    payload = {
        "start_time": time(10, 0).isoformat(),
        "end_time": time(11, 0).isoformat(),
        "weekdays": weekdays,
    }

    response = client_with_auth.post("/time-slots", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("start_time, end_time, weekdays, expected_status_code", [
    # 겹치지 않는 경우
    (time(9, 0), time(10, 0), [calendar.MONDAY], status.HTTP_201_CREATED),
    (time(11, 0), time(12, 0), [calendar.MONDAY], status.HTTP_201_CREATED),
    (time(10, 0), time(11, 0), [calendar.THURSDAY], status.HTTP_201_CREATED),
    
    # 겹치는 경우 (같은 요일)
    (time(10, 30), time(11, 30), [calendar.MONDAY], status.HTTP_422_UNPROCESSABLE_ENTITY),
    (time(9, 30), time(10, 30), [calendar.MONDAY], status.HTTP_422_UNPROCESSABLE_ENTITY),
    (time(10, 0), time(11, 0), [calendar.MONDAY], status.HTTP_422_UNPROCESSABLE_ENTITY),
    
    # 겹치지 않는 경우 (다른 요일)
    (time(10, 0), time(11, 0), [calendar.THURSDAY], status.HTTP_201_CREATED),
    (time(10, 0), time(11, 0), [calendar.FRIDAY], status.HTTP_201_CREATED),
])
@pytest.mark.usefixtures("host_user_calendar")
async def test_겹치는_시간대가_있는_경우_HTTP_422_응답을_한다(
    client_with_auth: TestClient,
    start_time: time,
    end_time: time,
    weekdays: list[int],
    expected_status_code: int,
):
    # 첫 번째 타임슬롯 생성
    payload = {
        "start_time": time(10, 0).isoformat(),
        "end_time": time(11, 0).isoformat(),
        "weekdays": [calendar.MONDAY, calendar.TUESDAY, calendar.WEDNESDAY],
    }
    response = client_with_auth.post("/time-slots", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    # 두 번째 타임슬롯 생성 시도
    payload = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "weekdays": weekdays,
    }
    response = client_with_auth.post("/time-slots", json=payload)
    assert response.status_code == expected_status_code


async def test_호스트_사용자의_타임슬롯_목록을_조회할_수_있다(
    client_with_auth: TestClient,
    host_user: User,
    time_slot_tuesday: TimeSlot,
    time_slot_monday: TimeSlot,
    time_slot_wednesday_thursday: TimeSlot,
    time_slot_friday: TimeSlot,
):
    time_slots = [
        time_slot_tuesday,
        time_slot_monday,
        time_slot_wednesday_thursday,
        time_slot_friday,
    ]
    response = client_with_auth.get(f"/time-slots/{host_user.username}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    host_timeslot_ids = [timeslot.id for timeslot in time_slots if timeslot.calendar_id == host_user.calendar.id]
    assert len(data) == len(host_timeslot_ids)
