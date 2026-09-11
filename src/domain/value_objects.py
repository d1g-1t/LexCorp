from __future__ import annotations

from enum import StrEnum, unique


@unique
class EntityStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LIQUIDATING = "LIQUIDATING"
    LIQUIDATED = "LIQUIDATED"


@unique
class EntityType(StrEnum):
    OOO = "OOO"
    AO = "AO"
    PAO = "PAO"
    IP = "IP"
    BRANCH = "BRANCH"
    REPRESENTATIVE_OFFICE = "REPRESENTATIVE_OFFICE"
    FOREIGN = "FOREIGN"


@unique
class MeetingType(StrEnum):
    BOARD = "BOARD"
    SHAREHOLDER = "SHAREHOLDER"
    SOLE_PARTICIPANT = "SOLE_PARTICIPANT"
    COMMITTEE = "COMMITTEE"


@unique
class MeetingStatus(StrEnum):
    DRAFT = "DRAFT"
    AGENDA_SET = "AGENDA_SET"
    PACK_ASSEMBLED = "PACK_ASSEMBLED"
    CIRCULATED = "CIRCULATED"
    IN_SESSION = "IN_SESSION"
    MINUTES_DRAFT = "MINUTES_DRAFT"
    MINUTES_FINAL = "MINUTES_FINAL"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


@unique
class ResolutionStatus(StrEnum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    ADOPTED = "ADOPTED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


@unique
class ActionItemStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    OVERDUE = "OVERDUE"


@unique
class PoAStatus(StrEnum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    SUSPENDED = "SUSPENDED"


@unique
class ObligationStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    WAIVED = "WAIVED"


@unique
class FilingStatus(StrEnum):
    PENDING = "PENDING"
    FILED = "FILED"
    OVERDUE = "OVERDUE"
    REJECTED = "REJECTED"


@unique
class DisclosureStatus(StrEnum):
    OPEN = "OPEN"
    DISCLOSED = "DISCLOSED"
    OVERDUE = "OVERDUE"


@unique
class GovernanceRiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@unique
class UserRole(StrEnum):
    ADMIN = "ADMIN"
    CORPORATE_SECRETARY = "CORPORATE_SECRETARY"
    LEGAL_COUNSEL = "LEGAL_COUNSEL"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"
    BOARD_MEMBER = "BOARD_MEMBER"
    VIEWER = "VIEWER"


@unique
class AuditEventType(StrEnum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    DELETED = "DELETED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    AI_ANALYSIS_RUN = "AI_ANALYSIS_RUN"
    PACK_ASSEMBLED = "PACK_ASSEMBLED"
    MINUTES_FINALIZED = "MINUTES_FINALIZED"
    POA_ISSUED = "POA_ISSUED"
    POA_REVOKED = "POA_REVOKED"
    FILING_COMPLETED = "FILING_COMPLETED"
    OVERRIDE = "OVERRIDE"
