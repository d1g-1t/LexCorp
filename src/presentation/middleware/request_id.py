"""Request-ID middleware.

Injects a unique ``X-Request-ID`` header into every request/response
and binds it to structlog context so all downstream log lines carry it.
"""

from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(HEADER) or str(uuid.uuid4())

        # Bind to structlog context for the duration of this request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Store on request state for downstream access
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[HEADER] = request_id
        return response
