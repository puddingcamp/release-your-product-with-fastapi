from typing import TYPE_CHECKING
from datetime import date, time, timezone, datetime

from fastapi_storages import FileSystemStorage
from fastapi_storages import StorageFile
from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import AwareDatetime, computed_field
from sqlalchemy_utc import UtcDateTime
from sqlmodel import SQLModel, Field, Relationship, Text, JSON, func, String, Column
from sqlmodel.main import SQLModelConfig

from .enums import AttendanceStatus

if TYPE_CHECKING:
    from appserver.apps.account.models import User


class Calendar(SQLModel, table=True):
    __tablename__ = "calendars"

    id: int = Field(default=None, primary_key=True)
    topics: list[str] = Field(
        sa_type=JSON().with_variant(JSONB(astext_type=Text()), "postgresql"),
        description="게스트와 나눌 주제들"
    )
    description: str = Field(sa_type=Text, description="게스트에게 보여줄 설명")
    google_calendar_id: str = Field(max_length=1024, description="Google Calendar ID")

    host_id: int = Field(foreign_key="users.id", unique=True)
    host: "User" = Relationship(
        back_populates="calendar",
        sa_relationship_kwargs={"uselist": False, "single_parent": True, "lazy": "joined"},
    )

    time_slots: list["TimeSlot"] = Relationship(
        back_populates="calendar",
        sa_relationship_kwargs={"lazy": "noload"},
    )

    created_at: AwareDatetime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    updated_at: AwareDatetime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )

    def __str__(self):
        return f"{self.host} 캘린더"


class TimeSlot(SQLModel, table=True):
    __tablename__ = "time_slots"

    id: int = Field(default=None, primary_key=True)
    start_time: time
    end_time: time
    weekdays: list[int] = Field(
        sa_type=JSON().with_variant(JSONB(astext_type=Text()), "postgresql"),
        description="예약 가능한 요일들"
    )

    calendar_id: int = Field(foreign_key="calendars.id")
    calendar: Calendar = Relationship(
        back_populates="time_slots",
        sa_relationship_kwargs={"lazy": "joined"},
    )

    bookings: list["Booking"] = Relationship(
        back_populates="time_slot",
        sa_relationship_kwargs={"lazy": "noload"},
    )

    created_at: AwareDatetime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    updated_at: AwareDatetime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )

    def __str__(self):
        return f"{self.calendar}. {self.start_time} - {self.end_time} {self.weekdays}"



class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: int = Field(default=None, primary_key=True)
    when: date
    topic: str
    description: str = Field(sa_type=Text, description="예약 설명")
    # 참석 상태 종류
    attendance_status: AttendanceStatus = Field(
        default=AttendanceStatus.SCHEDULED,
        description="참석 상태",
        sa_type=String,
    )

    time_slot_id: int = Field(foreign_key="time_slots.id")
    time_slot: TimeSlot = Relationship(
        back_populates="bookings",
        sa_relationship_kwargs={"lazy": "joined"},
    )

    guest_id: int = Field(foreign_key="users.id")
    guest: "User" = Relationship(
        back_populates="bookings",
        sa_relationship_kwargs={"lazy": "joined"},
    )

    files: list["BookingFile"] = Relationship(
        back_populates="booking",
        sa_relationship_kwargs={"lazy": "noload"},
    )

    google_event_id: str | None = Field(
        max_length=64,
        default=None,
        nullable=True,
        description="Google Calendar Event ID",
        sa_type=String,
    )

    created_at: AwareDatetime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    updated_at: AwareDatetime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )

    def __str__(self):
        return f"{self.when} {self.time_slot.start_time} - {self.time_slot.end_time}"

    @computed_field
    @property
    def host(self) -> "User":
        return self.time_slot.calendar.host


class BookingFile(SQLModel, table=True):
    __tablename__ = "booking_files"

    id: int = Field(default=None, primary_key=True)
    booking_id: int = Field(foreign_key="bookings.id")
    booking: Booking = Relationship(
        back_populates="files",
        sa_relationship_kwargs={"lazy": "noload"},
    )
    file: StorageFile = Field(
        exclude=True,
        sa_column=Column(
            FileType(storage=FileSystemStorage(path="uploads/bookings")),
            nullable=False,
        ),
    )

    model_config = SQLModelConfig(
        arbitrary_types_allowed=True,
    )

    def __str__(self):
        return self.file.name
