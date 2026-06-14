from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from modules.question_classification import (
    ClassificationCandidate,
    ClassificationModelError,
    ClassificationValidationError,
    QuestionClassificationService,
)
from modules.question_classification.service import (
    _extract_formula_texts,
)
from modules.taxonomy import load_validated_taxonomy


class FakeClassifier:
    def __init__(
        self,
        candidate: ClassificationCandidate | None = None,
        error: Exception | None = None,
    ) -> None:
        self.candidate = candidate
        self.error = error
        self.prompts: list[str] = []

    def classify(
        self,
        prompt: str,
    ) -> ClassificationCandidate:
        self.prompts.append(prompt)

        if self.error is not None:
            raise self.error

        if self.candidate is None:
            raise AssertionError("Fake candidate was not configured")

        return self.candidate


def make_question(
    *,
    question_id: str = "question-1",
    statement: str = "Tính tích phân bằng phương pháp từng phần.",
    solution: str | None = None,
    answer: str | None = None,
    formulas: list[dict[str, str]] | None = None,
):
    return SimpleNamespace(
        id=question_id,
        statement=statement,
        solution=solution,
        answer=answer,
        formulas=formulas or [],
    )


def integration_by_parts_candidate(
    *,
    confidence: float = 0.95,
) -> ClassificationCandidate:
    return ClassificationCandidate(
        chapter_code="GT1_C2_Integral_Calculus_One_Variable",
        topic_code="GT1_C2_01_Indefinite_Integrals",
        problem_type_code=(
            "GT1_C2_01_T03_Integration_By_Parts"
        ),
        skills=[
            "integration_by_parts",
            "indefinite_integral",
        ],
        difficulty="medium",
        confidence=confidence,
        reason=(
            "Đề bài yêu cầu tính tích phân bằng phương pháp "
            "từng phần."
        ),
    )


def domain_candidate() -> ClassificationCandidate:
    return ClassificationCandidate(
        chapter_code=(
            "GT1_C1_Differential_Calculus_One_Variable"
        ),
        topic_code="GT1_C1_02_Function_Basics",
        problem_type_code="GT1_C1_02_T01_Domain_And_Range",
        skills=[
            "function_domain_range",
            "algebraic_transformation",
        ],
        difficulty="easy",
        confidence=0.96,
        reason="Đề bài yêu cầu tìm tập xác định của hàm số.",
    )


def make_service(
    classifier: FakeClassifier,
) -> QuestionClassificationService:
    taxonomy, taxonomy_index = load_validated_taxonomy()

    return QuestionClassificationService(
        classifier=classifier,
        taxonomy=taxonomy,
        taxonomy_index=taxonomy_index,
    )


def test_classify_integration_by_parts_question() -> None:
    classifier = FakeClassifier(
        integration_by_parts_candidate()
    )
    service = make_service(classifier)

    result = service.classify_question(
        make_question(
            statement=r"Tính $\int x\ln x\,dx$ bằng từng phần.",
            formulas=[
                {
                    "latex": r"\int x\ln x\,dx",
                    "normalized_latex": r"\int x\ln x\,dx",
                    "source": "statement",
                }
            ],
        )
    )

    assert result.chapter_code == (
        "GT1_C2_Integral_Calculus_One_Variable"
    )
    assert result.topic_code == (
        "GT1_C2_01_Indefinite_Integrals"
    )
    assert result.problem_type_code == (
        "GT1_C2_01_T03_Integration_By_Parts"
    )
    assert result.problem_type_name == "Tích phân từng phần"
    assert result.review_status == "auto_accept"
    assert len(classifier.prompts) == 1


def test_classify_domain_question() -> None:
    classifier = FakeClassifier(domain_candidate())
    service = make_service(classifier)

    result = service.classify_question(
        make_question(
            statement=r"Tìm tập xác định của $f(x)=\sqrt{x-1}$."
        )
    )

    assert result.topic_name == "Hàm số và các khái niệm cơ bản"
    assert result.problem_type_name == (
        "Tìm tập xác định, tập giá trị"
    )
    assert result.difficulty == "easy"


def test_service_builds_prompt_with_question_data() -> None:
    classifier = FakeClassifier(
        integration_by_parts_candidate()
    )
    service = make_service(classifier)

    service.classify_question(
        make_question(
            question_id="question-88",
            statement=r"Tính $\int x e^x dx$.",
            solution="Sử dụng công thức tích phân từng phần.",
            answer=r"(x-1)e^x+C",
            formulas=[
                {
                    "latex": r"\int x e^x dx",
                    "normalized_latex": r"\int x e^x dx",
                    "source": "statement",
                }
            ],
        )
    )

    prompt = classifier.prompts[0]

    assert "question-88" in prompt
    assert r"\\int x e^x dx" in prompt
    assert "Sử dụng công thức tích phân từng phần." in prompt
    assert r"(x-1)e^x+C" in prompt


def test_service_rejects_unknown_taxonomy_code() -> None:
    candidate = ClassificationCandidate(
        chapter_code="GT1_UNKNOWN_CHAPTER",
        topic_code="GT1_C2_01_Indefinite_Integrals",
        problem_type_code=(
            "GT1_C2_01_T03_Integration_By_Parts"
        ),
        skills=["integration_by_parts"],
        difficulty="medium",
        confidence=0.90,
        reason="Phân loại thử nghiệm.",
    )

    service = make_service(FakeClassifier(candidate))

    with pytest.raises(
        ClassificationValidationError,
    ) as exc_info:
        service.classify_question(make_question())

    assert any(
        issue.code == "unknown_chapter"
        for issue in exc_info.value.issues
    )


def test_low_confidence_result_requires_review() -> None:
    classifier = FakeClassifier(
        integration_by_parts_candidate(confidence=0.45)
    )
    service = make_service(classifier)

    result = service.classify_question(make_question())

    assert result.confidence == 0.45
    assert result.review_status == "mandatory_review"


def test_soft_review_confidence_result() -> None:
    classifier = FakeClassifier(
        integration_by_parts_candidate(confidence=0.65)
    )
    service = make_service(classifier)

    result = service.classify_question(make_question())

    assert result.review_status == "soft_review"


def test_service_rejects_blank_statement() -> None:
    classifier = FakeClassifier(
        integration_by_parts_candidate()
    )
    service = make_service(classifier)

    with pytest.raises(
        ValidationError,
        match="statement must not be blank",
    ):
        service.classify_question(
            make_question(statement="   ")
        )

    assert classifier.prompts == []


def test_service_rejects_empty_question_id() -> None:
    classifier = FakeClassifier(
        integration_by_parts_candidate()
    )
    service = make_service(classifier)

    with pytest.raises(ValidationError):
        service.classify_question(
            make_question(question_id="")
        )

    assert classifier.prompts == []


def test_service_propagates_classifier_error() -> None:
    classifier = FakeClassifier(
        error=ClassificationModelError(
            "Gemini service unavailable"
        )
    )
    service = make_service(classifier)

    with pytest.raises(
        ClassificationModelError,
        match="Gemini service unavailable",
    ):
        service.classify_question(make_question())

    assert len(classifier.prompts) == 1


def test_service_loads_default_taxonomy() -> None:
    classifier = FakeClassifier(domain_candidate())

    service = QuestionClassificationService(
        classifier=classifier,
    )

    result = service.classify_question(
        make_question(
            statement="Tìm tập xác định của hàm số."
        )
    )

    assert result.taxonomy_id == "calculus_1_hust_mi1111"
    assert result.taxonomy_version == "1.0.0"


def test_service_requires_taxonomy_and_index_together() -> None:
    taxonomy, _ = load_validated_taxonomy()
    classifier = FakeClassifier(domain_candidate())

    with pytest.raises(
        ValueError,
        match="must be provided together",
    ):
        QuestionClassificationService(
            classifier=classifier,
            taxonomy=taxonomy,
            taxonomy_index=None,
        )


def test_extract_formula_texts_prefers_normalized_latex() -> None:
    formulas = [
        {
            "latex": r"\frac{x}{2}",
            "normalized_latex": r"\frac{x}{2}",
            "source": "statement",
        }
    ]

    result = _extract_formula_texts(formulas)

    assert result == [r"\frac{x}{2}"]


def test_extract_formula_texts_falls_back_to_original_latex() -> None:
    formulas = [
        {
            "latex": r"\int x\,dx",
            "normalized_latex": "",
            "source": "statement",
        }
    ]

    result = _extract_formula_texts(formulas)

    assert result == [r"\int x\,dx"]


def test_extract_formula_texts_removes_duplicates() -> None:
    formulas = [
        {
            "latex": r"\lim_{x\to0}x",
            "normalized_latex": r"\lim_{x\to0}x",
            "source": "statement",
        },
        {
            "latex": r"\lim_{x\to0}x",
            "normalized_latex": r"\lim_{x\to0}x",
            "source": "solution",
        },
    ]

    result = _extract_formula_texts(formulas)

    assert result == [r"\lim_{x\to0}x"]


def test_extract_formula_texts_ignores_empty_formulas() -> None:
    formulas = [
        {
            "latex": "",
            "normalized_latex": "",
            "source": "statement",
        }
    ]

    assert _extract_formula_texts(formulas) == []