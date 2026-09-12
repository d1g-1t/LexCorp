from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from src.core.security import PasetoService, hash_password, verify_password


@pytest.fixture
def mock_settings():
    s = MagicMock()
    s.paseto_secret_key.get_secret_value.return_value = "super-secret-key-exactly-32bytes"
    s.access_token_ttl_minutes = 60
    s.refresh_token_ttl_days = 7
    return s


@pytest.fixture
def paseto(mock_settings) -> PasetoService:
    return PasetoService(settings=mock_settings)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        h = hash_password("my-password")
        assert h != "my-password"

    def test_verify_correct(self):
        h = hash_password("my-password")
        assert verify_password("my-password", h) is True

    def test_verify_wrong(self):
        h = hash_password("my-password")
        assert verify_password("wrong-password", h) is False

    def test_different_hashes_same_input(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        # bcrypt is salted — hashes must differ
        assert h1 != h2


class TestPasetoService:
    def test_create_and_decode_access_token(self, paseto: PasetoService):
        user_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        token = paseto.create_access_token(user_id=user_id, role="admin", tenant_id=tenant_id)

        claims = paseto.decode(token)
        assert claims["sub"] == str(user_id)
        assert claims["role"] == "admin"
        assert claims["type"] == "access"
        assert claims["tid"] == str(tenant_id)

    def test_create_and_decode_refresh_token(self, paseto: PasetoService):
        user_id = uuid.uuid4()
        token = paseto.create_refresh_token(user_id=user_id)

        claims = paseto.decode(token)
        assert claims["sub"] == str(user_id)
        assert claims["type"] == "refresh"

    def test_token_has_expiry(self, paseto: PasetoService):
        token = paseto.create_access_token(
            user_id=uuid.uuid4(), role="admin", tenant_id=uuid.uuid4()
        )
        claims = paseto.decode(token)
        exp = datetime.fromisoformat(claims["exp"])
        assert exp > datetime.now(UTC)

    def test_token_has_jti(self, paseto: PasetoService):
        token = paseto.create_access_token(
            user_id=uuid.uuid4(), role="admin", tenant_id=uuid.uuid4()
        )
        claims = paseto.decode(token)
        assert "jti" in claims
        # jti must be a valid UUID string
        uuid.UUID(claims["jti"])

    def test_tampered_token_raises(self, paseto: PasetoService):
        token = paseto.create_access_token(
            user_id=uuid.uuid4(), role="admin", tenant_id=uuid.uuid4()
        )
        # Corrupt the token
        bad_token = token[:-5] + "ZZZZZ"
        with pytest.raises(Exception):
            paseto.decode(bad_token)

    def test_different_tokens_per_call(self, paseto: PasetoService):
        uid = uuid.uuid4()
        t1 = paseto.create_access_token(user_id=uid, role="admin", tenant_id=uuid.uuid4())
        t2 = paseto.create_access_token(user_id=uid, role="admin", tenant_id=uuid.uuid4())
        assert t1 != t2  # different jti + timestamps
