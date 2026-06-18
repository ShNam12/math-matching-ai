from __future__ import annotations

import re
from typing import TYPE_CHECKING, Protocol

from infra.db.models import Question

if TYPE_CHECKING:
    from modules.question_generation.schemas import GeneratedQuestionCandidate
    
from modules.question_quality.schemas import (
    QualityIssue,
    QuestionQualityReport,
    SemanticDuplicateHit,
    TaxonomyQualityReport,
)

from modules.taxonomy import TaxonomyDefinition, TaxonomyIndex
from modules.question_segmenter.formula_extractor import extract_formulas
from modules.semantic_search.schemas import QuestionSearchFilters


VALID_FORMULA_SOURCES = {"statement", "solution", "answer"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}

class TaxonomyClassificationQualityService:
    def __init__(
        self,
        *,
        taxonomy: TaxonomyDefinition,
        index: TaxonomyIndex,
    ) -> None:
        self.taxonomy = taxonomy
        self.index = index

    def assess_question(self, question: Question) -> TaxonomyQualityReport:
        warnings: list[QualityIssue] = []
        blocking_issues: list[QualityIssue] = []

        if question.classification_status == "failed":
            blocking_issues.append(
                QualityIssue(
                    code="classification_failed",
                    message="Question classification failed",
                    severity="error",
                    field="classification_status",
                )
            )

        if question.classification_status != "completed":
            blocking_issues.append(
                QualityIssue(
                    code="missing_classification",
                    message="Question has not been classified successfully",
                    severity="error",
                    field="classification_status",
                )
            )

        self._validate_required_codes(question, blocking_issues)
        self._validate_code_existence(question, blocking_issues)
        self._validate_parent_relations(question, blocking_issues)
        self._validate_confidence(question, warnings)
        self._validate_skills(question, warnings)
        self._validate_difficulty(question, blocking_issues)

        return TaxonomyQualityReport(
            question_id=question.id,
            warnings=warnings,
            blocking_issues=blocking_issues,
        )

    def _validate_required_codes(
        self,
        question: Question,
        blocking_issues: list[QualityIssue],
    ) -> None:
        required_fields = {
            "chapter_code": question.chapter_code,
            "topic_code": question.topic_code,
            "problem_type_code": question.problem_type_code,
        }

        for field_name, value in required_fields.items():
            if not value:
                blocking_issues.append(
                    QualityIssue(
                        code="missing_taxonomy_code",
                        message=f"Missing {field_name}",
                        severity="error",
                        field=field_name,
                    )
                )

    def _validate_code_existence(
        self,
        question: Question,
        blocking_issues: list[QualityIssue],
    ) -> None:
        if question.chapter_code and question.chapter_code not in self.index.chapters:
            blocking_issues.append(
                QualityIssue(
                    code="invalid_chapter_code",
                    message="Chapter code does not exist in taxonomy",
                    severity="error",
                    field="chapter_code",
                )
            )

        if question.topic_code and question.topic_code not in self.index.topics:
            blocking_issues.append(
                QualityIssue(
                    code="invalid_topic_code",
                    message="Topic code does not exist in taxonomy",
                    severity="error",
                    field="topic_code",
                )
            )

        if (
            question.problem_type_code
            and question.problem_type_code not in self.index.problem_types
        ):
            blocking_issues.append(
                QualityIssue(
                    code="invalid_problem_type_code",
                    message="Problem type code does not exist in taxonomy",
                    severity="error",
                    field="problem_type_code",
                )
            )

    def _validate_parent_relations(
        self,
        question: Question,
        blocking_issues: list[QualityIssue],
    ) -> None:
        topic = self.index.topics.get(question.topic_code or "")
        problem_type = self.index.problem_types.get(
            question.problem_type_code or ""
        )

        if topic and question.chapter_code and topic.parent != question.chapter_code:
            blocking_issues.append(
                QualityIssue(
                    code="topic_chapter_mismatch",
                    message="Topic does not belong to selected chapter",
                    severity="error",
                    field="topic_code",
                )
            )

        if problem_type and question.topic_code and problem_type.parent != question.topic_code:
            blocking_issues.append(
                QualityIssue(
                    code="problem_type_topic_mismatch",
                    message="Problem type does not belong to selected topic",
                    severity="error",
                    field="problem_type_code",
                )
            )

    def _validate_confidence(
        self,
        question: Question,
        warnings: list[QualityIssue],
    ) -> None:
        if question.taxonomy_confidence is None:
            warnings.append(
                QualityIssue(
                    code="missing_confidence",
                    message="Classification confidence is missing",
                    severity="warning",
                    field="taxonomy_confidence",
                )
            )
            return

        if question.taxonomy_confidence < self.taxonomy.confidence_policy.auto_accept:
            warnings.append(
                QualityIssue(
                    code="low_confidence",
                    message="Classification confidence is below auto accept threshold",
                    severity="warning",
                    field="taxonomy_confidence",
                )
            )

    def _validate_skills(
        self,
        question: Question,
        warnings: list[QualityIssue],
    ) -> None:
        if not question.skills:
            warnings.append(
                QualityIssue(
                    code="missing_skills",
                    message="Question has no assigned skills",
                    severity="warning",
                    field="skills",
                )
            )
            return

        skill_vocabulary = set(self.taxonomy.skill_vocabulary)

        for skill in question.skills:
            if skill not in skill_vocabulary:
                warnings.append(
                    QualityIssue(
                        code="unknown_skill",
                        message=f"Skill is not in taxonomy vocabulary: {skill}",
                        severity="warning",
                        field="skills",
                    )
                )

    def _validate_difficulty(
        self,
        question: Question,
        blocking_issues: list[QualityIssue],
    ) -> None:
        if question.difficulty not in self.taxonomy.difficulty_levels:
            blocking_issues.append(
                QualityIssue(
                    code="invalid_difficulty",
                    message="Difficulty must be easy, medium or hard",
                    severity="error",
                    field="difficulty",
                )
            )

class SemanticQuestionSearch(Protocol):
    async def search_questions(
        self,
        *,
        query: str,
        limit: int = 10,
        filters: QuestionSearchFilters | None = None,
    ):
        ...


def normalize_statement(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


class QuestionQualityService:
    def __init__(
        self,
        *,
        semantic_search_service: SemanticQuestionSearch | None = None,
        semantic_duplicate_threshold: float = 0.92,
    ) -> None:
        self.semantic_search_service = semantic_search_service
        self.semantic_duplicate_threshold = semantic_duplicate_threshold

    async def assess_candidate(
        self,
        *,
        candidate: GeneratedQuestionCandidate,
        source_question: Question,
        existing_questions: list[Question],
        requested_difficulty: str | None = None,
    ) -> QuestionQualityReport:
        blocking_issues: list[QualityIssue] = []
        warnings: list[QualityIssue] = []

        statement = candidate.statement.strip()

        if not statement:
            blocking_issues.append(
                QualityIssue(
                    code="empty_statement",
                    message="Generated statement must not be empty",
                    severity="error",
                    field="statement",
                )
            )

        existing_statements = {
            normalize_statement(question.statement)
            for question in existing_questions
        }

        if normalize_statement(statement) in existing_statements:
            blocking_issues.append(
                QualityIssue(
                    code="exact_duplicate_statement",
                    message="Generated statement duplicates an existing question",
                    severity="error",
                    field="statement",
                )
            )

        warnings.extend(self._validate_formula_payload(candidate))
        blocking_issues.extend(self._validate_formula_payload_blocking(candidate))
        warnings.extend(self._validate_extracted_formulas(candidate))
        warnings.extend(
            self._validate_difficulty(
                candidate=candidate,
                source_question=source_question,
                requested_difficulty=requested_difficulty,
            )
        )
        warnings.extend(self._validate_solution_and_answer(candidate))

        semantic_duplicates = await self._find_semantic_duplicates(
            candidate=candidate,
            source_question=source_question,
        )

        if semantic_duplicates:
            warnings.append(
                QualityIssue(
                    code="semantic_duplicate_candidate",
                    message="Generated statement is semantically close to existing questions",
                    severity="warning",
                    field="statement",
                )
            )

        return QuestionQualityReport(
            warnings=warnings,
            blocking_issues=blocking_issues,
            semantic_duplicates=semantic_duplicates,
        )

    def _validate_formula_payload(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> list[QualityIssue]:
        if candidate.formulas:
            return []

        return [
            QualityIssue(
                code="no_formula_detected",
                message="No formula was detected in generated content",
                severity="warning",
                field="formulas",
            )
        ]

    def _validate_formula_payload_blocking(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> list[QualityIssue]:
        blocking_issues: list[QualityIssue] = []

        for index, formula in enumerate(candidate.formulas):
            latex = str(formula.get("latex") or "").strip()
            normalized_latex = str(formula.get("normalized_latex") or "").strip()
            source = str(formula.get("source") or "").strip()

            if not latex or not normalized_latex or source not in VALID_FORMULA_SOURCES:
                blocking_issues.append(
                    QualityIssue(
                        code="invalid_formula_payload",
                        message="Formula payload must contain latex, normalized_latex and valid source",
                        severity="error",
                        field=f"formulas[{index}]",
                    )
                )

        return blocking_issues

    def _validate_extracted_formulas(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> list[QualityIssue]:
        extracted = []

        for formula in extract_formulas(candidate.statement, source="statement"):
            extracted.append(formula.normalized_latex)

        for formula in extract_formulas(candidate.solution, source="solution"):
            extracted.append(formula.normalized_latex)

        for formula in extract_formulas(candidate.answer, source="answer"):
            extracted.append(formula.normalized_latex)

        payload_formulas = {
            str(formula.get("normalized_latex") or "").strip()
            for formula in candidate.formulas
        }

        missing = [
            formula
            for formula in extracted
            if formula and formula not in payload_formulas
        ]

        if not missing:
            return []

        return [
            QualityIssue(
                code="formula_payload_mismatch",
                message="Formula payload does not include every formula extracted from generated content",
                severity="warning",
                field="formulas",
            )
        ]

    def _validate_difficulty(
        self,
        *,
        candidate: GeneratedQuestionCandidate,
        source_question: Question,
        requested_difficulty: str | None,
    ) -> list[QualityIssue]:
        warnings: list[QualityIssue] = []
        difficulty = candidate.difficulty

        if difficulty and difficulty not in VALID_DIFFICULTIES:
            warnings.append(
                QualityIssue(
                    code="invalid_difficulty",
                    message="Difficulty should be easy, medium or hard",
                    severity="warning",
                    field="difficulty",
                )
            )

        target_difficulty = requested_difficulty or source_question.difficulty

        if difficulty and target_difficulty and difficulty != target_difficulty:
            warnings.append(
                QualityIssue(
                    code="difficulty_mismatch",
                    message="Generated difficulty does not match the requested/source difficulty",
                    severity="warning",
                    field="difficulty",
                )
            )

        return warnings

    def _validate_solution_and_answer(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> list[QualityIssue]:
        warnings: list[QualityIssue] = []

        if not candidate.solution:
            warnings.append(
                QualityIssue(
                    code="missing_solution",
                    message="Generated question does not include a solution",
                    severity="warning",
                    field="solution",
                )
            )

        if not candidate.answer:
            warnings.append(
                QualityIssue(
                    code="missing_answer",
                    message="Generated question does not include an answer",
                    severity="warning",
                    field="answer",
                )
            )

        return warnings

    async def _find_semantic_duplicates(
        self,
        *,
        candidate: GeneratedQuestionCandidate,
        source_question: Question,
    ) -> list[SemanticDuplicateHit]:
        if self.semantic_search_service is None:
            return []

        results = await self.semantic_search_service.search_questions(
            query=candidate.statement,
            limit=5,
            filters=QuestionSearchFilters(
                subject=candidate.subject or source_question.subject,
                chapter=candidate.chapter or source_question.chapter,
                difficulty=candidate.difficulty or source_question.difficulty,
            ),
        )

        duplicates: list[SemanticDuplicateHit] = []

        for result in results:
            if result.question_id == source_question.id:
                continue

            if result.score < self.semantic_duplicate_threshold:
                continue

            duplicates.append(
                SemanticDuplicateHit(
                    question_id=result.question_id,
                    document_id=result.document_id,
                    score=result.score,
                    statement=result.statement,
                )
            )

        return duplicates