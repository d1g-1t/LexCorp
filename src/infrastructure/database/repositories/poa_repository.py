"""Concrete repository – Power of Attorney."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.power_of_attorney import PowerOfAttorney
from src.domain.repositories.i_poa_repository import IPoARepository
from src.domain.value_objects import PoAStatus
from src.infrastructure.database.models import PowerOfAttorneyModel


def _to_domain(m: PowerOfAttorneyModel) -> PowerOfAttorney:
    return PowerOfAttorney(
        id=m.id,
        entity_id=m.entity_id,
        attorney_name=m.attorney_name,
        scope_text=m.scope_text,
        subdelegation_allowed=m.subdelegation_allowed,
        issued_at=m.issued_at,
        expires_at=m.expires_at,
        status=PoAStatus(m.status),
        revoked_at=m.revoked_at,
        metadata=m.metadata_,
    )


class PoARepository(IPoARepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, poa_id: uuid.UUID) -> PowerOfAttorney | None:
        result = await self._session.execute(
            select(PowerOfAttorneyModel).where(PowerOfAttorneyModel.id == poa_id)
        )
        row = result.scalar_one_or_none()
        return _to_domain(row) if row else None

    async def list_by_entity(
        self,
        entity_id: uuid.UUID,
        *,
        status: PoAStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[PowerOfAttorney]:
        stmt = select(PowerOfAttorneyModel).where(PowerOfAttorneyModel.entity_id == entity_id)
        if status:
            stmt = stmt.where(PowerOfAttorneyModel.status == status.value)
        stmt = stmt.order_by(PowerOfAttorneyModel.expires_at).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        rows: Sequence[PowerOfAttorneyModel] = result.scalars().all()
        return [_to_domain(r) for r in rows]

    async def list_expiring(
        self, *, before: datetime, status: PoAStatus = PoAStatus.ACTIVE
    ) -> list[PowerOfAttorney]:
        stmt = (
            select(PowerOfAttorneyModel)
            .where(
                PowerOfAttorneyModel.status == status.value,
                PowerOfAttorneyModel.expires_at <= before,
            )
            .order_by(PowerOfAttorneyModel.expires_at)
        )
        result = await self._session.execute(stmt)
        return [_to_domain(r) for r in result.scalars().all()]

    async def save(self, poa: PowerOfAttorney) -> PowerOfAttorney:
        model = PowerOfAttorneyModel(
            id=poa.id,
            entity_id=poa.entity_id,
            attorney_name=poa.attorney_name,
            scope_text=poa.scope_text,
            subdelegation_allowed=poa.subdelegation_allowed,
            issued_at=poa.issued_at,
            expires_at=poa.expires_at,
            status=poa.status.value,
            revoked_at=poa.revoked_at,
            metadata_=poa.metadata,
        )
        self._session.add(model)
        await self._session.flush()
        return poa

    async def update(self, poa: PowerOfAttorney) -> PowerOfAttorney:
        result = await self._session.execute(
            select(PowerOfAttorneyModel).where(PowerOfAttorneyModel.id == poa.id)
        )
        row = result.scalar_one()
        row.status = poa.status.value
        row.revoked_at = poa.revoked_at
        await self._session.flush()
        return poa
