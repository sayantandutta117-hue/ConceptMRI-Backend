from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_session
from app.schemas.report import ReportCreateRequest, ReportResponse
from app.services.report.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("", response_model=dict)
async def create_report(
    payload: ReportCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = ReportService(session)
    report = await service.create_report(payload.model_dump())
    await session.flush()
    return {
        "success": True,
        "message": "Report created successfully.",
        "data": {
            "id": str(report.id),
            "evaluation_id": str(report.evaluation_id),
            "overall_score": report.overall_score,
            "mastery_level": report.mastery_level.value if hasattr(report.mastery_level, "value") else report.mastery_level,
            "teacher_summary": report.teacher_summary,
            "student_summary": report.student_summary,
            "strengths": report.strengths,
            "weaknesses": report.weaknesses,
            "misconceptions": report.misconceptions,
            "recommendations": report.recommendations,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        },
    }


@router.get("/{report_id}", response_model=dict)
async def get_report(
    report_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = ReportService(session)
    report = await service.get_report_by_id(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return {
        "success": True,
        "data": {
            "id": str(report.id),
            "evaluation_id": str(report.evaluation_id),
            "overall_score": report.overall_score,
            "mastery_level": report.mastery_level.value if hasattr(report.mastery_level, "value") else report.mastery_level,
            "teacher_summary": report.teacher_summary,
            "student_summary": report.student_summary,
            "strengths": report.strengths,
            "weaknesses": report.weaknesses,
            "misconceptions": report.misconceptions,
            "recommendations": report.recommendations,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        },
    }
