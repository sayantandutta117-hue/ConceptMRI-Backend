import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.models import Assessment, Class, Evaluation, Student, Teacher, User
from app.db.repositories.assessment_repository import AssessmentRepository
from app.db.repositories.class_repository import ClassRepository
from app.db.repositories.evaluation_repository import EvaluationRepository
from app.db.repositories.student_repository import StudentRepository
from app.db.repositories.teacher_repository import TeacherRepository
from app.db.repositories.user_repository import UserRepository


class TeacherService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.teacher_repo = TeacherRepository(session)
        self.class_repo = ClassRepository(session)
        self.student_repo = StudentRepository(session)
        self.assessment_repo = AssessmentRepository(session)
        self.evaluation_repo = EvaluationRepository(session)
        self.user_repo = UserRepository(session)

    async def get_students_with_latest_assessment(
        self, teacher_user_id: str
    ) -> list[dict[str, Any]]:
        teacher = await self.teacher_repo.get_by_user_id(teacher_user_id)
        if teacher is None:
            return []

        classes = await self.class_repo.get_by_teacher_id(teacher.id)
        if not classes:
            return []

        class_ids = [c.id for c in classes]
        students: list[Student] = []
        for class_id in class_ids:
            students.extend(await self.student_repo.get_by_class_id(class_id))

        result: list[dict[str, Any]] = []
        for student in students:
            user = await self.user_repo.get_by_id(student.user_id)
            assessments = await self.assessment_repo.get_by_student_id(student.id)
            latest_assessment: Assessment | None = None
            if assessments:
                latest_assessment = sorted(
                    assessments,
                    key=lambda a: (
                        a.created_at or datetime.min.replace(tzinfo=timezone.utc),
                        a.id,
                    ),
                    reverse=True,
                )[0]

            latest = None
            if latest_assessment is not None:
                evaluation = await self.evaluation_repo.get_by_assessment_id(
                    latest_assessment.id
                )
                latest = {
                    "id": str(latest_assessment.id),
                    "status": (
                        latest_assessment.status.value
                        if hasattr(latest_assessment.status, "value")
                        else latest_assessment.status
                    ),
                    "score": evaluation.overall_score if evaluation else None,
                    "created_at": (
                        latest_assessment.created_at.isoformat()
                        if latest_assessment.created_at
                        else None
                    ),
                    "submitted_at": (
                        latest_assessment.submitted_at.isoformat()
                        if latest_assessment.submitted_at
                        else None
                    ),
                }

            result.append(
                {
                    "student_id": str(student.id),
                    "name": user.name if user else None,
                    "email": user.email if user else None,
                    "latest_assessment": latest,
                }
            )

        return result
