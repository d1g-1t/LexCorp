"""Domain entity – Meeting Minutes."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.domain.value_objects import MeetingStatus


class MeetingMinutes:
    __slots__ = (
        "id",
        "meeting_id",
        "draft_text",
        "final_text",
        "status",
        "reviewed_by",
        "finalized_at",
        "created_at",
    )

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        meeting_id: uuid.UUID,
        draft_text: str,
        final_text: str | None = None,
        status: MeetingStatus = MeetingStatus.MINUTES_DRAFT,
        reviewed_by: uuid.UUID | None = None,
        finalized_at: datetime | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.meeting_id = meeting_id
        self.draft_text = draft_text
        self.final_text = final_text
        self.status = status
        self.reviewed_by = reviewed_by
        self.finalized_at = finalized_at
        self.created_at = created_at or datetime.now(UTC)

    def finalize(self, final_text: str, reviewer_id: uuid.UUID) -> None:
        self.final_text = final_text
        self.reviewed_by = reviewer_id
        self.finalized_at = datetime.now(UTC)
        self.status = MeetingStatus.MINUTES_FINAL
