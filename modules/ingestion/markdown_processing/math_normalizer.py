# Mục đích:

# Chuẩn hóa delimiter công thức toán từ dạng LaTeX phổ biến sang dạng Markdown-friendly hơn.

def normalize_math_delimiters(text: str) -> str:
    text = text.replace("\\(", "$")
    text = text.replace("\\)", "$")
    text = text.replace("\\[", "$$")
    text = text.replace("\\]", "$$")
    return text
