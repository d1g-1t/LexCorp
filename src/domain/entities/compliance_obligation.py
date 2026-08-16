"""Domain entity – Compliance Obligation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.value_objects import ObligationStatus


class ComplianceObligation:
    __slots__ = (
        "id",
        "entity_id",
        "obligation_type",
        "title",
        "due_at",
        "recurrence_rule",
        "status",
        "evidence_path",
        "created_at",
        "completed_at",
    )

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        entity_id: uuid.UUID,
        obligation_type: str,
        title: str,
        due_at: datetime,
        recurrence_rule: str | None = None,
        status: ObligationStatus = ObligationStatus.OPEN,
        evidence_path: str | None = None,
        created_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.entity_id = entity_id
        self.obligation_type = obligation_type
        self.title = title
        self.due_at = due_at
        self.recurrence_rule = recurrence_rule
        self.status = status
        self.evidence_path = evidence_path
        self.created_at = created_at or datetime.now(UTC)
        self.completed_at = completed_at

    def complete(self, evidence_path: str | None = None) -> None:
        self.status = ObligationStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        if evidence_path:
            self.evidence_path = evidence_path

    def mark_overdue(self) -> None:
        if self.status == ObligationStatus.OPEN and self.due_at <= datetime.now(UTC):
            self.status = ObligationStatus.OVERDUE
