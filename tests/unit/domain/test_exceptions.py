from __future__ import annotations

import uuid

from src.domain.exceptions import (
    AuthorizationError,
    DomainError,
    DuplicateResourceError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    PoAExpiredError,
    QuorumNotMetError,
)


class TestDomainExceptions:
    def test_entity_not_found_is_domain_error(self) -> None:
        rid = uuid.uuid4()
        err = EntityNotFoundError("legal_entity", rid)
        assert isinstance(err, DomainError)
        assert str(rid) in str(err)

    def test_invalid_state_transition_message(self) -> None:
        err = InvalidStateTransitionError("Meeting", "DRAFT", "CLOSED")
        assert "DRAFT" in str(err)
        assert "CLOSED" in str(err)

    def test_quorum_not_met(self) -> None:
        err = QuorumNotMetError(required=5, present=3)
        assert isinstance(err, DomainError)

    def test_poa_expired(self) -> None:
        poa_id = uuid.uuid4()
        err = PoAExpiredError(poa_id)
        assert str(poa_id) in str(err)

    def test_authorization_error(self) -> None:
        err = AuthorizationError("not allowed")
        assert isinstance(err, DomainError)

    def test_duplicate_resource(self) -> None:
        err = DuplicateResourceError("entity", "1234567890")
        assert isinstance(err, DomainError)
        assert "1234567890" in str(err)
