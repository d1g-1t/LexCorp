"""Resolution endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.application.dto.schemas import CreateResolutionRequest, ResolutionResponse
from src.presentation.deps import AuthUser, ResolutionServiceDep

router = APIRouter(prefix="/resolutions", tags=["resolutions"])


@router.post("/", response_model=ResolutionResponse, status_code=201)
async def create_resolution(
    body: CreateResolutionRequest,
    svc: ResolutionServiceDep,
    user: AuthUser,
) -> ResolutionResponse:
    return await svc.create_resolution(body, tenant_id=user.tenant_id, actor_id=user.user_id)


@router.get("/", response_model=list[ResolutionResponse])
async def list_resolutions(
    svc: ResolutionServiceDep,
    user: AuthUser,
    entity_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
) -> list[ResolutionResponse]:
    return await svc.list_resolutions(entity_id, status=status, limit=limit, offset=offset)


@router.get("/{resolution_id}", response_model=ResolutionResponse)
async def get_resolution(
    resolution_id: uuid.UUID, svc: ResolutionServiceDep, user: AuthUser
) -> ResolutionResponse:
    return await svc.get_resolution(resolution_id)


@router.post("/{resolution_id}/adopt", response_model=ResolutionResponse)
async def adopt_resolution(
    resolution_id: uuid.UUID, svc: ResolutionServiceDep, user: AuthUser
) -> ResolutionResponse:
    return await svc.adopt_resolution(
        resolution_id, tenant_id=user.tenant_id, actor_id=user.user_id
    )
