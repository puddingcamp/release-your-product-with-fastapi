from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine

from appserver.apps.account.endpoints import router as account_router
from appserver.apps.calendar.endpoints import router as calendar_router
from appserver.admin import include_admin_views, AdminAuthentication
from .db import engine

app = FastAPI()

def include_routers(_app: FastAPI):
    _app.include_router(account_router)
    _app.include_router(calendar_router)
    
    _app.mount("/static", StaticFiles(directory="static"), name="static")
    _app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

include_routers(app)


def init_admin(_app: FastAPI, _engine: AsyncEngine):
    return Admin(
        _app,
        _engine,
        base_url="/@/-_-/@/nimda/",
        authentication_backend=AdminAuthentication("secret-key"),
    )


admin = init_admin(app, engine)
include_admin_views(admin)
