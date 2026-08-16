"""Domain entity – Resolution."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.exceptions import InvalidStateTransitionError
from src.domain.value_objects import ResolutionStatus

_RES_TRANSITIONS: dict[ResolutionStatus, frozenset[ResolutionStatus]] = {
    ResolutionStatus.DRAFT: frozenset({ResolutionStatus.PROPOSED}),
    ResolutionStatus.PROPOSED: frozenset({ResolutionStatus.ADOPTED, ResolutionStatus.REJECTED}),
    ResolutionStatus.ADOPTED: frozenset({ResolutionStatus.SUPERSEDED}),
    ResolutionStatus.REJECTED: frozenset(),
    ResolutionStatus.SUPERSEDED: frozenset(),
}


class Resolution:
    __slots__ = (
        "id",
        "entity_id",
        "meeting_id",
        "resolution_type",
        "title",
        "text_body",
        "status",
        "adopted_at",
        "effective_at",
        "created_by",
        "created_at",
    )

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        entity_id: uuid.UUID,
        meeting_id: uuid.UUID | None = None,
        resolution_type: str,
        title: str,
        text_body: str,
        status: ResolutionStatus = ResolutionStatus.DRAFT,
        adopted_at: datetime | None = None,
        effective_at: datetime | None = None,
        created_by: uuid.UUID,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.entity_id = entity_id
        self.meeting_id = meeting_id
        self.resolution_type = resolution_type
        self.title = title
        self.text_body = text_body
        self.status = status
        self.adopted_at = adopted_at
        self.effective_at = effective_at
        self.created_by = created_by
        self.created_at = created_at or datetime.now(UTC)

    def advance(self, target: ResolutionStatus) -> None:
        allowed = _RES_TRANSITIONS.get(self.status, frozenset())
        if target not in allowed:
            raise InvalidStateTransitionError("Resolution", self.status, target)
        self.status = target
        if target == ResolutionStatus.ADOPTED:
            self.adopted_at = datetime.now(UTC)
