"""Power of Attorney endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.application.dto.schemas import IssuePoaRequest, PoAResponse
from src.presentation.deps import AuthUser, PoAServiceDep, SettingsDep

router = APIRouter(prefix="/poa", tags=["poa"])


@router.post("/", response_model=PoAResponse, status_code=201)
async def issue_poa(
    body: IssuePoaRequest,
    svc: PoAServiceDep,
    user: AuthUser,
) -> PoAResponse:
    return await svc.issue_poa(body, tenant_id=user.tenant_id, actor_id=user.user_id)


@router.get("/", response_model=list[PoAResponse])
async def list_poa(
    svc: PoAServiceDep,
    user: AuthUser,
    entity_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
) -> list[PoAResponse]:
    return await svc.list_poa(entity_id, status=status, limit=limit, offset=offset)


@router.get("/dashboard/expiring", response_model=list[PoAResponse])
async def expiring_poa(
    svc: PoAServiceDep,
    user: AuthUser,
    settings: SettingsDep,
) -> list[PoAResponse]:
    return await svc.list_expiring(warning_days=settings.poa_expiry_warning_days)


@router.get("/{poa_id}", response_model=PoAResponse)
async def get_poa(poa_id: uuid.UUID, svc: PoAServiceDep, user: AuthUser) -> PoAResponse:
    return await svc.get_poa(poa_id)


@router.post("/{poa_id}/revoke", response_model=PoAResponse)
async def revoke_poa(
    poa_id: uuid.UUID, svc: PoAServiceDep, user: AuthUser
) -> PoAResponse:
    return await svc.revoke_poa(poa_id, tenant_id=user.tenant_id, actor_id=user.user_id)
