from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from src.domain.entities.power_of_attorney import PowerOfAttorney
from src.domain.exceptions import PoAExpiredError
from src.domain.value_objects import PoAStatus


@pytest.fixture
def valid_poa() -> PowerOfAttorney:
    return PowerOfAttorney(
        entity_id=uuid.uuid4(),
        attorney_name="Иванов Иван Иванович",
        scope_text="Подписание договоров от имени ООО",
        expires_at=datetime.now(UTC) + timedelta(days=365),
    )


@pytest.fixture
def expired_poa() -> PowerOfAttorney:
    return PowerOfAttorney(
        entity_id=uuid.uuid4(),
        attorney_name="Петров Пётр Петрович",
        scope_text="Представительство в суде",
        expires_at=datetime.now(UTC) - timedelta(days=1),
    )


class TestPowerOfAttorney:
    def test_initial_status_active(self, valid_poa: PowerOfAttorney):
        assert valid_poa.status == PoAStatus.ACTIVE

    def test_is_valid_when_active_and_not_expired(self, valid_poa: PowerOfAttorney):
        assert valid_poa.is_valid is True

    def test_is_not_valid_when_expired(self, expired_poa: PowerOfAttorney):
        assert expired_poa.is_valid is False

    def test_revoke_active(self, valid_poa: PowerOfAttorney):
        valid_poa.revoke()
        assert valid_poa.status == PoAStatus.REVOKED
        assert valid_poa.revoked_at is not None

    def test_revoke_expired_raises(self, expired_poa: PowerOfAttorney):
        with pytest.raises(PoAExpiredError):
            expired_poa.revoke()

    def test_check_expiry_marks_expired(self, expired_poa: PowerOfAttorney):
        expired_poa.check_expiry()
        assert expired_poa.status == PoAStatus.EXPIRED

    def test_check_expiry_no_change_for_valid(self, valid_poa: PowerOfAttorney):
        valid_poa.check_expiry()
        assert valid_poa.status == PoAStatus.ACTIVE

    def test_subdelegation_default_false(self, valid_poa: PowerOfAttorney):
        assert valid_poa.subdelegation_allowed is False

    def test_subdelegation_allowed(self):
        poa = PowerOfAttorney(
            entity_id=uuid.uuid4(),
            attorney_name="Тест",
            scope_text="Тест",
            expires_at=datetime.now(UTC) + timedelta(days=90),
            subdelegation_allowed=True,
        )
        assert poa.subdelegation_allowed is True
