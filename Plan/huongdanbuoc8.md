# Huong Dan Buoc 8: Luu Tru Cau Hoi Va Embedding

## 1. Muc tieu

Buoc 8 lam cho viec luu tru cau hoi trong PostgreSQL va embedding trong Qdrant tro nen dong bo, co trang thai va co the kiem tra lai.

Sau buoc 7, he thong da lam duoc:

```text
questions trong PostgreSQL
 -> Gemini embedding
 -> Qdrant question_embeddings va formula_embeddings
```

Nhung buoc 7 moi chi la pipeline tao embedding. Buoc 8 bo sung lop "storage sync":

```text
Document completed
 -> segment questions vao PostgreSQL
 -> danh dau questions.embedding_status = pending
 -> tao embeddings vao Qdrant
 -> neu thanh cong: questions.embedding_status = completed
 -> neu loi: questions.embedding_status = failed va luu error
 -> kiem tra PostgreSQL va Qdrant khop nhau
```

Ket qua can dat:

```text
- PostgreSQL biet question nao da embed thanh cong.
- PostgreSQL biet model va dimension da dung de embed.
- PostgreSQL luu thoi diem embedded_at.
- PostgreSQL luu loi embedding neu co.
- Qdrant co payload du de truy vet ve Question.
- Co script chay tron pipeline: segment + embed + verify.
- Co test xac nhan sync status dung.
```

Buoc 8 chua lam:

```text
- Chua tao API search.
- Chua sua frontend.
- Chua tao worker queue that.
- Chua retry/backoff nang cao.
- Chua tao Alembic migration chuan production.
- Chua them search endpoint.
```

## 2. Hien trang dau vao

Sau buoc 6:

```text
PostgreSQL:
  questions
```

Sau buoc 7:

```text
Qdrant:
  question_embeddings
  formula_embeddings
```

Code hien co:

```text
infra/db/models.py
infra/db/repositories/questions.py
modules/question_catalog/service.py
modules/embeddings/service.py
infra/vector_db/repositories/embeddings.py
scripts/test_question_catalog.py
scripts/test_question_embeddings.py
```

Van de con thieu:

```text
PostgreSQL chua co cot nao de biet embedding cua question da duoc luu vao Qdrant hay chua.
```

Neu Qdrant loi giua chung, database hien khong biet document dang lech sync.

## 3. Nguyen tac thiet ke

### 3.1 PostgreSQL la source of truth

PostgreSQL giu du lieu nghiep vu:

```text
documents
questions
question metadata
embedding sync status
```

Qdrant giu vector:

```text
question vector
formula vector
payload truy vet ve PostgreSQL
```

Khi co lech, PostgreSQL la noi quyet dinh can embed lai cai gi.

### 3.2 Khong luu vector vao PostgreSQL

Khong them cot:

```text
embedding_vector JSON
embedding_vector BYTEA
```

vao bang `questions`.

Ly do:

```text
- Vector 768 chieu khong phu hop de query trong PostgreSQL hien tai.
- Qdrant da toi uu cho vector search.
- PostgreSQL chi can luu status va metadata cua embedding.
```

### 3.3 Them embedding sync fields vao `questions`

Moi question can co cac field:

```text
embedding_status
embedding_model
embedding_dimension
embedding_error
embedded_at
```

Y nghia:

```text
embedding_status      pending | completed | failed
embedding_model       gemini-embedding-2
embedding_dimension   768
embedding_error       loi neu Gemini hoac Qdrant fail
embedded_at           thoi diem Qdrant ghi vector thanh cong
```

### 3.4 Idempotent van la yeu cau bat buoc

Chay lai pipeline khong duoc tao du lieu trung:

```text
segment + embed lan 1 -> 2 questions, 7 formula points
segment + embed lan 2 -> van 2 questions, 7 formula points
```

Vi buoc 6 segment lai se tao question UUID moi, buoc 8 tiep tuc dung chien luoc cua buoc 7:

```text
xoa Qdrant points theo document_id truoc khi upsert points moi
```

## 4. Cau truc can bo sung

Them:

```text
modules/
  question_storage/
    __init__.py
    service.py

tests/
  modules/
    question_storage/
      __init__.py
      test_service.py

scripts/
  migrate_step8_embedding_status.py
  sync_question_storage.py
  check_question_embedding_sync.py
```

Sua:

```text
infra/db/models.py
infra/db/repositories/questions.py
modules/embeddings/service.py
tests/modules/embeddings/test_service.py
```

Khong sua trong MVP buoc 8:

```text
apps/api/
apps/frontend/
modules/ingestion/
```

## 5. Mo rong database model `Question`

Mo:

```text
infra/db/models.py
```

Tim class:

```python
class Question(Base):
```

Them cac field sau sau `skills` va truoc `created_at`:

```python
    embedding_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="pending",
    )
    embedding_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_dimension: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    embedding_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
```

Sau khi them, phan cuoi model se co dang:

```python
    skills: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    embedding_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="pending",
    )
    embedding_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_dimension: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    embedding_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
```

### 5.1 Vi sao khong sua `documents`

Co the them status vao `documents`, nhung MVP buoc 8 nen tracking o `questions`.

Ly do:

```text
- Embedding gan voi tung question.
- Mot document co the co question completed va question failed neu sau nay embed partial.
- Buoc 9 search theo question, khong search truc tiep theo document.
```

Neu sau nay can dashboard cap document, co the tinh tu bang questions:

```sql
SELECT embedding_status, COUNT(*)
FROM questions
WHERE document_id = '<document_id>'
GROUP BY embedding_status;
```

## 6. Tao migration script cho cot moi

`Base.metadata.create_all()` khong them cot vao bang da ton tai.

Vi `questions` da duoc tao o buoc 6, phai chay `ALTER TABLE`.

Tao:

```text
scripts/migrate_step8_embedding_status.py
```

Them:

```python
import asyncio

from sqlalchemy import text

from infra.db.session import engine


MIGRATION_SQL = """
ALTER TABLE questions
ADD COLUMN IF NOT EXISTS embedding_status TEXT NOT NULL DEFAULT 'pending';

ALTER TABLE questions
ADD COLUMN IF NOT EXISTS embedding_model TEXT;

ALTER TABLE questions
ADD COLUMN IF NOT EXISTS embedding_dimension INTEGER;

ALTER TABLE questions
ADD COLUMN IF NOT EXISTS embedding_error TEXT;

ALTER TABLE questions
ADD COLUMN IF NOT EXISTS embedded_at TIMESTAMPTZ;
"""


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(text(MIGRATION_SQL))

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
```

Chay:

```powershell
python -m scripts.migrate_step8_embedding_status
```

Kiem tra PostgreSQL:

```powershell
psql -h localhost -p 5432 -U postgres -d datn_db
```

Chay:

```sql
SELECT
    marker_number,
    embedding_status,
    embedding_model,
    embedding_dimension,
    embedding_error,
    embedded_at
FROM questions
ORDER BY document_id, sequence_number;
```

Ket qua ban dau co the la:

```text
embedding_status = pending
embedding_model = null
embedding_dimension = null
embedding_error = null
embedded_at = null
```

## 7. Cap nhat `QuestionRepository`

Mo:

```text
infra/db/repositories/questions.py
```

### 7.1 Them import

Them:

```python
from datetime import UTC, datetime
```

Sua import SQLAlchemy:

```python
from sqlalchemy import delete, select
```

thanh:

```python
from sqlalchemy import delete, select, update
```

### 7.2 Sua `replace_for_document`

Trong object `Question(...)`, them:

```python
                embedding_status="pending",
                embedding_model=None,
                embedding_dimension=None,
                embedding_error=None,
                embedded_at=None,
```

Thanh:

```python
            Question(
                document_id=document_id,
                sequence_number=question.sequence_number,
                marker=question.marker,
                marker_number=question.marker_number,
                statement=question.statement,
                solution=question.solution,
                answer=question.answer,
                formulas=[
                    formula.model_dump()
                    for formula in question.formulas
                ],
                subject=None,
                chapter=None,
                difficulty=None,
                skills=[],
                embedding_status="pending",
                embedding_model=None,
                embedding_dimension=None,
                embedding_error=None,
                embedded_at=None,
            )
```

Ly do:

```text
Moi lan segment lai document, questions moi can bat dau o pending.
Sau do embedding service moi chuyen sang completed.
```

### 7.3 Them methods cap nhat embedding status

Them vao class `QuestionRepository`:

```python
    async def mark_embedding_pending_for_document(
        self,
        document_id: str,
    ) -> None:
        await self.session.execute(
            update(Question)
            .where(Question.document_id == document_id)
            .values(
                embedding_status="pending",
                embedding_error=None,
                embedded_at=None,
            )
        )
        await self.session.commit()

    async def mark_embedding_completed_for_document(
        self,
        *,
        document_id: str,
        embedding_model: str,
        embedding_dimension: int,
    ) -> None:
        await self.session.execute(
            update(Question)
            .where(Question.document_id == document_id)
            .values(
                embedding_status="completed",
                embedding_model=embedding_model,
                embedding_dimension=embedding_dimension,
                embedding_error=None,
                embedded_at=datetime.now(UTC),
            )
        )
        await self.session.commit()

    async def mark_embedding_failed_for_document(
        self,
        *,
        document_id: str,
        error_message: str,
    ) -> None:
        await self.session.execute(
            update(Question)
            .where(Question.document_id == document_id)
            .values(
                embedding_status="failed",
                embedding_error=error_message[:4000],
            )
        )
        await self.session.commit()

    async def count_by_embedding_status(
        self,
        document_id: str,
    ) -> dict[str, int]:
        questions = await self.list_by_document(document_id)
        counts: dict[str, int] = {}

        for question in questions:
            counts[question.embedding_status] = (
                counts.get(question.embedding_status, 0) + 1
            )

        return counts
```

### 7.4 Vi sao mark theo document

MVP embed theo document:

```text
embed_document(document_id)
```

Nen status cung cap nhat theo document.

Sau nay neu can partial retry tung question, co the them:

```python
mark_embedding_completed(question_id)
mark_embedding_failed(question_id)
```

Chua can lam ngay.

## 8. Cap nhat `QuestionEmbeddingService`

Mo:

```text
modules/embeddings/service.py
```

Trong `embed_document`, can them trang thai:

```text
pending -> completed
pending -> failed neu loi
```

Thay toan bo ham `embed_document` bang:

```python
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
```

### 8.1 Vi sao mark pending truoc

Neu embed lai document, status cu co the dang:

```text
completed
failed
```

Truoc khi embed lai, dua ve:

```text
pending
```

de biet pipeline dang tao lai embedding.

### 8.2 Vi sao mark completed sau Qdrant upsert

Chi duoc coi la completed khi:

```text
- Gemini tao vector thanh cong.
- Qdrant replace_for_document thanh cong.
```

Neu Gemini thanh cong nhung Qdrant loi, PostgreSQL phai la:

```text
embedding_status = failed
```

khong duoc la `completed`.

### 8.3 Vi sao can catch exception

Neu loi, can luu vao PostgreSQL:

```text
embedding_error = str(exc)
```

De sau nay dashboard hoac script biet can retry document nao.

## 9. Cap nhat unit test embedding service

Mo:

```text
tests/modules/embeddings/test_service.py
```

### 9.1 Sua FakeQuestionRepository

Them state va methods:

```python
class FakeQuestionRepository:
    def __init__(self, questions) -> None:
        self.questions = questions
        self.pending_document_id = None
        self.completed_document_id = None
        self.failed_document_id = None
        self.embedding_model = None
        self.embedding_dimension = None
        self.error_message = None

    async def list_by_document(self, document_id: str):
        return [
            question
            for question in self.questions
            if question.document_id == document_id
        ]

    async def mark_embedding_pending_for_document(
        self,
        document_id: str,
    ) -> None:
        self.pending_document_id = document_id

    async def mark_embedding_completed_for_document(
        self,
        *,
        document_id: str,
        embedding_model: str,
        embedding_dimension: int,
    ) -> None:
        self.completed_document_id = document_id
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension

    async def mark_embedding_failed_for_document(
        self,
        *,
        document_id: str,
        error_message: str,
    ) -> None:
        self.failed_document_id = document_id
        self.error_message = error_message
```

### 9.2 Sua FakeEmbedder

Them model va dimension:

```python
class FakeEmbedder:
    model = "fake-embedding-model"
    dimension = 3

    def __init__(self) -> None:
        self.texts = []

    def embed_text(self, text: str) -> list[float]:
        self.texts.append(text)
        return [0.1, 0.2, 0.3]
```

### 9.3 Cap nhat assert trong `test_embed_document`

Can tao bien repository:

```python
question_repository = FakeQuestionRepository([question])
```

Sau do truyen vao service:

```python
service = QuestionEmbeddingService(
    question_repository=question_repository,
    vector_repository=vector_repository,
    embedder=embedder,
)
```

Them assert:

```python
    assert question_repository.pending_document_id == "document-id"
    assert question_repository.completed_document_id == "document-id"
    assert question_repository.embedding_model == "fake-embedding-model"
    assert question_repository.embedding_dimension == 3
    assert question_repository.failed_document_id is None
```

### 9.4 Them test failed status

Them:

```python
class FailingEmbedder:
    model = "failing-model"
    dimension = 3

    def embed_text(self, text: str) -> list[float]:
        raise RuntimeError("embedding failed")


def test_mark_failed_when_embedding_fails() -> None:
    question = SimpleNamespace(
        id="question-id",
        document_id="document-id",
        sequence_number=1,
        marker="Bai",
        marker_number="27",
        statement="Tinh $x^2 + 1$.",
        solution=None,
        answer=None,
        formulas=[],
        subject=None,
        chapter=None,
        difficulty=None,
        skills=[],
    )

    question_repository = FakeQuestionRepository([question])
    service = QuestionEmbeddingService(
        question_repository=question_repository,
        vector_repository=FakeVectorRepository(),
        embedder=FailingEmbedder(),
    )

    with pytest.raises(RuntimeError, match="embedding failed"):
        asyncio.run(service.embed_document("document-id"))

    assert question_repository.pending_document_id == "document-id"
    assert question_repository.failed_document_id == "document-id"
    assert question_repository.error_message == "embedding failed"
```

Chay:

```powershell
pytest tests/modules/embeddings -q
```

Ket qua mong doi:

```text
5 passed
```

## 10. Tao question storage orchestration service

Buoc 6 co `QuestionCatalogService`.

Buoc 7 co `QuestionEmbeddingService`.

Buoc 8 tao service dieu phoi:

```text
segment document
 -> luu questions vao PostgreSQL
 -> embed questions
 -> luu embeddings vao Qdrant
 -> tra ket qua dong bo
```

Tao:

```text
modules/question_storage/__init__.py
```

Them:

```python
from modules.question_storage.service import (
    QuestionStorageResult,
    QuestionStorageService,
)

__all__ = ["QuestionStorageResult", "QuestionStorageService"]
```

Tao:

```text
modules/question_storage/service.py
```

Them:

```python
from dataclasses import dataclass

from modules.embeddings.schemas import EmbeddingResult
from modules.embeddings.service import QuestionEmbeddingService
from modules.question_catalog import QuestionCatalogService


@dataclass(frozen=True)
class QuestionStorageResult:
    document_id: str
    question_count: int
    formula_count: int


class QuestionStorageService:
    def __init__(
        self,
        *,
        question_catalog_service: QuestionCatalogService,
        embedding_service: QuestionEmbeddingService,
    ) -> None:
        self.question_catalog_service = question_catalog_service
        self.embedding_service = embedding_service

    async def store_document(self, document_id: str) -> QuestionStorageResult:
        questions = await self.question_catalog_service.segment_document(
            document_id
        )
        embedding_result: EmbeddingResult = (
            await self.embedding_service.embed_document(document_id)
        )

        return QuestionStorageResult(
            document_id=document_id,
            question_count=len(questions),
            formula_count=embedding_result.formula_count,
        )
```

### 10.1 Vi sao can service nay

Neu moi lan phai goi hai script rieng:

```powershell
python -m scripts.test_question_catalog
python -m scripts.test_question_embeddings
```

thi pipeline de sai thu tu.

`QuestionStorageService` tao mot workflow ro rang:

```text
store_document(document_id)
```

Sau nay endpoint hoac worker co the goi service nay.

## 11. Viet unit test cho question storage service

Tao:

```text
tests/modules/question_storage/__init__.py
```

De file rong.

Tao:

```text
tests/modules/question_storage/test_service.py
```

Them:

```python
import asyncio
from types import SimpleNamespace

from modules.embeddings.schemas import EmbeddingResult
from modules.question_storage import QuestionStorageService


class FakeQuestionCatalogService:
    def __init__(self) -> None:
        self.document_id = None

    async def segment_document(self, document_id: str):
        self.document_id = document_id
        return [
            SimpleNamespace(id="q1"),
            SimpleNamespace(id="q2"),
        ]


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.document_id = None

    async def embed_document(self, document_id: str) -> EmbeddingResult:
        self.document_id = document_id
        return EmbeddingResult(
            document_id=document_id,
            question_count=2,
            formula_count=7,
        )


def test_store_document_segments_before_embedding() -> None:
    catalog_service = FakeQuestionCatalogService()
    embedding_service = FakeEmbeddingService()
    service = QuestionStorageService(
        question_catalog_service=catalog_service,
        embedding_service=embedding_service,
    )

    result = asyncio.run(service.store_document("document-id"))

    assert catalog_service.document_id == "document-id"
    assert embedding_service.document_id == "document-id"
    assert result.document_id == "document-id"
    assert result.question_count == 2
    assert result.formula_count == 7
```

Chay:

```powershell
pytest tests/modules/question_storage -q
```

Ket qua mong doi:

```text
1 passed
```

## 12. Tao script chay tron pipeline luu tru

Tao:

```text
scripts/sync_question_storage.py
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
from modules.question_catalog import QuestionCatalogService
from modules.question_storage import QuestionStorageService


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
            catalog_service = QuestionCatalogService(
                document_repository=document_repository,
                question_repository=question_repository,
            )
            embedding_service = QuestionEmbeddingService(
                question_repository=question_repository,
                vector_repository=vector_repository,
                embedder=GeminiEmbedder(),
            )
            storage_service = QuestionStorageService(
                question_catalog_service=catalog_service,
                embedding_service=embedding_service,
            )

            documents = await document_repository.list_documents()
            completed_documents = [
                document
                for document in documents
                if document.status == "completed" and document.markdown_content
            ]

            if not completed_documents:
                raise RuntimeError("No completed document with Markdown was found")

            document = next(
                (
                    document
                    for document in completed_documents
                    if document.filename == "bttx.md"
                ),
                completed_documents[0],
            )

            result = await storage_service.store_document(document.id)
            status_counts = await question_repository.count_by_embedding_status(
                document.id
            )
            question_points = await vector_repository.count_for_document(
                collection_name=settings.qdrant_question_collection,
                document_id=document.id,
            )
            formula_points = await vector_repository.count_for_document(
                collection_name=settings.qdrant_formula_collection,
                document_id=document.id,
            )

            print("Document:", document.id)
            print("Filename:", document.filename)
            print("Questions stored:", result.question_count)
            print("Formulas embedded:", result.formula_count)
            print("PostgreSQL embedding statuses:", status_counts)
            print("Qdrant question points:", question_points)
            print("Qdrant formula points:", formula_points)
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Chay:

```powershell
python -m scripts.sync_question_storage
```

Voi `bttx.md`, ket qua mong doi:

```text
Filename: bttx.md
Questions stored: 2
Formulas embedded: 7
PostgreSQL embedding statuses: {'completed': 2}
Qdrant question points: 2
Qdrant formula points: 7
```

## 13. Tao script kiem tra dong bo PostgreSQL va Qdrant

Tao:

```text
scripts/check_question_embedding_sync.py
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

            documents = await document_repository.list_documents()

            for document in documents:
                questions = await question_repository.list_by_document(document.id)

                if not questions:
                    continue

                expected_formula_count = sum(
                    len(question.formulas)
                    for question in questions
                )
                status_counts = await question_repository.count_by_embedding_status(
                    document.id
                )
                question_points = await vector_repository.count_for_document(
                    collection_name=settings.qdrant_question_collection,
                    document_id=document.id,
                )
                formula_points = await vector_repository.count_for_document(
                    collection_name=settings.qdrant_formula_collection,
                    document_id=document.id,
                )

                print()
                print("Document:", document.id)
                print("Filename:", document.filename)
                print("PostgreSQL questions:", len(questions))
                print("PostgreSQL formulas:", expected_formula_count)
                print("PostgreSQL embedding statuses:", status_counts)
                print("Qdrant question points:", question_points)
                print("Qdrant formula points:", formula_points)

                if question_points != len(questions):
                    print("WARNING: question point count mismatch")

                if formula_points != expected_formula_count:
                    print("WARNING: formula point count mismatch")
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Chay:

```powershell
python -m scripts.check_question_embedding_sync
```

Ket qua mong doi voi `bttx.md`:

```text
PostgreSQL questions: 2
PostgreSQL formulas: 7
PostgreSQL embedding statuses: {'completed': 2}
Qdrant question points: 2
Qdrant formula points: 7
```

## 14. Kiem tra PostgreSQL truc tiep

Vao psql:

```powershell
psql -h localhost -p 5432 -U postgres -d datn_db
```

Chay:

```sql
SELECT
    marker_number,
    embedding_status,
    embedding_model,
    embedding_dimension,
    embedding_error,
    embedded_at
FROM questions
ORDER BY document_id, sequence_number;
```

Ket qua dung voi `bttx.md`:

```text
27 | completed | gemini-embedding-2 | 768 | null | <timestamp>
28 | completed | gemini-embedding-2 | 768 | null | <timestamp>
```

Kiem tra tong hop:

```sql
SELECT
    document_id,
    embedding_status,
    COUNT(*)
FROM questions
GROUP BY document_id, embedding_status
ORDER BY document_id, embedding_status;
```

## 15. Kiem tra Qdrant

Kiem tra collections:

```powershell
curl.exe http://localhost:6333/collections
```

Kiem tra question payload:

```powershell
curl.exe -X POST `
  http://localhost:6333/collections/question_embeddings/points/scroll `
  -H "Content-Type: application/json" `
  -d '{\"limit\": 10, \"with_payload\": true, \"with_vector\": false}'
```

Kiem tra formula payload:

```powershell
curl.exe -X POST `
  http://localhost:6333/collections/formula_embeddings/points/scroll `
  -H "Content-Type: application/json" `
  -d '{\"limit\": 20, \"with_payload\": true, \"with_vector\": false}'
```

Can thay:

```text
question_embeddings: 2 points voi bttx.md
formula_embeddings: 7 points voi bttx.md
```

## 16. Kiem tra idempotent

Chay:

```powershell
python -m scripts.sync_question_storage
python -m scripts.sync_question_storage
python -m scripts.check_question_embedding_sync
```

Ket qua van phai la:

```text
PostgreSQL questions: 2
PostgreSQL formulas: 7
PostgreSQL embedding statuses: {'completed': 2}
Qdrant question points: 2
Qdrant formula points: 7
```

Khong duoc thanh:

```text
Qdrant question points: 4
Qdrant formula points: 14
```

## 17. Kiem tra loi embedding

Unit test da test loi bang fake embedder.

Neu muon test thu cong, co the tam thoi dat sai:

```env
EMBEDDING_MODEL=invalid-model
```

Sau do chay:

```powershell
python -m scripts.sync_question_storage
```

Ket qua mong doi:

```text
script bao loi
questions.embedding_status = failed
questions.embedding_error co noi dung loi
```

Sau khi test xong, phai doi lai:

```env
EMBEDDING_MODEL=gemini-embedding-2
```

roi chay lai:

```powershell
python -m scripts.sync_question_storage
```

Luu y:

```text
Khong nen test loi nay neu dang can giu pipeline sach.
Unit test la du cho MVP.
```

## 18. Chay test tong the

Chay:

```powershell
pytest tests/modules/embeddings -q
pytest tests/modules/question_storage -q
pytest tests/modules -q
pytest -q
```

Chay syntax check:

```powershell
python -m compileall apps/api core infra modules tests scripts
```

Chay integration:

```powershell
python -m scripts.sync_question_storage
python -m scripts.check_question_embedding_sync
```

## 19. Loi thuong gap

### 19.1 Chay `create_all` nhung khong thay cot moi

Nguyen nhan:

```text
create_all khong sua bang da ton tai.
```

Phai chay:

```powershell
python -m scripts.migrate_step8_embedding_status
```

### 19.2 Loi `column questions.embedding_status does not exist`

Nguyen nhan:

```text
Da sua SQLAlchemy model nhung chua chay migration script.
```

Chay:

```powershell
python -m scripts.migrate_step8_embedding_status
```

### 19.3 PostgreSQL completed nhung Qdrant count sai

Nguyen nhan co the:

```text
- Qdrant bi xoa collection thu cong.
- Qdrant dang chay volume khac.
- Script embed bi ngat sau khi mark completed.
```

Xu ly:

```powershell
python -m scripts.sync_question_storage
python -m scripts.check_question_embedding_sync
```

### 19.4 Qdrant connection refused

Kiem tra:

```powershell
docker ps
curl.exe http://localhost:6333/collections
```

Neu container dung:

```powershell
docker start datn-qdrant
```

### 19.5 Gemini API loi

Kiem tra:

```powershell
python -c "from core.config.settings import settings; print(bool(settings.gemini_api_key)); print(settings.embedding_model)"
```

Can thay:

```text
True
gemini-embedding-2
```

## 20. Mo rong sau MVP

### 20.1 Dung Alembic migration

Buoc 8 MVP dung script SQL rieng.

Khi schema on dinh hon, can chuyen sang Alembic:

```text
alembic revision -m "add question embedding status"
alembic upgrade head
```

### 20.2 Embedding job queue

Thay vi goi script thu cong:

```text
upload completed
 -> segmentation job
 -> embedding job
 -> sync verification job
```

Dung worker queue de:

```text
- Retry loi Gemini.
- Retry loi Qdrant.
- Khong chan request upload.
- Luu lich su job.
```

### 20.3 Version hoa collection

Neu doi model hoac dimension:

```text
gemini-embedding-2 768 -> model khac 1536
```

Khong nen ghi chung collection cu.

Nen dung:

```text
question_embeddings_v1
formula_embeddings_v1
question_embeddings_v2
formula_embeddings_v2
```

### 20.4 Luu sync audit table

Neu can debug production, tao bang:

```text
embedding_sync_events
```

Cot de xuat:

```text
id
document_id
event_type
status
message
metadata
created_at
```

MVP buoc 8 chua can.

## 21. Thu tu trien khai khuyen nghi

Lam lan luot:

```text
1. Them embedding sync fields vao Question model.
2. Tao scripts/migrate_step8_embedding_status.py.
3. Chay migration script.
4. Kiem tra cot moi bang psql.
5. Cap nhat QuestionRepository replace_for_document.
6. Them methods mark_embedding_pending/completed/failed.
7. Cap nhat QuestionEmbeddingService de mark status.
8. Cap nhat tests/modules/embeddings/test_service.py.
9. Chay pytest tests/modules/embeddings -q.
10. Tao modules/question_storage/service.py.
11. Tao tests/modules/question_storage/test_service.py.
12. Chay pytest tests/modules/question_storage -q.
13. Tao scripts/sync_question_storage.py.
14. Tao scripts/check_question_embedding_sync.py.
15. Chay python -m scripts.sync_question_storage.
16. Chay python -m scripts.check_question_embedding_sync.
17. Chay lai sync de kiem tra idempotent.
18. Chay pytest -q.
19. Chay compileall.
```

## 22. Tieu chi hoan thanh

Buoc 8 MVP hoan tat khi:

```text
1. Bang questions co cot embedding_status.
2. Bang questions co embedding_model, embedding_dimension, embedding_error, embedded_at.
3. Questions moi sau segmentation co embedding_status = pending.
4. Sau khi embed thanh cong, questions co embedding_status = completed.
5. embedding_model = gemini-embedding-2.
6. embedding_dimension = 768.
7. embedded_at co timestamp.
8. Neu embedding loi, questions co embedding_status = failed va embedding_error.
9. Qdrant question_embeddings co so point bang so questions cua document.
10. Qdrant formula_embeddings co so point bang tong so formulas cua document.
11. Script sync_question_storage chay tron segment + embed.
12. Script check_question_embedding_sync phat hien duoc lech count.
13. Chay sync nhieu lan khong tao point trung.
14. Unit test embeddings va question_storage pass.
15. Tat ca test cu van pass.
```

Sau buoc 8, he thong san sang cho:

```text
- Buoc 9: semantic search theo question_embeddings.
- Buoc 10: formula matching theo formula_embeddings.
- Worker pipeline ingestion -> segmentation -> embedding.
```
