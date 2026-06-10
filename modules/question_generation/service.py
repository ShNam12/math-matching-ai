import asyncio
import json
import re
from typing import Protocol

from infra.db.models import Question
from infra.db.repositories.questions import QuestionRepository
from modules.question_generation.prompt_builder import (
    build_question_generation_prompt,
)
from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    GenerationConstraints,
    QuestionGenerationPreview,
)
from modules.question_segmenter.formula_extractor import extract_formulas
from modules.question_quality.service import QuestionQualityService


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
            blocking_codes = ", ".join(quality_report.quality_warnings)
            raise ValueError(
                f"Generated question failed quality checks: {blocking_codes}"
            )

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

        solution = (
            str(solution_value).strip()
            if solution_value is not None and str(solution_value).strip()
            else None
        )
        answer = (
            str(answer_value).strip()
            if answer_value is not None and str(answer_value).strip()
            else None
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
        for extracted in extract_formulas(statement, source="statement"):
            formulas.append(extracted.model_dump())

        for extracted in extract_formulas(solution, source="solution"):
            formulas.append(extracted.model_dump())

        for extracted in extract_formulas(answer, source="answer"):
            formulas.append(extracted.model_dump())

        quality_warnings: list[str] = []

        return GeneratedQuestionCandidate(
            statement=statement,
            solution=solution,
            answer=answer,
            subject=constraints.subject or source_question.subject,
            chapter=constraints.chapter or source_question.chapter,
            difficulty=difficulty,
            skills=skills,
            formulas=formulas,
            quality_warnings=quality_warnings,
        )