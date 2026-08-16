"""Domain entity – Power of Attorney."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from src.domain.exceptions import PoAExpiredError
from src.domain.value_objects import PoAStatus


class PowerOfAttorney:
    __slots__ = (
        "id",
        "entity_id",
        "attorney_name",
        "scope_text",
        "subdelegation_allowed",
        "issued_at",
        "expires_at",
        "status",
        "revoked_at",
        "metadata",
    )

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        entity_id: uuid.UUID,
        attorney_name: str,
        scope_text: str,
        subdelegation_allowed: bool = False,
        issued_at: datetime | None = None,
        expires_at: datetime,
        status: PoAStatus = PoAStatus.ACTIVE,
        revoked_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.entity_id = entity_id
        self.attorney_name = attorney_name
        self.scope_text = scope_text
        self.subdelegation_allowed = subdelegation_allowed
        self.issued_at = issued_at or datetime.now(UTC)
        self.expires_at = expires_at
        self.status = status
        self.revoked_at = revoked_at
        self.metadata = metadata or {}

    @property
    def is_valid(self) -> bool:
        return self.status == PoAStatus.ACTIVE and self.expires_at > datetime.now(UTC)

    def revoke(self) -> None:
        if not self.is_valid:
            raise PoAExpiredError(self.id)
        self.status = PoAStatus.REVOKED
        self.revoked_at = datetime.now(UTC)

    def check_expiry(self) -> None:
        """Mark as expired if past expiry date."""
        if self.status == PoAStatus.ACTIVE and self.expires_at <= datetime.now(UTC):
            self.status = PoAStatus.EXPIRED
