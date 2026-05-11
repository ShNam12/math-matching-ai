# Mục đích:

# Tạo trước interface xử lý PDF.
# Bước này chưa gọi Gemini thật.
# Nếu upload PDF ở bước này, ingestion có thể chuyển sang trạng thái failed, điều đó là chấp nhận được.
# Lý do làm như vậy:

# Nên cho Markdown chạy end-to-end trước.
# PDF + Gemini là phần phức tạp hơn, nên tách sang bước sau.

async def convert_pdf_to_markdown(
    *,
    filename: str,
    content: bytes,
) -> str:
    raise NotImplementedError("PDF to Markdown conversion is not implemented yet")
