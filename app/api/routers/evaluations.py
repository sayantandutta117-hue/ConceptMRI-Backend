from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_session
from app.schemas.evaluation import EvaluationCreateRequest, EvaluationResponse
from app.services.evaluation.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


def _evaluation_response(evaluation: Any) -> dict:
    return {
        "id": str(evaluation.id),
        "assessment_id": str(evaluation.assessment_id),
        "overall_score": evaluation.overall_score,
        "mastery_level": evaluation.mastery_level.value if hasattr(evaluation.mastery_level, "value") else evaluation.mastery_level,
        "confidence_level": evaluation.confidence_level.value if hasattr(evaluation.confidence_level, "value") else evaluation.confidence_level,
        "strengths": evaluation.strengths,
        "weaknesses": evaluation.weaknesses,
        "misconceptions": evaluation.misconceptions,
        "created_at": evaluation.created_at.isoformat() if evaluation.created_at else None,
    }


@router.post("", response_model=dict)
async def create_evaluation(
    payload: EvaluationCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    overall_score = payload.overall_score if payload.overall_score is not None else 0
    confidence_level = (
        str(payload.confidence_level)
        if payload.confidence_level is not None
        else "MEDIUM"
    )
    strengths = payload.strengths or []
    weaknesses = payload.weaknesses or []
    misconceptions = payload.misconceptions or []

    service = EvaluationService(session)
    evaluation = await service.create_evaluation(
        assessment_id=payload.assessment_id,
        overall_score=overall_score,
        mastery_level=payload.mastery_level,
        confidence_level=confidence_level,
        strengths=strengths,
        weaknesses=weaknesses,
        misconceptions=misconceptions,
    )
    await session.flush()
    return {
        "success": True,
        "message": "Evaluation created successfully.",
        "data": _evaluation_response(evaluation),
    }


@router.get("/{evaluation_id}", response_model=dict)
async def get_evaluation(
    evaluation_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = EvaluationService(session)
    evaluation = await service.get_evaluation_by_id(evaluation_id)
    if evaluation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )
    return {
        "success": True,
        "data": _evaluation_response(evaluation),
    }
