from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_teacher, get_session
from app.services.teacher.teacher_service import TeacherService

router = APIRouter(prefix="/teacher", tags=["Teacher"])


@router.get("/students", response_model=dict)
async def get_teacher_students(
    current_teacher: dict[str, Any] = Depends(get_current_teacher),
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = TeacherService(session)
    students = await service.get_students_with_latest_assessment(
        current_teacher["id"]
    )
    return {
        "success": True,
        "data": students,
    }
