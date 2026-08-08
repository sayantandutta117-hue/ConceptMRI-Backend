from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_session
from app.schemas.dashboard import (
    AdminDashboardResponse,
    StudentDashboardResponse,
    TeacherDashboardResponse,
)
from app.services.dashboard.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/student/{student_id}", response_model=dict)
async def get_student_dashboard(
    student_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = DashboardService(session)
    data = await service.get_student_dashboard(student_id)
    return {"success": True, **data}


@router.get("/teacher/{teacher_id}", response_model=dict)
async def get_teacher_dashboard(
    teacher_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = DashboardService(session)
    data = await service.get_teacher_dashboard(teacher_id)
    return {"success": True, **data}


@router.get("/admin", response_model=dict)
async def get_admin_dashboard(
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = DashboardService(session)
    data = await service.get_admin_dashboard()
    return {"success": True, **data}
