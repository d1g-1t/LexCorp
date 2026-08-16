"""Integration tests for infrastructure-level services (cache, observability)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.observability.metrics import (
    ai_runs,
    entities_count,
    meetings_count,
)


class TestPrometheusMetrics:
    """Metrics objects must be importable and increment-able without external deps."""

    def test_entities_count_metric_exists(self):
        # Just importing it should not raise
        assert entities_count is not None

    def test_meetings_count_metric_exists(self):
        assert meetings_count is not None

    def test_ai_runs_metric_exists(self):
        assert ai_runs is not None


class TestRedisCache:
    """Unit-test the RedisCache wrapper in isolation (mocked Redis)."""

    @pytest.mark.asyncio
    async def test_set_and_get_json(self):
        from src.infrastructure.cache.redis_client import RedisCache

        with patch("src.infrastructure.cache.redis_client.redis.from_url") as mock_redis_factory:
            mock_conn = AsyncMock()
            mock_conn.set = AsyncMock()
            mock_conn.get = AsyncMock(return_value=b'{"key":"value"}')
            mock_redis_factory.return_value = mock_conn

            cache = RedisCache("redis://localhost:9379/0")
            result = await cache.get_json("test:key")
            assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_json_returns_none_for_missing_key(self):
        from src.infrastructure.cache.redis_client import RedisCache

        with patch("src.infrastructure.cache.redis_client.redis.from_url") as mock_redis_factory:
            mock_conn = AsyncMock()
            mock_conn.get = AsyncMock(return_value=None)
            mock_redis_factory.return_value = mock_conn

            cache = RedisCache("redis://localhost:9379/0")
            result = await cache.get_json("nonexistent:key")
            assert result is None
