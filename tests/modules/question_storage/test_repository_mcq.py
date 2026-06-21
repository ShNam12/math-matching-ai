import asyncio
from uuid import uuid4

from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from core.config.settings import settings
from infra.db.models import Document, Question
from infra.db.repositories.questions import QuestionRepository
from modules.question_segmenter.schemas import (
    ExtractedFormula,
    SegmentedChoice,
    SegmentedQuestion,
)
from scripts.migrate_step_mcq_fields import MIGRATION_SQL


test_engine = create_async_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def run_async_test(coroutine) -> None:
    asyncio.run(coroutine)


async def apply_mcq_migration(session: AsyncSession) -> None:
    for statement in MIGRATION_SQL:
        await session.execute(text(statement))

    await session.commit()


async def create_document(session: AsyncSession, document_id: str) -> None:
    session.add(
        Document(
            id=document_id,
            filename="mcq-repository-test.md",
            content_type="text/markdown",
            size_bytes=100,
            source_type="markdown",
            status="completed",
        )
    )
    await session.commit()


async def create_source_question(
    session: AsyncSession,
    *,
    document_id: str,
) -> Question:
    question = Question(
        document_id=document_id,
        sequence_number=1,
        marker="Bai",
        marker_number="1",
        statement="Tinh $1+1$.",
        solution=None,
        answer="2",
        formulas=[],
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["addition"],
        embedding_status="pending",
        classification_status="pending",
    )

    session.add(question)
    await session.commit()
    await session.refresh(question)

    return question


async def cleanup_document(session: AsyncSession, document_id: str) -> None:
    await session.execute(
        delete(Document).where(Document.id == document_id)
    )
    await session.commit()


def test_mcq_migration_sql_adds_defaults_and_backfills() -> None:
    joined_sql = "\n".join(MIGRATION_SQL)

    assert "ADD COLUMN IF NOT EXISTS question_type" in joined_sql
    assert "DEFAULT 'free_response'" in joined_sql
    assert "ADD COLUMN IF NOT EXISTS choices JSON" in joined_sql
    assert "DEFAULT '[]'::json" in joined_sql
    assert "ADD COLUMN IF NOT EXISTS validation_report JSON" in joined_sql
    assert "DEFAULT '{}'::json" in joined_sql
    assert "ADD COLUMN IF NOT EXISTS distractor_metadata JSON" in joined_sql
    assert "ADD COLUMN IF NOT EXISTS review_status TEXT" in joined_sql
    assert "WHERE question_type IS NULL" in joined_sql
    assert "WHERE choices IS NULL" in joined_sql
    assert "WHERE validation_report IS NULL" in joined_sql
    assert "SET review_status = 'draft'" in joined_sql


def test_create_generated_free_response_uses_mcq_defaults() -> None:
    async def run() -> None:
        async with TestSessionLocal() as session:
            await apply_mcq_migration(session)
            document_id = str(uuid4())
            await create_document(session, document_id)

            try:
                source_question = await create_source_question(
                    session,
                    document_id=document_id,
                )
                repository = QuestionRepository(session)

                saved = await repository.create_generated_question(
                    source_question=source_question,
                    statement="Tinh $2+2$.",
                    solution="$2+2=4$.",
                    answer="4",
                    formulas=[],
                    subject="math",
                    chapter="algebra",
                    difficulty="easy",
                    skills=["addition"],
                )

                assert saved.question_type == "free_response"
                assert saved.choices == []
                assert saved.correct_choice is None
                assert saved.validation_report == {}
                assert saved.generation_method is None
                assert saved.solver_code is None
                assert saved.distractor_metadata == {}
            finally:
                await cleanup_document(session, document_id)

    run_async_test(run())


def test_create_generated_multiple_choice_persists_choices() -> None:
    async def run() -> None:
        async with TestSessionLocal() as session:
            await apply_mcq_migration(session)
            document_id = str(uuid4())
            await create_document(session, document_id)

            try:
                source_question = await create_source_question(
                    session,
                    document_id=document_id,
                )
                repository = QuestionRepository(session)

                saved = await repository.create_generated_question(
                    source_question=source_question,
                    statement="Tinh $1+1$.",
                    solution="$1+1=2$.",
                    answer="2",
                    formulas=[],
                    subject="math",
                    chapter="algebra",
                    difficulty="easy",
                    skills=["addition"],
                    question_type="multiple_choice",
                    choices=[
                        {"key": "A", "text": "1", "is_correct": False},
                        {"key": "B", "text": "2", "is_correct": True},
                        {"key": "C", "text": "3", "is_correct": False},
                        {"key": "D", "text": "4", "is_correct": False},
                    ],
                    correct_choice="B",
                    validation_report={
                        "can_save": True,
                        "warnings": [],
                        "blocking_issues": [],
                        "symbolic_checks": [],
                    },
                    generation_method="ai_symbolic",
                    solver_code="ADD_INT",
                    distractor_metadata={"strategy": "nearby_integer"},
                )

                loaded = await repository.get_question(saved.id)

                assert loaded is not None
                assert loaded.question_type == "multiple_choice"
                assert loaded.correct_choice == "B"
                assert loaded.choices[1]["key"] == "B"
                assert loaded.choices[1]["is_correct"] is True
                assert loaded.validation_report["can_save"] is True
                assert loaded.generation_method == "ai_symbolic"
                assert loaded.solver_code == "ADD_INT"
                assert loaded.distractor_metadata["strategy"] == (
                    "nearby_integer"
                )
                assert loaded.review_status == "validated"
            finally:
                await cleanup_document(session, document_id)

    run_async_test(run())


def test_replace_for_document_persists_ingested_question_policy() -> None:
    async def run() -> None:
        async with TestSessionLocal() as session:
            await apply_mcq_migration(session)
            document_id = str(uuid4())
            await create_document(session, document_id)

            try:
                repository = QuestionRepository(session)

                saved_questions = await repository.replace_for_document(
                    document_id=document_id,
                    segmented_questions=[
                        SegmentedQuestion(
                            sequence_number=1,
                            marker="Bai",
                            marker_number="1",
                            statement="Tinh $1+1$.",
                            answer="2",
                            formulas=[
                                ExtractedFormula(
                                    latex="1+1",
                                    normalized_latex="1+1",
                                    source="statement",
                                )
                            ],
                        ),
                        SegmentedQuestion(
                            sequence_number=2,
                            marker="Bai",
                            marker_number="2",
                            statement="Tinh $2+2$.",
                            answer="B",
                            formulas=[],
                            question_type="multiple_choice",
                            choices=[
                                SegmentedChoice(
                                    key="A",
                                    text="3",
                                    is_correct=False,
                                ),
                                SegmentedChoice(
                                    key="B",
                                    text="4",
                                    is_correct=True,
                                ),
                                SegmentedChoice(
                                    key="C",
                                    text="5",
                                    is_correct=False,
                                ),
                                SegmentedChoice(
                                    key="D",
                                    text="6",
                                    is_correct=False,
                                ),
                            ],
                            correct_choice="B",
                        ),
                    ],
                )

                assert saved_questions[0].question_type == "free_response"
                assert saved_questions[0].choices == []
                assert saved_questions[0].correct_choice is None

                assert saved_questions[1].question_type == "multiple_choice"
                assert saved_questions[1].correct_choice == "B"
                assert saved_questions[1].choices[1]["key"] == "B"
                assert saved_questions[1].choices[1]["is_correct"] is True
                assert saved_questions[1].review_status == "draft"
            finally:
                await cleanup_document(session, document_id)

    run_async_test(run())
