"""Domain exceptions.

Thin, intentional exception hierarchy so application / presentation layers
can map domain violations to the right HTTP status or event.
"""

from __future__ import annotations

import uuid


class DomainError(Exception):
    """Base for all domain-level errors."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class EntityNotFoundError(DomainError):
    def __init__(self, resource: str, resource_id: uuid.UUID) -> None:
        super().__init__(f"{resource} {resource_id} not found")
        self.resource = resource
        self.resource_id = resource_id


class InvalidStateTransitionError(DomainError):
    def __init__(self, resource: str, current: str, target: str) -> None:
        super().__init__(f"{resource}: cannot transition from {current} to {target}")


class QuorumNotMetError(DomainError):
    def __init__(self, required: int, present: int) -> None:
        super().__init__(f"Quorum not met: required={required}, present={present}")


class PoAExpiredError(DomainError):
    def __init__(self, poa_id: uuid.UUID) -> None:
        super().__init__(f"Power of attorney {poa_id} is expired or revoked")


class AuthorizationError(DomainError):
    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(detail)


class DuplicateResourceError(DomainError):
    def __init__(self, resource: str, key: str) -> None:
        super().__init__(f"{resource} with key '{key}' already exists")


class AuditReasonRequiredError(DomainError):
    def __init__(self) -> None:
        super().__init__("Override actions require an audit reason")
