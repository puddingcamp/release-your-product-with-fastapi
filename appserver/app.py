from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine

from appserver.apps.account.endpoints import router as account_router
from appserver.apps.calendar.endpoints import router as calendar_router
from appserver.admin import include_admin_views
from .db import engine

app = FastAPI()

def include_routers(_app: FastAPI):
    _app.include_router(account_router)
    _app.include_router(calendar_router)

include_routers(app)


def init_admin(_app: FastAPI, _engine: AsyncEngine):
    return Admin(_app, _engine)


admin = init_admin(app, engine)
include_admin_views(admin)
