# Ke hoach ket noi day du cac chuc nang con thieu vao frontend

Ngay lap ke hoach: 2026-06-10

Muc tieu: dua frontend tu trang thai phan lon la UI/mock data sang ung dung co the thao tac that voi backend cho toan bo workflow:

Upload document -> xu ly document -> tach cau hoi -> embedding -> search -> xem chi tiet -> sinh bien the -> kiem dinh -> luu cau hoi moi -> dashboard/analytics.

## 1. Nguyen tac trien khai

- Uu tien noi cac API backend da co truoc khi viet API moi.
- Moi man frontend can co state ro rang: loading, error, empty, success.
- Tach API call vao `apps/frontend/src/services/*Api.js`, khong goi fetch truc tiep trong page.
- Khong tiep tuc dung mock data cho cac chuc nang da co backend that.
- Moi lan noi mot nhom chuc nang can test bang backend local va frontend local.
- Cac service backend da co nhung chua co endpoint can duoc bo sung API truoc khi noi UI.

## 2. Pham vi can ket noi

### 2.1. Da co backend API, can noi frontend

| Nhom | API can noi | Frontend page lien quan |
| --- | --- | --- |
| Health/readiness | `GET /`, `GET /health`, `GET /ready` | `Dashboard.jsx`, `Settings.jsx` |
| Document detail | `GET /documents/{document_id}` | `UploadDocument.jsx`, `ProblemDetail.jsx` neu can |
| Document status | `GET /documents/{document_id}/status` | `UploadDocument.jsx` |
| Document markdown | `GET /documents/{document_id}/markdown` | `UploadDocument.jsx`, co the them modal/viewer |
| Semantic question search | `POST /search/questions` | `SemanticSearch.jsx` |
| Formula search | `POST /search/formulas` | `SemanticSearch.jsx` |
| Generation preview | `POST /generation/questions/preview` | `GenVariants.jsx`, `ProblemDetail.jsx` |
| Generation quality | `POST /generation/questions/quality` | `GenVariants.jsx`, `QARules.jsx` |
| Generation save | `POST /generation/questions/save` | `GenVariants.jsx` |

### 2.2. Da co backend service, can them API roi moi noi frontend

| Nhom | Service backend da co | API de xuat |
| --- | --- | --- |
| Segment document | `QuestionCatalogService.segment_document` | `POST /documents/{document_id}/segment` |
| Embed document | `QuestionEmbeddingService.embed_document` | `POST /documents/{document_id}/embed` |
| Store document full flow | `QuestionStorageService.store_document` | `POST /documents/{document_id}/store` |
| List questions by document | `QuestionRepository.list_by_document` | `GET /documents/{document_id}/questions` |
| Question detail | `QuestionRepository.get_question` | `GET /questions/{question_id}` |
| Update metadata question | Chua co service rieng, co repository co the bo sung | `PATCH /questions/{question_id}` |
| Delete document | Chua co API | `DELETE /documents/{document_id}` |
| Retry ingestion | IngestionService da co, can route retry doc failed | `POST /documents/{document_id}/retry` |
| Analytics summary | Chua co service rieng | `GET /analytics/summary` |

## 3. Kien truc frontend can bo sung

### 3.1. Tao cac service API

Can them/cap nhat cac file:

- `apps/frontend/src/services/healthApi.js`
- `apps/frontend/src/services/searchApi.js`
- `apps/frontend/src/services/generationApi.js`
- `apps/frontend/src/services/questionApi.js`
- `apps/frontend/src/services/analyticsApi.js`
- Cap nhat `apps/frontend/src/services/ingestionApi.js`

De xuat ham:

```js
// healthApi.js
export function getRootStatus()
export function getHealth()
export function getReadiness()

// searchApi.js
export function searchQuestions(payload)
export function searchFormulas(payload)

// generationApi.js
export function previewGeneratedQuestions(payload)
export function assessGeneratedQuestionQuality(payload)
export function saveGeneratedQuestion(payload)

// questionApi.js
export function listDocumentQuestions(documentId)
export function getQuestion(questionId)
export function updateQuestion(questionId, payload)

// analyticsApi.js
export function getAnalyticsSummary()

// ingestionApi.js
export function segmentDocument(documentId)
export function embedDocument(documentId)
export function storeDocument(documentId)
export function deleteDocument(documentId)
export function retryDocument(documentId)
```

### 3.2. Tao shared UI/state helpers neu can

Nen them cac component nho, tranh lap lai:

- `LoadingState`
- `ErrorState`
- `EmptyState`
- `StatusBadge`
- `QualityIssueList`
- `QuestionResultCard`
- `DocumentMarkdownModal`
- `ConfirmDialog`

Neu chua muon tach component ngay, co the noi API truc tiep vao page truoc, sau do refactor.

## 4. Ke hoach theo giai doan

## Giai doan 1: Noi document flow hien co cho tron ven

Muc tieu: man Upload Document khong chi upload/list, ma co the xem chi tiet, xem markdown va theo doi status ro rang.

### Viec can lam backend

- Giu nguyen cac endpoint da co:
  - `POST /documents/upload`
  - `GET /documents`
  - `GET /documents/{document_id}`
  - `GET /documents/{document_id}/status`
  - `GET /documents/{document_id}/markdown`

### Viec can lam frontend

- Cap nhat `UploadDocument.jsx`:
  - Nut Eye goi `getDocumentMarkdown(document.id)`.
  - Hien modal/panel xem markdown.
  - Khi document chua co markdown thi hien thong bao.
  - Nut refresh status co the goi list documents hoac status tung document.
  - Hien ro `r2_original_url` neu co.
  - Disable nut xem markdown neu `markdown_available = false`.

### Ket qua mong doi

- Upload file xong nguoi dung thay document chuyen trang thai.
- Khi completed, nguoi dung xem duoc markdown da xu ly.

### Test

- Upload Markdown nho.
- Upload PDF neu co Gemini key.
- Kiem tra failed state khi file sai dinh dang.
- Kiem tra modal markdown.

## Giai doan 2: Bo sung API store document va noi vao Upload Document

Muc tieu: sau khi document completed, nguoi dung co the bam de tach cau hoi va tao embedding, san sang search.

### Viec can lam backend

Them endpoint:

- `POST /documents/{document_id}/store`

Endpoint nay goi:

- `QuestionCatalogService.segment_document(document_id)`
- `QuestionEmbeddingService.embed_document(document_id)`

Response de xuat:

```json
{
  "document_id": "string",
  "question_count": 10,
  "formula_count": 25
}
```

Co the them rieng neu can:

- `POST /documents/{document_id}/segment`
- `POST /documents/{document_id}/embed`

### Viec can lam frontend

- Cap nhat `ingestionApi.js` them `storeDocument(documentId)`.
- Trong `UploadDocument.jsx`, voi document `completed`:
  - Hien nut "Tach cau hoi & embedding".
  - Khi bam thi goi `storeDocument`.
  - Hien loading rieng cho document dang store.
  - Sau khi xong hien so cau hoi/cong thuc.

### Ket qua mong doi

- User co the chuyen document completed thanh du lieu search duoc.

### Test

- Upload markdown co nhieu cau hoi.
- Bam store.
- Kiem tra questions trong PostgreSQL.
- Kiem tra vectors trong Qdrant.
- Sau store, search phai co ket qua.

## Giai doan 3: Noi Semantic Search

Muc tieu: `SemanticSearch.jsx` khong dung `PROBLEMS` mock nua, ma goi API search that.

### Viec can lam backend

Backend da co:

- `POST /search/questions`
- `POST /search/formulas`

Co the giu nguyen.

### Viec can lam frontend

- Tao `apps/frontend/src/services/searchApi.js`.
- Them:
  - `searchQuestions({ query, limit, subject, chapter, difficulty })`
  - `searchFormulas({ latex, limit, source })`
- Cap nhat `SemanticSearch.jsx`:
  - Xoa phu thuoc vao `PROBLEMS` cho ket qua chinh.
  - Search button goi `searchQuestions`.
  - Co mode search:
    - Search cau hoi.
    - Search cong thuc.
  - Bo loc frontend map sang payload API.
  - Hien score tu backend.
  - Hien statement, solution, answer, subject, chapter, difficulty, skills.
  - Khi khong co ket qua hien empty state.
  - Nut "Xem loi giai" mo chi tiet hoac expand answer/solution.
  - Nut "Sinh bien the" dieu huong sang `GenVariants` kem `question_id`.

### Ket qua mong doi

- User nhap query va thay ket qua tu Qdrant/PostgreSQL.
- User co the tim theo noi dung tu nhien hoac cong thuc.

### Test

- Search query binh thuong.
- Search voi filter.
- Search query rong.
- Search formula LaTeX.
- Search khi chua co embedding.

## Giai doan 4: Them Question API va noi Problem Detail

Muc tieu: co trang chi tiet bai tap that thay vi mock.

### Viec can lam backend

Them endpoint:

- `GET /questions/{question_id}`
- `GET /documents/{document_id}/questions`

Response question can co:

- `id`
- `document_id`
- `sequence_number`
- `marker`
- `marker_number`
- `statement`
- `solution`
- `answer`
- `formulas`
- `subject`
- `chapter`
- `difficulty`
- `skills`
- `embedding_status`
- `created_at`
- `updated_at`

Co the them:

- `PATCH /questions/{question_id}` de cap nhat metadata.

### Viec can lam frontend

- Tao `questionApi.js`.
- Cap nhat routing state hien tai:
  - App dang dung `activePage`, chua co router that.
  - Can them state `selectedQuestionId`.
  - Khi bam result card -> set `selectedQuestionId`, navigate `detail`.
- Cap nhat `ProblemDetail.jsx`:
  - Goi `getQuestion(selectedQuestionId)`.
  - Hien statement/solution/answer/formulas that.
  - Nut "Bai tuong tu" goi `/search/questions` voi statement hien tai.
  - Nut "Sinh bien the" navigate sang `gen` kem source question.

### Ket qua mong doi

- User co the xem chi tiet cau hoi that tu ket qua search.

### Test

- Click result -> detail.
- Question khong ton tai -> error state.
- Similar questions tra dung data.

## Giai doan 5: Noi Gen Variants voi generation API

Muc tieu: sinh bien the cau hoi that bang Gemini va luu lai vao database.

### Viec can lam backend

Backend da co:

- `POST /generation/questions/preview`
- `POST /generation/questions/quality`
- `POST /generation/questions/save`

Can dam bao source question co san va document da co questions.

### Viec can lam frontend

- Tao `generationApi.js`.
- Cap nhat `GenVariants.jsx`:
  - Nhan `sourceQuestionId` tu App state.
  - Form constraints:
    - `generation_count`
    - `subject`
    - `chapter`
    - `difficulty`
    - `skills`
    - `preserve_formula_style`
    - `avoid_duplicate`
  - Nut preview goi `previewGeneratedQuestions`.
  - Hien danh sach candidates.
  - Moi candidate hien:
    - statement
    - solution
    - answer
    - formulas
    - quality_warnings
  - Nut "Kiem dinh" goi `assessGeneratedQuestionQuality`.
  - Nut "Luu" chi enable khi `can_save = true`.
  - Sau khi save thanh cong hien question id moi va embedding status.

### Ket qua mong doi

- User co the chon mot cau hoi va sinh bien the that.
- User co the xem canh bao chat luong.
- User co the luu cau hoi moi.

### Test

- Preview 1-3 cau hoi.
- Candidate thieu solution/answer hien warning.
- Candidate duplicate bi chan.
- Save thanh cong va question moi xuat hien khi list document questions.

## Giai doan 6: Noi QA Rules/Quality UI

Muc tieu: man QA Rules hien trang thai kiem dinh that thay vi rule mock.

### Viec can lam backend

Co the dung ngay:

- `POST /generation/questions/quality`

Neu muon hien danh sach rule cau hinh, can them endpoint moi:

- `GET /quality/rules`

Response de xuat:

```json
{
  "rules": [
    {
      "code": "empty_statement",
      "name": "Statement khong duoc rong",
      "severity": "error",
      "enabled": true
    }
  ]
}
```

### Viec can lam frontend

- Cap nhat `QARules.jsx`:
  - Neu chi can view rules: dung static rule list nhung gan voi code backend.
  - Neu can kiem tra candidate: nhan candidate/source question tu `GenVariants`.
  - Hien warnings/blocking issues tu API quality.
  - Hien semantic duplicates.

### Ket qua mong doi

- User hieu tai sao cau hoi sinh duoc/khong duoc luu.

### Test

- Candidate empty statement.
- Candidate duplicate.
- Candidate valid.

## Giai doan 7: Noi Dashboard va Settings voi health/readiness

Muc tieu: dashboard phan anh trang thai he thong that.

### Viec can lam backend

Backend da co:

- `GET /health`
- `GET /ready`

Co the them sau:

- `GET /analytics/summary`

### Viec can lam frontend

- Tao `healthApi.js`.
- Cap nhat `Dashboard.jsx`:
  - Goi `/health`.
  - Goi `/ready`.
  - Hien database/qdrant status that.
  - Lay document count qua `GET /documents`.
- Cap nhat `Settings.jsx`:
  - Hien API base URL.
  - Hien readiness status.
  - Hien CORS/app env neu backend co endpoint config sau nay.

### Ket qua mong doi

- User vao dashboard thay backend/database/vector DB dang online hay loi.

### Test

- Backend online.
- Tat Qdrant/Postgres de xem error state neu can.

## Giai doan 8: Analytics that

Muc tieu: thay mock analytics bang thong ke that.

### Viec can lam backend

Them endpoint:

- `GET /analytics/summary`

Response de xuat:

```json
{
  "document_count": 12,
  "completed_document_count": 10,
  "failed_document_count": 1,
  "question_count": 250,
  "embedded_question_count": 230,
  "formula_count": 600,
  "embedding_status_counts": {
    "pending": 5,
    "completed": 230,
    "failed": 15
  },
  "difficulty_counts": {
    "easy": 40,
    "medium": 120,
    "hard": 90
  },
  "chapter_counts": {
    "Tich phan": 80,
    "Dao ham": 70
  }
}
```

Can query tu PostgreSQL va co the dem Qdrant neu can.

### Viec can lam frontend

- Tao `analyticsApi.js`.
- Cap nhat `Analytics.jsx`:
  - Thay `STATS`, `TOPIC_DATA`, `DIFF_DATA` mock bang API.
  - Hien loading/error/empty.

### Ket qua mong doi

- Analytics phan anh so lieu that cua document/question/embedding.

### Test

- Database rong.
- Database co documents/questions.
- Co embedding failed/pending/completed.

## Giai doan 9: Taxonomy va metadata

Muc tieu: gan/cap nhat subject/chapter/difficulty/skills cho question that de search/filter tot hon.

### Viec can lam backend

Them endpoint:

- `PATCH /questions/{question_id}`
- Co the them `GET /taxonomy` neu muon taxonomy dong.

Payload patch de xuat:

```json
{
  "subject": "Calculus",
  "chapter": "Tich phan",
  "difficulty": "medium",
  "skills": ["Tinh toan", "Bien doi cong thuc"]
}
```

Sau khi update metadata, can xem co can re-embed question/document khong.

### Viec can lam frontend

- Cap nhat `CalculusTaxonomy.jsx`:
  - Co the hien taxonomy static truoc.
  - Them flow gan taxonomy cho selected question/document.
- Cap nhat `ProblemDetail.jsx`:
  - Cho phep sua subject/chapter/difficulty/skills.
  - Goi `updateQuestion`.

### Ket qua mong doi

- Search filters co du lieu that de loc.

### Test

- Update metadata.
- Search filter theo metadata moi.

## Giai doan 10: Delete/retry document va thao tac quan tri

Muc tieu: hoan thien vong doi document.

### Viec can lam backend

Them endpoint:

- `DELETE /documents/{document_id}`
- `POST /documents/{document_id}/retry`

Delete can xu ly:

- Xoa document.
- Xoa questions lien quan.
- Xoa vectors trong Qdrant theo `document_id`.
- Can than voi file R2 neu muon xoa file goc.

Retry can xu ly:

- Chi cho document failed hoac cho phep retry manual.
- Can co cach doc lai original file tu R2 hoac luu bytes. Hien tai upload background nhan `file_bytes`, nen retry sau nay co the can download tu R2.

### Viec can lam frontend

- Cap nhat `UploadDocument.jsx`:
  - Nut Trash goi delete co confirm.
  - Nut Retry cho document failed.
  - Sau delete/retry reload list.

### Ket qua mong doi

- User quan ly duoc document loi/khong can dung.

### Test

- Delete document completed.
- Delete document failed.
- Retry document failed.

## 5. Thu tu uu tien de lam that

Nen lam theo thu tu nay de moi buoc deu co gia tri ngay:

1. Noi xem markdown document trong `UploadDocument.jsx`.
2. Them `POST /documents/{document_id}/store`.
3. Noi nut store document tren UI.
4. Noi `SemanticSearch.jsx` voi `/search/questions`.
5. Noi formula search voi `/search/formulas`.
6. Them `GET /questions/{question_id}` va `GET /documents/{document_id}/questions`.
7. Noi `ProblemDetail.jsx`.
8. Noi `GenVariants.jsx` voi preview/quality/save.
9. Noi Dashboard voi `/health`, `/ready`, `/documents`.
10. Them analytics endpoint va noi `Analytics.jsx`.
11. Them update metadata/taxonomy.
12. Them delete/retry document.

## 6. Checklist chi tiet

### Backend checklist

- [ ] Them response schema cho store/segment/embed document.
- [ ] Them endpoint `POST /documents/{document_id}/store`.
- [ ] Them endpoint `POST /documents/{document_id}/segment` neu can.
- [ ] Them endpoint `POST /documents/{document_id}/embed` neu can.
- [ ] Them endpoint `GET /documents/{document_id}/questions`.
- [ ] Them endpoint `GET /questions/{question_id}`.
- [ ] Them endpoint `PATCH /questions/{question_id}`.
- [ ] Them endpoint `GET /analytics/summary`.
- [ ] Them endpoint `DELETE /documents/{document_id}`.
- [ ] Them endpoint `POST /documents/{document_id}/retry`.
- [ ] Viet test API cho cac endpoint moi.

### Frontend service checklist

- [ ] Tao `healthApi.js`.
- [ ] Tao `searchApi.js`.
- [ ] Tao `generationApi.js`.
- [ ] Tao `questionApi.js`.
- [ ] Tao `analyticsApi.js`.
- [ ] Cap nhat `ingestionApi.js`.

### Frontend page checklist

- [ ] `UploadDocument.jsx`: xem markdown.
- [ ] `UploadDocument.jsx`: store document.
- [ ] `UploadDocument.jsx`: delete/retry neu backend co.
- [ ] `SemanticSearch.jsx`: search questions.
- [ ] `SemanticSearch.jsx`: search formulas.
- [ ] `SemanticSearch.jsx`: navigate sang detail/gen.
- [ ] `ProblemDetail.jsx`: load question detail.
- [ ] `ProblemDetail.jsx`: similar questions.
- [ ] `ProblemDetail.jsx`: update metadata neu backend co.
- [ ] `GenVariants.jsx`: preview generation.
- [ ] `GenVariants.jsx`: quality check.
- [ ] `GenVariants.jsx`: save generated question.
- [ ] `QARules.jsx`: hien issues/rules that.
- [ ] `Dashboard.jsx`: health/readiness/document stats.
- [ ] `Analytics.jsx`: analytics summary.
- [ ] `Settings.jsx`: system status/config display.

## 7. Tieu chi hoan thanh

Frontend duoc xem la da ket noi day du khi:

- Khong con page chinh nao phu thuoc hoan toan vao mock data cho chuc nang da co backend.
- User co the upload document va xem markdown.
- User co the store document de tao questions + embeddings.
- User co the search questions/formulas that.
- User co the xem chi tiet question that.
- User co the sinh bien the, kiem dinh va luu question moi.
- Dashboard hien health/readiness that.
- Analytics hien thong ke that hoac co empty state dung khi database rong.
- Moi API call co loading/error/empty state tren UI.
- Test backend va build frontend pass.

## 8. Rủi ro va luu y

- Gemini/R2/Qdrant/PostgreSQL la external dependencies, can co `.env` dung de test end-to-end.
- Search chi co ket qua khi document da duoc segment va embed.
- Hien frontend dang dung state navigation noi bo trong `App.jsx`, chua co router URL. Neu app lon hon, nen can nhac React Router.
- Nhieu text tieng Viet trong frontend dang bi loi encoding. Nen sua encoding/noi dung song song hoac truoc khi demo.
- Generation save dang embed lai ca document, co the cham neu document lon.
- Retry ingestion can thiet ke lai neu khong luu duoc original bytes local; co the can download original tu R2.

## 9. De xuat chia task theo PR/commit

1. `frontend-documents-markdown-viewer`
   - Noi xem markdown document.

2. `backend-document-store-endpoint`
   - Them endpoint store/segment/embed va test.

3. `frontend-document-store-action`
   - Them nut store document trong Upload page.

4. `frontend-semantic-search-api`
   - Noi question/formula search.

5. `backend-question-read-endpoints`
   - Them question detail va list by document.

6. `frontend-question-detail`
   - Noi Problem Detail.

7. `frontend-generation-flow`
   - Noi preview/quality/save.

8. `frontend-dashboard-health`
   - Noi Dashboard/Settings voi health/readiness.

9. `backend-analytics-summary`
   - Them analytics endpoint.

10. `frontend-analytics-summary`
   - Noi Analytics.

11. `backend-question-metadata`
   - Them update metadata/taxonomy endpoint.

12. `frontend-taxonomy-metadata`
   - Noi taxonomy/metadata editing.

13. `backend-document-admin-actions`
   - Delete/retry document.

14. `frontend-document-admin-actions`
   - Noi delete/retry UI.

## 10. Ket luan

Du an nen duoc ket noi frontend theo luong nghiep vu that thay vi noi tung man rieng le mot cach roi rac. Thu tu tot nhat la:

Document hoan chinh -> Store/embedding -> Search -> Detail -> Generation -> Dashboard/Analytics -> Admin actions.

Neu lam theo thu tu nay, sau moi giai doan ung dung deu co them mot phan workflow chay duoc end-to-end va giam dan phu thuoc vao mock data.

## 11. Bo sung sau khi ra soat ky truoc khi trien khai

Phan ke hoach ben tren da bao phu luong chinh. Tuy nhien, neu muon bat tay lam lien tuc ma it bi khung lai giua chung, nen bo sung cac muc sau vao backlog.

### 11.1. Giai doan 0: On dinh nen tang truoc khi noi API lon

Muc tieu: tranh viec moi lan noi mot page lai phai sua lai navigation, encoding, env hoac error handling.

Viec can lam:

- Chuan hoa text tieng Viet bi loi encoding trong frontend.
- Kiem tra `VITE_API_BASE_URL` cho dev va Docker.
- Kiem tra CORS cho `localhost:5173` va `localhost:8080`.
- Chuan hoa `apiRequest`:
  - Co timeout neu can.
  - Xu ly loi network.
  - Xu ly loi backend tra ve `detail`.
  - Khong lam app crash khi response khong phai JSON.
- Quyet dinh navigation:
  - Tiep tuc dung `activePage` va state noi bo.
  - Hoac chuyen sang React Router neu can URL rieng cho question/detail.
- Kiem tra luong khoi tao database:
  - `scripts/create_tables.py`
  - Docker Compose
  - `.env`/`.env.example`

Neu bo qua muc nay, van co the noi API, nhung de phat sinh loi vat vat khi test end-to-end.

### 11.2. Bo sung xem/mo file goc cua document

Backend hien co `r2_original_key` va `r2_original_url` trong `DocumentResponse`.

Chuc nang nen them frontend:

- Hien link mo file goc neu `r2_original_url` co gia tri.
- Nut copy R2 key.
- Trang thai neu file goc khong public URL.

Chua can backend moi neu chi dung `r2_original_url`. Neu muon file private, can them endpoint tao signed URL:

- `GET /documents/{document_id}/original-url`

### 11.3. Bo sung trang thai store/embedding theo document

Plan da co `POST /documents/{document_id}/store`, nhung can them cach frontend biet document da store/embed xong hay chua.

De xuat backend:

- `GET /documents/{document_id}/questions`
- `GET /documents/{document_id}/embedding-status`

Response embedding status de xuat:

```json
{
  "document_id": "string",
  "question_count": 10,
  "embedding_status_counts": {
    "pending": 0,
    "completed": 10,
    "failed": 0
  },
  "qdrant_question_points": 10,
  "qdrant_formula_points": 25
}
```

Frontend:

- Sau khi document completed, hien trang thai:
  - Chua tach cau hoi.
  - Da tach cau hoi nhung chua embedding.
  - Da embedding xong.
  - Embedding loi.
- Nut store chi enable khi document `completed`.
- Neu da store roi, nut hien "Re-store/Re-embed" hoac "Da san sang search".

### 11.4. Bo sung source question picker cho man Gen Variants

Plan da noi `GenVariants.jsx` nhan `sourceQuestionId` tu App state. Nhung neu nguoi dung vao truc tiep menu "Sinh bien the", page se khong co source question.

Can them:

- O search/chon source question trong `GenVariants.jsx`.
- Co the dung `searchQuestions` de tim cau hoi nguon.
- Hoac chon document -> list questions -> chon source question.
- Empty state: "Hay chon mot cau hoi nguon de sinh bien the".

Backend can co:

- `GET /documents/{document_id}/questions`
- `GET /questions/{question_id}`

### 11.5. Bo sung list questions cua document tren Upload/Document detail

Sau khi store document, nguoi dung nen xem duoc document da tach ra bao nhieu cau hoi.

Frontend:

- Trong `UploadDocument.jsx`, them nut "Xem cau hoi".
- Hien panel/modal danh sach questions cua document.
- Click question -> mo `ProblemDetail.jsx`.

Backend:

- `GET /documents/{document_id}/questions`.

### 11.6. Bo sung search history va recent activity neu muon Dashboard het mock

Dashboard hien co recent queries/activities mock. Backend hien chua luu search logs hoac activity logs.

Lua chon toi thieu:

- Dung local state/localStorage cho recent search frontend.
- Dashboard lay recent documents tu `GET /documents`.

Lua chon day du:

- Them bang/activity log backend.
- Them endpoint:
  - `GET /activities/recent`
  - `GET /search/history`
  - `POST /search/history`

Neu chua can Dashboard that hoan toan, co the de muc nay sau analytics.

### 11.7. Bo sung cau hinh model/system status cho Settings

Settings hien la mock users/settings. Backend chua co auth/user/config endpoint.

Neu muon Settings co du lieu that, them endpoint read-only:

- `GET /settings/system`

Response de xuat:

```json
{
  "app_env": "local",
  "gemini_model": "gemini-2.5-flash",
  "embedding_model": "gemini-embedding-2",
  "embedding_dimension": 768,
  "qdrant_question_collection": "question_embeddings",
  "qdrant_formula_collection": "formula_embeddings",
  "max_upload_size_mb": 40
}
```

Frontend:

- `Settings.jsx` hien system config dang doc tu backend.
- Khong hien secret key.

### 11.8. Bo sung test/build checklist truoc moi giai doan

Moi giai doan nen chay:

- Backend unit/API tests:
  - `.\.venv\Scripts\python.exe -m pytest -q`
- Frontend lint/build:
  - `npm run lint`
  - `npm run build`
- Neu co Docker:
  - `docker compose up --build`
  - Kiem tra `GET /ready`
  - Kiem tra frontend goi dung API base URL.

### 11.9. Cac muc co the de sau, khong bat buoc cho ban dau

Cac muc nay khong can lam ngay neu muc tieu la demo luong chinh:

- Auth/user management that.
- Search history backend.
- Activity log backend.
- Signed URL cho file private.
- Retry ingestion hoan chinh neu chua co co che download file goc tu R2.
- Bulk taxonomy tagging.
- Re-embed tung question rieng le.
- Export ket qua search/generation.

## 12. Checklist cuoi cung truoc khi bat dau code

- [ ] Sua/ghi nhan viec text tieng Viet frontend bi loi encoding.
- [ ] Quyet dinh co dung React Router hay tiep tuc `activePage`.
- [ ] Dam bao `.env` co PostgreSQL, Qdrant, Gemini, R2 dung.
- [ ] Chay test backend hien tai pass.
- [ ] Chay build frontend hien tai de biet loi san co.
- [ ] Lam Giai doan 0 neu can on dinh nen tang.
- [ ] Bat dau Giai doan 1: noi xem markdown document.
- [ ] Sau do moi them store/embedding endpoint.
