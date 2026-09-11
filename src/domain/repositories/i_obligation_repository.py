from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.entities.compliance_obligation import ComplianceObligation
from src.domain.value_objects import ObligationStatus


class IObligationRepository(ABC):
    @abstractmethod
    async def get_by_id(self, obligation_id: uuid.UUID) -> ComplianceObligation | None: ...

    @abstractmethod
    async def list_by_entity(
        self,
        entity_id: uuid.UUID,
        *,
        status: ObligationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ComplianceObligation]: ...

    @abstractmethod
    async def list_upcoming(self, *, before: datetime) -> list[ComplianceObligation]: ...

    @abstractmethod
    async def list_overdue(self) -> list[ComplianceObligation]: ...

    @abstractmethod
    async def save(self, obligation: ComplianceObligation) -> ComplianceObligation: ...

    @abstractmethod
    async def update(self, obligation: ComplianceObligation) -> ComplianceObligation: ...
