import uuid

from sqlalchemy import select

from app.db.models.models import Topic
from app.db.repositories.base import BaseRepository


class TopicRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, Topic)

    async def get_by_subject_and_name(
        self, subject: str, topic_name: str
    ) -> Topic | None:
        stmt = select(Topic).where(
            Topic.subject == subject,
            Topic.topic_name == topic_name,
            Topic.is_archived == False,  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(
        self, subject: str | None = None, difficulty: str | None = None
    ) -> list[Topic]:
        stmt = select(Topic).where(Topic.is_archived == False)  # noqa: E712
        if subject:
            stmt = stmt.where(Topic.subject == subject)
        if difficulty:
            stmt = stmt.where(Topic.difficulty == difficulty)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
