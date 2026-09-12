from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Query
from sqlalchemy import select

from src.application.dto.schemas import (
    CompleteFilingRequest,
    CreateFilingRequest,
    FilingResponse,
)
from src.infrastructure.database.models import FilingEventModel
from src.presentation.deps import AuthUser, DbSession

router = APIRouter(prefix="/filings", tags=["filings"])


@router.post("/", response_model=FilingResponse, status_code=201)
async def create_filing(
    body: CreateFilingRequest,
    session: DbSession,
    user: AuthUser,
) -> FilingResponse:
    filing_id = uuid.uuid4()
    model = FilingEventModel(
        id=filing_id,
        entity_id=body.entity_id,
        obligation_id=body.obligation_id,
        filing_type=body.filing_type,
        deadline_at=body.deadline_at,
        status="PENDING",
        evidence_payload={},
    )
    session.add(model)
    await session.flush()
    return FilingResponse(
        id=filing_id,
        entity_id=body.entity_id,
        obligation_id=body.obligation_id,
        filing_type=body.filing_type,
        filed_at=None,
        deadline_at=body.deadline_at,
        status="PENDING",
        evidence_payload={},
    )


@router.get("/", response_model=list[FilingResponse])
async def list_filings(
    session: DbSession,
    user: AuthUser,
    entity_id: uuid.UUID | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
) -> list[FilingResponse]:
    stmt = select(FilingEventModel)
    if entity_id:
        stmt = stmt.where(FilingEventModel.entity_id == entity_id)
    stmt = stmt.order_by(FilingEventModel.deadline_at).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return [
        FilingResponse(
            id=r.id,
            entity_id=r.entity_id,
            obligation_id=r.obligation_id,
            filing_type=r.filing_type,
            filed_at=r.filed_at,
            deadline_at=r.deadline_at,
            status=r.status,
            evidence_payload=r.evidence_payload,
        )
        for r in result.scalars().all()
    ]


@router.post("/{filing_id}/complete", response_model=FilingResponse)
async def complete_filing(
    filing_id: uuid.UUID,
    body: CompleteFilingRequest,
    session: DbSession,
    user: AuthUser,
) -> FilingResponse:
    result = await session.execute(
        select(FilingEventModel).where(FilingEventModel.id == filing_id)
    )
    row = result.scalar_one()
    row.status = "FILED"
    row.filed_at = datetime.now(UTC)
    row.evidence_payload = body.evidence_payload
    await session.flush()
    return FilingResponse(
        id=row.id,
        entity_id=row.entity_id,
        obligation_id=row.obligation_id,
        filing_type=row.filing_type,
        filed_at=row.filed_at,
        deadline_at=row.deadline_at,
        status=row.status,
        evidence_payload=row.evidence_payload,
    )
