import asyncio
import json
from types import SimpleNamespace

import pytest

from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    GenerationConstraints,
)

from modules.question_generation.service import (
    QuestionGenerationService,
    _loads_generation_json,
    _normalize_for_duplicate_check,
)


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
            id="generated-id",
            document_id=source_question.document_id,
            sequence_number=2,
            marker="Generated",
            marker_number="2",
            statement=kwargs["statement"],
            solution=kwargs["solution"],
            answer=kwargs["answer"],
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

        if isinstance(self.payload, str):
            return self.payload

        return json.dumps(self.payload)


def make_question():
    return SimpleNamespace(
        id="source-id",
        document_id="document-id",
        marker="Bai",
        marker_number="28",
        statement="Tinh $(1+i\\sqrt{3})^{9}$.",
        solution=None,
        answer=None,
        subject="complex",
        chapter="complex-number",
        difficulty="medium",
        skills=["complex-power"],
    )


def test_normalize_for_duplicate_check() -> None:
    assert _normalize_for_duplicate_check("   Tinh   $x+1$  ") == "tinh $x+1$"


def test_loads_generation_json_accepts_plain_json() -> None:
    payload = _loads_generation_json('{"items": []}')

    assert payload == {"items": []}


def test_loads_generation_json_accepts_markdown_fenced_json() -> None:
    payload = _loads_generation_json(
        """
```json
{"items": []}
```
"""
    )
    assert payload == {"items": []}


def test_preview_questions_returns_candidates_with_extracted_formulas() -> None:
    question = make_question()
    repository = FakeQuestionRepository([question])
    generator = FakeGenerator(
        {
            "items": [
                {
                    "statement": "Tinh $(1-i\\sqrt{3})^{6}$.",
                    "solution": "Doi sang dang luong giac.",
                    "answer": "$-64$",
                    "difficulty": "medium",
                    "skills": ["complex-power"],
                }
            ]
        }
    )
    service = QuestionGenerationService(
        question_repository=repository,
        generator=generator,
    )

    preview = asyncio.run(
        service.preview_questions(
            source_question_id="source-id",
            generation_count=1,
            constraints=GenerationConstraints(),
        )
    )

    assert preview.source_question_id == "source-id"
    assert len(preview.candidates) == 1
    assert preview.candidates[0].statement == "Tinh $(1-i\\sqrt{3})^{6}$."
    assert preview.candidates[0].formulas[0]["normalized_latex"] == (
        "(1-i\\sqrt{3})^{6}"
    )
    assert preview.candidates[0].quality_warnings == []
    assert generator.prompts


def test_preview_questions_rejects_unknown_source_question() -> None:
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([]),
        generator=FakeGenerator({"items": []}),
    )

    with pytest.raises(ValueError, match="Source question not found"):
        asyncio.run(
            service.preview_questions(source_question_id="missing")
        )


def test_preview_questions_rejects_invalid_generation_count() -> None:
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([make_question()]),
        generator=FakeGenerator({"items": []}),
    )

    with pytest.raises(ValueError, match="Generation count"):
        asyncio.run(
            service.preview_questions(
                source_question_id="source-id",
                generation_count=20,
            )
        )


def test_preview_questions_rejects_missing_items_list() -> None:
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([make_question()]),
        generator=FakeGenerator({"wrong": []}),
    )

    with pytest.raises(ValueError, match="items list"):
        asyncio.run(
            service.preview_questions(source_question_id="source-id")
        )


def test_preview_questions_rejects_empty_statement() -> None:
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([make_question()]),
        generator=FakeGenerator(
            {
                "items": [
                    {
                        "statement": " ",
                        "solution": None,
                        "answer": None,
                        "difficulty": "medium",
                        "skills": [],
                    }
                ]
            }
        ),
    )

    with pytest.raises(ValueError, match="statement"):
        asyncio.run(
            service.preview_questions(source_question_id="source-id")
        )


def test_preview_questions_marks_duplicate_statement() -> None:
    question = make_question()
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator(
            {
                "items": [
                    {
                        "statement": " Tinh $(1+i\\sqrt{3})^{9}$. ",
                        "solution": None,
                        "answer": None,
                        "difficulty": "medium",
                        "skills": ["complex-power"],
                    }
                ]
            }
        ),
    )

    preview = asyncio.run(
        service.preview_questions(
            source_question_id="source-id",
            generation_count=1,
        )
    )

    assert preview.candidates[0].quality_warnings == [
        "duplicate_statement",
        "review_required",
    ]


def test_preview_questions_marks_no_formula_detected() -> None:
    question = make_question()
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator(
            {
                "items": [
                    {
                        "statement": "Neu khai niem so phuc lien hop.",
                        "solution": None,
                        "answer": None,
                        "difficulty": None,
                        "skills": [],
                    }
                ]
            }
        ),
    )

    preview = asyncio.run(
        service.preview_questions(
            source_question_id="source-id",
            generation_count=1,
        )
    )

    assert preview.candidates[0].quality_warnings == ["no_formula_detected"]


def test_preview_questions_limits_items_to_generation_count() -> None:
    question = make_question()
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator(
            {
                "items": [
                    {
                        "statement": "Tinh $x+1$.",
                        "solution": None,
                        "answer": None,
                        "difficulty": "easy",
                        "skills": [],
                    },
                    {
                        "statement": "Tinh $x+2$.",
                        "solution": None,
                        "answer": None,
                        "difficulty": "easy",
                        "skills": [],
                    },
                ]
            }
        ),
    )

    preview = asyncio.run(
        service.preview_questions(
            source_question_id="source-id",
            generation_count=1,
        )
    )

    assert len(preview.candidates) == 1
    assert preview.candidates[0].statement == "Tinh $x+1$."

def make_candidate(statement="Tinh $x+1$."):
    return GeneratedQuestionCandidate(
        statement=statement,
        solution="Cong them 1 vao x.",
        answer="$x+1$",
        subject="algebra",
        chapter="expression",
        difficulty="easy",
        skills=["simplify"],
        formulas=[
            {
                "latex": "x+1",
                "normalized_latex": "x+1",
                "source": "statement",
            }
        ],
        quality_warnings=[],
    )


def test_save_generated_question_creates_question() -> None:
    question = make_question()
    repository = FakeQuestionRepository([question])
    service = QuestionGenerationService(
        question_repository=repository,
        generator=FakeGenerator({"items": []}),
    )

    saved = asyncio.run(
        service.save_generated_question(
            source_question_id="source-id",
            candidate=make_candidate(),
        )
    )

    assert saved.id == "generated-id"
    assert saved.document_id == "document-id"
    assert saved.marker == "Generated"
    assert saved.embedding_status == "pending"
    assert repository.created_payload["source_question"] == question
    assert repository.created_payload["statement"] == "Tinh $x+1$."
    assert repository.created_payload["solution"] == "Cong them 1 vao x."
    assert repository.created_payload["answer"] == "$x+1$"
    assert repository.created_payload["formulas"][0]["normalized_latex"] == "x+1"


def test_save_generated_question_rejects_unknown_source_question() -> None:
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([]),
        generator=FakeGenerator({"items": []}),
    )

    with pytest.raises(ValueError, match="Source question not found"):
        asyncio.run(
            service.save_generated_question(
                source_question_id="missing",
                candidate=make_candidate(),
            )
        )


def test_save_generated_question_rejects_duplicate_statement() -> None:
    question = make_question()
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator({"items": []}),
    )

    with pytest.raises(ValueError, match="duplicates"):
        asyncio.run(
            service.save_generated_question(
                source_question_id="source-id",
                candidate=make_candidate(statement=question.statement),
            )
        )