# Thiet Ke Chi Tiet He Thong Xu Ly Tai Lieu Dau Vao

## 1. Muc tieu tai lieu

Tai lieu nay mo ta thiet ke chi tiet cho chuong trinh xu ly tai lieu dau vao cua du an DATN.

Muc tieu chinh:

- Giup AI/coder hieu dung kien truc hien tai cua he thong.
- Lam co so de xay dung cau truc database PostgreSQL.
- Xac dinh vi tri file can them/sua trong backend va frontend.
- Dinh nghia luong upload PDF/Markdown, chuyen PDF sang Markdown bang Gemini, chuan hoa Markdown, luu file goc vao Cloudflare R2 va luu Markdown vao PostgreSQL.

Pham vi cua tai lieu nay tap trung vao buoc xu ly tai lieu dau vao, con goi la ingestion.

## 2. Hien trang du an

Cau truc thuc te hien co:

```text
DATN/
  apps/
    api/
      main.py
      v1/
        endpoints/
          documents.py
        models/
          documents.py
        services/
          documents.py
        utils/
    frontend/
      src/
        App.jsx
        pages/
          UploadDocument.jsx
  core/
    config/
      settings.py
  modules/
    ingestion/
  infra/
  tests/
    api/
      test_documents.py
  requirements.txt
  .env
```

Nhan xet:

- Backend dang dung FastAPI.
- Frontend dang dung React/Vite.
- API upload document da ton tai o `apps/api/v1/endpoints/documents.py`.
- Logic upload hien nam trong `apps/api/v1/services/documents.py`.
- Model API hien nam trong `apps/api/v1/models/documents.py`.
- Frontend upload hien dang la giao dien mock trong `apps/frontend/src/pages/UploadDocument.jsx`.
- `modules/ingestion` da co thu muc nhung chua co logic.
- `infra` dang trong, nen can bo sung database, storage, migration tai day.
- `core/config/settings.py` can duoc chuyen thanh module cau hinh hop le.

## 3. Nguyen tac kien truc

He thong nen chia thanh 4 lop ro rang:

```text
Frontend
  -> API Layer
  -> Business Module
  -> Infrastructure Layer
```

Trong do:

- Frontend: hien thi upload, danh sach tai lieu, trang thai xu ly.
- API Layer: nhan request, validate input co ban, tra response.
- Business Module: xu ly nghiep vu ingestion, Gemini, chuan hoa Markdown.
- Infrastructure Layer: ket noi PostgreSQL, Cloudflare R2, migration.

Khong nen de logic Gemini, R2, Markdown nam truc tiep trong endpoint.

Khong nen de `apps/api/v1/services/documents.py` lam tat ca moi viec. File nay chi nen dong vai tro dieu phoi API-level.

Logic xu ly tai lieu nen nam trong:

```text
modules/ingestion
```

Logic ha tang nen nam trong:

```text
infra
```

## 4. Luong xu ly tong the

Luong xu ly khi nguoi dung upload file:

```text
1. Frontend chon file PDF/Markdown.
2. Frontend gui POST /documents/upload voi multipart/form-data.
3. Backend nhan UploadFile.
4. Backend validate:
   - Co filename hay khong.
   - Extension co thuoc .pdf, .md, .markdown hay khong.
   - Dung luong co vuot MAX_UPLOAD_SIZE_MB hay khong.
5. Backend tao ban ghi documents trong PostgreSQL voi status = uploaded.
6. Backend chuyen status = processing.
7. Backend upload file goc len Cloudflare R2.
8. Neu file la PDF:
   - Goi Gemini API de chuyen PDF sang Markdown.
9. Neu file la Markdown:
   - Decode noi dung file thanh text.
10. Chay pipeline chuan hoa Markdown.
11. Luu Markdown da chuan hoa vao PostgreSQL.
12. Cap nhat documents.status = completed.
13. Neu co loi o bat ky buoc nao:
   - Cap nhat documents.status = failed.
   - Luu error_message.
14. Frontend polling GET /documents/{id}/status de cap nhat UI.
15. Frontend co the goi GET /documents/{id}/markdown de xem Markdown ket qua.
```

## 5. Cau truc thu muc de xuat

Can bo sung cau truc sau:

```text
core/
  config/
    settings.py

infra/
  db/
    __init__.py
    base.py
    session.py
    models.py
    repositories/
      __init__.py
      documents.py
    migrations/
  storage/
    __init__.py
    r2_client.py

modules/
  ingestion/
    __init__.py
    service.py
    schemas.py
    pdf_processing/
      __init__.py
      gemini_pdf_converter.py
    markdown_processing/
      __init__.py
      normalizer.py
      ocr_cleanup.py
      math_normalizer.py

apps/
  api/
    v1/
      endpoints/
        documents.py
      models/
        documents.py
      services/
        documents.py

apps/
  frontend/
    src/
      services/
        apiClient.js
        ingestionApi.js
```

## 6. Bien moi truong

File `.env` can co cac bien:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/datn

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

R2_ENDPOINT_URL=https://your_account_id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_r2_access_key_id
R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
R2_BUCKET_NAME=datn-documents
R2_PUBLIC_BASE_URL=

MAX_UPLOAD_SIZE_MB=40
```

Yeu cau:

- Khong commit `.env` len GitHub.
- Backend chi doc bien moi truong tu `core/config/settings.py`.
- Frontend khong duoc truy cap truc tiep Gemini API key hoac R2 secret key.

## 7. Thiet ke settings

File:

```text
core/config/settings.py
```

Trach nhiem:

- Doc bien moi truong.
- Cung cap cau hinh cho database, Gemini, R2, upload limit.

Class de xuat:

```python
class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    r2_endpoint_url: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    r2_public_base_url: str | None = None
    max_upload_size_mb: int = 40
```

## 8. Thiet ke database PostgreSQL

### 8.1 Bang documents

Bang `documents` la bang trung tam cua buoc ingestion.

Muc dich:

- Luu metadata tai lieu.
- Luu trang thai xu ly.
- Luu key file goc tren R2.
- Luu Markdown da chuan hoa.

Schema de xuat:

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    content_type TEXT,
    source_type TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    r2_original_key TEXT,
    r2_original_url TEXT,
    markdown_content TEXT,
    markdown_checksum TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    processed_at TIMESTAMPTZ
);
```

Gia tri hop le:

```text
source_type:
  pdf
  markdown

status:
  uploaded
  processing
  completed
  failed
```

Index nen co:

```sql
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_source_type ON documents(source_type);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
```

Ghi chu:

- `filename`: ten file da sanitize de luu va hien thi.
- `original_filename`: ten file goc nguoi dung upload.
- `r2_original_key`: key object trong Cloudflare R2.
- `r2_original_url`: URL public neu bucket public, co the null.
- `markdown_content`: noi dung Markdown da chuan hoa.
- `markdown_checksum`: checksum de phat hien trung lap/noi dung thay doi.
- `error_message`: thong tin loi neu status = failed.

### 8.2 Bang document_processing_events

Nen co bang log su kien xu ly de debug ingestion.

Schema de xuat:

```sql
CREATE TABLE document_processing_events (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL
);
```

Gia tri `event_type` de xuat:

```text
upload_received
db_record_created
r2_upload_started
r2_upload_completed
gemini_conversion_started
gemini_conversion_completed
markdown_normalization_started
markdown_normalization_completed
document_completed
document_failed
```

Index nen co:

```sql
CREATE INDEX idx_document_processing_events_document_id
ON document_processing_events(document_id);

CREATE INDEX idx_document_processing_events_created_at
ON document_processing_events(created_at DESC);
```

Bang nay khong bat buoc cho MVP, nhung rat huu ich khi Gemini/R2 loi.

### 8.3 Bang document_assets

Neu sau nay PDF co anh, bang, hinh ve, nen tach asset rieng.

Schema de xuat:

```sql
CREATE TABLE document_assets (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    asset_type TEXT NOT NULL,
    r2_key TEXT NOT NULL,
    content_type TEXT,
    size_bytes BIGINT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL
);
```

Gia tri `asset_type`:

```text
original_pdf
image
table
markdown_backup
```

Bang nay co the lam sau. Trong MVP, chi can `documents.r2_original_key`.

## 9. Thiet ke SQLAlchemy models

File:

```text
infra/db/models.py
```

Model can co:

```text
Document
DocumentProcessingEvent
DocumentAsset
```

`Document` nen map voi bang `documents`.

Kieu du lieu Python de xuat:

```text
id: UUID
filename: str
original_filename: str
content_type: str | None
source_type: str
size_bytes: int
status: str
message: str
r2_original_key: str | None
r2_original_url: str | None
markdown_content: str | None
markdown_checksum: str | None
error_message: str | None
created_at: datetime
updated_at: datetime
processed_at: datetime | None
```

## 10. Repository layer

File:

```text
infra/db/repositories/documents.py
```

Trach nhiem:

- Lam viec truc tiep voi database.
- Khong xu ly Gemini.
- Khong xu ly Markdown.
- Khong nhan `UploadFile` tu FastAPI.

Ham de xuat:

```python
async def create_document(...)
async def get_document(document_id: UUID)
async def list_documents(...)
async def update_status(document_id: UUID, status: str, message: str)
async def attach_r2_original(document_id: UUID, key: str, url: str | None)
async def save_markdown(document_id: UUID, markdown: str, checksum: str)
async def mark_completed(document_id: UUID)
async def mark_failed(document_id: UUID, error_message: str)
```

## 11. Cloudflare R2 storage layer

File:

```text
infra/storage/r2_client.py
```

Trach nhiem:

- Khoi tao S3-compatible client bang `boto3`.
- Upload file goc len R2.
- Tao object key thong nhat.
- Neu co public base URL thi tao public URL.

Key format:

```text
documents/{document_id}/original/{filename}
documents/{document_id}/normalized/document.md
```

Ham de xuat:

```python
def build_original_key(document_id: str, filename: str) -> str
async def upload_bytes(key: str, content: bytes, content_type: str | None) -> None
def build_public_url(key: str) -> str | None
```

Luu y:

- R2 secret key chi nam trong backend.
- Neu tai lieu la private, `R2_PUBLIC_BASE_URL` co the de trong.
- Sau nay co the tao signed URL de tai file.

## 12. Ingestion module

Thu muc:

```text
modules/ingestion
```

### 12.1 `modules/ingestion/service.py`

Trach nhiem:

- Dieu phoi toan bo workflow ingestion.
- Goi R2 upload.
- Goi Gemini converter neu la PDF.
- Goi Markdown normalizer.
- Goi repository de cap nhat database.

Ham de xuat:

```python
async def process_document(document_id: UUID, filename: str, content_type: str | None, file_bytes: bytes) -> None
```

Pseudo-flow:

```text
update status processing
upload original file to R2
if pdf:
    markdown = convert_pdf_to_markdown(file_bytes)
else:
    markdown = decode_markdown(file_bytes)
normalized = normalize_markdown(markdown)
checksum = sha256(normalized)
save markdown to DB
mark completed
if error:
    mark failed
```

### 12.2 `modules/ingestion/pdf_processing/gemini_pdf_converter.py`

Trach nhiem:

- Nhan PDF bytes.
- Goi Gemini API.
- Tra ve Markdown text.

Prompt de xuat:

```text
Convert this PDF into clean Markdown.
Preserve headings, lists, tables, mathematical formulas.
Use LaTeX for math:
- inline math: $...$
- block math: $$...$$
Do not summarize. Do not omit content.
Return only Markdown.
```

Neu file lon, dung Gemini Files API.

### 12.3 `modules/ingestion/markdown_processing/normalizer.py`

Trach nhiem:

- Dieu phoi cac buoc chuan hoa Markdown.

Pipeline:

```text
normalize_newlines
remove_control_characters
fix_common_ocr_errors
normalize_math_delimiters
normalize_headings
collapse_excess_blank_lines
ensure_trailing_newline
```

### 12.4 `modules/ingestion/markdown_processing/ocr_cleanup.py`

Trach nhiem:

- Sua cac loi OCR pho bien.

Vi du:

```text
"d x" -> "dx"
"lim x -> 0" -> "\lim_{x \to 0}"
"∫" -> "\int"
"≤" -> "\le"
"≥" -> "\ge"
```

### 12.5 `modules/ingestion/markdown_processing/math_normalizer.py`

Trach nhiem:

- Chuan hoa delimiter cong thuc.

Quy tac:

```text
\( ... \) -> $...$
\[ ... \] -> $$...$$
```

Khong nen parse LaTeX qua sau o buoc nay. Muc tieu la lam Markdown on dinh cho segmentation.

## 13. API layer

### 13.1 File endpoint

File:

```text
apps/api/v1/endpoints/documents.py
```

Endpoint can co:

```text
POST /documents/upload
GET /documents
GET /documents/{document_id}
GET /documents/{document_id}/status
GET /documents/{document_id}/markdown
```

### 13.2 `POST /documents/upload`

Request:

```text
multipart/form-data
file: PDF | Markdown
```

Response:

```json
{
  "id": "uuid",
  "filename": "sample.pdf",
  "source_type": "pdf",
  "content_type": "application/pdf",
  "size_bytes": 123456,
  "status": "uploaded",
  "message": "Document uploaded and queued for processing",
  "markdown_available": false,
  "created_at": "...",
  "updated_at": "..."
}
```

Nen dung `BackgroundTasks` de xu ly sau khi tra response.

### 13.3 `GET /documents/{document_id}/status`

Response:

```json
{
  "id": "uuid",
  "status": "processing",
  "message": "Converting PDF to Markdown",
  "error_message": null,
  "updated_at": "..."
}
```

### 13.4 `GET /documents/{document_id}/markdown`

Response:

```json
{
  "id": "uuid",
  "markdown_content": "# Title\n\n...",
  "markdown_checksum": "sha256..."
}
```

Neu chua co Markdown:

```text
404 hoac 409
```

Khuyen nghi dung `409 Conflict` neu tai lieu ton tai nhung chua xu ly xong.

## 14. API models

File:

```text
apps/api/v1/models/documents.py
```

Model can co:

```text
DocumentStatus
DocumentSourceType
DocumentResponse
DocumentUploadResponse
DocumentStatusResponse
DocumentMarkdownResponse
DocumentListResponse
```

Truong `DocumentResponse` de xuat:

```text
id
filename
source_type
content_type
size_bytes
status
message
r2_original_key
r2_original_url
markdown_available
error_message
created_at
updated_at
processed_at
```

## 15. API service layer

File:

```text
apps/api/v1/services/documents.py
```

Trach nhiem:

- Validate upload file.
- Tao document record.
- Goi background ingestion.
- Lay document tu repository.
- Map database model sang API response.

Khong nen:

- Goi Gemini truc tiep.
- Tu upload R2 truc tiep neu logic da nam trong ingestion service.
- Luu `_documents` trong RAM.
- Ghi file local vao `data/uploads` cho production flow.

## 16. Frontend integration

### 16.1 File API client

Them:

```text
apps/frontend/src/services/apiClient.js
apps/frontend/src/services/ingestionApi.js
```

`apiClient.js`:

- Dinh nghia `API_BASE_URL`.
- Boc `fetch`.
- Xu ly JSON/error chung.

`ingestionApi.js`:

```text
uploadDocument(file)
listDocuments()
getDocument(documentId)
getDocumentStatus(documentId)
getDocumentMarkdown(documentId)
```

### 16.2 Sua UploadDocument.jsx

File:

```text
apps/frontend/src/pages/UploadDocument.jsx
```

Can thay:

```text
const DOCS = [...]
```

Bang state tu API:

```text
const [documents, setDocuments] = useState([])
const [uploading, setUploading] = useState(false)
const [error, setError] = useState(null)
```

Can them:

```text
input type="file" accept=".pdf,.md,.markdown"
onChange upload
onDrop upload
polling status khi document dang processing
```

UI hien tai dang ghi ho tro `DOCX`, `TEX`, `TXT`, `EPUB`. Can sua lai thanh:

```text
PDF, Markdown
```

Cho dung voi backend.

## 17. CORS

File:

```text
apps/api/main.py
```

Can them CORS cho frontend Vite:

```text
http://localhost:5173
```

Neu khong them CORS, browser se chan request frontend -> backend.

## 18. Xu ly loi

He thong can xu ly cac loi:

```text
filename rong
extension khong duoc ho tro
file qua lon
Markdown decode loi
Gemini API loi
Gemini tra ve noi dung rong
R2 upload loi
Database loi
Markdown normalizer loi
```

Khi loi:

- Cap nhat `documents.status = failed`.
- Luu `error_message`.
- Luu event `document_failed` neu co bang events.
- API status endpoint tra loi cho frontend hien thi.

## 19. Bao mat

Nguyen tac:

- Khong dua Gemini key len frontend.
- Khong dua R2 secret key len frontend.
- Khong public file upload mac dinh neu tai lieu co kha nang nhay cam.
- Validate extension va content type.
- Gioi han dung luong upload.
- Sanitize filename de tranh path traversal.
- Khong dung filename nguoi dung lam duong dan truc tiep.

## 20. Test

Test hien co:

```text
tests/api/test_documents.py
```

Can bo sung:

```text
tests/modules/ingestion/test_markdown_normalizer.py
tests/modules/ingestion/test_ocr_cleanup.py
tests/modules/ingestion/test_math_normalizer.py
tests/api/test_documents_ingestion.py
tests/infra/test_r2_client.py
tests/infra/test_document_repository.py
```

Case can test:

```text
upload .txt bi reject
upload filename rong bi reject
upload file qua lon bi reject
upload markdown tao document va markdown_content
upload PDF goi Gemini converter
Gemini loi thi status failed
R2 loi thi status failed
Markdown \(x^2\) duoc chuyen thanh $x^2$
Markdown \[x^2\] duoc chuyen thanh $$x^2$$
GET /documents/{id}/markdown tra 409 khi chua completed
```

Trong test khong nen goi Gemini/R2 that. Can mock converter va storage.

## 21. Thu tu trien khai khuyen nghi

1. Sua `core/config/settings.py`.
2. Them dependency trong `requirements.txt`.
3. Tao `infra/db/session.py`, `infra/db/base.py`, `infra/db/models.py`.
4. Tao migration cho bang `documents`.
5. Tao repository `infra/db/repositories/documents.py`.
6. Tao R2 client `infra/storage/r2_client.py`.
7. Tao Markdown normalizer trong `modules/ingestion/markdown_processing`.
8. Tao Gemini PDF converter trong `modules/ingestion/pdf_processing`.
9. Tao ingestion service trong `modules/ingestion/service.py`.
10. Sua `apps/api/v1/models/documents.py`.
11. Sua `apps/api/v1/services/documents.py`.
12. Sua `apps/api/v1/endpoints/documents.py`.
13. Them CORS trong `apps/api/main.py`.
14. Sua frontend `UploadDocument.jsx` va them API client.
15. Viet test unit cho normalizer.
16. Viet test API voi mock ingestion.
17. Chay test va kiem tra Swagger UI.

## 22. Tieu chi hoan thanh

Buoc 4 duoc xem la hoan thanh khi:

- Upload duoc PDF va Markdown tu frontend hoac Swagger UI.
- File goc duoc luu vao Cloudflare R2.
- Metadata document duoc luu vao PostgreSQL.
- PDF duoc Gemini chuyen thanh Markdown.
- Markdown dau vao duoc doc truc tiep va chuan hoa.
- Markdown da chuan hoa duoc luu trong PostgreSQL.
- API status tra dung `uploaded`, `processing`, `completed`, `failed`.
- Frontend hien thi dung danh sach file va trang thai xu ly.
- Co test cho upload, normalizer, loi Gemini/R2.

## 23. Dinh huong mo rong sau buoc 4

Sau khi ingestion on dinh, cac buoc tiep theo co the dung bang `documents.markdown_content` lam dau vao:

- Segmentation: tach cau hoi, loi giai, dap an.
- Classification: gan taxonomy, dang bai, do kho.
- Embedding: tao vector cho cau hoi va loi giai.
- Search: tim kiem semantic/formula.
- Generation: sinh bien the cau hoi.
- QA: kiem tra trung lap, loi cong thuc, chat luong cau hoi.

Vi vay, thiet ke database can dam bao Markdown sach, co checksum, co status ro rang va co kha nang truy vet loi.
