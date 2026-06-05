from uuid import NAMESPACE_URL, uuid5

from qdrant_client import AsyncQdrantClient, models

from modules.embeddings.schemas import FormulaVector, QuestionVector

from modules.semantic_search.schemas import (
    QuestionSearchFilters,
    QuestionSearchVectorHit,
)

class EmbeddingVectorRepository:
    def __init__(
        self,
        *,
        client: AsyncQdrantClient,
        dimension: int,
        question_collection: str,
        formula_collection: str,
    ) -> None:
        self.client = client
        self.dimension = dimension
        self.question_collection = question_collection
        self.formula_collection = formula_collection

    async def ensure_collections(self) -> None:
        await self._ensure_collection(self.question_collection)
        await self._ensure_collection(self.formula_collection)

    async def _ensure_collection(self, collection_name: str) -> None:
        exists = await self.client.collection_exists(collection_name)

        if exists:
            return

        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=self.dimension,
                distance=models.Distance.COSINE,
            ),
        )

    async def replace_for_document(
        self,
        *,
        document_id: str,
        questions: list[QuestionVector],
        formulas: list[FormulaVector],
    ) -> None:
        await self.ensure_collections()

        await self._delete_document_points(
            collection_name=self.question_collection,
            document_id=document_id,
        )
        await self._delete_document_points(
            collection_name=self.formula_collection,
            document_id=document_id,
        )

        question_points = [
            models.PointStruct(
                id=question.question_id,
                vector=question.vector,
                payload={
                    "question_id": question.question_id,
                    "document_id": question.document_id,
                    "sequence_number": question.sequence_number,
                    "marker": question.marker,
                    "marker_number": question.marker_number,
                    "statement": question.statement,
                    "subject": question.subject,
                    "chapter": question.chapter,
                    "difficulty": question.difficulty,
                    "skills": question.skills,
                },
            )
            for question in questions
        ]

        formula_points = [
            models.PointStruct(
                id=str(
                    uuid5(
                        NAMESPACE_URL,
                        (
                            f"question-formula:{formula.question_id}:"
                            f"{formula.formula_index}"
                        ),
                    )
                ),
                vector=formula.vector,
                payload={
                    "question_id": formula.question_id,
                    "document_id": formula.document_id,
                    "formula_index": formula.formula_index,
                    "latex": formula.latex,
                    "normalized_latex": formula.normalized_latex,
                    "source": formula.source,
                },
            )
            for formula in formulas
        ]

        if question_points:
            await self.client.upsert(
                collection_name=self.question_collection,
                points=question_points,
                wait=True,
            )

        if formula_points:
            await self.client.upsert(
                collection_name=self.formula_collection,
                points=formula_points,
                wait=True,
            )

    async def _delete_document_points(
        self,
        *,
        collection_name: str,
        document_id: str,
    ) -> None:
        await self.client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
            wait=True,
        )

    async def count_for_document(
        self,
        *,
        collection_name: str,
        document_id: str,
    ) -> int:
        result = await self.client.count(
            collection_name=collection_name,
            count_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            ),
            exact=True,
        )

        return result.count
    
    async def search_questions(
        self,
        *,
        vector: list[float],
        limit: int,
        filters: QuestionSearchFilters,
    ) -> list[QuestionSearchVectorHit]:
        await self.ensure_collections()

        must_conditions: list[models.FieldCondition] = []

        if filters.subject:
            must_conditions.append(
                models.FieldCondition(
                    key="subject",
                    match=models.MatchValue(value=filters.subject),
                )
            )

        if filters.chapter:
            must_conditions.append(
                models.FieldCondition(
                    key="chapter",
                    match=models.MatchValue(value=filters.chapter),
                )
            )

        if filters.difficulty:
            must_conditions.append(
                models.FieldCondition(
                    key="difficulty",
                    match=models.MatchValue(value=filters.difficulty),
                )
            )

        query_filter = None
        if must_conditions:
            query_filter = models.Filter(must=must_conditions)

        result = await self.client.query_points(
            collection_name=self.question_collection,
            query=vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        hits: list[QuestionSearchVectorHit] = []

        for point in result.points:
            payload = point.payload or {}
            question_id = payload.get("question_id")
            document_id = payload.get("document_id")

            if not question_id or not document_id:
                continue

            hits.append(
                QuestionSearchVectorHit(
                    question_id=str(question_id),
                    document_id=str(document_id),
                    score=float(point.score),
                )
            )

        return hits