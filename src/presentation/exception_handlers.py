"""Global exception handlers → consistent JSON error responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from src.domain.exceptions import (
    AuthorizationError,
    DomainError,
    DuplicateResourceError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    PoAExpiredError,
    QuorumNotMetError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EntityNotFoundError)
    async def _not_found(_req: Request, exc: EntityNotFoundError) -> ORJSONResponse:
        return ORJSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(InvalidStateTransitionError)
    async def _bad_transition(_req: Request, exc: InvalidStateTransitionError) -> ORJSONResponse:
        return ORJSONResponse(status_code=409, content={"detail": exc.detail})

    @app.exception_handler(QuorumNotMetError)
    async def _quorum(_req: Request, exc: QuorumNotMetError) -> ORJSONResponse:
        return ORJSONResponse(status_code=422, content={"detail": exc.detail})

    @app.exception_handler(PoAExpiredError)
    async def _poa_expired(_req: Request, exc: PoAExpiredError) -> ORJSONResponse:
        return ORJSONResponse(status_code=410, content={"detail": exc.detail})

    @app.exception_handler(AuthorizationError)
    async def _authz(_req: Request, exc: AuthorizationError) -> ORJSONResponse:
        return ORJSONResponse(status_code=403, content={"detail": exc.detail})

    @app.exception_handler(DuplicateResourceError)
    async def _duplicate(_req: Request, exc: DuplicateResourceError) -> ORJSONResponse:
        return ORJSONResponse(status_code=409, content={"detail": exc.detail})

    @app.exception_handler(DomainError)
    async def _domain(_req: Request, exc: DomainError) -> ORJSONResponse:
        return ORJSONResponse(status_code=400, content={"detail": exc.detail})
