from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.compliance_obligation import ComplianceObligation
from src.domain.repositories.i_obligation_repository import IObligationRepository
from src.domain.value_objects import ObligationStatus
from src.infrastructure.database.models import ComplianceObligationModel


def _to_domain(m: ComplianceObligationModel) -> ComplianceObligation:
    return ComplianceObligation(
        id=m.id,
        entity_id=m.entity_id,
        obligation_type=m.obligation_type,
        title=m.title,
        due_at=m.due_at,
        recurrence_rule=m.recurrence_rule,
        status=ObligationStatus(m.status),
        evidence_path=m.evidence_path,
        created_at=m.created_at,
        completed_at=m.completed_at,
    )


class ObligationRepository(IObligationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, obligation_id: uuid.UUID) -> ComplianceObligation | None:
        result = await self._session.execute(
            select(ComplianceObligationModel).where(ComplianceObligationModel.id == obligation_id)
        )
        row = result.scalar_one_or_none()
        return _to_domain(row) if row else None

    async def list_by_entity(
        self,
        entity_id: uuid.UUID,
        *,
        status: ObligationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ComplianceObligation]:
        stmt = select(ComplianceObligationModel).where(
            ComplianceObligationModel.entity_id == entity_id
        )
        if status:
            stmt = stmt.where(ComplianceObligationModel.status == status.value)
        stmt = stmt.order_by(ComplianceObligationModel.due_at).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        rows: Sequence[ComplianceObligationModel] = result.scalars().all()
        return [_to_domain(r) for r in rows]

    async def list_upcoming(self, *, before: datetime) -> list[ComplianceObligation]:
        stmt = (
            select(ComplianceObligationModel)
            .where(
                ComplianceObligationModel.status == ObligationStatus.OPEN.value,
                ComplianceObligationModel.due_at <= before,
            )
            .order_by(ComplianceObligationModel.due_at)
        )
        result = await self._session.execute(stmt)
        return [_to_domain(r) for r in result.scalars().all()]

    async def list_overdue(self) -> list[ComplianceObligation]:
        now = datetime.now(UTC)
        stmt = (
            select(ComplianceObligationModel)
            .where(
                ComplianceObligationModel.status == ObligationStatus.OPEN.value,
                ComplianceObligationModel.due_at < now,
            )
            .order_by(ComplianceObligationModel.due_at)
        )
        result = await self._session.execute(stmt)
        return [_to_domain(r) for r in result.scalars().all()]

    async def save(self, obligation: ComplianceObligation) -> ComplianceObligation:
        model = ComplianceObligationModel(
            id=obligation.id,
            entity_id=obligation.entity_id,
            obligation_type=obligation.obligation_type,
            title=obligation.title,
            due_at=obligation.due_at,
            recurrence_rule=obligation.recurrence_rule,
            status=obligation.status.value,
            evidence_path=obligation.evidence_path,
            created_at=obligation.created_at,
            completed_at=obligation.completed_at,
        )
        self._session.add(model)
        await self._session.flush()
        return obligation

    async def update(self, obligation: ComplianceObligation) -> ComplianceObligation:
        result = await self._session.execute(
            select(ComplianceObligationModel).where(
                ComplianceObligationModel.id == obligation.id
            )
        )
        row = result.scalar_one()
        row.status = obligation.status.value
        row.evidence_path = obligation.evidence_path
        row.completed_at = obligation.completed_at
        await self._session.flush()
        return obligation
