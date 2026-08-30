import uuid

from sqlalchemy import select

from app.db.models.models import Rubric
from app.db.repositories.base import BaseRepository


class RubricRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, Rubric)

    async def get_active_by_topic_id(self, topic_id: str | uuid.UUID) -> Rubric | None:
        topic_id = self._coerce_uuid(topic_id)
        stmt = select(Rubric).where(
            Rubric.topic_id == topic_id, Rubric.status == "ACTIVE"
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_topic_id(self, topic_id: str | uuid.UUID) -> list[Rubric]:
        topic_id = self._coerce_uuid(topic_id)
        stmt = select(Rubric).where(Rubric.topic_id == topic_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_active(self) -> list[Rubric]:
        stmt = select(Rubric).where(Rubric.status == "ACTIVE")
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
