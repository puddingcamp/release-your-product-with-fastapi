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
