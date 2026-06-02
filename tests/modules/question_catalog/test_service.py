import asyncio
from types import SimpleNamespace

import pytest

from modules.question_catalog import QuestionCatalogService


class FakeDocumentRepository:
    def __init__(self, document) -> None:
        self.document = document

    async def get_document(self, document_id: str):
        if self.document is None:
            return None

        if self.document.id != document_id:
            return None

        return self.document


class FakeQuestionRepository:
    def __init__(self) -> None:
        self.document_id = None
        self.segmented_questions = []

    async def replace_for_document(
        self,
        *,
        document_id: str,
        segmented_questions,
    ):
        self.document_id = document_id
        self.segmented_questions = segmented_questions
        return segmented_questions


def test_segment_completed_document() -> None:
    document = SimpleNamespace(
        id="document-id",
        status="completed",
        markdown_content="""
Bài 1. Tính $x^2 + 1$.

Bài 2. Tính $x^3 + 1$.
""",
    )

    question_repository = FakeQuestionRepository()
    service = QuestionCatalogService(
        document_repository=FakeDocumentRepository(document),
        question_repository=question_repository,
    )

    questions = asyncio.run(service.segment_document("document-id"))

    assert len(questions) == 2
    assert question_repository.document_id == "document-id"
    assert questions[0].marker_number == "1"
    assert questions[1].marker_number == "2"


def test_reject_missing_document() -> None:
    service = QuestionCatalogService(
        document_repository=FakeDocumentRepository(None),
        question_repository=FakeQuestionRepository(),
    )

    with pytest.raises(ValueError, match="Document not found"):
        asyncio.run(service.segment_document("missing"))


def test_reject_document_that_is_not_completed() -> None:
    document = SimpleNamespace(
        id="document-id",
        status="processing",
        markdown_content="# Pending",
    )

    service = QuestionCatalogService(
        document_repository=FakeDocumentRepository(document),
        question_repository=FakeQuestionRepository(),
    )

    with pytest.raises(ValueError, match="not ready for segmentation"):
        asyncio.run(service.segment_document("document-id"))


def test_reject_document_without_markdown() -> None:
    document = SimpleNamespace(
        id="document-id",
        status="completed",
        markdown_content=None,
    )

    service = QuestionCatalogService(
        document_repository=FakeDocumentRepository(document),
        question_repository=FakeQuestionRepository(),
    )

    with pytest.raises(ValueError, match="Markdown is not available"):
        asyncio.run(service.segment_document("document-id"))