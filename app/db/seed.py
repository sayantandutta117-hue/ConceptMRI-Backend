import uuid
from datetime import datetime, timezone

from app.db.models.enums import (
    AssessmentStatus,
    ConfidenceLevel,
    Difficulty,
    MasteryLevel,
    RecommendationPriority,
    RubricStatus,
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


async def seed_demo_data(session) -> None:
    user_repo = UserRepository(session)
    teacher_repo = TeacherRepository(session)
    student_repo = StudentRepository(session)
    class_repo = ClassRepository(session)
    topic_repo = TopicRepository(session)
    rubric_repo = RubricRepository(session)
    assessment_repo = AssessmentRepository(session)
    evaluation_repo = EvaluationRepository(session)
    report_repo = MRIReportRepository(session)
    recommendation_repo = RecommendationRepository(session)
    knowledge_graph_repo = KnowledgeGraphRepository(session)

    admin_user = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        email="admin@conceptmri.com",
        password_hash="$2b$12$LJ3mZz9Q8xQ8xQ8xQ8xQ8e8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ",  # admin123
        name="Admin User",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    teacher_user = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        email="teacher@conceptmri.com",
        password_hash="$2b$12$LJ3mZz9Q8xQ8xQ8xQ8xQ8e8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ",  # teacher123
        name="Teacher Demo",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
        institution="Demo School",
    )
    student_user1 = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000003"),
        email="student1@conceptmri.com",
        password_hash="$2b$12$LJ3mZz9Q8xQ8xQ8xQ8xQ8e8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ",  # student123
        name="Student One",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    student_user2 = User(
        id=uuid.UUID("00000000-0000-0000-0000-000000000004"),
        email="student2@conceptmri.com",
        password_hash="$2b$12$LJ3mZz9Q8xQ8xQ8xQ8xQ8e8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ8xQ",  # student123
        name="Student Two",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )

    for user in [admin_user, teacher_user, student_user1, student_user2]:
        existing = await user_repo.get_by_email(user.email)
        if existing is None:
            await user_repo.create(user)

    teacher = Teacher(
        id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        user_id=teacher_user.id,
    )
    await session.merge(teacher)

    demo_class = Class(
        id=uuid.UUID("00000000-0000-0000-0000-000000000030"),
        name="Demo CS101",
        teacher_id=teacher.id,
    )
    existing_class = await class_repo.get_by_name(demo_class.name)
    if existing_class is None:
        await class_repo.create(demo_class)

    student1 = Student(
        id=uuid.UUID("00000000-0000-0000-0000-000000000020"),
        user_id=student_user1.id,
        class_id=demo_class.id,
        learning_streak=3,
    )
    student2 = Student(
        id=uuid.UUID("00000000-0000-0000-0000-000000000021"),
        user_id=student_user2.id,
        class_id=demo_class.id,
        learning_streak=1,
    )

    for profile in [student1, student2]:
        await session.merge(profile)

    topic = Topic(
        id=uuid.UUID("00000000-0000-0000-0000-000000000040"),
        subject="Python",
        topic_name="Recursion",
        difficulty=Difficulty.MEDIUM,
        description="Understand recursion, base cases, and stack behavior.",
        learning_objectives=["Explain recursion", "Write recursive functions"],
        prerequisites=[],
    )
    existing_topic = await topic_repo.get_by_subject_and_name(topic.subject, topic.topic_name)
    if existing_topic is None:
        await topic_repo.create(topic)

    rubric = Rubric(
        id=uuid.UUID("00000000-0000-0000-0000-000000000050"),
        topic_id=topic.id,
        concepts=[{"id": "base_case", "name": "Base Case"}],
        evaluation_rules=[{"criterion": "Correct base case", "weight": 1}],
        common_misconceptions=[{"concept": "recursion", "misconception": "Confuses recursion with loops"}],
        status=RubricStatus.ACTIVE,
    )
    existing_rubric = await rubric_repo.get_active_by_topic_id(topic.id)
    if existing_rubric is None:
        await rubric_repo.create(rubric)

    now = datetime.now(timezone.utc)
    assessment = Assessment(
        id=uuid.UUID("00000000-0000-0000-0000-000000000060"),
        student_id=student1.id,
        topic_id=topic.id,
        answer="Recursion is when a function calls itself until it reaches a base case.",
        status=AssessmentStatus.COMPLETED,
        submitted_at=now,
        completed_at=now,
    )
    await assessment_repo.create(assessment)

    evaluation = Evaluation(
        id=uuid.UUID("00000000-0000-0000-0000-000000000070"),
        assessment_id=assessment.id,
        overall_score=82,
        mastery_level=MasteryLevel.PROFICIENT,
        confidence_level=ConfidenceLevel.HIGH,
        strengths=["Good base case explanation"],
        weaknesses=["Could mention stack frames"],
        misconceptions=[],
        raw_ai_response={"overall_score": 82},
    )
    await evaluation_repo.create(evaluation)

    report = MRIReport(
        id=uuid.UUID("00000000-0000-0000-0000-000000000080"),
        evaluation_id=evaluation.id,
        overall_score=82,
        mastery_level=MasteryLevel.PROFICIENT,
        teacher_summary="Student understands recursion well but should explore stack behavior.",
        student_summary="Great work! Explore recursion stack frames to deepen understanding.",
        strengths=["Good base case explanation"],
        weaknesses=["Could mention stack frames"],
        misconceptions=[],
        recommendations=["Practice tree recursion", "Visualize call stack"],
    )
    await report_repo.create(report)

    recommendation = Recommendation(
        id=uuid.UUID("00000000-0000-0000-0000-000000000090"),
        student_id=student1.id,
        evaluation_id=evaluation.id,
        concept="Recursion",
        description="Practice recursive tree traversal.",
        reason="Strengthens base case and stack understanding.",
        suggested_action="Solve 3 tree problems.",
        priority=RecommendationPriority.HIGH,
    )
    await recommendation_repo.create(recommendation)

    node = KnowledgeGraphNode(
        id=uuid.UUID("00000000-0000-0000-0000-0000000000a0"),
        student_id=student1.id,
        concept_id="recursion",
        status=MasteryLevel.PROFICIENT,
        confidence=ConfidenceLevel.HIGH,
    )
    edge = KnowledgeGraphEdge(
        id=uuid.UUID("00000000-0000-0000-0000-0000000000b0"),
        student_id=student1.id,
        from_concept="functions",
        to_concept="recursion",
    )
    existing_node = await knowledge_graph_repo.get_node_by_concept(student1.id, "recursion")
    if existing_node is None:
        await knowledge_graph_repo.create(node)
        await session.flush()
        await session.merge(edge)
