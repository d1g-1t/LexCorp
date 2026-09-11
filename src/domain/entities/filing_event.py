from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from src.domain.value_objects import FilingStatus


class FilingEvent:
    __slots__ = (
        "id",
        "entity_id",
        "obligation_id",
        "filing_type",
        "filed_at",
        "deadline_at",
        "status",
        "evidence_payload",
    )

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        entity_id: uuid.UUID,
        obligation_id: uuid.UUID | None = None,
        filing_type: str,
        filed_at: datetime | None = None,
        deadline_at: datetime,
        status: FilingStatus = FilingStatus.PENDING,
        evidence_payload: dict[str, Any] | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.entity_id = entity_id
        self.obligation_id = obligation_id
        self.filing_type = filing_type
        self.filed_at = filed_at
        self.deadline_at = deadline_at
        self.status = status
        self.evidence_payload = evidence_payload or {}

    def file(self, evidence: dict[str, Any] | None = None) -> None:
        self.status = FilingStatus.FILED
        self.filed_at = datetime.now(UTC)
        if evidence:
            self.evidence_payload = evidence
