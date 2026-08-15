"""Application services (use cases) — orchestrate domain logic + repos + audit events.

Each service method represents a single business transaction.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from src.application.dto.schemas import (
    CreateEntityRequest,
    CreateMeetingRequest,
    CreateObligationRequest,
    CreateResolutionRequest,
    EntityResponse,
    GovernanceOverview,
    IssuePoaRequest,
    MeetingResponse,
    ObligationResponse,
    PoAResponse,
    ResolutionResponse,
    UpdateEntityRequest,
)
from src.domain.entities.audit_event import AuditEvent
from src.domain.entities.board_meeting import BoardMeeting
from src.domain.entities.compliance_obligation import ComplianceObligation
from src.domain.entities.legal_entity import LegalEntity
from src.domain.entities.power_of_attorney import PowerOfAttorney
from src.domain.entities.resolution import Resolution
from src.domain.exceptions import EntityNotFoundError
from src.domain.repositories.i_audit_repository import IAuditRepository
from src.domain.repositories.i_entity_repository import IEntityRepository
from src.domain.repositories.i_meeting_repository import IMeetingRepository
from src.domain.repositories.i_obligation_repository import IObligationRepository
from src.domain.repositories.i_poa_repository import IPoARepository
from src.domain.repositories.i_resolution_repository import IResolutionRepository
from src.domain.value_objects import (
    AuditEventType,
    EntityStatus,
    EntityType,
    MeetingStatus,
    MeetingType,
    ResolutionStatus,
)

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════
# Entity Service
# ═══════════════════════════════════════════════════════════════


class EntityService:
    def __init__(
        self,
        entity_repo: IEntityRepository,
        audit_repo: IAuditRepository,
    ) -> None:
        self._entity_repo = entity_repo
        self._audit_repo = audit_repo

    async def create_entity(
        self,
        req: CreateEntityRequest,
        *,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> EntityResponse:
        entity = LegalEntity(
            tenant_id=tenant_id,
            legal_name=req.legal_name,
            short_name=req.short_name,
            entity_type=EntityType(req.entity_type),
            inn=req.inn,
            ogrn=req.ogrn,
            jurisdiction=req.jurisdiction,
            registration_date=req.registration_date,
            parent_entity_id=req.parent_entity_id,
            metadata=req.metadata,
        )
        saved = await self._entity_repo.save(entity)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="legal_entity",
                resource_id=saved.id,
                event_type=AuditEventType.CREATED,
                payload={"legal_name": saved.legal_name},
            )
        )

        logger.info("entity_created", entity_id=str(saved.id), name=saved.legal_name)
        return _entity_to_response(saved)

    async def get_entity(self, entity_id: uuid.UUID) -> EntityResponse:
        entity = await self._entity_repo.get_by_id(entity_id)
        if not entity:
            raise EntityNotFoundError("LegalEntity", entity_id)
        return _entity_to_response(entity)

    async def list_entities(
        self,
        tenant_id: uuid.UUID,
        *,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[EntityResponse]:
        st = EntityStatus(status) if status else None
        entities = await self._entity_repo.list_by_tenant(
            tenant_id, status=st, limit=limit, offset=offset
        )
        return [_entity_to_response(e) for e in entities]

    async def update_entity(
        self,
        entity_id: uuid.UUID,
        req: UpdateEntityRequest,
        *,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> EntityResponse:
        entity = await self._entity_repo.get_by_id(entity_id)
        if not entity:
            raise EntityNotFoundError("LegalEntity", entity_id)

        if req.legal_name is not None:
            entity.legal_name = req.legal_name
        if req.short_name is not None:
            entity.short_name = req.short_name
        if req.inn is not None:
            entity.inn = req.inn
        if req.ogrn is not None:
            entity.ogrn = req.ogrn
        if req.jurisdiction is not None:
            entity.jurisdiction = req.jurisdiction
        if req.status is not None:
            entity.change_status(EntityStatus(req.status))
        if req.parent_entity_id is not None:
            entity.parent_entity_id = req.parent_entity_id
        if req.metadata is not None:
            entity.metadata = req.metadata
        entity.updated_at = datetime.now(UTC)

        updated = await self._entity_repo.update(entity)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="legal_entity",
                resource_id=updated.id,
                event_type=AuditEventType.UPDATED,
                payload=req.model_dump(exclude_none=True),
            )
        )
        return _entity_to_response(updated)


def _entity_to_response(e: LegalEntity) -> EntityResponse:
    return EntityResponse(
        id=e.id,
        tenant_id=e.tenant_id,
        legal_name=e.legal_name,
        short_name=e.short_name,
        entity_type=e.entity_type.value,
        inn=e.inn,
        ogrn=e.ogrn,
        jurisdiction=e.jurisdiction,
        registration_date=e.registration_date,
        status=e.status.value,
        parent_entity_id=e.parent_entity_id,
        metadata=e.metadata,
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


# ═══════════════════════════════════════════════════════════════
# Meeting Service
# ═══════════════════════════════════════════════════════════════


class MeetingService:
    def __init__(
        self,
        meeting_repo: IMeetingRepository,
        audit_repo: IAuditRepository,
    ) -> None:
        self._meeting_repo = meeting_repo
        self._audit_repo = audit_repo

    async def create_meeting(
        self,
        req: CreateMeetingRequest,
        *,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> MeetingResponse:
        meeting = BoardMeeting(
            entity_id=req.entity_id,
            meeting_type=MeetingType(req.meeting_type),
            title=req.title,
            scheduled_at=req.scheduled_at,
            quorum_required=req.quorum_required,
            created_by=actor_id,
        )
        saved = await self._meeting_repo.save(meeting)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="board_meeting",
                resource_id=saved.id,
                event_type=AuditEventType.CREATED,
                payload={"title": saved.title},
            )
        )
        return _meeting_to_response(saved)

    async def get_meeting(self, meeting_id: uuid.UUID) -> MeetingResponse:
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise EntityNotFoundError("BoardMeeting", meeting_id)
        return _meeting_to_response(meeting)

    async def list_meetings(
        self,
        entity_id: uuid.UUID | None = None,
        *,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MeetingResponse]:
        if not entity_id:
            return []
        st = MeetingStatus(status) if status else None
        meetings = await self._meeting_repo.list_by_entity(
            entity_id, status=st, limit=limit, offset=offset
        )
        return [_meeting_to_response(m) for m in meetings]

    async def advance_meeting(
        self,
        meeting_id: uuid.UUID,
        target_status: str,
        *,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> MeetingResponse:
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise EntityNotFoundError("BoardMeeting", meeting_id)
        target = MeetingStatus(target_status)
        meeting.advance(target)
        updated = await self._meeting_repo.update(meeting)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="board_meeting",
                resource_id=updated.id,
                event_type=AuditEventType.STATUS_CHANGED,
                payload={"new_status": target_status},
            )
        )
        return _meeting_to_response(updated)

    async def record_quorum(
        self,
        meeting_id: uuid.UUID,
        attendees_count: int,
        *,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> MeetingResponse:
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise EntityNotFoundError("BoardMeeting", meeting_id)
        meeting.record_quorum(attendees_count)
        updated = await self._meeting_repo.update(meeting)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="board_meeting",
                resource_id=updated.id,
                event_type=AuditEventType.APPROVED,
                payload={"attendees": attendees_count, "quorum_met": meeting.quorum_met},
            )
        )
        return _meeting_to_response(updated)


def _meeting_to_response(m: BoardMeeting) -> MeetingResponse:
    return MeetingResponse(
        id=m.id,
        entity_id=m.entity_id,
        meeting_type=m.meeting_type.value,
        title=m.title,
        scheduled_at=m.scheduled_at,
        status=m.status.value,
        quorum_required=m.quorum_required,
        quorum_met=m.quorum_met,
        pack_storage_path=m.pack_storage_path,
        created_by=m.created_by,
        created_at=m.created_at,
    )


# ═══════════════════════════════════════════════════════════════
# Resolution Service
# ═══════════════════════════════════════════════════════════════


class ResolutionService:
    def __init__(
        self,
        resolution_repo: IResolutionRepository,
        audit_repo: IAuditRepository,
    ) -> None:
        self._resolution_repo = resolution_repo
        self._audit_repo = audit_repo

    async def create_resolution(
        self,
        req: CreateResolutionRequest,
        *,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> ResolutionResponse:
        resolution = Resolution(
            entity_id=req.entity_id,
            meeting_id=req.meeting_id,
            resolution_type=req.resolution_type,
            title=req.title,
            text_body=req.text_body,
            created_by=actor_id,
        )
        saved = await self._resolution_repo.save(resolution)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="resolution",
                resource_id=saved.id,
                event_type=AuditEventType.CREATED,
                payload={"title": saved.title},
            )
        )
        return _resolution_to_response(saved)

    async def get_resolution(self, resolution_id: uuid.UUID) -> ResolutionResponse:
        resolution = await self._resolution_repo.get_by_id(resolution_id)
        if not resolution:
            raise EntityNotFoundError("Resolution", resolution_id)
        return _resolution_to_response(resolution)

    async def list_resolutions(
        self,
        entity_id: uuid.UUID | None = None,
        *,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ResolutionResponse]:
        if not entity_id:
            return []
        st = ResolutionStatus(status) if status else None
        resolutions = await self._resolution_repo.list_by_entity(
            entity_id, status=st, limit=limit, offset=offset
        )
        return [_resolution_to_response(r) for r in resolutions]

    async def adopt_resolution(
        self,
        resolution_id: uuid.UUID,
        *,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> ResolutionResponse:
        resolution = await self._resolution_repo.get_by_id(resolution_id)
        if not resolution:
            raise EntityNotFoundError("Resolution", resolution_id)
        resolution.advance(ResolutionStatus.PROPOSED)
        resolution.advance(ResolutionStatus.ADOPTED)
        updated = await self._resolution_repo.update(resolution)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="resolution",
                resource_id=updated.id,
                event_type=AuditEventType.APPROVED,
                payload={"status": "ADOPTED"},
            )
        )
        return _resolution_to_response(updated)


def _resolution_to_response(r: Resolution) -> ResolutionResponse:
    return ResolutionResponse(
        id=r.id,
        entity_id=r.entity_id,
        meeting_id=r.meeting_id,
        resolution_type=r.resolution_type,
        title=r.title,
        text_body=r.text_body,
        status=r.status.value,
        adopted_at=r.adopted_at,
        effective_at=r.effective_at,
        created_by=r.created_by,
        created_at=r.created_at,
    )


# ═══════════════════════════════════════════════════════════════
# PoA Service
# ═══════════════════════════════════════════════════════════════


class PoAService:
    def __init__(
        self,
        poa_repo: IPoARepository,
        audit_repo: IAuditRepository,
    ) -> None:
        self._poa_repo = poa_repo
        self._audit_repo = audit_repo

    async def issue_poa(
        self,
        req: IssuePoaRequest,
        *,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> PoAResponse:
        poa = PowerOfAttorney(
            entity_id=req.entity_id,
            attorney_name=req.attorney_name,
            scope_text=req.scope_text,
            subdelegation_allowed=req.subdelegation_allowed,
            expires_at=req.expires_at,
            metadata=req.metadata,
        )
        saved = await self._poa_repo.save(poa)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="power_of_attorney",
                resource_id=saved.id,
                event_type=AuditEventType.POA_ISSUED,
                payload={"attorney_name": saved.attorney_name},
            )
        )
        return _poa_to_response(saved)

    async def get_poa(self, poa_id: uuid.UUID) -> PoAResponse:
        poa = await self._poa_repo.get_by_id(poa_id)
        if not poa:
            raise EntityNotFoundError("PowerOfAttorney", poa_id)
        return _poa_to_response(poa)

    async def list_poa(
        self,
        entity_id: uuid.UUID | None = None,
        *,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[PoAResponse]:
        if not entity_id:
            return []
        from src.domain.value_objects import PoAStatus

        st = PoAStatus(status) if status else None
        poas = await self._poa_repo.list_by_entity(entity_id, status=st, limit=limit, offset=offset)
        return [_poa_to_response(p) for p in poas]

    async def revoke_poa(
        self,
        poa_id: uuid.UUID,
        *,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> PoAResponse:
        poa = await self._poa_repo.get_by_id(poa_id)
        if not poa:
            raise EntityNotFoundError("PowerOfAttorney", poa_id)
        poa.revoke()
        updated = await self._poa_repo.update(poa)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="power_of_attorney",
                resource_id=updated.id,
                event_type=AuditEventType.POA_REVOKED,
                payload={"attorney_name": updated.attorney_name},
            )
        )
        return _poa_to_response(updated)

    async def list_expiring(
        self, *, warning_days: int = 30
    ) -> list[PoAResponse]:
        from datetime import timedelta

        before = datetime.now(UTC) + timedelta(days=warning_days)
        poas = await self._poa_repo.list_expiring(before=before)
        return [_poa_to_response(p) for p in poas]


def _poa_to_response(p: PowerOfAttorney) -> PoAResponse:
    return PoAResponse(
        id=p.id,
        entity_id=p.entity_id,
        attorney_name=p.attorney_name,
        scope_text=p.scope_text,
        subdelegation_allowed=p.subdelegation_allowed,
        issued_at=p.issued_at,
        expires_at=p.expires_at,
        status=p.status.value,
        revoked_at=p.revoked_at,
        metadata=p.metadata,
    )


# ═══════════════════════════════════════════════════════════════
# Obligation Service
# ═══════════════════════════════════════════════════════════════


class ObligationService:
    def __init__(
        self,
        obligation_repo: IObligationRepository,
        audit_repo: IAuditRepository,
    ) -> None:
        self._obligation_repo = obligation_repo
        self._audit_repo = audit_repo

    async def create_obligation(
        self,
        req: CreateObligationRequest,
        *,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> ObligationResponse:
        obligation = ComplianceObligation(
            entity_id=req.entity_id,
            obligation_type=req.obligation_type,
            title=req.title,
            due_at=req.due_at,
            recurrence_rule=req.recurrence_rule,
        )
        saved = await self._obligation_repo.save(obligation)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="compliance_obligation",
                resource_id=saved.id,
                event_type=AuditEventType.CREATED,
                payload={"title": saved.title},
            )
        )
        return _obligation_to_response(saved)

    async def list_obligations(
        self,
        entity_id: uuid.UUID | None = None,
        *,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ObligationResponse]:
        if not entity_id:
            return []
        from src.domain.value_objects import ObligationStatus

        st = ObligationStatus(status) if status else None
        obligations = await self._obligation_repo.list_by_entity(
            entity_id, status=st, limit=limit, offset=offset
        )
        return [_obligation_to_response(o) for o in obligations]

    async def complete_obligation(
        self,
        obligation_id: uuid.UUID,
        *,
        evidence_path: str | None = None,
        tenant_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> ObligationResponse:
        obligation = await self._obligation_repo.get_by_id(obligation_id)
        if not obligation:
            raise EntityNotFoundError("ComplianceObligation", obligation_id)
        obligation.complete(evidence_path)
        updated = await self._obligation_repo.update(obligation)

        await self._audit_repo.save(
            AuditEvent(
                tenant_id=tenant_id,
                actor_user_id=actor_id,
                resource_type="compliance_obligation",
                resource_id=updated.id,
                event_type=AuditEventType.FILING_COMPLETED,
                payload={"evidence_path": evidence_path},
            )
        )
        return _obligation_to_response(updated)

    async def list_overdue(self) -> list[ObligationResponse]:
        obligations = await self._obligation_repo.list_overdue()
        return [_obligation_to_response(o) for o in obligations]

    async def list_upcoming(self, *, warning_days: int = 14) -> list[ObligationResponse]:
        from datetime import timedelta

        before = datetime.now(UTC) + timedelta(days=warning_days)
        obligations = await self._obligation_repo.list_upcoming(before=before)
        return [_obligation_to_response(o) for o in obligations]


def _obligation_to_response(o: ComplianceObligation) -> ObligationResponse:
    return ObligationResponse(
        id=o.id,
        entity_id=o.entity_id,
        obligation_type=o.obligation_type,
        title=o.title,
        due_at=o.due_at,
        recurrence_rule=o.recurrence_rule,
        status=o.status.value,
        evidence_path=o.evidence_path,
        created_at=o.created_at,
        completed_at=o.completed_at,
    )


# ═══════════════════════════════════════════════════════════════
# Analytics Service (cached via Redis)
# ═══════════════════════════════════════════════════════════════


class AnalyticsService:
    def __init__(
        self,
        entity_repo: IEntityRepository,
        meeting_repo: IMeetingRepository,
        obligation_repo: IObligationRepository,
        poa_repo: IPoARepository,
    ) -> None:
        self._entity_repo = entity_repo
        self._meeting_repo = meeting_repo
        self._obligation_repo = obligation_repo
        self._poa_repo = poa_repo

    async def governance_overview(self, tenant_id: uuid.UUID) -> GovernanceOverview:
        total = await self._entity_repo.count_by_tenant(tenant_id)
        active = await self._entity_repo.count_by_tenant(tenant_id, status=EntityStatus.ACTIVE)
        overdue = await self._obligation_repo.list_overdue()

        from datetime import timedelta

        before_poa = datetime.now(UTC) + timedelta(days=30)
        expiring = await self._poa_repo.list_expiring(before=before_poa)

        return GovernanceOverview(
            total_entities=total,
            active_entities=active,
            upcoming_meetings=0,  # simplified for now
            overdue_obligations=len(overdue),
            expiring_poa=len(expiring),
            pending_filings=0,
            open_action_items=0,
        )
