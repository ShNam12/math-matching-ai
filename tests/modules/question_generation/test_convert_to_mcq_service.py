import asyncio
import json
from types import SimpleNamespace

import pytest

from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    MultipleChoiceOption,
)
from modules.question_generation.service import QuestionGenerationService
from modules.question_quality.schemas import QualityIssue, QuestionQualityReport


class FakeQuestionRepository:
    def __init__(self, questions) -> None:
        self.questions = questions
        self.created_payload = None

    async def get_question(self, question_id: str):
        for question in self.questions:
            if question.id == question_id:
                return question

        return None

    async def list_by_document(self, document_id: str):
        return [
            question
            for question in self.questions
            if question.document_id == document_id
        ]

    async def create_generated_question(self, **kwargs):
        self.created_payload = kwargs
        source_question = kwargs["source_question"]

        return SimpleNamespace(
            id="converted-id",
            document_id=source_question.document_id,
            sequence_number=2,
            marker="Generated",
            marker_number="2",
            statement=kwargs["statement"],
            solution=kwargs["solution"],
            answer=kwargs["answer"],
            question_type=kwargs["question_type"],
            choices=kwargs["choices"],
            correct_choice=kwargs["correct_choice"],
            validation_report=kwargs["validation_report"],
            generation_method=kwargs["generation_method"],
            solver_code=kwargs["solver_code"],
            formulas=kwargs["formulas"],
            subject=kwargs["subject"],
            chapter=kwargs["chapter"],
            difficulty=kwargs["difficulty"],
            skills=kwargs["skills"],
            embedding_status="pending",
        )


class FakeGenerator:
    def __init__(self, payload) -> None:
        self.payload = payload
        self.prompts = []

    def generate_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return json.dumps(self.payload)


class FakeQualityService:
    def __init__(self, report: QuestionQualityReport | None = None) -> None:
        self.report = report or QuestionQualityReport()
        self.calls = []

    async def assess_candidate(self, **kwargs):
        self.calls.append(kwargs)
        return self.report


def make_source_question(**overrides):
    values = {
        "id": "source-id",
        "document_id": "document-id",
        "marker": "Bai",
        "marker_number": "1",
        "statement": "Tinh $1+1$.",
        "solution": "$1+1=2$.",
        "answer": "2",
        "question_type": "free_response",
        "subject": "math",
        "chapter": "algebra",
        "difficulty": "easy",
        "skills": ["addition"],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def mcq_payload():
    return {
        "items": [
            {
                "statement": "Chon ket qua cua $1+1$.",
                "solution": "$1+1=2$.",
                "answer": "2",
                "question_type": "multiple_choice",
                "choices": [
                    {"key": "A", "text": "1"},
                    {"key": "B", "text": "2", "is_correct": True},
                    {"key": "C", "text": "3"},
                    {"key": "D", "text": "4"},
                ],
                "correct_choice": "B",
            }
        ]
    }


def make_mcq_candidate() -> GeneratedQuestionCandidate:
    return GeneratedQuestionCandidate(
        statement="Chon ket qua cua $1+1$.",
        solution="$1+1=2$.",
        answer="2",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["addition"],
        formulas=[],
        quality_warnings=[],
        question_type="multiple_choice",
        choices=[
            MultipleChoiceOption(key="A", text="1"),
            MultipleChoiceOption(key="B", text="2", is_correct=True),
            MultipleChoiceOption(key="C", text="3"),
            MultipleChoiceOption(key="D", text="4"),
        ],
        correct_choice="B",
    )


def test_preview_convert_to_mcq_returns_candidate() -> None:
    source_question = make_source_question()
    quality_service = FakeQualityService()
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([source_question]),
        generator=FakeGenerator(mcq_payload()),
        quality_service=quality_service,
    )

    preview = asyncio.run(
        service.preview_convert_to_mcq(source_question_id="source-id")
    )

    candidate = preview.candidates[0]
    assert preview.source_question_id == "source-id"
    assert candidate.question_type == "multiple_choice"
    assert candidate.choices[1].key == "B"
    assert candidate.correct_choice == "B"
    assert candidate.generation_method == "ai_convert"
    assert "Convert the free-response source question" in (
        service.generator.prompts[0]
    )
    assert quality_service.calls[0]["source_question"] == source_question


def test_preview_convert_to_mcq_rejects_missing_question() -> None:
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([]),
        generator=FakeGenerator(mcq_payload()),
    )

    with pytest.raises(LookupError, match="Source question not found"):
        asyncio.run(
            service.preview_convert_to_mcq(source_question_id="missing")
        )


def test_preview_convert_to_mcq_rejects_existing_mcq() -> None:
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository(
            [make_source_question(question_type="multiple_choice")]
        ),
        generator=FakeGenerator(mcq_payload()),
    )

    with pytest.raises(ValueError, match="Only free_response"):
        asyncio.run(
            service.preview_convert_to_mcq(source_question_id="source-id")
        )


def test_save_convert_to_mcq_creates_new_question() -> None:
    source_question = make_source_question()
    repository = FakeQuestionRepository([source_question])
    service = QuestionGenerationService(
        question_repository=repository,
        generator=FakeGenerator(mcq_payload()),
    )

    saved = asyncio.run(
        service.save_convert_to_mcq(
            source_question_id="source-id",
            candidate=make_mcq_candidate(),
        )
    )

    assert saved.id == "converted-id"
    assert saved.question_type == "multiple_choice"
    assert repository.created_payload["source_question"] == source_question
    assert repository.created_payload["question_type"] == "multiple_choice"
    assert repository.created_payload["choices"][1]["is_correct"] is True
    assert repository.created_payload["correct_choice"] == "B"
    assert repository.created_payload["generation_method"] == "ai_convert"


def test_save_convert_to_mcq_rejects_quality_blocking_issue() -> None:
    source_question = make_source_question()
    repository = FakeQuestionRepository([source_question])
    service = QuestionGenerationService(
        question_repository=repository,
        generator=FakeGenerator(mcq_payload()),
        quality_service=FakeQualityService(
            QuestionQualityReport(
                blocking_issues=[
                    QualityIssue(
                        code="mcq_duplicate_choice_content",
                        message="Choice content must be distinct",
                        severity="error",
                        field="choices",
                    )
                ]
            )
        ),
    )

    with pytest.raises(ValueError, match="mcq_duplicate_choice_content"):
        asyncio.run(
            service.save_convert_to_mcq(
                source_question_id="source-id",
                candidate=make_mcq_candidate(),
            )
        )

    assert repository.created_payload is None
