from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.entities.resolution import Resolution
from src.domain.value_objects import ResolutionStatus


class IResolutionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, resolution_id: uuid.UUID) -> Resolution | None: ...

    @abstractmethod
    async def list_by_entity(
        self,
        entity_id: uuid.UUID,
        *,
        status: ResolutionStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Resolution]: ...

    @abstractmethod
    async def save(self, resolution: Resolution) -> Resolution: ...

    @abstractmethod
    async def update(self, resolution: Resolution) -> Resolution: ...
