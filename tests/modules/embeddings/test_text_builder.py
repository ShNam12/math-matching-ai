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
    assert "Statement:\nTinh $x^2 + 1$." in text
    assert "Solution:\nThay $x = 2$." in text
    assert "Answer:\n$5$" in text
    assert "Formulas:\n- x^2 + 1" in text


def test_build_formula_embedding_text() -> None:
    text = build_formula_embedding_text(r"\int_0^1 x dx")

    assert text == (
        "task: sentence similarity | query: "
        r"mathematical formula: \int_0^1 x dx"
    )