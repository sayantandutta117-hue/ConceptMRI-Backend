import uuid

from sqlalchemy import select

from app.db.models.models import Class
from app.db.repositories.base import BaseRepository


class ClassRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, Class)

    async def get_by_teacher_id(self, teacher_id: str | uuid.UUID) -> list[Class]:
        teacher_id = self._coerce_uuid(teacher_id)
        stmt = select(Class).where(Class.teacher_id == teacher_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Class | None:
        stmt = select(Class).where(Class.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
