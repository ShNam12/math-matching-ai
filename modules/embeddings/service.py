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

    async def replace_for_question(
        self,
        *,
        question: QuestionVector,
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
        retry_delays: tuple[float, ...] = (5, 10, 20, 40, 60),
    ) -> None:
        self.question_repository = question_repository
        self.vector_repository = vector_repository
        self.embedder = embedder
        self.retry_delays = retry_delays

    @staticmethod
    def _is_quota_error(error: Exception) -> bool:
        message = str(error).upper()
        status_code = getattr(error, "status_code", None)

        return (
            status_code == 429
            or "429" in message
            or "RESOURCE_EXHAUSTED" in message
            or "QUOTA EXCEEDED" in message
        )

    async def _embed_text_with_retry(self, text: str) -> list[float]:
        for attempt in range(len(self.retry_delays) + 1):
            try:
                return await asyncio.to_thread(self.embedder.embed_text, text)
            except Exception as exc:
                if (
                    not self._is_quota_error(exc)
                    or attempt == len(self.retry_delays)
                ):
                    raise

                await asyncio.sleep(self.retry_delays[attempt])

        raise RuntimeError("Embedding retry loop ended unexpectedly")

    async def embed_document(self, document_id: str) -> EmbeddingResult:
        questions = await self.question_repository.list_by_document(document_id)

        if not questions:
            raise ValueError(
                f"No segmented questions were found: {document_id}"
            )

        targets = [
            question
            for question in questions
            if getattr(question, "embedding_status", "pending") != "completed"
        ]
        embedded_question_count = 0
        embedded_formula_count = 0
        failed_question_ids: list[str] = []
        pending_question_count = 0

        for index, question in enumerate(targets):
            try:
                result = await self.embed_question(question.id)
                embedded_question_count += result.question_count
                embedded_formula_count += result.formula_count
            except Exception as exc:
                failed_question_ids.append(question.id)

                # Continuing after a quota error would only consume more quota.
                # The remaining pending questions can be resumed in a later run.
                if self._is_quota_error(exc):
                    pending_question_count = len(targets) - index - 1
                    break

        return EmbeddingResult(
            document_id=document_id,
            question_count=embedded_question_count,
            formula_count=embedded_formula_count,
            failed_question_ids=tuple(failed_question_ids),
            pending_question_count=pending_question_count,
        )

    async def embed_question(self, question_id: str) -> EmbeddingResult:
        question = await self.question_repository.get_question(question_id)

        if question is None:
            raise ValueError(f"Question was not found: {question_id}")

        await self.question_repository.mark_embedding_pending_for_question(
            question_id
        )

        try:
            question_vector = await self._embed_text_with_retry(
                build_question_embedding_text(question)
            )

            question_item = QuestionVector(
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

            formula_items = []

            for formula_index, formula in enumerate(
                _question_formulas(question)
            ):
                normalized_latex = formula.get(
                    "normalized_latex",
                    "",
                ).strip()

                if not normalized_latex:
                    continue

                formula_vector = await self._embed_text_with_retry(
                    build_formula_embedding_text(normalized_latex)
                )

                formula_items.append(
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

            await self.vector_repository.replace_for_question(
                question=question_item,
                formulas=formula_items,
            )

            await self.question_repository.mark_embedding_completed_for_question(
                question_id=question_id,
                embedding_model=getattr(self.embedder, "model", "unknown"),
                embedding_dimension=getattr(self.embedder, "dimension", 0),
            )

            return EmbeddingResult(
                document_id=question.document_id,
                question_count=1,
                formula_count=len(formula_items),
            )

        except Exception as exc:
            await self.question_repository.mark_embedding_failed_for_question(
                question_id=question_id,
                error_message=str(exc),
            )
            raise
