from __future__ import annotations

from src.domain.value_objects import (
    EntityStatus,
    EntityType,
    FilingStatus,
    GovernanceRiskLevel,
    MeetingStatus,
    MeetingType,
    ObligationStatus,
    PoAStatus,
    ResolutionStatus,
    UserRole,
)


class TestEntityStatus:
    def test_all_values(self) -> None:
        assert set(EntityStatus) == {
            EntityStatus.ACTIVE,
            EntityStatus.INACTIVE,
            EntityStatus.LIQUIDATING,
            EntityStatus.LIQUIDATED,
        }

    def test_from_string(self) -> None:
        assert EntityStatus("ACTIVE") == EntityStatus.ACTIVE


class TestEntityType:
    def test_includes_ooo_and_ao(self) -> None:
        types = {e.value for e in EntityType}
        assert "OOO" in types
        assert "AO" in types


class TestMeetingStatus:
    def test_full_lifecycle(self) -> None:
        assert len(list(MeetingStatus)) >= 5

    def test_draft_exists(self) -> None:
        assert MeetingStatus.DRAFT == MeetingStatus("DRAFT")

    def test_closed_is_terminal(self) -> None:
        assert MeetingStatus.CLOSED.value == "CLOSED"


class TestResolutionStatus:
    def test_adopted_exists(self) -> None:
        assert ResolutionStatus.ADOPTED == ResolutionStatus("ADOPTED")


class TestPoAStatus:
    def test_active_and_revoked(self) -> None:
        assert PoAStatus.ACTIVE.value == "ACTIVE"
        assert PoAStatus.REVOKED.value == "REVOKED"


class TestObligationStatus:
    def test_open_and_completed(self) -> None:
        assert ObligationStatus.OPEN.value == "OPEN"
        assert ObligationStatus.COMPLETED.value == "COMPLETED"


class TestFilingStatus:
    def test_has_overdue(self) -> None:
        assert FilingStatus.OVERDUE.value == "OVERDUE"


class TestGovernanceRiskLevel:
    def test_ordering(self) -> None:
        levels = [e.value for e in GovernanceRiskLevel]
        assert "LOW" in levels
        assert "CRITICAL" in levels


class TestUserRole:
    def test_admin_exists(self) -> None:
        assert UserRole.ADMIN.value == "ADMIN"


class TestMeetingType:
    def test_board_and_shareholder(self) -> None:
        types = {e.value for e in MeetingType}
        assert "BOARD" in types
        assert "SHAREHOLDER" in types
