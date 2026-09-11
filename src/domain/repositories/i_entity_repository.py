from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.entities.legal_entity import LegalEntity
from src.domain.value_objects import EntityStatus


class IEntityRepository(ABC):
    @abstractmethod
    async def get_by_id(self, entity_id: uuid.UUID) -> LegalEntity | None: ...

    @abstractmethod
    async def list_by_tenant(
        self,
        tenant_id: uuid.UUID,
        *,
        status: EntityStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[LegalEntity]: ...

    @abstractmethod
    async def count_by_tenant(
        self, tenant_id: uuid.UUID, *, status: EntityStatus | None = None
    ) -> int: ...

    @abstractmethod
    async def save(self, entity: LegalEntity) -> LegalEntity: ...

    @abstractmethod
    async def update(self, entity: LegalEntity) -> LegalEntity: ...
