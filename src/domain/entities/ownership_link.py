from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal


class OwnershipLink:
    __slots__ = (
        "id",
        "parent_entity_id",
        "child_entity_id",
        "ownership_percent",
        "voting_percent",
        "effective_from",
        "effective_to",
    )

    def __init__(
        self,
        *,
        id: uuid.UUID | None = None,
        parent_entity_id: uuid.UUID,
        child_entity_id: uuid.UUID,
        ownership_percent: Decimal,
        voting_percent: Decimal | None = None,
        effective_from: datetime | None = None,
        effective_to: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.parent_entity_id = parent_entity_id
        self.child_entity_id = child_entity_id
        self.ownership_percent = ownership_percent
        self.voting_percent = voting_percent
        self.effective_from = effective_from or datetime.now(UTC)
        self.effective_to = effective_to

    @property
    def is_current(self) -> bool:
        return self.effective_to is None
