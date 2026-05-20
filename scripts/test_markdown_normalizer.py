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
    text = "Compute Ã¢Ë†Â« x d x and lim x -> 0"
    result = normalize_markdown(text)

    assert r"\int x dx" in result
    assert r"\lim_{x \to 0}" in result


if __name__ == "__main__":
    test_markdown_normalizer_basic()
    test_markdown_normalizer_block_math()
    test_markdown_normalizer_ocr_cleanup()
    print("Markdown normalizer tests passed")