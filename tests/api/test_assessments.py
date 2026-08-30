import pytest
from httpx import AsyncClient

from app.db.models.models import Assessment, Student, Topic, User
from app.db.repositories.assessment_repository import AssessmentRepository
from app.main import app


@pytest.mark.asyncio
async def test_create_assessment(client: AsyncClient, db_session) -> None:
    user = User(email="student@test.com", password_hash="hash", name="Test Student", role="STUDENT", status="ACTIVE")
    student = Student(user=user, user_id=user.id)
    topic = Topic(subject="Math", topic_name="Algebra", difficulty="EASY", is_archived=False)
    db_session.add(user)
    db_session.add(student)
    db_session.add(topic)
    await db_session.flush()

    payload = {
        "student_id": str(student.id),
        "topic_id": str(topic.id),
        "answer": "A" * 20,
    }
    response = await client.post("/api/v1/assessments", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["student_id"] == str(student.id)
    assert body["data"]["topic_id"] == str(topic.id)
    assert body["data"]["status"] == "PENDING_EVALUATION"


@pytest.mark.asyncio
async def test_create_assessment_answer_too_short(client: AsyncClient, db_session) -> None:
    user = User(email="student2@test.com", password_hash="hash", name="Test Student 2", role="STUDENT", status="ACTIVE")
    student = Student(user=user, user_id=user.id)
    topic = Topic(subject="Math", topic_name="Algebra", difficulty="EASY", is_archived=False)
    db_session.add(user)
    db_session.add(student)
    db_session.add(topic)
    await db_session.flush()

    payload = {
        "student_id": str(student.id),
        "topic_id": str(topic.id),
        "answer": "short",
    }
    response = await client.post("/api/v1/assessments", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_assessment_by_id(client: AsyncClient, db_session) -> None:
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

    response = await client.get(f"/api/v1/assessments/{assessment.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == str(assessment.id)


@pytest.mark.asyncio
async def test_get_assessments_by_student(client: AsyncClient, db_session) -> None:
    user = User(email="student4@test.com", password_hash="hash", name="Test Student 4", role="STUDENT", status="ACTIVE")
    student = Student(user=user, user_id=user.id)
    topic = Topic(subject="Math", topic_name="Algebra", difficulty="EASY", is_archived=False)
    db_session.add(user)
    db_session.add(student)
    db_session.add(topic)
    await db_session.flush()

    assessment = Assessment(student_id=student.id, topic_id=topic.id, answer="A" * 20, status="PENDING_EVALUATION")
    db_session.add(assessment)
    await db_session.flush()

    response = await client.get(f"/api/v1/assessments/student/{student.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["student_id"] == str(student.id)
