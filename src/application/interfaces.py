"""Application-layer interfaces (ports for external services)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ILLMAssistant(ABC):
    """Port for AI governance assistant."""

    @abstractmethod
    async def summarize_board_pack(self, documents: list[str]) -> str: ...

    @abstractmethod
    async def draft_minutes(self, agenda: str, notes: str) -> str: ...

    @abstractmethod
    async def extract_action_items(self, text: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def check_resolution_text(self, text: str) -> dict[str, Any]: ...

    @abstractmethod
    async def assess_agenda_risk(self, agenda_items: list[str]) -> list[dict[str, Any]]: ...


class INotificationService(ABC):
    """Port for sending notifications (email, telegram, webhooks)."""

    @abstractmethod
    async def send(self, channel: str, recipient: str, subject: str, body: str) -> None: ...
