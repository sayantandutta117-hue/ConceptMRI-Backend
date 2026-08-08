import uuid

from sqlalchemy import select

from app.db.models.models import Assessment, Evaluation
from app.db.repositories.base import BaseRepository


class EvaluationRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, Evaluation)

    async def get_by_assessment_id(
        self, assessment_id: str | uuid.UUID
    ) -> Evaluation | None:
        assessment_id = self._coerce_uuid(assessment_id)
        stmt = select(Evaluation).where(Evaluation.assessment_id == assessment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_student_id(self, student_id: str | uuid.UUID) -> list[Evaluation]:
        student_id = self._coerce_uuid(student_id)
        stmt = (
            select(Evaluation)
            .join(Evaluation.assessment)
            .where(Assessment.student_id == student_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
