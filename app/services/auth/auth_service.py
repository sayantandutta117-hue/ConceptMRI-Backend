from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, verify_password
from app.db.models.models import User
from app.db.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.user_repo.get_active_by_email(email)
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def get_user_by_id(self, user_id: str) -> User | None:
        return await self.user_repo.get_by_id(user_id)

    async def create_tokens(self, user: User) -> dict[str, Any]:
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }
