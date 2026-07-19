from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.models.generation import (
    ConvertToMCQPreviewRequest,
    ConvertToMCQSaveRequest,
    GeneratedFormulaItem,
    GeneratedQuestionCandidateItem,
    GenerationConstraintsRequest,
    QualityIssueItem,
    QualityRuleResultItem,
    QuestionGenerationPreviewRequest,
    QuestionGenerationPreviewResponse,
    QuestionGenerationQualityRequest,
    QuestionGenerationQualityResponse,
    QuestionGenerationSaveRequest,
    QuestionGenerationSaveResponse,
    SemanticDuplicateItem,
    SymbolicMCQPreviewRequest,
    SymbolicMCQPreviewResponse,
    SymbolicMCQSolverItem,
    SymbolicMCQSolversResponse,
)
from apps.api.v1.endpoints.questions import (
    to_choice_items,
    to_validation_report_item,
)
from apps.api.v1.services.auth import require_admin

from core.config.settings import settings
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import get_db_session
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder, QuestionEmbeddingService
from modules.question_generation import (
    GeneratedQuestionCandidate,
    GeminiQuestionGenerator,
    GenerationConstraints,
    MultipleChoiceOption,
    QuestionGenerationService,
    QuestionQualityCheckError,
    SymbolicMCQGenerator,
)

from modules.neuro_symbolic import SolverRegistry
from modules.neuro_symbolic.solver_registry import CALCULUS_1_SOLVER_CODES
from modules.question_quality import (
    QuestionQualityReport,
    QuestionQualityService,
    QuestionValidationReport,
)
from modules.semantic_search import SemanticSearchService

router = APIRouter(
    prefix="/generation",
    tags=["generation"],
    dependencies=[Depends(require_admin)],
)

def create_question_generation_service(
    session: AsyncSession,
) -> QuestionGenerationService:
    return QuestionGenerationService(
        question_repository=QuestionRepository(session),
        generator=GeminiQuestionGenerator(),
    )


def create_symbolic_mcq_generator() -> SymbolicMCQGenerator:
    return SymbolicMCQGenerator()


def create_solver_registry() -> SolverRegistry:
    return SolverRegistry()

def ensure_calculus_1_solver(solver_code: str) -> str:
    normalized_code = solver_code.strip().upper()

    if normalized_code not in CALCULUS_1_SOLVER_CODES:
        raise ValueError(
            f"Solver is not supported for Calculus 1: {normalized_code}"
        )

    return normalized_code

def create_question_embedding_service(
    *,
    session: AsyncSession,
    client,
) -> QuestionEmbeddingService:
    return QuestionEmbeddingService(
        question_repository=QuestionRepository(session),
        vector_repository=EmbeddingVectorRepository(
            client=client,
            dimension=settings.embedding_dimension,
            question_collection=settings.qdrant_question_collection,
            formula_collection=settings.qdrant_formula_collection,
        ),
        embedder=GeminiEmbedder(),
    )

def create_semantic_search_service(
    *,
    session: AsyncSession,
    client,
) -> SemanticSearchService:
    return SemanticSearchService(
        question_repository=QuestionRepository(session),
        vector_repository=EmbeddingVectorRepository(
            client=client,
            dimension=settings.embedding_dimension,
            question_collection=settings.qdrant_question_collection,
            formula_collection=settings.qdrant_formula_collection,
        ),
        embedder=GeminiEmbedder(),
    )


def _to_generation_constraints(
    request: GenerationConstraintsRequest | None,
) -> GenerationConstraints:
    if request is None:
        return GenerationConstraints()

    return GenerationConstraints(
        subject=request.subject,
        chapter=request.chapter,
        difficulty=request.difficulty,
        skills=request.skills,
        note=request.note,
        preserve_formula_style=request.preserve_formula_style,
        avoid_duplicate=request.avoid_duplicate,
    )


def _to_candidate_response(
    candidate: GeneratedQuestionCandidate,
) -> GeneratedQuestionCandidateItem:
    return GeneratedQuestionCandidateItem(
        statement=candidate.statement,
        solution=candidate.solution,
        answer=candidate.answer,
        question_type=candidate.question_type,
        choices=[
            choice.to_dict()
            for choice in candidate.choices
        ],
        correct_choice=candidate.correct_choice,
        symbolic_answer=candidate.symbolic_answer,
        generation_method=candidate.generation_method,
        solver_code=candidate.solver_code,
        validation_report=candidate.validation_report.to_dict(),
        subject=candidate.subject,
        chapter=candidate.chapter,
        difficulty=candidate.difficulty,
        skills=candidate.skills,
        formulas=[
            GeneratedFormulaItem(
                latex=formula["latex"],
                normalized_latex=formula["normalized_latex"],
                source=formula["source"],
            )
            for formula in candidate.formulas
        ],
        quality_warnings=candidate.quality_warnings,
    )


def _to_generated_candidate(
    candidate: GeneratedQuestionCandidateItem,
) -> GeneratedQuestionCandidate:
    return GeneratedQuestionCandidate(
        statement=candidate.statement,
        solution=candidate.solution,
        answer=candidate.answer,
        question_type=candidate.question_type,
        choices=[
            MultipleChoiceOption.from_dict(choice.model_dump())
            for choice in candidate.choices
        ],
        correct_choice=candidate.correct_choice,
        symbolic_answer=candidate.symbolic_answer,
        generation_method=candidate.generation_method,
        solver_code=candidate.solver_code,
        validation_report=QuestionValidationReport.from_dict(
            candidate.validation_report.model_dump()
        ),
        subject=candidate.subject,
        chapter=candidate.chapter,
        difficulty=candidate.difficulty,
        skills=candidate.skills,
        formulas=[
            formula.model_dump()
            for formula in candidate.formulas
        ],
        quality_warnings=candidate.quality_warnings,
    )


def _to_save_response(saved_question) -> QuestionGenerationSaveResponse:
    return QuestionGenerationSaveResponse(
        question_id=saved_question.id,
        document_id=saved_question.document_id,
        sequence_number=saved_question.sequence_number,
        marker=saved_question.marker,
        marker_number=saved_question.marker_number,
        statement=saved_question.statement,
        solution=saved_question.solution,
        answer=saved_question.answer,
        question_type=getattr(
            saved_question,
            "question_type",
            "free_response",
        ),
        choices=to_choice_items(getattr(saved_question, "choices", [])),
        correct_choice=getattr(saved_question, "correct_choice", None),
        validation_report=to_validation_report_item(
            getattr(saved_question, "validation_report", {})
        ),
        generation_method=getattr(
            saved_question,
            "generation_method",
            None,
        ),
        solver_code=getattr(saved_question, "solver_code", None),
        review_status=getattr(saved_question, "review_status", None),
        subject=saved_question.subject,
        chapter=saved_question.chapter,
        difficulty=saved_question.difficulty,
        skills=saved_question.skills,
        formulas=[
            GeneratedFormulaItem(
                latex=formula["latex"],
                normalized_latex=formula["normalized_latex"],
                source=formula["source"],
            )
            for formula in saved_question.formulas
        ],
        embedding_status=saved_question.embedding_status,
    )


@router.post(
    "/questions/preview",
    response_model=QuestionGenerationPreviewResponse,
)
async def preview_generated_questions(
    request: QuestionGenerationPreviewRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationPreviewResponse:
    try:
        service = create_question_generation_service(session)

        preview = await service.preview_questions(
            source_question_id=request.source_question_id,
            generation_count=request.generation_count,
            constraints=_to_generation_constraints(request.constraints),
        )

        return QuestionGenerationPreviewResponse(
            source_question_id=preview.source_question_id,
            candidates=[
                _to_candidate_response(candidate)
                for candidate in preview.candidates
            ],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/mcq/solvers",
    response_model=SymbolicMCQSolversResponse,
)
async def list_symbolic_mcq_solvers() -> SymbolicMCQSolversResponse:
    registry = create_solver_registry()

    return SymbolicMCQSolversResponse(
        solvers=[
            SymbolicMCQSolverItem(
                code=solver.code,
                name=solver.name,
                taxonomy_hint=solver.taxonomy_hint,
                param_schema=solver.param_schema,
            )
            for solver in registry.list_solvers()
            if solver.code in CALCULUS_1_SOLVER_CODES
        ]
    )


@router.post(
    "/mcq/symbolic/preview",
    response_model=SymbolicMCQPreviewResponse,
)
async def preview_symbolic_mcq(
    request: SymbolicMCQPreviewRequest,
) -> SymbolicMCQPreviewResponse:
    try:
        solver_code = ensure_calculus_1_solver(request.solver_code)

        generator = create_symbolic_mcq_generator()
        candidates = await generator.generate(
            solver_code=solver_code,
            generation_count=request.generation_count,
            difficulty=request.difficulty,
            subject=request.subject,
            chapter=request.chapter,
            skills=request.skills,
            taxonomy_metadata=request.taxonomy,
            seed=request.seed,
        )

        return SymbolicMCQPreviewResponse(
            solver_code=solver_code,
            candidates=[
                _to_candidate_response(candidate)
                for candidate in candidates
            ],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/questions/{question_id}/convert-to-mcq/preview",
    response_model=QuestionGenerationPreviewResponse,
)
async def preview_convert_to_mcq(
    question_id: str,
    request: ConvertToMCQPreviewRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationPreviewResponse:
    try:
        service = create_question_generation_service(session)
        preview = await service.preview_convert_to_mcq(
            source_question_id=question_id,
            generation_count=request.generation_count,
            constraints=_to_generation_constraints(request.constraints),
        )

        return QuestionGenerationPreviewResponse(
            source_question_id=preview.source_question_id,
            candidates=[
                _to_candidate_response(candidate)
                for candidate in preview.candidates
            ],
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    
def _to_quality_issue_item(issue) -> QualityIssueItem:
    return QualityIssueItem(
        code=issue.code,
        message=issue.message,
        severity=issue.severity,
        field=issue.field,
    )


def _to_quality_response(
    report: QuestionQualityReport,
) -> QuestionGenerationQualityResponse:
    return QuestionGenerationQualityResponse(
        can_save=report.can_save,
        quality_warnings=report.quality_warnings,
        warnings=[
            _to_quality_issue_item(issue)
            for issue in report.warnings
        ],
        blocking_issues=[
            _to_quality_issue_item(issue)
            for issue in report.blocking_issues
        ],
        symbolic_checks=[
            to_validation_report_item(
                {"symbolic_checks": [check.to_dict()]}
            ).symbolic_checks[0]
            for check in report.symbolic_checks
        ],
        semantic_duplicates=[
            SemanticDuplicateItem(
                question_id=duplicate.question_id,
                document_id=duplicate.document_id,
                score=duplicate.score,
                statement=duplicate.statement,
            )
            for duplicate in report.semantic_duplicates
        ],
        rule_results=[
            QualityRuleResultItem(
                rule_id=result.rule_id,
                title=result.title,
                category=result.category,
                status=result.status,
                issues=[
                    _to_quality_issue_item(issue)
                    for issue in result.issues
                ],
                check_codes=result.check_codes,
            )
            for result in report.rule_results
        ],
    )

@router.post(
    "/questions/quality",
    response_model=QuestionGenerationQualityResponse,
)
async def assess_generated_question_quality(
    request: QuestionGenerationQualityRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationQualityResponse:
    client = create_qdrant_client()

    try:
        question_repository = QuestionRepository(session)
        source_question = await question_repository.get_question(
            request.source_question_id
        )

        if source_question is None:
            raise ValueError("Source question not found")

        existing_questions = await question_repository.list_by_document(
            source_question.document_id
        )

        quality_service = QuestionQualityService(
            semantic_search_service=create_semantic_search_service(
                session=session,
                client=client,
            )
        )

        report = await quality_service.assess_candidate(
            candidate=_to_generated_candidate(request.candidate),
            source_question=source_question,
            existing_questions=existing_questions,
            requested_difficulty=request.requested_difficulty,
        )

        return _to_quality_response(report)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()

@router.post(
    "/questions/save",
    response_model=QuestionGenerationSaveResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_generated_question(
    request: QuestionGenerationSaveRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationSaveResponse:
    client = create_qdrant_client()

    try:
        generation_service = create_question_generation_service(session)

        saved_question = await generation_service.save_generated_question(
            source_question_id=request.source_question_id,
            candidate=_to_generated_candidate(request.candidate),
        )

        embedding_service = create_question_embedding_service(
            session=session,
            client=client,
        )

        await embedding_service.embed_question(saved_question.id)
        await session.refresh(saved_question)

        return _to_save_response(saved_question)
    except QuestionQualityCheckError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "quality_check_failed",
                "message": str(exc),
                "quality_report": _to_quality_response(exc.report).model_dump(),
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()


@router.post(
    "/mcq/symbolic/save",
    response_model=QuestionGenerationSaveResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_symbolic_mcq(
    request: QuestionGenerationSaveRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationSaveResponse:
    client = create_qdrant_client()

    try:
        ensure_calculus_1_solver(request.candidate.solver_code or "")
        generation_service = create_question_generation_service(session)
        saved_question = await generation_service.save_generated_question(
            source_question_id=request.source_question_id,
            candidate=_to_generated_candidate(request.candidate),
        )
        embedding_service = create_question_embedding_service(
            session=session,
            client=client,
        )

        await embedding_service.embed_question(saved_question.id)
        await session.refresh(saved_question)

        return _to_save_response(saved_question)
    except QuestionQualityCheckError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "quality_check_failed",
                "message": str(exc),
                "quality_report": _to_quality_response(exc.report).model_dump(),
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()


@router.post(
    "/questions/{question_id}/convert-to-mcq/save",
    response_model=QuestionGenerationSaveResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_convert_to_mcq(
    question_id: str,
    request: ConvertToMCQSaveRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationSaveResponse:
    client = create_qdrant_client()

    try:
        generation_service = create_question_generation_service(session)
        saved_question = await generation_service.save_convert_to_mcq(
            source_question_id=question_id,
            candidate=_to_generated_candidate(request.candidate),
        )
        embedding_service = create_question_embedding_service(
            session=session,
            client=client,
        )

        await embedding_service.embed_question(saved_question.id)
        await session.refresh(saved_question)

        return _to_save_response(saved_question)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except QuestionQualityCheckError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "quality_check_failed",
                "message": str(exc),
                "quality_report": _to_quality_response(exc.report).model_dump(),
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()
