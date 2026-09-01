from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user_optional, get_session
from app.core.exceptions import ValidationError
from app.db.models.enums import AssessmentStatus, UserRole
from app.db.repositories.assessment_repository import AssessmentRepository
from app.db.repositories.mri_report_repository import MRIReportRepository
from app.db.repositories.student_repository import StudentRepository
from app.schemas.assessment import AssessmentCreateRequest
from app.services.assessment.assessment_service import AssessmentService


router = APIRouter(prefix="/assessments", tags=["Assessments"])


def _assessment_response(assessment: Any, report: Any = None) -> dict:
    data = {
        "id": str(assessment.id),
        "student_id": str(assessment.student_id),
        "topic_id": str(assessment.topic_id),
        "answer": assessment.answer,
        "status": (
            assessment.status.value
            if hasattr(assessment.status, "value")
            else assessment.status
        ),
        "submitted_at": (
            assessment.submitted_at.isoformat()
            if assessment.submitted_at
            else None
        ),
        "completed_at": (
            assessment.completed_at.isoformat()
            if assessment.completed_at
            else None
        ),
        "created_at": (
            assessment.created_at.isoformat()
            if assessment.created_at
            else None
        ),
    }
    if report is not None:
        data["report"] = {
            "id": str(report.id),
            "evaluation_id": str(report.evaluation_id),
            "overall_score": report.overall_score,
            "mastery_level": (
                report.mastery_level.value
                if hasattr(report.mastery_level, "value")
                else report.mastery_level
            ),
            "teacher_summary": report.teacher_summary,
            "student_summary": report.student_summary,
            "strengths": report.strengths,
            "weaknesses": report.weaknesses,
            "misconceptions": report.misconceptions,
            "recommendations": report.recommendations,
            "created_at": (
                report.created_at.isoformat() if report.created_at else None
            ),
        }
    return data


@router.post("", response_model=dict)
async def create_assessment(
    payload: AssessmentCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: dict[str, Any] | None = Depends(get_current_user_optional),
) -> dict:

    student_repo = StudentRepository(session)

    print("DEBUG current_user:", current_user)
    print("DEBUG payload student_id:", payload.student_id)
    if current_user is not None:
        if current_user["role"] != UserRole.STUDENT.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student access required",
            )

        student = await student_repo.get_by_user_id(current_user["id"])

        if student is None:
            raise ValidationError(
                message="Student profile not found.",
                details=[
                    {
                        "field": "student_id",
                        "message": (
                            "No student profile exists for this user."
                        ),
                    }
                ],
            )

        student_id = str(student.id)

    else:
        student_id = payload.student_id

        if student_id is not None:
            student = await student_repo.get_by_id(student_id)

            if student is None:
                raise ValidationError(
                    message="Invalid student_id.",
                    details=[
                        {
                            "field": "student_id",
                            "message": (
                                "The provided student_id does not exist "
                                "in the students table."
                            ),
                        }
                    ],
                )

            student_id = str(student.id)

        else:
            all_students = await student_repo.get_all()

            if not all_students:
                raise ValidationError(
                    message="Student profile not found.",
                    details=[
                        {
                            "field": "student_id",
                            "message": (
                                "No student profile exists for this user."
                            ),
                        }
                    ],
                )

            student_id = str(all_students[0].id)

    service = AssessmentService(session)

    assessment = await service.create_assessment(
        student_id=student_id,
        topic_id=payload.topic_id,
        answer=payload.answer,
    )

    await session.flush()

    assessment = await service.evaluate_assessment(assessment.id)

    report = None
    if assessment.status == AssessmentStatus.COMPLETED:
        report_repo = MRIReportRepository(session)
        report = await report_repo.get_by_assessment_id(str(assessment.id))

    return {
        "success": True,
        "message": "Assessment created successfully.",
        "data": _assessment_response(assessment, report=report),
    }


@router.get("", response_model=dict)
async def get_all_assessments(
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AssessmentService(session)

    assessments = await service.get_all_assessments()

    return {
        "success": True,
        "data": [
            _assessment_response(assessment)
            for assessment in assessments
        ],
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

    report = None
    if assessment.status == AssessmentStatus.COMPLETED:
        report_repo = MRIReportRepository(session)
        report = await report_repo.get_by_assessment_id(assessment_id)

    return {
        "success": True,
        "data": _assessment_response(assessment, report=report),
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
        "data": [
            _assessment_response(assessment)
            for assessment in assessments
        ],
    }