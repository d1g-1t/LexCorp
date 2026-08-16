"""Domain entity – Board Meeting.

First-class meeting lifecycle: DRAFT → AGENDA_SET → PACK_ASSEMBLED →
CIRCULATED → IN_SESSION → MINUTES_DRAFT → MINUTES_FINAL → CLOSED.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.exceptions import InvalidStateTransitionError, QuorumNotMetError
from src.domain.value_objects import MeetingStatus, MeetingType

_MEETING_TRANSITIONS: dict[MeetingStatus, frozenset[MeetingStatus]] = {
    MeetingStatus.DRAFT: frozenset({MeetingStatus.AGENDA_SET, MeetingStatus.CANCELLED}),
    MeetingStatus.AGENDA_SET: frozenset({MeetingStatus.PACK_ASSEMBLED, MeetingStatus.CANCELLED}),
    MeetingStatus.PACK_ASSEMBLED: frozenset({MeetingStatus.CIRCULATED, MeetingStatus.CANCELLED}),
    MeetingStatus.CIRCULATED: frozenset({MeetingStatus.IN_SESSION, MeetingStatus.CANCELLED}),
    MeetingStatus.IN_SESSION: frozenset({MeetingStatus.MINUTES_DRAFT}),
    MeetingStatus.MINUTES_DRAFT: frozenset({MeetingStatus.MINUTES_FINAL}),
    MeetingStatus.MINUTES_FINAL: frozenset({MeetingStatus.CLOSED}),
    MeetingStatus.CLOSED: frozenset(),
    MeetingStatus.CANCELLED: frozenset(),
}


class BoardMeeting:
    __slots__ = (
        "id",
        "entity_id",
        "meeting_type",
        "title",
        "scheduled_at",
        "status",
        "quorum_required",
        "quorum_met",
        "pack_storage_path",
        "created_by",
        "created_at",
    )

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        entity_id: uuid.UUID,
        meeting_type: MeetingType,
        title: str,
        scheduled_at: datetime,
        quorum_required: int,
        created_by: uuid.UUID,
        status: MeetingStatus = MeetingStatus.DRAFT,
        quorum_met: bool | None = None,
        pack_storage_path: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.entity_id = entity_id
        self.meeting_type = meeting_type
        self.title = title
        self.scheduled_at = scheduled_at
        self.status = status
        self.quorum_required = quorum_required
        self.quorum_met = quorum_met
        self.pack_storage_path = pack_storage_path
        self.created_by = created_by
        self.created_at = created_at or datetime.now(UTC)

    def advance(self, target: MeetingStatus) -> None:
        allowed = _MEETING_TRANSITIONS.get(self.status, frozenset())
        if target not in allowed:
            raise InvalidStateTransitionError("BoardMeeting", self.status, target)
        self.status = target

    def record_quorum(self, attendees_count: int) -> None:
        self.quorum_met = attendees_count >= self.quorum_required
        if not self.quorum_met:
            raise QuorumNotMetError(self.quorum_required, attendees_count)
