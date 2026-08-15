"""Auth endpoints — login, refresh, me."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from src.application.dto.schemas import LoginRequest, TokenResponse, UserResponse
from src.core.security import PasetoService, verify_password
from src.infrastructure.database.models import ApiUserModel
from src.presentation.deps import AuthUser, DbSession, SettingsDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: DbSession, settings: SettingsDep) -> TokenResponse:
    result = await session.execute(
        select(ApiUserModel).where(ApiUserModel.email == body.email)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")

    paseto = PasetoService(settings)
    return TokenResponse(
        access_token=paseto.create_access_token(user.id, user.role, user.tenant_id),
        refresh_token=paseto.create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: dict,
    session: DbSession,
    settings: SettingsDep,
) -> TokenResponse:
    paseto = PasetoService(settings)
    try:
        payload = paseto.decode(body.get("refresh_token", ""))
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    import uuid

    user_id = uuid.UUID(payload["sub"])
    result = await session.execute(select(ApiUserModel).where(ApiUserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or disabled")

    return TokenResponse(
        access_token=paseto.create_access_token(user.id, user.role, user.tenant_id),
        refresh_token=paseto.create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
async def me(user: AuthUser, session: DbSession) -> UserResponse:
    result = await session.execute(select(ApiUserModel).where(ApiUserModel.id == user.user_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return UserResponse(
        id=row.id,
        tenant_id=row.tenant_id,
        email=row.email,
        role=row.role,
        is_active=row.is_active,
        created_at=row.created_at,
    )
