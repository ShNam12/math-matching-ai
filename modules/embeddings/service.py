import asyncio
from typing import Protocol

from infra.db.repositories.questions import QuestionRepository
from modules.embeddings.schemas import (
    EmbeddingResult,
    FormulaVector,
    QuestionVector,
)
from modules.embeddings.text_builder import (
    build_formula_embedding_text,
    build_question_embedding_text,
)
from modules.question_segmenter.formula_extractor import (
    extract_formulas,
    normalize_formula,
)


class TextEmbedder(Protocol):
    def embed_text(self, text: str) -> list[float]:
        ...


class VectorRepository(Protocol):
    async def replace_for_document(
        self,
        *,
        document_id: str,
        questions: list[QuestionVector],
        formulas: list[FormulaVector],
    ) -> None:
        ...


def _choice_value(choice: object, field: str):
    if isinstance(choice, dict):
        return choice.get(field)

    return getattr(choice, field, None)


def _question_formulas(question) -> list[dict[str, str]]:
    formulas: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for formula in getattr(question, "formulas", []):
        normalized_latex = str(formula.get("normalized_latex") or "").strip()
        source = str(formula.get("source") or "statement").strip()

        if not normalized_latex:
            continue

        key = (source, normalized_latex)
        if key in seen:
            continue

        seen.add(key)
        formulas.append(
            {
                "latex": str(formula.get("latex") or normalized_latex),
                "normalized_latex": normalized_latex,
                "source": source,
            }
        )

    for choice in getattr(question, "choices", []) or []:
        text = _choice_value(choice, "text")
        latex = _choice_value(choice, "latex")

        for extracted in extract_formulas(str(text or ""), source="choice"):
            key = ("choice", extracted.normalized_latex)
            if key in seen:
                continue

            seen.add(key)
            formulas.append(extracted.model_dump())

        if latex is None:
            continue

        latex_text = str(latex).strip()
        if not latex_text:
            continue

        extracted_formulas = extract_formulas(latex_text, source="choice")

        if extracted_formulas:
            candidates = [
                extracted.model_dump()
                for extracted in extracted_formulas
            ]
        else:
            candidates = [
                {
                    "latex": latex_text,
                    "normalized_latex": normalize_formula(latex_text),
                    "source": "choice",
                }
            ]

        for formula in candidates:
            normalized_latex = formula["normalized_latex"]
            key = ("choice", normalized_latex)
            if key in seen:
                continue

            seen.add(key)
            formulas.append(formula)

    return formulas


class QuestionEmbeddingService:
    def __init__(
        self,
        *,
        question_repository: QuestionRepository,
        vector_repository: VectorRepository,
        embedder: TextEmbedder,
    ) -> None:
        self.question_repository = question_repository
        self.vector_repository = vector_repository
        self.embedder = embedder

    async def embed_document(self, document_id: str) -> EmbeddingResult:
        questions = await self.question_repository.list_by_document(document_id)

        if not questions:
            raise ValueError(
                f"No segmented questions were found: {document_id}"
            )

        await self.question_repository.mark_embedding_pending_for_document(
            document_id
        )

        try:
            question_vectors = []
            formula_vectors = []

            for question in questions:
                question_vector = await asyncio.to_thread(
                    self.embedder.embed_text,
                    build_question_embedding_text(question),
                )

                question_vectors.append(
                    QuestionVector(
                        question_id=question.id,
                        document_id=question.document_id,
                        sequence_number=question.sequence_number,
                        marker=question.marker,
                        marker_number=question.marker_number,
                        statement=question.statement,
                        question_type=getattr(
                            question,
                            "question_type",
                            "free_response",
                        ),
                        subject=question.subject,
                        chapter=question.chapter,
                        difficulty=question.difficulty,
                        skills=question.skills,
                        subject_code=question.subject_code,
                        chapter_code=question.chapter_code,
                        chapter_name=question.chapter_name,
                        topic_code=question.topic_code,
                        topic_name=question.topic_name,
                        problem_type_code=question.problem_type_code,
                        problem_type_name=question.problem_type_name,
                        taxonomy_confidence=question.taxonomy_confidence,
                        review_status=question.review_status,
                        classification_status=question.classification_status,
                        vector=question_vector,
                    )
                )

                for formula_index, formula in enumerate(
                    _question_formulas(question)
                ):
                    normalized_latex = formula.get(
                        "normalized_latex",
                        "",
                    ).strip()

                    if not normalized_latex:
                        continue

                    formula_vector = await asyncio.to_thread(
                        self.embedder.embed_text,
                        build_formula_embedding_text(normalized_latex),
                    )

                    formula_vectors.append(
                        FormulaVector(
                            question_id=question.id,
                            document_id=question.document_id,
                            formula_index=formula_index,
                            latex=formula.get("latex", normalized_latex),
                            normalized_latex=normalized_latex,
                            source=formula.get("source", "statement"),
                            vector=formula_vector,
                        )
                    )

            await self.vector_repository.replace_for_document(
                document_id=document_id,
                questions=question_vectors,
                formulas=formula_vectors,
            )

            await self.question_repository.mark_embedding_completed_for_document(
                document_id=document_id,
                embedding_model=getattr(self.embedder, "model", "unknown"),
                embedding_dimension=getattr(self.embedder, "dimension", 0),
            )

            return EmbeddingResult(
                document_id=document_id,
                question_count=len(question_vectors),
                formula_count=len(formula_vectors),
            )

        except Exception as exc:
            await self.question_repository.mark_embedding_failed_for_document(
                document_id=document_id,
                error_message=str(exc),
            )
            raise
