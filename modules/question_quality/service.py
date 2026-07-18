from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING, Protocol

from infra.db.models import Question

if TYPE_CHECKING:
    from modules.question_generation.schemas import GeneratedQuestionCandidate
    
from modules.question_quality.schemas import (
    QualityIssue,
    QuestionQualityReport,
    QuestionValidationReport,
    QualityRuleResult,
    SemanticDuplicateHit,
    SymbolicCheckResult,
    TaxonomyQualityReport,
)

from modules.neuro_symbolic.solver_registry import CALCULUS_1_SOLVER_CODES
from modules.taxonomy import TaxonomyDefinition, TaxonomyIndex
from modules.question_segmenter.formula_extractor import (
    extract_formulas,
    normalize_formula,
)
from modules.semantic_search.schemas import QuestionSearchFilters
from modules.neuro_symbolic.symbolic_validator import SymbolicMCQValidator


VALID_FORMULA_SOURCES = {"statement", "solution", "answer", "choice"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_MCQ_KEYS = {"A", "B", "C", "D"}

CANDIDATE_RULE_DEFINITIONS = (
    {
        "rule_id": "statement_required",
        "title": "Nội dung đề bài không được rỗng",
        "category": "Nội dung",
        "codes": {"empty_statement"},
    },
    {
        "rule_id": "exact_duplicate",
        "title": "Không trùng hoàn toàn với bài đã có",
        "category": "Trùng lặp",
        "codes": {"exact_duplicate_statement"},
    },
    {
        "rule_id": "mcq_structure",
        "title": "Cấu trúc câu hỏi trắc nghiệm",
        "category": "Trắc nghiệm",
        "mcq_only": True,
        "codes": {
            "mcq_missing_choices",
            "mcq_invalid_choice_count",
            "mcq_invalid_choice_key",
            "mcq_duplicate_choice_key",
            "mcq_empty_choice_text",
            "mcq_missing_correct_choice",
            "mcq_correct_choice_not_found",
            "mcq_multiple_correct_choices",
            "mcq_no_correct_choice_flagged",
        },
    },
    {
        "rule_id": "mcq_distractors",
        "title": "Các phương án nhiễu hợp lệ",
        "category": "Trắc nghiệm",
        "mcq_only": True,
        "codes": {
            "mcq_duplicate_choice_content",
            "mcq_distractor_equals_correct_answer",
            "mcq_all_choices_too_similar",
        },
    },
    {
        "rule_id": "solver_domain",
        "title": "Bộ giải phù hợp miền kiến thức",
        "category": "Bộ giải toán",
        "mcq_only": True,
        "codes": {"solver_domain_mismatch"},
    },
    {
        "rule_id": "symbolic_validation",
        "title": "Kiểm chứng bằng bộ giải ký hiệu",
        "category": "Bộ giải toán",
        "mcq_only": True,
        "codes": {
            "solver_not_available",
            "symbolic_correct_answer_mismatch",
            "symbolic_distractor_equals_correct",
            "symbolic_distractor_duplicate",
            "symbolic_parse_failed",
        },
    },
    {
        "rule_id": "formula_payload",
        "title": "Dữ liệu công thức hợp lệ",
        "category": "Công thức",
        "codes": {
            "no_formula_detected",
            "invalid_formula_payload",
            "formula_payload_mismatch",
        },
    },
    {
        "rule_id": "difficulty",
        "title": "Độ khó phù hợp yêu cầu",
        "category": "Metadata",
        "codes": {"invalid_difficulty", "difficulty_mismatch"},
    },
    {
        "rule_id": "solution_answer",
        "title": "Có lời giải và đáp án",
        "category": "Nội dung",
        "codes": {"missing_solution", "missing_answer"},
    },
    {
        "rule_id": "semantic_duplicate",
        "title": "Không quá tương đồng về ngữ nghĩa",
        "category": "Trùng lặp",
        "codes": {"semantic_duplicate_candidate"},
    },
)

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


def normalize_choice_text(text: str) -> str:
    return normalize_statement(text)


def normalize_choice_latex(latex: str | None) -> str:
    if not latex:
        return ""

    return re.sub(r"\s+", "", normalize_formula(latex)).lower()


def _numeric_key(value: int | float) -> tuple[str, str]:
    if isinstance(value, int) or value.is_integer():
        return ("num", str(int(value)))

    return ("num", str(value))


def _flatten_ast_key(
    op_name: str,
    left,
    right,
) -> list[tuple]:
    items = []

    for item in [left, right]:
        if isinstance(item, tuple) and item and item[0] == op_name:
            items.extend(item[1])
        else:
            items.append(item)

    return items


def _numeric_value(item: tuple) -> float | None:
    if item[0] != "num":
        return None

    try:
        return float(item[1])
    except ValueError:
        return None


def _fold_numeric_add(items: list[tuple]) -> tuple | None:
    values = [_numeric_value(item) for item in items]

    if any(value is None for value in values):
        return None

    return _numeric_key(sum(value for value in values if value is not None))


def _fold_numeric_mul(items: list[tuple]) -> tuple | None:
    values = [_numeric_value(item) for item in items]

    if any(value is None for value in values):
        return None

    product = 1.0

    for value in values:
        if value is not None:
            product *= value

    return _numeric_key(product)


def _canonical_ast_key(node) -> tuple | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return _numeric_key(node.value)

    if isinstance(node, ast.Name):
        return ("var", node.id)

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        operand = _canonical_ast_key(node.operand)
        if operand is None:
            return None

        if operand[0] == "num":
            value = float(operand[1]) * -1
            return _numeric_key(value)

        return ("neg", operand)

    if isinstance(node, ast.BinOp):
        left = _canonical_ast_key(node.left)
        right = _canonical_ast_key(node.right)

        if left is None or right is None:
            return None

        if isinstance(node.op, ast.Add):
            items = _flatten_ast_key("add", left, right)
            folded = _fold_numeric_add(items)

            if folded is not None:
                return folded

            return ("add", tuple(sorted(items, key=repr)))

        if isinstance(node.op, ast.Sub):
            right_value = _numeric_value(right)
            negated_right = (
                _numeric_key(right_value * -1)
                if right_value is not None
                else ("neg", right)
            )
            items = _flatten_ast_key("add", left, negated_right)
            folded = _fold_numeric_add(items)

            if folded is not None:
                return folded

            return ("add", tuple(sorted(items, key=repr)))

        if isinstance(node.op, ast.Mult):
            items = _flatten_ast_key("mul", left, right)
            folded = _fold_numeric_mul(items)

            if folded is not None:
                return folded

            return ("mul", tuple(sorted(items, key=repr)))

        if isinstance(node.op, ast.Div):
            left_value = _numeric_value(left)
            right_value = _numeric_value(right)

            if left_value is not None and right_value not in {None, 0.0}:
                return _numeric_key(left_value / right_value)

            return ("div", left, right)

        if isinstance(node.op, ast.Pow):
            left_value = _numeric_value(left)
            right_value = _numeric_value(right)

            if left_value is not None and right_value is not None:
                return _numeric_key(left_value ** right_value)

            return ("pow", left, right)

    return None


def symbolic_choice_key(value: str | None) -> str | None:
    if not value:
        return None

    expression = value.strip()
    expression = expression.strip("$")
    expression = expression.replace(r"\(", "").replace(r"\)", "")
    expression = expression.replace(r"\[", "").replace(r"\]", "")
    expression = expression.replace("{", "(").replace("}", ")")
    expression = expression.replace("^", "**")
    expression = re.sub(r"\s+", "", expression)

    if not expression:
        return None

    if "\\" in expression:
        return None

    if not re.fullmatch(r"[A-Za-z0-9_+\-*/().]+", expression):
        return None

    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError:
        return None

    key = _canonical_ast_key(parsed.body)

    return repr(key) if key is not None else None


class QuestionQualityService:
    def __init__(
        self,
        *,
        semantic_search_service: SemanticQuestionSearch | None = None,
        semantic_duplicate_threshold: float = 0.92,
        symbolic_validator: SymbolicMCQValidator | None = None,
    ) -> None:
        self.semantic_search_service = semantic_search_service
        self.semantic_duplicate_threshold = semantic_duplicate_threshold
        self.symbolic_validator = symbolic_validator or SymbolicMCQValidator()

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

        blocking_issues.extend(self._validate_mcq_structure(candidate))
        blocking_issues.extend(self._validate_mcq_distractors(candidate))

        blocking_issues.extend(
            self._validate_calculus_1_solver_domain(candidate, source_question)
        )
        symbolic_checks: list[SymbolicCheckResult] = []
        symbolic_report = self._validate_mcq_symbolically(candidate)
        warnings.extend(symbolic_report.warnings)
        blocking_issues.extend(symbolic_report.blocking_issues)
        symbolic_checks.extend(symbolic_report.symbolic_checks)
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

        rule_results = self._build_rule_results(
            candidate=candidate,
            warnings=warnings,
            blocking_issues=blocking_issues,
            symbolic_checks=symbolic_checks,
        )

        return QuestionQualityReport(
            warnings=warnings,
            blocking_issues=blocking_issues,
            semantic_duplicates=semantic_duplicates,
            symbolic_checks=symbolic_checks,
            rule_results=rule_results,
        )

    def _build_rule_results(
        self,
        *,
        candidate: GeneratedQuestionCandidate,
        warnings: list[QualityIssue],
        blocking_issues: list[QualityIssue],
        symbolic_checks: list[SymbolicCheckResult],
    ) -> list[QualityRuleResult]:
        """Expose existing validation outcomes rule by rule without changing them."""
        warning_codes = {issue.code for issue in warnings}
        blocking_codes = {issue.code for issue in blocking_issues}
        all_issues = [*blocking_issues, *warnings]
        results: list[QualityRuleResult] = []

        for definition in CANDIDATE_RULE_DEFINITIONS:
            if (
                definition.get("mcq_only")
                and candidate.question_type != "multiple_choice"
            ):
                results.append(
                    QualityRuleResult(
                        rule_id=definition["rule_id"],
                        title=definition["title"],
                        category=definition["category"],
                        status="skipped",
                    )
                )
                continue

            matched_issues = [
                issue for issue in all_issues
                if issue.code in definition["codes"]
            ]

            if any(issue.code in blocking_codes for issue in matched_issues):
                rule_status = "fail"
            elif any(issue.code in warning_codes for issue in matched_issues):
                rule_status = "warn"
            else:
                rule_status = "pass"

            check_codes: list[str] = []
            if definition["rule_id"] == "symbolic_validation":
                check_codes = [check.code for check in symbolic_checks]
                if (
                    rule_status != "fail"
                    and any(not check.passed for check in symbolic_checks)
                ):
                    rule_status = "warn"

            results.append(
                QualityRuleResult(
                    rule_id=definition["rule_id"],
                    title=definition["title"],
                    category=definition["category"],
                    status=rule_status,
                    issues=matched_issues,
                    check_codes=check_codes,
                )
            )

        return results

    def _validate_mcq_symbolically(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> QuestionValidationReport:
        if candidate.question_type != "multiple_choice":
            return QuestionValidationReport()

        return self.symbolic_validator.validate_candidate(
            candidate,
            params=self._extract_solver_params(candidate),
        )

    def _extract_solver_params(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> dict[str, object] | None:
        for choice in candidate.choices:
            params = choice.metadata.get("solver_params")
            if isinstance(params, dict):
                return params

        return None

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

    def _validate_mcq_structure(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> list[QualityIssue]:
        if candidate.question_type != "multiple_choice":
            return []

        blocking_issues: list[QualityIssue] = []
        choices = candidate.choices

        if not choices:
            return [
                QualityIssue(
                    code="mcq_missing_choices",
                    message="Multiple-choice questions must include choices",
                    severity="error",
                    field="choices",
                )
            ]

        if len(choices) != 4:
            blocking_issues.append(
                QualityIssue(
                    code="mcq_invalid_choice_count",
                    message="Multiple-choice questions must have exactly 4 choices",
                    severity="error",
                    field="choices",
                )
            )

        seen_keys: set[str] = set()
        duplicate_keys: set[str] = set()
        correct_keys: list[str] = []

        for index, choice in enumerate(choices):
            key = choice.key.strip().upper()

            if key not in VALID_MCQ_KEYS:
                blocking_issues.append(
                    QualityIssue(
                        code="mcq_invalid_choice_key",
                        message="Choice key must be one of A, B, C or D",
                        severity="error",
                        field=f"choices[{index}].key",
                    )
                )

            if key in seen_keys:
                duplicate_keys.add(key)
            else:
                seen_keys.add(key)

            if not choice.text.strip():
                blocking_issues.append(
                    QualityIssue(
                        code="mcq_empty_choice_text",
                        message="Choice text must not be empty",
                        severity="error",
                        field=f"choices[{index}].text",
                    )
                )

            if choice.is_correct:
                correct_keys.append(key)

        for key in sorted(duplicate_keys):
            blocking_issues.append(
                QualityIssue(
                    code="mcq_duplicate_choice_key",
                    message=f"Choice key is duplicated: {key}",
                    severity="error",
                    field="choices",
                )
            )

        correct_choice = (
            candidate.correct_choice.strip().upper()
            if candidate.correct_choice
            else None
        )

        if correct_choice is None:
            blocking_issues.append(
                QualityIssue(
                    code="mcq_missing_correct_choice",
                    message="Multiple-choice questions must include correct_choice",
                    severity="error",
                    field="correct_choice",
                )
            )
        elif correct_choice not in seen_keys:
            blocking_issues.append(
                QualityIssue(
                    code="mcq_correct_choice_not_found",
                    message="correct_choice must match one of the choice keys",
                    severity="error",
                    field="correct_choice",
                )
            )

        if len(correct_keys) > 1:
            blocking_issues.append(
                QualityIssue(
                    code="mcq_multiple_correct_choices",
                    message="Only one choice may be marked as correct",
                    severity="error",
                    field="choices",
                )
            )
        elif len(correct_keys) == 0:
            blocking_issues.append(
                QualityIssue(
                    code="mcq_no_correct_choice_flagged",
                    message="Exactly one choice must be marked as correct",
                    severity="error",
                    field="choices",
                )
            )
        elif (
            correct_choice is not None
            and correct_choice in seen_keys
            and correct_keys[0] != correct_choice
        ):
            blocking_issues.append(
                QualityIssue(
                    code="mcq_correct_choice_not_found",
                    message="correct_choice must match the choice marked as correct",
                    severity="error",
                    field="correct_choice",
                )
            )

        return blocking_issues

    def _validate_mcq_distractors(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> list[QualityIssue]:
        if candidate.question_type != "multiple_choice" or not candidate.choices:
            return []

        blocking_issues: list[QualityIssue] = []
        issue_codes: set[str] = set()

        def add_issue(code: str, message: str, field: str) -> None:
            if code in issue_codes:
                return

            issue_codes.add(code)
            blocking_issues.append(
                QualityIssue(
                    code=code,
                    message=message,
                    severity="error",
                    field=field,
                )
            )

        correct_choice_key = (
            candidate.correct_choice.strip().upper()
            if candidate.correct_choice
            else None
        )
        correct_choice = None

        for choice in candidate.choices:
            key = choice.key.strip().upper()

            if correct_choice_key and key == correct_choice_key:
                correct_choice = choice
                break

        if correct_choice is None:
            flagged_correct = [
                choice
                for choice in candidate.choices
                if choice.is_correct
            ]

            if len(flagged_correct) == 1:
                correct_choice = flagged_correct[0]

        correct_text_key = (
            normalize_choice_text(correct_choice.text)
            if correct_choice is not None
            else ""
        )
        correct_latex_key = (
            normalize_choice_latex(correct_choice.latex)
            if correct_choice is not None
            else ""
        )
        correct_symbolic_key = (
            symbolic_choice_key(correct_choice.latex)
            or symbolic_choice_key(correct_choice.text)
            if correct_choice is not None
            else None
        )

        seen_text: dict[str, str] = {}
        seen_latex: dict[str, str] = {}
        seen_symbolic: dict[str, str] = {}
        unique_content_keys: set[str] = set()

        for choice in candidate.choices:
            key = choice.key.strip().upper()
            text_key = normalize_choice_text(choice.text)
            latex_key = normalize_choice_latex(choice.latex)
            symbolic_key = (
                symbolic_choice_key(choice.latex)
                or symbolic_choice_key(choice.text)
            )
            primary_key = latex_key or text_key

            if primary_key:
                unique_content_keys.add(primary_key)

            if text_key:
                if text_key in seen_text:
                    add_issue(
                        "mcq_duplicate_choice_content",
                        "Choice content must be distinct",
                        "choices",
                    )
                else:
                    seen_text[text_key] = key

            if latex_key:
                if latex_key in seen_latex:
                    add_issue(
                        "mcq_duplicate_choice_content",
                        "Choice LaTeX content must be distinct",
                        "choices",
                    )
                else:
                    seen_latex[latex_key] = key

            if symbolic_key:
                if symbolic_key in seen_symbolic:
                    add_issue(
                        "mcq_duplicate_choice_content",
                        "Choice symbolic content must be distinct",
                        "choices",
                    )
                else:
                    seen_symbolic[symbolic_key] = key

            if correct_choice is None or choice == correct_choice:
                continue

            if (
                text_key
                and correct_text_key
                and text_key == correct_text_key
            ):
                add_issue(
                    "mcq_distractor_equals_correct_answer",
                    "Distractors must not equal the correct answer",
                    "choices",
                )

            if (
                latex_key
                and correct_latex_key
                and latex_key == correct_latex_key
            ):
                add_issue(
                    "mcq_distractor_equals_correct_answer",
                    "Distractor LaTeX must not equal the correct answer",
                    "choices",
                )

            if (
                symbolic_key
                and correct_symbolic_key
                and symbolic_key == correct_symbolic_key
            ):
                add_issue(
                    "mcq_distractor_equals_correct_answer",
                    "Distractor symbolic value must not equal the correct answer",
                    "choices",
                )

        if len(candidate.choices) > 1 and len(unique_content_keys) == 1:
            add_issue(
                "mcq_all_choices_too_similar",
                "All choices are too similar",
                "choices",
            )

        return blocking_issues

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
    
    def _validate_calculus_1_solver_domain(
        self,
        candidate: GeneratedQuestionCandidate,
        source_question: Question,
    ) -> list[QualityIssue]:
        if candidate.question_type != "multiple_choice":
            return []

        if not candidate.solver_code:
            return []

        subject_values = [
            str(candidate.subject or "").lower(),
            str(getattr(source_question, "subject", "") or "").lower(),
            str(getattr(source_question, "subject_code", "") or "").lower(),
        ]

        is_calculus_1 = any(
            value in {"calculus", "calculus 1", "gt1", "giai tich 1", "giải tích 1"}
            or "calculus" in value
            or "giai tich" in value
            or "giải tích" in value
            for value in subject_values
        )

        solver_code = candidate.solver_code.strip().upper()

        if is_calculus_1 and solver_code not in CALCULUS_1_SOLVER_CODES:
            return [
                QualityIssue(
                    code="solver_domain_mismatch",
                    message="Solver is not supported for Calculus 1",
                    severity="error",
                    field="solver_code",
                )
            ]

        return []
