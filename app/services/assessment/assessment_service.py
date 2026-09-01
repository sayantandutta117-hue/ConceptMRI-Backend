import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models.enums import AssessmentStatus, ConfidenceLevel, MasteryLevel
from app.db.models.models import Assessment, Topic
from app.db.repositories.assessment_repository import AssessmentRepository
from app.services.evaluation.evaluation_service import EvaluationService
from app.services.report.report_service import ReportService


logger = get_logger("assessment")


class AssessmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.assessment_repo = AssessmentRepository(session)

    async def create_assessment(
        self, student_id: str, topic_id: str, answer: str
    ) -> Assessment:
        assessment = Assessment(
            student_id=uuid.UUID(student_id),
            topic_id=uuid.UUID(topic_id),
            answer=answer,
            status=AssessmentStatus.PENDING_EVALUATION,
        )
        return await self.assessment_repo.create(assessment)

    async def get_assessment_by_id(self, assessment_id: str) -> Assessment | None:
        return await self.assessment_repo.get_by_id(assessment_id)

    async def get_assessments_by_student_id(self, student_id: str) -> list[Assessment]:
        return await self.assessment_repo.get_by_student_id(student_id)

    async def evaluate_assessment(self, assessment_id: str) -> Assessment:
        assessment = await self.assessment_repo.get_by_id(assessment_id)
        if assessment is None:
            raise ValueError(f"Assessment {assessment_id} not found")

        assessment.status = AssessmentStatus.PROCESSING
        await self.session.flush()

        try:
            async with self.session.begin_nested():
                answer_length = len(assessment.answer)

                if answer_length >= 100:
                    overall_score = 85
                    mastery_level = MasteryLevel.PROFICIENT
                    confidence_level = ConfidenceLevel.HIGH
                    strengths = ["Detailed explanation", "Good use of concepts"]
                    weaknesses = ["Could add examples"]
                    misconceptions = []
                    teacher_summary = "Strong understanding demonstrated."
                    student_summary = "Excellent work! Keep it up."
                    recommendations = ["Practice advanced problems"]
                elif answer_length >= 50:
                    overall_score = 70
                    mastery_level = MasteryLevel.DEVELOPING
                    confidence_level = ConfidenceLevel.MEDIUM
                    strengths = ["Basic understanding", "Correct terminology"]
                    weaknesses = ["Needs more detail", "Missing examples"]
                    misconceptions = []
                    teacher_summary = "Good start, add more detail."
                    student_summary = "Good work! Add more detail next time."
                    recommendations = ["Review topic concepts", "Practice with examples"]
                else:
                    overall_score = 50
                    mastery_level = MasteryLevel.BEGINNER
                    confidence_level = ConfidenceLevel.LOW
                    strengths = ["Attempted the question"]
                    weaknesses = ["Answer too brief", "Lacks depth"]
                    misconceptions = []
                    teacher_summary = "Answer is too brief. Please review the topic."
                    student_summary = "Try to write more detailed answers."
                    recommendations = ["Review learning materials", "Ask teacher for help"]

                eval_service = EvaluationService(self.session)
                evaluation = await eval_service.create_evaluation(
                    assessment_id=str(assessment_id),
                    overall_score=overall_score,
                    mastery_level=mastery_level.value,
                    confidence_level=confidence_level.value,
                    strengths=strengths,
                    weaknesses=weaknesses,
                    misconceptions=misconceptions,
                )

                report_service = ReportService(self.session)
                await report_service.create_report(
                    {
                        "evaluation_id": str(evaluation.id),
                        "overall_score": overall_score,
                        "mastery_level": mastery_level.value,
                        "teacher_summary": teacher_summary,
                        "student_summary": student_summary,
                        "strengths": strengths,
                        "weaknesses": weaknesses,
                        "misconceptions": misconceptions,
                        "recommendations": recommendations,
                    }
                )

                assessment.status = AssessmentStatus.COMPLETED
                assessment.completed_at = datetime.now(timezone.utc)
                await self.session.flush()

            return assessment

        except Exception as exc:
            assessment = await self.assessment_repo.get_by_id(assessment_id)
            if assessment is not None:
                await self.session.refresh(assessment)
                assessment.status = AssessmentStatus.FAILED
                assessment.completed_at = datetime.now(timezone.utc)
                await self.session.flush()
            logger.exception(
                "Evaluation failed for assessment %s: %s", assessment_id, exc
            )
            return assessment
