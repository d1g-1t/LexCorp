"""Concrete repository – Audit Event (append-only)."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.audit_event import AuditEvent
from src.domain.repositories.i_audit_repository import IAuditRepository
from src.domain.value_objects import AuditEventType
from src.infrastructure.database.models import AuditEventModel


def _to_domain(m: AuditEventModel) -> AuditEvent:
    return AuditEvent(
        id=m.id,
        tenant_id=m.tenant_id,
        actor_user_id=m.actor_user_id,
        resource_type=m.resource_type,
        resource_id=m.resource_id,
        event_type=AuditEventType(m.event_type),
        trace_id=m.trace_id,
        payload=m.payload,
        created_at=m.created_at,
    )


class AuditRepository(IAuditRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, event: AuditEvent) -> AuditEvent:
        model = AuditEventModel(
            id=event.id,
            tenant_id=event.tenant_id,
            actor_user_id=event.actor_user_id,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            event_type=event.event_type.value,
            trace_id=event.trace_id,
            payload=event.payload,
            created_at=event.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return event

    async def get_timeline(
        self,
        resource_type: str,
        resource_id: uuid.UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEvent]:
        stmt = (
            select(AuditEventModel)
            .where(
                AuditEventModel.resource_type == resource_type,
                AuditEventModel.resource_id == resource_id,
            )
            .order_by(AuditEventModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        rows: Sequence[AuditEventModel] = result.scalars().all()
        return [_to_domain(r) for r in rows]
