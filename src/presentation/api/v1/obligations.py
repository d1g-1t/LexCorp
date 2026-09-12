from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.application.dto.schemas import CreateObligationRequest, ObligationResponse
from src.presentation.deps import AuthUser, ObligationServiceDep, SettingsDep

router = APIRouter(prefix="/obligations", tags=["obligations"])


@router.post("/", response_model=ObligationResponse, status_code=201)
async def create_obligation(
    body: CreateObligationRequest,
    svc: ObligationServiceDep,
    user: AuthUser,
) -> ObligationResponse:
    return await svc.create_obligation(body, tenant_id=user.tenant_id, actor_id=user.user_id)


@router.get("/", response_model=list[ObligationResponse])
async def list_obligations(
    svc: ObligationServiceDep,
    user: AuthUser,
    entity_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
) -> list[ObligationResponse]:
    return await svc.list_obligations(entity_id, status=status, limit=limit, offset=offset)


@router.post("/{obligation_id}/complete", response_model=ObligationResponse)
async def complete_obligation(
    obligation_id: uuid.UUID,
    svc: ObligationServiceDep,
    user: AuthUser,
) -> ObligationResponse:
    return await svc.complete_obligation(
        obligation_id, tenant_id=user.tenant_id, actor_id=user.user_id
    )


@router.get("/dashboard/upcoming", response_model=list[ObligationResponse])
async def upcoming_obligations(
    svc: ObligationServiceDep,
    user: AuthUser,
    settings: SettingsDep,
) -> list[ObligationResponse]:
    return await svc.list_upcoming(warning_days=settings.filing_deadline_warning_days)


@router.get("/dashboard/overdue", response_model=list[ObligationResponse])
async def overdue_obligations(
    svc: ObligationServiceDep,
    user: AuthUser,
) -> list[ObligationResponse]:
    return await svc.list_overdue()
