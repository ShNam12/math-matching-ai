from types import SimpleNamespace

from modules.question_quality import TaxonomyClassificationQualityService
from modules.taxonomy import load_validated_taxonomy


def make_question(**overrides):
    data = {
        "id": "question-id",
        "classification_status": "completed",
        "chapter_code": "GT1_C1_Differential_Calculus_One_Variable",
        "topic_code": "GT1_C1_08_Derivatives_Differentials",
        "problem_type_code": "GT1_C1_08_T01_Basic_Derivative",
        "taxonomy_confidence": 0.95,
        "skills": ["derivative_computation"],
        "difficulty": "easy",
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_service():
    taxonomy, index = load_validated_taxonomy()
    return TaxonomyClassificationQualityService(
        taxonomy=taxonomy,
        index=index,
    )


def issue_codes(report):
    return {
        issue.code
        for issue in [*report.blocking_issues, *report.warnings]
    }


def test_missing_classification_is_flagged():
    service = make_service()

    report = service.assess_question(
        make_question(
            classification_status="pending",
            chapter_code=None,
            topic_code=None,
            problem_type_code=None,
        )
    )

    assert "missing_classification" in issue_codes(report)
    assert "missing_taxonomy_code" in issue_codes(report)
    assert report.can_accept is False


def test_low_confidence_is_warning():
    service = make_service()

    report = service.assess_question(
        make_question(taxonomy_confidence=0.5)
    )

    assert "low_confidence" in issue_codes(report)
    assert report.can_accept is True


def test_invalid_taxonomy_code_is_error():
    service = make_service()

    report = service.assess_question(
        make_question(chapter_code="INVALID")
    )

    assert "invalid_chapter_code" in issue_codes(report)
    assert report.can_accept is False


def test_problem_type_topic_mismatch_is_error():
    service = make_service()

    report = service.assess_question(
        make_question(
            problem_type_code="GT1_C1_02_T01_Domain_And_Range"
        )
    )

    assert "problem_type_topic_mismatch" in issue_codes(report)
    assert report.can_accept is False


def test_invalid_difficulty_is_error():
    service = make_service()

    report = service.assess_question(
        make_question(difficulty="very_hard")
    )

    assert "invalid_difficulty" in issue_codes(report)
    assert report.can_accept is False


def test_missing_skills_is_warning():
    service = make_service()

    report = service.assess_question(
        make_question(skills=[])
    )

    assert "missing_skills" in issue_codes(report)
    assert report.can_accept is True