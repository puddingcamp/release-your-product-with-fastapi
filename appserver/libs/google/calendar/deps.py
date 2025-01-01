import os
from typing import Annotated
from fastapi import Depends

from .services import GoogleCalendarService


def get_google_calendar_service(google_calendar_id: str | None = None) -> GoogleCalendarService:
    google_calendar_id = google_calendar_id or os.getenv("GOOGLE_CALENDAR_ID")
    if google_calendar_id is None:
        raise ValueError("GOOGLE_CALENDAR_ID is not set")

    return GoogleCalendarService(google_calendar_id)


GoogleCalendarServiceDep = Annotated[GoogleCalendarService, Depends(get_google_calendar_service)]
