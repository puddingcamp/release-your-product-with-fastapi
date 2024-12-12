from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)


def create_engine(dsn: str):
    return create_async_engine(
        dsn,
        echo=False,
    )


def create_session(async_engine: AsyncEngine | None = None):
    if async_engine is None:
        async_engine = create_engine()

    return async_sessionmaker(
        async_engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )


async def use_session():
    async with async_session_factory() as session:
        yield session

DbSessionDep = Annotated[AsyncSession, Depends(use_session)]


DSN = "sqlite+aiosqlite:///./local.db"

engine = create_engine(DSN)

async_session_factory = create_session(engine)
