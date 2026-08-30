import uuid

from sqlalchemy import select

from app.db.models.models import Assessment, Evaluation, MRIReport
from app.db.repositories.base import BaseRepository


class MRIReportRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, MRIReport)

    async def get_by_evaluation_id(
        self, evaluation_id: str | uuid.UUID
    ) -> MRIReport | None:
        evaluation_id = self._coerce_uuid(evaluation_id)
        stmt = select(MRIReport).where(MRIReport.evaluation_id == evaluation_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_student_id(self, student_id: str | uuid.UUID) -> list[MRIReport]:
        student_id = self._coerce_uuid(student_id)
        stmt = (
            select(MRIReport)
            .join(MRIReport.evaluation)
            .join(Evaluation.assessment)
            .where(Assessment.student_id == student_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
