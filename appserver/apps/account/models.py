from typing import TYPE_CHECKING, Union
from datetime import datetime, timezone

from pydantic import AwareDatetime, EmailStr
from sqlmodel import SQLModel, Field, Relationship, func, String
from sqlmodel.main import SQLModelConfig
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utc import UtcDateTime

from .enums import AccountStatus

if TYPE_CHECKING:
    from apps.calendar.models import Calendar, Booking


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_email"),
    )

    id: int = Field(default=None, primary_key=True)
    username: str = Field(min_length=4, max_length=40, description="사용자 계정 ID")
    email: EmailStr = Field(unique=True, max_length=128, description="사용자 이메일")
    display_name: str = Field(min_length=4, max_length=40, description="사용자 표시 이름")
    hashed_password: str = Field(min_length=8, max_length=128, description="사용자 비밀번호")
    is_host: bool = Field(default=False, description="사용자가 호스트인지 여부")
    status: AccountStatus = Field(
        default=AccountStatus.ACTIVE.value,
        description="사용자 상태",
        sa_type=String,
    )

    oauth_accounts: list["OAuthAccount"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "noload"},
    )
    calendar: Union["Calendar", None] = Relationship(
        back_populates="host",
        sa_relationship_kwargs={"uselist": False, "single_parent": True, "lazy": "joined"},
    )
    bookings: list["Booking"] = Relationship(
        back_populates="guest",
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

    model_config = SQLModelConfig(
        ignored_types=(hybrid_property,),
    )

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"

    @hybrid_property
    def is_active(self) -> bool:
        return self.status in [AccountStatus.ACTIVE, AccountStatus.ACTIVE.value]

    @is_active.expression
    def is_active(cls) -> bool:
        statuses = [AccountStatus.ACTIVE.value]
        return cls.status.in_(statuses)

    @hybrid_property
    def is_deleted(self) -> bool:
        return self.status in [AccountStatus.DELETED, AccountStatus.DELETED.value]

    @is_deleted.expression
    def is_deleted(cls) -> bool:
        statuses = [AccountStatus.DELETED.value]
        return cls.status.in_(statuses)



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
    user: User = Relationship(
        back_populates="oauth_accounts",
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
