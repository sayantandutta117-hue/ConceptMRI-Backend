from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_session
from app.schemas.topic import TopicCreateRequest, TopicUpdateRequest
from app.services.topic.topic_service import TopicService

router = APIRouter(prefix="/topics", tags=["Topics"])


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _topic_response(topic: Any) -> dict:
    return {
        "id": str(topic.id),
        "subject": topic.subject,
        "topic_name": topic.topic_name,
        "difficulty": _enum_value(topic.difficulty),
        "description": topic.description,
        "learning_objectives": topic.learning_objectives,
        "prerequisites": topic.prerequisites,
        "is_archived": topic.is_archived,
        "created_at": topic.created_at.isoformat() if topic.created_at else None,
        "updated_at": topic.updated_at.isoformat() if topic.updated_at else None,
    }


@router.get("", response_model=dict)
async def list_topics(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    subject: str | None = Query(None),
    difficulty: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = TopicService(session)
    topics, pagination = await service.list_topics(
        page=page, limit=limit, subject=subject, difficulty=difficulty
    )
    return {
        "success": True,
        "data": [_topic_response(topic) for topic in topics],
        "pagination": pagination,
    }


@router.get("/{topic_id}", response_model=dict)
async def get_topic(
    topic_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = TopicService(session)
    topic = await service.get_topic_by_id(topic_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )
    return {
        "success": True,
        "data": _topic_response(topic),
    }


@router.post("", response_model=dict)
async def create_topic(
    payload: TopicCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = TopicService(session)
    topic = await service.create_topic(payload.model_dump())
    await session.flush()
    return {
        "success": True,
        "message": "Topic created successfully.",
        "data": _topic_response(topic),
    }


@router.patch("/{topic_id}", response_model=dict)
async def update_topic(
    topic_id: str,
    payload: TopicUpdateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = TopicService(session)
    topic = await service.update_topic(topic_id, payload.model_dump(exclude_none=True))
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )
    await session.flush()
    return {
        "success": True,
        "message": "Topic updated successfully.",
        "data": _topic_response(topic),
    }


@router.delete("/{topic_id}", response_model=dict)
async def delete_topic(
    topic_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = TopicService(session)
    deleted = await service.delete_topic(topic_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )
    await session.flush()
    return {
        "success": True,
        "message": "Topic deleted successfully.",
    }
