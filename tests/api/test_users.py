import pytest
from httpx import AsyncClient

from app.db.models.enums import UserRole


@pytest.mark.asyncio
async def test_admin_list_users_success(client: AsyncClient) -> None:
    admin_payload = {
        "email": "admin_list_test@example.com",
        "password": "AdminPass1!",
        "name": "Admin User",
        "role": "admin",
    }
    register = await client.post("/api/v1/auth/register", json=admin_payload)
    assert register.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_payload["email"], "password": admin_payload["password"]},
    )
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/users/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


@pytest.mark.asyncio
async def test_student_list_users_forbidden(client: AsyncClient) -> None:
    student_payload = {
        "email": "student_list_test@example.com",
        "password": "StudentPass1!",
        "name": "Student User",
        "role": "student",
    }
    register = await client.post("/api/v1/auth/register", json=student_payload)
    assert register.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": student_payload["email"], "password": student_payload["password"]},
    )
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/users/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_get_user_by_id_success(client: AsyncClient) -> None:
    admin_payload = {
        "email": "admin_get_test@example.com",
        "password": "AdminPass1!",
        "name": "Admin User",
        "role": "admin",
    }
    register = await client.post("/api/v1/auth/register", json=admin_payload)
    assert register.status_code == 200
    admin_id = register.json()["data"]["id"]

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_payload["email"], "password": admin_payload["password"]},
    )
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]

    response = await client.get(
        f"/api/v1/users/admin/users/{admin_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == admin_id


@pytest.mark.asyncio
async def test_student_get_user_by_id_forbidden(client: AsyncClient) -> None:
    student_payload = {
        "email": "student_get_test@example.com",
        "password": "StudentPass1!",
        "name": "Student User",
        "role": "student",
    }
    register = await client.post("/api/v1/auth/register", json=student_payload)
    assert register.status_code == 200
    student_id = register.json()["data"]["id"]

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": student_payload["email"], "password": student_payload["password"]},
    )
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]

    response = await client.get(
        f"/api/v1/users/admin/users/{student_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
