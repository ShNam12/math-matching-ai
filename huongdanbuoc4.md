# Huong Dan Buoc 4: Xu Ly Tai Lieu Dau Vao

## 1. Hien trang du an

Sau khi doc cau truc du an, hien trang dang la:

- Backend FastAPI da co API document co ban tai `apps/api/v1/endpoints/documents.py`.
- Logic upload hien nam tai `apps/api/v1/services/documents.py`.
- Model response hien nam tai `apps/api/v1/models/documents.py`.
- Frontend upload hien la UI mock, dung du lieu gia `DOCS` trong `apps/frontend/src/pages/UploadDocument.jsx`.
- `modules/ingestion` da ton tai nhung dang trong, day la noi hop ly nhat de dat logic PDF/Markdown.
- `infra` hien trong, nen phan PostgreSQL, Cloudflare R2, migration, storage client nen duoc bo sung tai day.
- `core/config/settings.py` hien chi co ten bien tho, chua phai Python hop le. File nay can duoc thiet ke lai truoc khi dung config that.

Nguon tham chieu API hien hanh:

- Google khuyen nghi dung `google-genai` SDK cho Gemini API.
- Gemini Files API phu hop khi xu ly file lon hon khoang 20 MB.
- Cloudflare R2 tuong thich S3 API va co the dung `boto3` voi `endpoint_url` rieng.

Tai lieu tham khao:

- Google Gemini libraries: https://ai.google.dev/gemini-api/docs/libraries
- Google Gemini Files API: https://ai.google.dev/gemini-api/docs/files
- Cloudflare R2 S3 API: https://developers.cloudflare.com/r2/get-started/s3/

## 2. Luong xu ly dung nen trien khai

Luong tong the nen la:

```text
Frontend Upload
 -> POST /documents/upload
 -> Backend nhan file
 -> Luu file goc len Cloudflare R2
 -> Tao ban ghi documents trong PostgreSQL
 -> Neu PDF: Gemini chuyen PDF sang Markdown
 -> Neu Markdown: doc truc tiep
 -> Chuan hoa Markdown
 -> Luu markdown vao PostgreSQL
 -> Cap nhat status completed / failed
 -> Frontend polling /documents/{id}/status
```

## 3. Sua cau hinh truoc

File can sua:

```text
core/config/settings.py
```

Hien file nay chua hop le vi chi chua cac dong nhu:

```python
DATABASE_URL
GEMINI_API_KEY
GEMINI_MODEL
R2_ENDPOINT_URL
R2_ACCESS_KEY_ID
R2_SECRET_ACCESS_KEY
R2_BUCKET_NAME
R2_PUBLIC_BASE_URL
```

Nen bien file nay thanh module cau hinh dung `pydantic-settings`.

Can them dependency vao:

```text
requirements.txt
```

De xuat them:

```text
pydantic-settings
google-genai
boto3
sqlalchemy
asyncpg
alembic
python-dotenv
```

Nhung bien cau hinh can co:

```text
DATABASE_URL
GEMINI_API_KEY
GEMINI_MODEL
R2_ENDPOINT_URL
R2_ACCESS_KEY_ID
R2_SECRET_ACCESS_KEY
R2_BUCKET_NAME
R2_PUBLIC_BASE_URL
MAX_UPLOAD_SIZE_MB
```

Tat ca module Gemini, R2, PostgreSQL nen import config tu `core.config.settings`.

## 4. Thiet ke database PostgreSQL

Nen them cau truc:

```text
infra/db/
  __init__.py
  session.py
  base.py
  models.py
  migrations/
```

Bang quan trong nhat la `documents`.

Cot nen co:

```text
id UUID primary key
filename text
content_type text
size_bytes bigint
source_type text
status text
r2_original_key text
r2_original_url text nullable
markdown_content text nullable
markdown_checksum text nullable
error_message text nullable
created_at timestamp
updated_at timestamp
processed_at timestamp nullable
```

Trong do:

```text
source_type: pdf | markdown
status: uploaded | processing | completed | failed
```

Ly do: hien `DocumentService` dang luu metadata trong RAM bang `_documents`, nen khi restart server se mat du lieu. Buoc 4 yeu cau luu Markdown vao PostgreSQL, vi vay can chuyen `_documents` sang repository/database.

Nen them file:

```text
infra/db/repositories/
  documents.py
```

Repository nay chiu trach nhiem:

```text
create_document(...)
get_document(document_id)
update_status(...)
save_markdown(...)
mark_failed(...)
```

## 5. Thiet ke Cloudflare R2 storage

Nen them:

```text
infra/storage/
  __init__.py
  r2_client.py
```

`r2_client.py` dung `boto3.client("s3", endpoint_url=...)`.

Key luu file nen thong nhat:

```text
documents/{document_id}/original/{filename}
documents/{document_id}/normalized/document.md
```

Voi yeu cau hien tai, toi thieu can luu file goc len R2. Markdown luu PostgreSQL la chinh. Co the backup Markdown len R2 neu muon, nhung khong nen thay the PostgreSQL vi cac buoc sau can query noi dung Markdown de segmentation.

## 6. Tao module ingestion dung vi tri

Nen bo sung duoi `modules/ingestion`:

```text
modules/ingestion/
  __init__.py
  service.py
  schemas.py
  pdf_processing/
    __init__.py
    gemini_pdf_converter.py
  markdown_processing/
    __init__.py
    normalizer.py
    math_normalizer.py
    ocr_cleanup.py
```

Vai tro tung file:

- `service.py`: orchestration chinh cho ingestion.
- `gemini_pdf_converter.py`: goi Gemini de chuyen PDF sang Markdown.
- `normalizer.py`: pipeline chuan hoa Markdown.
- `ocr_cleanup.py`: sua loi OCR pho bien.
- `math_normalizer.py`: chuan hoa cong thuc toan hoc.
- `schemas.py`: dataclass/Pydantic noi bo nhu `IngestionResult`.

Luong trong `service.py` nen la:

```text
ingest_document(document_id, filename, content_type, file_bytes)
 -> upload original to R2
 -> if PDF: convert_pdf_to_markdown(...)
 -> if Markdown: decode bytes
 -> normalize_markdown(...)
 -> save markdown_content to PostgreSQL
 -> update status completed
```

## 7. Tich hop Gemini PDF sang Markdown

File can them:

```text
modules/ingestion/pdf_processing/gemini_pdf_converter.py
```

Nen dung `google-genai`, khong dung thu vien Gemini legacy.

Prompt nen ro rang:

```text
Convert this PDF into clean Markdown.
Preserve headings, lists, tables, mathematical formulas.
Use LaTeX for math:
- inline math: $...$
- block math: $$...$$
Do not summarize. Do not omit content.
Return only Markdown.
```

Voi PDF lon, nen dung Gemini Files API: upload file len Gemini roi goi `generate_content` voi file do. Theo Google docs, Files API la huong phu hop khi tong request lon hon 20 MB.

Nen gioi han file o backend. Hien frontend mock ghi "40 MB", nhung backend chua kiem tra size. Nen them:

```text
MAX_UPLOAD_SIZE_MB=40
```

## 8. Chuan hoa Markdown

File can them:

```text
modules/ingestion/markdown_processing/normalizer.py
```

Pipeline nen chia thanh cac buoc nho:

```text
normalize_newlines
remove_control_characters
fix_common_ocr_errors
normalize_math_delimiters
normalize_headings
collapse_excess_blank_lines
ensure_trailing_newline
```

File OCR:

```text
modules/ingestion/markdown_processing/ocr_cleanup.py
```

Nhung loi nen xu ly truoc:

```text
"l" nham "1" trong ngu canh so hoc
"O" nham "0" trong cong thuc
"d x" -> "dx"
"∫ ... d x" -> "\int ... dx"
"lim x -> 0" -> "\lim_{x \to 0}"
```

File toan:

```text
modules/ingestion/markdown_processing/math_normalizer.py
```

Nen chuan hoa:

```text
\( ... \) -> $...$
\[ ... \] -> $$...$$
\displaystyle giu nguyen trong block math neu can
multiple spaces trong formula
```

Khong nen co parse toan bo LaTeX o buoc nay. Buoc 4 chi can Markdown sach de buoc segmentation dung tiep.

## 9. Sua service hien tai

File can sua:

```text
apps/api/v1/services/documents.py
```

Hien logic upload dang:

- Doc file.
- Tao folder local `data/uploads`.
- Ghi file bang `write_bytes`.
- Luu metadata vao dict `_documents`.

Nen thay thanh:

```text
validate filename
validate extension
validate size
create DB row status=uploaded
call ingestion service
return DocumentResponse
```

Co hai cach trien khai:

### Cach don gian cho MVP

Xu ly dong bo ngay trong request:

```text
POST /documents/upload cho den khi convert xong
```

### Cach tot hon

Tra response som, xu ly async/background:

```text
POST /documents/upload
 -> status uploaded/processing
 -> BackgroundTasks chay ingestion
 -> frontend goi /documents/{id}/status
```

Voi du an hien tai, nen dung `BackgroundTasks` truoc, chua can Celery/RQ vi `apps/worker` chua ton tai thuc te.

## 10. Sua endpoint upload

File can sua:

```text
apps/api/v1/endpoints/documents.py
```

Them `BackgroundTasks` vao endpoint:

```python
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile)
```

Sau do service tao document truoc, roi enqueue ingestion.

Nen giu endpoint hien tai:

```text
POST /documents/upload
GET /documents/{document_id}
GET /documents/{document_id}/status
```

Nen bo sung endpoint:

```text
GET /documents
GET /documents/{document_id}/markdown
```

`GET /documents/{id}/markdown` rat can de kiem tra ket qua Gemini va chuan hoa Markdown truoc khi qua buoc segmentation.

## 11. Mo rong Pydantic models

File can sua:

```text
apps/api/v1/models/documents.py
```

`DocumentResponse` nen them:

```text
source_type
r2_original_key
markdown_available
error_message
updated_at
processed_at
```

Nen them model:

```text
DocumentMarkdownResponse:
  id
  markdown_content
  markdown_checksum
```

Status hien co on:

```python
uploaded
processing
completed
failed
```

Nhung nen dung status nhu sau:

```text
uploaded     vua tao record
processing   dang upload R2 / Gemini / normalize
completed    da co markdown_content
failed       loi R2, Gemini, DB hoac normalize
```

## 12. Ket noi frontend

File hien tai:

```text
apps/frontend/src/pages/UploadDocument.jsx
```

Hien `DOCS` la mock. Khi backend xong, nen tach API client ra thay vi goi `fetch` truc tiep trong component.

Them:

```text
apps/frontend/src/services/
  apiClient.js
  ingestionApi.js
```

`ingestionApi.js` nen co:

```text
uploadDocument(file)
getDocument(id)
getDocumentStatus(id)
listDocuments()
getDocumentMarkdown(id)
```

Trong `UploadDocument.jsx` can thay:

```text
const DOCS = [...]
```

Bang state:

```text
const [documents, setDocuments] = useState([])
const [uploading, setUploading] = useState(false)
```

Vung upload zone can them:

```text
input type="file" accept=".pdf,.md,.markdown"
onChange -> uploadDocument(file)
onDrop -> uploadDocument(droppedFile)
```

Quan trong: UI hien ghi ho tro `DOCX`, `TEX`, `TXT`, `EPUB`, nhung backend hien chi ho tro `.pdf`, `.md`, `.markdown`. Nen sua text frontend chi con:

```text
PDF, Markdown
```

De tranh sai logic.

## 13. CORS cho frontend

File can sua:

```text
apps/api/main.py
```

Them `CORSMiddleware` cho Vite dev server:

```text
http://localhost:5173
```

Neu khong, frontend goi backend se bi browser chan.

## 14. Test can them

Hien test chi kiem tra upload mock tai:

```text
tests/api/test_documents.py
```

Nen bo sung:

```text
tests/modules/ingestion/test_markdown_normalizer.py
tests/modules/ingestion/test_ocr_cleanup.py
tests/modules/ingestion/test_math_normalizer.py
tests/api/test_documents_ingestion.py
```

Test nen mock Gemini va R2, khong goi API that.

Case can co:

```text
upload .txt bi reject
upload file qua lon bi reject
upload markdown luu duoc markdown_content
upload pdf goi converter
converter loi -> status failed
markdown math \(x^2\) -> $x^2$
block math \[...\] -> $$...$$
```

## 15. Thu tu lam khuyen nghi

1. Sua `core/config/settings.py`.
2. Them DB session, model, repository trong `infra/db`.
3. Them R2 client trong `infra/storage`.
4. Them ingestion module trong `modules/ingestion`.
5. Sua `DocumentService` de dung DB + R2 + ingestion thay vi RAM/local file.
6. Sua endpoint de chay background task.
7. Them endpoint lay Markdown.
8. Sua frontend upload de goi API that.
9. Them test cho normalizer, API, trang thai loi.
10. Sau khi on moi chuyen sang worker queue rieng.

## 16. Luu y kien truc

Khong nen de `apps/api/v1/services/documents.py` chua toan bo logic Gemini, R2, Markdown.

File do chi nen dieu phoi API-level. Logic nghiep vu nen nam trong:

```text
modules/ingestion
```

Ha tang nen nam trong:

```text
infra
```

Cach nay giu dung thiet ke he thong va giup cac buoc sau nhu segmentation, embedding, search dung lai Markdown de dang.
