import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Rubric
from app.db.repositories.rubric_repository import RubricRepository


class RubricService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.rubric_repo = RubricRepository(session)

    async def create_rubric(self, topic_id: str, concepts: list[dict], evaluation_rules: list[dict], common_misconceptions: list[dict]) -> Rubric:
        rubric = Rubric(
            topic_id=uuid.UUID(topic_id),
            concepts=concepts,
            evaluation_rules=evaluation_rules,
            common_misconceptions=common_misconceptions,
            status="ACTIVE",
        )
        return await self.rubric_repo.create(rubric)

    async def get_rubrics_by_topic_id(self, topic_id: str) -> list[Rubric]:
        return await self.rubric_repo.get_by_topic_id(topic_id)
