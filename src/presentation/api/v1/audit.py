"""Audit timeline endpoint."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.application.dto.schemas import AuditTimelineEntry
from src.infrastructure.database.repositories.audit_repository import AuditRepository
from src.presentation.deps import AuthUser, DbSession

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/resources/{resource_type}/{resource_id}/timeline", response_model=list[AuditTimelineEntry])
async def audit_timeline(
    resource_type: str,
    resource_id: uuid.UUID,
    session: DbSession,
    user: AuthUser,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
) -> list[AuditTimelineEntry]:
    repo = AuditRepository(session)
    events = await repo.get_timeline(resource_type, resource_id, limit=limit, offset=offset)
    return [
        AuditTimelineEntry(
            id=e.id,
            event_type=e.event_type.value,
            resource_type=e.resource_type,
            resource_id=e.resource_id,
            actor_user_id=e.actor_user_id,
            payload=e.payload,
            created_at=e.created_at,
        )
        for e in events
    ]
