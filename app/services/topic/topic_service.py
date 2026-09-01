import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import Difficulty
from app.db.models.models import Topic
from app.db.repositories.topic_repository import TopicRepository


DIFFICULTY_ALIASES = {
    "beginner": Difficulty.EASY,
    "intermediate": Difficulty.MEDIUM,
    "advanced": Difficulty.HARD,
    "easy": Difficulty.EASY,
    "medium": Difficulty.MEDIUM,
    "hard": Difficulty.HARD,
}


def _normalize_difficulty(value: str) -> Difficulty:
    if isinstance(value, Difficulty):
        return value
    normalized = str(value).strip().lower()
    if normalized in DIFFICULTY_ALIASES:
        return DIFFICULTY_ALIASES[normalized]
    return Difficulty[normalized.upper()]


class TopicService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.topic_repo = TopicRepository(session)

    async def list_topics(
        self,
        page: int = 1,
        limit: int = 20,
        subject: str | None = None,
        difficulty: str | None = None,
    ) -> tuple[list[Any], dict[str, Any]]:
        offset = (page - 1) * limit
        topics = await self.topic_repo.list_active(
            subject=subject, difficulty=difficulty
        )
        total = len(topics)
        paginated = topics[offset : offset + limit]
        pages = (total + limit - 1) // limit if limit > 0 else 0
        pagination = {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages,
        }
        return paginated, pagination

    async def get_topic_by_id(self, topic_id: str) -> Any | None:
        return await self.topic_repo.get_by_id(topic_id)

    async def create_topic(self, payload: dict) -> Topic:
        topic = Topic(
            subject=payload["subject"],
            topic_name=payload["topic_name"],
            difficulty=_normalize_difficulty(payload.get("difficulty", Difficulty.EASY)),
            description=payload.get("description"),
            learning_objectives=payload.get("learning_objectives"),
            prerequisites=payload.get("prerequisites"),
            is_archived=payload.get("is_archived", False),
        )
        return await self.topic_repo.create(topic)

    async def update_topic(self, topic_id: str, payload: dict) -> Topic | None:
        topic = await self.topic_repo.get_by_id(topic_id)
        if topic is None:
            return None
        for key, value in payload.items():
            if value is not None and hasattr(topic, key):
                if key == "difficulty":
                    value = _normalize_difficulty(value)
                setattr(topic, key, value)
        return await self.topic_repo.update(topic)

    async def delete_topic(self, topic_id: str) -> bool:
        return await self.topic_repo.delete(topic_id)
