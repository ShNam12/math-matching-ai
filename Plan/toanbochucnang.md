# Toan bo chuc nang hien co va trang thai ket noi frontend

Ngay kiem tra: 2026-06-10

Tai lieu nay tong hop cac chuc nang dang co trong du an, chia theo 3 nhom:

- Chuc nang da co API backend va da duoc frontend goi.
- Chuc nang da co API backend nhung frontend chua goi.
- Chuc nang da co o tang service/script backend nhung chua co API endpoint rieng.

## 1. Tong quan nhanh

| Nhom chuc nang | Backend | Frontend |
| --- | --- | --- |
| Upload/list document | Da co API | Da ket noi mot phan |
| Xem chi tiet document | Da co API | Da co ham service, chua thay UI dung ro |
| Xem status document | Da co API | Da co ham service, UI chu yeu polling bang list documents |
| Xem markdown document | Da co API | Da co ham service, chua thay UI dung ro |
| Health/readiness | Da co API | Chua ket noi |
| Semantic search cau hoi | Da co API | Chua ket noi, UI dang dung mock data |
| Formula search | Da co API | Chua ket noi |
| Sinh bien the cau hoi | Da co API | Chua ket noi, UI dang dung mock data |
| Kiem dinh chat luong cau hoi sinh | Da co API | Chua ket noi, UI QA dang mock data |
| Luu cau hoi sinh | Da co API | Chua ket noi |
| Tach cau hoi tu markdown | Da co service | Chua co API rieng, chua ket noi frontend |
| Embedding document/cau hoi/cong thuc | Da co service | Chua co API rieng, chua ket noi frontend |
| Store document: tach cau hoi + embedding | Da co service/script | Chua co API rieng, chua ket noi frontend |
| Dashboard/Analytics/Settings | UI da co | Chu yeu mock/static, chua goi backend |

Ket luan ngan gon: frontend hien moi ket noi chac chan voi phan upload va danh sach document. Phan lon cac man con lai dang la UI/mock data hoac co ham service nhung chua duoc su dung ro trong UI.

## 2. Chuc nang backend da co API

### 2.1. Health va readiness

| Chuc nang | Endpoint | File backend | Trang thai frontend |
| --- | --- | --- | --- |
| Kiem tra API dang chay | `GET /` | `apps/api/main.py` | Chua ket noi |
| Health check co ban | `GET /health` | `apps/api/main.py` | Chua ket noi |
| Readiness check PostgreSQL va Qdrant | `GET /ready` | `apps/api/main.py` | Chua ket noi |

Ghi chu:

- Dashboard hien co mock data `HEALTH` trong `apps/frontend/src/pages/Dashboard.jsx`.
- Chua co frontend service goi `/health` hoac `/ready`.

### 2.2. Quan ly document

| Chuc nang | Endpoint | File backend | File frontend | Trang thai frontend |
| --- | --- | --- | --- | --- |
| Upload PDF/Markdown | `POST /documents/upload` | `apps/api/v1/endpoints/documents.py` | `apps/frontend/src/services/ingestionApi.js`, `apps/frontend/src/pages/UploadDocument.jsx` | Da ket noi |
| Lay danh sach document | `GET /documents` | `apps/api/v1/endpoints/documents.py` | `apps/frontend/src/services/ingestionApi.js`, `apps/frontend/src/pages/UploadDocument.jsx` | Da ket noi |
| Lay chi tiet mot document | `GET /documents/{document_id}` | `apps/api/v1/endpoints/documents.py` | `apps/frontend/src/services/ingestionApi.js` | Da co ham service, chua thay UI dung ro |
| Lay status document | `GET /documents/{document_id}/status` | `apps/api/v1/endpoints/documents.py` | `apps/frontend/src/services/ingestionApi.js` | Da co ham service, chua thay UI dung ro |
| Lay markdown da xu ly | `GET /documents/{document_id}/markdown` | `apps/api/v1/endpoints/documents.py` | `apps/frontend/src/services/ingestionApi.js` | Da co ham service, chua thay UI dung ro |

Chi tiet backend da ho tro:

- Chi nhan file `.pdf`, `.md`, `.markdown`.
- Kiem tra filename rong.
- Kiem tra file rong.
- Gioi han kich thuoc file theo `MAX_UPLOAD_SIZE_MB`, mac dinh 40 MB.
- Tao document record trong PostgreSQL.
- Chay background ingestion sau khi upload.
- Tra status: `uploaded`, `processing`, `completed`, `failed`.
- Luu va tra markdown sau xu ly neu co.

Chi tiet frontend da ho tro:

- Chon file tu may.
- Keo tha file.
- Upload file.
- Load danh sach document.
- Polling danh sach khi co document dang `uploaded` hoac `processing`.
- Loc document theo `all`, `completed`, `processing`, `failed`.
- Hien thi kich thuoc file, ngay tao, status, loi neu co.

Chua ket noi ro tren UI:

- Nut xem document/markdown.
- Nut xoa document. Backend cung chua co endpoint delete.
- Goi rieng status endpoint cho tung document.
- Goi endpoint lay markdown de hien thi noi dung da convert.

### 2.3. Semantic search

| Chuc nang | Endpoint | File backend | Trang thai frontend |
| --- | --- | --- | --- |
| Tim cau hoi theo ngu nghia | `POST /search/questions` | `apps/api/v1/endpoints/search.py` | Chua ket noi |
| Tim cong thuc LaTeX | `POST /search/formulas` | `apps/api/v1/endpoints/search.py` | Chua ket noi |

Backend da ho tro tim cau hoi:

- Input `query`.
- Gioi han `limit` tu 1 den 50.
- Filter theo `subject`, `chapter`, `difficulty`.
- Tao embedding query bang Gemini.
- Query Qdrant collection cau hoi.
- Lay lai noi dung cau hoi tu PostgreSQL.
- Chi tra cau hoi co `embedding_status = completed`.

Backend da ho tro tim cong thuc:

- Input `latex`.
- Gioi han `limit` tu 1 den 50.
- Filter theo `source`.
- Normalize cong thuc.
- Tao embedding cho cong thuc.
- Query Qdrant collection cong thuc.
- Lay lai noi dung cau hoi tu PostgreSQL.

Frontend hien tai:

- `apps/frontend/src/pages/SemanticSearch.jsx` co UI tim kiem, bo loc, danh sach ket qua.
- Nhung du lieu dang lay tu const `PROBLEMS`, khong goi API.
- Chua co file service rieng cho search API.

### 2.4. Sinh bien the cau hoi

| Chuc nang | Endpoint | File backend | Trang thai frontend |
| --- | --- | --- | --- |
| Preview cau hoi sinh bang Gemini | `POST /generation/questions/preview` | `apps/api/v1/endpoints/generation.py` | Chua ket noi |
| Kiem dinh chat luong candidate | `POST /generation/questions/quality` | `apps/api/v1/endpoints/generation.py` | Chua ket noi |
| Luu cau hoi sinh | `POST /generation/questions/save` | `apps/api/v1/endpoints/generation.py` | Chua ket noi |

Backend preview generation da ho tro:

- Lay source question theo `source_question_id`.
- Nhan `generation_count` tu 1 den 10.
- Nhan constraints:
  - `subject`
  - `chapter`
  - `difficulty`
  - `skills`
  - `preserve_formula_style`
  - `avoid_duplicate`
- Build prompt.
- Goi Gemini sinh JSON.
- Parse candidate.
- Extract formula tu statement/solution/answer.
- Chay quality assessment va gan warnings.

Backend quality check da ho tro:

- Kiem tra source question ton tai.
- Kiem tra candidate voi danh sach cau hoi trong cung document.
- Kiem tra duplicate chinh xac.
- Kiem tra semantic duplicate neu co semantic search service.
- Kiem tra formula payload.
- Canh bao thieu formula.
- Canh bao formula payload khong khop cong thuc extract duoc.
- Kiem tra difficulty.
- Canh bao thieu solution/answer.
- Tra `can_save`, `warnings`, `blocking_issues`, `semantic_duplicates`.

Backend save generated question da ho tro:

- Kiem tra source question.
- Kiem tra quality truoc khi luu.
- Tao question moi voi marker `Generated`.
- Gan sequence number tiep theo trong document.
- Luu PostgreSQL.
- Embed lai document sau khi luu.
- Tra thong tin question moi va `embedding_status`.

Frontend hien tai:

- `apps/frontend/src/pages/GenVariants.jsx` co UI sinh bien the nhung dung mock data `VARIANTS_DATA`.
- `apps/frontend/src/pages/QARules.jsx` co UI rule/quality nhung dung mock data `RULES`.
- Chua co service frontend cho `/generation`.

## 3. Chuc nang backend co service/script nhung chua co API endpoint rieng

### 3.1. Ingestion document

| Chuc nang | File backend | Trang thai API | Trang thai frontend |
| --- | --- | --- | --- |
| Upload file goc len R2 | `infra/storage/r2_client.py` | Duoc dung trong background upload | Gian tiep qua upload document |
| Convert PDF sang Markdown bang Gemini | `modules/ingestion/pdf_processing/gemini_pdf_converter.py` | Duoc dung trong background upload | Gian tiep qua upload document |
| Normalize Markdown | `modules/ingestion/markdown_processing/normalizer.py` | Duoc dung trong background upload | Gian tiep qua upload document |
| Fix OCR loi pho bien | `modules/ingestion/markdown_processing/ocr_cleanup.py` | Duoc dung trong normalize | Gian tiep qua upload document |
| Normalize math delimiter | `modules/ingestion/markdown_processing/math_normalizer.py` | Duoc dung trong normalize | Gian tiep qua upload document |

Ghi chu:

- Nhom nay da duoc kich hoat gian tiep sau khi upload document.
- Frontend khong goi truc tiep tung buoc.

### 3.2. Tach cau hoi va catalog

| Chuc nang | File backend | Trang thai API | Trang thai frontend |
| --- | --- | --- | --- |
| Tach cau hoi tu Markdown | `modules/question_segmenter/segmenter.py` | Chua co endpoint rieng | Chua ket noi |
| Nhan dien marker cau hoi | `modules/question_segmenter/patterns.py` | Chua co endpoint rieng | Chua ket noi |
| Tach statement/solution/answer | `modules/question_segmenter/segmenter.py` | Chua co endpoint rieng | Chua ket noi |
| Extract formula LaTeX | `modules/question_segmenter/formula_extractor.py` | Chua co endpoint rieng | Chua ket noi |
| Replace questions theo document | `infra/db/repositories/questions.py` | Chua co endpoint rieng | Chua ket noi |
| Segment document da completed | `modules/question_catalog/service.py` | Chua co endpoint rieng | Chua ket noi |

Ghi chu:

- Co test cho question segmenter va question catalog.
- Chua thay API kieu `POST /documents/{id}/segment` hoac `POST /questions/segment`.

### 3.3. Embedding va luu vector

| Chuc nang | File backend | Trang thai API | Trang thai frontend |
| --- | --- | --- | --- |
| Tao embedding bang Gemini | `modules/embeddings/gemini_embedder.py` | Duoc dung trong search/generation save/script | Chua ket noi truc tiep |
| Build text embedding cho cau hoi | `modules/embeddings/text_builder.py` | Service noi bo | Chua ket noi |
| Build text embedding cho cong thuc | `modules/embeddings/text_builder.py` | Service noi bo | Chua ket noi |
| Embed tat ca cau hoi trong document | `modules/embeddings/service.py` | Chua co endpoint rieng | Chua ket noi |
| Tao Qdrant collections neu chua co | `infra/vector_db/repositories/embeddings.py` | Service noi bo | Chua ket noi truc tiep |
| Replace vector theo document | `infra/vector_db/repositories/embeddings.py` | Service noi bo | Chua ket noi truc tiep |
| Dem vector theo document | `infra/vector_db/repositories/embeddings.py` | Service noi bo/script | Chua ket noi |

Ghi chu:

- Search API va generation save co su dung embedding.
- Chua co endpoint rieng de nguoi dung bam "Embed document".

### 3.4. Store document full flow

| Chuc nang | File backend | Trang thai API | Trang thai frontend |
| --- | --- | --- | --- |
| Store document: segment + embed | `modules/question_storage/service.py` | Chua co endpoint rieng | Chua ket noi |
| Script sync question storage | `scripts/sync_question_storage.py` | Script noi bo | Chua ket noi |

Ghi chu:

- Day la luong rat quan trong: document da completed -> tach question -> embed -> san sang search.
- Hien chua co API public cho frontend kich hoat.

## 4. Chuc nang frontend hien co theo page

### 4.1. `UploadDocument.jsx`

Trang thai: da ket noi mot phan voi backend.

Da co:

- Sidebar navigation.
- Upload zone.
- Chon file.
- Drag and drop.
- Goi `uploadDocument(file)`.
- Goi `listDocuments()`.
- Loc document theo status.
- Polling khi co document dang xu ly.
- Hien thi tong so file, tong dung luong, dang xu ly, loi.

Chua co/Chua ket noi ro:

- Xem chi tiet document bang endpoint `GET /documents/{id}`.
- Xem markdown bang endpoint `GET /documents/{id}/markdown`.
- Xoa document. Backend chua co endpoint delete.
- Retry failed ingestion. Backend chua co endpoint retry.
- Trigger store/segment/embed sau khi document completed. Backend chua co endpoint.

### 4.2. `SemanticSearch.jsx`

Trang thai: UI mock, chua ket noi backend.

Da co UI:

- Search box.
- Filter chuyen de, do kho, ky nang.
- Danh sach ket qua.
- Match score.
- Expand/collapse statement.
- Star/unstar local state.
- Nut xem loi giai, bai tuong tu, sinh bien the.

Chua ket noi:

- `POST /search/questions`.
- `POST /search/formulas`.
- Dieu huong sang detail that cua question.
- Nut sinh bien the dua theo question id that.

### 4.3. `GenVariants.jsx`

Trang thai: UI mock, chua ket noi backend.

Da co UI:

- Danh sach bien the cau hoi.
- Trang thai kiem dinh/diem chat luong theo mock.
- Mot so hanh dong UI.

Chua ket noi:

- `POST /generation/questions/preview`.
- `POST /generation/questions/quality`.
- `POST /generation/questions/save`.

### 4.4. `QARules.jsx`

Trang thai: UI mock, chua ket noi backend.

Da co UI:

- Danh sach rules.
- Trang thai rule.
- Badge/canh bao theo mock.

Chua ket noi:

- Quality check API `POST /generation/questions/quality`.
- Du lieu rule thuc te tu backend. Hien backend chua co endpoint list/config rules.

### 4.5. `ProblemDetail.jsx`

Trang thai: UI mock, chua ket noi backend.

Da co UI:

- Hien chi tiet bai tap theo mock.
- Hien cac buoc giai.
- Hien bai tuong tu.

Chua ket noi:

- Lay question that theo id. Backend hien co repository `get_question`, nhung chua co endpoint public `GET /questions/{id}`.
- Lay similar questions that qua `/search/questions`.
- Nut sinh bien the theo question id that.

### 4.6. `Dashboard.jsx`

Trang thai: UI mock/static, chua ket noi backend.

Da co UI:

- Health cards.
- Recent problems.
- Activities.
- Topics.
- Quick actions.
- Recent queries.

Chua ket noi:

- `GET /health`.
- `GET /ready`.
- Thong ke document/question/search thật. Backend chua co analytics endpoint rieng.
- Recent questions/documents thật.

### 4.7. `Analytics.jsx`

Trang thai: UI mock/static, chua ket noi backend.

Da co UI:

- Stats.
- Query trend.
- Topic data.
- Difficulty data.
- Logs.

Chua ket noi:

- Backend chua co endpoint analytics.
- Chua co service frontend cho analytics.

### 4.8. `CalculusTaxonomy.jsx`

Trang thai: UI mock/static, chua ket noi backend.

Da co UI:

- Danh sach chuong/chuyen de calculus.
- Hien thi cau truc phan loai theo mock.

Chua ket noi:

- Backend chua co endpoint taxonomy.
- Chua co update subject/chapter/difficulty/skills cho question.

### 4.9. `Settings.jsx`

Trang thai: UI mock/static, chua ket noi backend.

Da co UI:

- Tabs settings.
- Toggle.
- Users mock.

Chua ket noi:

- Backend chua co endpoint settings/users.
- Chua goi health/readiness/config thật.

## 5. Bang endpoint backend va trang thai ket noi frontend

| Endpoint | Chuc nang | Trang thai frontend |
| --- | --- | --- |
| `GET /` | Root message | Chua ket noi |
| `GET /health` | Health check | Chua ket noi |
| `GET /ready` | Check database + Qdrant | Chua ket noi |
| `POST /documents/upload` | Upload PDF/Markdown | Da ket noi |
| `GET /documents` | List documents | Da ket noi |
| `GET /documents/{document_id}` | Get document detail | Co ham service, chua thay UI dung ro |
| `GET /documents/{document_id}/status` | Get document status | Co ham service, chua thay UI dung ro |
| `GET /documents/{document_id}/markdown` | Get processed markdown | Co ham service, chua thay UI dung ro |
| `POST /search/questions` | Semantic question search | Chua ket noi |
| `POST /search/formulas` | Formula vector search | Chua ket noi |
| `POST /generation/questions/preview` | Generate variants preview | Chua ket noi |
| `POST /generation/questions/quality` | Assess generated question quality | Chua ket noi |
| `POST /generation/questions/save` | Save generated question | Chua ket noi |

## 6. Cac chuc nang nen noi frontend tiep theo

Thu tu de xuat:

1. Noi `SemanticSearch.jsx` voi `POST /search/questions`.
2. Them service frontend `searchApi.js`.
3. Noi tim cong thuc voi `POST /search/formulas`.
4. Them endpoint backend cho question detail: `GET /questions/{question_id}`.
5. Noi `ProblemDetail.jsx` voi question detail that.
6. Noi `GenVariants.jsx` voi `POST /generation/questions/preview`.
7. Noi quality check va save generated question.
8. Them endpoint store document: `POST /documents/{document_id}/store` de chay segment + embed.
9. Them UI cho document completed: nut "Tach cau hoi va tao embedding".
10. Noi Dashboard voi `/ready`, `/documents`, va cac thong ke that.

## 7. Cac khoang trong backend nen bo sung API

Backend co service nhung nen them endpoint neu muon frontend dieu khien:

| Endpoint de xuat | Muc dich |
| --- | --- |
| `POST /documents/{document_id}/segment` | Tach cau hoi tu markdown da xu ly |
| `POST /documents/{document_id}/embed` | Tao embedding cho tat ca cau hoi/cong thuc trong document |
| `POST /documents/{document_id}/store` | Chay tron luong segment + embed |
| `GET /documents/{document_id}/questions` | Lay danh sach cau hoi cua document |
| `GET /questions/{question_id}` | Lay chi tiet mot cau hoi |
| `PATCH /questions/{question_id}` | Cap nhat subject/chapter/difficulty/skills |
| `DELETE /documents/{document_id}` | Xoa document va related questions/vectors |
| `POST /documents/{document_id}/retry` | Chay lai ingestion khi failed |
| `GET /analytics/summary` | Thong ke dashboard |

## 8. Ket luan

Du an da co loi backend kha day du cho workflow AI Matching:

- Upload tai lieu.
- Chuyen PDF sang Markdown.
- Chuan hoa noi dung.
- Tach cau hoi va cong thuc.
- Luu PostgreSQL.
- Tao embedding.
- Luu Qdrant.
- Tim kiem ngu nghia.
- Tim cong thuc.
- Sinh bien the cau hoi.
- Kiem dinh va luu cau hoi sinh.

Tuy nhien frontend hien chi moi noi chac chan phan upload/list document. Cac man con lai phan lon la mock UI. Ngoai ra, mot so service backend quan trong nhu segment/embed/store document chua co endpoint API rieng, nen frontend chua the goi truc tiep neu khong bo sung route.
