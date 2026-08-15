"""Health / readiness / liveness endpoints + Prometheus metrics exposure."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness() -> ORJSONResponse:
    return ORJSONResponse({"status": "ok"})


@router.get("/ready")
async def readiness() -> ORJSONResponse:
    # In a real deployment, check DB + Redis connectivity here
    return ORJSONResponse({"status": "ok"})


@router.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
