"""Rate-limiting middleware using slowapi.

Applies per-IP throttling to protect the API from abuse.
Limits are configurable via environment variables.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

# Default: 120 requests per minute per IP (generous for internal use)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
    storage_uri=None,  # will be set to Redis URI in main.py
    strategy="fixed-window",
)
