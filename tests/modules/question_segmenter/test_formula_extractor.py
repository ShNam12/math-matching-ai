from modules.question_segmenter.formula_extractor import extract_formulas


def test_extract_inline_and_block_formulas() -> None:
    text = r"""
    Tính $x^2   +   1$ và:
    $$
    \int_0^1   x dx
    $$
    """

    formulas = extract_formulas(text, source="statement")

    assert len(formulas) == 2

    assert formulas[0].latex == "x^2   +   1"
    assert formulas[0].normalized_latex == "x^2 + 1"
    assert formulas[0].source == "statement"

    assert formulas[1].latex == r"\int_0^1   x dx"
    assert formulas[1].normalized_latex == r"\int_0^1 x dx"
    assert formulas[1].source == "statement"


def test_extract_legacy_math_delimiters() -> None:
    text = r"""
    Inline: \(x^2 + 1\)
    Block: \[\int_0^1 x dx\]
    """

    formulas = extract_formulas(text, source="solution")

    assert len(formulas) == 2
    assert formulas[0].normalized_latex == "x^2 + 1"
    assert formulas[1].normalized_latex == r"\int_0^1 x dx"
    assert all(formula.source == "solution" for formula in formulas)


def test_empty_text_returns_empty_list() -> None:
    assert extract_formulas(None, source="answer") == []
    assert extract_formulas("", source="answer") == []