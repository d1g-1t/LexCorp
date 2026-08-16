"""Concrete repository – Board Meeting."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.board_meeting import BoardMeeting
from src.domain.repositories.i_meeting_repository import IMeetingRepository
from src.domain.value_objects import MeetingStatus, MeetingType
from src.infrastructure.database.models import BoardMeetingModel


def _to_domain(m: BoardMeetingModel) -> BoardMeeting:
    return BoardMeeting(
        id=m.id,
        entity_id=m.entity_id,
        meeting_type=MeetingType(m.meeting_type),
        title=m.title,
        scheduled_at=m.scheduled_at,
        status=MeetingStatus(m.status),
        quorum_required=m.quorum_required,
        quorum_met=m.quorum_met,
        pack_storage_path=m.pack_storage_path,
        created_by=m.created_by,
        created_at=m.created_at,
    )


class MeetingRepository(IMeetingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, meeting_id: uuid.UUID) -> BoardMeeting | None:
        result = await self._session.execute(
            select(BoardMeetingModel).where(BoardMeetingModel.id == meeting_id)
        )
        row = result.scalar_one_or_none()
        return _to_domain(row) if row else None

    async def list_by_entity(
        self,
        entity_id: uuid.UUID,
        *,
        status: MeetingStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[BoardMeeting]:
        stmt = select(BoardMeetingModel).where(BoardMeetingModel.entity_id == entity_id)
        if status:
            stmt = stmt.where(BoardMeetingModel.status == status.value)
        stmt = stmt.order_by(BoardMeetingModel.scheduled_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        rows: Sequence[BoardMeetingModel] = result.scalars().all()
        return [_to_domain(r) for r in rows]

    async def list_upcoming(
        self, entity_id: uuid.UUID, *, before: datetime | None = None
    ) -> list[BoardMeeting]:
        now = datetime.now(UTC)
        stmt = (
            select(BoardMeetingModel)
            .where(
                BoardMeetingModel.entity_id == entity_id,
                BoardMeetingModel.scheduled_at >= now,
            )
        )
        if before:
            stmt = stmt.where(BoardMeetingModel.scheduled_at <= before)
        stmt = stmt.order_by(BoardMeetingModel.scheduled_at)
        result = await self._session.execute(stmt)
        return [_to_domain(r) for r in result.scalars().all()]

    async def save(self, meeting: BoardMeeting) -> BoardMeeting:
        model = BoardMeetingModel(
            id=meeting.id,
            entity_id=meeting.entity_id,
            meeting_type=meeting.meeting_type.value,
            title=meeting.title,
            scheduled_at=meeting.scheduled_at,
            status=meeting.status.value,
            quorum_required=meeting.quorum_required,
            quorum_met=meeting.quorum_met,
            pack_storage_path=meeting.pack_storage_path,
            created_by=meeting.created_by,
            created_at=meeting.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return meeting

    async def update(self, meeting: BoardMeeting) -> BoardMeeting:
        result = await self._session.execute(
            select(BoardMeetingModel).where(BoardMeetingModel.id == meeting.id)
        )
        row = result.scalar_one()
        row.status = meeting.status.value
        row.quorum_met = meeting.quorum_met
        row.pack_storage_path = meeting.pack_storage_path
        await self._session.flush()
        return meeting
