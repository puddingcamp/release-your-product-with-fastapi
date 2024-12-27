import random
import string
from datetime import datetime
from typing import Any, Type

import wtforms as wtf
from fastapi import Request
from sqladmin import ModelView, fields
from sqlmodel import select
from sqlalchemy.sql.expression import Select, select

from appserver.apps.account.enums import AccountStatus
from appserver.apps.account.utils import hash_password

from .models import OAuthAccount, User


class UserAdmin(ModelView, model=User):
    category = "계정"
    icon = "fa-solid fa-user"
    name = "사용자"
    name_plural = "사용자"
    column_list = [
        User.id,
        User.email,
        User.username,
        User.display_name,
        User.is_host,
        User.status,
        User.created_at,
        User.updated_at,
    ]
    column_searchable_list = [User.id, User.username, User.created_at]
    column_sortable_list = [
        User.id,
        User.email,
        User.username,
        User.status,
        User.created_at,
        User.updated_at,
    ]
    column_labels = {
        User.id: "ID",
        User.email: "이메일",
        User.username: "사용자 계정 ID",
        User.display_name: "표시 이름",
        User.is_host: "호스트 여부",
        User.status: "상태",
        User.created_at: "생성 일시",
        User.updated_at: "수정 일시",
    }
    column_default_sort = (User.created_at, True)

    form_columns = [
        User.email,
        User.username,
        User.display_name,
        User.is_host,
        User.status,
        User.hashed_password,
    ]
    form_overrides = {
        "email": wtf.EmailField,
    }
    column_type_formatters = {
        datetime: lambda v: v.strftime("%Y년 %m월 %d일 %H:%M:%S") if v else "-",
    }
    form_ajax_refs = {
        "calendar": {
           "fields": ["id", "description"],
            "order_by": "id",
        },
    }

    # 이중으로 암호화해싱을 하므로 주석 처리 함.
    # async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
    #     if is_created:
    #         data["hashed_password"] = hash_password(data["hashed_password"])
    #     else:
    #         if model.hashed_password != data["hashed_password"]:
    #             data["hashed_password"] = hash_password(data["hashed_password"])

    async def insert_model(self, request: Request, data: dict) -> Any:
        data["hashed_password"] = hash_password(data["hashed_password"])
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: str, data: dict) -> Any:
        async with self.session_maker() as session:
            obj: User = await session.get(User, pk)
            
        if obj.hashed_password != data["hashed_password"]:
            data["hashed_password"] = hash_password(data["hashed_password"])
        return await super().update_model(request, pk, data)

    async def on_model_delete(self, model: User, request: Request) -> None:
        random_string = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        model.username = f"deleted/{random_string}"
        model.email = f"deleted/{random_string}@localhost"
        model.hashed_password = ""
        model.display_name = ""
    
    async def delete_model(self, request: Request, pk: Any) -> None:
        async with self.session_maker() as session:
            obj: User = await session.get(User, pk)

            await self.on_model_delete(obj, request)

            obj.status = AccountStatus.DELETED.value
            await session.commit()
            await session.refresh(obj)

            await self.after_model_delete(obj, request)

    async def after_model_delete(self, model: User, request: Request) -> None:
        async with self.session_maker() as session:
            stmt = select(OAuthAccount).where(OAuthAccount.user_id == model.id)
            result = await session.execute(stmt)
            for oauth_account in result.scalars().all():
                await session.delete(oauth_account)
            await session.commit()

    async def scaffold_form(self, rules: list[str] | None = None) -> Type[wtf.Form]:
        form = await super().scaffold_form(rules)
        form.status = fields.SelectField(
            label="상태",
            allow_blank=User.status.nullable,
            choices=[(member.value, member.name) for member in AccountStatus],
        )
        return form

    def list_query(self, request: Request) -> Select:
        stmt = super().list_query(request)
        stmt = stmt.where(~User.is_deleted)
        return stmt


class OAuthAccountAdmin(ModelView, model=OAuthAccount):
    category = "계정"
    icon = "fa-solid fa-user-plus"
    name = "소셜 계정"
    name_plural = "소셜 계정"
    column_list = [
        OAuthAccount.id,
        OAuthAccount.user,
        OAuthAccount.provider,
        OAuthAccount.provider_account_id,
        OAuthAccount.created_at,
        OAuthAccount.updated_at,
    ]
    column_type_formatters = {
        datetime: lambda v: v.strftime("%Y년 %m월 %d일 %H:%M:%S") if v else "-",
    }
    column_labels = {
        OAuthAccount.user: "사용자",
        OAuthAccount.provider: "OAuth 제공자",
        OAuthAccount.provider_account_id: "OAuth 제공자 계정 ID",
        OAuthAccount.created_at: "생성 일시",
        OAuthAccount.updated_at: "수정 일시",
    }
    form_columns = [
        OAuthAccount.user,
        OAuthAccount.provider,
        OAuthAccount.provider_account_id,
    ]
    form_ajax_refs = {
        "user": {
            "fields": ["id", "username"],
            "order_by": "id",
        },
    }
