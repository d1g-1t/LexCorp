"""Domain entity – Audit Event (immutable governance audit trail)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from src.domain.value_objects import AuditEventType


class AuditEvent:
    """Immutable: once created, never modified."""

    __slots__ = (
        "id",
        "tenant_id",
        "actor_user_id",
        "resource_type",
        "resource_id",
        "event_type",
        "trace_id",
        "payload",
        "created_at",
    )

    def __init__(
        self,
        *,
        tenant_id: uuid.UUID,
        actor_user_id: uuid.UUID | None = None,
        resource_type: str,
        resource_id: uuid.UUID,
        event_type: AuditEventType,
        trace_id: str | None = None,
        payload: dict[str, Any] | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.tenant_id = tenant_id
        self.actor_user_id = actor_user_id
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.event_type = event_type
        self.trace_id = trace_id
        self.payload = payload or {}
        self.created_at = created_at or datetime.now(UTC)
