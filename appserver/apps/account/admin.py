from sqladmin import ModelView

from .models import User


class UserAdmin(ModelView, model=User):
    pass