"""Application-layer DTOs (Pydantic v2 models).

These are the contracts between the API layer and application services.
No ORM models or domain entities leak into the presentation layer.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ═══════════════════════════════════════════════════
# Entity DTOs
# ═══════════════════════════════════════════════════


class CreateEntityRequest(BaseModel):
    legal_name: str
    short_name: str | None = None
    entity_type: str
    inn: str | None = None
    ogrn: str | None = None
    jurisdiction: str = "RU"
    registration_date: date | None = None
    parent_entity_id: uuid.UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateEntityRequest(BaseModel):
    legal_name: str | None = None
    short_name: str | None = None
    inn: str | None = None
    ogrn: str | None = None
    jurisdiction: str | None = None
    status: str | None = None
    parent_entity_id: uuid.UUID | None = None
    metadata: dict[str, Any] | None = None


class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    legal_name: str
    short_name: str | None
    entity_type: str
    inn: str | None
    ogrn: str | None
    jurisdiction: str
    registration_date: date | None
    status: str
    parent_entity_id: uuid.UUID | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


# ═══════════════════════════════════════════════════
# Officer DTOs
# ═══════════════════════════════════════════════════


class CreateOfficerRequest(BaseModel):
    full_name: str
    position_title: str
    appointed_at: datetime | None = None
    authority_scope: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OfficerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entity_id: uuid.UUID
    full_name: str
    position_title: str
    appointed_at: datetime
    ceased_at: datetime | None
    authority_scope: list[str]
    metadata: dict[str, Any]


# ═══════════════════════════════════════════════════
# Meeting DTOs
# ═══════════════════════════════════════════════════


class CreateMeetingRequest(BaseModel):
    entity_id: uuid.UUID
    meeting_type: Literal["BOARD", "SHAREHOLDER", "SOLE_PARTICIPANT", "COMMITTEE"]
    title: str
    scheduled_at: datetime
    quorum_required: int


class MeetingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entity_id: uuid.UUID
    meeting_type: str
    title: str
    scheduled_at: datetime
    status: str
    quorum_required: int
    quorum_met: bool | None
    pack_storage_path: str | None
    created_by: uuid.UUID
    created_at: datetime


class CreateAgendaItemRequest(BaseModel):
    item_order: int
    title: str
    description: str | None = None
    risk_level: str = "LOW"
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgendaItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    item_order: int
    title: str
    description: str | None
    risk_level: str
    metadata: dict[str, Any]


class RecordQuorumRequest(BaseModel):
    attendees_count: int


class FinalizeMinutesRequest(BaseModel):
    final_text: str


# ═══════════════════════════════════════════════════
# Resolution DTOs
# ═══════════════════════════════════════════════════


class CreateResolutionRequest(BaseModel):
    entity_id: uuid.UUID
    meeting_id: uuid.UUID | None = None
    resolution_type: str
    title: str
    text_body: str


class ResolutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entity_id: uuid.UUID
    meeting_id: uuid.UUID | None
    resolution_type: str
    title: str
    text_body: str
    status: str
    adopted_at: datetime | None
    effective_at: datetime | None
    created_by: uuid.UUID
    created_at: datetime


# ═══════════════════════════════════════════════════
# PoA DTOs
# ═══════════════════════════════════════════════════


class IssuePoaRequest(BaseModel):
    entity_id: uuid.UUID
    attorney_name: str
    scope_text: str
    subdelegation_allowed: bool = False
    expires_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class PoAResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entity_id: uuid.UUID
    attorney_name: str
    scope_text: str
    subdelegation_allowed: bool
    issued_at: datetime
    expires_at: datetime
    status: str
    revoked_at: datetime | None
    metadata: dict[str, Any]


# ═══════════════════════════════════════════════════
# Compliance / Filing DTOs
# ═══════════════════════════════════════════════════


class CreateObligationRequest(BaseModel):
    entity_id: uuid.UUID
    obligation_type: str
    title: str
    due_at: datetime
    recurrence_rule: str | None = None


class ObligationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entity_id: uuid.UUID
    obligation_type: str
    title: str
    due_at: datetime
    recurrence_rule: str | None
    status: str
    evidence_path: str | None
    created_at: datetime
    completed_at: datetime | None


class CreateFilingRequest(BaseModel):
    entity_id: uuid.UUID
    obligation_id: uuid.UUID | None = None
    filing_type: str
    deadline_at: datetime


class FilingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entity_id: uuid.UUID
    obligation_id: uuid.UUID | None
    filing_type: str
    filed_at: datetime | None
    deadline_at: datetime
    status: str
    evidence_payload: dict[str, Any]


class CompleteFilingRequest(BaseModel):
    evidence_payload: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════
# Analytics DTOs
# ═══════════════════════════════════════════════════


class GovernanceOverview(BaseModel):
    total_entities: int
    active_entities: int
    upcoming_meetings: int
    overdue_obligations: int
    expiring_poa: int
    pending_filings: int
    open_action_items: int


class AuditTimelineEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    resource_type: str
    resource_id: uuid.UUID
    actor_user_id: uuid.UUID | None
    payload: dict[str, Any]
    created_at: datetime


# ═══════════════════════════════════════════════════
# Auth DTOs
# ═══════════════════════════════════════════════════


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime


# ═══════════════════════════════════════════════════
# Pagination
# ═══════════════════════════════════════════════════


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    limit: int
    offset: int
