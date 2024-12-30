import ujson
from fastapi import status
from sqladmin import Admin
from jose.exceptions import JWTError
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from appserver.apps.account.utils import decode_token
from appserver.apps.account.schemas import LoginPayload
from appserver.apps.account.endpoints import login
from appserver.apps.account.admin import OAuthAccountAdmin, UserAdmin
from appserver.apps.calendar.admin import BookingAdmin, BookingFileAdmin, CalendarAdmin, TimeSlotAdmin
from appserver.db import use_session

def include_admin_views(admin: Admin):
    admin.add_view(UserAdmin)
    admin.add_view(CalendarAdmin)
    admin.add_view(TimeSlotAdmin)
    admin.add_view(BookingAdmin)
    admin.add_view(BookingFileAdmin)
    admin.add_view(OAuthAccountAdmin)


class AdminAuthentication(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        payload = LoginPayload(username=username, password=password)

        async for session in use_session():
            res = await login(payload, session)
            if res.status_code == status.HTTP_200_OK:
                try:
                    data = ujson.loads(res.body)
                except ujson.JSONDecodeError:
                    return False
                
                request.session.update({"token": data["access_token"]})
                return True
        
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        try:
            return not not decode_token(token)
        except JWTError:
            return False
