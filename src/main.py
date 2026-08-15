"""
LexCorp — FastAPI Application Factory
=====================================================

Single entry-point that wires together every layer:
  - DI container (dependency-injector)
  - Database engine + async session factory
  - Redis cache
  - PASETO security service
  - OpenTelemetry tracing + structlog
  - Middleware stack (request-id, security-headers, CORS)
  - Rate limiter (slowapi)
  - Domain-exception → HTTP-error handlers
  - All v1 API routers
  - Lifespan events (startup / shutdown)

Usage:
    uvicorn src.main:app --host 0.0.0.0 --port 9100 --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import Settings
from src.core.logging import setup_logging
from src.core.security import PasetoService
from src.core.telemetry import setup_telemetry
from src.infrastructure.cache.redis_client import RedisCache
from src.presentation.api.v1 import (
    analytics,
    audit,
    auth,
    entities,
    filings,
    health,
    meetings,
    obligations,
    poa,
    resolutions,
)
from src.presentation.deps import set_paseto_service, set_session_factory
from src.presentation.exception_handlers import register_exception_handlers
from src.presentation.middleware.rate_limit import limiter
from src.presentation.middleware.request_id import RequestIDMiddleware
from src.presentation.middleware.security_headers import SecurityHeadersMiddleware

logger = structlog.get_logger(__name__)


# =====================================================================
#  Lifespan — startup / shutdown
# =====================================================================
@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage resources that live for the entire application lifetime."""
    settings: Settings = application.state.settings

    # --- Database ---
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    set_session_factory(session_factory)

    # --- Redis ---
    redis = RedisCache(settings.redis_url)
    application.state.redis = redis

    # --- PASETO ---
    paseto_svc = PasetoService(
        secret_key=settings.paseto_secret_key,
        access_token_ttl=settings.access_token_ttl,
        refresh_token_ttl=settings.refresh_token_ttl,
    )
    set_paseto_service(paseto_svc)

    logger.info(
        "app_startup_complete",
        database=settings.postgres_host,
        redis=settings.redis_host,
        debug=settings.debug,
    )

    yield  # application runs here

    # --- Shutdown ---
    await engine.dispose()
    await redis.close()
    logger.info("app_shutdown_complete")


# =====================================================================
#  Factory
# =====================================================================
def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and return the fully-wired FastAPI application."""
    if settings is None:
        settings = Settings()

    # Logging & tracing
    setup_logging(json_output=not settings.debug)
    if settings.otel_exporter_otlp_endpoint:
        setup_telemetry(
            service_name=settings.app_name,
            otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        )

    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="LexCorp — AI-powered corporate governance platform",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )
    application.state.settings = settings

    # ---------- Middleware (order matters: outermost first) ----------
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------- Rate limiter ----------
    limiter.storage_uri = settings.redis_url
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ---------- Domain exception handlers ----------
    register_exception_handlers(application)

    # ---------- Routers ----------
    api_prefix = "/api/v1"
    application.include_router(auth.router, prefix=api_prefix, tags=["Auth"])
    application.include_router(entities.router, prefix=api_prefix, tags=["Entities"])
    application.include_router(meetings.router, prefix=api_prefix, tags=["Meetings"])
    application.include_router(resolutions.router, prefix=api_prefix, tags=["Resolutions"])
    application.include_router(poa.router, prefix=api_prefix, tags=["Powers of Attorney"])
    application.include_router(obligations.router, prefix=api_prefix, tags=["Obligations"])
    application.include_router(filings.router, prefix=api_prefix, tags=["Filings"])
    application.include_router(analytics.router, prefix=api_prefix, tags=["Analytics"])
    application.include_router(audit.router, prefix=api_prefix, tags=["Audit"])
    application.include_router(health.router, tags=["Health"])

    logger.info("app_created", app_name=settings.app_name)
    return application


# Default app instance for `uvicorn src.main:app`
app = create_app()
