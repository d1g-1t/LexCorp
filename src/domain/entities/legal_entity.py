from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from typing import Any

from src.domain.exceptions import InvalidStateTransitionError
from src.domain.value_objects import EntityStatus, EntityType

_VALID_TRANSITIONS: dict[EntityStatus, frozenset[EntityStatus]] = {
    EntityStatus.ACTIVE: frozenset({EntityStatus.INACTIVE, EntityStatus.LIQUIDATING}),
    EntityStatus.INACTIVE: frozenset({EntityStatus.ACTIVE, EntityStatus.LIQUIDATING}),
    EntityStatus.LIQUIDATING: frozenset({EntityStatus.LIQUIDATED}),
    EntityStatus.LIQUIDATED: frozenset(),
}


class LegalEntity:
    """Aggregate root for entity management."""

    __slots__ = (
        "id",
        "tenant_id",
        "legal_name",
        "short_name",
        "entity_type",
        "inn",
        "ogrn",
        "jurisdiction",
        "registration_date",
        "status",
        "parent_entity_id",
        "metadata",
        "created_at",
        "updated_at",
    )

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        tenant_id: uuid.UUID,
        legal_name: str,
        short_name: str | None = None,
        entity_type: EntityType,
        inn: str | None = None,
        ogrn: str | None = None,
        jurisdiction: str = "RU",
        registration_date: date | None = None,
        status: EntityStatus = EntityStatus.ACTIVE,
        parent_entity_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.tenant_id = tenant_id
        self.legal_name = legal_name
        self.short_name = short_name
        self.entity_type = entity_type
        self.inn = inn
        self.ogrn = ogrn
        self.jurisdiction = jurisdiction
        self.registration_date = registration_date
        self.status = status
        self.parent_entity_id = parent_entity_id
        self.metadata = metadata or {}
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def change_status(self, target: EntityStatus) -> None:
        allowed = _VALID_TRANSITIONS.get(self.status, frozenset())
        if target not in allowed:
            raise InvalidStateTransitionError("LegalEntity", self.status, target)
        self.status = target
        self.updated_at = datetime.now(UTC)
