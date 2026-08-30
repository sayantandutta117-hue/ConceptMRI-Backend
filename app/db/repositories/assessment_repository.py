import uuid

from sqlalchemy import select

from app.db.models.models import Assessment
from app.db.repositories.base import BaseRepository


class AssessmentRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, Assessment)

    async def get_by_student_id(self, student_id: str | uuid.UUID) -> list[Assessment]:
        student_id = self._coerce_uuid(student_id)
        stmt = select(Assessment).where(Assessment.student_id == student_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending_by_student_id(
        self, student_id: str | uuid.UUID
    ) -> list[Assessment]:
        student_id = self._coerce_uuid(student_id)
        stmt = select(Assessment).where(
            Assessment.student_id == student_id,
            Assessment.status.in_(
                ["PENDING_EVALUATION", "PROCESSING"]
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_completed_by_student_id(
        self, student_id: str | uuid.UUID
    ) -> list[Assessment]:
        student_id = self._coerce_uuid(student_id)
        stmt = select(Assessment).where(
            Assessment.student_id == student_id,
            Assessment.status == "COMPLETED",
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_student_and_topic(
        self, student_id: str | uuid.UUID, topic_id: str | uuid.UUID
    ) -> Assessment | None:
        student_id = self._coerce_uuid(student_id)
        topic_id = self._coerce_uuid(topic_id)
        stmt = select(Assessment).where(
            Assessment.student_id == student_id,
            Assessment.topic_id == topic_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
