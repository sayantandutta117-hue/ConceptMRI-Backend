import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import (
    AssessmentStatus,
    ConfidenceLevel,
    MasteryLevel,
    UserRole,
    UserStatus,
)
from app.db.models.models import (
    Assessment,
    Class,
    Evaluation,
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    MRIReport,
    Recommendation,
    Rubric,
    Student,
    Teacher,
    Topic,
    User,
)
from app.db.repositories import (
    AssessmentRepository,
    ClassRepository,
    EvaluationRepository,
    KnowledgeGraphRepository,
    MRIReportRepository,
    RecommendationRepository,
    RubricRepository,
    StudentRepository,
    TeacherRepository,
    TopicRepository,
    UserRepository,
)


@pytest.mark.asyncio
async def test_user_repository_crud(db_session: AsyncSession) -> None:
    repo = UserRepository(db_session)
    user = User(
        id=uuid.uuid4(),
        email="repo-test@example.com",
        password_hash="hashed",
        name="Repo Test",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    created = await repo.create(user)
    assert created.id == user.id

    fetched = await repo.get_by_id(user.id)
    assert fetched is not None
    assert fetched.email == "repo-test@example.com"

    by_email = await repo.get_by_email(user.email)
    assert by_email is not None
    assert by_email.id == user.id

    assert await repo.exists_by_email(user.email) is True
    assert await repo.exists_by_email("missing@example.com") is False

    count = await repo.count()
    assert count == 1

    await repo.delete(user.id)
    assert await repo.get_by_id(user.id) is None


@pytest.mark.asyncio
async def test_student_repository_relationships(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    student_repo = StudentRepository(db_session)

    user = User(
        id=uuid.uuid4(),
        email="student-repo@example.com",
        password_hash="hashed",
        name="Student Repo",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    await user_repo.create(user)

    student = Student(id=uuid.uuid4(), user_id=user.id, learning_streak=2)
    await student_repo.create(student)

    fetched = await student_repo.get_by_user_id(user.id)
    assert fetched is not None
    assert fetched.learning_streak == 2

    fetched_with_user = await student_repo.get_with_user(student.id)
    assert fetched_with_user is not None
    assert fetched_with_user.user.email == user.email


@pytest.mark.asyncio
async def test_topic_repository_filtering(db_session: AsyncSession) -> None:
    repo = TopicRepository(db_session)
    topic = Topic(
        id=uuid.uuid4(),
        subject="Python",
        topic_name="Lists",
        difficulty="EASY",
        description="Learn lists.",
        learning_objectives=["Create lists"],
    )
    await repo.create(topic)

    active_topics = await repo.list_active(subject="Python")
    assert len(active_topics) == 1

    by_name = await repo.get_by_subject_and_name("Python", "Lists")
    assert by_name is not None
    assert by_name.id == topic.id


@pytest.mark.asyncio
async def test_assessment_lifecycle(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    student_repo = StudentRepository(db_session)
    topic_repo = TopicRepository(db_session)
    assessment_repo = AssessmentRepository(db_session)

    user = User(
        id=uuid.uuid4(),
        email="assess-lifecycle@example.com",
        password_hash="hashed",
        name="Assess User",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    await user_repo.create(user)

    student = Student(id=uuid.uuid4(), user_id=user.id)
    await student_repo.create(student)

    topic = Topic(
        id=uuid.uuid4(),
        subject="Python",
        topic_name="Loops",
        difficulty="EASY",
    )
    await topic_repo.create(topic)

    assessment = Assessment(
        id=uuid.uuid4(),
        student_id=student.id,
        topic_id=topic.id,
        answer="A loop repeats code while a condition is true.",
        status=AssessmentStatus.PENDING_EVALUATION,
    )
    await assessment_repo.create(assessment)

    fetched = await assessment_repo.get_by_id(assessment.id)
    assert fetched is not None
    assert fetched.status == AssessmentStatus.PENDING_EVALUATION

    by_student = await assessment_repo.get_by_student_id(student.id)
    assert len(by_student) == 1


@pytest.mark.asyncio
async def test_evaluation_and_report(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    student_repo = StudentRepository(db_session)
    topic_repo = TopicRepository(db_session)
    assessment_repo = AssessmentRepository(db_session)
    evaluation_repo = EvaluationRepository(db_session)
    report_repo = MRIReportRepository(db_session)

    user = User(
        id=uuid.uuid4(),
        email="eval-report@example.com",
        password_hash="hashed",
        name="Eval User",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    await user_repo.create(user)

    student = Student(id=uuid.uuid4(), user_id=user.id)
    await student_repo.create(student)

    topic = Topic(
        id=uuid.uuid4(),
        subject="Python",
        topic_name="Functions",
        difficulty="MEDIUM",
    )
    await topic_repo.create(topic)

    assessment = Assessment(
        id=uuid.uuid4(),
        student_id=student.id,
        topic_id=topic.id,
        answer="Functions allow code reuse through definitions.",
        status=AssessmentStatus.COMPLETED,
    )
    await assessment_repo.create(assessment)

    evaluation = Evaluation(
        id=uuid.uuid4(),
        assessment_id=assessment.id,
        overall_score=75,
        mastery_level=MasteryLevel.DEVELOPING,
        confidence_level=ConfidenceLevel.MEDIUM,
        strengths=["Clear explanation"],
        weaknesses=["Missing examples"],
        misconceptions=[],
    )
    await evaluation_repo.create(evaluation)

    report = MRIReport(
        id=uuid.uuid4(),
        evaluation_id=evaluation.id,
        overall_score=75,
        mastery_level=MasteryLevel.DEVELOPING,
        teacher_summary="Good start, add examples.",
        student_summary="Good work! Add examples next time.",
        strengths=["Clear explanation"],
        weaknesses=["Missing examples"],
        misconceptions=[],
        recommendations=["Practice with examples"],
    )
    await report_repo.create(report)

    fetched_report = await report_repo.get_by_evaluation_id(evaluation.id)
    assert fetched_report is not None
    assert fetched_report.student_summary == report.student_summary


@pytest.mark.asyncio
async def test_knowledge_graph_repository(db_session: AsyncSession) -> None:
    user_repo = UserRepository(db_session)
    student_repo = StudentRepository(db_session)
    graph_repo = KnowledgeGraphRepository(db_session)

    user = User(
        id=uuid.uuid4(),
        email="graph@example.com",
        password_hash="hashed",
        name="Graph User",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    await user_repo.create(user)

    student = Student(id=uuid.uuid4(), user_id=user.id)
    await student_repo.create(student)

    node = KnowledgeGraphNode(
        id=uuid.uuid4(),
        student_id=student.id,
        concept_id="loops",
        status=MasteryLevel.PROFICIENT,
        confidence=ConfidenceLevel.HIGH,
    )
    await graph_repo.create(node)

    fetched_node = await graph_repo.get_node_by_concept(student.id, "loops")
    assert fetched_node is not None
    assert fetched_node.status == MasteryLevel.PROFICIENT
