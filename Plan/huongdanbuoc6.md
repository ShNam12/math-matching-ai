# Huong Dan Buoc 6: Tao Cau Truc Du Lieu Cho Cau Hoi

## 1. Muc tieu

Buoc 6 dua ket qua tu module `question_segmenter` vao PostgreSQL.

Luong xu ly sau khi hoan thanh:

```text
documents.markdown_content
 -> segment_questions(markdown_content)
 -> danh sach SegmentedQuestion
 -> luu questions vao PostgreSQL
 -> truy van lai cau hoi theo document_id
```

Moi cau hoi can luu:

```text
- Tai lieu nguon.
- Thu tu xuat hien trong tai lieu.
- Marker goc: Bai, Cau hoi, Vi du...
- So bai goc: 27, 28, 1.1...
- De bai.
- Loi giai neu co.
- Dap an neu co.
- Danh sach cong thuc LaTeX.
- Metadata phuc vu phan loai sau nay.
```

Buoc 6 chua lam:

```text
- Chua tao embedding.
- Chua ket noi Qdrant.
- Chua tim kiem semantic.
- Chua dung AI de tu dong gan metadata.
- Chua sua frontend.
- Chua tach cac y nho (a), (b), (c) thanh record rieng.
```

## 2. Hien trang dau vao

Bang `documents` da co tai:

```text
infra/db/models.py
```

Field dau vao:

```python
Document.markdown_content
```

Module segmentation da co:

```text
modules/question_segmenter/
  __init__.py
  schemas.py
  patterns.py
  formula_extractor.py
  segmenter.py
```

Ham chinh:

```python
from modules.question_segmenter import segment_questions
```

Ket qua:

```python
SegmentationResult(
    preamble=...,
    questions=[
        SegmentedQuestion(
            sequence_number=...,
            marker=...,
            marker_number=...,
            statement=...,
            solution=...,
            answer=...,
            formulas=[...],
        ),
    ],
)
```

## 3. Nguyen tac thiet ke

### 3.1 Tach ro ba lop

```text
modules/question_catalog/
  Xu ly nghiep vu: lay Markdown, segment, yeu cau repository luu.

infra/db/models.py
  Khai bao bang PostgreSQL.

infra/db/repositories/questions.py
  Doc va ghi question records.
```

Khong dat logic segmentation truc tiep trong:

```text
apps/api/v1/endpoints/
infra/db/repositories/
```

### 3.2 Luu cong thuc bang JSON

Trong MVP, luu danh sach cong thuc vao mot cot JSON:

```json
[
  {
    "latex": "x^2   + 1",
    "normalized_latex": "x^2 + 1",
    "source": "statement"
  }
]
```

Ly do:

```text
- Cong thuc da co cau truc ro rang tu ExtractedFormula.
- Mot cau hoi co the co nhieu cong thuc.
- Buoc 6 chua can query tung cong thuc bang SQL.
- Sau nay neu formula search can index rieng, co the tach bang question_formulas.
```

### 3.3 Metadata de nullable

Buoc 6 tao noi luu metadata, nhung chua tu dong gan metadata.

Vi vay cac field sau de `nullable=True`:

```text
subject
chapter
difficulty
```

Field danh sach ky nang khoi tao bang mang rong:

```text
skills = []
```

### 3.4 Dam bao idempotent

Neu segment lai cung mot document, khong duoc tao record trung lap.

Workflow:

```text
segment_document(document_id)
 -> xoa questions cu cua document
 -> insert danh sach moi
 -> commit mot lan
```

Them unique constraint:

```text
(document_id, sequence_number)
```

## 4. Cau truc thu muc can bo sung

Them:

```text
infra/
  db/
    repositories/
      questions.py

modules/
  question_catalog/
    __init__.py
    service.py

tests/
  modules/
    question_catalog/
      __init__.py
      test_service.py

scripts/
  test_question_catalog.py
```

Sua:

```text
infra/db/models.py
scripts/create_tables.py
```

Khong sua trong lan trien khai toi thieu:

```text
apps/api/
apps/frontend/
modules/ingestion/
modules/question_segmenter/
requirements.txt
```

## 5. Mo rong database model

Mo file:

```text
infra/db/models.py
```

### 5.1 Sua import

Tim:

```python
from sqlalchemy import BigInteger, DateTime, Text
```

Thay bang:

```python
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Text,
    UniqueConstraint,
)
```

### 5.2 Them model `Question`

Them phia duoi class `Document`:

```python
class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "sequence_number",
            name="uq_questions_document_sequence",
        ),
    )

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    document_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    marker: Mapped[str] = mapped_column(Text, nullable=False)
    marker_number: Mapped[str] = mapped_column(Text, nullable=False)

    statement: Mapped[str] = mapped_column(Text, nullable=False)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    formulas: Mapped[list[dict[str, str]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    chapter: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

### 5.3 Y nghia cac cot

```text
id                UUID dang string, nhat quan voi Document hien tai.
document_id       Truy vet tai lieu nguon.
sequence_number   Thu tu xuat hien trong document.
marker            Marker goc: Bai, Cau hoi, Vi du...
marker_number     So bai goc: 27, 28, 1.1...
statement         De bai.
solution          Loi giai neu tai lieu co cung cap.
answer            Dap an neu tai lieu co cung cap.
formulas          Danh sach cong thuc dang JSON.
subject           Mon hoc, vi du: Giai tich.
chapter           Chuong hoac chu de.
difficulty        Muc do: easy, medium, hard hoac quy uoc sau nay.
skills            Danh sach ky nang, khoi tao [].
created_at        Thoi diem tao record.
updated_at        Thoi diem cap nhat record.
```

## 6. Cap nhat script tao bang

Mo:

```text
scripts/create_tables.py
```

Tim:

```python
from infra.db.models import Document
```

Thay bang:

```python
from infra.db.models import Document, Question
```

Ly do:

```text
Base.metadata.create_all chi tao model da duoc import.
Import Question dam bao bang questions nam trong metadata khi chay script.
```

Chay:

```powershell
python -m scripts.create_tables
```

Luu y:

```text
create_all chi tao bang moi.
create_all khong thay the migration khi sua cot da ton tai.
```

Trong MVP hien tai, them bang moi bang `create_all` la du. Khi schema on dinh hon, can dua migration vao Alembic.

## 7. Tao question repository

Tao:

```text
infra/db/repositories/questions.py
```

Them noi dung:

```python
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.models import Question
from modules.question_segmenter.schemas import SegmentedQuestion


class QuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def replace_for_document(
        self,
        *,
        document_id: str,
        segmented_questions: list[SegmentedQuestion],
    ) -> list[Question]:
        await self.session.execute(
            delete(Question).where(Question.document_id == document_id)
        )

        questions = [
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
            )
            for question in segmented_questions
        ]

        self.session.add_all(questions)
        await self.session.commit()

        for question in questions:
            await self.session.refresh(question)

        return questions

    async def list_by_document(self, document_id: str) -> list[Question]:
        result = await self.session.execute(
            select(Question)
            .where(Question.document_id == document_id)
            .order_by(Question.sequence_number)
        )

        return list(result.scalars().all())

    async def get_question(self, question_id: str) -> Question | None:
        result = await self.session.execute(
            select(Question).where(Question.id == question_id)
        )

        return result.scalar_one_or_none()
```

### 7.1 Trach nhiem repository

```text
replace_for_document()
  Xoa ket qua segment cu va ghi danh sach moi trong cung session.

list_by_document()
  Lay danh sach cau hoi theo dung thu tu tai lieu.

get_question()
  Lay mot cau hoi theo ID de dung cho API sau nay.
```

Repository khong:

```text
- Tu doc markdown_content.
- Tu goi segment_questions().
- Tu gan metadata bang AI.
```

## 8. Tao question catalog service

Tao:

```text
modules/question_catalog/__init__.py
```

Them:

```python
from modules.question_catalog.service import QuestionCatalogService

__all__ = ["QuestionCatalogService"]
```

Tao:

```text
modules/question_catalog/service.py
```

Them:

```python
from infra.db.models import Question
from infra.db.repositories.documents import DocumentRepository
from infra.db.repositories.questions import QuestionRepository
from modules.question_segmenter import segment_questions


class QuestionCatalogService:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        question_repository: QuestionRepository,
    ) -> None:
        self.document_repository = document_repository
        self.question_repository = question_repository

    async def segment_document(self, document_id: str) -> list[Question]:
        document = await self.document_repository.get_document(document_id)

        if document is None:
            raise ValueError(f"Document not found: {document_id}")

        if document.status != "completed":
            raise ValueError(
                f"Document is not ready for segmentation: {document_id}"
            )

        if not document.markdown_content:
            raise ValueError(
                f"Document Markdown is not available: {document_id}"
            )

        result = segment_questions(document.markdown_content)

        return await self.question_repository.replace_for_document(
            document_id=document.id,
            segmented_questions=result.questions,
        )
```

### 8.1 Trach nhiem service

```text
1. Tim document.
2. Kiem tra document ton tai.
3. Kiem tra ingestion da completed.
4. Kiem tra markdown_content co du lieu.
5. Goi segment_questions().
6. Yeu cau repository replace ket qua cu.
7. Tra danh sach Question da luu.
```

### 8.2 Vi sao tach `question_catalog`

`question_segmenter` can tiep tuc doc lap:

```text
markdown string -> SegmentationResult
```

`question_catalog` la lop orchestration:

```text
PostgreSQL document -> segmenter -> PostgreSQL questions
```

Cach tach nay giup unit test regex khong phu thuoc database.

## 9. Viet unit test service

Tao:

```text
tests/modules/question_catalog/__init__.py
```

De file rong.

Tao:

```text
tests/modules/question_catalog/test_service.py
```

Them:

```python
import asyncio
from types import SimpleNamespace

import pytest

from modules.question_catalog.service import QuestionCatalogService


class FakeDocumentRepository:
    def __init__(self, document) -> None:
        self.document = document

    async def get_document(self, document_id: str):
        if self.document is None:
            return None

        if self.document.id != document_id:
            return None

        return self.document


class FakeQuestionRepository:
    def __init__(self) -> None:
        self.document_id = None
        self.segmented_questions = []

    async def replace_for_document(
        self,
        *,
        document_id: str,
        segmented_questions,
    ):
        self.document_id = document_id
        self.segmented_questions = segmented_questions
        return segmented_questions


def test_segment_completed_document() -> None:
    document = SimpleNamespace(
        id="document-id",
        status="completed",
        markdown_content="""
Bài 1. Tính $x^2 + 1$.

Bài 2. Tính $x^3 + 1$.
""",
    )

    question_repository = FakeQuestionRepository()
    service = QuestionCatalogService(
        document_repository=FakeDocumentRepository(document),
        question_repository=question_repository,
    )

    questions = asyncio.run(service.segment_document("document-id"))

    assert len(questions) == 2
    assert question_repository.document_id == "document-id"
    assert questions[0].marker_number == "1"
    assert questions[1].marker_number == "2"


def test_reject_missing_document() -> None:
    service = QuestionCatalogService(
        document_repository=FakeDocumentRepository(None),
        question_repository=FakeQuestionRepository(),
    )

    with pytest.raises(ValueError, match="Document not found"):
        asyncio.run(service.segment_document("missing"))


def test_reject_document_that_is_not_completed() -> None:
    document = SimpleNamespace(
        id="document-id",
        status="processing",
        markdown_content="# Pending",
    )

    service = QuestionCatalogService(
        document_repository=FakeDocumentRepository(document),
        question_repository=FakeQuestionRepository(),
    )

    with pytest.raises(ValueError, match="not ready for segmentation"):
        asyncio.run(service.segment_document("document-id"))


def test_reject_document_without_markdown() -> None:
    document = SimpleNamespace(
        id="document-id",
        status="completed",
        markdown_content=None,
    )

    service = QuestionCatalogService(
        document_repository=FakeDocumentRepository(document),
        question_repository=FakeQuestionRepository(),
    )

    with pytest.raises(ValueError, match="Markdown is not available"):
        asyncio.run(service.segment_document("document-id"))
```

Chay:

```powershell
pytest tests/modules/question_catalog -q
```

Ket qua mong doi:

```text
4 passed
```

Sau do chay:

```powershell
pytest tests/modules -q
```

Ket qua mong doi:

```text
Tat ca test modules cu va moi deu pass.
```

## 10. Tao script test voi PostgreSQL

Tao:

```text
scripts/test_question_catalog.py
```

Them:

```python
import asyncio

from infra.db.repositories.documents import DocumentRepository
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from modules.question_catalog import QuestionCatalogService


async def main() -> None:
    async with AsyncSessionLocal() as session:
        document_repository = DocumentRepository(session)
        question_repository = QuestionRepository(session)
        service = QuestionCatalogService(
            document_repository=document_repository,
            question_repository=question_repository,
        )

        documents = await document_repository.list_documents()
        completed_documents = [
            document
            for document in documents
            if document.status == "completed" and document.markdown_content
        ]

        if not completed_documents:
            raise RuntimeError("No completed document with Markdown was found")

        document = completed_documents[0]
        questions = await service.segment_document(document.id)

        print("Document:", document.id)
        print("Filename:", document.filename)
        print("Question count:", len(questions))

        for question in questions:
            print()
            print(f"{question.marker} {question.marker_number}")
            print("Sequence:", question.sequence_number)
            print("Statement:")
            print(question.statement)
            print("Formula count:", len(question.formulas))


if __name__ == "__main__":
    asyncio.run(main())
```

Truoc tien dam bao bang moi da duoc tao:

```powershell
python -m scripts.create_tables
```

Sau do chay:

```powershell
python -m scripts.test_question_catalog
```

## 11. Kiem tra PostgreSQL

Vao `psql`, chay:

```sql
SELECT
    id,
    document_id,
    sequence_number,
    marker,
    marker_number,
    subject,
    chapter,
    difficulty,
    skills
FROM questions
ORDER BY document_id, sequence_number;
```

Kiem tra cong thuc:

```sql
SELECT
    marker_number,
    formulas
FROM questions
ORDER BY document_id, sequence_number;
```

Kiem tra idempotent:

```text
1. Chay python -m scripts.test_question_catalog.
2. Dem so questions.
3. Chay lai script.
4. Dem lai so questions.
5. So luong cua cung document khong duoc tang gap doi.
```

SQL dem:

```sql
SELECT document_id, COUNT(*)
FROM questions
GROUP BY document_id;
```

## 12. Tich hop tu dong sau ingestion

Khong lam ngay khi chua test repository va service doc lap.

Sau khi script PostgreSQL chay on, co the tich hop segmentation vao workflow ingestion.

Mo:

```text
modules/ingestion/service.py
```

Hien tai cuoi workflow la:

```python
await self.document_repository.save_markdown(
    document,
    markdown,
)
```

Khong nen chen truc tiep `QuestionCatalogService` vao day trong lan dau, vi:

```text
- Ingestion hien chi duoc truyen DocumentRepository va R2StorageClient.
- Them QuestionRepository se mo rong dependency cua ingestion.
- Can quyet dinh loi segmentation co lam document ingestion failed hay khong.
```

Khuyen nghi MVP:

```text
1. Giu ingestion va segmentation tach rieng.
2. Chay segmentation bang script hoac endpoint rieng.
3. Khi da on dinh, moi them worker pipeline:
   ingestion completed -> segmentation queued.
```

Neu can tu dong hoa ngay sau MVP, nen tao orchestration worker rieng thay vi lam ingestion service phuc tap hon.

## 13. API mo rong tuy chon

API khong bat buoc de hoan thanh phan luu database toi thieu.

Sau khi repository va service on dinh, co the them:

```text
POST /documents/{document_id}/segment
GET  /documents/{document_id}/questions
GET  /questions/{question_id}
PATCH /questions/{question_id}/metadata
```

Trong do:

```text
POST /documents/{document_id}/segment
  Chay segmentation thu cong.

GET /documents/{document_id}/questions
  Lay danh sach cau hoi cua tai lieu.

GET /questions/{question_id}
  Lay chi tiet mot cau hoi.

PATCH /questions/{question_id}/metadata
  Gan subject, chapter, difficulty va skills thu cong.
```

Khong sua frontend cho den khi API contract da co test.

## 14. Metadata va taxonomy

Buoc 6 chi tao noi luu:

```text
subject
chapter
difficulty
skills
```

Chua can gan tu dong.

Quy uoc tam thoi de xuat:

```text
subject:
  "calculus"
  "complex_numbers"

difficulty:
  "easy"
  "medium"
  "hard"

skills:
  [
    "differentiate",
    "integrate",
    "compute_limit",
    "convert_complex_number_form"
  ]
```

Sau nay neu taxonomy phuc tap hon, co the tach:

```text
taxonomy_nodes
question_taxonomy_nodes
skills
question_skills
```

Khong can tach bang quan he ngay trong MVP.

## 15. Thu tu trien khai khuyen nghi

1. Them model `Question` vao `infra/db/models.py`.
2. Import `Question` trong `scripts/create_tables.py`.
3. Chay `python -m scripts.create_tables`.
4. Tao `infra/db/repositories/questions.py`.
5. Tao `modules/question_catalog/service.py`.
6. Tao `modules/question_catalog/__init__.py`.
7. Viet unit test cho `QuestionCatalogService`.
8. Chay `pytest tests/modules/question_catalog -q`.
9. Chay `pytest tests/modules -q`.
10. Tao `scripts/test_question_catalog.py`.
11. Chay script voi PostgreSQL.
12. Kiem tra idempotent.
13. Sau khi on dinh moi can nhac API va worker orchestration.

## 16. Tieu chi hoan thanh

Buoc 6 MVP hoan tat khi:

```text
1. PostgreSQL co bang questions.
2. Questions co foreign key document_id -> documents.id.
3. Moi question luu statement, solution, answer va formulas.
4. Moi question co noi luu subject, chapter, difficulty va skills.
5. QuestionRepository luu va doc duoc cau hoi theo document.
6. QuestionCatalogService chi segment document completed co Markdown.
7. Segment lai cung document khong tao record trung lap.
8. Unit test service pass.
9. Tat ca unit test modules cu van pass.
10. Script PostgreSQL tao questions tu document that thanh cong.
```

Sau buoc 6, du lieu da san sang cho:

```text
- Gan taxonomy va metadata nang cao.
- Tao embedding.
- Luu vector vao Qdrant.
- Tim kiem semantic va formula matching.
```
