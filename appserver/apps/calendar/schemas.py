from pydantic import AwareDatetime
from sqlmodel import SQLModel


class CalendarOut(SQLModel):
    topics: list[str]
    description: str


class CalendarDetailOut(CalendarOut):
    google_calendar_id: str
    created_at: AwareDatetime
    updated_at: AwareDatetime

