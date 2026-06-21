import asyncio
import json
from types import SimpleNamespace

import pytest

from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    GenerationConstraints,
    MultipleChoiceOption,
)
from modules.question_quality.schemas import (
    QualityIssue,
    QuestionQualityReport,
    QuestionValidationReport,
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


class FakeQualityService:
    def __init__(
        self,
        report: QuestionQualityReport | None = None,
    ) -> None:
        self.report = report or QuestionQualityReport()
        self.calls = []

    async def assess_candidate(self, **kwargs):
        self.calls.append(kwargs)
        return self.report


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

    assert "exact_duplicate_statement" in preview.candidates[0].quality_warnings
    assert "missing_solution" in preview.candidates[0].quality_warnings
    assert "missing_answer" in preview.candidates[0].quality_warnings


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

    assert "no_formula_detected" in preview.candidates[0].quality_warnings
    assert "missing_solution" in preview.candidates[0].quality_warnings
    assert "missing_answer" in preview.candidates[0].quality_warnings


def test_preview_questions_returns_mcq_quality_report() -> None:
    question = make_question()
    quality_service = FakeQualityService(
        QuestionQualityReport(
            warnings=[
                QualityIssue(
                    code="solver_not_available",
                    message="No solver is available for this candidate",
                    severity="warning",
                    field="solver_code",
                )
            ]
        )
    )
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator(
            {
                "items": [
                    {
                        "statement": "Tinh $1+1$.",
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
                        "generation_method": "ai_symbolic",
                        "solver_code": "ADD_INT",
                    }
                ]
            }
        ),
        quality_service=quality_service,
    )

    preview = asyncio.run(
        service.preview_questions(
            source_question_id="source-id",
            generation_count=1,
        )
    )
    candidate = preview.candidates[0]

    assert candidate.question_type == "multiple_choice"
    assert candidate.choices[1].key == "B"
    assert candidate.correct_choice == "B"
    assert candidate.quality_warnings == ["solver_not_available"]
    assert candidate.validation_report.can_save is True
    assert candidate.validation_report.warnings[0].code == "solver_not_available"


def test_preview_questions_parses_fenced_mcq_output() -> None:
    question = make_question()
    raw_output = """
```json
{
  "items": [
    {
      "statement": "Tinh $1+1$.",
      "solution": "$1+1=2$.",
      "question_type": "multiple_choice",
      "choices": [
        {"key": "a", "text": "$1$", "latex": "1"},
        {"key": "b", "text": "$2$", "latex": "2", "is_correct": true},
        {"key": "c", "text": "$3$", "latex": "3"},
        {"key": "d", "text": "$4$", "latex": "4"}
      ],
      "generation_method": "ai"
    }
  ]
}
```
"""
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator(raw_output),
        quality_service=FakeQualityService(),
    )

    preview = asyncio.run(
        service.preview_questions(
            source_question_id="source-id",
            generation_count=1,
        )
    )
    candidate = preview.candidates[0]

    assert candidate.question_type == "multiple_choice"
    assert [choice.key for choice in candidate.choices] == ["A", "B", "C", "D"]
    assert candidate.correct_choice == "B"
    assert candidate.answer == "2"
    assert candidate.generation_method == "ai"
    assert any(
        formula["source"] == "choice"
        and formula["normalized_latex"] == "2"
        for formula in candidate.formulas
    )


def test_preview_questions_uses_correct_choice_answer_when_answer_missing() -> None:
    question = make_question()
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator(
            {
                "items": [
                    {
                        "statement": "Tinh $2+2$.",
                        "solution": "$2+2=4$.",
                        "question_type": "multiple_choice",
                        "choices": [
                            {"key": "A", "text": "3"},
                            {
                                "key": "B",
                                "text": "4",
                                "latex": "4",
                                "is_correct": True,
                            },
                            {"key": "C", "text": "5"},
                            {"key": "D", "text": "6"},
                        ],
                        "correct_choice": "b",
                    }
                ]
            }
        ),
        quality_service=FakeQualityService(),
    )

    preview = asyncio.run(
        service.preview_questions(
            source_question_id="source-id",
            generation_count=1,
        )
    )
    candidate = preview.candidates[0]

    assert candidate.correct_choice == "B"
    assert candidate.answer == "4"


def test_preview_questions_missing_choices_returns_quality_report() -> None:
    question = make_question()
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator(
            {
                "items": [
                    {
                        "statement": "Tinh $2+2$.",
                        "solution": "$2+2=4$.",
                        "answer": "4",
                        "question_type": "multiple_choice",
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
    candidate = preview.candidates[0]

    assert candidate.question_type == "multiple_choice"
    assert candidate.choices == []
    assert "mcq_missing_choices" in candidate.quality_warnings
    assert candidate.validation_report.can_save is False


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
    assert repository.created_payload["question_type"] == "free_response"
    assert repository.created_payload["choices"] == []
    assert repository.created_payload["correct_choice"] is None
    assert repository.created_payload["validation_report"]["can_save"] is True


def make_mcq_candidate() -> GeneratedQuestionCandidate:
    return GeneratedQuestionCandidate(
        statement="Tinh $1+1$.",
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
            MultipleChoiceOption(
                key="A",
                text="1",
                distractor_type="off_by_one",
                rationale="Cong thieu 1.",
            ),
            MultipleChoiceOption(key="B", text="2", is_correct=True),
            MultipleChoiceOption(key="C", text="3"),
            MultipleChoiceOption(key="D", text="4"),
        ],
        correct_choice="B",
        generation_method="ai_symbolic",
        solver_code="ADD_INT",
        validation_report=QuestionValidationReport(),
    )


def test_save_generated_question_passes_mcq_fields_to_repository() -> None:
    question = make_question()
    repository = FakeQuestionRepository([question])
    service = QuestionGenerationService(
        question_repository=repository,
        generator=FakeGenerator({"items": []}),
    )
    candidate = make_mcq_candidate()

    asyncio.run(
        service.save_generated_question(
            source_question_id="source-id",
            candidate=candidate,
        )
    )

    assert repository.created_payload["question_type"] == "multiple_choice"
    assert repository.created_payload["choices"][1]["key"] == "B"
    assert repository.created_payload["choices"][1]["is_correct"] is True
    assert repository.created_payload["correct_choice"] == "B"
    assert repository.created_payload["generation_method"] == "ai_symbolic"
    assert repository.created_payload["solver_code"] == "ADD_INT"
    assert repository.created_payload["distractor_metadata"] == {
        "distractors": [
            {
                "key": "A",
                "distractor_type": "off_by_one",
                "rationale": "Cong thieu 1.",
                "metadata": {},
            },
            {
                "key": "C",
                "distractor_type": None,
                "rationale": None,
                "metadata": {},
            },
            {
                "key": "D",
                "distractor_type": None,
                "rationale": None,
                "metadata": {},
            },
        ],
    }


def test_save_generated_question_stores_fresh_quality_report() -> None:
    question = make_question()
    repository = FakeQuestionRepository([question])
    service = QuestionGenerationService(
        question_repository=repository,
        generator=FakeGenerator({"items": []}),
        quality_service=FakeQualityService(
            QuestionQualityReport(
                warnings=[
                    QualityIssue(
                        code="solver_not_available",
                        message="No solver is available for this candidate",
                        severity="warning",
                        field="solver_code",
                    )
                ]
            )
        ),
    )

    asyncio.run(
        service.save_generated_question(
            source_question_id="source-id",
            candidate=make_mcq_candidate(),
        )
    )

    validation_report = repository.created_payload["validation_report"]
    assert validation_report["can_save"] is True
    assert validation_report["warnings"][0]["code"] == "solver_not_available"
    assert validation_report["warnings"][0]["field"] == "solver_code"


def test_save_generated_question_rejects_duplicate_mcq_choice() -> None:
    question = make_question()
    repository = FakeQuestionRepository([question])
    service = QuestionGenerationService(
        question_repository=repository,
        generator=FakeGenerator({"items": []}),
    )
    candidate = GeneratedQuestionCandidate(
        statement="Tinh $1+1$.",
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
            MultipleChoiceOption(key="A", text="2"),
            MultipleChoiceOption(key="B", text="2", is_correct=True),
            MultipleChoiceOption(key="C", text="3"),
            MultipleChoiceOption(key="D", text="4"),
        ],
        correct_choice="B",
    )

    with pytest.raises(ValueError, match="failed quality checks") as exc_info:
        asyncio.run(
            service.save_generated_question(
                source_question_id="source-id",
                candidate=candidate,
            )
        )

    assert "mcq_duplicate_choice_content" in str(exc_info.value)
    assert repository.created_payload is None


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

    with pytest.raises(ValueError, match="failed quality checks") as exc_info:
        asyncio.run(
            service.save_generated_question(
                source_question_id="source-id",
                candidate=make_candidate(statement=question.statement),
            )
        )

    assert "exact_duplicate_statement" in str(exc_info.value)
def test_save_generated_question_rejects_invalid_formula_payload() -> None:
    question = make_question()
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator({"items": []}),
    )

    candidate = make_candidate()
    invalid_candidate = GeneratedQuestionCandidate(
        statement=candidate.statement,
        solution=candidate.solution,
        answer=candidate.answer,
        subject=candidate.subject,
        chapter=candidate.chapter,
        difficulty=candidate.difficulty,
        skills=candidate.skills,
        formulas=[
            {
                "latex": "",
                "normalized_latex": "x+1",
                "source": "statement",
            }
        ],
        quality_warnings=[],
    )

    with pytest.raises(ValueError, match="failed quality checks") as exc_info:
        asyncio.run(
            service.save_generated_question(
                source_question_id="source-id",
                candidate=invalid_candidate,
            )
        )

    assert "invalid_formula_payload" in str(exc_info.value)
