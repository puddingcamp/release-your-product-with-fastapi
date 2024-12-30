import os
from datetime import datetime

import pytest

from appserver.libs.google.calendar.services import GoogleCalendarService


@pytest.fixture()
def calendar_id() -> str:
    return os.getenv("GOOGLE_CALENDAR_ID")


@pytest.fixture()
def service(calendar_id: str) -> GoogleCalendarService:
    return GoogleCalendarService(default_google_calendar_id=calendar_id)


@pytest.mark.skipif(
    os.getenv("GOOGLE_CALENDAR_ID") is None,
    reason="GOOGLE_CALENDAR_ID is not set",
)
async def test_create_event(service: GoogleCalendarService):
    result = await service.create_event(
        summary="푸딩캠프와 관련된 테스트 일정",
        start_datetime=datetime.now(),
        end_datetime=datetime.now(),
    )

    assert result is not None
    assert result["kind"] == "calendar#event"
    assert not not result["id"]
    assert "https://www.google.com/calendar/event" in result["htmlLink"]
