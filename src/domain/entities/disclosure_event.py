from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from src.domain.value_objects import DisclosureStatus


class DisclosureEvent:
    __slots__ = ("id", "entity_id", "event_type", "title", "due_at", "status", "metadata")

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        entity_id: uuid.UUID,
        event_type: str,
        title: str,
        due_at: datetime,
        status: DisclosureStatus = DisclosureStatus.OPEN,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.entity_id = entity_id
        self.event_type = event_type
        self.title = title
        self.due_at = due_at
        self.status = status
        self.metadata = metadata or {}

    def disclose(self) -> None:
        self.status = DisclosureStatus.DISCLOSED

    def mark_overdue(self) -> None:
        if self.status == DisclosureStatus.OPEN and self.due_at <= datetime.now(UTC):
            self.status = DisclosureStatus.OVERDUE
