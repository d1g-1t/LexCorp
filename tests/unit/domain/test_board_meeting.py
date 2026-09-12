from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from src.domain.entities.board_meeting import BoardMeeting
from src.domain.exceptions import InvalidStateTransitionError, QuorumNotMetError
from src.domain.value_objects import MeetingStatus, MeetingType


@pytest.fixture
def draft_meeting() -> BoardMeeting:
    return BoardMeeting(
        entity_id=uuid.uuid4(),
        meeting_type=MeetingType.BOARD,
        title="Очередное заседание совета директоров",
        scheduled_at=datetime.now(UTC) + timedelta(days=7),
        quorum_required=5,
        created_by=uuid.uuid4(),
    )


class TestBoardMeetingLifecycle:
    """Full happy-path lifecycle through all states."""

    def test_initial_status_is_draft(self, draft_meeting: BoardMeeting):
        assert draft_meeting.status == MeetingStatus.DRAFT

    def test_advance_draft_to_agenda_set(self, draft_meeting: BoardMeeting):
        draft_meeting.advance(MeetingStatus.AGENDA_SET)
        assert draft_meeting.status == MeetingStatus.AGENDA_SET

    def test_full_lifecycle(self, draft_meeting: BoardMeeting):
        transitions = [
            MeetingStatus.AGENDA_SET,
            MeetingStatus.PACK_ASSEMBLED,
            MeetingStatus.CIRCULATED,
            MeetingStatus.IN_SESSION,
            MeetingStatus.MINUTES_DRAFT,
            MeetingStatus.MINUTES_FINAL,
            MeetingStatus.CLOSED,
        ]
        for target in transitions:
            draft_meeting.advance(target)
        assert draft_meeting.status == MeetingStatus.CLOSED

    def test_cancel_from_draft(self, draft_meeting: BoardMeeting):
        draft_meeting.advance(MeetingStatus.CANCELLED)
        assert draft_meeting.status == MeetingStatus.CANCELLED

    def test_cancel_from_circulated(self, draft_meeting: BoardMeeting):
        draft_meeting.advance(MeetingStatus.AGENDA_SET)
        draft_meeting.advance(MeetingStatus.PACK_ASSEMBLED)
        draft_meeting.advance(MeetingStatus.CIRCULATED)
        draft_meeting.advance(MeetingStatus.CANCELLED)
        assert draft_meeting.status == MeetingStatus.CANCELLED


class TestBoardMeetingInvalidTransitions:
    def test_cannot_skip_states(self, draft_meeting: BoardMeeting):
        with pytest.raises(InvalidStateTransitionError):
            draft_meeting.advance(MeetingStatus.IN_SESSION)

    def test_cannot_go_backwards(self, draft_meeting: BoardMeeting):
        draft_meeting.advance(MeetingStatus.AGENDA_SET)
        with pytest.raises(InvalidStateTransitionError):
            draft_meeting.advance(MeetingStatus.DRAFT)

    def test_closed_is_terminal(self, draft_meeting: BoardMeeting):
        for target in [
            MeetingStatus.AGENDA_SET,
            MeetingStatus.PACK_ASSEMBLED,
            MeetingStatus.CIRCULATED,
            MeetingStatus.IN_SESSION,
            MeetingStatus.MINUTES_DRAFT,
            MeetingStatus.MINUTES_FINAL,
            MeetingStatus.CLOSED,
        ]:
            draft_meeting.advance(target)
        with pytest.raises(InvalidStateTransitionError):
            draft_meeting.advance(MeetingStatus.DRAFT)

    def test_cancelled_is_terminal(self, draft_meeting: BoardMeeting):
        draft_meeting.advance(MeetingStatus.CANCELLED)
        with pytest.raises(InvalidStateTransitionError):
            draft_meeting.advance(MeetingStatus.DRAFT)

    def test_cannot_cancel_from_in_session(self, draft_meeting: BoardMeeting):
        draft_meeting.advance(MeetingStatus.AGENDA_SET)
        draft_meeting.advance(MeetingStatus.PACK_ASSEMBLED)
        draft_meeting.advance(MeetingStatus.CIRCULATED)
        draft_meeting.advance(MeetingStatus.IN_SESSION)
        with pytest.raises(InvalidStateTransitionError):
            draft_meeting.advance(MeetingStatus.CANCELLED)


class TestQuorum:
    def test_quorum_met(self, draft_meeting: BoardMeeting):
        draft_meeting.record_quorum(5)
        assert draft_meeting.quorum_met is True

    def test_quorum_not_met(self, draft_meeting: BoardMeeting):
        with pytest.raises(QuorumNotMetError):
            draft_meeting.record_quorum(3)

    def test_quorum_exactly_required(self, draft_meeting: BoardMeeting):
        draft_meeting.record_quorum(5)  # quorum_required=5
        assert draft_meeting.quorum_met is True
