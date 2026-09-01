import uuid

import pytest
from httpx import AsyncClient

from app.db.models.enums import UserRole, UserStatus
from app.db.models.models import Assessment, Class, Evaluation, Student, Teacher, Topic, User
from app.main import app


def _auth_header(user_id: str) -> dict[str, str]:
    from app.core.security import create_access_token

    token = create_access_token(subject=user_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_teacher_students_empty(client: AsyncClient, db_session) -> None:
    teacher_user = User(
        email="teacher-empty@test.com",
        password_hash="hash",
        name="Empty Teacher",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
    )
    teacher = Teacher(user=teacher_user, user_id=teacher_user.id)
    db_session.add(teacher_user)
    db_session.add(teacher)
    await db_session.flush()

    response = await client.get(
        "/api/v1/teacher/students",
        headers=_auth_header(str(teacher_user.id)),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == []


@pytest.mark.asyncio
async def test_teacher_students_with_data(client: AsyncClient, db_session) -> None:
    teacher_user = User(
        email="teacher-data@test.com",
        password_hash="hash",
        name="Data Teacher",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
    )
    teacher = Teacher(user=teacher_user, user_id=teacher_user.id)
    db_session.add(teacher_user)
    db_session.add(teacher)
    await db_session.flush()

    class_ = Class(name="Test Class", teacher_id=teacher.id)
    db_session.add(class_)
    await db_session.flush()

    student_user = User(
        email="student-teacher@test.com",
        password_hash="hash",
        name="Student For Teacher",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    student = Student(user=student_user, user_id=student_user.id, class_id=class_.id)
    topic = Topic(subject="Math", topic_name="Algebra", difficulty="EASY", is_archived=False)
    db_session.add(student_user)
    db_session.add(student)
    db_session.add(topic)
    await db_session.flush()

    assessment = Assessment(
        student_id=student.id,
        topic_id=topic.id,
        answer="A" * 20,
        status="COMPLETED",
    )
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

    response = await client.get(
        "/api/v1/teacher/students",
        headers=_auth_header(str(teacher_user.id)),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    student_data = body["data"][0]
    assert student_data["student_id"] == str(student.id)
    assert student_data["name"] == "Student For Teacher"
    assert student_data["email"] == "student-teacher@test.com"
    assert student_data["latest_assessment"] is not None
    assert student_data["latest_assessment"]["id"] == str(assessment.id)
    assert student_data["latest_assessment"]["status"] == "COMPLETED"
    assert student_data["latest_assessment"]["score"] == 90
    assert student_data["latest_assessment"]["created_at"] is not None
    assert student_data["latest_assessment"]["submitted_at"] is not None


@pytest.mark.asyncio
async def test_non_teacher_cannot_access_teacher_students(
    client: AsyncClient, db_session
) -> None:
    student_user = User(
        email="student-block@test.com",
        password_hash="hash",
        name="Block Student",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    student = Student(user=student_user, user_id=student_user.id)
    db_session.add(student_user)
    db_session.add(student)
    await db_session.flush()

    response = await client.get(
        "/api/v1/teacher/students",
        headers=_auth_header(str(student_user.id)),
    )
    assert response.status_code == 403
    body = response.json()
    assert body["detail"] == "Teacher access required"


@pytest.mark.asyncio
async def test_teacher_students_latest_assessment_when_multiple(
    client: AsyncClient, db_session
) -> None:
    teacher_user = User(
        email="teacher-multi@test.com",
        password_hash="hash",
        name="Multi Teacher",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
    )
    teacher = Teacher(user=teacher_user, user_id=teacher_user.id)
    db_session.add(teacher_user)
    db_session.add(teacher)
    await db_session.flush()

    class_ = Class(name="Multi Class", teacher_id=teacher.id)
    db_session.add(class_)
    await db_session.flush()

    student_user = User(
        email="student-multi@test.com",
        password_hash="hash",
        name="Multi Student",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    student = Student(user=student_user, user_id=student_user.id, class_id=class_.id)
    topic = Topic(subject="Math", topic_name="Algebra", difficulty="EASY", is_archived=False)
    db_session.add(student_user)
    db_session.add(student)
    db_session.add(topic)
    await db_session.flush()

    assessment1 = Assessment(
        student_id=student.id,
        topic_id=topic.id,
        answer="First answer",
        status="PENDING_EVALUATION",
    )
    db_session.add(assessment1)
    await db_session.flush()

    assessment2 = Assessment(
        student_id=student.id,
        topic_id=topic.id,
        answer="Second answer",
        status="COMPLETED",
    )
    db_session.add(assessment2)
    await db_session.flush()

    evaluation = Evaluation(
        assessment_id=assessment2.id,
        overall_score=95,
        mastery_level="EXPERT",
        confidence_level="HIGH",
        strengths=["Great"],
        weaknesses=[],
        misconceptions=[],
    )
    db_session.add(evaluation)
    await db_session.flush()

    response = await client.get(
        "/api/v1/teacher/students",
        headers=_auth_header(str(teacher_user.id)),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    latest = body["data"][0]["latest_assessment"]
    assert latest is not None
    assert latest["id"] == str(assessment2.id)
    assert latest["status"] == "COMPLETED"
    assert latest["score"] == 95
