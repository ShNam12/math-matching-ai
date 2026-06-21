from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.models.analytics import AnalyticsSummaryResponse
from infra.db.models import Document, Question
from infra.db.session import get_db_session


router = APIRouter(prefix="/analytics", tags=["analytics"])


DISTRACTOR_ISSUE_CODES = {
    "mcq_duplicate_choice_content",
    "mcq_distractor_equals_correct_answer",
    "mcq_all_choices_too_similar",
    "symbolic_distractor_equals_correct",
    "symbolic_distractor_duplicate",
}

CORRECT_ANSWER_ISSUE_CODES = {
    "mcq_missing_correct_choice",
    "mcq_correct_choice_not_found",
    "mcq_multiple_correct_choices",
    "mcq_no_correct_choice_flagged",
    "symbolic_correct_answer_mismatch",
}

SOLVER_UNAVAILABLE_CODES = {
    "solver_not_available",
}


def _issue_code(issue: object) -> str | None:
    if isinstance(issue, dict):
        code = issue.get("code")
        return str(code) if code else None

    if isinstance(issue, str):
        return issue

    return None


def _validation_issues(report: object, key: str) -> list[object]:
    if not isinstance(report, dict):
        return []

    value = report.get(key)
    return value if isinstance(value, list) else []


def _has_distractor_issue(report: object) -> bool:
    return _has_issue_code(report, DISTRACTOR_ISSUE_CODES)


def _has_correct_answer_issue(report: object) -> bool:
    return _has_issue_code(report, CORRECT_ANSWER_ISSUE_CODES)


def _has_solver_unavailable_issue(report: object) -> bool:
    return _has_issue_code(report, SOLVER_UNAVAILABLE_CODES)


def _has_warning(report: object) -> bool:
    return bool(_validation_issues(report, "warnings"))


def _has_issue_code(report: object, issue_codes: set[str]) -> bool:
    issues = [
        *_validation_issues(report, "warnings"),
        *_validation_issues(report, "blocking_issues"),
        *_validation_issues(report, "symbolic_checks"),
    ]

    return any(
        (code := _issue_code(issue)) in issue_codes
        for issue in issues
    )


def _has_symbolic_validation(
    *,
    solver_code: str | None,
    validation_report: object,
) -> bool:
    if solver_code:
        return True

    symbolic_checks = _validation_issues(
        validation_report,
        "symbolic_checks",
    )

    return any(
        bool(code := _issue_code(check)) and code != "solver_not_available"
        for check in symbolic_checks
    )


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    session: AsyncSession = Depends(get_db_session),
) -> AnalyticsSummaryResponse:
    document_status_result = await session.execute(
        select(Document.status, func.count(Document.id)).group_by(Document.status)
    )
    document_status_counts = {
        status: count
        for status, count in document_status_result.all()
    }

    embedding_status_result = await session.execute(
        select(Question.embedding_status, func.count(Question.id)).group_by(
            Question.embedding_status
        )
    )
    embedding_status_counts = {
        status: count
        for status, count in embedding_status_result.all()
    }

    difficulty_result = await session.execute(
        select(Question.difficulty, func.count(Question.id)).group_by(
            Question.difficulty
        )
    )
    difficulty_counts = {
        difficulty or "unknown": count
        for difficulty, count in difficulty_result.all()
    }

    chapter_result = await session.execute(
        select(Question.chapter, func.count(Question.id)).group_by(Question.chapter)
    )
    chapter_counts = {
        chapter or "unknown": count
        for chapter, count in chapter_result.all()
    }

    topic_result = await session.execute(
        select(Question.topic_name, func.count(Question.id)).group_by(
            Question.topic_name
        )
    )
    topic_counts = {
        topic or "unknown": count
        for topic, count in topic_result.all()
    }

    question_count = sum(embedding_status_counts.values())

    formula_result = await session.execute(
        select(Question.formulas)
    )
    formula_count = sum(
        len(formulas or [])
        for formulas in formula_result.scalars().all()
    )

    question_type_result = await session.execute(
        select(
            Question.question_type,
            Question.validation_report,
            Question.solver_code,
            Question.generation_method,
            Question.review_status,
        )
    )

    question_type_counts: dict[str, int] = {}
    generation_method_counts: dict[str, int] = {}
    validated_mcq_count = 0
    blocking_mcq_count = 0
    symbolic_validated_question_count = 0
    correct_answer_error_count = 0
    distractor_error_count = 0
    solver_unavailable_count = 0
    needs_review_count = 0

    for (
        question_type,
        validation_report,
        solver_code,
        generation_method,
        review_status,
    ) in question_type_result.all():
        normalized_type = question_type or "free_response"
        question_type_counts[normalized_type] = (
            question_type_counts.get(normalized_type, 0) + 1
        )

        if generation_method:
            generation_method_counts[generation_method] = (
                generation_method_counts.get(generation_method, 0) + 1
            )

        if _has_symbolic_validation(
            solver_code=solver_code,
            validation_report=validation_report,
        ):
            symbolic_validated_question_count += 1

        if normalized_type != "multiple_choice":
            continue

        blocking_issues = _validation_issues(
            validation_report,
            "blocking_issues",
        )

        if isinstance(validation_report, dict) and (
            validation_report.get("can_save") is True
        ):
            validated_mcq_count += 1

        if blocking_issues:
            blocking_mcq_count += 1

        if _has_distractor_issue(validation_report):
            distractor_error_count += 1

        if _has_correct_answer_issue(validation_report):
            correct_answer_error_count += 1

        if _has_solver_unavailable_issue(validation_report):
            solver_unavailable_count += 1

        if review_status == "needs_review" or _has_warning(validation_report):
            needs_review_count += 1

    multiple_choice_question_count = question_type_counts.get(
        "multiple_choice",
        0,
    )
    free_response_question_count = question_type_counts.get(
        "free_response",
        0,
    )
    distractor_error_rate = (
        distractor_error_count / multiple_choice_question_count
        if multiple_choice_question_count
        else 0.0
    )
    valid_mcq_rate = (
        validated_mcq_count / multiple_choice_question_count
        if multiple_choice_question_count
        else 0.0
    )
    correct_answer_error_rate = (
        correct_answer_error_count / multiple_choice_question_count
        if multiple_choice_question_count
        else 0.0
    )
    solver_unavailable_rate = (
        solver_unavailable_count / multiple_choice_question_count
        if multiple_choice_question_count
        else 0.0
    )
    needs_review_rate = (
        needs_review_count / multiple_choice_question_count
        if multiple_choice_question_count
        else 0.0
    )

    return AnalyticsSummaryResponse(
        document_count=sum(document_status_counts.values()),
        completed_document_count=document_status_counts.get("completed", 0),
        failed_document_count=document_status_counts.get("failed", 0),
        question_count=question_count,
        embedded_question_count=embedding_status_counts.get("completed", 0),
        formula_count=formula_count,
        multiple_choice_question_count=multiple_choice_question_count,
        free_response_question_count=free_response_question_count,
        validated_mcq_count=validated_mcq_count,
        blocking_mcq_count=blocking_mcq_count,
        symbolic_validated_question_count=symbolic_validated_question_count,
        correct_answer_error_count=correct_answer_error_count,
        distractor_error_count=distractor_error_count,
        solver_unavailable_count=solver_unavailable_count,
        needs_review_count=needs_review_count,
        valid_mcq_rate=valid_mcq_rate,
        correct_answer_error_rate=correct_answer_error_rate,
        distractor_error_rate=distractor_error_rate,
        solver_unavailable_rate=solver_unavailable_rate,
        needs_review_rate=needs_review_rate,
        embedding_status_counts=embedding_status_counts,
        question_type_counts=question_type_counts,
        difficulty_counts=difficulty_counts,
        chapter_counts=chapter_counts,
        topic_counts=topic_counts,
        generation_method_counts=generation_method_counts,
    )
