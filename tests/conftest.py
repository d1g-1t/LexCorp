from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import Settings
from src.core.security import PasetoService
from src.infrastructure.database.models import Base
from src.main import create_app
from src.presentation.deps import set_paseto_service, set_session_factory

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Return settings tuned for testing."""
    return Settings(
        postgres_host="localhost",
        postgres_port=9432,
        postgres_user="test",
        postgres_password="test",
        postgres_db="test_lexcorp",
        redis_host="localhost",
        redis_port=9379,
        paseto_secret_key="test-secret-key-must-be-32-bytes!",
        debug=True,
        cors_allow_origins="*",
        app_env="dev",
    )


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncIterator[AsyncSession]:
    """Yield a session wrapped in a savepoint that rolls back after each test."""
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
def paseto_service(settings: Settings) -> PasetoService:
    return PasetoService(settings)


@pytest.fixture
def sample_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def sample_tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def access_token(
    paseto_service: PasetoService,
    sample_user_id: uuid.UUID,
    sample_tenant_id: uuid.UUID,
) -> str:
    return paseto_service.create_access_token(
        user_id=sample_user_id,
        role="admin",
        tenant_id=sample_tenant_id,
    )


@pytest.fixture
def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def client(db_engine, paseto_service, settings: Settings) -> AsyncIterator[AsyncClient]:
    """Provide an httpx AsyncClient connected to a test app instance."""
    app = create_app(settings)

    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    set_session_factory(session_factory)
    set_paseto_service(paseto_service)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def entity_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def meeting_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def now() -> datetime:
    return datetime.now(UTC)


@pytest.fixture
def future_date() -> datetime:
    return datetime.now(UTC) + timedelta(days=30)
