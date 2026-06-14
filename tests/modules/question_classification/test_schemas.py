import pytest
from pydantic import ValidationError

from modules.question_classification import (
    ClassificationCandidate,
    ClassificationIssue,
    QuestionClassificationRequest,
)


def valid_candidate_data() -> dict:
    return {
        "chapter_code": "GT1_C1_Differential_Calculus_One_Variable",
        "topic_code": "GT1_C1_05_Function_Limits",
        "problem_type_code": (
            "GT1_C1_05_T02_Algebraic_Transformation_Limit"
        ),
        "skills": [
            "function_limit",
            "algebraic_transformation",
        ],
        "difficulty": "medium",
        "confidence": 0.88,
        "reason": "Câu hỏi yêu cầu tính giới hạn bằng biến đổi đại số.",
    }


def test_classification_request_accepts_valid_data() -> None:
    request = QuestionClassificationRequest(
        question_id="question-1",
        statement="Tính giới hạn của biểu thức khi x tiến tới 0.",
        formulas=[r"\lim_{x\to0}\frac{\sqrt{1+x}-1}{x}"],
    )

    assert request.question_id == "question-1"
    assert request.statement == (
        "Tính giới hạn của biểu thức khi x tiến tới 0."
    )
    assert len(request.formulas) == 1


def test_classification_request_strips_statement() -> None:
    request = QuestionClassificationRequest(
        question_id="question-1",
        statement="  Tính đạo hàm của hàm số.  ",
    )

    assert request.statement == "Tính đạo hàm của hàm số."


def test_classification_request_rejects_blank_statement() -> None:
    with pytest.raises(ValidationError, match="statement must not be blank"):
        QuestionClassificationRequest(
            question_id="question-1",
            statement="   ",
        )


def test_classification_request_rejects_empty_question_id() -> None:
    with pytest.raises(ValidationError):
        QuestionClassificationRequest(
            question_id="",
            statement="Tính giới hạn.",
        )


def test_candidate_accepts_valid_data() -> None:
    candidate = ClassificationCandidate(**valid_candidate_data())

    assert candidate.difficulty == "medium"
    assert candidate.confidence == 0.88
    assert candidate.skills == [
        "function_limit",
        "algebraic_transformation",
    ]


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_candidate_rejects_invalid_confidence(
    confidence: float,
) -> None:
    data = valid_candidate_data()
    data["confidence"] = confidence

    with pytest.raises(ValidationError):
        ClassificationCandidate(**data)


def test_candidate_accepts_confidence_boundaries() -> None:
    lower_data = valid_candidate_data()
    lower_data["confidence"] = 0

    upper_data = valid_candidate_data()
    upper_data["confidence"] = 1

    lower = ClassificationCandidate(**lower_data)
    upper = ClassificationCandidate(**upper_data)

    assert lower.confidence == 0
    assert upper.confidence == 1


def test_candidate_rejects_invalid_difficulty() -> None:
    data = valid_candidate_data()
    data["difficulty"] = "very_hard"

    with pytest.raises(ValidationError):
        ClassificationCandidate(**data)


def test_candidate_rejects_empty_skills() -> None:
    data = valid_candidate_data()
    data["skills"] = []

    with pytest.raises(ValidationError):
        ClassificationCandidate(**data)


def test_candidate_strips_reason() -> None:
    data = valid_candidate_data()
    data["reason"] = "  Nhận diện theo phương pháp biến đổi đại số.  "

    candidate = ClassificationCandidate(**data)

    assert candidate.reason == (
        "Nhận diện theo phương pháp biến đổi đại số."
    )


def test_candidate_rejects_blank_reason() -> None:
    data = valid_candidate_data()
    data["reason"] = "   "

    with pytest.raises(ValidationError, match="reason must not be blank"):
        ClassificationCandidate(**data)


def test_candidate_rejects_extra_field() -> None:
    data = valid_candidate_data()
    data["unexpected_field"] = "not allowed"

    with pytest.raises(ValidationError):
        ClassificationCandidate(**data)


def test_classification_issue_accepts_valid_data() -> None:
    issue = ClassificationIssue(
        code="unknown_topic",
        field="topic_code",
        message="Unknown topic code",
    )

    assert issue.code == "unknown_topic"
    assert issue.field == "topic_code"