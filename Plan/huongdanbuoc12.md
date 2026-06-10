# Huong Dan Buoc 12: Kiem Tra Chat Luong, Duplicate Nang Cao Va Bao Tri He Thong

## 1. Muc tieu

Buoc 12 tiep noi buoc 11. Sau buoc 11, he thong da co:

```text
POST /generation/questions/preview
POST /generation/questions/save

modules/question_generation
QuestionGenerationService.preview_questions(...)
QuestionGenerationService.save_generated_question(...)
QuestionRepository.create_generated_question(...)
QuestionEmbeddingService.embed_document(...)
SemanticSearchService.search_questions(...)
SemanticSearchService.search_formulas(...)
```

Buoc 12 bo sung lop kiem tra chat luong cau hoi truoc khi luu va tang do tin cay cua he thong.

MVP cua buoc 12 can dat:

```text
- Co module modules/question_quality.
- Co schema danh gia chat luong cau hoi.
- Co exact duplicate check dung lai normalized statement.
- Co semantic duplicate check dua tren SemanticSearchService neu duoc cau hinh.
- Co formula validation co ban:
  - formula co du latex, normalized_latex, source
  - source nam trong statement/solution/answer
  - latex khong rong
  - cong thuc trong candidate khop voi cong thuc extract lai tu statement/solution/answer
- Co difficulty validation co ban:
  - difficulty nam trong easy/medium/hard neu co
  - canh bao neu candidate difficulty lech constraints
- Co answer/solution validation co ban:
  - canh bao neu thieu answer
  - canh bao neu thieu solution
- Preview generation gan quality_warnings tu question_quality.
- Save generation chan duplicate nghiem trong.
- Co endpoint tuy chon:
  POST /generation/questions/quality
  de client co the kiem tra candidate truoc khi save.
- Co unit test cho question_quality.
- Co API test cho endpoint quality bang fake service.
- Tat ca test cu van pass.
```

Buoc 12 chua lam:

```text
- Chua dung SymPy de chung minh dap an dung.
- Chua co LLM judge cham diem loi giai.
- Chua co review workflow rieng.
- Chua tao bang generated_questions rieng.
- Chua queue/background job.
- Chua auto-fix candidate.
```

Ly do:

```text
- SymPy can parse LaTeX phuc tap, de fail voi de bai thuc te.
- LLM judge ton quota va can prompt/test rieng.
- He thong hien tai dang luu generated question truc tiep vao bang questions.
- Buoc 12 nen tap trung vao quality gates nhe, on dinh, test duoc.
```

## 2. Hien trang dau vao

Sau buoc 11, cac file quan trong dang co:

```text
modules/question_generation/
  schemas.py
  prompt_builder.py
  gemini_generator.py
  service.py
  __init__.py

apps/api/v1/models/generation.py
apps/api/v1/endpoints/generation.py

infra/db/repositories/questions.py
infra/vector_db/repositories/embeddings.py
modules/semantic_search/service.py
modules/question_segmenter/formula_extractor.py
```

Luang hien tai:

```text
preview:
  source_question_id
  -> get source question
  -> Gemini generate JSON
  -> parse candidate
  -> exact duplicate warning
  -> no_formula warning
  -> response candidates

save:
  source_question_id + candidate
  -> exact duplicate reject
  -> save vao questions
  -> embed_document
  -> Qdrant sync
```

Diem can cai tien trong buoc 12:

```text
- Quality logic dang nam trong QuestionGenerationService.
- Duplicate chi so sanh exact normalized statement.
- Chua co semantic duplicate warning.
- Chua validate formulas payload ky.
- Chua co endpoint quality rieng.
- Save moi chan duplicate exact, chua chan candidate co quality issue nghiem trong.
```

## 3. Nguyen tac thiet ke

### 3.1 Tach question_quality khoi question_generation

Khong nen tiep tuc nhet tat ca quality logic vao:

```text
modules/question_generation/service.py
```

Vi:

```text
- Generation tao candidate.
- Quality danh gia candidate.
- Semantic duplicate, formula validation, difficulty validation se lon dan.
- Sau nay frontend/review workflow cung can goi quality rieng.
```

Tao module moi:

```text
modules/question_quality/
```

### 3.2 Quality warning va blocking issue tach nhau

Can phan biet:

```text
warning:
  Van cho preview/save neu nguoi dung chap nhan.

blocking issue:
  Save phai chan vi nguy co cao.
```

MVP de xuat:

```text
blocking:
  - exact_duplicate_statement
  - invalid_formula_payload
  - empty_statement

warning:
  - semantic_duplicate_candidate
  - no_formula_detected
  - missing_solution
  - missing_answer
  - difficulty_mismatch
  - invalid_difficulty
```

### 3.3 Semantic duplicate la canh bao truoc

Semantic duplicate dua tren vector search co the sai so.

Trong MVP:

```text
- Preview gan warning neu score >= threshold.
- Save chua bat buoc chan semantic duplicate.
- Sau nay co the cau hinh threshold va rule block.
```

### 3.4 Formula validation chi lam co ban

MVP khong validate toan hoc dung/sai.

Chi kiem tra:

```text
- formulas payload du field.
- source hop le.
- latex/normalized_latex khong rong.
- formulas trong payload khong thieu cong thuc extract lai tu text.
```

## 4. Cau truc can bo sung va sua

Them:

```text
modules/question_quality/
  __init__.py
  schemas.py
  service.py

tests/modules/question_quality/
  __init__.py
  test_service.py

tests/api/test_generation_quality_endpoint.py
```

Sua:

```text
modules/question_generation/service.py
apps/api/v1/models/generation.py
apps/api/v1/endpoints/generation.py
```

Khong bat buoc sua:

```text
infra/db/models.py
infra/db/repositories/questions.py
```

Ly do:

```text
- Buoc 12 MVP chua can bang quality_reports.
- Quality co the tinh on-demand tu candidate va questions hien co.
```

## 5. Them schemas cho question_quality

Tao folder:

```text
modules/question_quality/
```

Tao file:

```text
modules/question_quality/schemas.py
```

Them:

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class QualityIssue:
    code: str
    message: str
    severity: str
    field: str | None = None


@dataclass(frozen=True)
class SemanticDuplicateHit:
    question_id: str
    document_id: str
    score: float
    statement: str


@dataclass(frozen=True)
class QuestionQualityReport:
    warnings: list[QualityIssue] = field(default_factory=list)
    blocking_issues: list[QualityIssue] = field(default_factory=list)
    semantic_duplicates: list[SemanticDuplicateHit] = field(default_factory=list)

    @property
    def quality_warnings(self) -> list[str]:
        return [
            issue.code
            for issue in [*self.blocking_issues, *self.warnings]
        ]

    @property
    def can_save(self) -> bool:
        return not self.blocking_issues
```

Y nghia:

```text
QualityIssue:
  Mot van de chat luong.

SemanticDuplicateHit:
  Ket qua duplicate semantic gan voi cau hoi cu.

QuestionQualityReport:
  Bao cao tong hop, co warnings, blocking_issues, semantic_duplicates.
```

## 6. Them service question_quality

Tao file:

```text
modules/question_quality/service.py
```

Them:

```python
import re
from typing import Protocol

from infra.db.models import Question
from modules.question_generation.schemas import GeneratedQuestionCandidate
from modules.question_segmenter.formula_extractor import extract_formulas
from modules.question_quality.schemas import (
    QualityIssue,
    QuestionQualityReport,
    SemanticDuplicateHit,
)
from modules.semantic_search.schemas import QuestionSearchFilters


VALID_FORMULA_SOURCES = {"statement", "solution", "answer"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}


class SemanticQuestionSearch(Protocol):
    async def search_questions(
        self,
        *,
        query: str,
        limit: int = 10,
        filters: QuestionSearchFilters | None = None,
    ):
        ...


def normalize_statement(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


class QuestionQualityService:
    def __init__(
        self,
        *,
        semantic_search_service: SemanticQuestionSearch | None = None,
        semantic_duplicate_threshold: float = 0.92,
    ) -> None:
        self.semantic_search_service = semantic_search_service
        self.semantic_duplicate_threshold = semantic_duplicate_threshold

    async def assess_candidate(
        self,
        *,
        candidate: GeneratedQuestionCandidate,
        source_question: Question,
        existing_questions: list[Question],
        requested_difficulty: str | None = None,
    ) -> QuestionQualityReport:
        blocking_issues: list[QualityIssue] = []
        warnings: list[QualityIssue] = []

        statement = candidate.statement.strip()

        if not statement:
            blocking_issues.append(
                QualityIssue(
                    code="empty_statement",
                    message="Generated statement must not be empty",
                    severity="error",
                    field="statement",
                )
            )

        existing_statements = {
            normalize_statement(question.statement)
            for question in existing_questions
        }

        if normalize_statement(statement) in existing_statements:
            blocking_issues.append(
                QualityIssue(
                    code="exact_duplicate_statement",
                    message="Generated statement duplicates an existing question",
                    severity="error",
                    field="statement",
                )
            )

        warnings.extend(self._validate_formula_payload(candidate))
        blocking_issues.extend(self._validate_formula_payload_blocking(candidate))
        warnings.extend(self._validate_extracted_formulas(candidate))
        warnings.extend(
            self._validate_difficulty(
                candidate=candidate,
                source_question=source_question,
                requested_difficulty=requested_difficulty,
            )
        )
        warnings.extend(self._validate_solution_and_answer(candidate))

        semantic_duplicates = await self._find_semantic_duplicates(
            candidate=candidate,
            source_question=source_question,
        )

        if semantic_duplicates:
            warnings.append(
                QualityIssue(
                    code="semantic_duplicate_candidate",
                    message="Generated statement is semantically close to existing questions",
                    severity="warning",
                    field="statement",
                )
            )

        return QuestionQualityReport(
            warnings=warnings,
            blocking_issues=blocking_issues,
            semantic_duplicates=semantic_duplicates,
        )

    def _validate_formula_payload(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> list[QualityIssue]:
        warnings: list[QualityIssue] = []

        if not candidate.formulas:
            warnings.append(
                QualityIssue(
                    code="no_formula_detected",
                    message="No formula was detected in generated content",
                    severity="warning",
                    field="formulas",
                )
            )

        return warnings

    def _validate_formula_payload_blocking(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> list[QualityIssue]:
        blocking_issues: list[QualityIssue] = []

        for index, formula in enumerate(candidate.formulas):
            latex = str(formula.get("latex") or "").strip()
            normalized_latex = str(formula.get("normalized_latex") or "").strip()
            source = str(formula.get("source") or "").strip()

            if not latex or not normalized_latex or source not in VALID_FORMULA_SOURCES:
                blocking_issues.append(
                    QualityIssue(
                        code="invalid_formula_payload",
                        message="Formula payload must contain latex, normalized_latex and valid source",
                        severity="error",
                        field=f"formulas[{index}]",
                    )
                )

        return blocking_issues

    def _validate_extracted_formulas(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> list[QualityIssue]:
        extracted = []

        for formula in extract_formulas(candidate.statement, source="statement"):
            extracted.append(formula.normalized_latex)

        for formula in extract_formulas(candidate.solution, source="solution"):
            extracted.append(formula.normalized_latex)

        for formula in extract_formulas(candidate.answer, source="answer"):
            extracted.append(formula.normalized_latex)

        payload_formulas = {
            str(formula.get("normalized_latex") or "").strip()
            for formula in candidate.formulas
        }

        missing = [
            formula
            for formula in extracted
            if formula and formula not in payload_formulas
        ]

        if missing:
            return [
                QualityIssue(
                    code="formula_payload_mismatch",
                    message="Formula payload does not include every formula extracted from generated content",
                    severity="warning",
                    field="formulas",
                )
            ]

        return []

    def _validate_difficulty(
        self,
        *,
        candidate: GeneratedQuestionCandidate,
        source_question: Question,
        requested_difficulty: str | None,
    ) -> list[QualityIssue]:
        warnings: list[QualityIssue] = []
        difficulty = candidate.difficulty

        if difficulty and difficulty not in VALID_DIFFICULTIES:
            warnings.append(
                QualityIssue(
                    code="invalid_difficulty",
                    message="Difficulty should be easy, medium or hard",
                    severity="warning",
                    field="difficulty",
                )
            )

        target_difficulty = requested_difficulty or source_question.difficulty

        if difficulty and target_difficulty and difficulty != target_difficulty:
            warnings.append(
                QualityIssue(
                    code="difficulty_mismatch",
                    message="Generated difficulty does not match the requested/source difficulty",
                    severity="warning",
                    field="difficulty",
                )
            )

        return warnings

    def _validate_solution_and_answer(
        self,
        candidate: GeneratedQuestionCandidate,
    ) -> list[QualityIssue]:
        warnings: list[QualityIssue] = []

        if not candidate.solution:
            warnings.append(
                QualityIssue(
                    code="missing_solution",
                    message="Generated question does not include a solution",
                    severity="warning",
                    field="solution",
                )
            )

        if not candidate.answer:
            warnings.append(
                QualityIssue(
                    code="missing_answer",
                    message="Generated question does not include an answer",
                    severity="warning",
                    field="answer",
                )
            )

        return warnings

    async def _find_semantic_duplicates(
        self,
        *,
        candidate: GeneratedQuestionCandidate,
        source_question: Question,
    ) -> list[SemanticDuplicateHit]:
        if self.semantic_search_service is None:
            return []

        results = await self.semantic_search_service.search_questions(
            query=candidate.statement,
            limit=5,
            filters=QuestionSearchFilters(
                subject=candidate.subject or source_question.subject,
                chapter=candidate.chapter or source_question.chapter,
                difficulty=candidate.difficulty or source_question.difficulty,
            ),
        )

        duplicates: list[SemanticDuplicateHit] = []

        for result in results:
            if result.question_id == source_question.id:
                continue

            if result.score < self.semantic_duplicate_threshold:
                continue

            duplicates.append(
                SemanticDuplicateHit(
                    question_id=result.question_id,
                    document_id=result.document_id,
                    score=result.score,
                    statement=result.statement,
                )
            )

        return duplicates
```

Ghi chu:

```text
- semantic_search_service la optional de unit test va runtime co the dung/khong dung.
- Exact duplicate la blocking.
- Semantic duplicate la warning.
- Formula payload sai shape la blocking.
- Missing solution/answer chi la warning vi co cau hoi co the chua co loi giai trong MVP.
```

## 7. Export module question_quality

Tao file:

```text
modules/question_quality/__init__.py
```

Them:

```python
from modules.question_quality.schemas import (
    QualityIssue,
    QuestionQualityReport,
    SemanticDuplicateHit,
)
from modules.question_quality.service import QuestionQualityService

__all__ = [
    "QualityIssue",
    "QuestionQualityReport",
    "QuestionQualityService",
    "SemanticDuplicateHit",
]
```

## 8. Unit test question_quality service

Tao folder:

```text
tests/modules/question_quality/
```

Tao file:

```text
tests/modules/question_quality/__init__.py
```

Co the de rong.

Tao file:

```text
tests/modules/question_quality/test_service.py
```

Them:

```python
import asyncio
from types import SimpleNamespace

from modules.question_generation.schemas import GeneratedQuestionCandidate
from modules.question_quality import QuestionQualityService


def make_question(
    *,
    question_id="source-id",
    statement="Tinh $x+1$.",
):
    return SimpleNamespace(
        id=question_id,
        document_id="document-id",
        marker="Bai",
        marker_number="1",
        statement=statement,
        solution=None,
        answer=None,
        subject="math",
        chapter="algebra",
        difficulty="medium",
        skills=["simplify"],
    )


def make_candidate(
    *,
    statement="Tinh $x+2$.",
    solution="Cong 2 vao x.",
    answer="$x+2$",
    difficulty="medium",
    formulas=None,
):
    return GeneratedQuestionCandidate(
        statement=statement,
        solution=solution,
        answer=answer,
        subject="math",
        chapter="algebra",
        difficulty=difficulty,
        skills=["simplify"],
        formulas=formulas
        if formulas is not None
        else [
            {
                "latex": "x+2",
                "normalized_latex": "x+2",
                "source": "statement",
            }
        ],
        quality_warnings=[],
    )


def test_assess_candidate_allows_valid_candidate() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate()

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
            requested_difficulty="medium",
        )
    )

    assert report.can_save is True
    assert report.blocking_issues == []
    assert report.quality_warnings == []


def test_assess_candidate_blocks_exact_duplicate_statement() -> None:
    service = QuestionQualityService()
    source_question = make_question(statement="Tinh $x+1$.")
    candidate = make_candidate(statement="  Tinh   $x+1$. ")

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert report.can_save is False
    assert report.blocking_issues[0].code == "exact_duplicate_statement"
    assert "exact_duplicate_statement" in report.quality_warnings


def test_assess_candidate_warns_when_no_formula_detected() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate(
        statement="Neu khai niem so phuc lien hop.",
        answer=None,
        formulas=[],
    )

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert report.can_save is True
    assert "no_formula_detected" in report.quality_warnings
    assert "missing_answer" in report.quality_warnings


def test_assess_candidate_blocks_invalid_formula_payload() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate(
        formulas=[
            {
                "normalized_latex": "x+2",
                "source": "statement",
            }
        ]
    )

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert report.can_save is False
    assert "invalid_formula_payload" in report.quality_warnings


def test_assess_candidate_warns_formula_payload_mismatch() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate(
        statement="Tinh $x+3$.",
        formulas=[
            {
                "latex": "x+2",
                "normalized_latex": "x+2",
                "source": "statement",
            }
        ],
    )

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert report.can_save is True
    assert "formula_payload_mismatch" in report.quality_warnings


def test_assess_candidate_warns_difficulty_mismatch() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate(difficulty="hard")

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
            requested_difficulty="medium",
        )
    )

    assert "difficulty_mismatch" in report.quality_warnings


def test_assess_candidate_warns_invalid_difficulty() -> None:
    service = QuestionQualityService()
    source_question = make_question()
    candidate = make_candidate(difficulty="very-hard")

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert "invalid_difficulty" in report.quality_warnings


def test_assess_candidate_warns_semantic_duplicate() -> None:
    class FakeSemanticSearchService:
        async def search_questions(self, **kwargs):
            return [
                SimpleNamespace(
                    question_id="similar-id",
                    document_id="document-id",
                    score=0.95,
                    statement="Tinh $x+2$.",
                )
            ]

    service = QuestionQualityService(
        semantic_search_service=FakeSemanticSearchService(),
        semantic_duplicate_threshold=0.92,
    )
    source_question = make_question()
    candidate = make_candidate()

    report = asyncio.run(
        service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=[source_question],
        )
    )

    assert "semantic_duplicate_candidate" in report.quality_warnings
    assert report.semantic_duplicates[0].question_id == "similar-id"
```

Chay:

```powershell
pytest tests/modules/question_quality -q
```

Ky vong:

```text
8 passed
```

## 9. Tich hop quality service vao question_generation preview

Mo:

```text
modules/question_generation/service.py
```

Them import:

```python
from modules.question_quality import QuestionQualityService
```

Sua constructor tu:

```python
    def __init__(
        self,
        *,
        question_repository: QuestionRepository,
        generator: TextQuestionGenerator,
    ) -> None:
        self.question_repository = question_repository
        self.generator = generator
```

Thanh:

```python
    def __init__(
        self,
        *,
        question_repository: QuestionRepository,
        generator: TextQuestionGenerator,
        quality_service: QuestionQualityService | None = None,
    ) -> None:
        self.question_repository = question_repository
        self.generator = generator
        self.quality_service = quality_service or QuestionQualityService()
```

Trong `preview_questions`, hien tai co:

```python
        existing_statements = {
            _normalize_for_duplicate_check(question.statement)
            for question in existing_questions
        }
```

Va parse candidate nhu sau:

```python
            candidate = self._parse_candidate(
                item=item,
                source_question=source_question,
                existing_statements=existing_statements,
                constraints=constraints,
            )

            candidates.append(candidate)
```

Sua thanh:

```python
            candidate = self._parse_candidate(
                item=item,
                source_question=source_question,
                constraints=constraints,
            )

            quality_report = await self.quality_service.assess_candidate(
                candidate=candidate,
                source_question=source_question,
                existing_questions=existing_questions,
                requested_difficulty=constraints.difficulty,
            )

            candidates.append(
                GeneratedQuestionCandidate(
                    statement=candidate.statement,
                    solution=candidate.solution,
                    answer=candidate.answer,
                    subject=candidate.subject,
                    chapter=candidate.chapter,
                    difficulty=candidate.difficulty,
                    skills=candidate.skills,
                    formulas=candidate.formulas,
                    quality_warnings=quality_report.quality_warnings,
                )
            )
```

Sau do sua signature `_parse_candidate`.

Tu:

```python
    def _parse_candidate(
        self,
        *,
        item: object,
        source_question: Question,
        existing_statements: set[str],
        constraints: GenerationConstraints,
    ) -> GeneratedQuestionCandidate:
```

Thanh:

```python
    def _parse_candidate(
        self,
        *,
        item: object,
        source_question: Question,
        constraints: GenerationConstraints,
    ) -> GeneratedQuestionCandidate:
```

Trong `_parse_candidate`, xoa block cu:

```python
        quality_warnings: list[str] = []

        if _normalize_for_duplicate_check(statement) in existing_statements:
            quality_warnings.append("duplicate_statement")

        if constraints.avoid_duplicate and quality_warnings:
            quality_warnings.append("review_required")

        if not formulas:
            quality_warnings.append("no_formula_detected")
```

Thay bang:

```python
        quality_warnings: list[str] = []
```

Ly do:

```text
- _parse_candidate chi parse Gemini output.
- assess_candidate moi la noi danh gia chat luong.
- Service generation gon hon, de test hon.
```

## 10. Tich hop quality service vao save

Trong `save_generated_question`, sau khi co:

```python
        existing_questions = await self.question_repository.list_by_document(
            source_question.document_id
        )
```

Them:

```python
        quality_report = await self.quality_service.assess_candidate(
            candidate=candidate,
            source_question=source_question,
            existing_questions=existing_questions,
            requested_difficulty=None,
        )

        if not quality_report.can_save:
            raise ValueError(
                ", ".join(quality_report.quality_warnings)
            )
```

Sau do co the xoa duplicate check cu:

```python
        existing_statements = {
            _normalize_for_duplicate_check(question.statement)
            for question in existing_questions
        }

        if _normalize_for_duplicate_check(candidate.statement) in existing_statements:
            raise ValueError("Generated question duplicates an existing question")
```

Hoac giu lai duplicate check cu trong vong dau neu muon thong bao loi cu.

Khuyen nghi de giu tuong thich test hien co:

```python
        existing_statements = {
            _normalize_for_duplicate_check(question.statement)
            for question in existing_questions
        }

        if _normalize_for_duplicate_check(candidate.statement) in existing_statements:
            raise ValueError("Generated question duplicates an existing question")
```

Sau do chay quality_report de chan invalid_formula_payload.

Thu tu save nen la:

```text
1. source question exists
2. exact duplicate check cu de giu message cu
3. quality_report
4. if blocking -> raise ValueError
5. create_generated_question
```

## 11. Cap nhat unit test generation service

Mo:

```text
tests/modules/question_generation/test_service.py
```

Sau khi tich hop quality service, mot so test warnings se can doi expectation.

### 11.1 Duplicate preview warning moi

Test cu co the dang expect:

```python
assert preview.candidates[0].quality_warnings == [
    "duplicate_statement",
    "review_required",
]
```

Sua thanh:

```python
assert preview.candidates[0].quality_warnings == [
    "exact_duplicate_statement",
    "missing_solution",
    "missing_answer",
]
```

Neu candidate duplicate co formula hop le thi warnings se gom:

```text
exact_duplicate_statement
missing_solution
missing_answer
```

### 11.2 No formula test moi

Test cu:

```python
assert preview.candidates[0].quality_warnings == ["no_formula_detected"]
```

Sua thanh:

```python
assert "no_formula_detected" in preview.candidates[0].quality_warnings
```

Vi quality service co the them:

```text
missing_solution
missing_answer
```

### 11.3 Them test save chan invalid formula payload

Them vao cuoi file:

```python
def test_save_generated_question_rejects_invalid_formula_payload() -> None:
    question = make_question()
    service = QuestionGenerationService(
        question_repository=FakeQuestionRepository([question]),
        generator=FakeGenerator({"items": []}),
    )

    candidate = GeneratedQuestionCandidate(
        statement="Tinh $x+1$.",
        solution="Cong 1 vao x.",
        answer="$x+1$",
        subject="math",
        chapter="algebra",
        difficulty="easy",
        skills=["simplify"],
        formulas=[
            {
                "normalized_latex": "x+1",
                "source": "statement",
            }
        ],
        quality_warnings=[],
    )

    with pytest.raises(ValueError, match="invalid_formula_payload"):
        asyncio.run(
            service.save_generated_question(
                source_question_id="source-id",
                candidate=candidate,
            )
        )
```

Chay:

```powershell
pytest tests/modules/question_generation/test_service.py -q
pytest tests/modules/question_quality -q
```

## 12. Them API model cho quality endpoint

Mo:

```text
apps/api/v1/models/generation.py
```

Them cuoi file:

```python
class QualityIssueItem(BaseModel):
    code: str
    message: str
    severity: str
    field: str | None = None


class SemanticDuplicateItem(BaseModel):
    question_id: str
    document_id: str
    score: float
    statement: str


class QuestionGenerationQualityRequest(BaseModel):
    source_question_id: str = Field(min_length=1)
    candidate: GeneratedQuestionCandidateItem
    requested_difficulty: str | None = None


class QuestionGenerationQualityResponse(BaseModel):
    can_save: bool
    quality_warnings: list[str]
    warnings: list[QualityIssueItem]
    blocking_issues: list[QualityIssueItem]
    semantic_duplicates: list[SemanticDuplicateItem]
```

Vi sao:

```text
- Client co the bam nut "Check quality" truoc khi save.
- Response tach warnings/blocking/semantic duplicates ro rang.
```

## 13. Them endpoint quality

Mo:

```text
apps/api/v1/endpoints/generation.py
```

Them import model moi:

```python
    QualityIssueItem,
    QuestionGenerationQualityRequest,
    QuestionGenerationQualityResponse,
    SemanticDuplicateItem,
```

Them import:

```python
from modules.question_quality import QuestionQualityService
from modules.semantic_search import (
    QuestionSearchFilters,
    SemanticSearchService,
)
```

Neu da import `SemanticSearchService` o endpoint search thi o file generation van can import rieng.

Them factory:

```python
def create_semantic_search_service(
    *,
    session: AsyncSession,
    client,
) -> SemanticSearchService:
    return SemanticSearchService(
        question_repository=QuestionRepository(session),
        vector_repository=EmbeddingVectorRepository(
            client=client,
            dimension=settings.embedding_dimension,
            question_collection=settings.qdrant_question_collection,
            formula_collection=settings.qdrant_formula_collection,
        ),
        embedder=GeminiEmbedder(),
    )
```

Them helper:

```python
def _to_quality_issue_item(issue) -> QualityIssueItem:
    return QualityIssueItem(
        code=issue.code,
        message=issue.message,
        severity=issue.severity,
        field=issue.field,
    )
```

Them endpoint:

```python
@router.post(
    "/questions/quality",
    response_model=QuestionGenerationQualityResponse,
)
async def assess_generated_question_quality(
    request: QuestionGenerationQualityRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionGenerationQualityResponse:
    client = create_qdrant_client()

    try:
        question_repository = QuestionRepository(session)
        source_question = await question_repository.get_question(
            request.source_question_id
        )

        if source_question is None:
            raise ValueError("Source question not found")

        existing_questions = await question_repository.list_by_document(
            source_question.document_id
        )

        quality_service = QuestionQualityService(
            semantic_search_service=create_semantic_search_service(
                session=session,
                client=client,
            )
        )

        report = await quality_service.assess_candidate(
            candidate=_to_generated_candidate(request.candidate),
            source_question=source_question,
            existing_questions=existing_questions,
            requested_difficulty=request.requested_difficulty,
        )

        return QuestionGenerationQualityResponse(
            can_save=report.can_save,
            quality_warnings=report.quality_warnings,
            warnings=[
                _to_quality_issue_item(issue)
                for issue in report.warnings
            ],
            blocking_issues=[
                _to_quality_issue_item(issue)
                for issue in report.blocking_issues
            ],
            semantic_duplicates=[
                SemanticDuplicateItem(
                    question_id=duplicate.question_id,
                    document_id=duplicate.document_id,
                    score=duplicate.score,
                    statement=duplicate.statement,
                )
                for duplicate in report.semantic_duplicates
            ],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    finally:
        await client.close()
```

Swagger se co them:

```text
POST /generation/questions/quality
```

## 14. API test quality endpoint

Tao file:

```text
tests/api/test_generation_quality_endpoint.py
```

Them:

```python
from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import generation as generation_endpoint
from modules.question_quality.schemas import QualityIssue, QuestionQualityReport


class FakeQdrantClient:
    async def close(self) -> None:
        pass


class FakeQuestionRepository:
    def __init__(self, session) -> None:
        self.source_question = SimpleNamespace(
            id="source-id",
            document_id="document-id",
            marker="Bai",
            marker_number="1",
            statement="Tinh $x+1$.",
            solution=None,
            answer=None,
            subject="math",
            chapter="algebra",
            difficulty="medium",
            skills=["simplify"],
        )

    async def get_question(self, question_id: str):
        if question_id == "source-id":
            return self.source_question
        return None

    async def list_by_document(self, document_id: str):
        return [self.source_question]


class FakeQualityService:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def assess_candidate(self, **kwargs):
        return QuestionQualityReport(
            warnings=[
                QualityIssue(
                    code="missing_solution",
                    message="Generated question does not include a solution",
                    severity="warning",
                    field="solution",
                )
            ],
            blocking_issues=[],
            semantic_duplicates=[],
        )


def test_generation_quality_endpoint_returns_report(monkeypatch) -> None:
    monkeypatch.setattr(
        generation_endpoint,
        "create_qdrant_client",
        lambda: FakeQdrantClient(),
    )
    monkeypatch.setattr(
        generation_endpoint,
        "QuestionRepository",
        FakeQuestionRepository,
    )
    monkeypatch.setattr(
        generation_endpoint,
        "QuestionQualityService",
        FakeQualityService,
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/quality",
        json={
            "source_question_id": "source-id",
            "requested_difficulty": "medium",
            "candidate": {
                "statement": "Tinh $x+2$.",
                "solution": None,
                "answer": "$x+2$",
                "subject": "math",
                "chapter": "algebra",
                "difficulty": "medium",
                "skills": ["simplify"],
                "formulas": [
                    {
                        "latex": "x+2",
                        "normalized_latex": "x+2",
                        "source": "statement",
                    }
                ],
                "quality_warnings": [],
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["can_save"] is True
    assert payload["quality_warnings"] == ["missing_solution"]
    assert payload["warnings"][0]["field"] == "solution"


def test_generation_quality_endpoint_returns_400_for_missing_source(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        generation_endpoint,
        "create_qdrant_client",
        lambda: FakeQdrantClient(),
    )
    monkeypatch.setattr(
        generation_endpoint,
        "QuestionRepository",
        FakeQuestionRepository,
    )

    client = TestClient(app)

    response = client.post(
        "/generation/questions/quality",
        json={
            "source_question_id": "missing",
            "candidate": {
                "statement": "Tinh $x+2$.",
                "solution": None,
                "answer": "$x+2$",
                "subject": "math",
                "chapter": "algebra",
                "difficulty": "medium",
                "skills": ["simplify"],
                "formulas": [
                    {
                        "latex": "x+2",
                        "normalized_latex": "x+2",
                        "source": "statement",
                    }
                ],
                "quality_warnings": [],
            },
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Source question not found"
```

Chay:

```powershell
pytest tests/api/test_generation_quality_endpoint.py -q
```

Ky vong:

```text
2 passed
```

## 15. Test API quality bang Swagger/PowerShell

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
POST /generation/questions/quality
```

Goi PowerShell:

```powershell
$body = @{
  source_question_id = 'ce9b7fc5-fa39-463a-8488-3006a23afa6d'
  requested_difficulty = 'medium'
  candidate = @{
    statement = 'Tinh $x+2$.'
    solution = $null
    answer = '$x+2$'
    subject = 'math'
    chapter = 'algebra'
    difficulty = 'medium'
    skills = @('simplify')
    formulas = @(
      @{
        latex = 'x+2'
        normalized_latex = 'x+2'
        source = 'statement'
      }
    )
    quality_warnings = @()
  }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod `
  -Uri 'http://localhost:8000/generation/questions/quality' `
  -Method Post `
  -ContentType 'application/json; charset=utf-8' `
  -Body $body

$response | ConvertTo-Json -Depth 10
```

Ket qua mong doi:

```json
{
  "can_save": true,
  "quality_warnings": [
    "missing_solution"
  ],
  "warnings": [...],
  "blocking_issues": [],
  "semantic_duplicates": []
}
```

Neu statement trung voi cau da co:

```powershell
statement = 'Su dung cong thuc De Moivre, hay viet so phuc sau duoi dang chinh tac $a+bi$: $z = (\sqrt{3}+i)^6 (1-i)^{10}$'
```

Ky vong:

```json
{
  "can_save": false,
  "quality_warnings": [
    "exact_duplicate_statement",
    ...
  ]
}
```

## 16. Cap nhat API preview/save tests neu can

Do preview bay gio dung quality service, cac test endpoint fake service van pass vi monkeypatch service.

Can chay lai:

```powershell
pytest tests/api/test_generation_preview_endpoint.py -q
pytest tests/api/test_generation_save_endpoint.py -q
pytest tests/api/test_generation_endpoint.py -q
pytest tests/api/test_generation_models.py -q
pytest tests/api/test_generation_router_registration.py -q
pytest tests/api/test_generation_quality_endpoint.py -q
```

Neu test save endpoint bi fail do message duplicate doi, giu lai duplicate check cu trong `save_generated_question` nhu muc 10.

## 17. Integration script quality

Khong bat buoc trong MVP, nhung nen tao script de test nhanh quality.

Tao file:

```text
scripts/test_question_quality.py
```

Them:

```python
import asyncio
import sys

from core.config.settings import settings
from infra.db.repositories.questions import QuestionRepository
from infra.db.session import AsyncSessionLocal
from infra.vector_db.qdrant_client import create_qdrant_client
from infra.vector_db.repositories.embeddings import EmbeddingVectorRepository
from modules.embeddings import GeminiEmbedder
from modules.question_generation.schemas import GeneratedQuestionCandidate
from modules.question_quality import QuestionQualityService
from modules.semantic_search import SemanticSearchService


async def main() -> None:
    document_id = sys.argv[1] if len(sys.argv) > 1 else None

    if not document_id:
        print("Usage:")
        print("  python -m scripts.test_question_quality <document_id>")
        return

    client = create_qdrant_client()

    try:
        async with AsyncSessionLocal() as session:
            question_repository = QuestionRepository(session)
            questions = await question_repository.list_by_document(document_id)

            if not questions:
                print(f"No questions found for document_id: {document_id}")
                return

            source_question = questions[-1]

            semantic_search_service = SemanticSearchService(
                question_repository=question_repository,
                vector_repository=EmbeddingVectorRepository(
                    client=client,
                    dimension=settings.embedding_dimension,
                    question_collection=settings.qdrant_question_collection,
                    formula_collection=settings.qdrant_formula_collection,
                ),
                embedder=GeminiEmbedder(),
            )

            quality_service = QuestionQualityService(
                semantic_search_service=semantic_search_service,
            )

            candidate = GeneratedQuestionCandidate(
                statement=source_question.statement,
                solution=source_question.solution,
                answer=source_question.answer,
                subject=source_question.subject,
                chapter=source_question.chapter,
                difficulty=source_question.difficulty,
                skills=source_question.skills,
                formulas=source_question.formulas,
                quality_warnings=[],
            )

            report = await quality_service.assess_candidate(
                candidate=candidate,
                source_question=source_question,
                existing_questions=questions,
                requested_difficulty=source_question.difficulty,
            )

            print("Can save:", report.can_save)
            print("Warnings:", report.quality_warnings)
            print("Blocking issues:", report.blocking_issues)
            print("Semantic duplicates:", report.semantic_duplicates)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Chay:

```powershell
python -m scripts.test_question_quality 4052feaa-2158-4dd6-8d13-4bf3698e71f1
```

Ky vong voi candidate trung source:

```text
Can save: False
Warnings: ['exact_duplicate_statement', ...]
```

## 18. Chay test tong the

Chay:

```powershell
pytest tests/modules/question_quality -q
pytest tests/modules/question_generation -q
pytest tests/api/test_generation_quality_endpoint.py -q
pytest tests/api -q
pytest tests/modules -q
pytest -q
```

Chay compile:

```powershell
python -m compileall apps/api core infra modules tests scripts
```

Chay integration lien quan:

```powershell
python -m scripts.check_question_embedding_sync
python -m scripts.test_question_generation 4052feaa-2158-4dd6-8d13-4bf3698e71f1
python -m scripts.test_question_quality 4052feaa-2158-4dd6-8d13-4bf3698e71f1
```

## 19. Loi thuong gap

### 19.1 Circular import

Neu gap circular import giua:

```text
modules/question_generation
modules/question_quality
```

Xu ly:

```text
- question_quality chi import schema GeneratedQuestionCandidate.
- question_generation import QuestionQualityService.
- Khong import QuestionGenerationService trong question_quality.
```

### 19.2 Test preview warning fail vi co them missing_solution/missing_answer

Sau khi dung quality service, warnings nhieu hon buoc 11.

Nen assert bang:

```python
assert "no_formula_detected" in preview.candidates[0].quality_warnings
```

Khong nen assert bang exact list neu khong can thu tu.

### 19.3 PowerShell loi ky tu `$`

Neu body co LaTeX:

```text
$x+1$
```

Dung nhay don:

```powershell
statement = 'Tinh $x+1$.'
```

Khong dung nhay kep:

```powershell
statement = "Tinh $x+1$."
```

### 19.4 Semantic duplicate goi Gemini embedding cham

Endpoint quality co semantic search nen co the cham.

MVP chap nhan.

Sau nay co the:

```text
- Tat semantic check bang flag.
- Cache embedding candidate.
- Dua quality semantic check vao background job.
```

### 19.5 Semantic duplicate khong phat hien cau gan giong

Nguyen nhan:

```text
- threshold qua cao.
- embedding chua sync.
- filter subject/chapter/difficulty qua chat.
```

Xu ly:

```text
- Giam semantic_duplicate_threshold tu 0.92 xuong 0.88.
- Chay lai check_question_embedding_sync.
- Tam thoi bo filter difficulty khi search.
```

## 20. Mo rong sau MVP

### 20.1 SymPy validation

Them module:

```text
modules/question_quality/symbolic_validator.py
```

Dung de:

```text
- Parse LaTeX don gian.
- So sanh answer voi expected expression.
- Canh bao symbolic_answer_mismatch.
```

### 20.2 LLM judge

Them:

```text
modules/question_quality/gemini_judge.py
```

Output JSON:

```json
{
  "solvable": true,
  "difficulty": "medium",
  "solution_complete": true,
  "score": 0.86,
  "issues": []
}
```

### 20.3 Review workflow

Tao bang:

```text
generated_questions
  id
  source_question_id
  document_id
  statement
  solution
  answer
  formulas
  status
  quality_report
```

Chi publish vao `questions` khi reviewer approve.

### 20.4 Monitoring va bao tri

Them scripts:

```text
scripts/audit_question_quality.py
scripts/audit_embedding_sync.py
scripts/audit_duplicate_questions.py
```

De kiem tra dinh ky:

```text
- questions trung normalized statement
- questions failed embedding
- Qdrant count lech PostgreSQL
- generated questions co warnings nang
```

## 21. Thu tu trien khai khuyen nghi

Lam lan luot:

```text
1. Tao modules/question_quality/schemas.py.
2. Tao modules/question_quality/service.py.
3. Tao modules/question_quality/__init__.py.
4. Viet tests/modules/question_quality/test_service.py.
5. Chay pytest tests/modules/question_quality -q.
6. Tich hop QuestionQualityService vao QuestionGenerationService.preview_questions.
7. Tich hop QuestionQualityService vao QuestionGenerationService.save_generated_question.
8. Cap nhat tests/modules/question_generation/test_service.py.
9. Chay pytest tests/modules/question_generation -q.
10. Them API models quality vao apps/api/v1/models/generation.py.
11. Them POST /generation/questions/quality vao apps/api/v1/endpoints/generation.py.
12. Viet tests/api/test_generation_quality_endpoint.py.
13. Chay pytest tests/api/test_generation_quality_endpoint.py -q.
14. Chay pytest tests/api -q.
15. Tao scripts/test_question_quality.py.
16. Chay python -m scripts.test_question_quality <document_id>.
17. Chay pytest tests/modules -q.
18. Chay pytest -q.
19. Chay python -m compileall apps/api core infra modules tests scripts.
20. Test Swagger endpoint /generation/questions/quality.
```

## 22. Tieu chi hoan thanh

Buoc 12 MVP hoan tat khi:

```text
1. Co module modules/question_quality.
2. Co QualityIssue, SemanticDuplicateHit, QuestionQualityReport.
3. Co QuestionQualityService.assess_candidate.
4. Exact duplicate duoc danh dau blocking.
5. Invalid formula payload duoc danh dau blocking.
6. Missing formula/solution/answer duoc danh dau warning.
7. Difficulty mismatch/invalid difficulty duoc danh dau warning.
8. Semantic duplicate duoc danh dau warning khi co semantic_search_service.
9. Preview generation gan quality_warnings tu question_quality.
10. Save generation chan blocking issue.
11. API co POST /generation/questions/quality.
12. Unit test question_quality pass.
13. Unit test question_generation cu van pass.
14. API test generation quality pass.
15. Tat ca tests/api pass.
16. Tat ca tests/modules pass.
17. pytest -q pass.
18. compileall toan project khong loi.
19. Integration script quality chay duoc voi document_id that.
```

Sau buoc 12, he thong san sang cho:

```text
- Buoc 13: trien khai he thong va toi uu runtime.
- Them generated_questions review workflow.
- Them frontend hien thi quality warnings.
- Them SymPy/LLM judge de validate dap an sau MVP.
```
