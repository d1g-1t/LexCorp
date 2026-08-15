"""SQLAlchemy 2 ORM models — the single source of truth that mirrors the SQL schema.

Uses mapped_column / Mapped typing for strict mypy compatibility.
All models share the same DeclarativeBase so Alembic can auto-detect them.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""

    type_annotation_map = {
        dict[str, Any]: JSON,
        list[str]: JSON,
    }


# ── Tenant ──────────────────────────────────────────────────────────────────


class TenantModel(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    users: Mapped[list[ApiUserModel]] = relationship(back_populates="tenant", lazy="selectin")


# ── API User ────────────────────────────────────────────────────────────────


class ApiUserModel(Base):
    __tablename__ = "api_users"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tenant: Mapped[TenantModel] = relationship(back_populates="users", lazy="joined")


# ── Legal Entity ────────────────────────────────────────────────────────────


class LegalEntityModel(Base):
    __tablename__ = "legal_entities"
    __table_args__ = (
        Index("idx_entities_status", "tenant_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
    ogrn: Mapped[str | None] = mapped_column(String(15), nullable=True)
    jurisdiction: Mapped[str] = mapped_column(String(128), nullable=False)
    registration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    parent_entity_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_entities.id"), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships: eagerly loaded to prevent N+1
    officers: Mapped[list[CorporateOfficerModel]] = relationship(back_populates="entity", lazy="selectin", cascade="all, delete-orphan")
    children: Mapped[list[LegalEntityModel]] = relationship(back_populates="parent", lazy="selectin")
    parent: Mapped[LegalEntityModel | None] = relationship(back_populates="children", remote_side="LegalEntityModel.id", lazy="joined")


# ── Corporate Officer ───────────────────────────────────────────────────────


class CorporateOfficerModel(Base):
    __tablename__ = "corporate_officers"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    position_title: Mapped[str] = mapped_column(String(255), nullable=False)
    appointed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ceased_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    authority_scope: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=list)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)

    entity: Mapped[LegalEntityModel] = relationship(back_populates="officers", lazy="joined")


# ── Ownership Link ──────────────────────────────────────────────────────────


class OwnershipLinkModel(Base):
    __tablename__ = "ownership_links"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False)
    child_entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False)
    ownership_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    voting_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ── Board Meeting ───────────────────────────────────────────────────────────


class BoardMeetingModel(Base):
    __tablename__ = "board_meetings"
    __table_args__ = (
        Index("idx_meetings_schedule", "entity_id", "scheduled_at", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False)
    meeting_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    quorum_required: Mapped[int] = mapped_column(Integer, nullable=False)
    quorum_met: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    pack_storage_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("api_users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    agenda_items: Mapped[list[AgendaItemModel]] = relationship(back_populates="meeting", lazy="selectin", cascade="all, delete-orphan")
    resolutions: Mapped[list[ResolutionModel]] = relationship(back_populates="meeting", lazy="selectin")
    minutes: Mapped[list[MeetingMinutesModel]] = relationship(back_populates="meeting", lazy="selectin", cascade="all, delete-orphan")


# ── Agenda Item ─────────────────────────────────────────────────────────────


class AgendaItemModel(Base):
    __tablename__ = "agenda_items"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("board_meetings.id", ondelete="CASCADE"), nullable=False)
    item_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="LOW")
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)

    meeting: Mapped[BoardMeetingModel] = relationship(back_populates="agenda_items", lazy="joined")


# ── Resolution ──────────────────────────────────────────────────────────────


class ResolutionModel(Base):
    __tablename__ = "resolutions"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False)
    meeting_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("board_meetings.id"), nullable=True)
    resolution_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    text_body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    adopted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("api_users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    meeting: Mapped[BoardMeetingModel | None] = relationship(back_populates="resolutions", lazy="joined")


# ── Meeting Minutes ─────────────────────────────────────────────────────────


class MeetingMinutesModel(Base):
    __tablename__ = "meeting_minutes"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("board_meetings.id", ondelete="CASCADE"), nullable=False)
    draft_text: Mapped[str] = mapped_column(Text, nullable=False)
    final_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("api_users.id"), nullable=True)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    meeting: Mapped[BoardMeetingModel] = relationship(back_populates="minutes", lazy="joined")


# ── Action Item ─────────────────────────────────────────────────────────────


class ActionItemModel(Base):
    __tablename__ = "action_items"
    __table_args__ = (
        Index("idx_actions_due", "status", "due_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("board_meetings.id"), nullable=True)
    resolution_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("resolutions.id"), nullable=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("api_users.id"), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ── Power of Attorney ───────────────────────────────────────────────────────


class PowerOfAttorneyModel(Base):
    __tablename__ = "powers_of_attorney"
    __table_args__ = (
        Index("idx_poa_expiry", "status", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False)
    attorney_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope_text: Mapped[str] = mapped_column(Text, nullable=False)
    subdelegation_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)


# ── Compliance Obligation ───────────────────────────────────────────────────


class ComplianceObligationModel(Base):
    __tablename__ = "compliance_obligations"
    __table_args__ = (
        Index("idx_obligations_due", "status", "due_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False)
    obligation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recurrence_rule: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    evidence_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ── Filing Event ────────────────────────────────────────────────────────────


class FilingEventModel(Base):
    __tablename__ = "filing_events"
    __table_args__ = (
        Index("idx_filings_deadline", "status", "deadline_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False)
    obligation_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("compliance_obligations.id"), nullable=True)
    filing_type: Mapped[str] = mapped_column(String(64), nullable=False)
    filed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    evidence_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


# ── Disclosure Event ────────────────────────────────────────────────────────


class DisclosureEventModel(Base):
    __tablename__ = "disclosure_events"
    __table_args__ = (
        Index("idx_disclosures_due", "status", "due_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("legal_entities.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)


# ── AI Analysis Run ─────────────────────────────────────────────────────────


class AiAnalysisRunModel(Base):
    __tablename__ = "ai_analysis_runs"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("legal_entities.id"), nullable=True)
    meeting_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("board_meetings.id"), nullable=True)
    pipeline_type: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(32), nullable=False)
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    output_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# ── Audit Event ─────────────────────────────────────────────────────────────


class AuditEventModel(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        Index("idx_audit_resource", "resource_type", "resource_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("api_users.id"), nullable=True)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
