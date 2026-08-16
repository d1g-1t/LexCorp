"""Entity management endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.application.dto.schemas import (
    CreateEntityRequest,
    CreateOfficerRequest,
    EntityResponse,
    OfficerResponse,
    UpdateEntityRequest,
)
from src.domain.entities.corporate_officer import CorporateOfficer
from src.infrastructure.database.models import CorporateOfficerModel
from src.presentation.deps import AuthUser, DbSession, EntityServiceDep

router = APIRouter(prefix="/entities", tags=["entities"])


@router.post("/", response_model=EntityResponse, status_code=201)
async def create_entity(
    body: CreateEntityRequest,
    svc: EntityServiceDep,
    user: AuthUser,
) -> EntityResponse:
    return await svc.create_entity(body, tenant_id=user.tenant_id, actor_id=user.user_id)


@router.get("/", response_model=list[EntityResponse])
async def list_entities(
    svc: EntityServiceDep,
    user: AuthUser,
    status: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
) -> list[EntityResponse]:
    return await svc.list_entities(user.tenant_id, status=status, limit=limit, offset=offset)


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: uuid.UUID, svc: EntityServiceDep, user: AuthUser) -> EntityResponse:
    return await svc.get_entity(entity_id)


@router.patch("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: uuid.UUID,
    body: UpdateEntityRequest,
    svc: EntityServiceDep,
    user: AuthUser,
) -> EntityResponse:
    return await svc.update_entity(
        entity_id, body, tenant_id=user.tenant_id, actor_id=user.user_id
    )


@router.post("/{entity_id}/officers", response_model=OfficerResponse, status_code=201)
async def create_officer(
    entity_id: uuid.UUID,
    body: CreateOfficerRequest,
    session: DbSession,
    user: AuthUser,
) -> OfficerResponse:
    officer = CorporateOfficer(
        entity_id=entity_id,
        full_name=body.full_name,
        position_title=body.position_title,
        appointed_at=body.appointed_at,
        authority_scope=body.authority_scope,
        metadata=body.metadata,
    )
    model = CorporateOfficerModel(
        id=officer.id,
        entity_id=officer.entity_id,
        full_name=officer.full_name,
        position_title=officer.position_title,
        appointed_at=officer.appointed_at,
        ceased_at=officer.ceased_at,
        authority_scope=officer.authority_scope,
        metadata_=officer.metadata,
    )
    session.add(model)
    await session.flush()
    return OfficerResponse(
        id=officer.id,
        entity_id=officer.entity_id,
        full_name=officer.full_name,
        position_title=officer.position_title,
        appointed_at=officer.appointed_at,
        ceased_at=officer.ceased_at,
        authority_scope=officer.authority_scope,
        metadata=officer.metadata,
    )


@router.get("/{entity_id}/officers", response_model=list[OfficerResponse])
async def list_officers(
    entity_id: uuid.UUID,
    session: DbSession,
    user: AuthUser,
) -> list[OfficerResponse]:
    from sqlalchemy import select

    result = await session.execute(
        select(CorporateOfficerModel).where(CorporateOfficerModel.entity_id == entity_id)
    )
    return [
        OfficerResponse(
            id=r.id,
            entity_id=r.entity_id,
            full_name=r.full_name,
            position_title=r.position_title,
            appointed_at=r.appointed_at,
            ceased_at=r.ceased_at,
            authority_scope=r.authority_scope or [],
            metadata=r.metadata_ or {},
        )
        for r in result.scalars().all()
    ]
