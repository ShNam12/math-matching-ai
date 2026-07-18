import asyncio
import json
import re
from typing import Protocol

from infra.db.models import Question
from infra.db.repositories.questions import QuestionRepository
from modules.question_generation.prompt_builder import (
    build_convert_to_mcq_prompt,
    build_question_generation_prompt,
)
from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    GenerationConstraints,
    MultipleChoiceOption,
    QuestionGenerationPreview,
)
from modules.question_segmenter.formula_extractor import (
    extract_formulas,
    normalize_formula,
)
from modules.question_quality.service import QuestionQualityService
from modules.question_quality.schemas import (
    QuestionQualityReport,
    QuestionValidationReport,
)


class QuestionQualityCheckError(ValueError):
    """Raised when the final, pre-save quality validation blocks a candidate."""

    def __init__(self, report: QuestionQualityReport) -> None:
        self.report = report
        codes = ", ".join(report.quality_warnings)
        super().__init__(
            f"Generated question failed quality checks: {codes}"
        )


class TextQuestionGenerator(Protocol):
    def generate_text(self, prompt: str) -> str:
        ...


def _normalize_for_duplicate_check(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _loads_generation_json(raw_text: str) -> dict:
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    return json.loads(cleaned)


def _to_validation_report(
    quality_report: QuestionQualityReport,
) -> QuestionValidationReport:
    return QuestionValidationReport(
        warnings=quality_report.warnings,
        blocking_issues=quality_report.blocking_issues,
        symbolic_checks=quality_report.symbolic_checks,
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def _parse_choices(value: object) -> list[MultipleChoiceOption]:
    if not isinstance(value, list):
        return []

    return [
        MultipleChoiceOption.from_dict(choice)
        for choice in value
        if isinstance(choice, dict)
    ]


def _infer_correct_choice(
    *,
    correct_choice: str | None,
    choices: list[MultipleChoiceOption],
) -> str | None:
    if correct_choice:
        return correct_choice.strip().upper()

    correct_choices = [
        choice.key
        for choice in choices
        if choice.is_correct
    ]

    if len(correct_choices) == 1:
        return correct_choices[0]

    return None


def _answer_from_correct_choice(
    *,
    answer: str | None,
    correct_choice: str | None,
    choices: list[MultipleChoiceOption],
) -> str | None:
    if answer or not correct_choice:
        return answer

    for choice in choices:
        if choice.key == correct_choice:
            return choice.latex or choice.text

    return answer


def _append_extracted_formulas(
    formulas: list[dict[str, str]],
    text: str | None,
    *,
    source: str,
) -> None:
    for extracted in extract_formulas(text, source=source):
        formulas.append(extracted.model_dump())


def _append_choice_latex_formula(
    formulas: list[dict[str, str]],
    latex: str | None,
) -> None:
    if not latex:
        return

    text = latex.strip()

    if not text:
        return

    extracted = extract_formulas(text, source="choice")

    if extracted:
        formulas.extend(formula.model_dump() for formula in extracted)
        return

    formulas.append(
        {
            "latex": text,
            "normalized_latex": normalize_formula(text),
            "source": "choice",
        }
    )


def _build_distractor_metadata(
    choices: list[MultipleChoiceOption],
) -> dict[str, object]:
    distractors = []

    for choice in choices:
        if choice.is_correct:
            continue

        distractors.append(
            {
                "key": choice.key,
                "distractor_type": choice.distractor_type,
                "rationale": choice.rationale,
                "metadata": choice.metadata,
            }
        )

    return {
        "distractors": distractors,
    } if distractors else {}


class QuestionGenerationService:
    def __init__(
        self,
        *,
        question_repository: QuestionRepository,
        generator: TextQuestionGenerator,
        quality_service: QuestionQualityService | None = None,
    ) -> None:
        self.question_repository = question_repository
        self.generator = generator
        self.quality_service = quality_service or QuestionQualityService()

    async def preview_questions(
        self,
        *,
        source_question_id: str,
        generation_count: int = 3,
        constraints: GenerationConstraints | None = None,
    ) -> QuestionGenerationPreview:
        if generation_count < 1 or generation_count > 10:
            raise ValueError("Generation count must be between 1 and 10")

        source_question = await self.question_repository.get_question(
            source_question_id
        )

        if source_question is None:
            raise ValueError("Source question not found")

        constraints = constraints or GenerationConstraints()

        prompt = build_question_generation_prompt(
            source_question=source_question,
            generation_count=generation_count,
            constraints=constraints,
        )

        raw_output = await asyncio.to_thread(
            self.generator.generate_text,
            prompt,
        )

        payload = _loads_generation_json(raw_output)
        items = payload.get("items")

        if not isinstance(items, list):
            raise ValueError("Generation output must contain an items list")

        existing_questions = await self.question_repository.list_by_document(
            source_question.document_id
        )

        candidates: list[GeneratedQuestionCandidate] = []

        for item in items[:generation_count]:
            candidate = self._parse_candidate(
                item=item,
                source_question=source_question,
                constraints=constraints,
            )

            quality_report = await self.quality_service.assess_candidate(
                candidate=candidate,
                source_question=source_question,
                existing_questions=existing_questions,
                requested_difficulty=constraints.difficulty,
            )

            candidates.append(
                GeneratedQuestionCandidate(
                    statement=candidate.statement,
                    solution=candidate.solution,
                    answer=candidate.answer,
                    question_type=candidate.question_type,
                    choices=candidate.choices,
                    correct_choice=candidate.correct_choice,
                    symbolic_answer=candidate.symbolic_answer,
                    generation_method=candidate.generation_method,
                    solver_code=candidate.solver_code,
                    validation_report=_to_validation_report(quality_report),
                    subject=candidate.subject,
                    chapter=candidate.chapter,
                    difficulty=candidate.difficulty,
                    skills=candidate.skills,
                    formulas=candidate.formulas,
                    quality_warnings=quality_report.quality_warnings,
                )
            )

        return QuestionGenerationPreview(
            source_question_id=source_question.id,
            candidates=candidates,
        )

    async def preview_convert_to_mcq(
        self,
        *,
        source_question_id: str,
        generation_count: int = 1,
        constraints: GenerationConstraints | None = None,
    ) -> QuestionGenerationPreview:
        if generation_count < 1 or generation_count > 10:
            raise ValueError("Generation count must be between 1 and 10")

        source_question = await self.question_repository.get_question(
            source_question_id
        )

        if source_question is None:
            raise LookupError("Source question not found")

        if getattr(source_question, "question_type", "free_response") != (
            "free_response"
        ):
            raise ValueError("Only free_response questions can be converted to MCQ")

        constraints = constraints or GenerationConstraints()
        prompt = build_convert_to_mcq_prompt(
            source_question=source_question,
            generation_count=generation_count,
            constraints=constraints,
        )

        raw_output = await asyncio.to_thread(
            self.generator.generate_text,
            prompt,
        )

        payload = _loads_generation_json(raw_output)
        items = payload.get("items")

        if not isinstance(items, list):
            raise ValueError("Generation output must contain an items list")

        existing_questions = await self.question_repository.list_by_document(
            source_question.document_id
        )
        candidates: list[GeneratedQuestionCandidate] = []

        for item in items[:generation_count]:
            candidate = self._parse_candidate(
                item=item,
                source_question=source_question,
                constraints=constraints,
            )

            if candidate.question_type != "multiple_choice":
                raise ValueError("Converted candidate must be multiple_choice")

            quality_report = await self.quality_service.assess_candidate(
                candidate=candidate,
                source_question=source_question,
                existing_questions=existing_questions,
                requested_difficulty=constraints.difficulty,
            )

            candidates.append(
                GeneratedQuestionCandidate(
                    statement=candidate.statement,
                    solution=candidate.solution,
                    answer=candidate.answer,
                    question_type=candidate.question_type,
                    choices=candidate.choices,
                    correct_choice=candidate.correct_choice,
                    symbolic_answer=candidate.symbolic_answer,
                    generation_method=candidate.generation_method
                    or "ai_convert",
                    solver_code=candidate.solver_code,
                    validation_report=_to_validation_report(quality_report),
                    subject=candidate.subject,
                    chapter=candidate.chapter,
                    difficulty=candidate.difficulty,
                    skills=candidate.skills,
                    formulas=candidate.formulas,
                    quality_warnings=quality_report.quality_warnings,
                )
            )

        return QuestionGenerationPreview(
            source_question_id=source_question.id,
            candidates=candidates,
        )

    async def save_convert_to_mcq(
        self,
        *,
        source_question_id: str,
        candidate: GeneratedQuestionCandidate,
    ) -> Question:
        source_question = await self.question_repository.get_question(
            source_question_id
        )

        if source_question is None:
            raise LookupError("Source question not found")

        if getattr(source_question, "question_type", "free_response") != (
            "free_response"
        ):
            raise ValueError("Only free_response questions can be converted to MCQ")

        if candidate.question_type != "multiple_choice":
            raise ValueError("Converted candidate must be multiple_choice")

        return await self.save_generated_question(
            source_question_id=source_question_id,
            candidate=GeneratedQuestionCandidate(
                statement=candidate.statement,
                solution=candidate.solution,
                answer=candidate.answer,
                subject=candidate.subject,
                chapter=candidate.chapter,
                difficulty=candidate.difficulty,
                skills=candidate.skills,
                formulas=candidate.formulas,
                quality_warnings=candidate.quality_warnings,
                question_type=candidate.question_type,
                choices=candidate.choices,
                correct_choice=candidate.correct_choice,
                symbolic_answer=candidate.symbolic_answer,
                generation_method=candidate.generation_method
                or "ai_convert",
                solver_code=candidate.solver_code,
                validation_report=candidate.validation_report,
            ),
        )
    
    async def save_generated_question(
        self,
        *,
        source_question_id: str,
        candidate: GeneratedQuestionCandidate,
    ) -> Question:
        source_question = await self.question_repository.get_question(
            source_question_id
        )

        if source_question is None:
            raise ValueError("Source question not found")

        existing_questions = await self.question_repository.list_by_document(
            source_question.document_id
        )

        quality_report = await self.quality_service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=existing_questions,
            requested_difficulty=None,
        )

        if not quality_report.can_save:
            raise QuestionQualityCheckError(quality_report)

        validation_report = _to_validation_report(quality_report)

        return await self.question_repository.create_generated_question(
            source_question=source_question,
            statement=candidate.statement,
            solution=candidate.solution,
            answer=candidate.answer,
            formulas=candidate.formulas,
            subject=candidate.subject,
            chapter=candidate.chapter,
            difficulty=candidate.difficulty,
            skills=candidate.skills,
            question_type=candidate.question_type,
            choices=[
                choice.to_dict()
                for choice in candidate.choices
            ],
            correct_choice=candidate.correct_choice,
            validation_report=validation_report.to_dict(),
            generation_method=candidate.generation_method,
            solver_code=candidate.solver_code,
            distractor_metadata=_build_distractor_metadata(candidate.choices),
        )

    def _parse_candidate(
        self,
        *,
        item: object,
        source_question: Question,
        constraints: GenerationConstraints,
    ) -> GeneratedQuestionCandidate:
        if not isinstance(item, dict):
            raise ValueError("Each generated item must be an object")

        statement = str(item.get("statement") or "").strip()

        if not statement:
            raise ValueError("Generated statement must not be empty")

        solution_value = item.get("solution")
        answer_value = item.get("answer")
        difficulty_value = item.get("difficulty")
        skills_value = item.get("skills")
        question_type = str(
            item.get("question_type") or "free_response"
        ).strip()
        choices_value = item.get("choices")
        correct_choice_value = item.get("correct_choice")
        symbolic_answer_value = item.get("symbolic_answer")
        generation_method_value = item.get("generation_method")
        solver_code_value = item.get("solver_code")
        validation_report_value = item.get("validation_report")

        solution = _optional_str(solution_value)
        choices = _parse_choices(choices_value)
        correct_choice = _infer_correct_choice(
            correct_choice=_optional_str(correct_choice_value),
            choices=choices,
        )
        answer = _answer_from_correct_choice(
            answer=_optional_str(answer_value),
            correct_choice=correct_choice,
            choices=choices,
        )
        difficulty = (
            str(difficulty_value).strip()
            if difficulty_value is not None and str(difficulty_value).strip()
            else constraints.difficulty or source_question.difficulty
        )

        skills = (
            [str(skill).strip() for skill in skills_value if str(skill).strip()]
            if isinstance(skills_value, list)
            else constraints.skills or source_question.skills
        )

        formulas = []
        _append_extracted_formulas(formulas, statement, source="statement")
        _append_extracted_formulas(formulas, solution, source="solution")
        _append_extracted_formulas(formulas, answer, source="answer")

        for choice in choices:
            _append_extracted_formulas(formulas, choice.text, source="choice")
            _append_choice_latex_formula(formulas, choice.latex)

        quality_warnings: list[str] = []

        return GeneratedQuestionCandidate(
            statement=statement,
            solution=solution,
            answer=answer,
            question_type=question_type,
            choices=choices,
            correct_choice=correct_choice,
            symbolic_answer=(
                str(symbolic_answer_value).strip()
                if symbolic_answer_value is not None
                and str(symbolic_answer_value).strip()
                else None
            ),
            generation_method=(
                str(generation_method_value).strip()
                if generation_method_value is not None
                and str(generation_method_value).strip()
                else None
            ),
            solver_code=(
                str(solver_code_value).strip()
                if solver_code_value is not None
                and str(solver_code_value).strip()
                else None
            ),
            validation_report=QuestionValidationReport.from_dict(
                validation_report_value
                if isinstance(validation_report_value, dict)
                else None
            ),
            subject=constraints.subject or source_question.subject,
            chapter=constraints.chapter or source_question.chapter,
            difficulty=difficulty,
            skills=skills,
            formulas=formulas,
            quality_warnings=quality_warnings,
        )
