from datetime import datetime
import wtforms as wtf
from sqladmin import ModelView
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
        User.created_at,
        User.updated_at,
    ]
    column_searchable_list = [User.id, User.username, User.created_at]
    column_sortable_list = [
        User.id,
        User.email,
        User.username,
        User.created_at,
        User.updated_at,
    ]
    column_labels = {
        User.id: "ID",
        User.email: "이메일",
        User.username: "사용자 계정 ID",
        User.display_name: "표시 이름",
        User.is_host: "호스트 여부",
        User.created_at: "생성 일시",
        User.updated_at: "수정 일시",
    }
    column_default_sort = (User.created_at, True)

    form_columns = [User.email, User.username, User.display_name, User.is_host, User.hashed_password]
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

