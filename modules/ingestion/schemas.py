# Nơi đặt schema nội bộ cho ingestion.
# Mục đích:

# Tạo schema chuẩn cho kết quả ingestion.
# Hiện tại chưa nhất thiết dùng ngay.
# Các bước sau có thể dùng để trả kết quả nội bộ thay vì truyền dữ liệu rời rạc.

from pydantic import BaseModel


class IngestionResult(BaseModel):
    markdown_content: str
    markdown_checksum: str
