# Mục đích:

# Tạo sẵn nơi xử lý lỗi OCR.
# Ở bước này chưa nên thêm rule sửa lỗi phức tạp.
# Lý do: sửa OCR quá sớm có thể làm sai nội dung toán học hoặc công thức LaTeX.

def fix_common_ocr_errors(text: str) -> str:
    return text
