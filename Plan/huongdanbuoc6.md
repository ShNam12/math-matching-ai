# Huong Dan Buoc 6: Tao Module Ingestion

## 1. Muc tieu cua buoc 6

Buoc nay tao module ingestion rieng de xu ly tai lieu sau khi backend nhan file upload.

Luong toi thieu can co:

```text
file upload
 -> upload file goc len Cloudflare R2
 -> neu Markdown: doc noi dung truc tiep tu file_bytes
 -> neu PDF: tam thoi de placeholder, se tich hop Gemini o buoc 7
 -> chuan hoa Markdown
 -> luu markdown_content vao PostgreSQL
 -> cap nhat status completed / failed
```

Buoc 6 chua can sua frontend. Frontend nen ket noi sau khi backend upload flow da on dinh.

## 2. Cau truc thu muc can tao

Tao cac file va thu muc sau:

```text
modules/ingestion/
  __init__.py
  schemas.py
  service.py
  markdown_processing/
    __init__.py
    normalizer.py
    ocr_cleanup.py
    math_normalizer.py
  pdf_processing/
    __init__.py
    gemini_pdf_converter.py
```

Vai tro tung file:

```text
service.py                  Dieu phoi toan bo ingestion
schemas.py                  Schema noi bo cho ingestion
normalizer.py               Pipeline chuan hoa Markdown
ocr_cleanup.py              Sua loi OCR pho bien
math_normalizer.py          Chuan hoa delimiter cong thuc toan
gemini_pdf_converter.py     Chuyen PDF sang Markdown, buoc 6 chi de placeholder
```

## 3. Tao `modules/ingestion/schemas.py`

Them noi dung:

```python
from pydantic import BaseModel


class IngestionResult(BaseModel):
    markdown_content: str
    markdown_checksum: str
```

File nay chua bat buoc dung ngay, nhung nen tao truoc de cac buoc sau co noi dat schema noi bo.

## 4. Tao `modules/ingestion/markdown_processing/ocr_cleanup.py`

Them noi dung toi thieu:

```python
def fix_common_ocr_errors(text: str) -> str:
    return text
```

Buoc nay chi tao khung. Cac rule OCR co the bo sung sau, vi xu ly OCR qua som de gay loi sai noi dung toan hoc.

## 5. Tao `modules/ingestion/markdown_processing/math_normalizer.py`

Them noi dung:

```python
def normalize_math_delimiters(text: str) -> str:
    text = text.replace("\\(", "$")
    text = text.replace("\\)", "$")
    text = text.replace("\\[", "$$")
    text = text.replace("\\]", "$$")
    return text
```

Muc tieu:

```text
\(x^2\)  -> $x^2$
\[x^2\]  -> $$x^2$$
```

Chua nen parse LaTeX phuc tap o buoc nay.

## 6. Tao `modules/ingestion/markdown_processing/normalizer.py`

Them noi dung:

```python
import re

from modules.ingestion.markdown_processing.math_normalizer import normalize_math_delimiters
from modules.ingestion.markdown_processing.ocr_cleanup import fix_common_ocr_errors


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def remove_control_characters(text: str) -> str:
    return "".join(
        char for char in text
        if char == "\n" or char == "\t" or ord(char) >= 32
    )


def collapse_excess_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def ensure_trailing_newline(text: str) -> str:
    return text.rstrip() + "\n"


def normalize_markdown(text: str) -> str:
    text = normalize_newlines(text)
    text = remove_control_characters(text)
    text = fix_common_ocr_errors(text)
    text = normalize_math_delimiters(text)
    text = collapse_excess_blank_lines(text)
    text = ensure_trailing_newline(text)
    return text
```

Pipeline nay giup Markdown sach hon truoc khi luu vao PostgreSQL.

## 7. Tao `modules/ingestion/pdf_processing/gemini_pdf_converter.py`

Buoc 6 chua can noi Gemini that. Them placeholder:

```python
async def convert_pdf_to_markdown(
    *,
    filename: str,
    content: bytes,
) -> str:
    raise NotImplementedError("PDF to Markdown conversion is not implemented yet")
```

Ly do: nen cho luong Markdown chay end-to-end truoc. PDF + Gemini lam o buoc 7.

## 8. Tao `modules/ingestion/service.py`

Them noi dung:

```python
from infra.db.repositories.documents import DocumentRepository
from infra.storage.r2_client import R2StorageClient
from modules.ingestion.markdown_processing.normalizer import normalize_markdown
from modules.ingestion.pdf_processing.gemini_pdf_converter import convert_pdf_to_markdown


class IngestionService:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        storage_client: R2StorageClient,
    ) -> None:
        self.document_repository = document_repository
        self.storage_client = storage_client

    async def ingest_document(
        self,
        *,
        document_id: str,
        filename: str,
        content_type: str | None,
        file_bytes: bytes,
    ) -> None:
        document = await self.document_repository.get_document(document_id)

        if document is None:
            raise ValueError(f"Document not found: {document_id}")

        try:
            await self.document_repository.update_status(document, "processing")

            original_key = f"documents/{document_id}/original/{filename}"
            original_url = self.storage_client.upload_bytes(
                key=original_key,
                content=file_bytes,
                content_type=content_type,
            )

            await self.document_repository.save_r2_original(
                document,
                r2_original_key=original_key,
                r2_original_url=original_url,
            )

            if document.source_type == "markdown":
                raw_markdown = file_bytes.decode("utf-8")
            elif document.source_type == "pdf":
                raw_markdown = await convert_pdf_to_markdown(
                    filename=filename,
                    content=file_bytes,
                )
            else:
                raise ValueError(f"Unsupported source type: {document.source_type}")

            markdown = normalize_markdown(raw_markdown)

            await self.document_repository.save_markdown(
                document,
                markdown,
            )

        except Exception as exc:
            await self.document_repository.mark_failed(
                document,
                str(exc),
            )
            raise
```

## 9. Test rieng Markdown normalizer

Tao file:

```text
scripts/test_markdown_normalizer.py
```

Noi dung:

```python
from modules.ingestion.markdown_processing.normalizer import normalize_markdown


text = "Title\r\n\r\n\r\nText with math \\(x^2\\)\r\n"
print(normalize_markdown(text))
```

Chay:

```powershell
python -m scripts.test_markdown_normalizer
```

Ket qua mong doi:

```text
Title

Text with math $x^2$
```

## 10. Test ingestion voi Markdown

Sau khi tao xong module ingestion, co the tao script test rieng:

```text
scripts/test_ingestion_markdown.py
```

Noi dung:

```python
import asyncio

from infra.db.repositories.documents import DocumentRepository
from infra.db.session import AsyncSessionLocal
from infra.storage.r2_client import R2StorageClient
from modules.ingestion.service import IngestionService


async def main() -> None:
    file_bytes = b"# Demo\r\n\r\nMath: \\(x^2\\)\r\n"

    async with AsyncSessionLocal() as session:
        repo = DocumentRepository(session)

        document = await repo.create_document(
            filename="demo.md",
            content_type="text/markdown",
            size_bytes=len(file_bytes),
            source_type="markdown",
        )

        ingestion = IngestionService(
            document_repository=repo,
            storage_client=R2StorageClient(),
        )

        await ingestion.ingest_document(
            document_id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            file_bytes=file_bytes,
        )

        updated = await repo.get_document(document.id)
        print("Status:", updated.status)
        print("R2 key:", updated.r2_original_key)
        print("Markdown:")
        print(updated.markdown_content)


if __name__ == "__main__":
    asyncio.run(main())
```

Chay:

```powershell
python -m scripts.test_ingestion_markdown
```

Neu thanh cong, ket qua nen co:

```text
Status: completed
R2 key: documents/<document_id>/original/demo.md
Markdown:
# Demo

Math: $x^2$
```

Dong thoi Cloudflare R2 se co file:

```text
documents/<document_id>/original/demo.md
```

PostgreSQL se co `markdown_content` va `markdown_checksum`.

## 11. Kiem tra trong PostgreSQL

Vao `psql`:

```powershell
psql -h localhost -p 5432 -U postgres -d datn_db
```

Chay:

```sql
SELECT id, filename, source_type, status, r2_original_key, markdown_checksum
FROM documents
ORDER BY created_at DESC
LIMIT 5;
```

Neu thay document moi co:

```text
status = completed
r2_original_key co gia tri
markdown_checksum co gia tri
```

thi buoc 6 da hoan thanh voi Markdown.

## 12. Luu y quan trong

- Buoc 6 chua noi frontend.
- Buoc 6 chua can Gemini PDF that.
- Neu test PDF o buoc nay, status co the thanh `failed` vi `convert_pdf_to_markdown` dang la placeholder.
- Nen dam bao Markdown chay end-to-end truoc khi lam PDF.
- Sau buoc 6, co the qua buoc 7 tich hop Gemini hoac qua buoc 9 de noi ingestion vao `DocumentService`.

