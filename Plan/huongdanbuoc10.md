# Huong Dan Buoc 10: Tim Kiem Theo Cong Thuc Toan Hoc

## 1. Muc tieu

Buoc 10 bo sung kha nang tim kiem cong thuc toan hoc dua tren collection:

```text
formula_embeddings
```

Sau buoc 9, he thong da co semantic search theo cau hoi:

```text
POST /search/questions
query text
 -> Gemini embedding
 -> Qdrant question_embeddings
 -> PostgreSQL questions
 -> response
```

Buoc 10 tao luong search rieng cho cong thuc:

```text
POST /search/formulas
latex query
 -> normalize LaTeX
 -> build formula embedding text
 -> Gemini embedding
 -> Qdrant formula_embeddings
 -> PostgreSQL questions
 -> response gom formula hit + question context
```

Ket qua can dat:

```text
- Search duoc cong thuc tu input LaTeX.
- Search trong Qdrant collection formula_embeddings.
- Moi ket qua tra ve latex, normalized_latex, source, formula_index.
- Moi ket qua co them context cua Question tu PostgreSQL.
- Khong tra question co embedding_status khac completed.
- Co API POST /search/formulas.
- Co unit test service va repository.
- Co script integration test voi PostgreSQL + Qdrant + Gemini.
```

Buoc 10 chua lam:

```text
- Chua lam symbolic equivalence bang SymPy.
- Chua so sanh cau truc cay bieu thuc nang cao.
- Chua tao frontend formula search.
- Chua tao ranking hybrid giua vector score va symbolic score.
- Chua retry/backoff cho Gemini 429.
```

## 2. Hien trang dau vao

He thong hien co:

```text
modules/semantic_search/
  schemas.py
  service.py

infra/vector_db/repositories/embeddings.py
  search_questions(...)

apps/api/v1/models/search.py
  QuestionSearchRequest
  QuestionSearchResponse

apps/api/v1/endpoints/search.py
  POST /search/questions

modules/embeddings/text_builder.py
  build_formula_embedding_text(...)

modules/question_segmenter/formula_extractor.py
  normalize_formula(...)

Qdrant:
  question_embeddings
  formula_embeddings
```

Collection `formula_embeddings` da co payload dang:

```python
{
    "question_id": formula.question_id,
    "document_id": formula.document_id,
    "formula_index": formula.formula_index,
    "latex": formula.latex,
    "normalized_latex": formula.normalized_latex,
    "source": formula.source,
}
```

Buoc 10 se dung chinh payload nay de tra ket qua.

## 3. Nguyen tac thiet ke

### 3.1 Formula search tach khoi question search

Khong nen nhet formula search vao `search_questions`.

Ly do:

```text
- Input formula la LaTeX, khac input text tu nhien.
- Collection search la formula_embeddings, khong phai question_embeddings.
- Response can formula_index, latex, normalized_latex, source.
- Buoc 10 sau nay co the them symbolic score rieng.
```

### 3.2 Van enrich ket qua tu PostgreSQL

Qdrant chi tra formula hit:

```text
question_id
document_id
formula_index
latex
normalized_latex
source
score
```

Nhung API can them context:

```text
marker
marker_number
statement
solution
answer
subject
chapter
difficulty
skills
```

Nen service phai lay lai questions tu PostgreSQL bang:

```python
QuestionRepository.list_by_ids(...)
```

### 3.3 Chuan hoa cong thuc truoc khi embed

Input:

```text
  x ^ 2   +   1
```

can normalize thanh:

```text
x ^ 2 + 1
```

Dung lai:

```python
normalize_formula(...)
```

tu:

```text
modules/question_segmenter/formula_extractor.py
```

### 3.4 Dung cung text builder voi pipeline embedding

Khi tao formula vector o buoc 8, he thong dung:

```python
build_formula_embedding_text(normalized_latex)
```

Khi search formula, query cung phai dung ham nay.

Neu embed luc luu va embed luc search khac format, similarity se kem on dinh.

## 4. Cau truc can bo sung va sua

Sua:

```text
modules/semantic_search/schemas.py
modules/semantic_search/service.py
modules/semantic_search/__init__.py
infra/vector_db/repositories/embeddings.py
apps/api/v1/models/search.py
apps/api/v1/endpoints/search.py
```

Them:

```text
tests/modules/semantic_search/test_formula_service.py
tests/modules/embeddings/test_formula_vector_search_repository.py
scripts/test_formula_search.py
```

Khong can migration database trong buoc 10.

Ly do:

```text
- Formulas da luu trong questions.formulas.
- Formula vectors da luu trong Qdrant formula_embeddings.
- Payload Qdrant da co du field can tra ve.
```

## 5. Mo rong `modules/semantic_search/schemas.py`

Mo:

```text
modules/semantic_search/schemas.py
```

Sau class `QuestionSearchResult`, them:

```python

@dataclass(frozen=True)
class FormulaSearchFilters:
    source: str | None = None


@dataclass(frozen=True)
class FormulaSearchVectorHit:
    question_id: str
    document_id: str
    formula_index: int
    latex: str
    normalized_latex: str
    source: str
    score: float


@dataclass(frozen=True)
class FormulaSearchResult:
    question_id: str
    document_id: str
    formula_index: int
    latex: str
    normalized_latex: str
    source: str
    score: float
    marker: str
    marker_number: str
    statement: str
    solution: str | None
    answer: str | None
    subject: str | None
    chapter: str | None
    difficulty: str | None
    skills: list[str]
```

Y nghia:

```text
FormulaSearchFilters:
  Loc cong thuc theo source statement/solution/answer.

FormulaSearchVectorHit:
  Ket qua tho tu Qdrant formula_embeddings.

FormulaSearchResult:
  Ket qua cuoi cung sau khi enrich question tu PostgreSQL.
```

## 6. Cap nhat `modules/semantic_search/service.py`

Mo:

```text
modules/semantic_search/service.py
```

### 6.1 Them import

Sua import schemas tu:

```python
from modules.semantic_search.schemas import (
    QuestionSearchFilters,
    QuestionSearchResult,
    QuestionSearchVectorHit,
)
```

thanh:

```python
from modules.semantic_search.schemas import (
    FormulaSearchFilters,
    FormulaSearchResult,
    FormulaSearchVectorHit,
    QuestionSearchFilters,
    QuestionSearchResult,
    QuestionSearchVectorHit,
)
```

Them import:

```python
from modules.embeddings.text_builder import build_formula_embedding_text
from modules.question_segmenter.formula_extractor import normalize_formula
```

### 6.2 Mo rong Protocol

Sau method `search_questions(...)` trong `QuestionVectorSearchRepository`, them:

```python
    async def search_formulas(
        self,
        *,
        vector: list[float],
        limit: int,
        filters: FormulaSearchFilters,
    ) -> list[FormulaSearchVectorHit]:
        ...
```

Sau khi sua, Protocol co dang:

```python
class QuestionVectorSearchRepository(Protocol):
    async def search_questions(
        self,
        *,
        vector: list[float],
        limit: int,
        filters: QuestionSearchFilters,
    ) -> list[QuestionSearchVectorHit]:
        ...

    async def search_formulas(
        self,
        *,
        vector: list[float],
        limit: int,
        filters: FormulaSearchFilters,
    ) -> list[FormulaSearchVectorHit]:
        ...
```

Co the doi ten Protocol thanh `VectorSearchRepository`, nhung MVP co the giu ten cu de giam sua doi.

### 6.3 Them method `search_formulas`

Them method sau vao class `SemanticSearchService`, sau `search_questions`:

```python
    async def search_formulas(
        self,
        *,
        latex: str,
        limit: int = 10,
        filters: FormulaSearchFilters | None = None,
    ) -> list[FormulaSearchResult]:
        normalized_latex = normalize_formula(latex)

        if not normalized_latex:
            raise ValueError("Formula query must not be empty")

        if limit < 1 or limit > 50:
            raise ValueError("Search limit must be between 1 and 50")

        filters = filters or FormulaSearchFilters()

        query_vector = await asyncio.to_thread(
            self.embedder.embed_text,
            build_formula_embedding_text(normalized_latex),
        )

        hits = await self.vector_repository.search_formulas(
            vector=query_vector,
            limit=limit,
            filters=filters,
        )

        if not hits:
            return []

        question_ids = [hit.question_id for hit in hits]
        questions = await self.question_repository.list_by_ids(question_ids)
        questions_by_id = {
            question.id: question
            for question in questions
        }

        results: list[FormulaSearchResult] = []

        for hit in hits:
            question = questions_by_id.get(hit.question_id)

            if question is None:
                continue

            if question.embedding_status != "completed":
                continue

            results.append(
                FormulaSearchResult(
                    question_id=question.id,
                    document_id=question.document_id,
                    formula_index=hit.formula_index,
                    latex=hit.latex,
                    normalized_latex=hit.normalized_latex,
                    source=hit.source,
                    score=hit.score,
                    marker=question.marker,
                    marker_number=question.marker_number,
                    statement=question.statement,
                    solution=question.solution,
                    answer=question.answer,
                    subject=question.subject,
                    chapter=question.chapter,
                    difficulty=question.difficulty,
                    skills=question.skills,
                )
            )

        return results
```

### 6.4 Vi sao khong dung raw latex de embed

Khong nen:

```python
self.embedder.embed_text(latex)
```

Nen dung:

```python
build_formula_embedding_text(normalized_latex)
```

Vi pipeline tao formula embedding cung dung format:

```text
task: sentence similarity | query: mathematical formula: ...
```

Search query va stored vector can cung "ngon ngu embedding".

## 7. Cap nhat `modules/semantic_search/__init__.py`

Mo:

```text
modules/semantic_search/__init__.py
```

Sua import schemas thanh:

```python
from modules.semantic_search.schemas import (
    FormulaSearchFilters,
    FormulaSearchResult,
    FormulaSearchVectorHit,
    QuestionSearchFilters,
    QuestionSearchResult,
    QuestionSearchVectorHit,
)
```

Sua `__all__` thanh:

```python
__all__ = [
    "FormulaSearchFilters",
    "FormulaSearchResult",
    "FormulaSearchVectorHit",
    "QuestionSearchFilters",
    "QuestionSearchResult",
    "QuestionSearchVectorHit",
    "SemanticSearchService",
]
```

## 8. Them `search_formulas` vao Qdrant repository

Mo:

```text
infra/vector_db/repositories/embeddings.py
```

### 8.1 Cap nhat import

Hien file da import:

```python
from modules.semantic_search.schemas import (
    QuestionSearchFilters,
    QuestionSearchVectorHit,
)
```

Sua thanh:

```python
from modules.semantic_search.schemas import (
    FormulaSearchFilters,
    FormulaSearchVectorHit,
    QuestionSearchFilters,
    QuestionSearchVectorHit,
)
```

### 8.2 Them method `search_formulas`

Them method sau vao class `EmbeddingVectorRepository`, sau `search_questions`:

```python
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
```

### 8.3 Vi sao filter chi co `source`

Payload formula hien co:

```text
question_id
document_id
formula_index
latex
normalized_latex
source
```

Chua co:

```text
subject
chapter
difficulty
skills
```

Nen MVP buoc 10 chi filter truc tiep trong Qdrant theo `source`.

Neu muon filter formula theo subject/chapter/difficulty, co 2 cach sau nay:

```text
1. Them metadata subject/chapter/difficulty vao FormulaVector payload khi upsert.
2. Search formula truoc, enrich PostgreSQL sau, roi loc trong service.
```

MVP nen giu don gian.

## 9. Cap nhat API models

Mo:

```text
apps/api/v1/models/search.py
```

Sau `QuestionSearchResponse`, them:

```python

class FormulaSearchRequest(BaseModel):
    latex: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)
    source: str | None = None


class FormulaSearchItem(BaseModel):
    question_id: str
    document_id: str
    formula_index: int
    latex: str
    normalized_latex: str
    source: str
    score: float
    marker: str
    marker_number: str
    statement: str
    solution: str | None = None
    answer: str | None = None
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str]


class FormulaSearchResponse(BaseModel):
    latex: str
    results: list[FormulaSearchItem]
```

### 9.1 Vi sao request dung `latex`

Cong thuc search nen ro nghia:

```json
{
  "latex": "x^2 + 1",
  "limit": 5
}
```

Khong nen dung `query` chung chung vi API da co:

```text
QuestionSearchRequest.query
```

## 10. Cap nhat search endpoint

Mo:

```text
apps/api/v1/endpoints/search.py
```

### 10.1 Cap nhat import models

Hien dang co:

```python
from apps.api.v1.models.search import (
    QuestionSearchItem,
    QuestionSearchRequest,
    QuestionSearchResponse,
)
```

Sua thanh:

```python
from apps.api.v1.models.search import (
    FormulaSearchItem,
    FormulaSearchRequest,
    FormulaSearchResponse,
    QuestionSearchItem,
    QuestionSearchRequest,
    QuestionSearchResponse,
)
```

### 10.2 Cap nhat import semantic search

Hien dang co:

```python
from modules.semantic_search import (
    QuestionSearchFilters,
    SemanticSearchService,
)
```

Sua thanh:

```python
from modules.semantic_search import (
    FormulaSearchFilters,
    QuestionSearchFilters,
    SemanticSearchService,
)
```

### 10.3 Them endpoint `POST /search/formulas`

Them sau endpoint `search_questions`:

```python

@router.post("/formulas", response_model=FormulaSearchResponse)
async def search_formulas(
    request: FormulaSearchRequest,
    session: AsyncSession = Depends(get_db_session),
) -> FormulaSearchResponse:
    client = create_qdrant_client()

    try:
        service = SemanticSearchService(
            question_repository=QuestionRepository(session),
            vector_repository=EmbeddingVectorRepository(
                client=client,
                dimension=settings.embedding_dimension,
                question_collection=settings.qdrant_question_collection,
                formula_collection=settings.qdrant_formula_collection,
            ),
            embedder=GeminiEmbedder(),
        )

        results = await service.search_formulas(
            latex=request.latex,
            limit=request.limit,
            filters=FormulaSearchFilters(
                source=request.source,
            ),
        )

        return FormulaSearchResponse(
            latex=request.latex,
            results=[
                FormulaSearchItem(
                    question_id=result.question_id,
                    document_id=result.document_id,
                    formula_index=result.formula_index,
                    latex=result.latex,
                    normalized_latex=result.normalized_latex,
                    source=result.source,
                    score=result.score,
                    marker=result.marker,
                    marker_number=result.marker_number,
                    statement=result.statement,
                    solution=result.solution,
                    answer=result.answer,
                    subject=result.subject,
                    chapter=result.chapter,
                    difficulty=result.difficulty,
                    skills=result.skills,
                )
                for result in results
            ],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()
```

### 10.4 Kiem tra Swagger

Chay:

```powershell
uvicorn apps.api.main:app --reload
```

Mo:

```text
http://localhost:8000/docs
```

Can thay:

```text
search
  POST /search/questions
  POST /search/formulas
```

## 11. Unit test FormulaSearchService

Tao file:

```text
tests/modules/semantic_search/test_formula_service.py
```

Them:

```python
import asyncio
from types import SimpleNamespace

import pytest

from modules.semantic_search import (
    FormulaSearchFilters,
    FormulaSearchVectorHit,
    SemanticSearchService,
)


class FakeQuestionRepository:
    def __init__(self, questions) -> None:
        self.questions = questions
        self.question_ids = None

    async def list_by_ids(self, question_ids: list[str]):
        self.question_ids = question_ids
        questions_by_id = {
            question.id: question
            for question in self.questions
        }

        return [
            questions_by_id[question_id]
            for question_id in question_ids
            if question_id in questions_by_id
        ]


class FakeVectorRepository:
    def __init__(self, hits) -> None:
        self.hits = hits
        self.vector = None
        self.limit = None
        self.filters = None

    async def search_questions(self, **kwargs):
        return []

    async def search_formulas(
        self,
        *,
        vector: list[float],
        limit: int,
        filters: FormulaSearchFilters,
    ):
        self.vector = vector
        self.limit = limit
        self.filters = filters
        return self.hits


class FakeEmbedder:
    def __init__(self) -> None:
        self.texts = []

    def embed_text(self, text: str) -> list[float]:
        self.texts.append(text)
        return [0.1, 0.2, 0.3]


def make_question(
    *,
    question_id: str,
    embedding_status: str = "completed",
):
    return SimpleNamespace(
        id=question_id,
        document_id="document-id",
        marker="Bai",
        marker_number="27",
        statement="Tinh $x^2 + 1$.",
        solution=None,
        answer=None,
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
        embedding_status=embedding_status,
    )


def test_search_formulas_returns_enriched_results_in_score_order() -> None:
    q1 = make_question(question_id="q1")
    q2 = make_question(question_id="q2")

    vector_repository = FakeVectorRepository(
        [
            FormulaSearchVectorHit(
                question_id="q2",
                document_id="document-id",
                formula_index=1,
                latex="x^2 + 1",
                normalized_latex="x^2 + 1",
                source="statement",
                score=0.96,
            ),
            FormulaSearchVectorHit(
                question_id="q1",
                document_id="document-id",
                formula_index=0,
                latex="x^2",
                normalized_latex="x^2",
                source="answer",
                score=0.91,
            ),
        ]
    )
    question_repository = FakeQuestionRepository([q1, q2])
    embedder = FakeEmbedder()

    service = SemanticSearchService(
        question_repository=question_repository,
        vector_repository=vector_repository,
        embedder=embedder,
    )

    results = asyncio.run(
        service.search_formulas(
            latex="  x^2   +   1  ",
            limit=2,
            filters=FormulaSearchFilters(source="statement"),
        )
    )

    assert embedder.texts == [
        "task: sentence similarity | query: mathematical formula: x^2 + 1"
    ]
    assert vector_repository.vector == [0.1, 0.2, 0.3]
    assert vector_repository.limit == 2
    assert vector_repository.filters.source == "statement"
    assert question_repository.question_ids == ["q2", "q1"]

    assert [result.question_id for result in results] == ["q2", "q1"]
    assert results[0].formula_index == 1
    assert results[0].normalized_latex == "x^2 + 1"
    assert results[0].score == 0.96


def test_search_formulas_rejects_empty_formula() -> None:
    service = SemanticSearchService(
        question_repository=FakeQuestionRepository([]),
        vector_repository=FakeVectorRepository([]),
        embedder=FakeEmbedder(),
    )

    with pytest.raises(ValueError, match="Formula query must not be empty"):
        asyncio.run(service.search_formulas(latex="   "))


def test_search_formulas_rejects_invalid_limit() -> None:
    service = SemanticSearchService(
        question_repository=FakeQuestionRepository([]),
        vector_repository=FakeVectorRepository([]),
        embedder=FakeEmbedder(),
    )

    with pytest.raises(ValueError, match="Search limit"):
        asyncio.run(service.search_formulas(latex="x^2", limit=100))


def test_search_formulas_skips_non_completed_questions() -> None:
    question = make_question(
        question_id="q1",
        embedding_status="failed",
    )

    service = SemanticSearchService(
        question_repository=FakeQuestionRepository([question]),
        vector_repository=FakeVectorRepository(
            [
                FormulaSearchVectorHit(
                    question_id="q1",
                    document_id="document-id",
                    formula_index=0,
                    latex="x^2",
                    normalized_latex="x^2",
                    source="statement",
                    score=0.90,
                )
            ]
        ),
        embedder=FakeEmbedder(),
    )

    results = asyncio.run(service.search_formulas(latex="x^2"))

    assert results == []
```

Chay:

```powershell
pytest tests/modules/semantic_search -q
```

Ket qua mong doi:

```text
8 passed
```

## 12. Unit test Qdrant formula search repository

Tao file:

```text
tests/modules/embeddings/test_formula_vector_search_repository.py
```

Them:

```python
import asyncio
from types import SimpleNamespace

from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.semantic_search import FormulaSearchFilters


class FakeQdrantClient:
    def __init__(self) -> None:
        self.collection_name = None
        self.query = None
        self.query_filter = None
        self.limit = None
        self.with_payload = None
        self.with_vectors = None

    async def collection_exists(self, collection_name: str) -> bool:
        return True

    async def query_points(
        self,
        *,
        collection_name,
        query,
        query_filter,
        limit,
        with_payload,
        with_vectors,
    ):
        self.collection_name = collection_name
        self.query = query
        self.query_filter = query_filter
        self.limit = limit
        self.with_payload = with_payload
        self.with_vectors = with_vectors

        return SimpleNamespace(
            points=[
                SimpleNamespace(
                    score=0.94,
                    payload={
                        "question_id": "question-id",
                        "document_id": "document-id",
                        "formula_index": 2,
                        "latex": "x^2 + 1",
                        "normalized_latex": "x^2 + 1",
                        "source": "statement",
                    },
                )
            ]
        )


def test_search_formulas_calls_qdrant_with_filters() -> None:
    client = FakeQdrantClient()
    repository = EmbeddingVectorRepository(
        client=client,
        dimension=3,
        question_collection="question_embeddings",
        formula_collection="formula_embeddings",
    )

    hits = asyncio.run(
        repository.search_formulas(
            vector=[0.1, 0.2, 0.3],
            limit=5,
            filters=FormulaSearchFilters(source="statement"),
        )
    )

    assert client.collection_name == "formula_embeddings"
    assert client.query == [0.1, 0.2, 0.3]
    assert client.limit == 5
    assert client.with_payload is True
    assert client.with_vectors is False
    assert client.query_filter is not None

    assert len(hits) == 1
    assert hits[0].question_id == "question-id"
    assert hits[0].document_id == "document-id"
    assert hits[0].formula_index == 2
    assert hits[0].latex == "x^2 + 1"
    assert hits[0].normalized_latex == "x^2 + 1"
    assert hits[0].source == "statement"
    assert hits[0].score == 0.94
```

Chay:

```powershell
pytest tests/modules/embeddings/test_formula_vector_search_repository.py -q
```

Ket qua mong doi:

```text
1 passed
```

## 13. Tao script integration formula search

Tao:

```text
scripts/test_formula_search.py
```

Them:

```python
import asyncio

from core.config.settings import settings
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder
from modules.semantic_search import (
    FormulaSearchFilters,
    SemanticSearchService,
)


async def main() -> None:
    async with AsyncSessionLocal() as session:
        client = create_qdrant_client()

        try:
            service = SemanticSearchService(
                question_repository=QuestionRepository(session),
                vector_repository=EmbeddingVectorRepository(
                    client=client,
                    dimension=settings.embedding_dimension,
                    question_collection=settings.qdrant_question_collection,
                    formula_collection=settings.qdrant_formula_collection,
                ),
                embedder=GeminiEmbedder(),
            )

            results = await service.search_formulas(
                latex=r"(1+i\sqrt{3})^{9}",
                limit=5,
                filters=FormulaSearchFilters(),
            )

            if not results:
                print("No formula search results were found")
                return

            for index, result in enumerate(results, start=1):
                print()
                print("Rank:", index)
                print("Score:", result.score)
                print("Question ID:", result.question_id)
                print("Document ID:", result.document_id)
                print("Question:", result.marker, result.marker_number)
                print("Formula index:", result.formula_index)
                print("Latex:", result.latex)
                print("Normalized:", result.normalized_latex)
                print("Source:", result.source)
                print("Statement:", result.statement[:300])
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Chay:

```powershell
python -m scripts.test_formula_search
```

Ket qua mong doi voi `bttx.md`:

```text
Rank: 1
Score: ...
Question: Bai 28
Formula index: ...
Latex: ...
Normalized: ...
Source: statement
```

Luu y:

```text
Score khong can giong tuyet doi.
Voi corpus nho, ket qua co the chi la cong thuc gan nhat trong 7 formula hien co.
```

## 14. Test API formula search

Dam bao backend dang chay:

```powershell
uvicorn apps.api.main:app --reload
```

Dung PowerShell:

```powershell
$body = @{
  latex = "(1+i\sqrt{3})^{9}"
  limit = 5
} | ConvertTo-Json

$response = Invoke-RestMethod `
  -Uri "http://localhost:8000/search/formulas" `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $body

$response | ConvertTo-Json -Depth 10
```

Ket qua mong doi:

```json
{
  "latex": "(1+i\\sqrt{3})^{9}",
  "results": [
    {
      "question_id": "...",
      "document_id": "...",
      "formula_index": 0,
      "latex": "...",
      "normalized_latex": "...",
      "source": "statement",
      "score": 0.9,
      "marker": "Bai",
      "marker_number": "28",
      "statement": "..."
    }
  ]
}
```

Test query rong:

```powershell
$body = @{
  latex = "    "
  limit = 5
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:8000/search/formulas" `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
```

Ket qua mong doi:

```text
400 Bad Request
Formula query must not be empty
```

Test limit qua lon:

```powershell
$body = @{
  latex = "x^2"
  limit = 100
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:8000/search/formulas" `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
```

Ket qua mong doi:

```text
422 Unprocessable Entity
limit must be <= 50
```

## 15. Kiem tra sync truoc khi formula search

Buoc 10 phu thuoc vao formula_embeddings da co du point.

Chay:

```powershell
python -m scripts.sync_question_storage
python -m scripts.check_question_embedding_sync
```

Ket qua dung:

```text
PostgreSQL embedding statuses: {'completed': 2}
Qdrant question points: 2
Qdrant formula points: 7
```

Neu thay:

```text
PostgreSQL embedding statuses: {'failed': 2}
```

thi khong nen ket luan formula search sai. Can sync lai khi Gemini het 429:

```powershell
python -m scripts.sync_question_storage
```

## 16. Chay test tong the

Chay:

```powershell
pytest tests/modules/semantic_search -q
pytest tests/modules/embeddings/test_formula_vector_search_repository.py -q
pytest tests/modules -q
pytest -q
```

Chay compile:

```powershell
python -m compileall apps/api core infra modules tests scripts
```

Chay integration:

```powershell
python -m scripts.sync_question_storage
python -m scripts.check_question_embedding_sync
python -m scripts.test_formula_search
```

Chay API test:

```powershell
uvicorn apps.api.main:app --reload
```

Mo:

```text
http://localhost:8000/docs
```

Can thay:

```text
POST /search/questions
POST /search/formulas
```

## 17. Loi thuong gap

### 17.1 `No formula search results were found`

Nguyen nhan co the:

```text
- Qdrant formula_embeddings chua co point.
- PostgreSQL questions dang embedding_status = failed.
- Query formula qua khac corpus hien co.
```

Kiem tra:

```powershell
python -m scripts.check_question_embedding_sync
```

Can thay:

```text
Qdrant formula points: 7
PostgreSQL embedding statuses: {'completed': 2}
```

### 17.2 API tra rong du Qdrant co formula points

Nguyen nhan thuong gap:

```text
SemanticSearchService loc embedding_status != completed.
```

Kiem tra:

```powershell
python -m scripts.check_question_embedding_sync
```

Neu dang:

```text
{'failed': 2}
```

thi chay lai:

```powershell
python -m scripts.sync_question_storage
```

### 17.3 Gemini 429 RESOURCE_EXHAUSTED

Nguyen nhan:

```text
sync_question_storage goi nhieu embedding request lien tiep.
Voi bttx.md hien tai: 2 question vectors + 7 formula vectors = 9 request.
```

Xu ly tam thoi:

```text
- Doi quota/rate limit hoi lai.
- Khong chay sync lien tuc.
- Chay lai sync sau vai phut.
```

Mo rong sau MVP:

```text
- Them retry/backoff.
- Them delay giua cac lan embed formula.
- Cache embedding theo normalized_latex.
```

### 17.4 `AttributeError: AsyncQdrantClient has no attribute query_points`

Nguyen nhan:

```text
qdrant-client qua cu.
```

Xu ly:

```powershell
pip install -U qdrant-client
```

### 17.5 Filter `source` khong co ket qua

Neu request:

```json
{
  "latex": "x^2",
  "source": "answer"
}
```

ma corpus chi co formulas trong statement, ket qua se rong.

Voi `bttx.md`, formulas kha nang cao la:

```text
source = statement
```

Hay test:

```json
{
  "latex": "(1+i\\sqrt{3})^{9}",
  "source": "statement"
}
```

## 18. Mo rong sau MVP

### 18.1 Symbolic equivalence

Vector search chi biet gan nghia/gan bieu dien.

Sau MVP, co the them SymPy de nhan biet:

```text
x^2 + 2x + 1
(x + 1)^2
```

la tuong duong.

Huong lam:

```text
LaTeX -> SymPy expression -> simplify(expr1 - expr2) == 0
```

Luu y:

```text
LaTeX parsing co the loi voi expression phuc tap.
Nen dung symbolic score nhu tin hieu phu, khong thay the vector search.
```

### 18.2 Hybrid ranking

Diem cuoi co the gom:

```text
final_score = 0.7 * vector_score + 0.3 * symbolic_score
```

Trong do:

```text
vector_score: Qdrant cosine similarity
symbolic_score: exact/partial structural match
```

### 18.3 Them metadata vao formula payload

De filter Qdrant truc tiep theo subject/chapter/difficulty, mo rong `FormulaVector`:

```text
subject
chapter
difficulty
skills
```

Sau do update payload trong:

```text
EmbeddingVectorRepository.replace_for_document
```

### 18.4 Cache formula query embedding

Nguoi dung co the search lai cung mot cong thuc nhieu lan.

Co the cache theo:

```text
normalized_latex + embedding_model + embedding_dimension
```

De giam Gemini calls va tranh 429.

## 19. Thu tu trien khai khuyen nghi

Lam lan luot:

```text
1. Mo rong modules/semantic_search/schemas.py voi FormulaSearch* dataclasses.
2. Export FormulaSearch* trong modules/semantic_search/__init__.py.
3. Them search_formulas vao SemanticSearchService.
4. Them search_formulas vao EmbeddingVectorRepository.
5. Them FormulaSearchRequest/Item/Response vao apps/api/v1/models/search.py.
6. Them endpoint POST /search/formulas vao apps/api/v1/endpoints/search.py.
7. Chay compileall cac file vua sua.
8. Viet tests/modules/semantic_search/test_formula_service.py.
9. Chay pytest tests/modules/semantic_search -q.
10. Viet tests/modules/embeddings/test_formula_vector_search_repository.py.
11. Chay pytest tests/modules/embeddings/test_formula_vector_search_repository.py -q.
12. Tao scripts/test_formula_search.py.
13. Chay python -m scripts.sync_question_storage.
14. Chay python -m scripts.check_question_embedding_sync.
15. Chay python -m scripts.test_formula_search.
16. Test API POST /search/formulas bang Swagger hoac Invoke-RestMethod.
17. Chay pytest -q.
18. Chay python -m compileall apps/api core infra modules tests scripts.
```

## 20. Tieu chi hoan thanh

Buoc 10 MVP hoan tat khi:

```text
1. Co FormulaSearchFilters, FormulaSearchVectorHit, FormulaSearchResult.
2. SemanticSearchService co search_formulas.
3. search_formulas normalize input LaTeX.
4. search_formulas dung build_formula_embedding_text.
5. EmbeddingVectorRepository co search_formulas.
6. search_formulas cua repository query vao formula_embeddings.
7. Qdrant formula search parse payload formula_index/latex/normalized_latex/source.
8. API co POST /search/formulas.
9. Swagger hien POST /search/formulas.
10. Unit test formula service pass.
11. Unit test formula vector repository pass.
12. API reject latex rong/toan space.
13. API reject limit > 50.
14. Integration script test_formula_search tra Rank/Score/Formula.
15. check_question_embedding_sync hien Qdrant formula points dung.
16. Tat ca test cu van pass.
17. compileall toan project khong loi.
```

Sau buoc 10, he thong san sang cho:

```text
- Buoc 11: sinh cau hoi moi dua tren cau hoi/cong thuc tuong tu.
- Mo rong formula matching bang symbolic equivalence.
- Frontend search theo cong thuc.
```
