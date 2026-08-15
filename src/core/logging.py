"""Structured logging via structlog.

Emits JSON in production, pretty-printed key-value in dev.
Integrates request-id propagation for full trace correlation.
"""

from __future__ import annotations

import logging
import sys

import structlog

from src.core.config import Settings


def setup_logging(settings: Settings) -> None:
    """Configure structlog + stdlib bridge."""

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.enable_log_masking:
        shared_processors.append(_mask_sensitive_fields)

    if settings.app_env == "dev":
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    # Silence noisy libraries
    for name in ("uvicorn.access", "sqlalchemy.engine", "httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)


_SENSITIVE_KEYS = frozenset({
    "password", "hashed_password", "secret", "token",
    "paseto_secret_key", "authorization",
})


def _mask_sensitive_fields(
    _logger: structlog.types.WrappedLogger,
    _method: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    for key in _SENSITIVE_KEYS:
        if key in event_dict:
            event_dict[key] = "***"
    return event_dict
