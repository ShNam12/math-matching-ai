import random
from types import SimpleNamespace
from typing import Any

from modules.neuro_symbolic import (
    DistractorService,
    ParameterSampler,
    SolverExecutor,
    SolverRegistry,
)
from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    MultipleChoiceOption,
)
from modules.question_quality.schemas import (
    QuestionQualityReport,
    QuestionValidationReport,
)
from modules.question_quality.service import QuestionQualityService
from modules.question_segmenter.formula_extractor import extract_formulas


def _to_validation_report(
    quality_report: QuestionQualityReport,
) -> QuestionValidationReport:
    return QuestionValidationReport(
        warnings=quality_report.warnings,
        blocking_issues=quality_report.blocking_issues,
        symbolic_checks=quality_report.symbolic_checks,
    )


class SymbolicMCQGenerator:
    def __init__(
        self,
        *,
        registry: SolverRegistry | None = None,
        sampler: ParameterSampler | None = None,
        executor: SolverExecutor | None = None,
        distractor_service: DistractorService | None = None,
        quality_service: QuestionQualityService | None = None,
        seed: int | None = None,
        max_param_attempts: int = 40,
    ) -> None:
        self.registry = registry or SolverRegistry()
        self.executor = executor or SolverExecutor(self.registry)
        self.sampler = sampler or ParameterSampler(
            registry=self.registry,
            executor=self.executor,
            seed=seed,
        )
        self.distractor_service = distractor_service or DistractorService()
        self.quality_service = quality_service or QuestionQualityService()
        self.seed = seed
        self.max_param_attempts = max_param_attempts

    async def generate(
        self,
        *,
        solver_code: str,
        generation_count: int = 1,
        difficulty: str | None = None,
        subject: str | None = None,
        chapter: str | None = None,
        skills: list[str] | None = None,
        taxonomy_metadata: dict[str, Any] | None = None,
        seed: int | None = None,
    ) -> list[GeneratedQuestionCandidate]:
        if generation_count < 1:
            raise ValueError("generation_count must be at least 1")

        candidates: list[GeneratedQuestionCandidate] = []
        seen_params: set[tuple[tuple[str, str], ...]] = set()
        base_seed = self.seed if seed is None else seed
        attempt = 0

        while len(candidates) < generation_count and attempt < self.max_param_attempts:
            sample_seed = None if base_seed is None else base_seed + attempt
            params = self.sampler.sample_for_solver(
                solver_code,
                seed=sample_seed,
            )
            attempt += 1
            params_key = self._params_key(params)

            if params_key in seen_params:
                continue

            candidate = await self._generate_one(
                solver_code=solver_code,
                params=params,
                difficulty=difficulty,
                subject=subject,
                chapter=chapter,
                skills=skills or [],
                taxonomy_metadata=taxonomy_metadata or {},
                shuffle_seed=sample_seed,
            )
            seen_params.add(params_key)
            candidates.append(candidate)

        if len(candidates) < generation_count:
            raise ValueError("Could not generate enough unique symbolic MCQs")

        return candidates

    async def _generate_one(
        self,
        *,
        solver_code: str,
        params: dict[str, object],
        difficulty: str | None,
        subject: str | None,
        chapter: str | None,
        skills: list[str],
        taxonomy_metadata: dict[str, Any],
        shuffle_seed: int | None,
    ) -> GeneratedQuestionCandidate:
        solver = self.registry.get_solver(solver_code)
        solver_result = self.executor.execute(solver.code, params)

        if not solver_result.success or solver_result.output is None:
            raise ValueError(
                f"Solver {solver.code} failed: {solver_result.error or 'unknown error'}"
            )

        output = solver_result.output
        distractors = self.distractor_service.generate(
            correct_answer=output.answer,
            params=params,
            count=3,
            solver_func=lambda adjusted_params: solver.solve(adjusted_params).answer,
        )

        if len(distractors) < 3:
            raise ValueError(f"Solver {solver.code} did not produce enough distractors")

        option_payloads: list[dict[str, Any]] = [
            {
                "text": output.answer,
                "latex": output.answer_latex or output.answer,
                "is_correct": True,
                "distractor_type": None,
                "rationale": None,
                "metadata": {
                    "solver_code": solver.code,
                    "solver_params": params,
                    "solver_answer_latex": output.answer_latex,
                },
            }
        ]
        option_payloads.extend(
            {
                "text": distractor.text,
                "latex": distractor.latex or distractor.value,
                "is_correct": False,
                "distractor_type": distractor.error_type,
                "rationale": distractor.rationale,
                "metadata": {
                    "solver_code": solver.code,
                    "solver_params": params,
                    "distractor_latex": distractor.latex,
                },
            }
            for distractor in distractors[:3]
        )

        rng = random.Random(shuffle_seed)
        rng.shuffle(option_payloads)

        choices = [
            MultipleChoiceOption(key=key, **payload)
            for key, payload in zip(["A", "B", "C", "D"], option_payloads)
        ]
        correct_choice = next(choice.key for choice in choices if choice.is_correct)
        formulas = self._extract_formula_payloads(
            statement=output.statement,
            solution=output.solution,
            answer=output.answer,
        )
        candidate = GeneratedQuestionCandidate(
            statement=output.statement,
            solution=output.solution,
            answer=output.answer,
            subject=subject,
            chapter=chapter,
            difficulty=difficulty,
            skills=skills,
            formulas=formulas,
            quality_warnings=[],
            question_type="multiple_choice",
            choices=choices,
            correct_choice=correct_choice,
            symbolic_answer=output.answer,
            generation_method="symbolic",
            solver_code=solver.code,
        )
        quality_report = await self.quality_service.assess_candidate(
            candidate=candidate,
            source_question=self._source_question(
                candidate=candidate,
                taxonomy_metadata=taxonomy_metadata,
            ),
            existing_questions=[],
            requested_difficulty=difficulty,
        )

        return GeneratedQuestionCandidate(
            statement=candidate.statement,
            solution=candidate.solution,
            answer=candidate.answer,
            subject=candidate.subject,
            chapter=candidate.chapter,
            difficulty=candidate.difficulty,
            skills=candidate.skills,
            formulas=candidate.formulas,
            quality_warnings=quality_report.quality_warnings,
            question_type=candidate.question_type,
            choices=candidate.choices,
            correct_choice=candidate.correct_choice,
            symbolic_answer=candidate.symbolic_answer,
            generation_method=candidate.generation_method,
            solver_code=candidate.solver_code,
            validation_report=_to_validation_report(quality_report),
        )

    def _source_question(
        self,
        *,
        candidate: GeneratedQuestionCandidate,
        taxonomy_metadata: dict[str, Any],
    ):
        reserved_keys = {
            "id",
            "document_id",
            "statement",
            "solution",
            "answer",
            "subject",
            "chapter",
            "difficulty",
            "skills",
        }
        extra_metadata = {
            key: value
            for key, value in taxonomy_metadata.items()
            if key not in reserved_keys
        }

        return SimpleNamespace(
            id="symbolic-source",
            document_id="symbolic-generation",
            statement=candidate.statement,
            solution=candidate.solution,
            answer=candidate.answer,
            subject=candidate.subject,
            chapter=candidate.chapter,
            difficulty=candidate.difficulty,
            skills=candidate.skills,
            **extra_metadata,
        )

    def _extract_formula_payloads(
        self,
        *,
        statement: str,
        solution: str | None,
        answer: str | None,
    ) -> list[dict[str, str]]:
        formulas = []

        for source, text in [
            ("statement", statement),
            ("solution", solution),
            ("answer", answer),
        ]:
            formulas.extend(
                formula.__dict__
                for formula in extract_formulas(text, source=source)
            )

        return formulas

    def _params_key(
        self,
        params: dict[str, object],
    ) -> tuple[tuple[str, str], ...]:
        return tuple(
            sorted((str(key), repr(value)) for key, value in params.items())
        )
