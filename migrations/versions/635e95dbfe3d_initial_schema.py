"""initial schema

Revision ID: 635e95dbfe3d
Revises: 
Create Date: 2026-08-07 18:54:33.983269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "635e95dbfe3d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="ACTIVE"),
        sa.Column("institution", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    op.create_table(
        "teachers",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "students",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("class_id", sa.Uuid(as_uuid=True), sa.ForeignKey("classes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("learning_streak", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_students_class_id", "students", ["class_id"], unique=False)

    op.create_table(
        "classes",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("teacher_id", sa.Uuid(as_uuid=True), sa.ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "topics",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("topic_name", sa.String(255), nullable=False),
        sa.Column("difficulty", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("learning_objectives", sa.JSON, nullable=True),
        sa.Column("prerequisites", sa.JSON, nullable=True),
        sa.Column("is_archived", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_topics_subject", "topics", ["subject"], unique=False)
    op.create_index("ix_topics_difficulty", "topics", ["difficulty"], unique=False)

    op.create_table(
        "rubrics",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("topic_id", sa.Uuid(as_uuid=True), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("concepts", sa.JSON, nullable=False),
        sa.Column("evaluation_rules", sa.JSON, nullable=False),
        sa.Column("common_misconceptions", sa.JSON, nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="CREATED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "assessments",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", sa.Uuid(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic_id", sa.Uuid(as_uuid=True), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING_EVALUATION", index=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_assessments_student_id", "assessments", ["student_id"], unique=False)
    op.create_index("ix_assessments_topic_id", "assessments", ["topic_id"], unique=False)

    op.create_table(
        "evaluations",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("assessment_id", sa.Uuid(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, unique=True, index=True),
        sa.Column("overall_score", sa.Integer, nullable=False),
        sa.Column("mastery_level", sa.String(50), nullable=False),
        sa.Column("confidence_level", sa.String(50), nullable=False),
        sa.Column("strengths", sa.JSON, nullable=False),
        sa.Column("weaknesses", sa.JSON, nullable=False),
        sa.Column("misconceptions", sa.JSON, nullable=False),
        sa.Column("raw_ai_response", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "mri_reports",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("evaluation_id", sa.Uuid(as_uuid=True), sa.ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, unique=True, index=True),
        sa.Column("overall_score", sa.Integer, nullable=False),
        sa.Column("mastery_level", sa.String(50), nullable=False),
        sa.Column("teacher_summary", sa.Text, nullable=False),
        sa.Column("student_summary", sa.Text, nullable=False),
        sa.Column("strengths", sa.JSON, nullable=False),
        sa.Column("weaknesses", sa.JSON, nullable=False),
        sa.Column("misconceptions", sa.JSON, nullable=False),
        sa.Column("recommendations", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", sa.Uuid(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evaluation_id", sa.Uuid(as_uuid=True), sa.ForeignKey("evaluations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("class_id", sa.Uuid(as_uuid=True), sa.ForeignKey("classes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("concept", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("suggested_action", sa.Text, nullable=False),
        sa.Column("priority", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_recommendations_student_id", "recommendations", ["student_id"], unique=False)

    op.create_table(
        "knowledge_graph_nodes",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", sa.Uuid(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("concept_id", sa.String(255), nullable=False, index=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("confidence", sa.String(50), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "knowledge_graph_edges",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", sa.Uuid(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("from_concept", sa.String(255), nullable=False, index=True),
        sa.Column("to_concept", sa.String(255), nullable=False, index=True),
    )


def downgrade() -> None:
    op.drop_table("knowledge_graph_edges")
    op.drop_table("knowledge_graph_nodes")
    op.drop_table("recommendations")
    op.drop_table("mri_reports")
    op.drop_table("evaluations")
    op.drop_table("assessments")
    op.drop_table("rubrics")
    op.drop_table("topics")
    op.drop_table("classes")
    op.drop_table("students")
    op.drop_table("teachers")
    op.drop_table("users")
