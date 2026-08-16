"""Analytics endpoints (governance overview, risk, etc.)."""

from __future__ import annotations

from fastapi import APIRouter

from src.application.dto.schemas import GovernanceOverview
from src.presentation.deps import AnalyticsServiceDep, AuthUser

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/governance-overview", response_model=GovernanceOverview)
async def governance_overview(
    svc: AnalyticsServiceDep,
    user: AuthUser,
) -> GovernanceOverview:
    return await svc.governance_overview(user.tenant_id)
