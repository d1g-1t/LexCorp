"""Domain service – Authority validation for PoA and delegated authority."""

from __future__ import annotations

from datetime import UTC, datetime

from src.domain.entities.power_of_attorney import PowerOfAttorney
from src.domain.exceptions import PoAExpiredError
from src.domain.value_objects import PoAStatus


class AuthorityValidationService:
    """Validates that a power of attorney is valid for the requested scope."""

    @staticmethod
    def validate_poa(poa: PowerOfAttorney, required_scope: str | None = None) -> bool:
        if poa.status != PoAStatus.ACTIVE:
            raise PoAExpiredError(poa.id)
        if poa.expires_at <= datetime.now(UTC):
            raise PoAExpiredError(poa.id)
        if required_scope and required_scope not in poa.scope_text:
            return False
        return True
