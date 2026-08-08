import pytest
from httpx import AsyncClient

from app.db.models.models import Assessment, Evaluation, MRIReport, Student, Topic, User
from app.main import app


@pytest.mark.asyncio
async def test_create_report(client: AsyncClient, db_session) -> None:
    user = User(email="student@test.com", password_hash="hash", name="Test Student", role="STUDENT", status="ACTIVE")
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

    payload = {
        "evaluation_id": str(evaluation.id),
        "overall_score": 85,
        "mastery_level": "PROFICIENT",
        "teacher_summary": "Good job",
        "student_summary": "Keep it up",
        "strengths": ["Good"],
        "weaknesses": ["None"],
        "misconceptions": [],
        "recommendations": ["Practice more"],
    }
    response = await client.post("/api/v1/reports", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["evaluation_id"] == str(evaluation.id)
    assert body["data"]["overall_score"] == 85


@pytest.mark.asyncio
async def test_get_report_by_id(client: AsyncClient, db_session) -> None:
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

    response = await client.get(f"/api/v1/reports/{report.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == str(report.id)
    assert body["data"]["overall_score"] == 85
    assert body["data"]["teacher_summary"] == "Good job"


@pytest.mark.asyncio
async def test_get_report_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/reports/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
