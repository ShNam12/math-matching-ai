import asyncio
from types import SimpleNamespace

from modules.question_generation.schemas import GeneratedQuestionCandidate
from modules.question_quality.service import QuestionQualityService
from modules.semantic_search.schemas import QuestionSearchResult

def make_question(statement="Tinh $x+1$."):
    return SimpleNamespace(
        id="source-id",
        document_id="document-id",
        statement=statement,
        solution=None,
        answer=None,
        subject="math",
        chapter="algebra",
        difficulty="medium",
        skills=["simplify"],
    )


def make_candidate(
    statement="Tinh $x+2$.",
    solution="Cong 2 vao x.",
    answer="$x+2$",
    difficulty="medium",
    formulas=None,
):
    return GeneratedQuestionCandidate(
        statement=statement,
        solution=solution,
        answer=answer,
        subject="math",
        chapter="algebra",
        difficulty=difficulty,
        skills=["simplify"],
        formulas=formulas if formulas is not None else [
            {
                "latex": "x+2",
                "normalized_latex": "x+2",
                "source": "statement",
            }
        ],
        quality_warnings=[],
    )

class FakeSemanticSearchService:
    def __init__(self, results) -> None:
        self.results = results
        self.calls = []

    async def search_questions(self, *, query: str, limit: int = 10, filters=None):
        self.calls.append(
            {
                "query": query,
                "limit": limit,
                "filters": filters,
            }
        )
        return self.results
    
def make_search_result(
    *,
    question_id="similar-id",
    document_id="document-id",
    score=0.95,
    statement="Tinh $x+3$.",
):
    return QuestionSearchResult(
        question_id=question_id,
        document_id=document_id,
        score=score,
        marker="Bai",
        marker_number="2",
        statement=statement,
        solution=None,
        answer=None,
        subject="math",
        chapter="algebra",
        difficulty="medium",
        skills=["simplify"],
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


def test_assess_candidate_allows_valid_candidate() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate()

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
            requested_difficulty="medium",
        )
    )

    assert report.can_save is True
    assert report.blocking_issues == []
    assert report.quality_warnings == []


def test_assess_candidate_blocks_exact_duplicate_statement() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate(statement="  Tinh   $x+1$.  ")

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert report.can_save is False
    assert "exact_duplicate_statement" in report.quality_warnings


def test_assess_candidate_blocks_invalid_formula_payload() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate(
        formulas=[
            {
                "latex": "",
                "normalized_latex": "x+2",
                "source": "statement",
            }
        ]
    )

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert report.can_save is False
    assert "invalid_formula_payload" in report.quality_warnings


def test_assess_candidate_warns_missing_solution_and_answer() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate(solution=None, answer=None)

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert report.can_save is True
    assert "missing_solution" in report.quality_warnings
    assert "missing_answer" in report.quality_warnings


def test_assess_candidate_warns_difficulty_mismatch() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate(difficulty="hard")

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
            requested_difficulty="medium",
        )
    )

    assert report.can_save is True
    assert "difficulty_mismatch" in report.quality_warnings
    
def test_assess_candidate_warns_semantic_duplicate() -> None:
    semantic_service = FakeSemanticSearchService(
        [
            make_search_result(
                question_id="similar-id",
                score=0.95,
                statement="Tinh $x+3$.",
            )
        ]
    )
    service = QuestionQualityService(
        semantic_search_service=semantic_service,
        semantic_duplicate_threshold=0.92,
    )
    source_question = make_question()
    candidate = make_candidate()

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert report.can_save is True
    assert "semantic_duplicate_candidate" in report.quality_warnings
    assert len(report.semantic_duplicates) == 1
    assert report.semantic_duplicates[0].question_id == "similar-id"
    assert semantic_service.calls[0]["query"] == candidate.statement
    assert semantic_service.calls[0]["limit"] == 5
    assert semantic_service.calls[0]["filters"].subject == "math"
    assert semantic_service.calls[0]["filters"].chapter == "algebra"
    assert semantic_service.calls[0]["filters"].difficulty == "medium"


def test_assess_candidate_ignores_semantic_duplicate_below_threshold() -> None:
    semantic_service = FakeSemanticSearchService(
        [
            make_search_result(
                question_id="similar-id",
                score=0.80,
            )
        ]
    )
    service = QuestionQualityService(
        semantic_search_service=semantic_service,
        semantic_duplicate_threshold=0.92,
    )
    source_question = make_question()
    candidate = make_candidate()

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert report.can_save is True
    assert "semantic_duplicate_candidate" not in report.quality_warnings
    assert report.semantic_duplicates == []


def test_assess_candidate_ignores_source_question_semantic_hit() -> None:
    semantic_service = FakeSemanticSearchService(
        [
            make_search_result(
                question_id="source-id",
                score=0.99,
            )
        ]
    )
    service = QuestionQualityService(
        semantic_search_service=semantic_service,
        semantic_duplicate_threshold=0.92,
    )
    source_question = make_question()
    candidate = make_candidate()

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert report.can_save is True
    assert "semantic_duplicate_candidate" not in report.quality_warnings
    assert report.semantic_duplicates == []