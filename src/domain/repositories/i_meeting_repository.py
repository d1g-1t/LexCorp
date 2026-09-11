from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.entities.board_meeting import BoardMeeting
from src.domain.value_objects import MeetingStatus


class IMeetingRepository(ABC):
    @abstractmethod
    async def get_by_id(self, meeting_id: uuid.UUID) -> BoardMeeting | None: ...

    @abstractmethod
    async def list_by_entity(
        self,
        entity_id: uuid.UUID,
        *,
        status: MeetingStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[BoardMeeting]: ...

    @abstractmethod
    async def list_upcoming(
        self, entity_id: uuid.UUID, *, before: datetime | None = None
    ) -> list[BoardMeeting]: ...

    @abstractmethod
    async def save(self, meeting: BoardMeeting) -> BoardMeeting: ...

    @abstractmethod
    async def update(self, meeting: BoardMeeting) -> BoardMeeting: ...
