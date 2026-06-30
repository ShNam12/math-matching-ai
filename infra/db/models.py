from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from infra.db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'user')",
            name="ck_users_role",
        ),
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid4()))

    username: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(Text, nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid4()))

    filename: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="uploaded")

    r2_original_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    r2_original_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    markdown_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    markdown_checksum: Mapped[str | None] = mapped_column(Text, nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "sequence_number",
            name="uq_questions_document_sequence",
        ),
    )

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    document_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    marker: Mapped[str] = mapped_column(Text, nullable=False)
    marker_number: Mapped[str] = mapped_column(Text, nullable=False)

    statement: Mapped[str] = mapped_column(Text, nullable=False)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)

    question_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="free_response",
    )
    choices: Mapped[list[dict[str, object]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    correct_choice: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_report: Mapped[dict[str, object]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    generation_method: Mapped[str | None] = mapped_column(Text, nullable=True)
    solver_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    distractor_metadata: Mapped[dict[str, object]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    formulas: Mapped[list[dict[str, str]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    chapter: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(Text, nullable=True)

    skills: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    subject_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    chapter_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        index=True,
    )
    chapter_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    topic_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        index=True,
    )
    topic_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    problem_type_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        index=True,
    )
    problem_type_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    taxonomy_id: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    taxonomy_version: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    taxonomy_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    taxonomy_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    review_status: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    classification_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="pending",
        index=True,
    )
    classification_model: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    classification_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    classified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    embedding_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="pending",
    )
    embedding_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_dimension: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    embedding_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
