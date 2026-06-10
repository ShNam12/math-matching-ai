# Huong Dan Buoc 13: Trien Khai He Thong Bang Docker, Docker Compose Va Toi Uu Runtime

## 1. Muc tieu

Buoc 13 tiep noi buoc 12. Sau buoc 12, he thong da co:

```text
Backend FastAPI:
  GET /health
  POST /documents/upload
  GET /documents/{id}
  GET /documents/{id}/status
  POST /search/questions
  POST /search/formulas
  POST /generation/questions/preview
  POST /generation/questions/save
  POST /generation/questions/quality

Core modules:
  modules/ingestion
  modules/question_segmenter
  modules/question_storage
  modules/embeddings
  modules/semantic_search
  modules/question_generation
  modules/question_quality

Infra:
  PostgreSQL qua SQLAlchemy asyncpg
  Qdrant qua qdrant-client
  Cloudflare R2 qua boto3
  Gemini generation/embedding/PDF conversion

Frontend:
  apps/frontend Vite React
```

Buoc 13 dua project tu trang thai chay local thu cong sang trang thai co the chay bang Docker Compose, co cau hinh ro rang, co health/readiness check, co workflow build/test/deploy co the lap lai.

MVP cua buoc 13 can dat:

```text
- Co Dockerfile cho backend API.
- Co .dockerignore de image build gon va khong copy secrets/cache.
- Co docker-compose.yml chay duoc:
  - api
  - postgres
  - qdrant
  - frontend neu muon chay UI trong container
- Co .env.example mau cho deploy.
- Settings doc ro cac bien moi truong can co.
- Co readiness endpoint kiem tra DB va Qdrant.
- Co API test cho readiness endpoint bang fake dependency hoac monkeypatch.
- Frontend doc cach tro toi backend bang VITE_API_BASE_URL.
- Co lenh khoi tao database trong container.
- Co checklist test truoc deploy:
  - pytest
  - compileall
  - docker compose build
  - docker compose up
  - curl/Invoke-RestMethod health/readiness
  - Swagger check
- Chua dua Celery/Redis queue vao MVP neu chua can.
```

Buoc 13 chua lam trong MVP:

```text
- Chua autoscale Kubernetes.
- Chua CI/CD GitHub Actions bat buoc.
- Chua monitoring Prometheus/Grafana day du.
- Chua background queue cho embedding/generation.
- Chua zero-downtime migration.
- Chua secret manager production that.
```

Ly do:

```text
- Project hien tai can mot deployment baseline on dinh truoc.
- Docker Compose la du cho demo/do an/local production-like environment.
- Queue/monitoring lon hon nen nen de buoc 14.
```

## 2. Hien trang dau vao

Repo hien tai co:

```text
apps/api/main.py
core/config/settings.py
infra/db/session.py
infra/vector_db/qdrant_client.py
scripts/create_tables.py
scripts/check_question_embedding_sync.py
scripts/test_question_generation.py
scripts/test_question_quality.py
apps/frontend/package.json
apps/frontend/src/services/apiClient.js
requirements.txt
.gitignore
```

Repo hien tai chua thay cac file deploy can them:

```text
Dockerfile
.dockerignore
docker-compose.yml
.env.example
apps/frontend/Dockerfile
apps/frontend/nginx.conf
```

Van de can giai quyet:

```text
1. Backend dang chay local bang uvicorn, chua dong goi container.
2. PostgreSQL/Qdrant phu thuoc nguoi dung bat Docker Desktop thu cong.
3. Settings co qdrant_url mac dinh localhost, nhung trong docker compose phai dung service name qdrant.
4. /health hien chi tra {"status": "ok"}, chua biet DB/Qdrant co san sang khong.
5. Chua co .env.example de nguoi khac biet can dien bien gi.
6. Chua co command khoi tao DB trong container.
7. Frontend co VITE_API_BASE_URL nhung chua co Dockerfile/nginx neu muon trien khai UI.
```

## 3. Nguyen tac thiet ke

### 3.1 Tach health va readiness

Giu:

```text
GET /health
```

de biet app process con song.

Them:

```text
GET /ready
```

de biet cac dependency quan trong san sang:

```text
- PostgreSQL ket noi duoc.
- Qdrant ket noi duoc.
```

Ly do:

```text
- /health dung cho container liveness.
- /ready dung cho deploy/load balancer/manual verification.
- Neu Qdrant/Postgres chet, /health van co the ok nhung /ready phai fail.
```

### 3.2 Docker Compose dung service name thay localhost

Trong host local:

```text
DATABASE_URL=postgresql+asyncpg://...@localhost:5432/...
QDRANT_URL=http://localhost:6333
```

Trong docker compose:

```text
DATABASE_URL=postgresql+asyncpg://...@postgres:5432/...
QDRANT_URL=http://qdrant:6333
```

Ly do:

```text
localhost ben trong api container la chinh container api, khong phai host.
```

### 3.3 Khong dua secrets vao image

Khong copy `.env` vao Docker image.

Dung:

```text
env_file:
  - .env
```

hoac bien moi truong cua server.

### 3.4 Migration MVP dung script hien co

Repo hien co:

```text
scripts/create_tables.py
```

MVP co the dung:

```powershell
docker compose exec api python -m scripts.create_tables
```

Sau MVP moi chuyen sang Alembic migration chuan.

## 4. Cau truc can bo sung va sua

Them:

```text
Dockerfile
.dockerignore
docker-compose.yml
.env.example
tests/api/test_readiness.py
apps/frontend/Dockerfile
apps/frontend/nginx.conf
```

Sua:

```text
core/config/settings.py
apps/api/main.py
```

Khong bat buoc sua:

```text
infra/db/session.py
infra/vector_db/qdrant_client.py
scripts/create_tables.py
```

## 5. Cap nhat settings cho deploy

Mo file:

```text
core/config/settings.py
```

Hien tai:

```python
class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
```

Nen bo sung cac bien runtime:

```python
    app_env: str = "local"
    cors_allow_origins: str = "http://localhost:5173"
```

Va them property:

```python
    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allow_origins.split(",")
            if origin.strip()
        ]
```

Code day du sau khi sua:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    cors_allow_origins: str = "http://localhost:5173"

    database_url: str
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    embedding_model: str = "gemini-embedding-2"
    embedding_dimension: int = 768

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_question_collection: str = "question_embeddings"
    qdrant_formula_collection: str = "formula_embeddings"

    r2_endpoint_url: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    r2_public_base_url: str | None = None

    max_upload_size_mb: int = 40

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allow_origins.split(",")
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
```

Vi sao:

```text
- Khi deploy frontend khong con nhat thiet o localhost:5173.
- Docker Compose/frontend nginx co the dung http://localhost:8080.
- Production co the dung domain that.
```

## 6. Them readiness endpoint

Mo file:

```text
apps/api/main.py
```

Hien tai CORS dang hard-code:

```python
allow_origins=["http://localhost:5173"],
```

Sua thanh:

```python
allow_origins=settings.cors_origins,
```

Can them import:

```python
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.settings import settings
from infra.db.session import get_db_session
from infra.vector_db.qdrant_client import create_qdrant_client
```

Them endpoint:

```python
@app.get("/ready", tags=["health"])
async def readiness_check(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    checks: dict[str, bool] = {
        "database": False,
        "qdrant": False,
    }

    await session.execute(text("SELECT 1"))
    checks["database"] = True

    client = create_qdrant_client()
    try:
        await client.get_collections()
        checks["qdrant"] = True
    finally:
        await client.close()

    return {
        "status": "ready",
        "checks": checks,
    }
```

File `apps/api/main.py` sau khi sua nen co dang:

```python
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.endpoints.documents import router as documents_router
from apps.api.v1.endpoints.generation import router as generation_router
from apps.api.v1.endpoints.search import router as search_router
from core.config.settings import settings
from infra.db.session import get_db_session
from infra.vector_db.qdrant_client import create_qdrant_client


app = FastAPI(
    title="AI Matching API",
    description="Backend API for document ingestion and processing workflows.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"message": "AI Matching API is running"}


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
async def readiness_check(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    checks: dict[str, bool] = {
        "database": False,
        "qdrant": False,
    }

    await session.execute(text("SELECT 1"))
    checks["database"] = True

    client = create_qdrant_client()
    try:
        await client.get_collections()
        checks["qdrant"] = True
    finally:
        await client.close()

    return {
        "status": "ready",
        "checks": checks,
    }


app.include_router(documents_router)
app.include_router(search_router)
app.include_router(generation_router)
```

Ghi chu:

```text
- Neu DB hoac Qdrant loi, FastAPI se tra 500. Chap nhan cho MVP readiness.
- Sau nay co the bat exception va tra 503 chi tiet hon.
```

## 7. Test readiness endpoint

Tao file:

```text
tests/api/test_readiness.py
```

Them:

```python
from fastapi.testclient import TestClient

from apps.api import main as api_main
from apps.api.main import app


class FakeResult:
    pass


class FakeSession:
    def __init__(self) -> None:
        self.executed = []

    async def execute(self, statement):
        self.executed.append(statement)
        return FakeResult()


class FakeQdrantClient:
    def __init__(self) -> None:
        self.closed = False

    async def get_collections(self):
        return []

    async def close(self) -> None:
        self.closed = True


def test_health_check_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check_returns_dependency_status(monkeypatch) -> None:
    fake_session = FakeSession()
    fake_qdrant = FakeQdrantClient()

    async def override_db_session():
        yield fake_session

    app.dependency_overrides[api_main.get_db_session] = override_db_session
    monkeypatch.setattr(
        api_main,
        "create_qdrant_client",
        lambda: fake_qdrant,
    )

    try:
        client = TestClient(app)
        response = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {
            "database": True,
            "qdrant": True,
        },
    }
    assert fake_session.executed
    assert fake_qdrant.closed is True
```

Chay:

```powershell
pytest tests/api/test_readiness.py -q
pytest tests/api -q
```

Ky vong:

```text
2 passed
tat ca tests/api pass
```

## 8. Them .dockerignore

Tao file:

```text
.dockerignore
```

Them:

```dockerignore
.git
.pytest_cache
.venv
venv
env
__pycache__
*.pyc
*.pyo
*.pyd

.env
.env.*
!.env.example

data
docker-data
postgres-data
qdrant-data
redis-data
storage
logs
*.log

apps/frontend/node_modules
apps/frontend/dist

.vscode
.idea
```

Vi sao:

```text
- Khong dua virtualenv, node_modules, data local, secrets vao Docker image.
- Image nhe hon va build nhanh hon.
```

## 9. Them Dockerfile backend

Tao file root:

```text
Dockerfile
```

Them:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY apps ./apps
COPY core ./core
COPY infra ./infra
COPY modules ./modules
COPY scripts ./scripts

EXPOSE 8000

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Ghi chu:

```text
- MVP copy source code truc tiep.
- Khong copy Plan/tests vao image runtime de image gon.
- Neu can chay test trong container, co the them target rieng sau.
```

## 10. Them .env.example

Tao file:

```text
.env.example
```

Them:

```env
APP_ENV=local
CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:8080

DATABASE_URL=postgresql+asyncpg://ai_matching:ai_matching_password@localhost:5432/ai_matching

GEMINI_API_KEY=replace-me
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-2
EMBEDDING_DIMENSION=768

QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_QUESTION_COLLECTION=question_embeddings
QDRANT_FORMULA_COLLECTION=formula_embeddings

R2_ENDPOINT_URL=https://replace-me.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=replace-me
R2_SECRET_ACCESS_KEY=replace-me
R2_BUCKET_NAME=replace-me
R2_PUBLIC_BASE_URL=

MAX_UPLOAD_SIZE_MB=40
```

Them ghi chu trong huong dan deploy:

```text
- Khi chay Docker Compose, DATABASE_URL nen dung host postgres.
- Khi chay Docker Compose, QDRANT_URL nen dung http://qdrant:6333.
```

Khong commit `.env` that.

## 11. Them docker-compose.yml

Tao file:

```text
docker-compose.yml
```

Them:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: ai-matching-postgres
    environment:
      POSTGRES_DB: ai_matching
      POSTGRES_USER: ai_matching
      POSTGRES_PASSWORD: ai_matching_password
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ai_matching -d ai_matching"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:v1.12.4
    container_name: ai-matching-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant-data:/qdrant/storage
    healthcheck:
      test:
        [
          "CMD-SHELL",
          "timeout 5 bash -c '</dev/tcp/127.0.0.1/6333' || exit 1",
        ]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-matching-api
    env_file:
      - .env
    environment:
      APP_ENV: docker
      DATABASE_URL: postgresql+asyncpg://ai_matching:ai_matching_password@postgres:5432/ai_matching
      QDRANT_URL: http://qdrant:6333
      CORS_ALLOW_ORIGINS: http://localhost:5173,http://localhost:8080
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_started

volumes:
  postgres-data:
  qdrant-data:
```

Ghi chu:

```text
- `env_file: .env` lay secrets Gemini/R2.
- `environment` override DATABASE_URL/QDRANT_URL de dung network noi bo Docker.
- `depends_on` khong thay the migration; van can chay create_tables.
```

Neu Qdrant image khong co `bash` trong healthcheck, co the bo healthcheck Qdrant trong MVP:

```yaml
    healthcheck:
      test: ["CMD", "true"]
```

hoac chi giu `depends_on: qdrant`.

## 12. Khoi tao database trong container

Sau khi compose up:

```powershell
docker compose up -d --build
```

Chay:

```powershell
docker compose exec api python -m scripts.create_tables
```

Kiem tra:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/ready
```

Ky vong:

```json
{
  "status": "ok"
}
```

va:

```json
{
  "status": "ready",
  "checks": {
    "database": true,
    "qdrant": true
  }
}
```

## 13. Them Dockerfile frontend

Neu muon deploy frontend trong container, tao:

```text
apps/frontend/Dockerfile
```

Them:

```dockerfile
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
```

Tao:

```text
apps/frontend/nginx.conf
```

Them:

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Cap nhat `docker-compose.yml` them service frontend:

```yaml
  frontend:
    build:
      context: ./apps/frontend
      dockerfile: Dockerfile
      args:
        VITE_API_BASE_URL: http://localhost:8000
    container_name: ai-matching-frontend
    ports:
      - "8080:80"
    depends_on:
      - api
```

Mo:

```text
http://localhost:8080
```

Vi sao:

```text
- Vite build can biet API base URL tai thoi diem build.
- Nginx phuc vu static dist gon hon chay vite dev server.
```

## 14. Cap nhat frontend API base URL khi chay local

File hien tai:

```text
apps/frontend/src/services/apiClient.js
```

Dang co:

```javascript
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
```

Phan nay da dung.

Khi chay local:

```powershell
cd apps/frontend
npm run dev
```

Co the tao file:

```text
apps/frontend/.env.example
```

Them:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Neu can chay frontend local voi API trong container, khong can sua gi vi API expose port 8000.

## 15. API performance va runtime guard nen them sau khi compose chay on

### 15.1 Van de hien tai

Mot so endpoint co the cham:

```text
POST /generation/questions/preview
POST /generation/questions/save
POST /generation/questions/quality
POST /search/questions
POST /search/formulas
```

Ly do:

```text
- Goi Gemini generation/embedding.
- Save re-embed ca document.
- Quality semantic duplicate goi embedding + Qdrant.
```

### 15.2 De xuat MVP

Chua dua queue vao buoc 13, nhung can cau hinh worker va timeout server hop ly.

Trong Dockerfile CMD co the giu:

```dockerfile
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Neu deploy production nho, co the dung:

```dockerfile
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

Can luu y:

```text
- Nhieu workers co the tang memory.
- Gemini quota van la bottleneck.
- Save endpoint van sync embedding, nen user co the doi lau.
```

Sau MVP:

```text
- Them Redis + Celery/RQ cho embedding background.
- Save generated question chi mark pending, worker embed sau.
- Them endpoint job status.
```

## 16. Test Docker Compose

Chay:

```powershell
docker compose config
docker compose build
docker compose up -d
docker compose ps
```

Khoi tao DB:

```powershell
docker compose exec api python -m scripts.create_tables
```

Kiem tra API:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/ready
```

Kiem tra Swagger:

```text
http://localhost:8000/docs
```

Can thay:

```text
documents
search
generation
health
```

Kiem tra Qdrant:

```powershell
Invoke-RestMethod http://localhost:6333/collections
```

Kiem tra logs:

```powershell
docker compose logs api --tail=100
docker compose logs postgres --tail=50
docker compose logs qdrant --tail=50
```

Dung stack:

```powershell
docker compose down
```

Neu muon xoa data volume local:

```powershell
docker compose down -v
```

Can can than voi `-v` vi se xoa database/Qdrant local.

## 17. Test tong the truoc deploy

Chay local:

```powershell
pytest tests/modules/question_quality -q
pytest tests/modules/question_generation -q
pytest tests/api -q
pytest tests/modules -q
pytest -q
python -m compileall apps/api core infra modules tests scripts
```

Chay frontend:

```powershell
cd apps/frontend
npm run lint
npm run build
```

Quay ve root:

```powershell
cd ..\..
```

Chay Docker:

```powershell
docker compose build
docker compose up -d
docker compose exec api python -m scripts.create_tables
Invoke-RestMethod http://localhost:8000/ready
```

Neu co sample document da sync:

```powershell
docker compose exec api python -m scripts.check_question_embedding_sync
```

## 18. Loi thuong gap

### 18.1 API container khong ket noi duoc PostgreSQL

Loi thuong gap:

```text
Connection refused localhost:5432
```

Nguyen nhan:

```text
DATABASE_URL trong container dang tro localhost.
```

Sua:

```env
DATABASE_URL=postgresql+asyncpg://ai_matching:ai_matching_password@postgres:5432/ai_matching
```

### 18.2 API container khong ket noi duoc Qdrant

Loi:

```text
All connection attempts failed
```

Nguyen nhan:

```text
QDRANT_URL dang la http://localhost:6333 trong container.
```

Sua:

```env
QDRANT_URL=http://qdrant:6333
```

### 18.3 Pydantic Settings bao thieu bien R2/Gemini

Loi:

```text
Field required: gemini_api_key/r2_endpoint_url/...
```

Nguyen nhan:

```text
.env chua co day du bien bat buoc.
```

Sua:

```text
Copy .env.example thanh .env va dien gia tri that.
```

### 18.4 /ready tra 500

Kiem tra:

```powershell
docker compose logs api --tail=100
```

Neu DB loi:

```powershell
docker compose ps
docker compose logs postgres --tail=100
```

Neu Qdrant loi:

```powershell
docker compose logs qdrant --tail=100
Invoke-RestMethod http://localhost:6333/collections
```

### 18.5 Frontend goi sai API URL

Neu frontend tai `http://localhost:8080` nhung request sai backend, kiem tra build arg:

```yaml
args:
  VITE_API_BASE_URL: http://localhost:8000
```

Va CORS:

```env
CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:8080
```

### 18.6 Database chua co bang

Loi:

```text
relation "documents" does not exist
```

Chay:

```powershell
docker compose exec api python -m scripts.create_tables
```

## 19. Mo rong sau MVP

### 19.1 Dung Alembic migration that

Repo da co dependency:

```text
alembic
```

Sau MVP nen them:

```text
alembic.ini
alembic/env.py
alembic/versions/
```

Command deploy:

```powershell
docker compose exec api alembic upgrade head
```

Thay cho:

```powershell
python -m scripts.create_tables
```

### 19.2 Queue cho embedding/generation

Them service:

```text
redis
worker
```

Flow moi:

```text
save generated question
-> luu DB embedding_status=pending
-> enqueue embedding job
-> worker embed document/question
-> API tra nhanh hon
```

### 19.3 Monitoring buoc 14

Them:

```text
Prometheus
Grafana
structured logging
request id middleware
metrics endpoint
```

### 19.4 Production security

Can them:

```text
- HTTPS reverse proxy.
- Secret manager.
- Rate limit endpoint generation/search.
- Auth cho upload/generation/save.
- Backup Postgres volume.
- Backup/export Qdrant collections.
```

## 20. Thu tu trien khai khuyen nghi

Lam lan luot:

```text
1. Cap nhat core/config/settings.py them APP_ENV va CORS_ALLOW_ORIGINS.
2. Cap nhat apps/api/main.py dung settings.cors_origins.
3. Them GET /ready kiem tra PostgreSQL va Qdrant.
4. Viet tests/api/test_readiness.py.
5. Chay pytest tests/api/test_readiness.py -q.
6. Chay pytest tests/api -q.
7. Tao .dockerignore.
8. Tao Dockerfile backend.
9. Tao .env.example.
10. Tao docker-compose.yml voi postgres/qdrant/api.
11. Chay docker compose config.
12. Chay docker compose build.
13. Chay docker compose up -d.
14. Chay docker compose exec api python -m scripts.create_tables.
15. Test /health va /ready.
16. Test Swagger.
17. Neu can frontend container, tao apps/frontend/Dockerfile va nginx.conf.
18. Them frontend service vao docker-compose.yml.
19. Chay npm run lint va npm run build trong apps/frontend.
20. Chay pytest -q.
21. Chay python -m compileall apps/api core infra modules tests scripts.
22. Ghi lai command deploy vao README hoac file Plan tiep theo.
```

## 21. Tieu chi hoan thanh

Buoc 13 MVP hoan tat khi:

```text
1. Co Dockerfile backend.
2. Co .dockerignore.
3. Co docker-compose.yml chay postgres/qdrant/api.
4. Co .env.example day du bien can thiet.
5. API container start duoc bang docker compose.
6. Chay duoc scripts.create_tables trong api container.
7. GET /health tra 200.
8. GET /ready tra 200 voi database=true va qdrant=true.
9. Swagger hien du endpoints documents/search/generation.
10. CORS doc ro cho localhost:5173 va localhost:8080.
11. Neu them frontend container, http://localhost:8080 load duoc UI.
12. pytest tests/api pass.
13. pytest tests/modules pass.
14. pytest -q pass.
15. compileall toan project khong loi.
16. docker compose logs api khong co startup exception.
17. Co huong dan xu ly loi ket noi DB/Qdrant.
```

Sau buoc 13, he thong san sang cho:

```text
- Buoc 14: monitoring, logging, metrics, backup, support.
- Them queue/worker de toi uu embedding/generation.
- Them CI/CD de auto test va build image.
```
