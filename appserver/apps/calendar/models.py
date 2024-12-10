from datetime import date, time, timezone, datetime
from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import JSONB
from pydantic import AwareDatetime
from sqlalchemy_utc import UtcDateTime
from sqlmodel import SQLModel, Field, Relationship, Text, JSON, func

if TYPE_CHECKING:
    from apps.account.models import User


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
        sa_relationship_kwargs={"single_parent": True},
    )

    time_slots: list["TimeSlot"] = Relationship(back_populates="calendar")

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
    calendar: Calendar = Relationship(back_populates="time_slots")

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
