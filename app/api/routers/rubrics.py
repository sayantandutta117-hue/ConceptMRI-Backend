import uuid
from typing import Any, Union

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_session
from app.core.exceptions import ValidationError
from app.services.rubric.rubric_service import RubricService

router = APIRouter(prefix="/rubrics", tags=["Rubrics"])


class RubricCreateRequest(BaseModel):
    topic_id: str
    concepts: list[Union[str, dict]] | None = None
    evaluation_rules: list[Union[str, dict]] | None = None
    common_misconceptions: list[Union[str, dict]] | None = None


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _coerce_uuid(value: str) -> uuid.UUID:
    cleaned = value.replace('"', "").replace("'", "").strip().rstrip(",;")
    try:
        return uuid.UUID(cleaned)
    except (ValueError, AttributeError) as exc:
        raise ValidationError(
            message=f"Invalid UUID: {value}",
            details=[{"field": "topic_id", "message": str(exc)}],
        ) from exc


@router.post("", response_model=dict)
async def create_rubric(
    payload: RubricCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = RubricService(session)
    rubric = await service.create_rubric(
        topic_id=payload.topic_id,
        concepts=payload.concepts or [],
        evaluation_rules=payload.evaluation_rules or [],
        common_misconceptions=payload.common_misconceptions or [],
    )
    await session.flush()
    return {
        "success": True,
        "message": "Rubric created successfully.",
        "data": {
            "id": str(rubric.id),
            "topic_id": str(rubric.topic_id),
            "concepts": rubric.concepts,
            "evaluation_rules": rubric.evaluation_rules,
            "common_misconceptions": rubric.common_misconceptions,
            "status": _enum_value(rubric.status),
            "created_at": rubric.created_at.isoformat() if rubric.created_at else None,
        },
    }


@router.get("/{topic_id}", response_model=dict)
async def get_rubrics_by_topic(
    topic_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    cleaned_topic_id = _coerce_uuid(topic_id)
    service = RubricService(session)
    rubrics = await service.get_rubrics_by_topic_id(str(cleaned_topic_id))
    return {
        "success": True,
        "data": [
            {
                "id": str(rubric.id),
                "topic_id": str(rubric.topic_id),
                "concepts": rubric.concepts,
                "evaluation_rules": rubric.evaluation_rules,
                "common_misconceptions": rubric.common_misconceptions,
                "status": _enum_value(rubric.status),
                "created_at": rubric.created_at.isoformat() if rubric.created_at else None,
            }
            for rubric in rubrics
        ],
    }
