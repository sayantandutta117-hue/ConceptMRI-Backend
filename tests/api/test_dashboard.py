import pytest
from httpx import AsyncClient

from app.db.models.models import (
    Assessment,
    Class,
    Evaluation,
    MRIReport,
    Student,
    Teacher,
    Topic,
    User,
)
from app.db.repositories.assessment_repository import AssessmentRepository
from app.db.repositories.evaluation_repository import EvaluationRepository
from app.db.repositories.mri_report_repository import MRIReportRepository
from app.main import app


@pytest.mark.asyncio
async def test_student_dashboard_empty(client: AsyncClient, db_session) -> None:
    user = User(email="student@test.com", password_hash="hash", name="Test Student", role="STUDENT", status="ACTIVE")
    student = Student(user=user, user_id=user.id)
    db_session.add(user)
    db_session.add(student)
    await db_session.flush()

    response = await client.get(f"/api/v1/dashboard/student/{student.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["total_assessments"] == 0
    assert body["completed_evaluations"] == 0
    assert body["average_score"] is None
    assert body["recent_reports"] == []


@pytest.mark.asyncio
async def test_student_dashboard_with_data(client: AsyncClient, db_session) -> None:
    user = User(email="student2@test.com", password_hash="hash", name="Test Student 2", role="STUDENT", status="ACTIVE")
    student = Student(user=user, user_id=user.id)
    topic = Topic(subject="Math", topic_name="Algebra", difficulty="EASY", is_archived=False)
    db_session.add(user)
    db_session.add(student)
    db_session.add(topic)
    await db_session.flush()

    assessment = Assessment(student_id=student.id, topic_id=topic.id, answer="A" * 20, status="PENDING_EVALUATION")
    db_session.add(assessment)
    await db_session.flush()

    evaluation = Evaluation(
        assessment_id=assessment.id,
        overall_score=85,
        mastery_level="PROFICIENT",
        confidence_level="HIGH",
        strengths=["Good"],
        weaknesses=["None"],
        misconceptions=[],
    )
    db_session.add(evaluation)
    await db_session.flush()

    report = MRIReport(
        evaluation_id=evaluation.id,
        overall_score=85,
        mastery_level="PROFICIENT",
        teacher_summary="Good job",
        student_summary="Keep it up",
        strengths=["Good"],
        weaknesses=["None"],
        misconceptions=[],
        recommendations=["Practice more"],
    )
    db_session.add(report)
    await db_session.flush()

    response = await client.get(f"/api/v1/dashboard/student/{student.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["total_assessments"] == 1
    assert body["completed_evaluations"] == 1
    assert body["average_score"] == 85.0
    assert len(body["recent_reports"]) == 1
    assert body["recent_reports"][0]["id"] == str(report.id)


@pytest.mark.asyncio
async def test_teacher_dashboard_empty(client: AsyncClient, db_session) -> None:
    user = User(email="teacher@test.com", password_hash="hash", name="Test Teacher", role="TEACHER", status="ACTIVE")
    teacher = Teacher(user=user, user_id=user.id)
    db_session.add(user)
    db_session.add(teacher)
    await db_session.flush()

    response = await client.get(f"/api/v1/dashboard/teacher/{teacher.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["total_students"] == 0
    assert body["total_assessments"] == 0
    assert body["average_class_score"] is None


@pytest.mark.asyncio
async def test_teacher_dashboard_with_data(client: AsyncClient, db_session) -> None:
    teacher_user = User(email="teacher2@test.com", password_hash="hash", name="Test Teacher 2", role="TEACHER", status="ACTIVE")
    teacher = Teacher(user=teacher_user, user_id=teacher_user.id)
    db_session.add(teacher_user)
    db_session.add(teacher)
    await db_session.flush()

    class_ = Class(name="Test Class", teacher_id=teacher.id)
    db_session.add(class_)
    await db_session.flush()

    student_user = User(email="student3@test.com", password_hash="hash", name="Test Student 3", role="STUDENT", status="ACTIVE")
    student = Student(user=student_user, user_id=student_user.id, class_id=class_.id)
    topic = Topic(subject="Math", topic_name="Algebra", difficulty="EASY", is_archived=False)
    db_session.add(student_user)
    db_session.add(student)
    db_session.add(topic)
    await db_session.flush()

    assessment = Assessment(student_id=student.id, topic_id=topic.id, answer="A" * 20, status="PENDING_EVALUATION")
    db_session.add(assessment)
    await db_session.flush()

    evaluation = Evaluation(
        assessment_id=assessment.id,
        overall_score=90,
        mastery_level="PROFICIENT",
        confidence_level="HIGH",
        strengths=["Good"],
        weaknesses=["None"],
        misconceptions=[],
    )
    db_session.add(evaluation)
    await db_session.flush()

    response = await client.get(f"/api/v1/dashboard/teacher/{teacher.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["total_students"] == 1
    assert body["total_assessments"] == 1
    assert body["average_class_score"] == 90.0


@pytest.mark.asyncio
async def test_admin_dashboard(client: AsyncClient, db_session) -> None:
    response = await client.get("/api/v1/dashboard/admin")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["total_users"] >= 0
    assert body["total_topics"] >= 0
    assert body["total_assessments"] >= 0
    assert body["total_evaluations"] >= 0
