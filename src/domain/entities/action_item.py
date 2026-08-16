"""Domain entity – Action Item."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.value_objects import ActionItemStatus


class ActionItem:
    __slots__ = (
        "id",
        "meeting_id",
        "resolution_id",
        "entity_id",
        "title",
        "description",
        "assigned_user_id",
        "due_at",
        "status",
        "completed_at",
    )

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        meeting_id: uuid.UUID | None = None,
        resolution_id: uuid.UUID | None = None,
        entity_id: uuid.UUID,
        title: str,
        description: str | None = None,
        assigned_user_id: uuid.UUID | None = None,
        due_at: datetime | None = None,
        status: ActionItemStatus = ActionItemStatus.OPEN,
        completed_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.meeting_id = meeting_id
        self.resolution_id = resolution_id
        self.entity_id = entity_id
        self.title = title
        self.description = description
        self.assigned_user_id = assigned_user_id
        self.due_at = due_at
        self.status = status
        self.completed_at = completed_at

    def complete(self) -> None:
        self.status = ActionItemStatus.COMPLETED
        self.completed_at = datetime.now(UTC)

    def mark_overdue(self) -> None:
        self.status = ActionItemStatus.OVERDUE
