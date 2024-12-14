import random
import string
from typing import Self
from pydantic import EmailStr, model_validator
from sqlmodel import SQLModel, Field


class SignupPayload(SQLModel):
    username: str = Field(min_length=4, max_length=40, description="사용자 계정 ID")
    email: EmailStr = Field(unique=True, max_length=128, description="사용자 이메일")
    display_name: str = Field(min_length=4, max_length=40, description="사용자 표시 이름")
    password: str = Field(min_length=8, max_length=128, description="사용자 비밀번호")
    password_again: str = Field(min_length=8, max_length=128, description="사용자 비밀번호 확인")

    @model_validator(mode="after")
    def verify_password(self) -> Self:
        if self.password != self.password_again:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return self

    @model_validator(mode="before")
    @classmethod
    def generate_display_name(cls, data: dict):
        if not data.get("display_name"):
            data["display_name"] = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        return data


class UserOut(SQLModel):
    username: str
    display_name: str
    is_host: bool


class LoginPayload(SQLModel):
    username: str = Field(min_length=4, max_length=40)
    password: str = Field(min_length=8, max_length=128)
