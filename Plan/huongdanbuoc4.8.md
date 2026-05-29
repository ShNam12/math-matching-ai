# Huong Dan Buoc 4.8: Chuan Hoa Markdown

## 1. Muc tieu

Buoc 4.8 co muc tieu lam sach va chuan hoa Markdown sau khi tai lieu dau vao da duoc doc truc tiep tu file Markdown hoac da duoc chuyen tu PDF sang Markdown.

Markdown sau khi chuan hoa se duoc luu vao PostgreSQL va dung tiep cho cac buoc segmentation, embedding, search va sinh cau hoi sau nay.

Pipeline can dat duoc:

```text
normalize_newlines
remove_control_characters
fix_common_ocr_errors
normalize_math_delimiters
normalize_headings
collapse_excess_blank_lines
ensure_trailing_newline
```

## 2. Cac file lien quan

Trong repo hien tai, cac file can lam viec nam tai:

```text
modules/ingestion/markdown_processing/
  __init__.py
  normalizer.py
  ocr_cleanup.py
  math_normalizer.py
```

File test tam thoi hien co:

```text
scripts/test_markdown_normalizer.py
```

Neu muon theo dung cau truc test lau dai, co the tao them:

```text
tests/modules/ingestion/test_markdown_normalizer.py
tests/modules/ingestion/test_ocr_cleanup.py
tests/modules/ingestion/test_math_normalizer.py
```

## 3. Trang thai hien tai

Repo hien da co khung co ban:

- `normalizer.py` da co `normalize_newlines`, `remove_control_characters`, `collapse_excess_blank_lines`, `ensure_trailing_newline`, `normalize_markdown`.
- `ocr_cleanup.py` da co ham `fix_common_ocr_errors`, nhung hien dang return nguyen ban text.
- `math_normalizer.py` da co `normalize_math_delimiters`, nhung moi replace truc tiep delimiter.
- `scripts/test_markdown_normalizer.py` hien chi in ket qua, chua co assert ro rang.

Can bo sung:

- Chuan hoa heading Markdown.
- Cleanup OCR an toan cho cac loi toan hoc pho bien.
- Chuan hoa delimiter toan tot hon.
- Test co assert de xac nhan output dung ky vong.

## 4. Hoan thien `normalizer.py`

File:

```text
modules/ingestion/markdown_processing/normalizer.py
```

Can dam bao file co cac ham sau:

```python
import re

from modules.ingestion.markdown_processing.math_normalizer import normalize_math_delimiters
from modules.ingestion.markdown_processing.ocr_cleanup import fix_common_ocr_errors


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def remove_control_characters(text: str) -> str:
    return "".join(
        char for char in text
        if char == "\n" or char == "\t" or ord(char) >= 32
    )


def normalize_headings(text: str) -> str:
    lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            lines.append("")
            continue

        stripped = re.sub(r"^(#{1,6})([^\s#])", r"\1 \2", stripped)
        stripped = re.sub(r"^(#{1,6})\s+", r"\1 ", stripped)

        lines.append(stripped)

    return "\n".join(lines)


def collapse_excess_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def ensure_trailing_newline(text: str) -> str:
    return text.rstrip() + "\n"


def normalize_markdown(text: str) -> str:
    text = normalize_newlines(text)
    text = remove_control_characters(text)
    text = fix_common_ocr_errors(text)
    text = normalize_math_delimiters(text)
    text = normalize_headings(text)
    text = collapse_excess_blank_lines(text)
    text = ensure_trailing_newline(text)
    return text
```

Ghi chu:

- `normalize_newlines`: dua newline Windows/macOS cu ve chuan `\n`.
- `remove_control_characters`: loai bo ky tu dieu khien, nhung giu lai newline va tab.
- `normalize_headings`: sua heading Markdown bi thieu khoang trang, vi du `#Title` thanh `# Title`.
- `collapse_excess_blank_lines`: rut gon tu 3 newline lien tiep tro len thanh 2 newline.
- `ensure_trailing_newline`: dam bao output ket thuc bang 1 newline.

## 5. Hoan thien `ocr_cleanup.py`

File:

```text
modules/ingestion/markdown_processing/ocr_cleanup.py
```

Chi nen them cac rule OCR an toan, tranh sua qua manh lam sai noi dung goc.

Noi dung de xuat:

```python
import re


def fix_common_ocr_errors(text: str) -> str:
    text = text.replace("âˆ«", r"\int")

    text = re.sub(r"\bd\s+x\b", "dx", text)

    text = re.sub(
        r"\blim\s+([a-zA-Z])\s*->\s*([^\s,.;]+)",
        r"\\lim_{\1 \\to \2}",
        text,
    )

    text = re.sub(r"(?<=\d)O(?=\d)", "0", text)
    text = re.sub(r"(?<=\d)l(?=\d)", "1", text)

    return text
```

Y nghia cac rule:

```text
âˆ« ... d x -> \int ... dx
lim x -> 0 -> \lim_{x \to 0}
101O1 -> 10101 trong ngu canh giua cac chu so
12l3 -> 1213 trong ngu canh giua cac chu so
```

Khong nen lam:

```text
Thay toan bo O thanh 0
Thay toan bo l thanh 1
Sua tu tieng Anh/tieng Viet bang rule rong
Parse toan bo LaTeX
```

Ly do: OCR cleanup qua manh co the pha noi dung Markdown, van ban thong thuong hoac cong thuc LaTeX hop le.

## 6. Hoan thien `math_normalizer.py`

File:

```text
modules/ingestion/markdown_processing/math_normalizer.py
```

Noi dung de xuat:

```python
import re


def _normalize_formula_spaces(formula: str) -> str:
    return re.sub(r"\s+", " ", formula).strip()


def normalize_math_delimiters(text: str) -> str:
    text = re.sub(
        r"\\\((.*?)\\\)",
        lambda match: f"${_normalize_formula_spaces(match.group(1))}$",
        text,
        flags=re.DOTALL,
    )

    text = re.sub(
        r"\\\[(.*?)\\\]",
        lambda match: f"$$\n{_normalize_formula_spaces(match.group(1))}\n$$",
        text,
        flags=re.DOTALL,
    )

    return text
```

Ket qua mong doi:

```text
\( x^2   +   1 \)
```

Thanh:

```text
$x^2 + 1$
```

Va:

```text
\[ x^2   +   1 \]
```

Thanh:

```text
$$
x^2 + 1
$$
```

O buoc 4.8, chua nen parse LaTeX phuc tap. Muc tieu chi la dua Markdown ve dang sach, on dinh, de cac buoc sau xu ly tiep.

## 7. Cap nhat script test nhanh

File:

```text
scripts/test_markdown_normalizer.py
```

Co the thay noi dung hien tai bang:

```python
from modules.ingestion.markdown_processing.normalizer import normalize_markdown


def test_markdown_normalizer_basic():
    text = "#Title\r\n\r\n\r\nText with math \\(x^2   +   1\\)\r\n"
    result = normalize_markdown(text)

    assert result == "# Title\n\nText with math $x^2 + 1$\n"


def test_markdown_normalizer_block_math():
    text = "Formula:\n\\[ x^2   +   1 \\]"
    result = normalize_markdown(text)

    assert "$$\nx^2 + 1\n$$" in result
    assert result.endswith("\n")


def test_markdown_normalizer_ocr_cleanup():
    text = "Compute âˆ« x d x and lim x -> 0"
    result = normalize_markdown(text)

    assert r"\int x dx" in result
    assert r"\lim_{x \to 0}" in result


if __name__ == "__main__":
    test_markdown_normalizer_basic()
    test_markdown_normalizer_block_math()
    test_markdown_normalizer_ocr_cleanup()
    print("Markdown normalizer tests passed")
```

Chay:

```powershell
python scripts/test_markdown_normalizer.py
```

Neu dung pytest, nen dua test vao:

```text
tests/modules/ingestion/test_markdown_normalizer.py
```

Va chay:

```powershell
pytest tests/modules/ingestion/test_markdown_normalizer.py
```

## 8. Test cases nen co

Can kiem tra toi thieu cac case sau:

```text
Windows newline \r\n -> \n
macOS newline cu \r -> \n
Control character bi loai bo
Nhieu dong trong lien tiep bi rut gon
#Title -> # Title
##   Title -> ## Title
\(x^2\) -> $x^2$
\[x^2\] -> $$...$$
âˆ« x d x -> \int x dx
lim x -> 0 -> \lim_{x \to 0}
Output luon ket thuc bang newline
```

## 9. Tich hop voi ingestion service

Sau khi `normalize_markdown` on dinh, `modules/ingestion/service.py` can goi ham nay sau khi da co markdown raw:

```python
from modules.ingestion.markdown_processing.normalizer import normalize_markdown


normalized_markdown = normalize_markdown(raw_markdown)
```

Luong xu ly mong doi:

```text
PDF -> Gemini -> raw markdown -> normalize_markdown -> save PostgreSQL
Markdown file -> decode bytes -> normalize_markdown -> save PostgreSQL
```

Khong nen de API service tu xu ly tung buoc Markdown. API service chi nen dieu phoi upload va trang thai. Logic chuan hoa Markdown nen nam trong `modules/ingestion/markdown_processing`.

## 10. Tieu chi hoan thanh

Buoc 4.8 duoc xem la hoan thanh khi:

```text
normalizer.py co du pipeline chuan hoa
ocr_cleanup.py co cac rule OCR an toan
math_normalizer.py chuan hoa inline va block math
normalize_headings da xu ly heading thieu khoang trang
script test nhanh chay pass
output Markdown luon sach va ket thuc bang newline
ingestion service co the goi normalize_markdown truoc khi luu database
```

Lenh kiem tra nhanh:

```powershell
python scripts/test_markdown_normalizer.py
```

Ket qua mong doi:

```text
Markdown normalizer tests passed
```

## 11. Luu y encoding

Mot so comment tieng Viet trong cac file hien tai co dau hieu bi loi encoding, vi du dang hien thanh:

```text
Chuyá»ƒn
Loáº¡i
chuáº©n
```

Nen sua comment sang tieng Viet khong dau hoac dam bao file duoc luu bang UTF-8.

De tranh loi encoding lap lai, khuyen nghi trong source code Python nen dung comment khong dau:

```python
# Chuan hoa newline ve dang \n.
# Loai bo ky tu dieu khien, giu lai newline va tab.
```

Hoac bo bot comment neu code da tu giai thich duoc.
