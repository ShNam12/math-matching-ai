# Huong Dan Buoc 4.7: Tich Hop Gemini PDF Sang Markdown

## 1. Muc tieu cua buoc 4.7

Buoc 4.7 se thay placeholder PDF hien tai bang logic goi Gemini that de chuyen PDF sang Markdown.

Hien tai du an da co:

```text
modules/ingestion/pdf_processing/gemini_pdf_converter.py
```

Nhung file nay dang chi co:

```python
async def convert_pdf_to_markdown(
    *,
    filename: str,
    content: bytes,
) -> str:
    raise NotImplementedError("PDF to Markdown conversion is not implemented yet")
```

Sau buoc 4.7, luong PDF mong muon la:

```text
Upload PDF
 -> tao document trong PostgreSQL voi source_type = pdf
 -> IngestionService upload file goc len Cloudflare R2
 -> convert_pdf_to_markdown(...) goi Gemini
 -> Gemini tra ve Markdown
 -> normalize_markdown(...)
 -> save_markdown(...) luu markdown_content + markdown_checksum
 -> status = completed
```

Buoc nay chi tap trung vao PDF sang Markdown. Chua can sua frontend neu frontend chua noi backend that.

## 2. File va thu muc lien quan

Nhung file can quan tam:

```text
core/config/settings.py
requirements.txt
.env
modules/ingestion/pdf_processing/gemini_pdf_converter.py
modules/ingestion/service.py
scripts/test_ingestion_markdown.py
```

Nhung file co the tao them de test:

```text
scripts/test_gemini_pdf_converter.py
scripts/test_ingestion_pdf.py
data/samples/sample.pdf
```

Khong can tao module moi. Buoc 4.7 chi cap nhat logic trong:

```text
modules/ingestion/pdf_processing/gemini_pdf_converter.py
```

## 3. Kiem tra dependency

Mo file:

```text
requirements.txt
```

Can dam bao co:

```text
google-genai
```

Du an cua ban hien da co dependency nay. Neu may chua cai package trong virtual environment, chay:

```powershell
pip install -r requirements.txt
```

Kiem tra nhanh:

```powershell
python -c "from google import genai; print('google-genai ok')"
```

Neu thay:

```text
google-genai ok
```

thi dependency da san sang.

## 4. Kiem tra cau hinh Gemini trong settings

Mo file:

```text
core/config/settings.py
```

Can co cac field:

```python
gemini_api_key: str
gemini_model: str = "gemini-2.5-flash"
```

Du an cua ban hien da co:

```python
class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
```

Nhu vay la dat yeu cau.

## 5. Kiem tra file `.env`

Mo file:

```text
.env
```

Can co:

```text
GEMINI_API_KEY=your_real_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Luu y:

- Khong de `GEMINI_API_KEY` rong.
- Khong dat dau nhay neu khong can.
- Khong commit `.env` len Git.
- Neu muon dung model khac, chi doi `GEMINI_MODEL`.

Kiem tra config doc duoc env:

```powershell
python -c "from core.config.settings import settings; print(settings.gemini_model); print(bool(settings.gemini_api_key))"
```

Ket qua mong doi:

```text
gemini-2.5-flash
True
```

## 6. Thiet ke converter PDF

File can sua:

```text
modules/ingestion/pdf_processing/gemini_pdf_converter.py
```

Vai tro cua file nay:

```text
Nhan filename + content bytes cua PDF
 -> ghi tam PDF ra file tam
 -> upload PDF len Gemini Files API
 -> goi model generate_content
 -> lay response.text
 -> validate Markdown tra ve khong rong
 -> xoa file tam
 -> return Markdown
```

Ly do can ghi file tam:

- `client.files.upload(...)` cua `google-genai` lam viec tot voi duong dan file.
- Du lieu PDF trong ingestion dang la `bytes`.
- Ghi vao `tempfile.NamedTemporaryFile` giup khong can luu file tam vao project.

## 7. Code can dat vao `gemini_pdf_converter.py`

Thay toan bo noi dung file:

```text
modules/ingestion/pdf_processing/gemini_pdf_converter.py
```

Bang:

```python
import tempfile
from pathlib import Path

from google import genai
from google.genai import types

from core.config.settings import settings


PDF_TO_MARKDOWN_PROMPT = """
Convert this PDF into clean Markdown.

Requirements:
- Preserve all meaningful content.
- Preserve headings, paragraphs, lists, tables, examples, and exercises.
- Preserve mathematical formulas using LaTeX.
- Use inline math as $...$.
- Use block math as $$...$$.
- Do not summarize.
- Do not omit content.
- Do not add explanations outside the converted document.
- Return only Markdown.
""".strip()


def _create_gemini_client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def _validate_pdf_input(filename: str, content: bytes) -> None:
    if not filename:
        raise ValueError("PDF filename is required")

    if not filename.lower().endswith(".pdf"):
        raise ValueError(f"Expected a PDF file, got: {filename}")

    if not content:
        raise ValueError("PDF content is empty")


def _extract_response_text(response: types.GenerateContentResponse) -> str:
    text = response.text or ""
    text = text.strip()

    if not text:
        raise ValueError("Gemini returned empty Markdown content")

    return text


async def convert_pdf_to_markdown(
    *,
    filename: str,
    content: bytes,
) -> str:
    _validate_pdf_input(filename, content)

    suffix = Path(filename).suffix or ".pdf"
    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        client = _create_gemini_client()

        uploaded_file = client.files.upload(
            file=temp_path,
            config={"mime_type": "application/pdf"},
        )

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=[
                PDF_TO_MARKDOWN_PROMPT,
                uploaded_file,
            ],
        )

        return _extract_response_text(response)

    finally:
        if temp_path is not None:
            Path(temp_path).unlink(missing_ok=True)
```

Ghi chu:

- `PDF_TO_MARKDOWN_PROMPT` giup Gemini tra ve Markdown sach.
- `_validate_pdf_input(...)` chan input sai som.
- `_extract_response_text(...)` dam bao khong luu Markdown rong vao PostgreSQL.
- `finally` dam bao file tam bi xoa ke ca khi Gemini loi.

## 8. Neu Pylance bao loi `config`

Neu dong nay bi Pylance bao loi:

```python
config={"mime_type": "application/pdf"}
```

Thi doi sang:

```python
config=types.UploadFileConfig(mime_type="application/pdf")
```

Luc do import `types` da co san:

```python
from google.genai import types
```

Neu SDK tren may ban khong nhan `mime_type`, thu doi thanh:

```python
config=types.UploadFileConfig(mimeType="application/pdf")
```

Tuy nhien voi `google-genai` ban moi, `mime_type` thuong la cach dung phu hop trong Python.

## 9. Luu y ve async

Ham `convert_pdf_to_markdown(...)` dang la:

```python
async def convert_pdf_to_markdown(...)
```

Nhung SDK `google-genai` trong vi du tren goi dong bo:

```python
client.files.upload(...)
client.models.generate_content(...)
```

Dieu nay van chay duoc, vi ham async co the chua code sync ben trong. Voi MVP hien tai chap nhan duoc.

Sau nay neu can toi uu, co the dua viec convert PDF sang worker rieng hoac background task. Chua can lam o buoc 4.7.

## 10. Test rieng Gemini PDF converter

Tao thu muc neu chua co:

```text
data/samples/
```

Dat mot file PDF that vao:

```text
data/samples/sample.pdf
```

Tao file:

```text
scripts/test_gemini_pdf_converter.py
```

Noi dung:

```python
import asyncio
from pathlib import Path

from modules.ingestion.pdf_processing.gemini_pdf_converter import (
    convert_pdf_to_markdown,
)


async def main() -> None:
    pdf_path = Path("data/samples/sample.pdf")

    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing sample PDF: {pdf_path}")

    markdown = await convert_pdf_to_markdown(
        filename=pdf_path.name,
        content=pdf_path.read_bytes(),
    )

    print("Markdown length:", len(markdown))
    print("Preview:")
    print(markdown[:2000])


if __name__ == "__main__":
    asyncio.run(main())
```

Chay:

```powershell
python -m scripts.test_gemini_pdf_converter
```

Ket qua mong doi:

```text
Markdown length: <so lon hon 0>
Preview:
...
```

Neu Markdown co heading, paragraph, cong thuc hoac noi dung PDF thi converter da hoat dong.

## 11. Test ingestion PDF end-to-end

Sau khi converter rieng da chay, tao file:

```text
scripts/test_ingestion_pdf.py
```

Noi dung:

```python
import asyncio
from pathlib import Path

from infra.db.repositories.documents import DocumentRepository
from infra.db.session import AsyncSessionLocal
from infra.storage.r2_client import R2StorageClient
from modules.ingestion.service import IngestionService


async def main() -> None:
    pdf_path = Path("data/samples/sample.pdf")

    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing sample PDF: {pdf_path}")

    file_bytes = pdf_path.read_bytes()

    async with AsyncSessionLocal() as session:
        repo = DocumentRepository(session)

        document = await repo.create_document(
            filename=pdf_path.name,
            content_type="application/pdf",
            size_bytes=len(file_bytes),
            source_type="pdf",
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

        print("ID:", updated.id)
        print("Status:", updated.status)
        print("R2 key:", updated.r2_original_key)
        print("Checksum:", updated.markdown_checksum)
        print("Markdown length:", len(updated.markdown_content or ""))
        print("Markdown preview:")
        print((updated.markdown_content or "")[:2000])


if __name__ == "__main__":
    asyncio.run(main())
```

Chay:

```powershell
python -m scripts.test_ingestion_pdf
```

Ket qua mong doi:

```text
Status: completed
R2 key: documents/<document_id>/original/sample.pdf
Checksum: <sha256>
Markdown length: <so lon hon 0>
Markdown preview:
...
```

Neu status la `completed`, buoc 4.7 da ket noi duoc PDF -> Gemini -> Markdown -> PostgreSQL.

## 12. Kiem tra PostgreSQL

Vao PostgreSQL:

```powershell
psql -h localhost -p 5432 -U postgres -d datn_db
```

Chay:

```sql
SELECT
    id,
    filename,
    source_type,
    status,
    r2_original_key,
    markdown_checksum,
    error_message,
    processed_at
FROM documents
ORDER BY created_at DESC
LIMIT 5;
```

Voi file PDF vua test, can thay:

```text
source_type = pdf
status = completed
r2_original_key co gia tri
markdown_checksum co gia tri
error_message = null
processed_at co gia tri
```

Neu muon xem noi dung Markdown:

```sql
SELECT LEFT(markdown_content, 2000)
FROM documents
WHERE id = '<document_id>';
```

## 13. Cac loi thuong gap va cach sua

### Loi 1: Thieu API key

Thong bao co the gap:

```text
API key not valid
GEMINI_API_KEY is missing
```

Cach sua:

Kiem tra `.env`:

```text
GEMINI_API_KEY=...
```

Sau do chay lai:

```powershell
python -c "from core.config.settings import settings; print(bool(settings.gemini_api_key))"
```

Phai ra:

```text
True
```

### Loi 2: Import `google` khong duoc

Thong bao:

```text
ModuleNotFoundError: No module named 'google'
```

Cach sua:

```powershell
pip install -r requirements.txt
```

Hoac:

```powershell
pip install google-genai
```

### Loi 3: Upload file len Gemini bi loi config

Neu gap loi lien quan:

```text
UploadFileConfig
mime_type
mimeType
```

Hay thu lan luot 2 cach:

```python
uploaded_file = client.files.upload(
    file=temp_path,
    config={"mime_type": "application/pdf"},
)
```

Hoac:

```python
uploaded_file = client.files.upload(
    file=temp_path,
    config=types.UploadFileConfig(mime_type="application/pdf"),
)
```

### Loi 4: Gemini tra ve Markdown rong

Thong bao:

```text
Gemini returned empty Markdown content
```

Cach xu ly:

- Kiem tra PDF co noi dung that khong.
- Thu file PDF nho hon.
- Doi prompt ro hon.
- Kiem tra model trong `.env`.

### Loi 5: Document status = failed

Kiem tra cot:

```sql
SELECT status, error_message
FROM documents
ORDER BY created_at DESC
LIMIT 5;
```

Neu `error_message` lien quan Gemini, sua converter.

Neu `error_message` lien quan R2, sua `.env` R2 hoac `R2StorageClient`.

Neu `error_message` lien quan DB, kiem tra PostgreSQL va model `Document`.

## 14. Kiem tra R2

Sau khi test PDF end-to-end, Cloudflare R2 can co file goc:

```text
documents/<document_id>/original/sample.pdf
```

Buoc 4.7 khong bat buoc upload Markdown len R2. Markdown hien luu chinh trong PostgreSQL:

```text
documents.markdown_content
documents.markdown_checksum
```

Dieu nay dung voi cac buoc tiep theo, vi segmentation se doc Markdown tu PostgreSQL.

## 15. Co can sua `IngestionService` khong?

Hien tai `modules/ingestion/service.py` da co logic:

```python
elif document.source_type == "pdf":
    raw_markdown = await convert_pdf_to_markdown(
        filename=filename,
        content=file_bytes,
    )
```

Vi vay neu ban da lam dung buoc 6, buoc 4.7 khong can sua `IngestionService`.

Chi can thay placeholder trong:

```text
modules/ingestion/pdf_processing/gemini_pdf_converter.py
```

la PDF flow se duoc kich hoat.

## 16. Co can sua frontend khong?

Chua can.

Buoc 4.7 nen test bang script backend truoc:

```powershell
python -m scripts.test_gemini_pdf_converter
python -m scripts.test_ingestion_pdf
```

Chi khi backend PDF flow on dinh moi noi frontend upload vao API that.

## 17. Tieu chi hoan thanh buoc 4.7

Buoc 4.7 duoc xem la hoan thanh khi dat du cac dieu kien:

```text
1. `gemini_pdf_converter.py` khong con raise NotImplementedError.
2. `python -m scripts.test_gemini_pdf_converter` tra ve Markdown length > 0.
3. `python -m scripts.test_ingestion_pdf` chay thanh cong.
4. File PDF goc duoc upload len Cloudflare R2.
5. PostgreSQL co document source_type = pdf.
6. Document status = completed.
7. `markdown_content` co noi dung Markdown.
8. `markdown_checksum` co gia tri SHA256.
9. `error_message` rong hoac null.
```

## 18. Tai lieu tham khao

Google Gemini Files API:

```text
https://ai.google.dev/api/files
```

Google Gemini generate content:

```text
https://ai.google.dev/api/generate-content
```

Ghi chu quan trong:

- Nen dung package `google-genai`.
- Khong dung package legacy `google-generativeai` cho code moi.
- Files API phu hop cho PDF vi PDF la input file, khong phai text ngan.
