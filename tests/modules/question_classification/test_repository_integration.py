import asyncio
from uuid import uuid4

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from core.config.settings import settings

from infra.db.models import Document, Question
from infra.db.repositories.questions import QuestionRepository
from modules.question_classification import (
    ClassificationCandidate,
    validate_classification,
)
from modules.taxonomy import load_validated_taxonomy

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

def classification_result(
    *,
    confidence: float = 0.95,
):
    taxonomy, index = load_validated_taxonomy()

    candidate = ClassificationCandidate(
        chapter_code="GT1_C2_Integral_Calculus_One_Variable",
        topic_code="GT1_C2_01_Indefinite_Integrals",
        problem_type_code="GT1_C2_01_T03_Integration_By_Parts",
        skills=["integration_by_parts", "indefinite_integral"],
        difficulty="medium",
        confidence=confidence,
        reason="Đề bài sử dụng phương pháp tích phân từng phần.",
    )

    return validate_classification(candidate, taxonomy, index)


async def create_question(
    session,
    *,
    document_id: str,
    sequence_number: int,
) -> Question:
    question = Question(
        document_id=document_id,
        sequence_number=sequence_number,
        marker="Bài",
        marker_number=str(sequence_number),
        statement="Tính tích phân.",
        solution=None,
        answer=None,
        formulas=[],
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        embedding_status="pending",
        classification_status="pending",
    )

    session.add(question)
    await session.commit()
    await session.refresh(question)

    return question


async def cleanup_document(session, document_id: str) -> None:
    await session.execute(
        delete(Document).where(Document.id == document_id)
    )
    await session.commit()

def test_update_classification_saves_all_fields() -> None:
    async def run() -> None:
        async with TestSessionLocal() as session:
            document_id = str(uuid4())

            document = Document(
                id=document_id,
                filename="classification-test.md",
                content_type="text/markdown",
                size_bytes=100,
                source_type="markdown",
                status="completed",
            )
            session.add(document)
            await session.commit()

            try:
                question = await create_question(
                    session,
                    document_id=document_id,
                    sequence_number=1,
                )
                repository = QuestionRepository(session)

                updated = await repository.update_classification(
                    question,
                    result=classification_result(),
                    classification_model="fake-model",
                )

                assert updated.classification_status == "completed"

                assert updated.subject == "Giải tích 1"
                assert updated.subject_code == "CALCULUS_1"

                assert updated.chapter == (
                    "Chương 2: Phép tính tích phân hàm một biến số"
                )
                assert updated.chapter_name == (
                    "Chương 2: Phép tính tích phân hàm một biến số"
                )
                assert updated.topic_name == "Tích phân bất định"

                assert updated.taxonomy_id == "calculus_1_hust_mi1111"
                assert updated.taxonomy_version == "1.0.0"
                assert updated.taxonomy_reason == (
                    "Đề bài sử dụng phương pháp tích phân từng phần."
                )

                assert updated.difficulty == "medium"
                assert updated.skills == [
                    "integration_by_parts",
                    "indefinite_integral",
                ]
        
                assert updated.chapter_code == (
                    "GT1_C2_Integral_Calculus_One_Variable"
                )
                assert updated.topic_code == (
                    "GT1_C2_01_Indefinite_Integrals"
                )
                assert updated.problem_type_code == (
                    "GT1_C2_01_T03_Integration_By_Parts"
                )
                assert updated.problem_type_name == "Tích phân từng phần"
                assert updated.taxonomy_confidence == 0.95
                assert updated.review_status == "auto_accept"
                assert updated.classification_model == "fake-model"
                assert updated.classified_at is not None
                assert updated.classification_error is None

            finally:
                await cleanup_document(session, document_id)

    run_async_test(run())

def test_mark_classification_failed_saves_error() -> None:
    async def run() -> None:
        async with TestSessionLocal() as session:
            document_id = str(uuid4())

            session.add(Document(
                id=document_id,
                filename="failed.md",
                content_type="text/markdown",
                size_bytes=20,
                source_type="markdown",
                status="completed",
            ))
            await session.commit()

            try:
                question = await create_question(
                    session,
                    document_id=document_id,
                    sequence_number=1,
                )
                repository = QuestionRepository(session)

                updated = await repository.mark_classification_failed(
                    question,
                    error_message="Invalid model output",
                    classification_model="fake-model",
                )

                assert updated.classification_status == "failed"
                assert updated.classification_error == (
                    "Invalid model output"
                )
                assert updated.classification_model == "fake-model"
                assert updated.classified_at is None
            finally:
                await cleanup_document(session, document_id)

    run_async_test(run())

def test_mark_classification_pending_for_document() -> None:
    async def run() -> None:
        async with TestSessionLocal() as session:
            document_id = str(uuid4())

            session.add(
                Document(
                    id=document_id,
                    filename="reset-pending.md",
                    content_type="text/markdown",
                    size_bytes=50,
                    source_type="markdown",
                    status="completed",
                )
            )
            await session.commit()

            try:
                completed_question = await create_question(
                    session,
                    document_id=document_id,
                    sequence_number=1,
                )
                failed_question = await create_question(
                    session,
                    document_id=document_id,
                    sequence_number=2,
                )

                repository = QuestionRepository(session)

                await repository.update_classification(
                    completed_question,
                    result=classification_result(),
                    classification_model="fake-model",
                )
                await repository.mark_classification_failed(
                    failed_question,
                    error_message="Temporary error",
                    classification_model="fake-model",
                )

                await repository.mark_classification_pending_for_document(
                    document_id
                )

                await session.refresh(completed_question)
                await session.refresh(failed_question)

                assert completed_question.classification_status == "pending"
                assert completed_question.classification_error is None
                assert completed_question.classified_at is None

                assert failed_question.classification_status == "pending"
                assert failed_question.classification_error is None
                assert failed_question.classified_at is None
            finally:
                await cleanup_document(session, document_id)

    run_async_test(run())

def test_list_unclassified_by_document() -> None:
    async def run() -> None:
        async with TestSessionLocal() as session:
            document_id = str(uuid4())

            session.add(
                Document(
                    id=document_id,
                    filename="unclassified.md",
                    content_type="text/markdown",
                    size_bytes=50,
                    source_type="markdown",
                    status="completed",
                )
            )
            await session.commit()

            try:
                completed_question = await create_question(
                    session,
                    document_id=document_id,
                    sequence_number=1,
                )
                failed_question = await create_question(
                    session,
                    document_id=document_id,
                    sequence_number=2,
                )
                pending_question = await create_question(
                    session,
                    document_id=document_id,
                    sequence_number=3,
                )

                repository = QuestionRepository(session)

                await repository.update_classification(
                    completed_question,
                    result=classification_result(),
                    classification_model="fake-model",
                )
                await repository.mark_classification_failed(
                    failed_question,
                    error_message="Classification failed",
                    classification_model="fake-model",
                )

                questions = (
                    await repository.list_unclassified_by_document(
                        document_id
                    )
                )

                assert [question.id for question in questions] == [
                    failed_question.id,
                    pending_question.id,
                ]
                assert [
                    question.classification_status
                    for question in questions
                ] == ["failed", "pending"]
            finally:
                await cleanup_document(session, document_id)

    run_async_test(run())

def test_count_by_taxonomy() -> None:
    async def run() -> None:
        async with TestSessionLocal() as session:
            document_id = str(uuid4())

            session.add(
                Document(
                    id=document_id,
                    filename="taxonomy-count.md",
                    content_type="text/markdown",
                    size_bytes=50,
                    source_type="markdown",
                    status="completed",
                )
            )
            await session.commit()

            try:
                first_question = await create_question(
                    session,
                    document_id=document_id,
                    sequence_number=1,
                )
                second_question = await create_question(
                    session,
                    document_id=document_id,
                    sequence_number=2,
                )

                # Câu pending này không được tính vào thống kê.
                await create_question(
                    session,
                    document_id=document_id,
                    sequence_number=3,
                )

                repository = QuestionRepository(session)

                for question in [first_question, second_question]:
                    await repository.update_classification(
                        question,
                        result=classification_result(),
                        classification_model="fake-model",
                    )

                counts = await repository.count_by_taxonomy(
                    document_id=document_id
                )

                assert counts == [
                    {
                        "chapter_code": (
                            "GT1_C2_Integral_Calculus_One_Variable"
                        ),
                        "topic_code": (
                            "GT1_C2_01_Indefinite_Integrals"
                        ),
                        "problem_type_code": (
                            "GT1_C2_01_T03_Integration_By_Parts"
                        ),
                        "question_count": 2,
                    }
                ]
            finally:
                await cleanup_document(session, document_id)

    run_async_test(run())