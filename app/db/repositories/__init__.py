from app.db.repositories.assessment_repository import AssessmentRepository
from app.db.repositories.base import BaseRepository
from app.db.repositories.class_repository import ClassRepository
from app.db.repositories.evaluation_repository import EvaluationRepository
from app.db.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from app.db.repositories.mri_report_repository import MRIReportRepository
from app.db.repositories.recommendation_repository import RecommendationRepository
from app.db.repositories.rubric_repository import RubricRepository
from app.db.repositories.student_repository import StudentRepository
from app.db.repositories.teacher_repository import TeacherRepository
from app.db.repositories.topic_repository import TopicRepository
from app.db.repositories.user_repository import UserRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "StudentRepository",
    "TeacherRepository",
    "ClassRepository",
    "TopicRepository",
    "RubricRepository",
    "AssessmentRepository",
    "EvaluationRepository",
    "MRIReportRepository",
    "RecommendationRepository",
    "KnowledgeGraphRepository",
]
