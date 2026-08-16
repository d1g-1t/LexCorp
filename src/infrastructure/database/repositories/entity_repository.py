"""Concrete repository – Legal Entity (PostgreSQL + SQLAlchemy 2 async).

Uses `selectin` eager loading on relationships to prevent N+1 queries.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.legal_entity import LegalEntity
from src.domain.repositories.i_entity_repository import IEntityRepository
from src.domain.value_objects import EntityStatus, EntityType
from src.infrastructure.database.models import LegalEntityModel


def _to_domain(m: LegalEntityModel) -> LegalEntity:
    return LegalEntity(
        id=m.id,
        tenant_id=m.tenant_id,
        legal_name=m.legal_name,
        short_name=m.short_name,
        entity_type=EntityType(m.entity_type),
        inn=m.inn,
        ogrn=m.ogrn,
        jurisdiction=m.jurisdiction,
        registration_date=m.registration_date,
        status=EntityStatus(m.status),
        parent_entity_id=m.parent_entity_id,
        metadata=m.metadata_,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _to_model(e: LegalEntity) -> LegalEntityModel:
    return LegalEntityModel(
        id=e.id,
        tenant_id=e.tenant_id,
        legal_name=e.legal_name,
        short_name=e.short_name,
        entity_type=e.entity_type.value,
        inn=e.inn,
        ogrn=e.ogrn,
        jurisdiction=e.jurisdiction,
        registration_date=e.registration_date,
        status=e.status.value,
        parent_entity_id=e.parent_entity_id,
        metadata_=e.metadata,
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


class EntityRepository(IEntityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: uuid.UUID) -> LegalEntity | None:
        stmt = select(LegalEntityModel).where(LegalEntityModel.id == entity_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return _to_domain(row) if row else None

    async def list_by_tenant(
        self,
        tenant_id: uuid.UUID,
        *,
        status: EntityStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[LegalEntity]:
        stmt = select(LegalEntityModel).where(LegalEntityModel.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(LegalEntityModel.status == status.value)
        stmt = stmt.order_by(LegalEntityModel.legal_name).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        rows: Sequence[LegalEntityModel] = result.scalars().all()
        return [_to_domain(r) for r in rows]

    async def count_by_tenant(
        self, tenant_id: uuid.UUID, *, status: EntityStatus | None = None
    ) -> int:
        stmt = select(func.count()).select_from(LegalEntityModel).where(
            LegalEntityModel.tenant_id == tenant_id
        )
        if status:
            stmt = stmt.where(LegalEntityModel.status == status.value)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def save(self, entity: LegalEntity) -> LegalEntity:
        model = _to_model(entity)
        self._session.add(model)
        await self._session.flush()
        return entity

    async def update(self, entity: LegalEntity) -> LegalEntity:
        stmt = select(LegalEntityModel).where(LegalEntityModel.id == entity.id)
        result = await self._session.execute(stmt)
        row = result.scalar_one()
        row.legal_name = entity.legal_name
        row.short_name = entity.short_name
        row.entity_type = entity.entity_type.value
        row.inn = entity.inn
        row.ogrn = entity.ogrn
        row.jurisdiction = entity.jurisdiction
        row.registration_date = entity.registration_date
        row.status = entity.status.value
        row.parent_entity_id = entity.parent_entity_id
        row.metadata_ = entity.metadata
        row.updated_at = entity.updated_at
        await self._session.flush()
        return entity
