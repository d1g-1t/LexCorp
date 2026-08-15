"""PASETO token service + password hashing utilities.

Uses PASETO v4.local (symmetric, authenticated encryption) instead of JWT
for stronger security guarantees (no algorithm confusion, no "none" attacks).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pyseto
from passlib.context import CryptContext
from pyseto import Key

from src.core.config import Settings

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)


class PasetoService:
    """Thin wrapper around pyseto for v4.local tokens."""

    def __init__(self, settings: Settings) -> None:
        secret = settings.paseto_secret_key.get_secret_value()
        # v4.local requires 32-byte symmetric key
        key_bytes = secret.encode("utf-8")[:32].ljust(32, b"\x00")
        self._key = Key.new(version=4, purpose="local", key=key_bytes)
        self._access_ttl = timedelta(minutes=settings.access_token_ttl_minutes)
        self._refresh_ttl = timedelta(days=settings.refresh_token_ttl_days)

    def create_access_token(self, user_id: uuid.UUID, role: str, tenant_id: uuid.UUID) -> str:
        return self._encode(
            {
                "sub": str(user_id),
                "role": role,
                "tid": str(tenant_id),
                "type": "access",
            },
            self._access_ttl,
        )

    def create_refresh_token(self, user_id: uuid.UUID) -> str:
        return self._encode(
            {"sub": str(user_id), "type": "refresh"},
            self._refresh_ttl,
        )

    def decode(self, token: str) -> dict[str, Any]:
        decoded = pyseto.decode(self._key, token)
        import orjson

        return orjson.loads(decoded.payload)

    # ── private ──────────────────────────────────────

    def _encode(self, claims: dict[str, Any], ttl: timedelta) -> str:
        import orjson

        now = datetime.now(UTC)
        claims["iat"] = now.isoformat()
        claims["exp"] = (now + ttl).isoformat()
        claims["jti"] = str(uuid.uuid4())
        token = pyseto.encode(self._key, orjson.dumps(claims))
        return token.decode("utf-8") if isinstance(token, bytes) else token
