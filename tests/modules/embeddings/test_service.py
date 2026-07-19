import asyncio
from types import SimpleNamespace

import pytest

from modules.embeddings.service import QuestionEmbeddingService


class FakeQuestionRepository:
    def __init__(self, questions) -> None:
        self.questions = questions
        self.pending_document_id = None
        self.completed_document_id = None
        self.failed_document_id = None
        self.embedding_model = None
        self.embedding_dimension = None
        self.error_message = None
        self.pending_question_id = None
        self.completed_question_id = None
        self.failed_question_id = None

    async def list_by_document(self, document_id: str):
        return [
            question
            for question in self.questions
            if question.document_id == document_id
        ]

    async def get_question(self, question_id: str):
        return next(
            (
                question
                for question in self.questions
                if question.id == question_id
            ),
            None,
        )

    async def mark_embedding_pending_for_document(
        self,
        document_id: str,
    ) -> None:
        self.pending_document_id = document_id

    async def mark_embedding_completed_for_document(
        self,
        *,
        document_id: str,
        embedding_model: str,
        embedding_dimension: int,
    ) -> None:
        self.completed_document_id = document_id
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension

    async def mark_embedding_failed_for_document(
        self,
        *,
        document_id: str,
        error_message: str,
    ) -> None:
        self.failed_document_id = document_id
        self.error_message = error_message

    async def mark_embedding_pending_for_question(
        self,
        question_id: str,
    ) -> None:
        self.pending_question_id = question_id

    async def mark_embedding_completed_for_question(
        self,
        *,
        question_id: str,
        embedding_model: str,
        embedding_dimension: int,
    ) -> None:
        self.completed_question_id = question_id
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension

    async def mark_embedding_failed_for_question(
        self,
        *,
        question_id: str,
        error_message: str,
    ) -> None:
        self.failed_question_id = question_id
        self.error_message = error_message

class FakeVectorRepository:
    def __init__(self) -> None:
        self.document_id = None
        self.questions = []
        self.formulas = []
        self.question = None
        self.question_formulas = []

    async def replace_for_document(
        self,
        *,
        document_id: str,
        questions,
        formulas,
    ) -> None:
        self.document_id = document_id
        self.questions = questions
        self.formulas = formulas

    async def replace_for_question(
        self,
        *,
        question,
        formulas,
    ) -> None:
        self.question = question
        self.question_formulas = formulas


class FakeEmbedder:
    model = "fake-embedding-model"
    dimension = 3

    def __init__(self) -> None:
        self.texts = []

    def embed_text(self, text: str) -> list[float]:
        self.texts.append(text)
        return [0.1, 0.2, 0.3]


def test_embed_document() -> None:
    question = SimpleNamespace(
        id="question-id",
        document_id="document-id",
        sequence_number=1,
        marker="Bai",
        marker_number="27",
        statement="Tinh $x^2 + 1$.",
        solution=None,
        answer=None,
        formulas=[
            {
                "latex": "x^2 + 1",
                "normalized_latex": "x^2 + 1",
                "source": "statement",
            }
        ],
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        subject_code=None,
        chapter_code=None,
        chapter_name=None,
        topic_code=None,
        topic_name=None,
        problem_type_code=None,
        problem_type_name=None,
        taxonomy_confidence=None,
        review_status=None,
        classification_status="pending",
    )

    question_repository = FakeQuestionRepository([question])
    vector_repository = FakeVectorRepository()
    embedder = FakeEmbedder()
    service = QuestionEmbeddingService(
        question_repository=question_repository,
        vector_repository=vector_repository,
        embedder=embedder,
    )

    result = asyncio.run(service.embed_document("document-id"))

    assert result.document_id == "document-id"
    assert result.question_count == 1
    assert result.formula_count == 1
    assert vector_repository.document_id == "document-id"
    assert len(vector_repository.questions) == 1
    assert len(vector_repository.formulas) == 1
    assert len(embedder.texts) == 2

    assert question_repository.pending_document_id == "document-id"
    assert question_repository.completed_document_id == "document-id"
    assert question_repository.embedding_model == "fake-embedding-model"
    assert question_repository.embedding_dimension == 3
    assert question_repository.failed_document_id is None


def test_embed_question_only_indexes_requested_question() -> None:
    first_question = SimpleNamespace(
        id="first-question-id",
        document_id="document-id",
        sequence_number=1,
        marker="Bai",
        marker_number="1",
        statement="Cau hoi cu.",
        solution=None,
        answer=None,
        formulas=[],
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        subject_code=None,
        chapter_code=None,
        chapter_name=None,
        topic_code=None,
        topic_name=None,
        problem_type_code=None,
        problem_type_name=None,
        taxonomy_confidence=None,
        review_status=None,
        classification_status="completed",
    )
    generated_question = SimpleNamespace(
        id="generated-question-id",
        document_id="document-id",
        sequence_number=2,
        marker="Generated",
        marker_number="2",
        statement="Cau hoi moi $x^2$.",
        solution=None,
        answer=None,
        formulas=[
            {
                "latex": "x^2",
                "normalized_latex": "x^2",
                "source": "statement",
            }
        ],
        subject="Calculus 1",
        chapter="Chuong 1",
        difficulty="medium",
        skills=["derivative"],
        subject_code=None,
        chapter_code=None,
        chapter_name=None,
        topic_code=None,
        topic_name=None,
        problem_type_code=None,
        problem_type_name=None,
        taxonomy_confidence=None,
        review_status="validated",
        classification_status="pending",
    )
    question_repository = FakeQuestionRepository(
        [first_question, generated_question]
    )
    vector_repository = FakeVectorRepository()
    embedder = FakeEmbedder()
    service = QuestionEmbeddingService(
        question_repository=question_repository,
        vector_repository=vector_repository,
        embedder=embedder,
    )

    result = asyncio.run(service.embed_question("generated-question-id"))

    assert result.document_id == "document-id"
    assert result.question_count == 1
    assert result.formula_count == 1
    assert vector_repository.document_id is None
    assert vector_repository.question.question_id == "generated-question-id"
    assert len(vector_repository.question_formulas) == 1
    assert len(embedder.texts) == 2
    assert question_repository.pending_question_id == "generated-question-id"
    assert question_repository.completed_question_id == "generated-question-id"
    assert question_repository.failed_question_id is None


def test_embed_document_includes_mcq_choices_in_question_text() -> None:
    question = SimpleNamespace(
        id="question-id",
        document_id="document-id",
        sequence_number=1,
        marker="Generated",
        marker_number="3",
        statement="Tinh $1+1$.",
        solution="$1+1=2$.",
        answer="2",
        question_type="multiple_choice",
        choices=[
            {"key": "A", "text": "1"},
            {"key": "B", "text": "2", "is_correct": True},
            {"key": "C", "text": "3"},
            {"key": "D", "text": "4"},
        ],
        correct_choice="B",
        formulas=[],
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        subject_code=None,
        chapter_code=None,
        chapter_name=None,
        topic_code=None,
        topic_name=None,
        problem_type_code=None,
        problem_type_name=None,
        taxonomy_confidence=None,
        review_status=None,
        classification_status="pending",
    )
    question_repository = FakeQuestionRepository([question])
    vector_repository = FakeVectorRepository()
    embedder = FakeEmbedder()
    service = QuestionEmbeddingService(
        question_repository=question_repository,
        vector_repository=vector_repository,
        embedder=embedder,
    )

    result = asyncio.run(service.embed_document("document-id"))

    assert result.question_count == 1
    assert result.formula_count == 0
    assert len(embedder.texts) == 1
    assert "Statement:\nTinh $1+1$." in embedder.texts[0]
    assert "Question type: multiple_choice" in embedder.texts[0]
    assert "Choices:\n- A: 1" in embedder.texts[0]
    assert "- B: 2 (correct)" in embedder.texts[0]
    assert "Correct choice: B" in embedder.texts[0]


def test_embed_document_indexes_formulas_from_mcq_choices() -> None:
    question = SimpleNamespace(
        id="question-id",
        document_id="document-id",
        sequence_number=1,
        marker="Generated",
        marker_number="4",
        statement="Tinh tich phan.",
        solution=None,
        answer="1/2",
        question_type="multiple_choice",
        choices=[
            {"key": "A", "text": "$0$", "latex": "0"},
            {
                "key": "B",
                "text": r"$\frac{1}{2}$",
                "latex": r"\frac{1}{2}",
                "is_correct": True,
            },
            {"key": "C", "text": "$1$", "latex": "1"},
            {"key": "D", "text": "$2$", "latex": "2"},
        ],
        correct_choice="B",
        formulas=[],
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        subject_code=None,
        chapter_code=None,
        chapter_name=None,
        topic_code=None,
        topic_name=None,
        problem_type_code=None,
        problem_type_name=None,
        taxonomy_confidence=None,
        review_status=None,
        classification_status="pending",
    )
    question_repository = FakeQuestionRepository([question])
    vector_repository = FakeVectorRepository()
    embedder = FakeEmbedder()
    service = QuestionEmbeddingService(
        question_repository=question_repository,
        vector_repository=vector_repository,
        embedder=embedder,
    )

    result = asyncio.run(service.embed_document("document-id"))

    assert result.formula_count == 4
    assert [
        formula.normalized_latex
        for formula in vector_repository.formulas
    ] == ["0", r"\frac{1}{2}", "1", "2"]
    assert all(
        formula.source == "choice"
        for formula in vector_repository.formulas
    )


def test_reject_document_without_segmented_questions() -> None:
    service = QuestionEmbeddingService(
        question_repository=FakeQuestionRepository([]),
        vector_repository=FakeVectorRepository(),
        embedder=FakeEmbedder(),
    )

    with pytest.raises(ValueError, match="No segmented questions"):
        asyncio.run(service.embed_document("missing-document"))

class FailingEmbedder:
    model = "failing-model"
    dimension = 3

    def embed_text(self, text: str) -> list[float]:
        raise RuntimeError("embedding failed")


def test_mark_failed_when_embedding_fails() -> None:
    question = SimpleNamespace(
        id="question-id",
        document_id="document-id",
        sequence_number=1,
        marker="Bai",
        marker_number="27",
        statement="Tinh $x^2 + 1$.",
        solution=None,
        answer=None,
        formulas=[],
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
    )

    question_repository = FakeQuestionRepository([question])
    service = QuestionEmbeddingService(
        question_repository=question_repository,
        vector_repository=FakeVectorRepository(),
        embedder=FailingEmbedder(),
    )

    with pytest.raises(RuntimeError, match="embedding failed"):
        asyncio.run(service.embed_document("document-id"))

    assert question_repository.pending_document_id == "document-id"
    assert question_repository.failed_document_id == "document-id"
    assert question_repository.error_message == "embedding failed"


def test_embed_question_marks_only_requested_question_as_failed() -> None:
    question = SimpleNamespace(
        id="question-id",
        document_id="document-id",
        sequence_number=1,
        marker="Bai",
        marker_number="1",
        statement="Tinh x.",
        solution=None,
        answer=None,
        formulas=[],
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        subject_code=None,
        chapter_code=None,
        chapter_name=None,
        topic_code=None,
        topic_name=None,
        problem_type_code=None,
        problem_type_name=None,
        taxonomy_confidence=None,
        review_status=None,
        classification_status="pending",
    )
    question_repository = FakeQuestionRepository([question])
    service = QuestionEmbeddingService(
        question_repository=question_repository,
        vector_repository=FakeVectorRepository(),
        embedder=FailingEmbedder(),
    )

    with pytest.raises(RuntimeError, match="embedding failed"):
        asyncio.run(service.embed_question("question-id"))

    assert question_repository.pending_question_id == "question-id"
    assert question_repository.failed_question_id == "question-id"
    assert question_repository.failed_document_id is None
