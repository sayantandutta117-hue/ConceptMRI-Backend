from sqlalchemy import select

from app.db.models.models import User
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email, User.status == "ACTIVE")
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_role(self, role: str) -> list[User]:
        stmt = select(User).where(User.role == role)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(User.id).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
