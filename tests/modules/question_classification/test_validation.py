import pytest

from modules.question_classification import (
    ClassificationCandidate,
    ClassificationValidationError,
    validate_classification,
)
from modules.taxonomy import load_validated_taxonomy


VALID_CHAPTER = "GT1_C1_Differential_Calculus_One_Variable"
VALID_TOPIC = "GT1_C1_05_Function_Limits"
VALID_PROBLEM_TYPE = (
    "GT1_C1_05_T02_Algebraic_Transformation_Limit"
)


@pytest.fixture(scope="module")
def taxonomy_context():
    return load_validated_taxonomy()


def create_candidate(
    *,
    chapter_code: str = VALID_CHAPTER,
    topic_code: str = VALID_TOPIC,
    problem_type_code: str = VALID_PROBLEM_TYPE,
    skills: list[str] | None = None,
    difficulty: str = "medium",
    confidence: float = 0.88,
) -> ClassificationCandidate:
    return ClassificationCandidate(
        chapter_code=chapter_code,
        topic_code=topic_code,
        problem_type_code=problem_type_code,
        skills=skills or [
            "function_limit",
            "algebraic_transformation",
        ],
        difficulty=difficulty,
        confidence=confidence,
        reason="Câu hỏi yêu cầu tính giới hạn bằng biến đổi đại số.",
    )


def get_issue_codes(error: ClassificationValidationError) -> set[str]:
    return {issue.code for issue in error.issues}


def test_validate_classification_accepts_valid_candidate(
    taxonomy_context,
) -> None:
    taxonomy, index = taxonomy_context
    candidate = create_candidate()

    result = validate_classification(candidate, taxonomy, index)

    assert result.chapter_code == VALID_CHAPTER
    assert result.topic_code == VALID_TOPIC
    assert result.problem_type_code == VALID_PROBLEM_TYPE
    assert result.chapter_name == (
        "Chương 1: Phép tính vi phân hàm một biến số"
    )
    assert result.topic_name == "Giới hạn hàm số"
    assert result.problem_type_name == (
        "Tính giới hạn bằng biến đổi đại số"
    )
    assert result.subject_code == "CALCULUS_1"
    assert result.subject_name == "Giải tích 1"
    assert result.taxonomy_id == "calculus_1_hust_mi1111"
    assert result.taxonomy_version == "1.0.0"
    assert result.review_status == "auto_accept"


def test_validator_rejects_unknown_chapter(
    taxonomy_context,
) -> None:
    taxonomy, index = taxonomy_context
    candidate = create_candidate(
        chapter_code="GT1_UNKNOWN_CHAPTER",
    )

    with pytest.raises(ClassificationValidationError) as exc_info:
        validate_classification(candidate, taxonomy, index)

    assert "unknown_chapter" in get_issue_codes(exc_info.value)


def test_validator_rejects_unknown_topic(
    taxonomy_context,
) -> None:
    taxonomy, index = taxonomy_context
    candidate = create_candidate(
        topic_code="GT1_UNKNOWN_TOPIC",
    )

    with pytest.raises(ClassificationValidationError) as exc_info:
        validate_classification(candidate, taxonomy, index)

    assert "unknown_topic" in get_issue_codes(exc_info.value)


def test_validator_rejects_unknown_problem_type(
    taxonomy_context,
) -> None:
    taxonomy, index = taxonomy_context
    candidate = create_candidate(
        problem_type_code="GT1_UNKNOWN_PROBLEM_TYPE",
    )

    with pytest.raises(ClassificationValidationError) as exc_info:
        validate_classification(candidate, taxonomy, index)

    assert "unknown_problem_type" in get_issue_codes(exc_info.value)


def test_validator_rejects_topic_from_different_chapter(
    taxonomy_context,
) -> None:
    taxonomy, index = taxonomy_context
    candidate = create_candidate(
        chapter_code="GT1_C2_Integral_Calculus_One_Variable",
        topic_code=VALID_TOPIC,
        problem_type_code=VALID_PROBLEM_TYPE,
    )

    with pytest.raises(ClassificationValidationError) as exc_info:
        validate_classification(candidate, taxonomy, index)

    assert "topic_parent_mismatch" in get_issue_codes(exc_info.value)


def test_validator_rejects_problem_type_from_different_topic(
    taxonomy_context,
) -> None:
    taxonomy, index = taxonomy_context
    candidate = create_candidate(
        topic_code="GT1_C1_08_Derivatives_Differentials",
        problem_type_code=VALID_PROBLEM_TYPE,
    )

    with pytest.raises(ClassificationValidationError) as exc_info:
        validate_classification(candidate, taxonomy, index)

    assert (
        "problem_type_parent_mismatch"
        in get_issue_codes(exc_info.value)
    )


def test_validator_rejects_unknown_skill(
    taxonomy_context,
) -> None:
    taxonomy, index = taxonomy_context
    candidate = create_candidate(
        skills=["function_limit", "unknown_skill"],
    )

    with pytest.raises(ClassificationValidationError) as exc_info:
        validate_classification(candidate, taxonomy, index)

    error = exc_info.value

    assert "unknown_skill" in get_issue_codes(error)
    assert any(
        issue.field == "skills"
        and "unknown_skill" in issue.message
        for issue in error.issues
    )


@pytest.mark.parametrize(
    ("confidence", "expected_status"),
    [
        (1.00, "auto_accept"),
        (0.75, "auto_accept"),
        (0.74, "soft_review"),
        (0.60, "soft_review"),
        (0.59, "mandatory_review"),
        (0.00, "mandatory_review"),
    ],
)
def test_validator_assigns_review_status_from_confidence(
    taxonomy_context,
    confidence: float,
    expected_status: str,
) -> None:
    taxonomy, index = taxonomy_context
    candidate = create_candidate(confidence=confidence)

    result = validate_classification(candidate, taxonomy, index)

    assert result.review_status == expected_status


def test_validator_preserves_candidate_data(
    taxonomy_context,
) -> None:
    taxonomy, index = taxonomy_context
    candidate = create_candidate(
        skills=["function_limit", "algebraic_transformation"],
        difficulty="hard",
        confidence=0.95,
    )

    result = validate_classification(candidate, taxonomy, index)

    assert result.skills == candidate.skills
    assert result.difficulty == "hard"
    assert result.confidence == 0.95
    assert result.reason == candidate.reason


def test_validator_collects_multiple_issues(
    taxonomy_context,
) -> None:
    taxonomy, index = taxonomy_context
    candidate = create_candidate(
        chapter_code="GT1_UNKNOWN_CHAPTER",
        topic_code="GT1_UNKNOWN_TOPIC",
        problem_type_code="GT1_UNKNOWN_PROBLEM_TYPE",
        skills=["unknown_skill"],
    )

    with pytest.raises(ClassificationValidationError) as exc_info:
        validate_classification(candidate, taxonomy, index)

    assert get_issue_codes(exc_info.value) == {
        "unknown_chapter",
        "unknown_topic",
        "unknown_problem_type",
        "unknown_skill",
    }