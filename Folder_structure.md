├── apps/                  # Mã nguồn của ứng dụng chính
│   ├── api/               # API Backend: FastAPI
│   │   ├── v1/            # API version 1
│   │   │   ├── endpoints/ # Các endpoint API
│   │   │   ├── models/    # Các schema, pydantic models
│   │   │   ├── services/  # Logic dịch vụ backend
│   │   │   └── utils/     # Các hàm tiện ích cho API
│   │   └── __init__.py    # Tập tin khởi tạo của API
│   ├── worker/            # Các worker xử lý nặng (task queue)
│   │   ├── tasks/         # Các task (job) xử lý bất đồng bộ
│   │   ├── utils/         # Các công cụ hỗ trợ worker
│   │   └── __init__.py    # Tập tin khởi tạo của worker
│   └── __init__.py        # Tập tin khởi tạo của ứng dụng
├── core/                  # Các cài đặt và logic cốt lõi của hệ thống
│   ├── config/            # Cấu hình ứng dụng (cấu hình database, môi trường, v.v.)
│   ├── logging/           # Cấu hình logging
│   ├── security/          # Xử lý bảo mật (xác thực, phân quyền)
│   └── utils/             # Các hàm tiện ích cốt lõi
├── modules/               # Các module tính năng của dự án
│   ├── ingestion/         # Nhận và chuẩn hóa tài liệu đầu vào (PDF/Markdown)
│   │   ├── pdf_processing/# Xử lý PDF, OCR, Marker integration
│   │   ├── markdown_processing/ # Xử lý và chuẩn hóa Markdown
│   │   └── __init__.py
│   ├── parser/            # Tách câu hỏi và nội dung từ tài liệu
│   │   ├── segmentation/  # Chia nhỏ câu hỏi, câu giải
│   │   ├── math_parser/   # Phân tích công thức toán học
│   │   └── __init__.py
│   ├── classifier/        # Phân loại bài toán, độ khó, kỹ năng
│   │   ├── taxonomy/      # Phân loại theo taxonomy (môn học, chương, v.v.)
│   │   ├── problem_type/  # Phân loại theo loại bài toán
│   │   ├── skill_tagging/ # Gán nhãn kỹ năng
│   │   └── __init__.py
│   ├── embeddings/        # Tạo và lưu embedding cho câu hỏi
│   │   ├── vectorization/ # Tạo vector cho câu hỏi, công thức
│   │   └── __init__.py
│   ├── search/            # Tìm kiếm thông minh
│   │   ├── semantic_search/# Tìm kiếm theo ngữ nghĩa
│   │   ├── formula_search/# Tìm kiếm theo công thức toán học
│   │   └── __init__.py
│   ├── generation/        # Tạo câu hỏi mới từ câu hỏi mẫu
│   │   ├── template_based_generation/ # Sinh câu hỏi theo template
│   │   └── __init__.py
│   ├── validation/        # Kiểm tra chất lượng câu hỏi
│   │   ├── duplication_check/ # Kiểm tra trùng lặp câu hỏi
│   │   └── __init__.py
│   ├── review/            # Quy trình duyệt câu hỏi
│   │   ├── review_tasks/  # Quản lý các task review
│   │   └── __init__.py
│   ├── analytics/         # Phân tích và thống kê
│   │   ├── user_behavior/ # Phân tích hành vi người dùng
│   │   ├── quality_analysis/ # Phân tích chất lượng câu hỏi
│   │   └── __init__.py
│   └── __init__.py
├── infra/                 # Cấu hình hạ tầng, database, message queue, storage
│   ├── db/                # Cấu hình database (PostgreSQL)
│   │   ├── migrations/    # Quản lý migrations
│   │   └── __init__.py
│   ├── vector_db/         # Cấu hình vector DB (Qdrant)
│   ├── queue/             # Cấu hình message queue (RabbitMQ, Redis)
│   ├── storage/           # Cấu hình lưu trữ (MinIO, S3)
│   └── __init__.py
├── tests/                 # Các bài kiểm tra tự động (unit test, integration test)
│   ├── api/               # Kiểm tra các API endpoints
│   ├── worker/            # Kiểm tra các worker task
│   ├── modules/           # Kiểm tra các modules tính năng
│   └── __init__.py
├── scripts/               # Các script hỗ trợ (data collection, training models, v.v.)
│   ├── data_preprocessing/# Tiền xử lý dữ liệu
│   ├── model_training/    # Huấn luyện mô hình AI (nếu có)
│   └── __init__.py
├── Dockerfile             # Dockerfile cho môi trường sản xuất
├── docker-compose.yml     # Docker Compose để cấu hình các dịch vụ
├── requirements.txt       # Danh sách các thư viện yêu cầu cho dự án
├── README.md              # Tài liệu mô tả dự án
└── __init__.py            # Tập tin khởi tạo của dự án