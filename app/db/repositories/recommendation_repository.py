import uuid

from sqlalchemy import select

from app.db.models.models import Recommendation
from app.db.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, Recommendation)

    async def get_by_student_id(
        self, student_id: str | uuid.UUID
    ) -> list[Recommendation]:
        student_id = self._coerce_uuid(student_id)
        stmt = select(Recommendation).where(Recommendation.student_id == student_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_class_id(
        self, class_id: str | uuid.UUID
    ) -> list[Recommendation]:
        class_id = self._coerce_uuid(class_id)
        stmt = select(Recommendation).where(Recommendation.class_id == class_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_evaluation_id(
        self, evaluation_id: str | uuid.UUID
    ) -> list[Recommendation]:
        evaluation_id = self._coerce_uuid(evaluation_id)
        stmt = select(Recommendation).where(
            Recommendation.evaluation_id == evaluation_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
