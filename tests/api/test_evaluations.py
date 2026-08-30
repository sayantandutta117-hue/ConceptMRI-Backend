import pytest
from httpx import AsyncClient

from app.db.models.models import Assessment, Evaluation, Student, Topic, User
from app.db.repositories.evaluation_repository import EvaluationRepository
from app.main import app


@pytest.mark.asyncio
async def test_create_evaluation(client: AsyncClient, db_session) -> None:
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

    payload = {
        "assessment_id": str(assessment.id),
        "overall_score": 85,
        "mastery_level": "PROFICIENT",
        "confidence_level": "HIGH",
        "strengths": ["Good understanding"],
        "weaknesses": ["Needs practice"],
        "misconceptions": [],
    }
    response = await client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["assessment_id"] == str(assessment.id)
    assert body["data"]["overall_score"] == 85


@pytest.mark.asyncio
async def test_create_evaluation_with_short_fields(client: AsyncClient, db_session) -> None:
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

    payload = {
        "assessment_id": str(assessment.id),
        "score": 80,
        "mastery_level": "PROFICIENT",
        "confidence": "HIGH",
        "strengths": ["Good"],
        "weaknesses": ["None"],
        "misconceptions": [],
    }
    response = await client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["overall_score"] == 80
    assert body["data"]["confidence_level"] == "HIGH"


@pytest.mark.asyncio
async def test_get_evaluation_by_id(client: AsyncClient, db_session) -> None:
    user = User(email="student3@test.com", password_hash="hash", name="Test Student 3", role="STUDENT", status="ACTIVE")
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
        overall_score=90,
        mastery_level="PROFICIENT",
        confidence_level="HIGH",
        strengths=["Good"],
        weaknesses=["None"],
        misconceptions=[],
    )
    db_session.add(evaluation)
    await db_session.flush()

    response = await client.get(f"/api/v1/evaluations/{evaluation.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == str(evaluation.id)
    assert body["data"]["overall_score"] == 90
