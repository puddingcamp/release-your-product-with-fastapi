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

    def make_event_body(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
        summary: Optional[str] = None,
        conference: Optional[dict] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        reminder: Optional[Reminder] = None,
        timezone: Optional[str] = "Asia/Seoul",
        send_update: Literal["all", "externalOnly", "none"] = "all",
    ) -> dict:
        event = {}

        event["start"] = {
            "dateTime": start_datetime.isoformat(),
            "timeZone": timezone,
        }
        event["end"] = {
            "dateTime": end_datetime.isoformat(),
            "timeZone": timezone,
        }

        if summary:
            event["summary"] = summary
        if conference:
            event["conferenceData"] = conference
        if location:
            event["location"] = location
        if description:
            event["description"] = description
        if reminder:
            event["reminders"] = reminder
        if send_update:
            event["sendUpdate"] = send_update

        return event

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
        event = self.make_event_body(
            start_datetime,
            end_datetime,
            summary=summary,
            conference=conference,
            location=location,
            description=description,
            reminder=reminder,
            timezone=timezone,
            send_update=send_update,
        )

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

    async def event_list(
        self,
        time_min: datetime,
        time_max: datetime,
        google_calendar_id: Optional[str] = None,
    ) -> list[CalendarEvent]:
        google_calendar_id = google_calendar_id or self.default_google_calendar_id

        events_result = (
            self.service.events()
            .list(
                calendarId=google_calendar_id,
                timeMin=time_min.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])

    async def delete_event(
        self,
        event_id: str,
        google_calendar_id: Optional[str] = None,
    ) -> bool:
        google_calendar_id = google_calendar_id or self.default_google_calendar_id
        try:
            self.service.events().delete(
                calendarId=google_calendar_id, eventId=event_id
            ).execute()
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

    async def update_event(
        self,
        event_id: str,
        start_datetime: datetime,
        end_datetime: datetime,
        google_calendar_id: Optional[str] = None,
        *,
        summary: Optional[str] = None,
        conference: Optional[dict] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        reminder: Optional[Reminder] = None,
        timezone: Optional[str] = "Asia/Seoul",
        send_update: Literal["all", "externalOnly", "none"] = "all",
    ) -> bool:
        event = self.make_event_body(
            start_datetime,
            end_datetime,
            summary=summary,
            conference=conference,
            location=location,
            description=description,
            reminder=reminder,
            timezone=timezone,
            send_update=send_update,
        )
       
        google_calendar_id = google_calendar_id or self.default_google_calendar_id
        try:
            self.service.events().update(
                calendarId=google_calendar_id,
                eventId=event_id,
                body=event,
            ).execute()
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

    async def get_event(
        self,
        event_id: str,
        google_calendar_id: Optional[str] = None,
    ) -> CalendarEvent | None:
        google_calendar_id = google_calendar_id or self.default_google_calendar_id
        try:
            return self.service.events().get(
                calendarId=google_calendar_id, eventId=event_id
            ).execute()
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
