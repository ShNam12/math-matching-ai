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
                        subject=question.subject,
                        chapter=question.chapter,
                        difficulty=question.difficulty,
                        skills=question.skills,
                        vector=question_vector,
                    )
                )

                for formula_index, formula in enumerate(question.formulas):
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
