import asyncio
import uuid
from copy import deepcopy
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional, Tuple

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import close_all_sessions

from app.config.config import Config
from app.core.database import Base, get_db
from app.core.entities.user.sex_entity import SexEntity
from app.core.redis.redis import get_redis
from app.core.redis.user_session_repository import UserSessionRepository
from app.core.schema.common_schemas import LoginType
from app.db.seeds.seeder import Seeder
from app.infra.dto.user.user_dto import UserDTO
from app.main import journeyLingua

TEST_USER_EMAIL = "journeylingua@gmail.com"
TEST_USER_PHONE = "0969090658"

MYSQL_TEST_URL = (
    f"mysql+aiomysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}"
    f"@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}"
    f"/{Config.MYSQL_TEST_DB_NAME}?charset=utf8mb4"
)


class TestingAsyncSession(AsyncSession):
    async def commit(self):
        await self.flush()
        self.expire_all()

    async def remove(self):
        self.expire_all()

    def real_remove(self):
        super(TestingAsyncSession, self).remove()


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.is_closed() or loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_client(event_loop, test_session) -> AsyncGenerator:
    try:
        test_session.begin_nested()
        async with AsyncClient(app=journeyLingua, base_url="http://journey-lingua-api:8082") as client:
            yield client
    finally:
        await test_session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_session(event_loop, test_db_seed) -> AsyncSession:
    engine = create_async_engine(MYSQL_TEST_URL, echo=True)
    function_scope = uuid.uuid4().hex
    async_session = async_scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            future=True,
            class_=TestingAsyncSession,
        ),
        scopefunc=lambda: function_scope,
    )

    async with async_session() as session:

        async def get_test_db():
            try:
                yield session
            except SQLAlchemyError as e:
                assert e is not None

        journeyLingua.dependency_overrides[get_db] = get_test_db

        try:
            yield session
        finally:
            await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_db_seed(event_loop, test_create_table) -> AsyncSession:
    engine = create_async_engine(MYSQL_TEST_URL, echo=True)
    function_scope = uuid.uuid4().hex
    async_session = async_scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            future=True,
            class_=AsyncSession,
        ),
        scopefunc=lambda: function_scope,
    )
    async with async_session() as session:
        try:
            await Seeder(session).seed()
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="session")
async def test_create_table(event_loop, test_create_db):
    engine = create_async_engine(MYSQL_TEST_URL, echo=True)
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        finally:
            await conn.close()


@pytest_asyncio.fixture(scope="session")
async def test_create_db(event_loop) -> AsyncGenerator:
    url = f"mysql+aiomysql://root:root@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}"
    engine = create_async_engine(url, echo=True)
    async with engine.begin() as conn:
        try:
            await conn.execute(
                text(f"GRANT ALL PRIVILEGES ON {Config.MYSQL_TEST_DB_NAME}.* TO 'local'@'%' WITH GRANT OPTION")
            )
            await conn.execute(text(f"DROP DATABASE IF EXISTS {Config.MYSQL_TEST_DB_NAME}"))
            await conn.execute(text(f"CREATE DATABASE {Config.MYSQL_TEST_DB_NAME}"))
        finally:
            await conn.close()

    try:
        yield
    finally:
        close_all_sessions()
        await engine.dispose()


class RedisMock:
    store: Dict[str, Tuple[str, Optional[int]]]

    def __init__(self):
        self.store = {}

    async def get(self, key: str) -> Optional[str]:
        try:
            value, expiration = self.store[key]
            if expiration is not None and expiration < datetime.now().timestamp():
                return None
            return value
        except KeyError:
            return None

    async def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None,
        nx: Optional[bool] = False,
    ):
        expiration = None
        if ex is not None:
            expiration = int(datetime.now().timestamp() + ex)
        if nx and await self.get(key) is not None:
            return None
        self.store[key] = (value, expiration)
        if nx:
            return True

    async def delete(self, key: str):
        try:
            del self.store[key]
        except KeyError:
            pass

    async def keys(self) -> List[str]:
        ex_idx = 1
        keys = []
        for key, val_ex in self.store.items():
            ex = val_ex[ex_idx]
            if ex is not None and int(ex) < datetime.now().timestamp():
                continue
            keys.append(key)
        return keys


@pytest_asyncio.fixture(scope="function")
def redis() -> RedisMock:
    mock_redis = RedisMock()

    def get_redis_mock():
        return mock_redis

    journeyLingua.dependency_overrides[get_redis] = get_redis_mock
    return mock_redis


@pytest_asyncio.fixture(scope="function")
async def test_create_user(test_session, request) -> UserDTO:
    email = request.param["email"] if "email" in request.param else None
    phone = request.param["phone"] if "phone" in request.param else None
    is_email_verified = request.param["is_email_verified"] if "is_email_verified" in request.param else False
    is_phone_verified = request.param["is_phone_verified"] if "is_phone_verified" in request.param else False
    test_session
    user = UserDTO(
        email=email,
        phone=phone,
        hashed_password="$2b$12$nWgpkd/pBg.75e9AeZzMA.Zme1CILXGDsNHy.xhQcoQdLs7uEiCn2",
        is_email_verified=is_email_verified,
        is_phone_verified=is_phone_verified,
        is_active=True,
        sex_code=SexEntity.CODE_NOT_KNOWN,
    )
    test_session.begin_nested()
    test_session.add(user)
    await test_session.flush()
    await test_session.refresh(user)
    user.user_code = str(user.id)
    await test_session.commit()
    await test_session.refresh(user)
    user = deepcopy(user)
    yield user


@pytest_asyncio.fixture(scope="function")
async def test_create_user_with_session(redis, test_create_user) -> UserDTO:
    if test_create_user.to_entity().email:
        token = await UserSessionRepository(redis=redis).write_token(test_create_user.to_entity(), LoginType.EMAIL)
    else:
        token = await UserSessionRepository(redis=redis).write_token(test_create_user.to_entity(), LoginType.PHONE)
    yield test_create_user, token
