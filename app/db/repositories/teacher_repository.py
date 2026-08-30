import uuid

from sqlalchemy import select

from app.db.models.models import Teacher
from app.db.repositories.base import BaseRepository


class TeacherRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, Teacher)

    async def get_by_user_id(self, user_id: str | uuid.UUID) -> Teacher | None:
        user_id = self._coerce_uuid(user_id)
        stmt = select(Teacher).where(Teacher.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
