"""Domain service – Quorum validation."""

from __future__ import annotations

from src.domain.entities.board_meeting import BoardMeeting
from src.domain.exceptions import QuorumNotMetError


class QuorumService:
    """Pure domain logic for quorum checks."""

    @staticmethod
    def validate(meeting: BoardMeeting, attendees_count: int) -> bool:
        """Return True if quorum is met, raise otherwise."""
        if attendees_count < meeting.quorum_required:
            raise QuorumNotMetError(meeting.quorum_required, attendees_count)
        return True
