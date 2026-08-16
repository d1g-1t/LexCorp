"""Meeting management endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query

from src.application.dto.schemas import (
    CreateAgendaItemRequest,
    CreateMeetingRequest,
    AgendaItemResponse,
    FinalizeMinutesRequest,
    MeetingResponse,
    RecordQuorumRequest,
)
from src.infrastructure.database.models import AgendaItemModel, MeetingMinutesModel
from src.presentation.deps import AuthUser, DbSession, MeetingServiceDep

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/", response_model=MeetingResponse, status_code=201)
async def create_meeting(
    body: CreateMeetingRequest,
    svc: MeetingServiceDep,
    user: AuthUser,
) -> MeetingResponse:
    return await svc.create_meeting(body, tenant_id=user.tenant_id, actor_id=user.user_id)


@router.get("/", response_model=list[MeetingResponse])
async def list_meetings(
    svc: MeetingServiceDep,
    user: AuthUser,
    entity_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
) -> list[MeetingResponse]:
    return await svc.list_meetings(entity_id, status=status, limit=limit, offset=offset)


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: uuid.UUID, svc: MeetingServiceDep, user: AuthUser
) -> MeetingResponse:
    return await svc.get_meeting(meeting_id)


@router.post("/{meeting_id}/agenda-items", response_model=AgendaItemResponse, status_code=201)
async def add_agenda_item(
    meeting_id: uuid.UUID,
    body: CreateAgendaItemRequest,
    session: DbSession,
    user: AuthUser,
) -> AgendaItemResponse:
    import uuid as _uuid

    item_id = _uuid.uuid4()
    model = AgendaItemModel(
        id=item_id,
        meeting_id=meeting_id,
        item_order=body.item_order,
        title=body.title,
        description=body.description,
        risk_level=body.risk_level,
        metadata_=body.metadata,
    )
    session.add(model)
    await session.flush()
    return AgendaItemResponse(
        id=item_id,
        meeting_id=meeting_id,
        item_order=body.item_order,
        title=body.title,
        description=body.description,
        risk_level=body.risk_level,
        metadata=body.metadata,
    )


@router.post("/{meeting_id}/assemble-pack", response_model=MeetingResponse)
async def assemble_pack(
    meeting_id: uuid.UUID, svc: MeetingServiceDep, user: AuthUser
) -> MeetingResponse:
    return await svc.advance_meeting(
        meeting_id, "PACK_ASSEMBLED", tenant_id=user.tenant_id, actor_id=user.user_id
    )


@router.post("/{meeting_id}/circulate", response_model=MeetingResponse)
async def circulate(
    meeting_id: uuid.UUID, svc: MeetingServiceDep, user: AuthUser
) -> MeetingResponse:
    return await svc.advance_meeting(
        meeting_id, "CIRCULATED", tenant_id=user.tenant_id, actor_id=user.user_id
    )


@router.post("/{meeting_id}/record-quorum", response_model=MeetingResponse)
async def record_quorum(
    meeting_id: uuid.UUID,
    body: RecordQuorumRequest,
    svc: MeetingServiceDep,
    user: AuthUser,
) -> MeetingResponse:
    return await svc.record_quorum(
        meeting_id, body.attendees_count, tenant_id=user.tenant_id, actor_id=user.user_id
    )


@router.post("/{meeting_id}/finalize-minutes", response_model=MeetingResponse)
async def finalize_minutes(
    meeting_id: uuid.UUID,
    body: FinalizeMinutesRequest,
    session: DbSession,
    svc: MeetingServiceDep,
    user: AuthUser,
) -> MeetingResponse:
    import uuid as _uuid

    minutes_model = MeetingMinutesModel(
        id=_uuid.uuid4(),
        meeting_id=meeting_id,
        draft_text=body.final_text,
        final_text=body.final_text,
        status="MINUTES_FINAL",
        reviewed_by=user.user_id,
    )
    session.add(minutes_model)
    await session.flush()

    return await svc.advance_meeting(
        meeting_id, "MINUTES_FINAL", tenant_id=user.tenant_id, actor_id=user.user_id
    )
