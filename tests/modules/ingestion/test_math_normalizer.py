from modules.ingestion.markdown_processing.math_normalizer import (
    normalize_math_delimiters,
)


def test_normalize_inline_math() -> None:
    result = normalize_math_delimiters(r"Formula: \( x^2   +   1 \)")

    assert result == "Formula: $x^2 + 1$"


def test_normalize_block_math() -> None:
    result = normalize_math_delimiters(r"Formula: \[ x^2   +   1 \]")

    assert result == "Formula: $$\nx^2 + 1\n$$"