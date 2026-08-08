import pytest
from httpx import AsyncClient

from app.db.models.enums import UserRole, UserStatus
from app.db.repositories.user_repository import UserRepository
from app.main import app


class _TestBase:
    pass


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient) -> None:
    payload = {
        "email": "newuser@example.com",
        "password": "StrongPass1!",
        "name": "New User",
        "role": "student",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == payload["email"]
    assert body["data"]["role"] == "student"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "StrongPass1!",
        "name": "First User",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 200

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    payload = {
        "email": "loginuser@example.com",
        "password": "LoginPass1!",
        "name": "Login User",
    }
    register = await client.post("/api/v1/auth/register", json=payload)
    assert register.status_code == 200

    login_payload = {"email": payload["email"], "password": payload["password"]}
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["user"]["email"] == payload["email"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient) -> None:
    payload = {
        "email": "badlogin@example.com",
        "password": "StrongPass1!",
        "name": "Bad Login",
    }
    await client.post("/api/v1/auth/register", json=payload)

    response = await client.post(
        "/api/v1/auth/login", json={"email": payload["email"], "password": "wrong"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_token(client: AsyncClient) -> None:
    payload = {
        "email": "tokenuser@example.com",
        "password": "TokenPass1!",
        "name": "Token User",
    }
    register = await client.post("/api/v1/auth/register", json=payload)
    assert register.status_code == 200

    login = await client.post(
        "/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]}
    )
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["email"] == payload["email"]


@pytest.mark.asyncio
async def test_admin_route_requires_admin(client: AsyncClient) -> None:
    payload = {
        "email": "student_admin_test@example.com",
        "password": "StudentPass1!",
        "name": "Student User",
        "role": "student",
    }
    register = await client.post("/api/v1/auth/register", json=payload)
    assert register.status_code == 200

    login = await client.post(
        "/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]}
    )
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/users/admin/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
