from pathlib import Path
from datetime import datetime
from typing import Any, Literal, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .schemas import CalendarEvent, Reminder


BASE_DIR = Path(__file__).parent.parent.parent.parent.parent

GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_PATH = BASE_DIR / "calendar-booking-service-account-credentials.json"


class GoogleCalendarService:
    def __init__(
        self,
        default_google_calendar_id: str,
        credentials_path: Optional[Path] = GOOGLE_SERVICE_ACCOUNT_CREDENTIAL_PATH,
    ):
        self.credentials_path = credentials_path
        self.default_google_calendar_id = default_google_calendar_id
        self.service = self._get_authenticated_service(credentials_path)

    def _get_authenticated_service(self, credentials_path: Path) -> Any:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path.as_posix(),
            scopes=[
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/calendar.events",
            ],
        )
        return build("calendar", "v3", credentials=credentials)

    async def create_event(
        self,
        summary: str,
        start_datetime: datetime,
        end_datetime: datetime,
        *,
        google_calendar_id: Optional[str] = None,
        conference: Optional[dict] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        reminder: Optional[Reminder] = None,
        timezone: Optional[str] = "Asia/Seoul",
        send_update: Literal["all", "externalOnly", "none"] = "all",
    ) -> CalendarEvent | None:
        event = {
            "summary": summary,
            "start": {
                "dateTime": start_datetime.isoformat(),
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_datetime.isoformat(),
                "timeZone": timezone,
            },
            "attendees": [],
            "sendUpdate": send_update,
        }

        if conference:
            event["conferenceData"] = conference
        if location:
            event["location"] = location
        if description:
            event["description"] = description
        if reminder:
            event["reminders"] = reminder

        calendar_id = google_calendar_id or self.default_google_calendar_id
        try:
            event = (
                self.service.events()
                .insert(
                    calendarId=calendar_id,
                    body=event,
                    conferenceDataVersion=1,
                )
                .execute()
            )
        except HttpError as e:
            print("create_calendar_event error", e)
            return None

        if event.get("htmlLink"):
            return event
        return None
