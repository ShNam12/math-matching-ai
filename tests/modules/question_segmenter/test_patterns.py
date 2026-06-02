from modules.question_segmenter.patterns import (
    QUESTION_START_RE,
    SECTION_MARKER_RE,
)


def test_match_question_on_same_line() -> None:
    match = QUESTION_START_RE.match("Bài 27. Viết các số phức sau")

    assert match is not None
    assert match.groupdict() == {
        "marker": "Bài",
        "number": "27",
        "rest": "Viết các số phức sau",
    }


def test_match_markdown_heading_question() -> None:
    match = QUESTION_START_RE.match("## Câu hỏi 2: Tính tích phân")

    assert match is not None
    assert match.group("marker") == "Câu hỏi"
    assert match.group("number") == "2"
    assert match.group("rest") == "Tính tích phân"


def test_match_bold_answer_marker() -> None:
    match = SECTION_MARKER_RE.match("**Đáp án:** $5$")

    assert match is not None
    assert match.group("section") == "Đáp án"
    assert match.group("rest") == "$5$"


def test_match_bold_solution_marker() -> None:
    match = SECTION_MARKER_RE.match("**Lời giải**: Thay x = 2")

    assert match is not None
    assert match.group("section") == "Lời giải"
    assert match.group("rest") == "Thay x = 2"