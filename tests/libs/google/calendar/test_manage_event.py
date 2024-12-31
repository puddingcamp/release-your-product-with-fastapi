import os
from datetime import datetime, timedelta, timezone

import pytest

from appserver.libs.google.calendar.services import GoogleCalendarService


@pytest.fixture()
def calendar_id() -> str:
    return os.getenv("GOOGLE_CALENDAR_ID")


@pytest.fixture()
def service(calendar_id: str) -> GoogleCalendarService:
    return GoogleCalendarService(default_google_calendar_id=calendar_id)


@pytest.fixture()
async def event(service: GoogleCalendarService):
    event = await service.create_event(
        summary="푸딩캠프와 관련된 테스트 일정",
        start_datetime=datetime.now(),
        end_datetime=datetime.now(),
    )

    yield event
    
    await service.delete_event(event_id=event["id"])


@pytest.mark.skipif(
    os.getenv("GOOGLE_CALENDAR_ID") is None,
    reason="GOOGLE_CALENDAR_ID is not set",
)
async def test_delete_event(service: GoogleCalendarService, event: dict):
    result = await service.delete_event(
        event_id=event["id"],
    )

    assert result is True

    deleted_event = await service.get_event(event_id=event["id"])
    assert deleted_event is not None
    assert deleted_event["status"] == "cancelled"


@pytest.mark.skipif(
    os.getenv("GOOGLE_CALENDAR_ID") is None,
    reason="GOOGLE_CALENDAR_ID is not set",
)
async def test_event_list(service: GoogleCalendarService, event: dict):
    time_max = datetime.now(tz=timezone.utc)
    time_min = time_max - timedelta(days=30)
    result = await service.event_list(
        time_min=time_min,
        time_max=time_max,
    )

    assert result is not None
    assert len(result) > 0

    ids = [event["id"] for event in result]
    assert event["id"] in ids


@pytest.mark.skipif(
    os.getenv("GOOGLE_CALENDAR_ID") is None,
    reason="GOOGLE_CALENDAR_ID is not set",
)
async def test_update_event(service: GoogleCalendarService, event: dict):
    result = await service.update_event(
        event_id=event["id"],
        summary="푸딩캠프와 관련된 테스트 일정 업데이트",
        start_datetime=datetime.now(),
        end_datetime=datetime.now(),
    )
    assert result is True

    updated_event = await service.get_event(event_id=event["id"])

    assert updated_event is not None
    assert updated_event["summary"] == "푸딩캠프와 관련된 테스트 일정 업데이트"
