import uuid

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from app.db.models.enums import UserRole
from app.db.models.models import Assessment, Student, Topic, User
from app.db.repositories.assessment_repository import AssessmentRepository
from app.main import app


def _auth_header(user_id: str) -> dict[str, str]:
    token = create_access_token(subject=user_id)
    return {"Authorization": f"Bearer {token}"}


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
async def test_create_assessment_authenticated_student_uses_student_id(
    client: AsyncClient, db_session
) -> None:
    from app.db.models.enums import UserStatus

    user = User(email="student-auth@test.com", password_hash="hash", name="Auth Student", role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    student = Student(user=user, user_id=user.id)
    topic = Topic(subject="Physics", topic_name="Kinematics", difficulty="MEDIUM", is_archived=False)
    db_session.add(user)
    db_session.add(student)
    db_session.add(topic)
    await db_session.flush()

    payload = {
        "student_id": str(user.id),
        "topic_id": str(topic.id),
        "answer": "A" * 20,
    }
    response = await client.post(
        "/api/v1/assessments",
        json=payload,
        headers=_auth_header(str(user.id)),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["student_id"] == str(student.id)
    assert body["data"]["topic_id"] == str(topic.id)
    assert body["data"]["status"] == "PENDING_EVALUATION"


@pytest.mark.asyncio
async def test_create_assessment_authenticated_student_without_profile(
    client: AsyncClient, db_session
) -> None:
    from app.db.models.enums import UserStatus

    user = User(email="student-no-profile@test.com", password_hash="hash", name="No Profile", role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    topic = Topic(subject="Chemistry", topic_name="Bonds", difficulty="EASY", is_archived=False)
    db_session.add(user)
    db_session.add(topic)
    await db_session.flush()

    payload = {
        "student_id": str(user.id),
        "topic_id": str(topic.id),
        "answer": "A" * 20,
    }
    response = await client.post(
        "/api/v1/assessments",
        json=payload,
        headers=_auth_header(str(user.id)),
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["message"] == "Student profile not found."


@pytest.mark.asyncio
async def test_create_assessment_authenticated_non_student_forbidden(
    client: AsyncClient, db_session
) -> None:
    from app.db.models.enums import UserStatus

    user = User(email="teacher-auth@test.com", password_hash="hash", name="Auth Teacher", role=UserRole.TEACHER, status=UserStatus.ACTIVE)
    topic = Topic(subject="Biology", topic_name="Cells", difficulty="EASY", is_archived=False)
    db_session.add(user)
    db_session.add(topic)
    await db_session.flush()

    payload = {
        "student_id": str(user.id),
        "topic_id": str(topic.id),
        "answer": "A" * 20,
    }
    response = await client.post(
        "/api/v1/assessments",
        json=payload,
        headers=_auth_header(str(user.id)),
    )
    assert response.status_code == 403
    body = response.json()
    assert body["detail"] == "Student access required"


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
