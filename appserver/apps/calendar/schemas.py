from typing import Annotated

from pydantic import AwareDatetime, EmailStr, AfterValidator
from sqlmodel import SQLModel, Field
from appserver.libs.collections.sort import deduplicate_and_sort


class CalendarOut(SQLModel):
    topics: list[str]
    description: str


class CalendarDetailOut(CalendarOut):
    host_id: int
    google_calendar_id: str
    created_at: AwareDatetime
    updated_at: AwareDatetime


Topics = Annotated[list[str], AfterValidator(deduplicate_and_sort)]


class CalendarCreateIn(SQLModel):
    topics: Topics = Field(min_length=1, description="게스트와 나눌 주제들")
    description: str = Field(min_length=1, description="게스트에게 보여줄 설명")
    google_calendar_id: EmailStr = Field(description="Google Calendar ID")

