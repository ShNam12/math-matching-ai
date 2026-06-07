# Huong Dan Buoc 11: Sinh Cau Hoi Moi Dua Tren Cau Hoi Tuong Tu

## 1. Muc tieu

Buoc 11 bo sung kha nang sinh cau hoi moi dua tren cau hoi da co trong he thong.

Sau buoc 10, he thong da co:

```text
POST /search/questions
POST /search/formulas
```

va co the tim cau hoi/cau truc cong thuc tuong tu trong:

```text
PostgreSQL questions
Qdrant question_embeddings
Qdrant formula_embeddings
```

Buoc 11 tao luong generation dau tien:

```text
POST /generation/questions/preview
source_question_id
generation_count
constraints
 -> PostgreSQL lay cau hoi goc
 -> tao prompt
 -> Gemini sinh JSON cau hoi moi
 -> parse + validate
 -> duplicate check co ban
 -> response preview
```

Va luong luu cau hoi da sinh:

```text
POST /generation/questions/save
source_question_id
generated question payload
 -> validate payload
 -> luu vao PostgreSQL questions
 -> extract formulas
 -> embedding_status pending
 -> goi embedding service cho document
 -> Qdrant question_embeddings + formula_embeddings duoc dong bo lai
 -> response generated question
```

Ket qua can dat:

```text
- Co module modules/question_generation.
- Sinh duoc cau hoi moi tu mot question_id goc.
- Prompt yeu cau Gemini tra JSON co statement, solution, answer, formulas, difficulty, skills.
- Co validate JSON output.
- Co duplicate check co ban dua tren normalized statement.
- Co API POST /generation/questions/preview.
- Co API POST /generation/questions/save.
- Cau hoi da save duoc luu vao PostgreSQL questions.
- Cau hoi da save duoc embed lai vao Qdrant thong qua QuestionEmbeddingService.
- Co unit test cho service generation.
- Co unit test cho repository create_generated_question.
- Co API test endpoint generation preview/save voi fake generator.
- Co script integration test voi PostgreSQL + Qdrant + Gemini.
```

Buoc 11 MVP chua lam:

```text
- Chua tao bang generated_questions rieng.
- Chua co workflow review/approve rieng.
- Chua co symbolic validation bang SymPy.
- Chua cham diem do kho bang model rieng.
- Chua sinh de thi nhieu cau.
- Chua frontend generation.
- Chua queue/background job cho generation.
```

Ly do chua tao bang rieng trong MVP:

```text
- Repo hien tai da co bang questions va embedding pipeline on dinh.
- Them bang rieng can migration va thay doi nhieu API/repository.
- MVP buoc 11 uu tien tao duoc cau hoi moi, luu duoc, embed duoc.
- Sau nay co the tach generated_questions khi them review workflow.
```

## 2. Hien trang dau vao

He thong hien co cac thanh phan quan trong:

```text
infra/db/models.py
  Document
  Question

infra/db/repositories/questions.py
  replace_for_document(...)
  list_by_document(...)
  get_question(...)
  list_by_ids(...)
  mark_embedding_pending_for_document(...)
  mark_embedding_completed_for_document(...)
  mark_embedding_failed_for_document(...)

modules/question_segmenter/formula_extractor.py
  extract_formulas(...)
  normalize_formula(...)

modules/embeddings/service.py
  QuestionEmbeddingService.embed_document(...)

modules/semantic_search/service.py
  search_questions(...)
  search_formulas(...)

apps/api/main.py
  include_router(documents_router)
  include_router(search_router)
```

Bang `questions` hien co:

```text
id
document_id
sequence_number
marker
marker_number
statement
solution
answer
formulas
subject
chapter
difficulty
skills
embedding_status
embedding_model
embedding_dimension
embedding_error
embedded_at
created_at
updated_at
```

Buoc 11 se luu cau hoi sinh moi vao cung bang `questions`.

## 3. Nguyen tac thiet ke

### 3.1 Generation tach khoi semantic_search

Khong nen nhet generation vao:

```text
modules/semantic_search
```

Vi:

```text
- Search la lay ket qua da co.
- Generation la tao noi dung moi bang LLM.
- Generation can prompt builder, JSON parser, validator rieng.
- Sau nay generation co workflow review, quality check, save/publish rieng.
```

Tao module moi:

```text
modules/question_generation/
```

### 3.2 Preview truoc, save sau

Khong nen cu goi API la luu ngay tat ca cau hoi sinh ra.

Nen co 2 endpoint:

```text
POST /generation/questions/preview
POST /generation/questions/save
```

Ly do:

```text
- Gemini co the sinh cau hoi chua dat chat luong.
- Nguoi dung/API client can xem truoc.
- Save can ghi DB va re-embed document, ton tai nguyen hon preview.
```

### 3.3 Output Gemini bat buoc la JSON

Khong nen parse free-form text.

Prompt phai yeu cau output:

```json
{
  "items": [
    {
      "statement": "...",
      "solution": "...",
      "answer": "...",
      "difficulty": "...",
      "skills": ["..."]
    }
  ]
}
```

Formula se duoc extract lai tu `statement`, `solution`, `answer` bang:

```python
extract_formulas(...)
```

### 3.4 Save xong phai re-embed

Khi them cau hoi moi vao `questions`, Qdrant chua biet cau hoi moi.

Nen sau khi save can goi:

```python
QuestionEmbeddingService.embed_document(document_id)
```

Ham nay se:

```text
- Lay tat ca questions cua document.
- Tao question vectors.
- Tao formula vectors.
- replace_for_document vao Qdrant.
- mark embedding_status completed/failed.
```

MVP chap nhan re-embed ca document vi corpus dang nho.

## 4. Cau truc can bo sung va sua

Them:

```text
modules/question_generation/
  __init__.py
  schemas.py
  prompt_builder.py
  gemini_generator.py
  service.py

apps/api/v1/models/generation.py
apps/api/v1/endpoints/generation.py

tests/modules/question_generation/
  __init__.py
  test_prompt_builder.py
  test_service.py

tests/api/test_generation.py

scripts/test_question_generation.py
```

Sua:

```text
infra/db/repositories/questions.py
apps/api/main.py
```

Khong bat buoc sua:

```text
infra/db/models.py
```

Ly do:

```text
- MVP luu generated question vao bang questions hien co.
- Khong can migration database trong buoc 11 MVP.
```

## 5. Them schema generation

Tao folder:

```text
modules/question_generation/
```

Tao file:

```text
modules/question_generation/schemas.py
```

Them:

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class GenerationConstraints:
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] = field(default_factory=list)
    preserve_formula_style: bool = True
    avoid_duplicate: bool = True


@dataclass(frozen=True)
class GeneratedQuestionCandidate:
    statement: str
    solution: str | None
    answer: str | None
    subject: str | None
    chapter: str | None
    difficulty: str | None
    skills: list[str]
    formulas: list[dict[str, str]]
    quality_warnings: list[str]


@dataclass(frozen=True)
class QuestionGenerationPreview:
    source_question_id: str
    candidates: list[GeneratedQuestionCandidate]
```

Y nghia:

```text
GenerationConstraints:
  Dieu kien yeu cau khi sinh cau hoi.

GeneratedQuestionCandidate:
  Mot cau hoi moi da duoc parse va validate.

QuestionGenerationPreview:
  Ket qua preview tra ve cho API.
```

## 6. Them prompt builder

Tao file:

```text
modules/question_generation/prompt_builder.py
```

Them:

```python
from infra.db.models import Question
from modules.question_generation.schemas import GenerationConstraints


def build_question_generation_prompt(
    *,
    source_question: Question,
    generation_count: int,
    constraints: GenerationConstraints,
) -> str:
    subject = constraints.subject or source_question.subject or "unknown"
    chapter = constraints.chapter or source_question.chapter or "unknown"
    difficulty = constraints.difficulty or source_question.difficulty or "same as source"
    skills = constraints.skills or source_question.skills

    skills_text = ", ".join(skills) if skills else "same as source"

    return f"""
You are an expert mathematics question generator.

Generate {generation_count} new mathematics questions based on the source question.

Requirements:
- Keep the same mathematical topic.
- Do not copy the source statement verbatim.
- Keep the question solvable.
- Use clear LaTeX for formulas.
- Return valid JSON only.
- Do not wrap JSON in markdown fences.
- The JSON must have exactly this shape:
{{
  "items": [
    {{
      "statement": "question statement with LaTeX",
      "solution": "solution or null",
      "answer": "final answer or null",
      "difficulty": "easy|medium|hard or null",
      "skills": ["skill 1", "skill 2"]
    }}
  ]
}}

Target metadata:
- subject: {subject}
- chapter: {chapter}
- difficulty: {difficulty}
- skills: {skills_text}
- preserve_formula_style: {constraints.preserve_formula_style}
- avoid_duplicate: {constraints.avoid_duplicate}

Source question:
Marker: {source_question.marker} {source_question.marker_number}
Statement:
{source_question.statement}

Solution:
{source_question.solution or ""}

Answer:
{source_question.answer or ""}
""".strip()
```

Vi sao prompt can chat:

```text
- API/service can parse JSON on dinh.
- Khong nen de Gemini tra markdown tu do.
- Statement/solution/answer la cac field he thong da co san.
```

## 7. Them Gemini generator

Tao file:

```text
modules/question_generation/gemini_generator.py
```

Them:

```python
from typing import Protocol

from google import genai

from core.config.settings import settings


class QuestionGenerator(Protocol):
    def generate_text(self, prompt: str) -> str:
        ...


class GeminiQuestionGenerator:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def generate_text(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Generation prompt must not be empty")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        text = getattr(response, "text", None)

        if not text or not text.strip():
            raise ValueError("Gemini returned empty generation output")

        return text.strip()
```

Luu y:

```text
- Buoc 11 dung settings.gemini_model, khong dung settings.embedding_model.
- gemini_model hien tai mac dinh la gemini-2.5-flash.
```

## 8. Them service generation

Tao file:

```text
modules/question_generation/service.py
```

Them:

```python
import asyncio
import json
import re
from typing import Protocol

from infra.db.models import Question
from infra.db.repositories.questions import QuestionRepository
from modules.question_generation.prompt_builder import (
    build_question_generation_prompt,
)
from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    GenerationConstraints,
    QuestionGenerationPreview,
)
from modules.question_segmenter.formula_extractor import (
    FormulaSource,
    extract_formulas,
)


class TextQuestionGenerator(Protocol):
    def generate_text(self, prompt: str) -> str:
        ...


def _normalize_for_duplicate_check(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _loads_generation_json(raw_text: str) -> dict:
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    return json.loads(cleaned)


class QuestionGenerationService:
    def __init__(
        self,
        *,
        question_repository: QuestionRepository,
        generator: TextQuestionGenerator,
    ) -> None:
        self.question_repository = question_repository
        self.generator = generator

    async def preview_questions(
        self,
        *,
        source_question_id: str,
        generation_count: int = 3,
        constraints: GenerationConstraints | None = None,
    ) -> QuestionGenerationPreview:
        if generation_count < 1 or generation_count > 10:
            raise ValueError("Generation count must be between 1 and 10")

        source_question = await self.question_repository.get_question(
            source_question_id
        )

        if source_question is None:
            raise ValueError("Source question not found")

        constraints = constraints or GenerationConstraints()

        prompt = build_question_generation_prompt(
            source_question=source_question,
            generation_count=generation_count,
            constraints=constraints,
        )

        raw_output = await asyncio.to_thread(
            self.generator.generate_text,
            prompt,
        )

        payload = _loads_generation_json(raw_output)
        items = payload.get("items")

        if not isinstance(items, list):
            raise ValueError("Generation output must contain an items list")

        existing_questions = await self.question_repository.list_by_document(
            source_question.document_id
        )
        existing_statements = {
            _normalize_for_duplicate_check(question.statement)
            for question in existing_questions
        }

        candidates: list[GeneratedQuestionCandidate] = []

        for item in items[:generation_count]:
            candidate = self._parse_candidate(
                item=item,
                source_question=source_question,
                existing_statements=existing_statements,
                constraints=constraints,
            )

            candidates.append(candidate)

        return QuestionGenerationPreview(
            source_question_id=source_question.id,
            candidates=candidates,
        )

    def _parse_candidate(
        self,
        *,
        item: object,
        source_question: Question,
        existing_statements: set[str],
        constraints: GenerationConstraints,
    ) -> GeneratedQuestionCandidate:
        if not isinstance(item, dict):
            raise ValueError("Each generated item must be an object")

        statement = str(item.get("statement") or "").strip()

        if not statement:
            raise ValueError("Generated statement must not be empty")

        solution_value = item.get("solution")
        answer_value = item.get("answer")
        difficulty_value = item.get("difficulty")
        skills_value = item.get("skills")

        solution = (
            str(solution_value).strip()
            if solution_value is not None and str(solution_value).strip()
            else None
        )
        answer = (
            str(answer_value).strip()
            if answer_value is not None and str(answer_value).strip()
            else None
        )
        difficulty = (
            str(difficulty_value).strip()
            if difficulty_value is not None and str(difficulty_value).strip()
            else constraints.difficulty or source_question.difficulty
        )

        skills = (
            [str(skill).strip() for skill in skills_value if str(skill).strip()]
            if isinstance(skills_value, list)
            else constraints.skills or source_question.skills
        )

        formulas = []
        for extracted in extract_formulas(
            statement,
            source=FormulaSource.statement,
        ):
            formulas.append(extracted.model_dump())

        for extracted in extract_formulas(
            solution,
            source=FormulaSource.solution,
        ):
            formulas.append(extracted.model_dump())

        for extracted in extract_formulas(
            answer,
            source=FormulaSource.answer,
        ):
            formulas.append(extracted.model_dump())

        quality_warnings: list[str] = []

        if _normalize_for_duplicate_check(statement) in existing_statements:
            quality_warnings.append("duplicate_statement")

        if constraints.avoid_duplicate and quality_warnings:
            quality_warnings.append("review_required")

        if not formulas:
            quality_warnings.append("no_formula_detected")

        return GeneratedQuestionCandidate(
            statement=statement,
            solution=solution,
            answer=answer,
            subject=constraints.subject or source_question.subject,
            chapter=constraints.chapter or source_question.chapter,
            difficulty=difficulty,
            skills=skills,
            formulas=formulas,
            quality_warnings=quality_warnings,
        )
```

Ghi chu:

```text
- Service nay chi preview, chua save.
- Duplicate check o MVP chi so sanh exact normalized statement trong cung document.
- Formula extraction dung lai logic cua question_segmenter.
```

## 9. Export module question_generation

Tao file:

```text
modules/question_generation/__init__.py
```

Them:

```python
from modules.question_generation.gemini_generator import GeminiQuestionGenerator
from modules.question_generation.schemas import (
    GeneratedQuestionCandidate,
    GenerationConstraints,
    QuestionGenerationPreview,
)
from modules.question_generation.service import QuestionGenerationService

__all__ = [
    "GeneratedQuestionCandidate",
    "GenerationConstraints",
    "GeminiQuestionGenerator",
    "QuestionGenerationPreview",
    "QuestionGenerationService",
]
```

## 10. Them repository method de save generated question

Mo:

```text
infra/db/repositories/questions.py
```

Them import:

```python
from sqlalchemy import delete, func, select, update
```

Hien tai file dang import:

```python
from sqlalchemy import delete, select, update
```

Sua thanh:

```python
from sqlalchemy import delete, func, select, update
```

Them method sau vao class `QuestionRepository`, sau `get_question` hoac sau `list_by_ids`:

```python
    async def create_generated_question(
        self,
        *,
        source_question: Question,
        statement: str,
        solution: str | None,
        answer: str | None,
        formulas: list[dict[str, str]],
        subject: str | None,
        chapter: str | None,
        difficulty: str | None,
        skills: list[str],
    ) -> Question:
        result = await self.session.execute(
            select(func.max(Question.sequence_number)).where(
                Question.document_id == source_question.document_id
            )
        )
        max_sequence_number = result.scalar_one() or 0
        sequence_number = int(max_sequence_number) + 1

        question = Question(
            document_id=source_question.document_id,
            sequence_number=sequence_number,
            marker="Generated",
            marker_number=str(sequence_number),
            statement=statement,
            solution=solution,
            answer=answer,
            formulas=formulas,
            subject=subject,
            chapter=chapter,
            difficulty=difficulty,
            skills=skills,
            embedding_status="pending",
            embedding_model=None,
            embedding_dimension=None,
            embedding_error=None,
            embedded_at=None,
        )

        self.session.add(question)
        await self.session.commit()
        await self.session.refresh(question)

        return question
```

Vi sao dung sequence_number max + 1:

```text
- Bang questions co unique constraint (document_id, sequence_number).
- Generated question can nam trong cung document voi source question.
- max + 1 tranh trung sequence_number.
```

Ghi chu:

```text
MVP marker = "Generated".
Sau nay co the them marker = "Generated from Bai 28" neu co cot rieng parent_question_id.
```

## 11. Them save method vao service generation

Mo:

```text
modules/question_generation/service.py
```

Them method sau vao class `QuestionGenerationService`, sau `preview_questions`:

```python
    async def save_generated_question(
        self,
        *,
        source_question_id: str,
        candidate: GeneratedQuestionCandidate,
    ) -> Question:
        source_question = await self.question_repository.get_question(
            source_question_id
        )

        if source_question is None:
            raise ValueError("Source question not found")

        if not candidate.statement.strip():
            raise ValueError("Generated statement must not be empty")

        existing_questions = await self.question_repository.list_by_document(
            source_question.document_id
        )
        existing_statements = {
            _normalize_for_duplicate_check(question.statement)
            for question in existing_questions
        }

        if _normalize_for_duplicate_check(candidate.statement) in existing_statements:
            raise ValueError("Generated question duplicates an existing question")

        return await self.question_repository.create_generated_question(
            source_question=source_question,
            statement=candidate.statement,
            solution=candidate.solution,
            answer=candidate.answer,
            formulas=candidate.formulas,
            subject=candidate.subject,
            chapter=candidate.chapter,
            difficulty=candidate.difficulty,
            skills=candidate.skills,
        )
```

Can them import `Question` o dau file neu chua co:

```python
from infra.db.models import Question
```

File service da co import nay o muc 8.

## 12. API models cho generation

Tao file:

```text
apps/api/v1/models/generation.py
```

Them:

```python
from pydantic import BaseModel, Field


class GenerationConstraintsModel(BaseModel):
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str] = Field(default_factory=list)
    preserve_formula_style: bool = True
    avoid_duplicate: bool = True


class QuestionGenerationPreviewRequest(BaseModel):
    source_question_id: str = Field(min_length=1)
    generation_count: int = Field(default=3, ge=1, le=10)
    constraints: GenerationConstraintsModel = Field(
        default_factory=GenerationConstraintsModel
    )


class GeneratedQuestionItem(BaseModel):
    statement: str
    solution: str | None = None
    answer: str | None = None
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str]
    formulas: list[dict[str, str]]
    quality_warnings: list[str]


class QuestionGenerationPreviewResponse(BaseModel):
    source_question_id: str
    candidates: list[GeneratedQuestionItem]


class QuestionGenerationSaveRequest(BaseModel):
    source_question_id: str = Field(min_length=1)
    candidate: GeneratedQuestionItem


class QuestionGenerationSaveResponse(BaseModel):
    question_id: str
    document_id: str
    sequence_number: int
    marker: str
    marker_number: str
    statement: str
    solution: str | None = None
    answer: str | None = None
    subject: str | None = None
    chapter: str | None = None
    difficulty: str | None = None
    skills: list[str]
    formulas: list[dict[str, str]]
    embedding_status: str
```

## 13. API endpoint generation

Tao file:

```text
apps/api/v1/endpoints/generation.py
```

Them:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.v1.models.generation import (
    GeneratedQuestionItem,
    QuestionGenerationPreviewRequest,
    QuestionGenerationPreviewResponse,
    QuestionGenerationSaveRequest,
    QuestionGenerationSaveResponse,
)
from core.config.settings import settings
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import get_db_session
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder
from modules.embeddings.service import QuestionEmbeddingService
from modules.question_generation import (
    GeminiQuestionGenerator,
    GenerationConstraints,
    QuestionGenerationService,
)
from modules.question_generation.schemas import GeneratedQuestionCandidate


router = APIRouter(prefix="/generation", tags=["generation"])


def _to_constraints(request: QuestionGenerationPreviewRequest) -> GenerationConstraints:
    constraints = request.constraints

    return GenerationConstraints(
        subject=constraints.subject,
        chapter=constraints.chapter,
        difficulty=constraints.difficulty,
        skills=constraints.skills,
        preserve_formula_style=constraints.preserve_formula_style,
        avoid_duplicate=constraints.avoid_duplicate,
    )


def _to_item(candidate: GeneratedQuestionCandidate) -> GeneratedQuestionItem:
    return GeneratedQuestionItem(
        statement=candidate.statement,
        solution=candidate.solution,
        answer=candidate.answer,
        subject=candidate.subject,
        chapter=candidate.chapter,
        difficulty=candidate.difficulty,
        skills=candidate.skills,
        formulas=candidate.formulas,
        quality_warnings=candidate.quality_warnings,
    )


@router.post(
    "/questions/preview",
    response_model=QuestionGenerationPreviewResponse,
)
async def preview_generated_questions(
    request: QuestionGenerationPreviewRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationPreviewResponse:
    service = QuestionGenerationService(
        question_repository=QuestionRepository(session),
        generator=GeminiQuestionGenerator(),
    )

    try:
        preview = await service.preview_questions(
            source_question_id=request.source_question_id,
            generation_count=request.generation_count,
            constraints=_to_constraints(request),
        )

        return QuestionGenerationPreviewResponse(
            source_question_id=preview.source_question_id,
            candidates=[
                _to_item(candidate)
                for candidate in preview.candidates
            ],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/questions/save",
    response_model=QuestionGenerationSaveResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_generated_question(
    request: QuestionGenerationSaveRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationSaveResponse:
    question_repository = QuestionRepository(session)
    service = QuestionGenerationService(
        question_repository=question_repository,
        generator=GeminiQuestionGenerator(),
    )
    client = create_qdrant_client()

    try:
        candidate = GeneratedQuestionCandidate(
            statement=request.candidate.statement,
            solution=request.candidate.solution,
            answer=request.candidate.answer,
            subject=request.candidate.subject,
            chapter=request.candidate.chapter,
            difficulty=request.candidate.difficulty,
            skills=request.candidate.skills,
            formulas=request.candidate.formulas,
            quality_warnings=request.candidate.quality_warnings,
        )

        question = await service.save_generated_question(
            source_question_id=request.source_question_id,
            candidate=candidate,
        )

        embedding_service = QuestionEmbeddingService(
            question_repository=question_repository,
            vector_repository=EmbeddingVectorRepository(
                client=client,
                dimension=settings.embedding_dimension,
                question_collection=settings.qdrant_question_collection,
                formula_collection=settings.qdrant_formula_collection,
            ),
            embedder=GeminiEmbedder(),
        )
        await embedding_service.embed_document(question.document_id)
        await session.refresh(question)

        return QuestionGenerationSaveResponse(
            question_id=question.id,
            document_id=question.document_id,
            sequence_number=question.sequence_number,
            marker=question.marker,
            marker_number=question.marker_number,
            statement=question.statement,
            solution=question.solution,
            answer=question.answer,
            subject=question.subject,
            chapter=question.chapter,
            difficulty=question.difficulty,
            skills=question.skills,
            formulas=question.formulas,
            embedding_status=question.embedding_status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()
```

Luu y:

```text
- Save endpoint goi embed_document ngay trong request.
- Voi corpus nho thi chap nhan duoc.
- Sau nay nen day qua background task/worker.
```

## 14. Dang ky router vao FastAPI

Mo:

```text
apps/api/main.py
```

Them import:

```python
from apps.api.v1.endpoints.generation import router as generation_router
```

Hien file dang co:

```python
from apps.api.v1.endpoints.documents import router as documents_router
from apps.api.v1.endpoints.search import router as search_router
```

Sua thanh:

```python
from apps.api.v1.endpoints.documents import router as documents_router
from apps.api.v1.endpoints.generation import router as generation_router
from apps.api.v1.endpoints.search import router as search_router
```

Them include router:

```python
app.include_router(generation_router)
```

Dat gan cac include router hien co:

```python
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(generation_router)
```

Sau do Swagger can co group:

```text
generation
  POST /generation/questions/preview
  POST /generation/questions/save
```

## 15. Unit test prompt builder

Tao folder:

```text
tests/modules/question_generation/
```

Tao file:

```text
tests/modules/question_generation/__init__.py
```

Tao file:

```text
tests/modules/question_generation/test_prompt_builder.py
```

Them:

```python
from types import SimpleNamespace

from modules.question_generation.prompt_builder import (
    build_question_generation_prompt,
)
from modules.question_generation.schemas import GenerationConstraints


def test_build_question_generation_prompt_contains_source_and_json_rules() -> None:
    source_question = SimpleNamespace(
        marker="Bai",
        marker_number="28",
        statement="Tinh $(1+i\\sqrt{3})^{9}$.",
        solution="Dung dang luong giac.",
        answer=None,
        subject="complex",
        chapter="complex-number",
        difficulty="medium",
        skills=["complex-power"],
    )

    prompt = build_question_generation_prompt(
        source_question=source_question,
        generation_count=2,
        constraints=GenerationConstraints(),
    )

    assert "Generate 2 new mathematics questions" in prompt
    assert "Return valid JSON only" in prompt
    assert '"items"' in prompt
    assert "Tinh $(1+i\\sqrt{3})^{9}$." in prompt
    assert "complex-power" in prompt
```

Chay:

```powershell
pytest tests/modules/question_generation/test_prompt_builder.py -q
```

Ky vong:

```text
1 passed
```

## 16. Unit test generation service

Tao file:

```text
tests/modules/question_generation/test_service.py
```

Them:

```python
import asyncio
import json
from types import SimpleNamespace

import pytest

from modules.question_generation import (
    GenerationConstraints,
    QuestionGenerationService,
)
from modules.question_generation.schemas import GeneratedQuestionCandidate


class FakeQuestionRepository:
    def __init__(self, questions) -> None:
        self.questions = questions
        self.created_payload = None

    async def get_question(self, question_id: str):
        for question in self.questions:
            if question.id == question_id:
                return question
        return None

    async def list_by_document(self, document_id: str):
        return [
            question
            for question in self.questions
            if question.document_id == document_id
        ]

    async def create_generated_question(self, **kwargs):
        self.created_payload = kwargs
        source_question = kwargs["source_question"]

        return SimpleNamespace(
            id="generated-id",
            document_id=source_question.document_id,
            sequence_number=2,
            marker="Generated",
            marker_number="2",
            statement=kwargs["statement"],
            solution=kwargs["solution"],
            answer=kwargs["answer"],
            formulas=kwargs["formulas"],
            subject=kwargs["subject"],
            chapter=kwargs["chapter"],
            difficulty=kwargs["difficulty"],
            skills=kwargs["skills"],
            embedding_status="pending",
        )


class FakeGenerator:
    def __init__(self, payload) -> None:
        self.payload = payload
        self.prompts = []

    def generate_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return json.dumps(self.payload)


def make_question():
    return SimpleNamespace(
        id="source-id",
        document_id="document-id",
        marker="Bai",
        marker_number="28",
        statement="Tinh $(1+i\\sqrt{3})^{9}$.",
        solution=None,
        answer=None,
        subject="complex",
        chapter="complex-number",
        difficulty="medium",
        skills=["complex-power"],
    )


def test_preview_questions_returns_candidates_with_extracted_formulas() -> None:
    question = make_question()
    repository = FakeQuestionRepository([question])
    generator = FakeGenerator(
        {
            "items": [
                {
                    "statement": "Tinh $(1-i\\sqrt{3})^{6}$.",
                    "solution": "Doi sang dang luong giac.",
                    "answer": None,
                    "difficulty": "medium",
                    "skills": ["complex-power"],
                }
            ]
        }
    )
    service = QuestionGenerationService(
        question_repository=repository,
        generator=generator,
    )

    preview = asyncio.run(
        service.preview_questions(
            source_question_id="source-id",
            generation_count=1,
            constraints=GenerationConstraints(),
        )
    )

    assert preview.source_question_id == "source-id"
    assert len(preview.candidates) == 1
    assert preview.candidates[0].statement == "Tinh $(1-i\\sqrt{3})^{6}$."
    assert preview.candidates[0].formulas[0]["normalized_latex"] == (
        "(1-i\\sqrt{3})^{6}"
    )
    assert preview.candidates[0].quality_warnings == []
    assert generator.prompts


def test_preview_questions_rejects_unknown_source_question() -> None:
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([]),
        generator=FakeGenerator({"items": []}),
    )

    with pytest.raises(ValueError, match="Source question not found"):
        asyncio.run(
            service.preview_questions(source_question_id="missing")
        )


def test_preview_questions_rejects_invalid_generation_count() -> None:
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([make_question()]),
        generator=FakeGenerator({"items": []}),
    )

    with pytest.raises(ValueError, match="Generation count"):
        asyncio.run(
            service.preview_questions(
                source_question_id="source-id",
                generation_count=20,
            )
        )


def test_save_generated_question_rejects_duplicate_statement() -> None:
    question = make_question()
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator({"items": []}),
    )

    candidate = GeneratedQuestionCandidate(
        statement=question.statement,
        solution=None,
        answer=None,
        subject="complex",
        chapter="complex-number",
        difficulty="medium",
        skills=["complex-power"],
        formulas=[],
        quality_warnings=[],
    )

    with pytest.raises(ValueError, match="duplicates"):
        asyncio.run(
            service.save_generated_question(
                source_question_id="source-id",
                candidate=candidate,
            )
        )
```

Chay:

```powershell
pytest tests/modules/question_generation -q
```

Ky vong:

```text
5 passed
```

## 17. Unit test repository create_generated_question

Co 2 cach:

```text
1. Test bang DB test hien co trong tests/api/conftest neu da cau hinh.
2. Test service voi fake repository la du cho MVP.
```

Neu muon test repository that, tao:

```text
tests/modules/question_generation/test_question_repository_generation.py
```

Nhung neu test DB hien tai dang phu thuoc moi truong local, co the de sang buoc 12.

MVP buoc 11 nen co it nhat:

```text
tests/modules/question_generation/test_service.py
tests/modules/question_generation/test_prompt_builder.py
```

## 18. API test generation

Viec test API generation co kho hon vi endpoint dung:

```python
GeminiQuestionGenerator()
QuestionEmbeddingService(...)
```

Neu test truc tiep endpoint preview, can monkeypatch generator.

Tao file:

```text
tests/api/test_generation.py
```

Huong MVP:

```python
def test_generation_preview_endpoint_returns_candidates(client, monkeypatch):
    ...
```

Nhung do repo hien tai chua co dependency override rieng cho generator, co the de API test endpoint generation sang buoc 12 de thiet ke dependency injection sach hon.

Trong buoc 11, bat buoc test service truoc.

## 19. Integration script generation

Tao file:

```text
scripts/test_question_generation.py
```

Them:

```python
import asyncio

from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from modules.question_generation import (
    GeminiQuestionGenerator,
    GenerationConstraints,
    QuestionGenerationService,
)


async def main() -> None:
    async with AsyncSessionLocal() as session:
        repository = QuestionRepository(session)

        questions = await repository.list_by_document(
            "4052feaa-2158-4dd6-8d13-4bf3698e71f1"
        )

        if not questions:
            print("No questions found. Run sync_question_storage first.")
            return

        source_question = questions[-1]

        service = QuestionGenerationService(
            question_repository=repository,
            generator=GeminiQuestionGenerator(),
        )

        preview = await service.preview_questions(
            source_question_id=source_question.id,
            generation_count=2,
            constraints=GenerationConstraints(),
        )

        print("Source question:", source_question.marker, source_question.marker_number)
        print("Source ID:", source_question.id)

        for index, candidate in enumerate(preview.candidates, start=1):
            print()
            print("Candidate:", index)
            print("Statement:", candidate.statement)
            print("Solution:", candidate.solution)
            print("Answer:", candidate.answer)
            print("Difficulty:", candidate.difficulty)
            print("Skills:", candidate.skills)
            print("Formulas:", candidate.formulas)
            print("Warnings:", candidate.quality_warnings)


if __name__ == "__main__":
    asyncio.run(main())
```

Luu y:

```text
Document ID trong script tren la vi du tu bttx.md cua buoc 10.
Neu document ID khac, thay bang document ID trong output sync cua ban.
```

Chay:

```powershell
python -m scripts.test_question_generation
```

Ket qua mong doi:

```text
Source question: Bài 28
Source ID: ...

Candidate: 1
Statement: ...
Solution: ...
Answer: ...
Difficulty: ...
Skills: [...]
Formulas: [...]
Warnings: [...]
```

## 20. Test API preview

Dam bao backend dang chay:

```powershell
uvicorn apps.api.main:app --reload
```

Mo:

```text
http://localhost:8000/docs
```

Can thay:

```text
generation
  POST /generation/questions/preview
  POST /generation/questions/save
```

Lay `source_question_id` tu output:

```powershell
python -m scripts.test_formula_search
```

Hoac tu database/check script.

Goi API:

```powershell
$body = @{
  source_question_id = "ce9b7fc5-fa39-463a-8488-3006a23afa6d"
  generation_count = 2
  constraints = @{
    difficulty = "medium"
    skills = @("complex-number", "complex-power")
    preserve_formula_style = $true
    avoid_duplicate = $true
  }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod `
  -Uri "http://localhost:8000/generation/questions/preview" `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $body

$response | ConvertTo-Json -Depth 10
```

Ket qua mong doi:

```json
{
  "source_question_id": "...",
  "candidates": [
    {
      "statement": "...",
      "solution": "...",
      "answer": "...",
      "subject": null,
      "chapter": null,
      "difficulty": "medium",
      "skills": ["complex-number", "complex-power"],
      "formulas": [
        {
          "latex": "...",
          "normalized_latex": "...",
          "source": "statement"
        }
      ],
      "quality_warnings": []
    }
  ]
}
```

## 21. Test API save

Lay candidate dau tien tu response preview, gui sang save.

Vi PowerShell thao tac object hoi dai, co the test bang Swagger de nhanh hon.

Body mau:

```json
{
  "source_question_id": "ce9b7fc5-fa39-463a-8488-3006a23afa6d",
  "candidate": {
    "statement": "Viết số phức $(1-i\\sqrt{3})^{6}$ dưới dạng chính tắc.",
    "solution": "Đổi sang dạng lượng giác rồi áp dụng công thức Moivre.",
    "answer": null,
    "subject": "complex-number",
    "chapter": "complex-power",
    "difficulty": "medium",
    "skills": ["complex-number", "complex-power"],
    "formulas": [
      {
        "latex": "(1-i\\sqrt{3})^{6}",
        "normalized_latex": "(1-i\\sqrt{3})^{6}",
        "source": "statement"
      }
    ],
    "quality_warnings": []
  }
}
```

PowerShell:

```powershell
$body = @{
  source_question_id = "ce9b7fc5-fa39-463a-8488-3006a23afa6d"
  candidate = @{
    statement = "Viet so phuc $(1-i\sqrt{3})^{6}$ duoi dang chinh tac."
    solution = "Doi sang dang luong giac roi ap dung cong thuc Moivre."
    answer = $null
    subject = "complex-number"
    chapter = "complex-power"
    difficulty = "medium"
    skills = @("complex-number", "complex-power")
    formulas = @(
      @{
        latex = "(1-i\sqrt{3})^{6}"
        normalized_latex = "(1-i\sqrt{3})^{6}"
        source = "statement"
      }
    )
    quality_warnings = @()
  }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod `
  -Uri "http://localhost:8000/generation/questions/save" `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $body

$response | ConvertTo-Json -Depth 10
```

Ket qua mong doi:

```json
{
  "question_id": "...",
  "document_id": "...",
  "sequence_number": 3,
  "marker": "Generated",
  "marker_number": "3",
  "statement": "...",
  "embedding_status": "completed"
}
```

Sau save, kiem tra sync:

```powershell
python -m scripts.check_question_embedding_sync
```

Neu truoc do co:

```text
PostgreSQL questions: 2
Qdrant question points: 2
Qdrant formula points: 7
```

Sau khi save 1 cau co 1 formula, co the thanh:

```text
PostgreSQL questions: 3
Qdrant question points: 3
Qdrant formula points: 8
```

So formula points co the khac tuy candidate co bao nhieu formula.

## 22. Test duplicate save

Goi lai cung body save lan nua.

Ket qua mong doi:

```text
400 Bad Request
Generated question duplicates an existing question
```

Ly do:

```text
save_generated_question so sanh normalized statement trong cung document.
```

## 23. Chay test tong the

Chay:

```powershell
pytest tests/modules/question_generation -q
pytest tests/modules/semantic_search -q
pytest tests/modules/embeddings -q
pytest tests/modules -q
pytest -q
```

Chay compile:

```powershell
python -m compileall apps/api core infra modules tests scripts
```

Chay integration lien quan:

```powershell
python -m scripts.sync_question_storage
python -m scripts.check_question_embedding_sync
python -m scripts.test_question_generation
```

Chay API:

```powershell
uvicorn apps.api.main:app --reload
```

Mo:

```text
http://localhost:8000/docs
```

Can thay:

```text
POST /generation/questions/preview
POST /generation/questions/save
```

## 24. Loi thuong gap

### 24.1 Gemini tra markdown fence

Vi du:

```text
```json
{...}
```
```

Service `_loads_generation_json` da co xu ly co ban.

Neu van loi, in raw output trong script de xem Gemini tra gi.

### 24.2 JSONDecodeError

Nguyen nhan:

```text
- Gemini tra text khong phai JSON.
- Prompt chua du chat.
- Model dang bi loi/bi chen canh bao.
```

Xu ly:

```text
- Giam generation_count.
- Chay lai.
- Them response_mime_type application/json sau nay neu SDK/model ho tro on dinh.
```

### 24.3 No formula detected

Neu candidate khong co cong thuc LaTeX:

```text
quality_warnings = ["no_formula_detected"]
```

Khong nhat thiet la loi neu cau hoi ly thuyet.

Voi bai toan cong thuc, nen yeu cau prompt ro hon:

```text
Every generated statement must contain at least one LaTeX formula.
```

### 24.4 Save cham

Save endpoint goi:

```python
QuestionEmbeddingService.embed_document(...)
```

Nen co the cham vi goi Gemini embedding cho tat ca questions/formulas trong document.

MVP chap nhan.

Sau nay:

```text
- Embed chi generated question moi.
- Upsert point moi thay vi replace_for_document.
- Dua embedding vao background task/worker.
```

### 24.5 Gemini 429 RESOURCE_EXHAUSTED

Nguyen nhan:

```text
- Preview goi Gemini generate.
- Save goi Gemini embedding.
- Neu chay lien tuc de bi quota.
```

Xu ly tam thoi:

```text
- Doi vai phut roi chay lai.
- Giam generation_count.
- Khong save nhieu candidate lien tuc.
```

Mo rong sau MVP:

```text
- Retry/backoff.
- Cache generation prompt.
- Queue job.
```

### 24.6 PowerShell hien thi loi tieng Viet

Neu thay:

```text
BÃƒ i
ViÃ¡ÂºÂ¿t
```

Day thuong la loi hien thi encoding cua PowerShell, khong nhat thiet la loi API.

Kiem tra bang Swagger/browser hoac Python script.

## 25. Mo rong sau MVP

### 25.1 Tao bang generated_questions rieng

Sau khi co review workflow, nen tao bang:

```text
generated_questions
  id
  source_question_id
  document_id
  statement
  solution
  answer
  formulas
  subject
  chapter
  difficulty
  skills
  status: draft/reviewed/published/rejected
  quality_score
  created_at
  updated_at
```

Khi publish moi ghi sang `questions`.

### 25.2 Them parent_question_id vao questions

Neu muon truy vet generated question:

```text
questions.parent_question_id nullable
questions.origin_type original/generated
```

Can migration.

### 25.3 Quality scoring

Them:

```text
- Duplicate score bang semantic search.
- Formula validity check.
- Difficulty consistency check.
- Solution completeness check.
```

### 25.4 Symbolic validation

Dung SymPy de validate dap an voi bai co cong thuc ro.

MVP khong lam vi LaTeX -> SymPy phuc tap va de fail voi expression thuc te.

### 25.5 Frontend generation

Them trang:

```text
apps/frontend/src/pages/GenVariants.jsx
```

Workflow:

```text
chon source question -> preview candidates -> chon candidate -> save
```

## 26. Thu tu trien khai khuyen nghi

Lam lan luot:

```text
1. Tao modules/question_generation/schemas.py.
2. Tao modules/question_generation/prompt_builder.py.
3. Tao modules/question_generation/gemini_generator.py.
4. Tao modules/question_generation/service.py voi preview_questions.
5. Tao modules/question_generation/__init__.py.
6. Viet test_prompt_builder.py.
7. Viet test_service.py cho preview.
8. Chay pytest tests/modules/question_generation -q.
9. Them QuestionRepository.create_generated_question.
10. Them save_generated_question vao QuestionGenerationService.
11. Bo sung test save duplicate.
12. Tao apps/api/v1/models/generation.py.
13. Tao apps/api/v1/endpoints/generation.py.
14. Dang ky generation_router trong apps/api/main.py.
15. Chay compileall cac file vua sua.
16. Tao scripts/test_question_generation.py.
17. Chay python -m scripts.test_question_generation.
18. Chay uvicorn va test Swagger preview.
19. Test save endpoint.
20. Chay python -m scripts.check_question_embedding_sync.
21. Chay pytest -q.
22. Chay python -m compileall apps/api core infra modules tests scripts.
```

## 27. Tieu chi hoan thanh

Buoc 11 MVP hoan tat khi:

```text
1. Co module modules/question_generation.
2. Co GenerationConstraints, GeneratedQuestionCandidate, QuestionGenerationPreview.
3. Co prompt builder yeu cau JSON output.
4. Co GeminiQuestionGenerator dung settings.gemini_model.
5. QuestionGenerationService preview duoc candidates.
6. Preview parse JSON va extract formulas.
7. Preview gan quality_warnings co ban.
8. QuestionRepository co create_generated_question.
9. Service save_generated_question luu vao questions.
10. Save reject duplicate statement.
11. API co POST /generation/questions/preview.
12. API co POST /generation/questions/save.
13. Save endpoint re-embed document vao Qdrant.
14. Swagger hien generation endpoints.
15. Unit test question_generation pass.
16. Integration script sinh duoc candidate.
17. Save xong check_question_embedding_sync thay question points tang.
18. Tat ca test cu van pass.
19. compileall toan project khong loi.
```

Sau buoc 11, he thong san sang cho:

```text
- Buoc 12: kiem tra chat luong, duplicate semantic, validation nang cao.
- Review workflow cho generated questions.
- Frontend sinh bien the cau hoi.
```
