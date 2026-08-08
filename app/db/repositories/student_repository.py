import uuid

from sqlalchemy import select

from app.db.models.models import Student
from app.db.repositories.base import BaseRepository


class StudentRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, Student)

    async def get_by_user_id(self, user_id: str | uuid.UUID) -> Student | None:
        user_id = self._coerce_uuid(user_id)
        stmt = select(Student).where(Student.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_class_id(self, class_id: str | uuid.UUID) -> list[Student]:
        class_id = self._coerce_uuid(class_id)
        stmt = select(Student).where(Student.class_id == class_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_user(self, student_id: str | uuid.UUID) -> Student | None:
        student_id = self._coerce_uuid(student_id)
        stmt = select(Student).where(Student.id == student_id)
        result = await self.session.execute(stmt)
        student = result.scalar_one_or_none()
        if student and not hasattr(student, "user"):
            await self.session.refresh(student, attribute_names=["user"])
        return student
