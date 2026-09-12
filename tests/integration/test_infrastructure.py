from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.infrastructure.observability.metrics import (
    lexcorp_ai_runs_total,
    lexcorp_entities_total,
    lexcorp_meetings_total,
)


class TestPrometheusMetrics:
    """Metrics objects must be importable without external deps."""

    def test_entities_count_metric_exists(self) -> None:
        assert lexcorp_entities_total is not None

    def test_meetings_count_metric_exists(self) -> None:
        assert lexcorp_meetings_total is not None

    def test_ai_runs_metric_exists(self) -> None:
        assert lexcorp_ai_runs_total is not None


class TestRedisCache:
    """Unit-test the RedisCache wrapper in isolation (mocked Redis)."""

    @pytest.mark.asyncio
    async def test_get_json_returns_none_for_missing_key(self) -> None:
        from src.infrastructure.cache.redis_client import RedisCache

        with patch("src.infrastructure.cache.redis_client.Redis.from_url") as mock_redis_factory:
            mock_conn = AsyncMock()
            mock_conn.get = AsyncMock(return_value=None)
            mock_redis_factory.return_value = mock_conn

            cache = RedisCache("redis://localhost:9379/0")
            result = await cache.get_json("nonexistent:key")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_json_deserialises_bytes(self) -> None:
        from src.infrastructure.cache.redis_client import RedisCache

        with patch("src.infrastructure.cache.redis_client.Redis.from_url") as mock_redis_factory:
            mock_conn = AsyncMock()
            mock_conn.get = AsyncMock(return_value=b'{"answer": 42}')
            mock_redis_factory.return_value = mock_conn

            cache = RedisCache("redis://localhost:9379/0")
            result = await cache.get_json("some:key")
            assert result == {"answer": 42}
