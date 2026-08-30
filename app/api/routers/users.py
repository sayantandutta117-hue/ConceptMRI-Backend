from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_admin, get_current_user, get_session
from app.db.models.enums import UserRole
from app.db.repositories.user_repository import UserRepository
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=dict)
async def get_my_profile(
    current_user: dict[str, str] = Depends(get_current_user),
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


@router.patch("/me", response_model=dict)
async def update_my_profile(
    current_user: dict[str, str] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    return {
        "success": True,
        "message": "Profile updated.",
        "data": {
            "id": current_user["id"],
            "email": current_user["email"],
            "name": current_user["name"],
            "role": current_user["role"],
        },
    }


@router.get("/admin/users", response_model=dict)
async def list_all_users(
    current_admin: dict[str, str] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
) -> dict:
    repo = UserRepository(session)
    users = await repo.get_all()
    return {
        "success": True,
        "data": [
            {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role.value,
                "status": user.status.value,
            }
            for user in users
        ],
    }


@router.get("/admin/users/{user_id}", response_model=dict)
async def get_user_by_id(
    user_id: str,
    current_admin: dict[str, str] = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
) -> dict:
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {
        "success": True,
        "data": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "status": user.status.value,
        },
    }
