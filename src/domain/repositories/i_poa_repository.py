from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.entities.power_of_attorney import PowerOfAttorney
from src.domain.value_objects import PoAStatus


class IPoARepository(ABC):
    @abstractmethod
    async def get_by_id(self, poa_id: uuid.UUID) -> PowerOfAttorney | None: ...

    @abstractmethod
    async def list_by_entity(
        self,
        entity_id: uuid.UUID,
        *,
        status: PoAStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[PowerOfAttorney]: ...

    @abstractmethod
    async def list_expiring(
        self, *, before: datetime, status: PoAStatus = PoAStatus.ACTIVE
    ) -> list[PowerOfAttorney]: ...

    @abstractmethod
    async def save(self, poa: PowerOfAttorney) -> PowerOfAttorney: ...

    @abstractmethod
    async def update(self, poa: PowerOfAttorney) -> PowerOfAttorney: ...
