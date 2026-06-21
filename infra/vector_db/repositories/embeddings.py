from uuid import NAMESPACE_URL, uuid5

from qdrant_client import AsyncQdrantClient, models

from modules.embeddings.schemas import FormulaVector, QuestionVector

from modules.semantic_search.schemas import (
    FormulaSearchFilters,
    FormulaSearchVectorHit,
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
                    "question_type": question.question_type,
                    "subject": question.subject,
                    "chapter": question.chapter,
                    "difficulty": question.difficulty,
                    "skills": question.skills,
                    "subject_code": question.subject_code,
                    "chapter_code": question.chapter_code,
                    "chapter_name": question.chapter_name,
                    "topic_code": question.topic_code,
                    "topic_name": question.topic_name,
                    "problem_type_code": question.problem_type_code,
                    "problem_type_name": question.problem_type_name,
                    "taxonomy_confidence": question.taxonomy_confidence,
                    "review_status": question.review_status,
                    "classification_status": question.classification_status,
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

    async def update_question_classification_payload(
        self,
        question,
    ) -> None:
        await self.ensure_collections()

        await self.client.set_payload(
            collection_name=self.question_collection,
            payload={
                "subject": question.subject,
                "chapter": question.chapter,
                "difficulty": question.difficulty,
                "skills": question.skills,
                "subject_code": question.subject_code,
                "chapter_code": question.chapter_code,
                "chapter_name": question.chapter_name,
                "topic_code": question.topic_code,
                "topic_name": question.topic_name,
                "problem_type_code": question.problem_type_code,
                "problem_type_name": question.problem_type_name,
                "taxonomy_confidence": question.taxonomy_confidence,
                "taxonomy_reason": question.taxonomy_reason,
                "review_status": question.review_status,
                "classification_status": question.classification_status,
            },
            points=[question.id],
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

        if filters.question_type:
            must_conditions.append(
                models.FieldCondition(
                    key="question_type",
                    match=models.MatchValue(value=filters.question_type),
                )
            )

        if filters.chapter_code:
            must_conditions.append(
                models.FieldCondition(
                    key="chapter_code",
                    match=models.MatchValue(value=filters.chapter_code),
                )
            )

        if filters.topic_code:
            must_conditions.append(
                models.FieldCondition(
                    key="topic_code",
                    match=models.MatchValue(value=filters.topic_code),
                )
            )

        if filters.problem_type_code:
            must_conditions.append(
                models.FieldCondition(
                    key="problem_type_code",
                    match=models.MatchValue(value=filters.problem_type_code),
                )
            )

        if filters.skill:
            must_conditions.append(
                models.FieldCondition(
                    key="skills",
                    match=models.MatchValue(value=filters.skill),
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
    
    async def search_formulas(
        self,
        *,
        vector: list[float],
        limit: int,
        filters: FormulaSearchFilters,
    ) -> list[FormulaSearchVectorHit]:
        await self.ensure_collections()

        must_conditions: list[models.FieldCondition] = []

        if filters.source:
            must_conditions.append(
                models.FieldCondition(
                    key="source",
                    match=models.MatchValue(value=filters.source),
                )
            )

        query_filter = None
        if must_conditions:
            query_filter = models.Filter(must=must_conditions)

        result = await self.client.query_points(
            collection_name=self.formula_collection,
            query=vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        hits: list[FormulaSearchVectorHit] = []

        for point in result.points:
            payload = point.payload or {}
            question_id = payload.get("question_id")
            document_id = payload.get("document_id")
            formula_index = payload.get("formula_index")
            latex = payload.get("latex")
            normalized_latex = payload.get("normalized_latex")
            source = payload.get("source")

            if (
                question_id is None
                or document_id is None
                or formula_index is None
                or latex is None
                or normalized_latex is None
                or source is None
            ):
                continue

            hits.append(
                FormulaSearchVectorHit(
                    question_id=str(question_id),
                    document_id=str(document_id),
                    formula_index=int(formula_index),
                    latex=str(latex),
                    normalized_latex=str(normalized_latex),
                    source=str(source),
                    score=float(point.score),
                )
            )

        return hits
