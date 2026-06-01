# Huong Dan Buoc 4.11: Mo Rong Pydantic Models Cho Document API

## 1. Muc tieu

Buoc 4.11 tap trung vao viec hoan thien contract du lieu giua backend API va frontend.

Sau cac buoc truoc, backend da co:

```text
PostgreSQL documents table
 -> DocumentRepository
 -> DocumentService
 -> FastAPI endpoints
```

Buoc 4.11 can dam bao API response tra ve du metadata de frontend:

```text
- Hien thi danh sach tai lieu.
- Theo doi trang thai xu ly bang polling.
- Bao loi khi R2, Gemini hoac normalize that bai.
- Biet khi nao Markdown da san sang.
- Lay Markdown da chuan hoa de kiem tra ket qua ingestion.
```

File chinh can lam viec:

```text
apps/api/v1/models/documents.py
```

Hai file lien quan can doi chieu:

```text
apps/api/v1/services/documents.py
apps/api/v1/endpoints/documents.py
```

Test can cap nhat:

```text
tests/api/test_documents.py
```

## 2. Trang thai hien tai cua du an

Sau khi ra soat code hien tai, phan lon noi dung buoc 4.11 da duoc them trong commit buoc 4.10.

Tai:

```text
apps/api/v1/models/documents.py
```

Da co enum status:

```python
class DocumentStatus(StrEnum):
    uploaded = "uploaded"
    processing = "processing"
    completed = "completed"
    failed = "failed"
```

Y nghia:

```text
uploaded     document row vua duoc tao, dang cho background task
processing   dang upload R2, convert PDF hoac normalize Markdown
completed    markdown_content da duoc luu vao PostgreSQL
failed       ingestion that bai va error_message da duoc luu
```

`DocumentResponse` hien da co cac field can thiet:

```python
class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str | None = None
    size_bytes: int = Field(ge=0)
    source_type: str
    status: DocumentStatus
    message: str
    r2_original_key: str | None = None
    r2_original_url: str | None = None
    markdown_available: bool
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None = None
```

`DocumentMarkdownResponse` cung da co:

```python
class DocumentMarkdownResponse(BaseModel):
    id: str
    markdown_content: str
    markdown_checksum: str | None = None
```

Vi vay, khong can viet lai toan bo file model. Chi can bo sung field con thieu trong status response va cap nhat test.

## 3. Vi sao can mo rong response model

Database model tai:

```text
infra/db/models.py
```

Da co cac cot:

```text
r2_original_key
r2_original_url
markdown_content
markdown_checksum
error_message
created_at
updated_at
processed_at
```

Neu Pydantic model khong expose cac field phu hop, du lieu van ton tai trong PostgreSQL nhung frontend khong the su dung.

Vi du:

```text
markdown_content co trong DB
nhung frontend chi can markdown_available trong danh sach tai lieu
```

Khong nen tra `markdown_content` trong moi response danh sach vi Markdown co the rat lon. Noi dung day du chi nen tra qua endpoint rieng:

```text
GET /documents/{document_id}/markdown
```

## 4. Bo sung `updated_at` vao status response

File can sua:

```text
apps/api/v1/models/documents.py
```

Vi tri hien tai:

```text
Dong 35-40: class DocumentStatusResponse
```

Hien tai:

```python
class DocumentStatusResponse(BaseModel):
    id: str
    status: DocumentStatus
    message: str
    markdown_available: bool
    error_message: str | None = None
```

Them mot dong ngay sau `error_message`:

```python
    updated_at: datetime
```

Ket qua:

```python
class DocumentStatusResponse(BaseModel):
    id: str
    status: DocumentStatus
    message: str
    markdown_available: bool
    error_message: str | None = None
    updated_at: datetime
```

Muc dich:

```text
- Frontend polling co the biet record duoc cap nhat luc nao.
- De debug khi tai lieu bi ket o status processing.
- Dong bo voi documents.updated_at da co trong PostgreSQL.
```

Khong can import them `datetime`, vi dau file da co:

```python
from datetime import datetime
```

## 5. Tra `updated_at` tu endpoint status

Sau khi them field bat buoc vao `DocumentStatusResponse`, endpoint tao model nay cung phai truyen gia tri.

File can sua:

```text
apps/api/v1/endpoints/documents.py
```

Vi tri hien tai:

```text
Dong 115-121: return DocumentStatusResponse(...)
```

Hien tai:

```python
return DocumentStatusResponse(
    id=document.id,
    status=document.status,
    message=document.message,
    markdown_available=document.markdown_available,
    error_message=document.error_message,
)
```

Them:

```python
    updated_at=document.updated_at,
```

Ket qua:

```python
return DocumentStatusResponse(
    id=document.id,
    status=document.status,
    message=document.message,
    markdown_available=document.markdown_available,
    error_message=document.error_message,
    updated_at=document.updated_at,
)
```

Ly do:

```text
DocumentService._to_response(...) da anh xa document.updated_at tu DB.
Endpoint status chi can lay lai gia tri nay de tra response gon.
```

## 6. Kiem tra mapping trong `DocumentService`

File can doc lai, khong can sua neu noi dung van giong hien tai:

```text
apps/api/v1/services/documents.py
```

Vi tri:

```text
Dong 71-87: def _to_response(...)
```

Can dam bao co cac mapping:

```python
source_type=document.source_type,
r2_original_key=document.r2_original_key,
r2_original_url=document.r2_original_url,
markdown_available=document.markdown_content is not None,
error_message=document.error_message,
updated_at=document.updated_at,
processed_at=document.processed_at,
```

Giai thich:

```text
source_type
  Cho biet tai lieu goc la PDF hay Markdown.

r2_original_key
  Key object cua file goc trong Cloudflare R2.

r2_original_url
  Public URL neu bucket hoac domain R2 duoc cau hinh public.

markdown_available
  Chi tra boolean thay vi markdown_content lon.
  Gia tri true khi PostgreSQL da co markdown_content.

error_message
  Hien loi khi ingestion that bai.

updated_at
  Thoi diem record duoc cap nhat gan nhat.

processed_at
  Thoi diem ingestion hoan thanh thanh cong.
```

## 7. Kiem tra endpoint lay Markdown

File can doc lai, khong can sua neu endpoint da ton tai:

```text
apps/api/v1/endpoints/documents.py
```

Vi tri:

```text
Dong 123-148: GET /documents/{document_id}/markdown
```

Endpoint can tra:

```python
return DocumentMarkdownResponse(
    id=document.id,
    markdown_content=document.markdown_content,
    markdown_checksum=document.markdown_checksum,
)
```

Muc dich:

```text
- Cho phep kiem tra Markdown sau khi Gemini convert va normalizer xu ly.
- Cung cap markdown_checksum de phat hien noi dung thay doi.
- Khong dua noi dung Markdown lon vao GET /documents hoac GET /documents/{id}.
```

Trang thai loi hop ly hien tai:

```text
Document khong ton tai              -> HTTP 404
Document chua co markdown_content    -> HTTP 404
```

Co the doi truong hop thu hai thanh HTTP 409 o buoc hoan thien API sau. Buoc 4.11 chua bat buoc thay doi.

## 8. Cap nhat test API theo response moi

File can sua:

```text
tests/api/test_documents.py
```

Vi tri:

```text
Dong 27-33: assert response cua GET /documents/{document_id}/status
```

Test hien tai dang so sanh dict cu:

```python
assert status_response.json() == {
    "id": document_id,
    "status": "uploaded",
    "message": "Document uploaded and waiting for processing",
}
```

Response status hien da co them:

```text
markdown_available
error_message
```

Sau khi hoan thien buoc 4.11 se co them:

```text
updated_at
```

Khong nen so sanh toan bo dict bang mot timestamp co dinh. Thay doan assert cu bang:

```python
status_data = status_response.json()

assert status_data["id"] == document_id
assert status_data["status"] == "uploaded"
assert status_data["message"] == "Document uploaded and waiting for processing"
assert status_data["markdown_available"] is False
assert status_data["error_message"] is None
assert status_data["updated_at"]
```

Ly do:

```text
- `updated_at` thay doi theo thoi gian tao record.
- Kiem tra tung field giup test ro rang hon khi API contract thay doi.
- Test xac nhan document vua upload chua co Markdown.
```

Luu y:

```text
Test API hien tai chua mock background ingestion va R2.
Neu BackgroundTasks chay that trong TestClient, test co the phu thuoc vao cau hinh R2.
Phan mock R2, Gemini va DB nen duoc bo sung trong buoc test integration sau.
```

## 9. Khong can sua database

Khong sua:

```text
infra/db/models.py
infra/db/repositories/documents.py
modules/ingestion/service.py
infra/storage/r2_client.py
```

Ly do:

```text
- DB model da co du cot metadata.
- Repository da luu checksum, processed_at va error_message.
- IngestionService da cap nhat status processing, completed va failed.
- Buoc 4.11 chi hoan thien API contract.
```

## 10. Khong sua frontend trong buoc nay

Khong sua:

```text
apps/frontend/src/pages/UploadDocument.jsx
```

Ly do:

```text
Frontend upload API that thuoc buoc 4.12.
Buoc 4.11 chi can backend response on dinh truoc khi frontend su dung.
```

## 11. Response mong doi

### 11.1 `GET /documents/{document_id}`

Vi du:

```json
{
  "id": "uuid",
  "filename": "sample.md",
  "content_type": "text/markdown",
  "size_bytes": 128,
  "source_type": "markdown",
  "status": "completed",
  "message": "Document processed successfully",
  "r2_original_key": "documents/uuid/original/sample.md",
  "r2_original_url": null,
  "markdown_available": true,
  "error_message": null,
  "created_at": "2026-05-31T10:00:00Z",
  "updated_at": "2026-05-31T10:00:01Z",
  "processed_at": "2026-05-31T10:00:01Z"
}
```

### 11.2 `GET /documents/{document_id}/status`

Vi du:

```json
{
  "id": "uuid",
  "status": "processing",
  "message": "Document is being processed",
  "markdown_available": false,
  "error_message": null,
  "updated_at": "2026-05-31T10:00:01Z"
}
```

### 11.3 `GET /documents/{document_id}/markdown`

Vi du:

```json
{
  "id": "uuid",
  "markdown_content": "# Sample\n\nContent\n",
  "markdown_checksum": "sha256..."
}
```

## 12. Lenh kiem tra

Sau khi sua code, kiem tra syntax:

```powershell
python -m compileall apps core infra modules tests
```

Chay test API:

```powershell
pytest tests/api/test_documents.py -v
```

Neu dang chay backend local:

```powershell
uvicorn apps.api.main:app --reload
```

Kiem tra Swagger:

```text
http://localhost:8000/docs
```

Trong Swagger, kiem tra cac endpoint:

```text
POST /documents/upload
GET  /documents
GET  /documents/{document_id}
GET  /documents/{document_id}/status
GET  /documents/{document_id}/markdown
```

## 13. Thu tu thuc hien

Lam lan luot:

```text
1. Mo apps/api/v1/models/documents.py.
2. Them updated_at: datetime vao DocumentStatusResponse.
3. Mo apps/api/v1/endpoints/documents.py.
4. Them updated_at=document.updated_at vao response status.
5. Mo tests/api/test_documents.py.
6. Cap nhat assert cua status response theo contract moi.
7. Chay syntax check.
8. Chay test API hoac kiem tra thu cong qua Swagger.
```

## 14. Tieu chi hoan thanh

Buoc 4.11 hoan thanh khi:

```text
1. DocumentResponse co source_type.
2. DocumentResponse co r2_original_key va r2_original_url.
3. DocumentResponse co markdown_available.
4. DocumentResponse co error_message.
5. DocumentResponse co updated_at va processed_at.
6. DocumentStatusResponse co markdown_available.
7. DocumentStatusResponse co error_message.
8. DocumentStatusResponse co updated_at.
9. DocumentMarkdownResponse co markdown_content va markdown_checksum.
10. Endpoint status tra dung updated_at.
11. Endpoint Markdown tra dung noi dung va checksum.
12. Test API duoc cap nhat theo response moi.
```

Sau khi hoan thanh buoc nay, co the chuyen sang buoc 4.12: ket noi frontend upload voi backend API that.
