from types import SimpleNamespace

from modules.embeddings.text_builder import (
    build_formula_embedding_text,
    build_question_embedding_text,
)


def test_build_question_embedding_text() -> None:
    question = SimpleNamespace(
        marker="Bai",
        marker_number="1",
        statement="Tinh $x^2 + 1$.",
        solution="Thay $x = 2$.",
        answer="$5$",
        formulas=[
            {
                "latex": "x^2 + 1",
                "normalized_latex": "x^2 + 1",
                "source": "statement",
            }
        ],
    )

    text = build_question_embedding_text(question)

    assert text.startswith("title: Bai 1 | text:")
    assert "Question type: free_response" in text
    assert "Statement:\nTinh $x^2 + 1$." in text
    assert "Solution:\nThay $x = 2$." in text
    assert "Answer:\n$5$" in text
    assert "Formulas:\n- x^2 + 1" in text


def test_build_question_embedding_text_contains_mcq_choices() -> None:
    question = SimpleNamespace(
        marker="Generated",
        marker_number="3",
        statement="Tinh $1+1$.",
        solution="$1+1=2$.",
        answer="2",
        question_type="multiple_choice",
        choices=[
            {"key": "A", "text": "1", "latex": "1"},
            {"key": "B", "text": "2", "latex": "2", "is_correct": True},
            {"key": "C", "text": "3", "latex": "3"},
            {"key": "D", "text": "4", "latex": "4"},
        ],
        correct_choice="B",
        formulas=[],
    )

    text = build_question_embedding_text(question)

    assert "Statement:\nTinh $1+1$." in text
    assert "Question type: multiple_choice" in text
    assert "Choices:\n- A: 1" in text
    assert "- B: 2 (correct)" in text
    assert "- C: 3" in text
    assert "- D: 4" in text
    assert "Correct choice: B" in text


def test_build_question_embedding_text_handles_empty_mcq_choices() -> None:
    question = SimpleNamespace(
        marker="Generated",
        marker_number="4",
        statement="Tinh $2+2$.",
        solution=None,
        answer=None,
        question_type="multiple_choice",
        choices=[],
        correct_choice=None,
        formulas=[],
    )

    text = build_question_embedding_text(question)

    assert "Question type: multiple_choice" in text
    assert "Statement:\nTinh $2+2$." in text
    assert "Choices:" not in text


def test_build_formula_embedding_text() -> None:
    text = build_formula_embedding_text(r"\int_0^1 x dx")

    assert text == (
        "task: sentence similarity | query: "
        r"mathematical formula: \int_0^1 x dx"
    )

def test_embedding_text_contains_taxonomy_metadata() -> None:
    question = SimpleNamespace(
        marker="Bài",
        marker_number="1",
        statement="Tính tích phân.",
        solution=None,
        answer=None,
        formulas=[],
        subject="Giải tích 1",
        chapter="Chương 2",
        chapter_name="Chương 2",
        topic_name="Tích phân bất định",
        problem_type_name="Tích phân từng phần",
        difficulty="medium",
        skills=["integration_by_parts"],
    )

    text = build_question_embedding_text(question)

    assert "Subject: Giải tích 1" in text
    assert "Chapter: Chương 2" in text
    assert "Topic: Tích phân bất định" in text
    assert "Problem type: Tích phân từng phần" in text
    assert "Difficulty: medium" in text
    assert "Skills: integration_by_parts" in text
