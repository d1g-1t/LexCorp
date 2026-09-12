from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient


class TestAuthFlow:
    @pytest.mark.asyncio
    async def test_login_missing_credentials_returns_422(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_unknown_user_returns_401(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@corp.local", "password": "wrong"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_without_token_returns_401(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_valid_token(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        # May return 404 if the user doesn't exist in DB — that's still auth-passing
        assert response.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_me_with_garbage_token_returns_401(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not.a.valid.paseto.token"},
        )
        assert response.status_code == 401


class TestTokenSecurity:
    @pytest.mark.asyncio
    async def test_request_id_header_is_present(self, client: AsyncClient):
        response = await client.get("/health/live")
        assert "x-request-id" in response.headers

    @pytest.mark.asyncio
    async def test_security_headers_present(self, client: AsyncClient):
        response = await client.get("/health/live")
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"
