from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any


class CorporateOfficer:
    __slots__ = (
        "id",
        "entity_id",
        "full_name",
        "position_title",
        "appointed_at",
        "ceased_at",
        "authority_scope",
        "metadata",
    )

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        entity_id: uuid.UUID,
        full_name: str,
        position_title: str,
        appointed_at: datetime | None = None,
        ceased_at: datetime | None = None,
        authority_scope: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.entity_id = entity_id
        self.full_name = full_name
        self.position_title = position_title
        self.appointed_at = appointed_at or datetime.now(UTC)
        self.ceased_at = ceased_at
        self.authority_scope = authority_scope or []
        self.metadata = metadata or {}

    @property
    def is_active(self) -> bool:
        return self.ceased_at is None

    def cease(self) -> None:
        self.ceased_at = datetime.now(UTC)
