from modules.ingestion.markdown_processing.normalizer import normalize_markdown


def test_normalize_markdown_pipeline() -> None:
    text = "#Title\r\n\r\n\r\nText with math \\(x^2   +   1\\)\r\n"

    result = normalize_markdown(text)

    assert result == "# Title\n\nText with math $x^2 + 1$\n"


def test_remove_control_characters() -> None:
    result = normalize_markdown("Text\x00 with\x07 control characters")

    assert result == "Text with control characters\n"


def test_ensure_trailing_newline() -> None:
    result = normalize_markdown("Text without newline")

    assert result == "Text without newline\n"