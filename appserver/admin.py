from sqladmin import Admin

from appserver.apps.account.admin import UserAdmin


def include_admin_views(admin: Admin):
    admin.add_view(UserAdmin)
