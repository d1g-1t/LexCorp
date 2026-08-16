"""Domain entity – Agenda Item."""

from __future__ import annotations

import uuid
from typing import Any

from src.domain.value_objects import GovernanceRiskLevel


class AgendaItem:
    __slots__ = ("id", "meeting_id", "item_order", "title", "description", "risk_level", "metadata")

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        meeting_id: uuid.UUID,
        item_order: int,
        title: str,
        description: str | None = None,
        risk_level: GovernanceRiskLevel = GovernanceRiskLevel.LOW,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.meeting_id = meeting_id
        self.item_order = item_order
        self.title = title
        self.description = description
        self.risk_level = risk_level
        self.metadata = metadata or {}
