"""FastAPI dependency injection helpers.

Provides the current DB session, authenticated user context, and
application services via the DI container.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Annotated, AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services import (
    AnalyticsService,
    EntityService,
    MeetingService,
    ObligationService,
    PoAService,
    ResolutionService,
)
from src.core.config import Settings, get_settings
from src.core.security import PasetoService
from src.infrastructure.database.repositories.audit_repository import AuditRepository
from src.infrastructure.database.repositories.entity_repository import EntityRepository
from src.infrastructure.database.repositories.meeting_repository import MeetingRepository
from src.infrastructure.database.repositories.obligation_repository import ObligationRepository
from src.infrastructure.database.repositories.poa_repository import PoARepository
from src.infrastructure.database.repositories.resolution_repository import ResolutionRepository


# ── Settings ────────────────────────────────────────────────
SettingsDep = Annotated[Settings, Depends(get_settings)]


# ── Database session ────────────────────────────────────────

_session_factory = None


def set_session_factory(factory: object) -> None:
    global _session_factory  # noqa: PLW0603
    _session_factory = factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized")
    async with _session_factory() as session:  # type: ignore[misc]
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DbSession = Annotated[AsyncSession, Depends(get_db_session)]


# ── Auth ────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class CurrentUser:
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role: str


_paseto: PasetoService | None = None


def set_paseto_service(svc: PasetoService) -> None:
    global _paseto  # noqa: PLW0603
    _paseto = svc


async def get_current_user(
    authorization: Annotated[str, Header()],
) -> CurrentUser:
    """Extract and validate PASETO token from Authorization header."""
    if not _paseto:
        raise RuntimeError("Paseto service not initialized")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid authorization header")

    try:
        payload = _paseto.decode(token)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    return CurrentUser(
        user_id=uuid.UUID(payload["sub"]),
        tenant_id=uuid.UUID(payload["tid"]),
        role=payload["role"],
    )


AuthUser = Annotated[CurrentUser, Depends(get_current_user)]


# ── Application Services ───────────────────────────────────

def get_entity_service(session: DbSession) -> EntityService:
    return EntityService(EntityRepository(session), AuditRepository(session))


def get_meeting_service(session: DbSession) -> MeetingService:
    return MeetingService(MeetingRepository(session), AuditRepository(session))


def get_resolution_service(session: DbSession) -> ResolutionService:
    return ResolutionService(ResolutionRepository(session), AuditRepository(session))


def get_poa_service(session: DbSession) -> PoAService:
    return PoAService(PoARepository(session), AuditRepository(session))


def get_obligation_service(session: DbSession) -> ObligationService:
    return ObligationService(ObligationRepository(session), AuditRepository(session))


def get_analytics_service(session: DbSession) -> AnalyticsService:
    return AnalyticsService(
        EntityRepository(session),
        MeetingRepository(session),
        ObligationRepository(session),
        PoARepository(session),
    )


EntityServiceDep = Annotated[EntityService, Depends(get_entity_service)]
MeetingServiceDep = Annotated[MeetingService, Depends(get_meeting_service)]
ResolutionServiceDep = Annotated[ResolutionService, Depends(get_resolution_service)]
PoAServiceDep = Annotated[PoAService, Depends(get_poa_service)]
ObligationServiceDep = Annotated[ObligationService, Depends(get_obligation_service)]
AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]
