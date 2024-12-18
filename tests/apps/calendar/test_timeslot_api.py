from datetime import time

import pytest
from fastapi import status
from fastapi.testclient import TestClient
import calendar


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
