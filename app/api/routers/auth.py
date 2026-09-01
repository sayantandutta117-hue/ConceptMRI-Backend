from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user, get_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.models.models import Student, User
from app.db.models.enums import UserRole, UserStatus
from app.db.repositories.student_repository import StudentRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RefreshTokenRequest, UserRegisterRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _create_tokens(user: User) -> dict[str, Any]:
    return {
        "access_token": create_access_token(subject=str(user.id)),
        "refresh_token": create_refresh_token(subject=str(user.id)),
        "token_type": "bearer",
    }


@router.post("/register", response_model=dict)
async def register(
    payload: UserRegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    repo = UserRepository(session)
    existing = await repo.get_by_email(payload.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    role = payload.role if payload.role in {"student", "teacher", "admin"} else "student"
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name or payload.email.split("@")[0],
        role=UserRole(role),
        status=UserStatus.ACTIVE,
    )
    await repo.create(user)
    await session.flush()

    if user.role == UserRole.STUDENT:
        student_repo = StudentRepository(session)
        student = Student(user_id=user.id)
        await student_repo.create(student)
        await session.flush()

    return {
        "success": True,
        "message": "User registered successfully.",
        "data": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
        },
    }


@router.post("/login", response_model=dict)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    repo = UserRepository(session)
    user = await repo.get_active_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    tokens = _create_tokens(user)
    return {
        "success": True,
        "message": "Login successful.",
        "data": {
            "access_token": tokens["access_token"],
            "token_type": tokens["token_type"],
            "refresh_token": tokens["refresh_token"],
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role.value,
            },
        },
    }


@router.post("/refresh", response_model=dict)
async def refresh_token(
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    try:
        token_data = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = token_data.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or user.status.value != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    tokens = _create_tokens(user)
    return {
        "success": True,
        "message": "Token refreshed successfully.",
        "data": {
            "access_token": tokens["access_token"],
            "token_type": tokens["token_type"],
            "refresh_token": tokens["refresh_token"],
        },
    }


@router.get("/me", response_model=dict)
async def get_me(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict:
    return {
        "success": True,
        "data": {
            "id": current_user["id"],
            "email": current_user["email"],
            "name": current_user["name"],
            "role": current_user["role"],
        },
    }
