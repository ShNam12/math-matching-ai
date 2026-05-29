# Huong Dan Buoc 4.9: Sua API Document Service De Dung PostgreSQL Va IngestionService

## 1. Muc tieu

Buoc 4.9 tap trung sua service API hien tai:

```text
apps/api/v1/services/documents.py
```

Hien file nay van la service mock:

```text
- Luu document trong RAM bang dict _documents
- Ghi file local vao data/uploads
- Chua tao document trong PostgreSQL
- Chua goi IngestionService de upload R2, convert PDF, normalize Markdown va luu DB
```

Sau buoc 4.9, luong upload mong muon la:

```text
POST /documents/upload
 -> validate file
 -> tao document row trong PostgreSQL voi status = uploaded
 -> tra response som cho frontend
 -> background task goi IngestionService
 -> IngestionService upload file goc len R2
 -> PDF thi convert qua Gemini, Markdown thi decode truc tiep
 -> normalize_markdown(...)
 -> save markdown_content vao PostgreSQL
 -> status = completed hoac failed
```

## 2. Cac file lien quan

File chinh can sua:

```text
apps/api/v1/services/documents.py
```

File endpoint cung can sua de service moi hoat dong:

```text
apps/api/v1/endpoints/documents.py
```

File response model co the can mo rong sau:

```text
apps/api/v1/models/documents.py
```

Cac file ha tang hien da co va se duoc dung lai:

```text
infra/db/session.py
infra/db/repositories/documents.py
infra/storage/r2_client.py
modules/ingestion/service.py
```

## 3. Trang thai hien tai

`modules/ingestion/service.py` hien da dung vai tro orchestration:

```text
- Lay document tu repository
- Cap nhat status = processing
- Upload file goc len R2
- Neu source_type = markdown thi decode bytes
- Neu source_type = pdf thi goi convert_pdf_to_markdown
- Goi normalize_markdown
- Luu markdown vao PostgreSQL
- Neu loi thi mark_failed
```

Vi vay buoc 4.9 khong can dua logic Gemini, R2 hay Markdown normalize vao API service.

API service chi nen lam viec API-level:

```text
- Validate upload
- Tao document row
- Chuyen file_bytes cho background ingestion
- Doc document/status tu PostgreSQL de tra response
```

## 4. Van de trong `apps/api/v1/services/documents.py`

File hien tai co dang:

```python
class DocumentService:
    def __init__(self) -> None:
        self._documents: dict[str, DocumentResponse] = {}
        self._upload_dir = Path("data/uploads")
        self._allowed_suffixes = {".pdf", ".md", ".markdown"}
```

Can bo:

```text
self._documents
self._upload_dir
uuid4
datetime
write_bytes vao data/uploads
```

Ly do:

```text
- RAM dict mat du lieu khi restart server
- data/uploads khong phai storage chinh cua he thong
- Document metadata phai nam trong PostgreSQL
- File goc phai duoc IngestionService upload len R2
```

## 5. Thiet ke moi cho `DocumentService`

`DocumentService` nen nhan `DocumentRepository` tu ben ngoai:

```python
from pathlib import Path

from fastapi import UploadFile

from apps.api.v1.models.documents import DocumentResponse, DocumentStatus
from core.config.settings import settings
from infra.db.models import Document
from infra.db.repositories.documents import DocumentRepository


class DocumentService:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self.document_repository = document_repository
        self._allowed_suffixes = {".pdf", ".md", ".markdown"}
```

Khong nen giu singleton global:

```python
document_service = DocumentService()
```

Ly do: service moi can DB session theo tung request.

## 6. Them helper xac dinh source_type

Trong `DocumentService`, nen co helper:

```python
def _get_source_type(self, filename: str) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        return "pdf"

    if suffix in {".md", ".markdown"}:
        return "markdown"

    raise ValueError("Only PDF and Markdown files are supported")
```

Y nghia:

```text
.pdf       -> source_type = pdf
.md        -> source_type = markdown
.markdown  -> source_type = markdown
file khac  -> reject
```

## 7. Them validate size

Sau khi doc bytes:

```python
content = await file.read()
```

Can kiem tra rong va qua lon:

```python
if not content:
    raise ValueError("Uploaded file is empty")

max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
if len(content) > max_size_bytes:
    raise ValueError(f"File size must not exceed {settings.max_upload_size_mb} MB")
```

Gia tri `max_upload_size_mb` da co trong:

```text
core/config/settings.py
```

## 8. Tao document trong PostgreSQL

Trong `create_from_upload`, sau khi validate:

```python
document = await self.document_repository.create_document(
    filename=filename,
    content_type=file.content_type,
    size_bytes=len(content),
    source_type=source_type,
)
```

Document moi tao se co:

```text
status = uploaded
markdown_content = null
r2_original_key = null
error_message = null
```

Sau do background ingestion se cap nhat cac cot con lai.

## 9. Can tra ve ca response va file_bytes

Endpoint can `file_bytes` de dua vao background task.

Vi vay `create_from_upload` nen return tuple:

```python
async def create_from_upload(
    self,
    file: UploadFile,
) -> tuple[DocumentResponse, bytes]:
```

Cuoi ham:

```python
return self._to_response(document), content
```

Day la cach don gian cho MVP.

Sau nay neu muon gon hon, co the tao dataclass noi bo:

```text
DocumentUploadResult(response, file_bytes)
```

## 10. Them helper convert DB model sang response

Nen them helper:

```python
def _to_response(self, document: Document) -> DocumentResponse:
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        size_bytes=document.size_bytes,
        status=DocumentStatus(document.status),
        message=self._build_message(document.status),
        created_at=document.created_at,
    )
```

Them helper message:

```python
def _build_message(self, status: str) -> str:
    if status == "uploaded":
        return "Document uploaded and waiting for processing"
    if status == "processing":
        return "Document is being processed"
    if status == "completed":
        return "Document processed successfully"
    if status == "failed":
        return "Document processing failed"
    return "Document status is unknown"
```

Neu sau nay mo rong `DocumentResponse` co `error_message`, co the dua `document.error_message` vao response.

## 11. Sua `get`

Hien tai:

```python
def get(self, document_id: str) -> DocumentResponse | None:
    return self._documents.get(document_id)
```

Can doi thanh async va doc tu PostgreSQL:

```python
async def get(self, document_id: str) -> DocumentResponse | None:
    document = await self.document_repository.get_document(document_id)

    if document is None:
        return None

    return self._to_response(document)
```

Sau thay doi nay, endpoint goi `get` phai them `await`.

## 12. Noi dung de xuat cho `apps/api/v1/services/documents.py`

Co the thay file hien tai bang cau truc sau:

```python
from pathlib import Path

from fastapi import UploadFile

from apps.api.v1.models.documents import DocumentResponse, DocumentStatus
from core.config.settings import settings
from infra.db.models import Document
from infra.db.repositories.documents import DocumentRepository


class DocumentService:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self.document_repository = document_repository
        self._allowed_suffixes = {".pdf", ".md", ".markdown"}

    async def create_from_upload(
        self,
        file: UploadFile,
    ) -> tuple[DocumentResponse, bytes]:
        filename = Path(file.filename or "").name
        if not filename:
            raise ValueError("Uploaded file must have a filename")

        source_type = self._get_source_type(filename)

        content = await file.read()
        if not content:
            raise ValueError("Uploaded file is empty")

        max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
        if len(content) > max_size_bytes:
            raise ValueError(
                f"File size must not exceed {settings.max_upload_size_mb} MB"
            )

        document = await self.document_repository.create_document(
            filename=filename,
            content_type=file.content_type,
            size_bytes=len(content),
            source_type=source_type,
        )

        return self._to_response(document), content

    async def get(self, document_id: str) -> DocumentResponse | None:
        document = await self.document_repository.get_document(document_id)

        if document is None:
            return None

        return self._to_response(document)

    def _get_source_type(self, filename: str) -> str:
        suffix = Path(filename).suffix.lower()

        if suffix == ".pdf":
            return "pdf"

        if suffix in {".md", ".markdown"}:
            return "markdown"

        raise ValueError("Only PDF and Markdown files are supported")

    def _to_response(self, document: Document) -> DocumentResponse:
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            status=DocumentStatus(document.status),
            message=self._build_message(document.status),
            created_at=document.created_at,
        )

    def _build_message(self, status: str) -> str:
        if status == "uploaded":
            return "Document uploaded and waiting for processing"
        if status == "processing":
            return "Document is being processed"
        if status == "completed":
            return "Document processed successfully"
        if status == "failed":
            return "Document processing failed"
        return "Document status is unknown"
```

## 13. Sua endpoint upload

File:

```text
apps/api/v1/endpoints/documents.py
```

Hien endpoint dang dung singleton:

```python
from apps.api.v1.services.documents import document_service
```

Can bo import nay.

Them imports:

```python
from fastapi import BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.services.documents import DocumentService
from infra.db.repositories.documents import DocumentRepository
from infra.db.session import AsyncSessionLocal, get_db_session
from infra.storage.r2_client import R2StorageClient
from modules.ingestion.service import IngestionService
```

Luu y: Neu da co import `fastapi` tren cung mot dong, gop lai cho gon.

## 14. Them background ingestion function

Trong `apps/api/v1/endpoints/documents.py`, them function:

```python
async def run_ingestion_background(
    document_id: str,
    filename: str,
    content_type: str | None,
    file_bytes: bytes,
) -> None:
    async with AsyncSessionLocal() as session:
        repo = DocumentRepository(session)
        ingestion = IngestionService(
            document_repository=repo,
            storage_client=R2StorageClient(),
        )

        await ingestion.ingest_document(
            document_id=document_id,
            filename=filename,
            content_type=content_type,
            file_bytes=file_bytes,
        )
```

Quan trong:

```text
Khong nen truyen request session vao background task.
Background task nen tao DB session moi bang AsyncSessionLocal.
```

## 15. Sua `upload_document`

Endpoint hien tai:

```python
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF or Markdown document to upload")],
) -> DocumentUploadResponse:
```

Can doi thanh:

```python
async def upload_document(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(description="PDF or Markdown document to upload")],
    session: AsyncSession = Depends(get_db_session),
) -> DocumentUploadResponse:
```

Trong body:

```python
repo = DocumentRepository(session)
service = DocumentService(repo)
document, file_bytes = await service.create_from_upload(file)

background_tasks.add_task(
    run_ingestion_background,
    document.id,
    document.filename,
    document.content_type,
    file_bytes,
)

return document
```

Giu lai `except ValueError` de tra HTTP 400.

## 16. Sua `get_document`

Hien tai:

```python
document = document_service.get(document_id)
```

Can doi thanh:

```python
repo = DocumentRepository(session)
service = DocumentService(repo)
document = await service.get(document_id)
```

Endpoint can them dependency:

```python
session: AsyncSession = Depends(get_db_session)
```

Dang de xuat:

```python
@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> DocumentResponse:
    repo = DocumentRepository(session)
    service = DocumentService(repo)
    document = await service.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document
```

## 17. Sua `get_document_status`

Tuong tu `get_document`, endpoint status phai doc tu PostgreSQL:

```python
@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> DocumentStatusResponse:
    repo = DocumentRepository(session)
    service = DocumentService(repo)
    document = await service.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return DocumentStatusResponse(
        id=document.id,
        status=document.status,
        message=document.message,
    )
```

## 18. Luong sau khi sua

Sau buoc 4.9:

```text
POST /documents/upload
 -> DocumentService.validate
 -> DocumentRepository.create_document
 -> response status uploaded
 -> BackgroundTasks.run_ingestion_background
 -> IngestionService.ingest_document
 -> R2 upload
 -> PDF/Markdown to raw markdown
 -> normalize_markdown
 -> DocumentRepository.save_markdown
 -> status completed
```

Neu loi trong background ingestion:

```text
status = failed
error_message = noi dung loi
```

## 19. Test nhanh upload Markdown

Nen test Markdown truoc PDF vi khong phu thuoc Gemini.

Chay API server:

```powershell
uvicorn apps.api.main:app --reload
```

Upload Markdown bang PowerShell:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/documents/upload" `
  -Method Post `
  -Form @{ file = Get-Item ".\data\samples\demo.md" }
```

Ket qua ban dau mong doi:

```text
status = uploaded
```

Sau do kiem tra status:

```powershell
Invoke-RestMethod "http://localhost:8000/documents/<document_id>/status"
```

Ket qua sau khi background task xong:

```text
status = completed
```

## 20. Kiem tra PostgreSQL

Dung SQL:

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

Voi Markdown upload thanh cong, can thay:

```text
source_type = markdown
status = completed
r2_original_key co gia tri
markdown_checksum co gia tri
error_message = null
processed_at co gia tri
```

## 21. Test file sai dinh dang

Upload file `.txt` hoac `.docx`.

Ket qua mong doi:

```text
HTTP 400
Only PDF and Markdown files are supported
```

## 22. Test file qua lon

Neu file lon hon:

```text
settings.max_upload_size_mb
```

Ket qua mong doi:

```text
HTTP 400
File size must not exceed <N> MB
```

## 23. Luu y quan trong

Khong dua cac logic sau vao `apps/api/v1/services/documents.py`:

```text
- Gemini PDF converter
- Markdown normalizer
- OCR cleanup
- Upload R2 truc tiep trong API service
- SHA256 markdown checksum
```

Nhung logic do da co noi dung rieng:

```text
modules/ingestion
infra/storage
infra/db/repositories
```

`apps/api/v1/services/documents.py` chi nen dieu phoi upload API va mapping response.

## 24. Tieu chi hoan thanh

Buoc 4.9 hoan thanh khi:

```text
1. apps/api/v1/services/documents.py khong con _documents.
2. apps/api/v1/services/documents.py khong con ghi file vao data/uploads.
3. Upload tao row moi trong PostgreSQL voi status = uploaded.
4. Endpoint upload enqueue background ingestion.
5. Background task goi modules.ingestion.service.IngestionService.
6. GET /documents/{id} doc tu PostgreSQL.
7. GET /documents/{id}/status doc tu PostgreSQL.
8. Upload Markdown that chuyen tu uploaded -> processing -> completed.
9. PostgreSQL co markdown_content va markdown_checksum.
10. Neu loi R2/Gemini/normalize thi status = failed va co error_message.
```
