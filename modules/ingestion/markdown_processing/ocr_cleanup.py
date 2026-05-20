# Mục đích:

# Tạo sẵn nơi xử lý lỗi OCR.
# Ở bước này chưa nên thêm rule sửa lỗi phức tạp.
# Lý do: sửa OCR quá sớm có thể làm sai nội dung toán học hoặc công thức LaTeX.

import re


def fix_common_ocr_errors(text: str) -> str:
    text = text.replace("Ã¢Ë†Â«", r"\int")

    text = re.sub(r"\bd\s+x\b", "dx", text)

    text = re.sub(
        r"\blim\s+([a-zA-Z])\s*->\s*([^\s,.;]+)",
        r"\\lim_{\1 \\to \2}",
        text,
    )

    text = re.sub(r"(?<=\d)O(?=\d)", "0", text)
    text = re.sub(r"(?<=\d)l(?=\d)", "1", text)

    return text