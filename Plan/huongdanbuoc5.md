# Huong Dan Buoc 5: Tach Cau Hoi Va Giai Phap

## 1. Muc tieu

Buoc 5 xay dung module tach cau hoi va noi dung tu Markdown da duoc ingestion xu ly.

Luong xu ly:

```text
documents.markdown_content
 -> nhan dien tung bai toan
 -> tach de bai / loi giai / dap an
 -> trich xuat cong thuc LaTeX
 -> tra ve danh sach object Python
```

Buoc 5 chua lam:

```text
- Chua tao bang questions.
- Chua ghi database.
- Chua them API.
- Chua sua frontend.
- Chua dung Gemini de phan loai.
```

Nhung viec nay thuoc buoc 6 hoac giai doan sau.

Dau vao da co san tai:

```text
infra/db/models.py
```

Field:

```python
Document.markdown_content
```

## 2. Quyet dinh cau truc thu muc

Tai lieu thiet ke hien co hai cach dat thu muc:

```text
Implementation_plan.md: modules/question_segmenter
Folder_structure.md:     modules/parser/segmentation
```

Voi code hien tai, nen chon cau truc don gian va nhat quan voi `modules/ingestion`:

```text
modules/
  question_segmenter/
    __init__.py
    schemas.py
    patterns.py
    formula_extractor.py
    segmenter.py

tests/
  modules/
    question_segmenter/
      __init__.py
      test_formula_extractor.py
      test_segmenter.py

scripts/
  test_question_segmenter.py
```

Khong tao dong thoi ca hai cau truc.

## 3. Tao schema ket qua

Tao file:

```text
modules/question_segmenter/schemas.py
```

Them noi dung:

```python
from typing import Literal

from pydantic import BaseModel


FormulaSource = Literal["statement", "solution", "answer"]


class ExtractedFormula(BaseModel):
    latex: str
    normalized_latex: str
    source: FormulaSource


class SegmentedQuestion(BaseModel):
    sequence_number: int
    marker: str
    marker_number: str
    statement: str
    solution: str | None = None
    answer: str | None = None
    formulas: list[ExtractedFormula]


class SegmentationResult(BaseModel):
    preamble: str | None = None
    questions: list[SegmentedQuestion]
```

Y nghia cac field:

```text
marker          Vi du: "Bai", "Cau hoi", "Vi du".
marker_number   Vi du: "27", "2", "1.1".
statement       De bai.
solution        Loi giai neu co.
answer          Dap an neu co.
formulas        Cong thuc thuoc tung phan.
preamble        Noi dung dau tai lieu: ten truong, ten chuong...
```

Khong dua `document_id` vao schema nay. Module segmentation chi xu ly van ban, khong phu thuoc database.

## 4. Khai bao regex

Tao file:

```text
modules/question_segmenter/patterns.py
```

Them noi dung:

```python
import re


QUESTION_START_RE = re.compile(
    r"""
    ^[ \t]*
    (?:\#{1,6}[ \t]*)?
    (?P<marker>Bài(?:[ \t]+tập)?|Câu(?:[ \t]+hỏi)?|Ví[ \t]+dụ)
    [ \t]*
    (?P<number>\d+(?:[.-]\d+)*)
    [ \t]*
    [.):\-]?
    [ \t]*
    (?P<rest>.*)
    $
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)


SECTION_MARKER_RE = re.compile(
    r"""
    ^[ \t]*
    (?:\#{1,6}[ \t]*)?
    (?:\*\*|__)?
    (?P<section>
        Lời[ \t]+giải
        |Hướng[ \t]+dẫn[ \t]+giải
        |Giải
        |Đáp[ \t]+án
    )
    (?:\*\*|__)?
    [ \t]*
    [:\-]?
    [ \t]*
    (?P<rest>.*)
    $
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)
```

Regex nay ho tro:

```text
Bai 1. ...
Bai tap 2: ...
Cau 3) ...
Cau hoi 4 - ...
Vi du 5. ...
## Bai 6
```

Mau hien tai trong `Plan/bttx.md` dung dang:

```text
Bai 27. ...
```

Do do khong duoc gia dinh moi cau hoi luon la heading Markdown.

## 5. Trich xuat cong thuc

Tao file:

```text
modules/question_segmenter/formula_extractor.py
```

Them noi dung:

```python
import re

from modules.question_segmenter.schemas import ExtractedFormula, FormulaSource


FORMULA_RE = re.compile(
    r"""
    (?<!\\)\$\$(?P<display>.*?)(?<!\\)\$\$
    |
    (?<!\\)\$(?P<inline>[^\n$]+?)(?<!\\)\$
    |
    \\\[(?P<bracket>.*?)\\\]
    |
    \\\((?P<paren>.*?)\\\)
    """,
    re.DOTALL | re.VERBOSE,
)


def normalize_formula(formula: str) -> str:
    return re.sub(r"\s+", " ", formula).strip()


def extract_formulas(
    text: str | None,
    *,
    source: FormulaSource,
) -> list[ExtractedFormula]:
    if not text:
        return []

    formulas = []

    for match in FORMULA_RE.finditer(text):
        latex = next(
            value
            for value in match.groupdict().values()
            if value is not None
        ).strip()

        formulas.append(
            ExtractedFormula(
                latex=latex,
                normalized_latex=normalize_formula(latex),
                source=source,
            )
        )

    return formulas
```

Ingestion hien da chuan hoa:

```text
\(...\) -> $...$
```

Tai:

```text
modules/ingestion/markdown_processing/math_normalizer.py
```

Tuy nhien extractor van ho tro ca hai dang de co the dung doc lap va xu ly du lieu cu.

Khong nen dung SymPy de thay doi noi dung LaTeX goc. SymPy co the khong parse duoc mot so bieu thuc hoc thuat hoac lam mat dinh dang. O buoc nay chi can:

```text
- Trich xuat cong thuc.
- Chuan hoa khoang trang.
- Giu nguyen latex goc de truy vet.
```

## 6. Tach de bai, loi giai va dap an

Tao file:

```text
modules/question_segmenter/segmenter.py
```

Them noi dung:

```python
from modules.question_segmenter.formula_extractor import extract_formulas
from modules.question_segmenter.patterns import (
    QUESTION_START_RE,
    SECTION_MARKER_RE,
)
from modules.question_segmenter.schemas import (
    SegmentationResult,
    SegmentedQuestion,
)


def _get_section_name(section_marker: str) -> str:
    normalized = section_marker.casefold()

    if normalized == "đáp án":
        return "answer"

    return "solution"


def _split_question_sections(content: str) -> tuple[str, str | None, str | None]:
    sections: dict[str, list[str]] = {
        "statement": [],
        "solution": [],
        "answer": [],
    }

    current_section = "statement"

    for line in content.splitlines():
        match = SECTION_MARKER_RE.match(line)

        if match:
            current_section = _get_section_name(match.group("section"))
            rest = match.group("rest").strip()

            if rest:
                sections[current_section].append(rest)

            continue

        sections[current_section].append(line)

    statement = "\n".join(sections["statement"]).strip()
    solution = "\n".join(sections["solution"]).strip() or None
    answer = "\n".join(sections["answer"]).strip() or None

    return statement, solution, answer


def segment_questions(markdown: str) -> SegmentationResult:
    matches = list(QUESTION_START_RE.finditer(markdown))

    if not matches:
        return SegmentationResult(
            preamble=markdown.strip() or None,
            questions=[],
        )

    preamble = markdown[:matches[0].start()].strip() or None
    questions = []

    for index, match in enumerate(matches):
        next_start = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(markdown)
        )

        remaining_content = markdown[match.end():next_start]
        first_line_content = match.group("rest").strip()

        content = "\n".join(
            part
            for part in [first_line_content, remaining_content.strip()]
            if part
        )

        statement, solution, answer = _split_question_sections(content)

        formulas = [
            *extract_formulas(statement, source="statement"),
            *extract_formulas(solution, source="solution"),
            *extract_formulas(answer, source="answer"),
        ]

        questions.append(
            SegmentedQuestion(
                sequence_number=index + 1,
                marker=match.group("marker"),
                marker_number=match.group("number"),
                statement=statement,
                solution=solution,
                answer=answer,
                formulas=formulas,
            )
        )

    return SegmentationResult(
        preamble=preamble,
        questions=questions,
    )
```

Tao file:

```text
modules/question_segmenter/__init__.py
```

Them noi dung:

```python
from modules.question_segmenter.segmenter import segment_questions

__all__ = ["segment_questions"]
```

## 7. Viet unit test

Tao file:

```text
tests/modules/question_segmenter/__init__.py
```

De file rong.

Tao file:

```text
tests/modules/question_segmenter/test_formula_extractor.py
```

Them noi dung:

```python
from modules.question_segmenter.formula_extractor import extract_formulas


def test_extract_inline_and_block_formulas() -> None:
    text = """
    Tính $x^2   + 1$ và:
    $$
    \\int_0^1 x dx
    $$
    """

    formulas = extract_formulas(text, source="statement")

    assert len(formulas) == 2
    assert formulas[0].normalized_latex == "x^2 + 1"
    assert formulas[1].normalized_latex == r"\int_0^1 x dx"
    assert formulas[0].source == "statement"
```

Tao file:

```text
tests/modules/question_segmenter/test_segmenter.py
```

Them noi dung:

```python
from modules.question_segmenter.segmenter import segment_questions


def test_segment_questions_from_markdown() -> None:
    markdown = """
ĐH Bách Khoa Hà Nội

Bài 1. Tính $x^2 + 1$.
Lời giải:
Ta thay $x = 2$.
Đáp án: $5$

Câu hỏi 2: Tính $\\int_0^1 x dx$.
"""

    result = segment_questions(markdown)

    assert result.preamble == "ĐH Bách Khoa Hà Nội"
    assert len(result.questions) == 2

    first = result.questions[0]
    assert first.marker == "Bài"
    assert first.marker_number == "1"
    assert first.statement == "Tính $x^2 + 1$."
    assert first.solution == "Ta thay $x = 2$."
    assert first.answer == "$5$"
    assert len(first.formulas) == 3

    second = result.questions[1]
    assert second.marker == "Câu hỏi"
    assert second.marker_number == "2"
    assert second.solution is None
    assert second.answer is None


def test_document_without_question_marker_returns_empty_list() -> None:
    result = segment_questions("# Chương 1\n\nNội dung lý thuyết")

    assert result.questions == []
    assert result.preamble == "# Chương 1\n\nNội dung lý thuyết"


def test_keep_subquestions_inside_parent_question() -> None:
    markdown = """
Bài 27. Viết các số phức sau dưới dạng lượng giác:
(a) $z=1+i$
(b) $z=1-i$
"""

    result = segment_questions(markdown)

    assert len(result.questions) == 1
    assert "(a)" in result.questions[0].statement
    assert "(b)" in result.questions[0].statement
    assert len(result.questions[0].formulas) == 2
```

Chay:

```powershell
pytest tests/modules/question_segmenter -q
```

## 8. Test voi file that

Tao file:

```text
scripts/test_question_segmenter.py
```

Them noi dung:

```python
from pathlib import Path

from modules.question_segmenter.segmenter import segment_questions


def main() -> None:
    markdown = Path("Plan/bttx.md").read_text(encoding="utf-8")
    result = segment_questions(markdown)

    print("Preamble:", result.preamble)
    print("Questions:", len(result.questions))

    for question in result.questions:
        print()
        print(f"{question.marker} {question.marker_number}")
        print(question.statement)
        print("Formula count:", len(question.formulas))


if __name__ == "__main__":
    main()
```

Chay:

```powershell
python -m scripts.test_question_segmenter
```

Ket qua mong doi voi `Plan/bttx.md`:

```text
Questions: 2
Bai 27
Formula count: 4

Bai 28
Formula count: 3
```

## 9. Chua tach cac y nho `(a)`, `(b)`

Trong mau hien tai, `Bai 27` co bon y nho. O buoc 5 nen giu chung trong mot `statement`.

Ly do:

```text
- Cac y nho thuong dung chung yeu cau.
- Bang questions o buoc 6 chua duoc thiet ke.
- Tach y nho som se can quan he parent_question_id.
```

Sau khi MVP chay on, co the bo sung:

```text
subquestions: list[SubQuestion]
```

Khong nen them ngay trong lan trien khai dau tien.

## 10. SymPy la phan mo rong

Chua can them dependency trong lan trien khai dau tien.

Sau khi regex chay on, neu can kiem tra cu phap cong thuc, them file:

```text
modules/question_segmenter/math_validator.py
```

SymPy chi nen dung nhu validator tuy chon:

```python
from sympy.parsing.latex import parse_latex


def can_parse_latex(latex: str) -> bool:
    try:
        parse_latex(latex)
        return True
    except Exception:
        return False
```

Khong loai bo cau hoi neu SymPy parse that bai. Cong thuc LaTeX hop le cho hien thi chua chac da phu hop voi parser cua SymPy.

## 11. Cac file khong chinh o buoc 5

Giu nguyen:

```text
infra/db/models.py
infra/db/repositories/documents.py
apps/api/v1/endpoints/documents.py
apps/api/v1/services/documents.py
apps/frontend/
```

O buoc 6 moi lam luong:

```text
Document.markdown_content
 -> segment_questions(markdown)
 -> luu tung SegmentedQuestion vao bang questions
```

## 12. Thu tu thuc hien

1. Tao thu muc `modules/question_segmenter`.
2. Tao `schemas.py`.
3. Tao `patterns.py`.
4. Tao `formula_extractor.py`.
5. Tao `segmenter.py`.
6. Tao `__init__.py`.
7. Tao unit test.
8. Chay unit test.
9. Tao script test voi `Plan/bttx.md`.
10. Kiem tra file that tach dung hai cau hoi.

## 13. Tieu chi hoan thanh

Buoc 5 hoan tat khi:

```text
1. Co module modules/question_segmenter.
2. Nhan dien duoc Bai, Bai tap, Cau, Cau hoi, Vi du.
3. Ho tro marker dang heading va marker nam cung dong voi de bai.
4. Tach duoc statement, solution, answer.
5. Trich xuat duoc inline va block LaTeX.
6. Khong phu thuoc PostgreSQL, API hoac frontend.
7. File Plan/bttx.md duoc tach thanh dung 2 cau hoi.
8. pytest tests/modules/question_segmenter -q chay thanh cong.
```

Sau do moi chuyen sang buoc 6: thiet ke bang `questions`, repository va tich hop segmentation voi document da ingestion.
