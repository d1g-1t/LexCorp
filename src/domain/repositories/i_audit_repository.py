from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from src.domain.entities.audit_event import AuditEvent


class IAuditRepository(ABC):
    @abstractmethod
    async def save(self, event: AuditEvent) -> AuditEvent: ...

    @abstractmethod
    async def get_timeline(
        self,
        resource_type: str,
        resource_id: uuid.UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEvent]: ...
