import uuid
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Assessment, Evaluation, MRIReport, User, Class
from app.db.repositories.assessment_repository import AssessmentRepository
from app.db.repositories.class_repository import ClassRepository
from app.db.repositories.evaluation_repository import EvaluationRepository
from app.db.repositories.mri_report_repository import MRIReportRepository
from app.db.repositories.student_repository import StudentRepository
from app.db.repositories.topic_repository import TopicRepository
from app.db.repositories.user_repository import UserRepository


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.assessment_repo = AssessmentRepository(session)
        self.evaluation_repo = EvaluationRepository(session)
        self.report_repo = MRIReportRepository(session)
        self.student_repo = StudentRepository(session)
        self.class_repo = ClassRepository(session)
        self.topic_repo = TopicRepository(session)
        self.user_repo = UserRepository(session)

    async def get_student_dashboard(self, student_id: str) -> dict[str, Any]:
        assessments = await self.assessment_repo.get_by_student_id(student_id)
        evaluations = []
        try:
            evaluations = await self.evaluation_repo.get_by_student_id(student_id)
        except Exception:
            evaluations = []

        reports = []
        try:
            reports = await self.report_repo.get_by_student_id(student_id)
        except Exception:
            reports = []

        total_assessments = len(assessments)
        completed_evaluations = len(evaluations)
        average_score = (
            sum(e.overall_score for e in evaluations) / completed_evaluations
            if completed_evaluations > 0
            else None
        )

        recent_reports = sorted(reports, key=lambda r: r.created_at, reverse=True)[:5]

        return {
            "total_assessments": total_assessments,
            "completed_evaluations": completed_evaluations,
            "average_score": average_score,
            "recent_reports": [
                {
                    "id": str(r.id),
                    "evaluation_id": str(r.evaluation_id),
                    "overall_score": r.overall_score,
                    "mastery_level": r.mastery_level.value if hasattr(r.mastery_level, "value") else r.mastery_level,
                    "teacher_summary": r.teacher_summary,
                    "student_summary": r.student_summary,
                    "strengths": r.strengths,
                    "weaknesses": r.weaknesses,
                    "misconceptions": r.misconceptions,
                    "recommendations": r.recommendations,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in recent_reports
            ],
        }

    async def get_teacher_dashboard(self, teacher_id: str) -> dict[str, Any]:
        classes = await self.class_repo.get_by_teacher_id(teacher_id)
        class_ids = [c.id for c in classes]

        students = []
        if class_ids:
            for class_id in class_ids:
                students.extend(await self.student_repo.get_by_class_id(class_id))

        student_ids = [s.id for s in students]

        assessments = []
        evaluations = []
        if student_ids:
            for sid in student_ids:
                assessments.extend(await self.assessment_repo.get_by_student_id(sid))
                try:
                    evaluations.extend(await self.evaluation_repo.get_by_student_id(sid))
                except Exception:
                    pass

        total_students = len(students)
        total_assessments = len(assessments)

        average_class_score = (
            sum(e.overall_score for e in evaluations) / len(evaluations)
            if evaluations
            else None
        )

        return {
            "total_students": total_students,
            "total_assessments": total_assessments,
            "average_class_score": average_class_score,
        }

    async def get_admin_dashboard(self) -> dict[str, Any]:
        total_users = await self.user_repo.count()
        total_topics = await self.topic_repo.count()
        total_assessments = await self.assessment_repo.count()
        total_evaluations = await self.evaluation_repo.count()

        return {
            "total_users": total_users,
            "total_topics": total_topics,
            "total_assessments": total_assessments,
            "total_evaluations": total_evaluations,
        }
