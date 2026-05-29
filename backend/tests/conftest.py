from unittest.mock import AsyncMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.models.user import User  # noqa: F401

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
test_session_factory = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with test_session_factory() as session:
        yield session


def make_redis_mock(store: dict | None = None) -> AsyncMock:
    if store is None:
        store = {}

    mock = AsyncMock()

    async def _setex(key, ttl, value):
        store[key] = value

    async def _get(key):
        return store.get(key)

    async def _delete(key):
        store.pop(key, None)

    async def _ping():
        return True

    async def _aclose():
        pass

    mock.setex = AsyncMock(side_effect=_setex)
    mock.get = AsyncMock(side_effect=_get)
    mock.delete = AsyncMock(side_effect=_delete)
    mock.ping = AsyncMock(side_effect=_ping)
    mock.aclose = AsyncMock(side_effect=_aclose)
    return mock


@pytest_asyncio.fixture
async def redis_store():
    return {}


@pytest_asyncio.fixture
async def redis_mock(redis_store):
    return make_redis_mock(redis_store)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, redis_mock):
    from app.core.deps import get_redis

    async def override_get_db():
        yield db_session

    async def override_get_redis():
        yield redis_mock

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(client: AsyncClient):
    resp = await client.post(
        "/auth/register", json={"email": "user@example.com", "password": "SecurePass123!"}
    )
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def auth_tokens(client: AsyncClient, test_user):
    resp = await client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "SecurePass123!"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"], resp.cookies.get("refresh_token")
