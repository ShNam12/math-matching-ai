<<<<<<< HEAD
# AI Matching - Hệ thống ngân hàng câu hỏi Toán học tích hợp AI

AI Matching la he thong backend FastAPI va frontend React/Vite dung de ingest tai lieu Toan, tach cau hoi, phan loai taxonomy Giai tich 1, tao embedding, tim kiem ngu nghia/cong thuc, sinh cau hoi trac nghiem va kiem dinh chat luong bang cac rule ket hop symbolic solver.

## Muc Luc

- [Tong Quan](#tong-quan)
- [Tinh Nang Chinh](#tinh-nang-chinh)
- [Cong Nghe Su Dung](#cong-nghe-su-dung)
- [Kien Truc He Thong](#kien-truc-he-thong)
- [Quy Trinh Xu Ly AI](#quy-trinh-xu-ly-ai)
- [Cau Truc Thu Muc](#cau-truc-thu-muc)
- [Yeu Cau He Thong](#yeu-cau-he-thong)
- [Huong Dan Cai Dat](#huong-dan-cai-dat)
- [Cau Hinh Bien Moi Truong](#cau-hinh-bien-moi-truong)
- [Khoi Chay Du An](#khoi-chay-du-an)
- [Huong Dan Su Dung](#huong-dan-su-dung)
- [API Documentation](#api-documentation)
- [Vi Du Dau Vao Va Dau Ra](#vi-du-dau-vao-va-dau-ra)
- [Kiem Thu](#kiem-thu)
- [Danh Gia He Thong AI](#danh-gia-he-thong-ai)
- [Bao Mat](#bao-mat)
- [Han Che Hien Tai](#han-che-hien-tai)
- [Huong Phat Trien](#huong-phat-trien)
- [Dong Gop](#dong-gop)
- [License](#license)
- [Tac Gia Va Lien He](#tac-gia-va-lien-he)

## Tong Quan

Du an giai quyet bai toan xay dung ngan hang cau hoi Toan hoc tu tai lieu dau vao nhu PDF hoac Markdown. He thong co the luu tru tai lieu, chuyen PDF sang Markdown bang Gemini, chuan hoa noi dung, tach cau hoi, trich xuat cong thuc, phan loai cau hoi theo taxonomy Giai tich 1, tao vector embedding va ho tro tim kiem cau hoi tuong tu.

Doi tuong su dung chinh la nguoi phat trien, giang vien hoac nguoi quan tri can xay dung va khai thac ngan hang cau hoi. Frontend hien co cac man hinh Dashboard, Upload Document, Semantic Search, Calculus Taxonomy, QA Rules, Problem Detail, GenVariants, Analytics va Settings.

Vai tro cua AI trong he thong:

- Gemini PDF converter: chuyen PDF thanh Markdown.
- Gemini classifier: phan loai cau hoi vao taxonomy.
- Gemini embedding: tao embedding cho cau hoi va cong thuc.
- Gemini generator: sinh cau hoi trac nghiem tu cau hoi nguon hoac chuyen cau hoi tu luan sang trac nghiem.
- Neuro-symbolic validation: dung SymPy, solver registry, distractor generator va rule-based validator de kiem tra dap an/dap an nhieu.

Pham vi hien tai cua du an bao gom ca cau hoi `free_response` va `multiple_choice`. Schema, API, search, generation, quality rules, analytics va frontend da co truong ho tro trac nghiem nhu `choices`, `correct_choice`, `validation_report`, `generation_method`, `solver_code` va `review_status`.

## Tinh Nang Chinh

### Quan ly va xu ly tai lieu

- Upload file PDF, Markdown hoac `.markdown`.
- Gioi han dung luong upload theo `MAX_UPLOAD_SIZE_MB`.
- Luu metadata tai lieu vao PostgreSQL.
- Upload ban goc len Cloudflare R2 thong qua API S3-compatible.
- Chuyen PDF sang Markdown bang Gemini.
- Chuan hoa Markdown sau khi ingest.
- Lay trang thai xu ly va noi dung Markdown da tao.

### Tach va luu cau hoi

- Tach cau hoi tu Markdown dua tren pattern marker.
- Tach phan de bai, loi giai va dap an.
- Phat hien cau hoi trac nghiem co lua chon A/B/C/D.
- Trich xuat cong thuc tu de bai, loi giai, dap an va choices.
- Luu cau hoi vao PostgreSQL voi metadata taxonomy, embedding va review.

### Taxonomy Classification

- Su dung taxonomy Giai tich 1 trong `core/taxonomy/calculus_1_taxonomy.json`.
- Phan loai cau hoi bang Gemini classifier.
- Luu `chapter_code`, `topic_code`, `problem_type_code`, ten hien thi, confidence, reason va model phan loai.
- Kiem tra chat luong taxonomy: thieu ma, sai quan he cha-con, confidence thap, skill ngoai vocabulary, difficulty khong hop le.

### Embedding, Semantic Search va Formula Search

- Tao embedding bang `gemini-embedding-2`.
- Luu vector vao Qdrant trong cac collection cau hinh.
- Tao text embedding gom statement, choices, correct choice, solution, answer, formula va taxonomy.
- Tim kiem semantic cau hoi theo query text.
- Tim kiem cong thuc theo LaTeX da normalize.
- Hybrid scoring ket hop semantic score, taxonomy score, formula score, difficulty score, skill score va choice structure score.
- Filter search theo subject, chapter, question type, taxonomy code, difficulty va skill.

### Sinh va kiem dinh cau hoi trac nghiem

- Sinh cau hoi trac nghiem AI tu cau hoi nguon.
- Chuyen cau hoi tu luan sang trac nghiem.
- Sinh trac nghiem symbolic theo solver Giai tich 1.
- Luu generated candidate vao question bank va tao lai embedding cho document.
- Kiem tra structural rules: dung 4 choices A/B/C/D, dung mot dap an, khong thieu text, khong trung key.
- Kiem tra distractor rules: khong trung noi dung, distractor khong bang dap an dung, choices khong qua giong nhau.
- Kiem tra symbolic neu co solver: dap an dung khop solver, distractor khong trung dap an dung.
- Tra ve `validation_report`, `warnings`, `blocking_issues`, `symbolic_checks` va semantic duplicates.

### Dashboard va Analytics

- Thong ke document theo trang thai.
- Thong ke cau hoi da embedding, cong thuc, difficulty, chapter, topic.
- Thong ke cau hoi trac nghiem, cau tu luan, MCQ validated, MCQ blocking issue.
- Do ty le valid MCQ, loi dap an dung, loi distractor, solver unavailable va cau can review.
- Thong ke theo `generation_method`.

## Cong Nghe Su Dung

### Backend

| Cong nghe | Vai tro |
| --- | --- |
| Python 3.12 | Runtime backend trong Dockerfile goc. |
| FastAPI | Xay dung REST API, OpenAPI va Swagger UI. |
| Pydantic / pydantic-settings | Dinh nghia request/response model va bien moi truong. |
| SQLAlchemy async | Truy cap PostgreSQL bang async session. |
| Uvicorn | ASGI server cho FastAPI. |
| pytest / httpx | Kiem thu module va API. |

### Frontend

| Cong nghe | Vai tro |
| --- | --- |
| React 19 | Xay dung giao dien mot trang. |
| Vite | Dev server va build frontend. |
| Tailwind CSS 4 | Styling frontend. |
| KaTeX | Render bieu thuc Toan trong UI. |
| lucide-react | Icon trong giao dien. |
| ESLint | Lint source frontend. |

### AI/ML

| Thanh phan | Vai tro |
| --- | --- |
| `google-genai` | Goi Gemini cho PDF conversion, classification, generation va embedding. |
| `GEMINI_MODEL` | Model sinh/phan loai mac dinh trong `.env.example`: `gemini-2.5-flash`. |
| `EMBEDDING_MODEL` | Embedding model mac dinh: `gemini-embedding-2`. |
| Qdrant | Vector database cho semantic search va formula search. |
| SymPy | Solver va validation symbolic cho mot so dang bai. |

### Database va Storage

| Cong nghe | Vai tro |
| --- | --- |
| PostgreSQL 16 Alpine | Database chinh trong Docker Compose. |
| Qdrant v1.12.4 | Luu vector embedding cua cau hoi va cong thuc. |
| Cloudflare R2 / S3-compatible storage | Luu file goc da upload thong qua `boto3`. |

### DevOps

| Cong nghe | Vai tro |
| --- | --- |
| Docker | Dong goi backend va frontend. |
| Docker Compose | Chay PostgreSQL, Qdrant, API va frontend. |
| Nginx | Serve frontend production image. |
| GitHub Actions | TODO: Can bo sung thong tin. Khong thay file CI/CD trong repository. |

## Kien Truc He Thong

```mermaid
flowchart LR
    User[User / Browser] --> Frontend[React Vite Frontend]
    Frontend --> API[FastAPI Backend]

    API --> Postgres[(PostgreSQL)]
    API --> R2[Cloudflare R2 / S3 API]
    API --> Qdrant[(Qdrant Vector DB)]

    API --> Ingestion[Ingestion Service]
    API --> Segmenter[Question Segmenter]
    API --> Classification[Gemini Classification]
    API --> Embedding[Gemini Embedding]
    API --> Generation[Gemini MCQ Generation]
    API --> Neuro[Neuro-symbolic Validation]

    Ingestion --> GeminiPDF[Gemini PDF Converter]
    Classification --> GeminiAPI[Gemini API]
    Embedding --> GeminiAPI
    Generation --> GeminiAPI
    Neuro --> SymPy[SymPy Solver]

    Segmenter --> Postgres
    Classification --> Postgres
    Embedding --> Qdrant
    Neuro --> Postgres
```

Luong du lieu chinh:

1. Frontend goi FastAPI.
2. API luu metadata vao PostgreSQL va file goc vao R2.
3. Ingestion chuyen PDF/Markdown thanh Markdown chuan hoa.
4. Store pipeline tach cau hoi, phan loai taxonomy va tao embedding.
5. Search truy van Qdrant, lay metadata tu PostgreSQL va tinh hybrid score.
6. Generation tao MCQ bang Gemini hoac symbolic generator.
7. Quality service kiem dinh candidate truoc khi luu.

## Quy Trinh Xu Ly AI

```mermaid
flowchart TD
    Upload[Upload PDF/Markdown] --> Validate[Validate filename, suffix, size]
    Validate --> StoreOriginal[Upload original to R2]
    StoreOriginal --> Convert{Source type}
    Convert -->|Markdown| Normalize[Normalize Markdown]
    Convert -->|PDF| GeminiPDF[Gemini PDF to Markdown]
    GeminiPDF --> Normalize
    Normalize --> SaveMarkdown[Save markdown to PostgreSQL]
    SaveMarkdown --> Segment[Segment questions and parse MCQ]
    Segment --> ExtractFormula[Extract formulas]
    ExtractFormula --> Classify[Gemini taxonomy classification]
    Classify --> SaveQuestions[Save questions and taxonomy metadata]
    SaveQuestions --> Embed[Gemini embeddings]
    Embed --> Qdrant[Store vectors in Qdrant]
    Qdrant --> Search[Semantic / Formula / Hybrid Search]
    SaveQuestions --> Generate[AI or Symbolic MCQ generation]
    Generate --> ValidateMCQ[Rule + symbolic quality validation]
    ValidateMCQ --> SaveGenerated[Save generated question]
```

Phan biet cac nhom xu ly:

- Rule-based: validate file upload, segment pattern, MCQ parser A/B/C/D, taxonomy quality rules, MCQ structural rules, duplicate rules.
- LLM: Gemini PDF conversion, question classification, AI question generation, convert free-response to MCQ.
- Semantic embedding: `QuestionEmbeddingService`, `GeminiEmbedder`, Qdrant repositories va hybrid search.
- Symbolic: `modules/neuro_symbolic` voi solver registry, executor, parameter sampler, distractor service va symbolic validator.
- Hau xu ly: normalize Markdown, normalize formula, quality report, validation report, review status va analytics.

## Cau Truc Thu Muc

```text
DATN/
|-- apps/
|   |-- api/
|   |   |-- main.py
|   |   `-- v1/
|   |       |-- endpoints/
|   |       |-- models/
|   |       `-- services/
|   `-- frontend/
|       |-- src/
|       |   |-- pages/
|       |   |-- services/
|       |   `-- components/
|       |-- package.json
|       `-- Dockerfile
|-- core/
|   |-- config/
|   `-- taxonomy/
|-- infra/
|   |-- db/
|   |-- storage/
|   `-- vector_db/
|-- modules/
|   |-- embeddings/
|   |-- ingestion/
|   |-- neuro_symbolic/
|   |-- question_classification/
|   |-- question_generation/
|   |-- question_quality/
|   |-- question_segmenter/
|   |-- question_storage/
|   |-- semantic_search/
|   `-- taxonomy/
|-- scripts/
|-- tests/
|-- Plan/
|-- MathBank-main/
|-- docker-compose.yml
|-- Dockerfile
|-- requirements.txt
`-- README.md
```

Vai tro chinh:

- `apps/api`: FastAPI app, endpoint, request/response model va API service layer.
- `apps/frontend`: React/Vite UI va API client.
- `core/config`: cau hinh moi truong qua Pydantic Settings.
- `core/taxonomy`: taxonomy Giai tich 1.
- `infra/db`: SQLAlchemy model, session va repository PostgreSQL.
- `infra/storage`: R2/S3-compatible storage client.
- `infra/vector_db`: Qdrant client va vector repository.
- `modules`: cac module nghiep vu AI, search, generation, quality va storage.
- `scripts`: script tao bang, migration, sync, test thu cong va evaluator.
- `tests`: unit/API/integration tests.
- `MathBank-main`: source legacy de tham khao logic solver/distractor, khong duoc import truc tiep vao production module hien tai.

## Yeu Cau He Thong

| Thanh phan | Phien ban / yeu cau lay tu repository |
| --- | --- |
| Python | 3.12 trong Dockerfile backend. |
| Node.js | 22 Alpine trong Dockerfile frontend. |
| PostgreSQL | 16 Alpine trong `docker-compose.yml`. |
| Qdrant | v1.12.4 trong `docker-compose.yml`. |
| Docker / Docker Compose | Can co de chay stack day du. |
| Gemini API key | Bat buoc neu dung PDF conversion, classification, embedding hoac generation. |
| Cloudflare R2 credentials | Bat buoc theo `Settings` vi ingestion upload file goc qua R2 client. |

Dung luong upload mac dinh trong `.env.example` la 40 MB.

## Huong Dan Cai Dat

Clone repository:

```bash
git clone <repository-url>
cd DATN
```

Tao va kich hoat moi truong Python tren Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Tao va kich hoat moi truong Python tren Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Cai dependency backend:

```bash
pip install -r requirements.txt
```

Cai dependency frontend:

```bash
cd apps/frontend
npm install
```

Tao file moi truong:

```bash
copy .env.example .env
```

Tren Linux/macOS:
=======
# Math Matching AI

Hệ thống ngân hàng câu hỏi Toán học tích hợp AI, hỗ trợ xử lý tài liệu, phân loại câu hỏi theo lược đồ tri thức, tìm kiếm ngữ nghĩa, sinh câu hỏi trắc nghiệm và kiểm định chất lượng bằng phương pháp neuro-symbolic.

## Tổng quan

Math Matching AI được xây dựng nhằm tự động hóa quá trình tạo và quản lý ngân hàng câu hỏi Toán học từ tài liệu PDF hoặc Markdown.

Hệ thống có khả năng:

* Chuyển đổi và chuẩn hóa tài liệu Toán học.
* Tách câu hỏi và trích xuất công thức.
* Phân loại câu hỏi theo taxonomy Giải tích 1.
* Tạo embedding và tìm kiếm câu hỏi tương tự.
* Sinh câu hỏi trắc nghiệm từ câu hỏi nguồn.
* Kiểm định cấu trúc, đáp án và phương án nhiễu.
* Xác minh một số dạng bài bằng SymPy.

## Tính năng chính

### Xử lý tài liệu

* Upload tài liệu PDF và Markdown.
* Chuyển PDF sang Markdown bằng Gemini.
* Chuẩn hóa nội dung và lưu trữ tài liệu.
* Tách câu hỏi, lời giải, đáp án và công thức.

### AI Matching và tìm kiếm

* Phân loại câu hỏi theo chương, chủ đề và dạng bài.
* Tạo embedding cho nội dung và công thức.
* Tìm kiếm ngữ nghĩa bằng Qdrant.
* Tìm kiếm theo taxonomy, độ khó và loại câu hỏi.

### Sinh câu hỏi trắc nghiệm

* Chuyển câu hỏi tự luận sang trắc nghiệm.
* Sinh biến thể câu hỏi bằng Gemini.
* Sinh câu hỏi bằng symbolic solver.
* Kiểm tra đáp án và phương án nhiễu trước khi lưu.

### Kiểm định chất lượng

* Kiểm tra đủ bốn lựa chọn A, B, C, D.
* Bảo đảm chỉ có một đáp án đúng.
* Phát hiện phương án trùng lặp.
* Xác minh đáp án bằng symbolic solver khi hỗ trợ.
* Phát hiện câu hỏi trùng về mặt ngữ nghĩa.

## Kiến trúc hệ thống

```mermaid
flowchart LR
    User[Người dùng] --> Frontend[React / Vite]
    Frontend --> API[FastAPI]

    API --> PostgreSQL[(PostgreSQL)]
    API --> Qdrant[(Qdrant)]
    API --> R2[Cloudflare R2]

    API --> Gemini[Gemini API]
    API --> SymPy[SymPy Solver]
```

Luồng xử lý chính:

```mermaid
flowchart LR
    Upload[PDF / Markdown]
    --> Normalize[Chuẩn hóa tài liệu]
    --> Segment[Tách câu hỏi]
    --> Classify[Phân loại taxonomy]
    --> Embed[Tạo embedding]
    --> Store[Lưu PostgreSQL và Qdrant]
    --> Search[Tìm kiếm / Sinh câu hỏi]
    --> Validate[Kiểm định chất lượng]
```

## Công nghệ sử dụng

### Backend

* Python 3.12
* FastAPI
* SQLAlchemy Async
* Pydantic
* PostgreSQL
* Uvicorn

### Frontend

* React
* Vite
* Tailwind CSS
* KaTeX

### AI và xử lý Toán học

* Google Gemini
* Gemini Embedding
* Qdrant
* SymPy

### Hạ tầng

* Docker
* Docker Compose
* Nginx
* Cloudflare R2

## Cấu trúc thư mục

```text
math-matching-ai/
├── apps/
│   ├── api/                 # FastAPI backend
│   └── frontend/            # React/Vite frontend
├── core/
│   ├── config/              # Cấu hình hệ thống
│   └── taxonomy/            # Taxonomy Giải tích 1
├── infra/
│   ├── db/                  # PostgreSQL
│   ├── storage/             # Cloudflare R2
│   └── vector_db/           # Qdrant
├── modules/
│   ├── embeddings/
│   ├── ingestion/
│   ├── neuro_symbolic/
│   ├── question_classification/
│   ├── question_generation/
│   ├── question_quality/
│   ├── question_segmenter/
│   ├── question_storage/
│   ├── semantic_search/
│   └── taxonomy/
├── scripts/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Cài đặt

### 1. Clone repository

```bash
git clone git@github.com:ShNam12/math-matching-ai.git
cd math-matching-ai
```

### 2. Tạo file cấu hình
>>>>>>> 9059a4aa92f9df53e972cff2565089a8bc61290d

```bash
cp .env.example .env
```

<<<<<<< HEAD
Sau do cap nhat cac gia tri API key, database, Qdrant va R2 trong `.env`.

## Cau Hinh Bien Moi Truong

Chi cac bien duoc source code su dung moi duoc liet ke o bang sau.

| Bien | Bat buoc | Mo ta | Gia tri vi du an toan |
| --- | --- | --- | --- |
| `APP_ENV` | Khong | Moi truong chay ung dung. | `local` |
| `CORS_ALLOW_ORIGINS` | Khong | Danh sach origin frontend duoc phep goi API. | `http://localhost:5173,http://localhost:8080` |
| `DATABASE_URL` | Co | PostgreSQL async URL cho SQLAlchemy. | `postgresql+asyncpg://ai_matching:ai_matching_password@localhost:5432/ai_matching` |
| `GEMINI_API_KEY` | Co | API key de goi Gemini. | `your_gemini_api_key_here` |
| `GEMINI_MODEL` | Khong | Model Gemini cho classification/generation. | `gemini-2.5-flash` |
| `EMBEDDING_MODEL` | Khong | Model embedding. | `gemini-embedding-2` |
| `EMBEDDING_DIMENSION` | Khong | So chieu vector embedding. | `768` |
| `QDRANT_URL` | Khong | URL Qdrant. | `http://localhost:6333` |
| `QDRANT_API_KEY` | Khong | API key Qdrant neu co. | `` |
| `QDRANT_QUESTION_COLLECTION` | Khong | Collection luu embedding cau hoi. | `question_embeddings` |
| `QDRANT_FORMULA_COLLECTION` | Khong | Collection luu embedding cong thuc. | `formula_embeddings` |
| `R2_ENDPOINT_URL` | Co | Endpoint S3-compatible cua Cloudflare R2. | `https://example.r2.cloudflarestorage.com` |
| `R2_ACCESS_KEY_ID` | Co | Access key R2. | `your_access_key_id` |
| `R2_SECRET_ACCESS_KEY` | Co | Secret key R2. | `your_secret_access_key` |
| `R2_BUCKET_NAME` | Co | Bucket luu file upload. | `ai-matching-documents` |
| `R2_PUBLIC_BASE_URL` | Khong | Public base URL neu bucket co public access. | `https://cdn.example.com` |
| `MAX_UPLOAD_SIZE_MB` | Khong | Gioi han dung luong upload. | `40` |
| `JWT_SECRET_KEY` | Khong | Secret ky JWT cho dang nhap demo. | `change-me-for-demo` |
| `JWT_ALGORITHM` | Khong | Thuat toan ky JWT. | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Khong | Thoi gian het han access token. | `480` |
| `VITE_API_BASE_URL` | Khong | Frontend API base URL. | `http://localhost:8000` |

Repository da co `.env.example`. Khong commit `.env` that len Git.

## Khoi Chay Du An

### Chay bang Docker Compose

Chay toan bo stack:
=======
Trên Windows:

```powershell
copy .env.example .env
```

Cập nhật các thông tin cần thiết trong `.env`, bao gồm:

* Gemini API key
* PostgreSQL
* Qdrant
* Cloudflare R2

### 3. Khởi chạy bằng Docker
>>>>>>> 9059a4aa92f9df53e972cff2565089a8bc61290d

```bash
docker compose up --build
```

<<<<<<< HEAD
API mac dinh:

```text
http://localhost:8000
```

Frontend production qua Nginx:

```text
http://localhost:8080
```

Qdrant:

```text
http://localhost:6333
```

Dung stack:
=======
Các dịch vụ mặc định:

| Dịch vụ     | Địa chỉ                      |
| ----------- | ---------------------------- |
| Frontend    | `http://localhost:8080`      |
| Backend API | `http://localhost:8000`      |
| Swagger UI  | `http://localhost:8000/docs` |
| Qdrant      | `http://localhost:6333`      |

Dừng hệ thống:
>>>>>>> 9059a4aa92f9df53e972cff2565089a8bc61290d

```bash
docker compose down
```

<<<<<<< HEAD
### Chay truc tiep trong moi truong phat trien

Chay database va vector database bang Docker Compose:

```bash
docker compose up -d postgres qdrant
```

Tao bang database:

```bash
.venv\Scripts\python.exe scripts\create_tables.py
```

Seed tai khoan demo admin/user:

```bash
.venv\Scripts\python.exe scripts\seed_demo_users.py
```

Chay migration MCQ neu database da co schema cu:

```bash
.venv\Scripts\python.exe scripts\migrate_step_mcq_fields.py
```

Chay backend:

```bash
.venv\Scripts\uvicorn.exe apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

Tren Linux/macOS:

```bash
python scripts/create_tables.py
python scripts/seed_demo_users.py
python scripts/migrate_step_mcq_fields.py
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

Chay frontend development:

```bash
cd apps/frontend
npm run dev
```

Frontend dev mac dinh cua Vite:
=======
## Chạy trong môi trường phát triển

### Backend

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn apps.api.main:app --reload
```

Linux hoặc macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn apps.api.main:app --reload
```

### Frontend

```bash
cd apps/frontend
npm install
npm run dev
```

Frontend development chạy tại:
>>>>>>> 9059a4aa92f9df53e972cff2565089a8bc61290d

```text
http://localhost:5173
```

<<<<<<< HEAD
## Huong Dan Su Dung

Luong su dung co ban:

1. Mo frontend tai `http://localhost:5173` khi chay dev hoac `http://localhost:8080` khi chay Docker Compose.
2. Dang nhap bang tai khoan demo da seed.
3. Neu dang nhap bang `admin`, vao Upload Document va upload file PDF/Markdown.
4. Doi backend ingest tai lieu, chuyen Markdown va luu trang thai document.
5. Goi store document de tach cau hoi, phan loai taxonomy va tao embedding.
6. Vao Semantic Search de tim cau hoi theo noi dung, cong thuc hoac taxonomy.
7. Mo Problem Detail de xem statement, choices, dap an, solution, taxonomy, embedding status va validation report.
8. Neu dang nhap bang `admin`, vao GenVariants de sinh MCQ bang AI, symbolic solver hoac convert tu cau hoi tu luan.
9. Neu dang nhap bang `admin`, kiem tra QA Rules/quality report truoc khi luu generated question.
10. Neu dang nhap bang `admin`, vao Analytics de xem phan bo cau hoi va chi so chat luong MCQ.

Tai khoan demo:

| Username | Password | Role |
| --- | --- | --- |
| `admin` | `Admin@123` | `admin` |
| `user1` | `User@123` | `user` |
| `user2` | `User@123` | `user` |
| `user3` | `User@123` | `user` |

Du lieu cau hoi, tai lieu, taxonomy va ket qua AI Matching duoc dung chung. Phan quyen chi kiem soat thao tac theo vai tro: `admin` van hanh/quan tri, `user` khai thac va tra cuu.

## API Documentation

FastAPI tu dong cung cap:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Nhom endpoint chinh

| Nhom | Endpoint tieu bieu | Muc dich |
| --- | --- | --- |
| Health | `GET /`, `GET /health`, `GET /ready` | Kiem tra API, database va Qdrant. |
| Auth | `POST /auth/login`, `GET /auth/me` | Dang nhap bang username/password va lay thong tin user hien tai. |
| Documents | `POST /documents/upload`, `POST /documents/{document_id}/store`, `POST /documents/{document_id}/classify` | Upload, ingest, store, classify va xem document. |
| Questions | `GET /questions/{question_id}`, `PATCH /questions/{question_id}`, `PATCH /questions/{question_id}/review-status` | Xem/cap nhat metadata, review status, classify tung cau hoi. |
| Search | `POST /search/questions`, `POST /search/formulas` | Tim cau hoi va cong thuc bang vector search. |
| Generation | `POST /generation/questions/preview`, `POST /generation/questions/save`, `GET /generation/mcq/solvers`, `POST /generation/mcq/symbolic/preview` | Sinh, kiem dinh va luu cau hoi. |
| Taxonomy | `GET /taxonomy`, `GET /taxonomy/stats` | Lay taxonomy va thong ke theo taxonomy. |
| Analytics | `GET /analytics/summary` | Lay thong ke dashboard/quality. |

### Vi du request

Upload tai lieu:

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@sample.md"
```

Luu cau hoi tu document da ingest:

```bash
curl -X POST "http://localhost:8000/documents/<document_id>/store"
```

Tim cau hoi trac nghiem va an dap an:

```bash
curl -X POST "http://localhost:8000/search/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "tich phan tung phan",
    "limit": 5,
    "include_answers": false,
    "question_type": "multiple_choice",
    "difficulty": "medium"
  }'
```

Sinh preview MCQ symbolic:

```bash
curl -X POST "http://localhost:8000/generation/mcq/symbolic/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "solver_code": "INT_MONOMIAL",
    "generation_count": 2,
    "difficulty": "easy",
    "subject": "calculus",
    "chapter": "integration",
    "skills": ["power_rule"],
    "seed": 42
  }'
```

Danh gia quality cho generated candidate:

```bash
curl -X POST "http://localhost:8000/generation/questions/quality" \
  -H "Content-Type: application/json" \
  -d '{
    "source_question_id": "<question_id>",
    "requested_difficulty": "medium",
    "candidate": {
      "statement": "Tinh tich phan bat dinh $\\int 2x\\,dx$.",
      "solution": "Dung cong thuc luy thua.",
      "answer": "x^2 + C",
      "question_type": "multiple_choice",
      "choices": [
        {"key": "A", "text": "x^2 + C", "latex": "x^2 + C", "is_correct": true},
        {"key": "B", "text": "2x^2 + C", "latex": "2x^2 + C", "is_correct": false},
        {"key": "C", "text": "2 + C", "latex": "2 + C", "is_correct": false},
        {"key": "D", "text": "x + C", "latex": "x + C", "is_correct": false}
      ],
      "correct_choice": "A",
      "difficulty": "medium",
      "skills": ["power_rule"],
      "formulas": [],
      "generation_method": "ai"
    }
  }'
```

## Vi Du Dau Vao Va Dau Ra

Dau vao Markdown:

```markdown
### Bai 1. Tinh tich phan bat dinh $\int 2x\,dx$.

A. $x^2 + C$
B. $2x^2 + C$
C. $2 + C$
D. $x + C$

Dap an: A

Loi giai: Ap dung cong thuc $\int ax dx = ax^2/2 + C$.
```

Cac buoc xu ly chinh:

1. Upload file Markdown.
2. Ingestion normalize Markdown va luu vao PostgreSQL.
3. Store pipeline segment thanh mot cau hoi.
4. MCQ parser nhan ra choices A/B/C/D va `correct_choice = "A"`.
5. Formula extractor lay cong thuc tu statement, choices va solution.
6. Classification gan taxonomy bang Gemini.
7. Embedding service tao vector va luu vao Qdrant.

Dau ra rut gon:

```json
{
  "question_type": "multiple_choice",
  "statement": "Tinh tich phan bat dinh $\\int 2x\\,dx$.",
  "choices": [
    {"key": "A", "text": "$x^2 + C$", "is_correct": true},
    {"key": "B", "text": "$2x^2 + C$", "is_correct": false},
    {"key": "C", "text": "$2 + C$", "is_correct": false},
    {"key": "D", "text": "$x + C$", "is_correct": false}
  ],
  "correct_choice": "A",
  "answer": "A",
  "embedding_status": "completed"
}
```

Neu output duoc sinh bang LLM, noi dung thuc te co the khac nhau giua cac lan chay.

## Kiem Thu

Chay toan bo test backend:

```bash
.venv\Scripts\python.exe -m pytest -q
```

Tren Linux/macOS:
=======
## Kiểm thử

Chạy toàn bộ backend test:
>>>>>>> 9059a4aa92f9df53e972cff2565089a8bc61290d

```bash
python -m pytest -q
```

<<<<<<< HEAD
Chay test theo nhom:

```bash
.venv\Scripts\python.exe -m pytest tests/api -q
.venv\Scripts\python.exe -m pytest tests/modules/question_quality -q
.venv\Scripts\python.exe -m pytest tests/modules/question_generation -q
.venv\Scripts\python.exe -m pytest tests/modules/semantic_search -q
.venv\Scripts\python.exe -m pytest tests/modules/neuro_symbolic -q
```

Chay lint va build frontend:
=======
Kiểm tra frontend:
>>>>>>> 9059a4aa92f9df53e972cff2565089a8bc61290d

```bash
cd apps/frontend
npm run lint
npm run build
```

<<<<<<< HEAD
Repository co nhieu test trong `tests/api` va `tests/modules`, nhung README nay khong tu cong bo ty le pass vi khong co file ket qua test co san trong repository.

## Danh Gia He Thong AI

Repository co script danh gia chat luong MCQ:

```bash
.venv\Scripts\python.exe scripts\evaluate_mcq_quality.py --pretty
```

Dataset mac dinh:

```text
tests/fixtures/calculus_1_mcq_eval.json
```

Metric script tra ve:

| Metric | Y nghia |
| --- | --- |
| `valid_structure_rate` | Ty le cau hoi co cau truc MCQ hop le. |
| `single_correct_rate` | Ty le cau hoi chi co mot dap an dung. |
| `distractor_distinct_rate` | Ty le distractor khong trung nhau/khong trung dap an dung. |
| `symbolic_correct_rate` | Ty le dap an dung duoc symbolic validator xac nhan tren mau co solver. |
| `taxonomy_valid_rate` | Ty le mau co taxonomy/difficulty hop le. |
| `semantic_duplicate_rate` | Ty le mau bi trung statement theo normalize text. |
| `can_save_rate` | Ty le mau khong co blocking issue. |
| `warning_rate` | Ty le mau co warning. |
| `blocking_issue_rate` | Ty le mau co blocking issue. |

Analytics API cung tinh mot so chi so van hanh nhu `valid_mcq_rate`, `correct_answer_error_rate`, `distractor_error_rate`, `solver_unavailable_rate` va `needs_review_rate`.

## Bao Mat

- Khong commit `.env`, API key, password, token hoac secret that.
- `.env.example` chi nen chua gia tri mau an toan.
- He thong da co dang nhap bang `username` va JWT access token cho muc demo do an.
- Mat khau duoc luu bang PBKDF2-SHA256 hash, khong luu mat khau tho trong database.
- Phan quyen RBAC gom hai vai tro `admin` va `user`.
- `admin` duoc quan ly document, generation, QA, settings va analytics.
- `user` duoc tra cuu search/taxonomy va xem chi tiet cau hoi tren du lieu dung chung.
- Frontend chi an/hien menu theo role; backend van la lop chan quyen chinh.
- Upload chi chap nhan PDF, Markdown va `.markdown`.
- File upload bi gioi han theo `MAX_UPLOAD_SIZE_MB`.
- Output LLM va generated MCQ can duoc kiem tra bang quality service truoc khi luu.
- Search va question detail co tham so `include_answers` de co the an dap an trong mot so view.
- Cau hinh CORS bang `CORS_ALLOW_ORIGINS`, khong nen de origin qua rong trong production.
- Khong tin tuyet doi vao output AI; voi MCQ can doc `validation_report`, `warnings`, `blocking_issues` va `symbolic_checks`.

## Han Che Hien Tai

- Authentication/authorization hien o muc demo do an, chua co refresh token, quen mat khau, audit log hoac giao dien quan ly tai khoan.
- Chua thay file CI/CD trong repository.
- Chua thay license o root repository.
- Ket qua classification/generation/embedding phu thuoc Gemini API va chat luong prompt.
- R2 credentials la bat buoc theo `Settings`, nen local ingestion can cau hinh storage hop le.
- Solver symbolic moi bao phu mot tap dang bai nhat dinh, chu yeu Giai tich 1 trong `CALCULUS_1_SOLVER_CODES`.
- Khong phai moi cau hoi AI generated deu co solver phu hop; khi khong co solver, he thong ghi warning thay vi dam bao symbolic.
- Chua thay monitoring, tracing hoac model versioning production.

## Huong Phat Trien

- Nang cap authentication voi refresh token, doi mat khau, khoa tai khoan va audit log neu trien khai production.
- Bo sung giao dien quan ly tai khoan neu can mo rong ngoai demo.
- Mo rong taxonomy va solver sang nhieu hoc phan Toan hon.
- Bo sung reranking cho semantic search.
- Cai thien human-in-the-loop review workflow cho cau hoi generated.
- Them cache cho embedding/search/generation neu can toi uu chi phi API.
- Bo sung monitoring, logging co cau truc va dashboard production.
- Tu dong hoa evaluation MCQ trong CI khi co pipeline CI/CD.
- Quan ly phien ban prompt, model va dataset evaluation.
- Mo rong symbolic validator de parse/so sanh nhieu dang bieu thuc LaTeX hon.

## Dong Gop

Repository chua co `CONTRIBUTING.md`, co the dung quy trinh chung:

1. Fork repository.
2. Tao branch moi cho thay doi.
3. Cai dat backend/frontend dependency.
4. Chay test lien quan va lint/build frontend neu sua UI.
5. Commit thay doi voi message ro rang.
6. Push branch va tao Pull Request.


## Tac Gia Va Lien He
Email: Snam11122004@gmail.com
=======
Đánh giá chất lượng tập câu hỏi trắc nghiệm:

```bash
python scripts/evaluate_mcq_quality.py --pretty
```

## API Documentation

FastAPI tự động cung cấp tài liệu API tại:

```text
http://localhost:8000/docs
```

Các nhóm API chính:

* Documents
* Questions
* Semantic Search
* Formula Search
* Taxonomy
* Question Generation
* Quality Validation
* Analytics

## Phạm vi hiện tại

Hệ thống hiện tập trung vào các câu hỏi thuộc học phần Giải tích 1. Symbolic solver mới hỗ trợ một số dạng đạo hàm, tích phân và giới hạn đã được định nghĩa trước.

Các kết quả do mô hình AI sinh ra cần được kiểm định trước khi đưa vào ngân hàng câu hỏi chính thức.

## Tác giả

**Sái Hoài Nam**

Sinh viên Khoa Toán – Tin, Đại học Bách khoa Hà Nội.
>>>>>>> 9059a4aa92f9df53e972cff2565089a8bc61290d
