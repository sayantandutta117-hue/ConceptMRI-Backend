import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import AssessmentStatus
from app.db.models.models import Assessment
from app.db.repositories.assessment_repository import AssessmentRepository


class AssessmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.assessment_repo = AssessmentRepository(session)

    async def create_assessment(
        self, student_id: str, topic_id: str, answer: str
    ) -> Assessment:
        assessment = Assessment(
            student_id=uuid.UUID(student_id),
            topic_id=uuid.UUID(topic_id),
            answer=answer,
            status=AssessmentStatus.PENDING_EVALUATION,
        )
        return await self.assessment_repo.create(assessment)

    async def get_assessment_by_id(self, assessment_id: str) -> Assessment | None:
        return await self.assessment_repo.get_by_id(assessment_id)

    async def get_assessments_by_student_id(self, student_id: str) -> list[Assessment]:
        return await self.assessment_repo.get_by_student_id(student_id)
