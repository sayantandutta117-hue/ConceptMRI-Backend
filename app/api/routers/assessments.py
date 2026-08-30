from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_session
from app.core.exceptions import ValidationError
from app.db.repositories.student_repository import StudentRepository
from app.schemas.assessment import AssessmentCreateRequest, AssessmentResponse
from app.services.assessment.assessment_service import AssessmentService

router = APIRouter(prefix="/assessments", tags=["Assessments"])


def _assessment_response(assessment: Any) -> dict:
    return {
        "id": str(assessment.id),
        "student_id": str(assessment.student_id),
        "topic_id": str(assessment.topic_id),
        "answer": assessment.answer,
        "status": assessment.status.value if hasattr(assessment.status, "value") else assessment.status,
        "submitted_at": assessment.submitted_at.isoformat() if assessment.submitted_at else None,
        "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
        "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
    }


@router.post("", response_model=dict)
async def create_assessment(
    payload: AssessmentCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    student_id = payload.student_id
    if student_id is None:
        all_students = await StudentRepository(session).get_all()
        if not all_students:
            raise ValidationError(
                message="student_id is required.",
                details=[{"field": "student_id", "message": "Provide student_id or ensure a student profile exists."}],
            )
        student_id = str(all_students[0].id)

    service = AssessmentService(session)
    assessment = await service.create_assessment(
        student_id=student_id,
        topic_id=payload.topic_id,
        answer=payload.answer,
    )
    await session.flush()
    return {
        "success": True,
        "message": "Assessment created successfully.",
        "data": _assessment_response(assessment),
    }


@router.get("/{assessment_id}", response_model=dict)
async def get_assessment(
    assessment_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AssessmentService(session)
    assessment = await service.get_assessment_by_id(assessment_id)
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return {
        "success": True,
        "data": _assessment_response(assessment),
    }


@router.get("/student/{student_id}", response_model=dict)
async def get_assessments_by_student(
    student_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AssessmentService(session)
    assessments = await service.get_assessments_by_student_id(student_id)
    return {
        "success": True,
        "data": [_assessment_response(assessment) for assessment in assessments],
    }
