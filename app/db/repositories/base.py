import uuid
from typing import Generic, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository:
    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self.session = session
        self.model = model

    async def get_by_id(self, entity_id: str | uuid.UUID) -> ModelType | None:
        entity_id = self._coerce_uuid(entity_id)
        stmt = select(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ModelType]:
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        await self.session.merge(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity_id: str | uuid.UUID) -> bool:
        entity = await self.get_by_id(entity_id)
        if entity is None:
            return False
        await self.session.delete(entity)
        await self.session.flush()
        return True

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    def _coerce_uuid(value: str | uuid.UUID) -> uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        cleaned = str(value).replace('"', "").replace("'", "").strip().rstrip(",;")
        return uuid.UUID(cleaned)
