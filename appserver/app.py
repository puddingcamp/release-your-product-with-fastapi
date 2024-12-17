from fastapi import FastAPI
from .apps.account.endpoints import router as account_router
from .apps.calendar.endpoints import router as calendar_router

app = FastAPI()

def include_routers(_app: FastAPI):
    _app.include_router(account_router)
    _app.include_router(calendar_router)

include_routers(app)
