from datetime import datetime, timezone
from typing import TYPE_CHECKING
from pydantic import AwareDatetime, EmailStr
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship, func
from sqlalchemy_utc import UtcDateTime

if TYPE_CHECKING:
    from apps.calendar.models import Calendar, Booking


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_email"),
    )

    id: int = Field(default=None, primary_key=True)
    username: str = Field(max_length=40, description="사용자 계정 ID")
    email: EmailStr = Field(unique=True, max_length=128, description="사용자 이메일")
    display_name: str = Field(max_length=40, description="사용자 표시 이름")
    password: str = Field(max_length=128, description="사용자 비밀번호")
    is_host: bool = Field(default=False, description="사용자가 호스트인지 여부")

    oauth_accounts: list["OAuthAccount"] = Relationship(back_populates="user")
    calendar: "Calendar" = Relationship(
        back_populates="host",
        sa_relationship_kwargs={"uselist": False, "single_parent": True},
    )
    bookings: list["Booking"] = Relationship(back_populates="guest")

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


class OAuthAccount(SQLModel, table=True):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_account_id",
            name="uq_provider_provider_account_id",
        ),
    )

    id: int = Field(default=None, primary_key=True)
    provider: str = Field(max_length=10, description="OAuth 제공자")
    provider_account_id: str = Field(max_length=128, description="OAuth 제공자 계정 ID")

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="oauth_accounts")

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
