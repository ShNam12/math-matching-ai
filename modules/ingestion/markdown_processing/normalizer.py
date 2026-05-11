


import re

from modules.ingestion.markdown_processing.math_normalizer import normalize_math_delimiters
from modules.ingestion.markdown_processing.ocr_cleanup import fix_common_ocr_errors


def normalize_newlines(text: str) -> str:  # Chuyển toàn bộ newline Windows/macOS cũ về dạng chuẩn \n.
    return text.replace("\r\n", "\n").replace("\r", "\n")


def remove_control_characters(text: str) -> str: # Loại bỏ các ký tự điều khiển không mong muốn (trừ newline và tab).
    return "".join(
        char for char in text
        if char == "\n" or char == "\t" or ord(char) >= 32
    )


def collapse_excess_blank_lines(text: str) -> str: # Giảm nhiều hơn 2 newline liên tiếp xuống còn 2 để tránh khoảng trắng quá lớn.
    return re.sub(r"\n{3,}", "\n\n", text)


def ensure_trailing_newline(text: str) -> str: # Đảm bảo văn bản có newline ở cuối.
    return text.rstrip() + "\n"


def normalize_markdown(text: str) -> str: # Hàm chính để chuẩn hóa markdown, gọi các bước xử lý lần lượt.
    text = normalize_newlines(text)
    text = remove_control_characters(text)
    text = fix_common_ocr_errors(text)
    text = normalize_math_delimiters(text)
    text = collapse_excess_blank_lines(text)
    text = ensure_trailing_newline(text)
    return text
