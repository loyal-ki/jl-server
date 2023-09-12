from asyncio import current_task
from typing import AsyncGenerator, TypeVar

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta

from app.config.config import Config

MYSQL_URL = (
    f"mysql+aiomysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}"
    f"@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}"
    f"/{Config.MYSQL_DB_NAME}?charset=utf8mb4"
)

async_engine = create_async_engine(MYSQL_URL, echo=True)
AsyncSessionLocal = async_scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine,
        future=True,
        class_=AsyncSession,
    ),
    scopefunc=current_task,
)

Base: DeclarativeMeta = declarative_base()

BaseT = TypeVar("BaseT", bound=DeclarativeMeta)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    @brief Get a database.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
