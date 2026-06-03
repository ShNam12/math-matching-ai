# Huong Dan Buoc 7: Tao Embedding Cho Cau Hoi

## 1. Muc tieu

Buoc 7 tao vector embedding cho du lieu cau hoi da duoc luu trong PostgreSQL o buoc 6 va dua vector vao Qdrant.

Luong xu ly sau khi hoan thanh:

```text
PostgreSQL questions
 -> tao text dai dien cho tung cau hoi
 -> Gemini Embedding API
 -> question vector
 -> luu vao Qdrant collection question_embeddings

questions.formulas
 -> lay tung normalized_latex
 -> Gemini Embedding API
 -> formula vector
 -> luu vao Qdrant collection formula_embeddings
```

Ket qua can dat:

```text
- Moi Question co mot vector dai dien cho noi dung bai toan.
- Moi cong thuc trong Question co mot vector rieng.
- Vector duoc luu trong Qdrant, khong luu truc tiep vao PostgreSQL.
- Payload Qdrant giu question_id va document_id de truy vet ve PostgreSQL.
- Chay lai embedding cho cung document khong tao vector rac.
```

Buoc 7 chua lam:

```text
- Chua tao API semantic search.
- Chua sua frontend.
- Chua tu dong chay embedding ngay sau ingestion.
- Chua tu dong chay embedding ngay sau segmentation.
- Chua them worker queue.
- Chua toi uu batch embedding cho kho du lieu lon.
- Chua danh gia chat luong retrieval bang benchmark rieng.
```

API search va giao dien search thuoc buoc 9. Dong bo nang cao giua PostgreSQL va Qdrant thuoc buoc 8.

## 2. Hien trang dau vao

Sau buoc 6, PostgreSQL da co bang:

```text
questions
```

Model hien tai:

```text
infra/db/models.py
```

Moi `Question` da co:

```python
id
document_id
sequence_number
marker
marker_number
statement
solution
answer
formulas
subject
chapter
difficulty
skills
```

Repository hien tai:

```text
infra/db/repositories/questions.py
```

Da co ham:

```python
list_by_document(document_id)
get_question(question_id)
```

Du lieu cong thuc dang JSON:

```json
[
  {
    "latex": "x^2   + 1",
    "normalized_latex": "x^2 + 1",
    "source": "statement"
  }
]
```

File mau `Plan/bttx.md` sau khi segment tao:

```text
Bai 27 -> 4 formulas
Bai 28 -> 3 formulas
```

Tong cong:

```text
2 question vectors
7 formula vectors
```

## 3. Quyet dinh thiet ke

### 3.1 Chon Gemini Embedding API

Du an hien da dung:

```text
google-genai
GEMINI_API_KEY
```

Vi vay buoc 7 nen tiep tuc dung Gemini API, khong them mot provider khac trong MVP.

Tai thoi diem viet huong dan nay, model embedding moi va on dinh la:

```text
gemini-embedding-2
```

Model nay ho tro:

```text
- Text.
- Image.
- Video.
- Audio.
- PDF.
- Output dimension linh hoat tu 128 den 3072.
```

Buoc 7 chi can input text, nhung dung model moi giup tranh phai migration vector ngay sau khi MVP hoan thanh.

Khong dung:

```text
gemini-embedding-001
```

cho code moi neu khong co yeu cau tuong thich du lieu cu. Hai model co embedding space khac nhau, nen vector tao boi hai model khong duoc tron trong cung collection.

### 3.2 Chon dimension `768`

Dung:

```text
EMBEDDING_DIMENSION=768
```

Ly do:

```text
- Gemini khuyen nghi 768, 1536 hoac 3072.
- 768 du nhe cho MVP.
- Giam RAM va dung luong luu tru Qdrant.
- Nhanh hon khi search so voi vector 3072 chieu.
- Sau nay co the benchmark va doi dimension neu can.
```

Qdrant collection co dimension co dinh. Neu doi dimension, can tao collection moi va embed lai toan bo du lieu.

### 3.3 Chon Qdrant

Dung Qdrant thay vi Pinecone vi:

```text
- Co the chay local bang Docker.
- Co Python client chinh thuc.
- Ho tro async client.
- Ho tro payload de filter theo metadata.
- Phu hop dinh huong trong Folder_structure.md va buoc 9.
```

### 3.4 Tach hai collection

Tao hai collection:

```text
question_embeddings
formula_embeddings
```

Khong gop tat ca vao mot collection.

Ly do:

```text
- Question vector dai dien cho noi dung bai toan.
- Formula vector dai dien cho mot cong thuc cu the.
- Mot Question co the co nhieu formulas.
- Buoc 9 search semantic se query question_embeddings.
- Buoc 10 formula matching se query formula_embeddings.
- Hai collection co payload va y nghia tim kiem khac nhau.
```

### 3.5 Khong luu vector vao PostgreSQL

PostgreSQL giu du lieu nghiep vu:

```text
Question.statement
Question.solution
Question.answer
Question.formulas
Question.metadata
```

Qdrant giu vector va payload truy vet:

```text
question_id
document_id
marker_number
formula_index
normalized_latex
```

Khong them cot JSON vector vao bang `questions`.

### 3.6 Dam bao idempotent

Buoc 6 dang dung workflow:

```text
segment lai document
 -> xoa questions cu
 -> tao questions moi
```

Vi vay `question_id` co the thay doi sau khi segment lai. Neu chi `upsert` theo ID moi, Qdrant se con vector cu khong con lien ket voi PostgreSQL.

Workflow dung o buoc 7:

```text
embed_document(document_id)
 -> xoa question vectors cu co payload.document_id = document_id
 -> xoa formula vectors cu co payload.document_id = document_id
 -> tao vector moi
 -> upsert vector moi
```

## 4. Cau truc thu muc can bo sung

Them:

```text
infra/
  vector_db/
    __init__.py
    qdrant_client.py
    repositories/
      __init__.py
      embeddings.py

modules/
  embeddings/
    __init__.py
    schemas.py
    text_builder.py
    gemini_embedder.py
    service.py

tests/
  modules/
    embeddings/
      __init__.py
      test_text_builder.py
      test_service.py

scripts/
  test_question_embeddings.py
```

Sua:

```text
core/config/settings.py
requirements.txt
.env
```

Khong sua trong MVP buoc 7:

```text
infra/db/models.py
infra/db/repositories/questions.py
modules/question_catalog/
modules/ingestion/
apps/api/
apps/frontend/
```

## 5. Khoi dong Qdrant local

### 5.1 Tao Docker volume

Chay:

```powershell
docker volume create datn_qdrant_storage
```

### 5.2 Chay Qdrant

Chay:

```powershell
docker run -d --name datn-qdrant `
  -p 6333:6333 `
  -p 6334:6334 `
  -v datn_qdrant_storage:/qdrant/storage `
  qdrant/qdrant
```

Neu container da duoc tao tu truoc va dang dung:

```powershell
docker start datn-qdrant
```

Qdrant local co:

```text
REST API:  http://localhost:6333
Dashboard: http://localhost:6333/dashboard
gRPC:      localhost:6334
```

Kiem tra nhanh:

```powershell
curl.exe http://localhost:6333/collections
```

Ket qua ban dau co the la:

```json
{"result":{"collections":[]},"status":"ok","time":0.00001}
```

Luu y:

```text
Qdrant local mac dinh khong co authentication.
Chi dung cho dev local.
Khong expose cong 6333 ra Internet khi chua cau hinh bao mat.
```

## 6. Them dependency

Mo:

```text
requirements.txt
```

Them:

```text
qdrant-client
```

Sau do cai dependency:

```powershell
pip install -r requirements.txt
```

Kiem tra:

```powershell
python -c "from qdrant_client import AsyncQdrantClient; print('qdrant-client ok')"
```

Ket qua mong doi:

```text
qdrant-client ok
```

## 7. Them cau hinh embedding va Qdrant

### 7.1 Sua settings

Mo:

```text
core/config/settings.py
```

Them cac field sau vao class `Settings`, phia duoi `gemini_model`:

```python
    embedding_model: str = "gemini-embedding-2"
    embedding_dimension: int = 768

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_question_collection: str = "question_embeddings"
    qdrant_formula_collection: str = "formula_embeddings"
```

Sau khi sua, class co phan cau hinh lien quan:

```python
class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    embedding_model: str = "gemini-embedding-2"
    embedding_dimension: int = 768

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_question_collection: str = "question_embeddings"
    qdrant_formula_collection: str = "formula_embeddings"
```

### 7.2 Sua `.env`

Mo:

```text
.env
```

Them:

```env
EMBEDDING_MODEL=gemini-embedding-2
EMBEDDING_DIMENSION=768

QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_QUESTION_COLLECTION=question_embeddings
QDRANT_FORMULA_COLLECTION=formula_embeddings
```

Voi Qdrant local:

```text
QDRANT_API_KEY=
```

de rong.

Neu sau nay dung Qdrant Cloud, dien:

```text
QDRANT_URL=<cluster-url>
QDRANT_API_KEY=<secret-key>
```

Khong commit `.env`.

## 8. Tao Qdrant client

Tao:

```text
infra/vector_db/__init__.py
```

De file rong.

Tao:

```text
infra/vector_db/qdrant_client.py
```

Them:

```python
from qdrant_client import AsyncQdrantClient

from core.config.settings import settings


def create_qdrant_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )
```

Ly do tach file:

```text
- Tap trung cau hinh ket noi Qdrant tai infrastructure layer.
- Module nghiep vu khong tu doc env.
- Sau nay doi local Qdrant sang Qdrant Cloud khong can sua service.
```

## 9. Tao schema noi bo cho embedding

Tao thu muc:

```text
modules/embeddings/
```

Tao:

```text
modules/embeddings/schemas.py
```

Them:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class QuestionVector:
    question_id: str
    document_id: str
    sequence_number: int
    marker: str
    marker_number: str
    statement: str
    subject: str | None
    chapter: str | None
    difficulty: str | None
    skills: list[str]
    vector: list[float]


@dataclass(frozen=True)
class FormulaVector:
    question_id: str
    document_id: str
    formula_index: int
    latex: str
    normalized_latex: str
    source: str
    vector: list[float]


@dataclass(frozen=True)
class EmbeddingResult:
    document_id: str
    question_count: int
    formula_count: int
```

### 9.1 Y nghia

```text
QuestionVector
  Du lieu can de tao mot point trong question_embeddings.

FormulaVector
  Du lieu can de tao mot point trong formula_embeddings.

EmbeddingResult
  Ket qua tong hop tra ve sau khi xu ly mot document.
```

Schema nay khong phai SQLAlchemy model va khong tao bang PostgreSQL.

## 10. Tao text builder

Tao:

```text
modules/embeddings/text_builder.py
```

Them:

```python
from infra.db.models import Question


def build_question_embedding_text(question: Question) -> str:
    parts = [
        f"Marker: {question.marker} {question.marker_number}",
        f"Statement:\n{question.statement}",
    ]

    if question.solution:
        parts.append(f"Solution:\n{question.solution}")

    if question.answer:
        parts.append(f"Answer:\n{question.answer}")

    normalized_formulas = [
        formula["normalized_latex"]
        for formula in question.formulas
        if formula.get("normalized_latex")
    ]

    if normalized_formulas:
        parts.append(
            "Formulas:\n"
            + "\n".join(
                f"- {formula}"
                for formula in normalized_formulas
            )
        )

    content = "\n\n".join(parts)

    return f"title: {question.marker} {question.marker_number} | text: {content}"


def build_formula_embedding_text(normalized_latex: str) -> str:
    return (
        "task: sentence similarity | query: "
        f"mathematical formula: {normalized_latex}"
    )
```

### 10.1 Vi sao question text co format rieng

Voi `gemini-embedding-2`, tai lieu chinh thuc khuyen nghi format cho retrieval document:

```text
title: {title} | text: {content}
```

Question se duoc tim bang semantic search o buoc 9. Vi vay question vector dung format document retrieval.

Sau nay query search can format:

```text
task: search result | query: {noi dung nguoi dung nhap}
```

### 10.2 Vi sao formula text dung sentence similarity

Formula matching can so sanh hai cong thuc theo cach doi xung:

```text
formula A <-> formula B
```

Vi vay dung format:

```text
task: sentence similarity | query: mathematical formula: ...
```

Buoc 10 co the mo rong bang parser cau truc toan hoc. Buoc 7 MVP chi tao embedding text tu `normalized_latex`.

## 11. Tao Gemini embedder

Tao:

```text
modules/embeddings/gemini_embedder.py
```

Them:

```python
from google import genai
from google.genai import types

from core.config.settings import settings


class GeminiEmbedder:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension

    def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Embedding text must not be empty")

        result = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=self.dimension,
            ),
        )

        if not result.embeddings:
            raise ValueError("Gemini returned no embedding")

        vector = list(result.embeddings[0].values)

        if len(vector) != self.dimension:
            raise ValueError(
                "Unexpected embedding dimension: "
                f"expected {self.dimension}, got {len(vector)}"
            )

        return vector
```

### 11.1 Vi sao embed tung text trong MVP

`gemini-embedding-2` co quy tac aggregation:

```text
Neu truyen nhieu input truc tiep vao contents,
model co the tao mot vector tong hop.
```

De implementation dau tien ro rang va kho bi sai, MVP goi:

```python
embed_text(text)
```

cho tung question va tung formula.

Sau khi workflow dung, co the toi uu batch bang:

```text
- Boc tung input trong types.Content.
- Hoac dung Gemini Batch API.
```

Khong toi uu batch som khi chua co benchmark va chua co so luong du lieu that.

## 12. Tao Qdrant embedding repository

Tao:

```text
infra/vector_db/repositories/__init__.py
```

De file rong.

Tao:

```text
infra/vector_db/repositories/embeddings.py
```

Them:

```python
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import AsyncQdrantClient, models

from modules.embeddings.schemas import FormulaVector, QuestionVector


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
```

### 12.1 Vi sao dung UUID deterministic cho formula

`Question.id` co the dung truc tiep lam Qdrant point ID cho question vector.

Formula khong co ID rieng trong PostgreSQL. Vi vay tao ID:

```text
uuid5(NAMESPACE_URL, "question-formula:<question_id>:<formula_index>")
```

Ket qua:

```text
- Cung question_id va formula_index -> cung point ID.
- Chay lai embedding khong sinh ID ngau nhien.
- De truy vet formula ve Question.
```

### 12.2 Vi sao xoa theo document_id truoc khi upsert

Neu document duoc segment lai:

```text
- Question cu bi xoa trong PostgreSQL.
- Question moi co UUID moi.
- Formula point ID cung thay doi.
```

Neu khong xoa Qdrant point cu, Qdrant se chua vector rac.

### 12.3 Vi sao dung Cosine

Semantic embedding thuong so sanh huong cua vector. Qdrant ho tro:

```text
Cosine
Dot
Euclid
Manhattan
```

MVP dung:

```python
models.Distance.COSINE
```

## 13. Tao embedding service

Tao:

```text
modules/embeddings/service.py
```

Them:

```python
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
                normalized_latex = formula.get("normalized_latex", "").strip()

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

        return EmbeddingResult(
            document_id=document_id,
            question_count=len(question_vectors),
            formula_count=len(formula_vectors),
        )
```

### 13.1 Trach nhiem service

```text
1. Lay questions cua document tu PostgreSQL.
2. Tu choi document chua co segmented questions.
3. Tao text dai dien cho tung question.
4. Goi embedder tao question vector.
5. Lay tung normalized_latex.
6. Goi embedder tao formula vector.
7. Yeu cau Qdrant repository replace vector cua document.
8. Tra ve so question vectors va formula vectors.
```

### 13.2 Vi sao dung `asyncio.to_thread`

Project hien dung async SQLAlchemy va Qdrant async client. Google SDK trong wrapper tren goi dong bo:

```python
self.client.models.embed_content(...)
```

Dung:

```python
await asyncio.to_thread(...)
```

de tranh chan event loop khi service sau nay duoc goi tu API hoac worker async.

## 14. Export module

Tao:

```text
modules/embeddings/__init__.py
```

Them:

```python
from modules.embeddings.gemini_embedder import GeminiEmbedder
from modules.embeddings.service import QuestionEmbeddingService

__all__ = ["GeminiEmbedder", "QuestionEmbeddingService"]
```

## 15. Viet unit test cho text builder

Tao:

```text
tests/modules/embeddings/__init__.py
```

De file rong.

Tao:

```text
tests/modules/embeddings/test_text_builder.py
```

Them:

```python
from types import SimpleNamespace

from modules.embeddings.text_builder import (
    build_formula_embedding_text,
    build_question_embedding_text,
)


def test_build_question_embedding_text() -> None:
    question = SimpleNamespace(
        marker="Bai",
        marker_number="1",
        statement="Tinh $x^2 + 1$.",
        solution="Thay $x = 2$.",
        answer="$5$",
        formulas=[
            {
                "latex": "x^2 + 1",
                "normalized_latex": "x^2 + 1",
                "source": "statement",
            }
        ],
    )

    text = build_question_embedding_text(question)

    assert text.startswith("title: Bai 1 | text:")
    assert "Statement:\nTinh $x^2 + 1$." in text
    assert "Solution:\nThay $x = 2$." in text
    assert "Answer:\n$5$" in text
    assert "Formulas:\n- x^2 + 1" in text


def test_build_formula_embedding_text() -> None:
    text = build_formula_embedding_text(r"\int_0^1 x dx")

    assert text == (
        "task: sentence similarity | query: "
        r"mathematical formula: \int_0^1 x dx"
    )
```

## 16. Viet unit test cho service

Tao:

```text
tests/modules/embeddings/test_service.py
```

Them:

```python
import asyncio
from types import SimpleNamespace

import pytest

from modules.embeddings.service import QuestionEmbeddingService


class FakeQuestionRepository:
    def __init__(self, questions) -> None:
        self.questions = questions

    async def list_by_document(self, document_id: str):
        return [
            question
            for question in self.questions
            if question.document_id == document_id
        ]


class FakeVectorRepository:
    def __init__(self) -> None:
        self.document_id = None
        self.questions = []
        self.formulas = []

    async def replace_for_document(
        self,
        *,
        document_id: str,
        questions,
        formulas,
    ) -> None:
        self.document_id = document_id
        self.questions = questions
        self.formulas = formulas


class FakeEmbedder:
    def __init__(self) -> None:
        self.texts = []

    def embed_text(self, text: str) -> list[float]:
        self.texts.append(text)
        return [0.1, 0.2, 0.3]


def test_embed_document() -> None:
    question = SimpleNamespace(
        id="question-id",
        document_id="document-id",
        sequence_number=1,
        marker="Bai",
        marker_number="27",
        statement="Tinh $x^2 + 1$.",
        solution=None,
        answer=None,
        formulas=[
            {
                "latex": "x^2 + 1",
                "normalized_latex": "x^2 + 1",
                "source": "statement",
            }
        ],
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
    )

    vector_repository = FakeVectorRepository()
    embedder = FakeEmbedder()
    service = QuestionEmbeddingService(
        question_repository=FakeQuestionRepository([question]),
        vector_repository=vector_repository,
        embedder=embedder,
    )

    result = asyncio.run(service.embed_document("document-id"))

    assert result.document_id == "document-id"
    assert result.question_count == 1
    assert result.formula_count == 1
    assert vector_repository.document_id == "document-id"
    assert len(vector_repository.questions) == 1
    assert len(vector_repository.formulas) == 1
    assert len(embedder.texts) == 2


def test_reject_document_without_segmented_questions() -> None:
    service = QuestionEmbeddingService(
        question_repository=FakeQuestionRepository([]),
        vector_repository=FakeVectorRepository(),
        embedder=FakeEmbedder(),
    )

    with pytest.raises(ValueError, match="No segmented questions"):
        asyncio.run(service.embed_document("missing-document"))
```

### 16.1 Chay unit test

Chay:

```powershell
pytest tests/modules/embeddings -q
```

Ket qua mong doi:

```text
4 passed
```

Sau do chay:

```powershell
pytest tests/modules -q
```

Tat ca test module cu va moi phai pass.

## 17. Tao script test voi Gemini va Qdrant that

Tao:

```text
scripts/test_question_embeddings.py
```

Them:

```python
import asyncio

from core.config.settings import settings
from infra.db.repositories.documents import DocumentRepository
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder, QuestionEmbeddingService


async def main() -> None:
    async with AsyncSessionLocal() as session:
        document_repository = DocumentRepository(session)
        question_repository = QuestionRepository(session)
        client = create_qdrant_client()

        try:
            vector_repository = EmbeddingVectorRepository(
                client=client,
                dimension=settings.embedding_dimension,
                question_collection=settings.qdrant_question_collection,
                formula_collection=settings.qdrant_formula_collection,
            )
            service = QuestionEmbeddingService(
                question_repository=question_repository,
                vector_repository=vector_repository,
                embedder=GeminiEmbedder(),
            )

            documents = await document_repository.list_documents()

            for document in documents:
                questions = await question_repository.list_by_document(document.id)

                if questions:
                    break
            else:
                raise RuntimeError("No document with segmented questions was found")

            result = await service.embed_document(document.id)

            question_count = await vector_repository.count_for_document(
                collection_name=settings.qdrant_question_collection,
                document_id=document.id,
            )
            formula_count = await vector_repository.count_for_document(
                collection_name=settings.qdrant_formula_collection,
                document_id=document.id,
            )

            print("Document:", document.id)
            print("Filename:", document.filename)
            print("Embedded questions:", result.question_count)
            print("Embedded formulas:", result.formula_count)
            print("Qdrant question points:", question_count)
            print("Qdrant formula points:", formula_count)
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### 17.1 Chay script

Dam bao Qdrant dang chay:

```powershell
docker start datn-qdrant
```

Sau do chay:

```powershell
python -m scripts.test_question_embeddings
```

Voi document `bttx.md`, ket qua mong doi:

```text
Filename: bttx.md
Embedded questions: 2
Embedded formulas: 7
Qdrant question points: 2
Qdrant formula points: 7
```

Luu y:

```text
Script goi Gemini API that.
Can co Internet.
Can co GEMINI_API_KEY hop le.
Co the ton quota API.
```

## 18. Kiem tra Qdrant

### 18.1 Kiem tra collections

Chay:

```powershell
curl.exe http://localhost:6333/collections
```

Can thay:

```text
question_embeddings
formula_embeddings
```

Hoac mo:

```text
http://localhost:6333/dashboard
```

### 18.2 Kiem tra question points

Chay:

```powershell
curl.exe -X POST `
  http://localhost:6333/collections/question_embeddings/points/scroll `
  -H "Content-Type: application/json" `
  -d '{\"limit\": 10, \"with_payload\": true, \"with_vector\": false}'
```

Payload can co:

```json
{
  "question_id": "...",
  "document_id": "...",
  "sequence_number": 1,
  "marker": "Bai",
  "marker_number": "27",
  "statement": "...",
  "subject": null,
  "chapter": null,
  "difficulty": null,
  "skills": []
}
```

### 18.3 Kiem tra formula points

Chay:

```powershell
curl.exe -X POST `
  http://localhost:6333/collections/formula_embeddings/points/scroll `
  -H "Content-Type: application/json" `
  -d '{\"limit\": 20, \"with_payload\": true, \"with_vector\": false}'
```

Payload can co:

```json
{
  "question_id": "...",
  "document_id": "...",
  "formula_index": 0,
  "latex": "...",
  "normalized_latex": "...",
  "source": "statement"
}
```

## 19. Kiem tra idempotent

Chay hai lan:

```powershell
python -m scripts.test_question_embeddings
python -m scripts.test_question_embeddings
```

Ket qua lan thu hai van phai la:

```text
Qdrant question points: 2
Qdrant formula points: 7
```

Khong duoc thanh:

```text
Qdrant question points: 4
Qdrant formula points: 14
```

### 19.1 Kiem tra sau khi segment lai

Day la test quan trong vi buoc 6 tao lai Question ID.

Chay:

```powershell
python -m scripts.test_question_catalog
python -m scripts.test_question_embeddings
```

Ket qua van phai la:

```text
Qdrant question points: 2
Qdrant formula points: 7
```

Ly do:

```text
EmbeddingVectorRepository xoa point cu theo document_id truoc khi upsert point moi.
```

## 20. Chay kiem tra tong the

Chay syntax check:

```powershell
python -m compileall apps/api core infra modules tests scripts
```

Chay tat ca test:

```powershell
pytest -q
```

Chay integration script that:

```powershell
python -m scripts.test_question_embeddings
```

## 21. Loi thuong gap

### Loi 1: Khong ket noi duoc Qdrant

Thong bao co the gap:

```text
ConnectError
Connection refused
```

Kiem tra:

```powershell
docker ps
curl.exe http://localhost:6333/collections
```

Neu container da ton tai nhung dang dung:

```powershell
docker start datn-qdrant
```

### Loi 2: Gemini API key khong hop le

Thong bao co the gap:

```text
API key not valid
```

Kiem tra:

```powershell
python -c "from core.config.settings import settings; print(bool(settings.gemini_api_key))"
```

Ket qua can la:

```text
True
```

### Loi 3: Sai dimension

Thong bao:

```text
Unexpected embedding dimension
```

Kiem tra:

```text
EMBEDDING_DIMENSION=768
```

Neu collection Qdrant cu duoc tao voi dimension khac, khong duoc chen vector moi vao collection cu.

Trong moi truong dev, co the xoa collection cu bang dashboard Qdrant roi chay lai script. Khong xoa collection production khi chua backup.

### Loi 4: Collection dimension mismatch

Thong bao Qdrant co the lien quan:

```text
expected dim
wrong vector dimension
```

Nguyen nhan:

```text
- EMBEDDING_DIMENSION trong .env da doi.
- Collection cu van dung dimension truoc do.
```

Huong xu ly production:

```text
1. Tao collection moi co ten version moi.
2. Embed lai toan bo questions.
3. Chuyen search sang collection moi.
4. Xoa collection cu sau khi xac minh.
```

### Loi 5: Khong co question de embed

Thong bao:

```text
No segmented questions were found
```

Chay segmentation truoc:

```powershell
python -m scripts.test_question_catalog
```

Sau do chay:

```powershell
python -m scripts.test_question_embeddings
```

### Loi 6: Script chon sai document

Script test chon document dau tien co questions. Neu muon test dung `bttx.md`, dam bao file nay da upload va segment o buoc 6.

Co the kiem tra PostgreSQL:

```sql
SELECT document_id, COUNT(*)
FROM questions
GROUP BY document_id;
```

## 22. Mo rong sau MVP

### 22.1 Batch embedding

MVP embed tung text de code ro rang. Khi du lieu lon, can:

```text
- Gom nhieu text.
- Dung Gemini Batch API neu latency khong quan trong.
- Hoac boc tung input trong Content object de lay vector rieng.
- Them retry va backoff cho rate limit.
```

### 22.2 Payload index

Khi buoc 9 search co filter metadata, tao Qdrant payload index cho:

```text
document_id
subject
chapter
difficulty
skills
```

MVP buoc 7 chua bat buoc vi du lieu con nho.

### 22.3 Worker orchestration

Khong chen embedding truc tiep vao ingestion service.

Huong mo rong:

```text
ingestion completed
 -> segmentation job
 -> embedding job
 -> Qdrant sync completed
```

Can worker queue de:

```text
- Retry khi Gemini loi.
- Retry khi Qdrant loi.
- Khong chan request upload.
- Theo doi trang thai tung stage.
```

### 22.4 Version hoa embedding

Khi he thong on dinh hon, them payload:

```text
embedding_model
embedding_dimension
embedding_version
```

Va dat ten collection co version:

```text
question_embeddings_v1
formula_embeddings_v1
```

Ly do:

```text
Vector tao boi model khac nhau khong duoc so sanh truc tiep.
```

## 23. Thu tu trien khai khuyen nghi

Lam lan luot:

```text
1. Khoi dong Qdrant local.
2. Them qdrant-client vao requirements.txt.
3. Cai dependency.
4. Them cau hinh embedding va Qdrant vao settings.py.
5. Them bien moi vao .env.
6. Tao infra/vector_db/qdrant_client.py.
7. Tao modules/embeddings/schemas.py.
8. Tao modules/embeddings/text_builder.py.
9. Tao modules/embeddings/gemini_embedder.py.
10. Tao infra/vector_db/repositories/embeddings.py.
11. Tao modules/embeddings/service.py.
12. Tao modules/embeddings/__init__.py.
13. Viet unit test text builder.
14. Viet unit test service.
15. Chay pytest tests/modules/embeddings -q.
16. Chay pytest tests/modules -q.
17. Tao scripts/test_question_embeddings.py.
18. Chay integration script voi Gemini va Qdrant that.
19. Kiem tra Qdrant dashboard.
20. Chay lai script de kiem tra idempotent.
21. Segment lai document va embed lai de kiem tra khong con vector rac.
22. Chay compileall va pytest -q.
```

## 24. Tieu chi hoan thanh

Buoc 7 MVP hoan tat khi:

```text
1. Qdrant local chay duoc.
2. Co hai collection question_embeddings va formula_embeddings.
3. GeminiEmbedder tao duoc vector 768 chieu.
4. QuestionEmbeddingService tao mot vector cho moi Question.
5. Moi normalized_latex co mot formula vector rieng.
6. Payload Qdrant co question_id va document_id de truy vet.
7. bttx.md tao 2 question vectors.
8. bttx.md tao 7 formula vectors.
9. Chay lai embedding khong tao point trung.
10. Segment lai roi embed lai khong de lai vector rac.
11. Unit test embedding pass.
12. Tat ca test cu van pass.
```

Sau buoc 7, du lieu san sang cho:

```text
- Buoc 8: dong bo va toi uu quy trinh luu PostgreSQL + Qdrant.
- Buoc 9: semantic search theo noi dung cau hoi.
- Buoc 10: tim cong thuc tuong tu.
```

## 25. Tai lieu tham khao

Gemini Embeddings:

```text
https://ai.google.dev/gemini-api/docs/embeddings
```

Qdrant local quickstart:

```text
https://qdrant.tech/documentation/quickstart/
```

Qdrant collections:

```text
https://qdrant.tech/documentation/manage-data/collections/
```

Qdrant points va delete theo filter:

```text
https://qdrant.tech/documentation/manage-data/points/
```

Qdrant filtering:

```text
https://qdrant.tech/documentation/search/filtering/
```
