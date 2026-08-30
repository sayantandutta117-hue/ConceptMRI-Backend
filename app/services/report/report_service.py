import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import MasteryLevel
from app.db.models.models import MRIReport
from app.db.repositories.mri_report_repository import MRIReportRepository


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.report_repo = MRIReportRepository(session)

    async def create_report(self, payload: dict) -> MRIReport:
        report = MRIReport(
            evaluation_id=uuid.UUID(payload["evaluation_id"]),
            overall_score=payload["overall_score"],
            mastery_level=payload["mastery_level"],
            teacher_summary=payload["teacher_summary"],
            student_summary=payload["student_summary"],
            strengths=payload["strengths"],
            weaknesses=payload["weaknesses"],
            misconceptions=payload["misconceptions"],
            recommendations=payload["recommendations"],
        )
        return await self.report_repo.create(report)

    async def get_report_by_id(self, report_id: str) -> Any | None:
        return await self.report_repo.get_by_id(report_id)
