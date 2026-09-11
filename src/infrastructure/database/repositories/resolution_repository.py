from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.resolution import Resolution
from src.domain.repositories.i_resolution_repository import IResolutionRepository
from src.domain.value_objects import ResolutionStatus
from src.infrastructure.database.models import ResolutionModel


def _to_domain(m: ResolutionModel) -> Resolution:
    return Resolution(
        id=m.id,
        entity_id=m.entity_id,
        meeting_id=m.meeting_id,
        resolution_type=m.resolution_type,
        title=m.title,
        text_body=m.text_body,
        status=ResolutionStatus(m.status),
        adopted_at=m.adopted_at,
        effective_at=m.effective_at,
        created_by=m.created_by,
        created_at=m.created_at,
    )


class ResolutionRepository(IResolutionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, resolution_id: uuid.UUID) -> Resolution | None:
        result = await self._session.execute(
            select(ResolutionModel).where(ResolutionModel.id == resolution_id)
        )
        row = result.scalar_one_or_none()
        return _to_domain(row) if row else None

    async def list_by_entity(
        self,
        entity_id: uuid.UUID,
        *,
        status: ResolutionStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Resolution]:
        stmt = select(ResolutionModel).where(ResolutionModel.entity_id == entity_id)
        if status:
            stmt = stmt.where(ResolutionModel.status == status.value)
        stmt = stmt.order_by(ResolutionModel.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        rows: Sequence[ResolutionModel] = result.scalars().all()
        return [_to_domain(r) for r in rows]

    async def save(self, resolution: Resolution) -> Resolution:
        model = ResolutionModel(
            id=resolution.id,
            entity_id=resolution.entity_id,
            meeting_id=resolution.meeting_id,
            resolution_type=resolution.resolution_type,
            title=resolution.title,
            text_body=resolution.text_body,
            status=resolution.status.value,
            adopted_at=resolution.adopted_at,
            effective_at=resolution.effective_at,
            created_by=resolution.created_by,
            created_at=resolution.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return resolution

    async def update(self, resolution: Resolution) -> Resolution:
        result = await self._session.execute(
            select(ResolutionModel).where(ResolutionModel.id == resolution.id)
        )
        row = result.scalar_one()
        row.status = resolution.status.value
        row.adopted_at = resolution.adopted_at
        row.effective_at = resolution.effective_at
        row.text_body = resolution.text_body
        await self._session.flush()
        return resolution
