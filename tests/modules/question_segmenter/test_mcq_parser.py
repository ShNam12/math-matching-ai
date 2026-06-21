from modules.question_segmenter import segment_questions
from modules.question_segmenter.mcq_parser import parse_mcq


def test_parse_dot_choices_with_answer_line() -> None:
    parsed = parse_mcq(
        """
Tính $1+1$.
A. 1
B. 2
C. 3
D. 4
Đáp án: B
"""
    )

    assert parsed is not None
    assert parsed.statement == "Tính $1+1$."
    assert parsed.correct_choice == "B"
    assert parsed.answer == "B"
    assert [choice.key for choice in parsed.choices] == ["A", "B", "C", "D"]
    assert [choice.is_correct for choice in parsed.choices] == [
        False,
        True,
        False,
        False,
    ]


def test_parse_parenthesized_choices() -> None:
    parsed = parse_mcq(
        """
Chọn nguyên hàm của $2x$.
(A) $x^2 + C$
(B) $2x + C$
(C) $x + C$
(D) $2 + C$
""",
        answer="A",
    )

    assert parsed is not None
    assert parsed.correct_choice == "A"
    assert parsed.choices[0].text == "$x^2 + C$"
    assert parsed.choices[0].is_correct is True


def test_parse_without_answer_keeps_choices() -> None:
    parsed = parse_mcq(
        """
Tính giới hạn.
A) 0
B) 1
C) 2
D) Không tồn tại
"""
    )

    assert parsed is not None
    assert parsed.correct_choice is None
    assert parsed.answer is None
    assert all(not choice.is_correct for choice in parsed.choices)


def test_choice_latex_is_preserved() -> None:
    parsed = parse_mcq(
        r"""
Tính tích phân.
A. $\frac{1}{2}$
B. $\frac{1}{3}$
C. $\frac{1}{4}$
D. $\frac{1}{5}$
Đáp án: C
"""
    )

    assert parsed is not None
    assert parsed.choices[2].text == r"$\frac{1}{4}$"


def test_free_response_text_is_not_detected_as_mcq() -> None:
    parsed = parse_mcq(
        """
Viết các số phức sau dưới dạng lượng giác:
(a) $z=1+i$
(b) $z=1-i$
"""
    )

    assert parsed is None


def test_segment_questions_marks_mcq_and_extracts_choice_formulas() -> None:
    result = segment_questions(
        r"""
Bài 1. Tính tích phân $\int_0^1 x dx$.
A. $0$
B. $\frac{1}{2}$
C. $1$
D. $2$
Đáp án: B
"""
    )

    question = result.questions[0]

    assert question.question_type == "multiple_choice"
    assert question.statement == r"Tính tích phân $\int_0^1 x dx$."
    assert question.correct_choice == "B"
    assert question.answer == "B"
    assert question.choices[1].is_correct is True
    assert [formula.source for formula in question.formulas] == [
        "statement",
        "choice",
        "choice",
        "choice",
        "choice",
    ]
