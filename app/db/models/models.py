import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        nullable=False,
        index=True,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status", native_enum=False),
        nullable=False,
        default=UserStatus.ACTIVE,
    )
    institution: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    student_profile: Mapped[Optional["Student"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    teacher_profile: Mapped[Optional["Teacher"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False
    )
    class_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("classes.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
    learning_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="student_profile")
    class_ref: Mapped[Optional["Class"]] = relationship(back_populates="students")
    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    knowledge_graph_nodes: Mapped[list["KnowledgeGraphNode"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    knowledge_graph_edges: Mapped[list["KnowledgeGraphEdge"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="teacher_profile")
    classes: Mapped[list["Class"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    teacher: Mapped["Teacher"] = relationship(back_populates="classes")
    students: Mapped[list["Student"]] = relationship(back_populates="class_ref")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    topic_name: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, name="difficulty", native_enum=False),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    learning_objectives: Mapped[Optional[list[str]]] = mapped_column(
        JSON, nullable=True
    )
    prerequisites: Mapped[Optional[list[str]]] = mapped_column(
        JSON, nullable=True
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    rubrics: Mapped[list["Rubric"]] = relationship(
        back_populates="topic", cascade="all, delete-orphan"
    )
    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="topic", cascade="all, delete-orphan"
    )


class Rubric(Base):
    __tablename__ = "rubrics"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    concepts: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    evaluation_rules: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    common_misconceptions: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    status: Mapped[RubricStatus] = mapped_column(
        Enum(RubricStatus, name="rubric_status", native_enum=False),
        nullable=False,
        default=RubricStatus.CREATED,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    topic: Mapped["Topic"] = relationship(back_populates="rubrics")


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[AssessmentStatus] = mapped_column(
        Enum(AssessmentStatus, name="assessment_status", native_enum=False),
        nullable=False,
        default=AssessmentStatus.PENDING_EVALUATION,
        index=True,
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    student: Mapped["Student"] = relationship(back_populates="assessments")
    topic: Mapped["Topic"] = relationship(back_populates="assessments")
    evaluation: Mapped[Optional["Evaluation"]] = relationship(
        back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    mastery_level: Mapped[MasteryLevel] = mapped_column(
        Enum(MasteryLevel, name="mastery_level", native_enum=False),
        nullable=False,
    )
    confidence_level: Mapped[ConfidenceLevel] = mapped_column(
        Enum(ConfidenceLevel, name="confidence_level", native_enum=False),
        nullable=False,
    )
    strengths: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    weaknesses: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    misconceptions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    raw_ai_response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    assessment: Mapped["Assessment"] = relationship(back_populates="evaluation")
    mri_report: Mapped[Optional["MRIReport"]] = relationship(
        back_populates="evaluation", uselist=False, cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan"
    )


class MRIReport(Base):
    __tablename__ = "mri_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("evaluations.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    mastery_level: Mapped[MasteryLevel] = mapped_column(
        Enum(MasteryLevel, name="mastery_level", native_enum=False),
        nullable=False,
    )
    teacher_summary: Mapped[str] = mapped_column(Text, nullable=False)
    student_summary: Mapped[str] = mapped_column(Text, nullable=False)
    strengths: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    weaknesses: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    misconceptions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    evaluation: Mapped["Evaluation"] = relationship(back_populates="mri_report")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    evaluation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("evaluations.id", ondelete="SET NULL"),
        nullable=True
    )
    class_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("classes.id", ondelete="SET NULL"),
        nullable=True
    )
    concept: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_action: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[RecommendationPriority] = mapped_column(
        Enum(RecommendationPriority, name="recommendation_priority", native_enum=False),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    student: Mapped["Student"] = relationship(back_populates="recommendations")
    evaluation: Mapped[Optional["Evaluation"]] = relationship(back_populates="recommendations")


class KnowledgeGraphNode(Base):
    __tablename__ = "knowledge_graph_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    concept_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[MasteryLevel] = mapped_column(
        Enum(MasteryLevel, name="mastery_level", native_enum=False),
        nullable=False,
    )
    confidence: Mapped[Optional[ConfidenceLevel]] = mapped_column(
        Enum(ConfidenceLevel, name="confidence_level", native_enum=False),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    student: Mapped["Student"] = relationship(back_populates="knowledge_graph_nodes")


class KnowledgeGraphEdge(Base):
    __tablename__ = "knowledge_graph_edges"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    from_concept: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    to_concept: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    student: Mapped["Student"] = relationship(back_populates="knowledge_graph_edges")
