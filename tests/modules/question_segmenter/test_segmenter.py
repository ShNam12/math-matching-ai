from modules.question_segmenter import segment_questions


def test_segment_questions_from_markdown() -> None:
    markdown = r"""
ĐH Bách Khoa Hà Nội

Bài 1. Tính $x^2 + 1$.
Lời giải:
Ta thay $x = 2$.
**Đáp án:** $5$

Câu hỏi 2: Tính $\int_0^1 x dx$.
"""

    result = segment_questions(markdown)

    assert result.preamble == "ĐH Bách Khoa Hà Nội"
    assert len(result.questions) == 2

    first = result.questions[0]
    assert first.sequence_number == 1
    assert first.question_type == "free_response"
    assert first.choices == []
    assert first.correct_choice is None
    assert first.marker == "Bài"
    assert first.marker_number == "1"
    assert first.statement == "Tính $x^2 + 1$."
    assert first.solution == "Ta thay $x = 2$."
    assert first.answer == "$5$"
    assert len(first.formulas) == 3
    assert [formula.source for formula in first.formulas] == [
        "statement",
        "solution",
        "answer",
    ]

    second = result.questions[1]
    assert second.sequence_number == 2
    assert second.marker == "Câu hỏi"
    assert second.marker_number == "2"
    assert second.solution is None
    assert second.answer is None
    assert len(second.formulas) == 1


def test_document_without_question_marker_returns_empty_list() -> None:
    result = segment_questions("# Chapter 1\n\nTheory content")

    assert result.questions == []
    assert result.preamble == "# Chapter 1\n\nTheory content"


def test_keep_subquestions_inside_parent_question() -> None:
    markdown = r"""
Bài 27. Viết các số phức sau dưới dạng lượng giác:
(a) $z=1+i$
(b) $z=1-i$
"""

    result = segment_questions(markdown)

    assert len(result.questions) == 1

    question = result.questions[0]

    assert "(a)" in question.statement
    assert "(b)" in question.statement
    assert len(question.formulas) == 2
