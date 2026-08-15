"""Dependency-Injector wiring.

Single container owns all singletons (settings, db session factory, redis,
paseto, repositories) so the FastAPI `Depends()` graph stays clean.
"""

from __future__ import annotations

from dependency_injector import containers, providers
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import Settings
from src.core.security import PasetoService


class Container(containers.DeclarativeContainer):
    """Root DI container for the application."""

    wiring_config = containers.WiringConfiguration(
        packages=["src.presentation", "src.application", "src.infrastructure"],
    )

    # ── Config ──────────────────────────────────────
    config = providers.Singleton(Settings)

    # ── Database ────────────────────────────────────
    db_engine = providers.Singleton(
        create_async_engine,
        url=config.provided.database_url,
        echo=False,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )

    db_session_factory = providers.Singleton(
        async_sessionmaker,
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # ── Redis ───────────────────────────────────────
    redis = providers.Singleton(
        Redis.from_url,
        url=config.provided.redis_url,
        decode_responses=True,
    )

    # ── Security ────────────────────────────────────
    paseto_service = providers.Singleton(PasetoService, settings=config)
