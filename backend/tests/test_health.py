from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_all_ok(client: AsyncClient):
    with (
        patch("app.routers.health.engine") as mock_engine,
        patch("app.routers.health.aioredis.from_url") as mock_redis_factory,
    ):
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_engine.connect.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine.connect.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()
        mock_redis.aclose = AsyncMock()
        mock_redis_factory.return_value = mock_redis

        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["database"] == "ok"
        assert data["redis"] == "ok"


@pytest.mark.asyncio
async def test_health_db_down(client: AsyncClient):
    with (
        patch("app.routers.health.engine") as mock_engine,
        patch("app.routers.health.aioredis.from_url") as mock_redis_factory,
    ):
        mock_engine.connect.side_effect = Exception("connection refused")

        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()
        mock_redis.aclose = AsyncMock()
        mock_redis_factory.return_value = mock_redis

        resp = await client.get("/health")
        assert resp.status_code == 503
        data = resp.json()
        assert data["database"] == "error"
        assert data["redis"] == "ok"
