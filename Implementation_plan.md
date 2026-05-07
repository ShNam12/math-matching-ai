# Kế hoạch triển khai dự án AI Matching

## Giai đoạn 1: Chuẩn bị môi trường và khởi tạo dự án

### Bước 1: Cài đặt môi trường phát triển
* Cài đặt Docker và Docker Compose
* Cài đặt IDE: VS Code hoặc PyCharm, cùng các extensions (Python, Docker, Git, etc.)

### Bước 2: Khởi tạo dự án
* Khởi tạo repository Git (GitHub, GitLab, Bitbucket)
* Tạo cấu trúc thư mục theo mô hình đã định sẵn (`apps/`, `modules/`, `infra/`, `tests/`, v.v.)
* Cài đặt các thư viện cần thiết trong `requirements.txt`
* Cấu hình Docker (`Dockerfile` và `docker-compose.yml` cho môi trường phát triển)
* Khởi tạo môi trường ảo (virtualenv) và cài đặt các gói phụ thuộc

---

## Giai đoạn 2: Xây dựng backend cơ bản

### Bước 3: Xây dựng API với FastAPI
* Khởi tạo ứng dụng FastAPI cơ bản trong `apps/api/`
* Cấu hình FastAPI trong `main.py` và chạy ứng dụng trên `http://localhost:8000`
* Xây dựng API Endpoints cơ bản:
  * `POST /documents/upload` - Tải tài liệu lên
  * `GET /documents/{id}` - Lấy thông tin tài liệu
  * `GET /documents/{id}/status` - Kiểm tra trạng thái xử lý

### Bước 4: Xử lý tài liệu đầu vào
* Tạo module để tiếp nhận tài liệu PDF và Markdown
* Tích hợp Google Gemini API để chuyển PDF sang Markdown
* Tiến hành chuẩn hóa Markdown (sửa lỗi OCR, chuẩn hóa công thức toán học)
* Lưu trữ tài liệu gốc vào Cloudflare R2 và Markdown vào PostgreSQL

---

## Giai đoạn 3: Tách câu hỏi và nội dung

### Bước 5: Tách câu hỏi và giải pháp
* Xây dựng module `question_segmenter` để tách câu hỏi và giải pháp
* Dùng regex và phương pháp phân tích văn bản để nhận diện câu hỏi (ví dụ: "Bài 1", "Câu hỏi 2")
* Sử dụng LaTeX parser hoặc SymPy để tách và chuẩn hóa các công thức toán học

### Bước 6: Tạo cấu trúc dữ liệu cho câu hỏi
* Thiết kế bảng `questions` trong PostgreSQL để lưu trữ câu hỏi (bao gồm đề bài, giải pháp, đáp án, công thức)
* Gán metadata cho câu hỏi: môn học, chương, độ khó, kỹ năng yêu cầu

---

## Giai đoạn 4: Tạo và lưu embedding

### Bước 7: Tạo embedding cho câu hỏi
* Chọn mô hình embedding (Sentence-BERT, OpenAI Embedding API)
* Tạo vector embedding cho câu hỏi và công thức toán học
* Lưu embedding vào Vector DB (Qdrant hoặc Pinecone)

### Bước 8: Lưu trữ câu hỏi và embedding
* Lưu câu hỏi vào database PostgreSQL và embedding vào vector DB
* Kiểm tra và tối ưu hoá quy trình lưu trữ (như đồng bộ dữ liệu giữa database và vector DB)

---

## Giai đoạn 5: Tìm kiếm và Matching

### Bước 9: Xây dựng hệ thống tìm kiếm thông minh
* Tạo API tìm kiếm theo ngữ nghĩa:
  * Tìm kiếm câu hỏi theo từ khóa
  * Tìm kiếm câu hỏi theo chủ đề
  * Tìm kiếm câu hỏi theo độ khó
* Sử dụng Qdrant để tìm kiếm thông qua vector embeddings

### Bước 10: Tìm kiếm theo công thức toán học
* Tạo module tìm kiếm đặc biệt cho công thức toán học:
  * Sử dụng vector hóa công thức toán học để tìm kiếm công thức tương tự
  * Phân tích cấu trúc công thức để so sánh tính tương đồng

---

## Giai đoạn 6: Sinh câu hỏi mới

### Bước 11: Xây dựng hệ thống sinh câu hỏi
* Tạo hệ thống sinh câu hỏi theo template (ví dụ: thay đổi tham số, miền giá trị)
* Kiểm tra chất lượng câu hỏi mới sinh ra (đảm bảo câu hỏi có thể giải được và đúng độ khó)
* Lưu trữ câu hỏi sinh ra vào cơ sở dữ liệu và vector DB

---

## Giai đoạn 7: Kiểm tra chất lượng và triển khai

### Bước 12: Kiểm tra và bảo trì hệ thống
* Viết Unit tests và Integration tests cho các module:
  * `ingestion`
  * `segmentation`
  * `embedding`
  * `generation`
  * `search`
* Kiểm tra chất lượng câu hỏi:
  * Kiểm tra trùng lặp câu hỏi
  * Kiểm tra tính hợp lệ công thức
  * Đánh giá độ khó câu hỏi

### Bước 13: Triển khai hệ thống
* Tạo Docker container cho ứng dụng và triển khai lên môi trường sản xuất
* Cấu hình Docker Compose để chạy các dịch vụ như database, queue service
* Tối ưu hóa hiệu suất:
  * Tối ưu API và embedding
  * Đảm bảo hệ thống có thể xử lý yêu cầu với số lượng tài liệu lớn

---

## Giai đoạn 8: Hỗ trợ và bảo trì

### Bước 14: Theo dõi và hỗ trợ
* Giám sát hệ thống bằng công cụ như Prometheus hoặc Grafana
* Cải tiến liên tục:
  * Thu thập phản hồi từ người dùng
  * Cập nhật và mở rộng hệ thống

---

## Giai đoạn mở rộng (sau triển khai)

### Bước 15: Mở rộng tính năng
* Phát triển hệ thống sinh câu hỏi nâng cao (sinh bài kiểm tra, câu hỏi ngẫu nhiên)
* Cải thiện hệ thống tìm kiếm thông minh (tìm kiếm theo các thuộc tính phức tạp hơn)
* Hỗ trợ người dùng cá nhân hóa: đề xuất bài học dựa trên lịch sử làm bài