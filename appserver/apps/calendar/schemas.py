from datetime import date, datetime, time
from typing import Annotated

from fastapi_storages import StorageFile
from pydantic import AwareDatetime, EmailStr, AfterValidator, computed_field, model_validator
from sqlmodel import SQLModel, Field
from sqlmodel.main import SQLModelConfig
from appserver.apps.account.schemas import UserOut
from appserver.libs.collections.sort import deduplicate_and_sort

from .enums import AttendanceStatus


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
    description: str = Field(min_length=10, description="게스트에게 보여줄 설명")
    google_calendar_id: EmailStr = Field(min_length=90, description="Google Calendar ID")


class CalendarUpdateIn(SQLModel):
    topics: Topics | None = Field(
        default=None,
        min_length=1,
        description="게스트와 나눌 주제들",
    )
    description: str | None = Field(
        default=None,
        min_length=10,
        description="게스트에게 보여줄 설명",
    )
    google_calendar_id: EmailStr | None = Field(
        default=None,
        min_length=20,
        description="Google Calendar ID",
    )


def validate_weekdays(weekdays: list[int]) -> list[int]:
    weekday_range = range(7)
    for weekday in weekdays:
        if weekday not in weekday_range:
            raise ValueError(f"요일 값은 0부터 6까지의 값이어야 합니다. 현재 값: {weekday}")
    return weekdays


Weekdays = Annotated[list[int], AfterValidator(validate_weekdays)]


class TimeSlotCreateIn(SQLModel):
    start_time: time
    end_time: time
    weekdays: Weekdays

    @model_validator(mode="after")
    def validate_time_slot(self):
        if self.start_time >= self.end_time:
            raise ValueError("시작 시간은 종료 시간보다 빨라야 합니다.")
        return self


class TimeSlotOut(SQLModel):
    id: int
    start_time: time
    end_time: time
    weekdays: list[int]
    created_at: AwareDatetime
    updated_at: AwareDatetime


class BookingCreateIn(SQLModel):
    when: date
    topic: str
    description: str
    time_slot_id: int


class BookingFileOut(SQLModel):
    id: int
    file: StorageFile

    model_config = SQLModelConfig(
        arbitrary_types_allowed=True,
    )


class BookingOut(SQLModel):
    id: int
    when: date
    topic: str
    description: str
    time_slot: TimeSlotOut
    host: UserOut
    attendance_status: AttendanceStatus
    google_event_id: str | None
    files: list[BookingFileOut]
    created_at: AwareDatetime
    updated_at: AwareDatetime


class PaginatedBookingOut(SQLModel):
    bookings: list[BookingOut]
    total_count: int


class SimpleBookingOut(SQLModel):
    id: int
    when: date
    time_slot: TimeSlotOut


class HostBookingUpdateIn(SQLModel):
    when: date | None = Field(default=None, description="예약 일자")
    time_slot_id: int | None = Field(default=None, description="타임슬롯 ID")


class GuestBookingUpdateIn(SQLModel):
    topic: str | None = Field(default=None, description="예약 주제")
    description: str | None = Field(default=None, description="예약 설명")
    when: date | None = Field(default=None, description="예약 일자")
    time_slot_id: int | None = Field(default=None, description="타임슬롯 ID")


class HostBookingStatusUpdateIn(SQLModel):
    attendance_status: AttendanceStatus



class GoogleCalendarTimeSlot(SQLModel):
    start_time: time
    end_time: time
    weekdays: list[int]


class GoogleCalendarEventOut(SQLModel):
    id: str
    start: dict = Field(exclude=True)
    end: dict = Field(exclude=True)

    @computed_field
    @property
    def time_slot(self) -> GoogleCalendarTimeSlot:
        if start_date := self.start.get("date"):
            start_time = time(0, 0)
            end_time = time(23, 59)
            start_date = date.fromisoformat(start_date)
        else:
            start = datetime.fromisoformat(self.start["dateTime"])
            start_time = start.time()
            start_date = start.date()
            end_time = datetime.fromisoformat(self.end["dateTime"]).time()

        weekdays = [start_date.weekday()]

        return GoogleCalendarTimeSlot(
            start_time=start_time,
            end_time=end_time,
            weekdays=weekdays,
        )

    @computed_field
    @property
    def when(self) -> date:
        if start_date := self.start.get("date"):
            return date.fromisoformat(start_date)
        return datetime.fromisoformat(self.start.get("dateTime")).date()
    