import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import ConfidenceLevel, MasteryLevel
from app.db.models.models import Evaluation
from app.db.repositories.evaluation_repository import EvaluationRepository


class EvaluationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.evaluation_repo = EvaluationRepository(session)

    @staticmethod
    def _coerce_confidence(value: str | float | None) -> str:
        if value is None:
            return ConfidenceLevel.MEDIUM.value
        if isinstance(value, (int, float)):
            if value >= 0.8:
                return ConfidenceLevel.HIGH.value
            if value >= 0.5:
                return ConfidenceLevel.MEDIUM.value
            return ConfidenceLevel.LOW.value
        value = str(value).strip().upper()
        mapping = {item.value: item for item in ConfidenceLevel}
        if value in mapping:
            return mapping[value].value
        if value in ("HIGH", "MEDIUM", "LOW"):
            return value
        return ConfidenceLevel.MEDIUM.value

    async def create_evaluation(
        self,
        assessment_id: str,
        overall_score: int,
        mastery_level: str,
        confidence_level: str | float | None,
        strengths: list[str],
        weaknesses: list[str],
        misconceptions: list[str],
    ) -> Evaluation:
        evaluation = Evaluation(
            assessment_id=uuid.UUID(assessment_id),
            overall_score=overall_score,
            mastery_level=mastery_level,
            confidence_level=self._coerce_confidence(confidence_level),
            strengths=strengths,
            weaknesses=weaknesses,
            misconceptions=misconceptions,
        )
        return await self.evaluation_repo.create(evaluation)

    async def get_evaluation_by_id(self, evaluation_id: str) -> Evaluation | None:
        return await self.evaluation_repo.get_by_id(evaluation_id)
