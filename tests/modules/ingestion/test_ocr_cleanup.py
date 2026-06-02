from modules.ingestion.markdown_processing.ocr_cleanup import (
    fix_common_ocr_errors,
)


def test_normalize_differential() -> None:
    assert fix_common_ocr_errors("integrate x d x") == "integrate x dx"


def test_normalize_limit() -> None:
    assert fix_common_ocr_errors("lim x -> 0") == r"\lim_{x \to 0}"


def test_replace_ocr_digits_between_numbers() -> None:
    assert fix_common_ocr_errors("1O1 and 2l2") == "101 and 212"