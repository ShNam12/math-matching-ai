from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from infra.db.base import Base


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