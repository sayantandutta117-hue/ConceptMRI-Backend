import uuid

from sqlalchemy import select

from app.db.models.models import KnowledgeGraphEdge, KnowledgeGraphNode
from app.db.repositories.base import BaseRepository


class KnowledgeGraphRepository(BaseRepository):
    def __init__(self, session) -> None:
        super().__init__(session, KnowledgeGraphNode)

    async def get_nodes_by_student_id(
        self, student_id: str | uuid.UUID
    ) -> list[KnowledgeGraphNode]:
        student_id = self._coerce_uuid(student_id)
        stmt = select(KnowledgeGraphNode).where(
            KnowledgeGraphNode.student_id == student_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_edges_by_student_id(
        self, student_id: str | uuid.UUID
    ) -> list[KnowledgeGraphEdge]:
        student_id = self._coerce_uuid(student_id)
        stmt = select(KnowledgeGraphEdge).where(
            KnowledgeGraphEdge.student_id == student_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_node_by_concept(
        self, student_id: str | uuid.UUID, concept_id: str
    ) -> KnowledgeGraphNode | None:
        student_id = self._coerce_uuid(student_id)
        stmt = select(KnowledgeGraphNode).where(
            KnowledgeGraphNode.student_id == student_id,
            KnowledgeGraphNode.concept_id == concept_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
