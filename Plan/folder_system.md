DATN/
├── apps/
│   ├── api/                         # Backend FastAPI hiện tại
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   └── __init__.py
│   │
│   ├── worker/                      # Worker xử lý task nặng hiện tại
│   │   ├── tasks/
│   │   ├── utils/
│   │   └── __init__.py
│   │
│   └── frontend/                    # React frontend mới
│       ├── public/
│       │   ├── favicon.ico
│       │   └── assets/              # Ảnh tĩnh public nếu cần
│       │
│       ├── src/
│       │   ├── app/                 # Khởi tạo app, router, providers
│       │   │   ├── App.jsx
│       │   │   ├── router.jsx
│       │   │   └── providers.jsx
│       │   │
│       │   ├── pages/               # Các trang chính
│       │   │   ├── DashboardPage.jsx
│       │   │   ├── UploadPage.jsx
│       │   │   ├── SearchPage.jsx
│       │   │   ├── ProblemDetailPage.jsx
│       │   │   ├── GeneratePage.jsx
│       │   │   ├── ReviewPage.jsx
│       │   │   └── AnalyticsPage.jsx
│       │   │
│       │   ├── features/            # Tách theo nghiệp vụ, khớp backend modules
│       │   │   ├── ingestion/       # Upload PDF/Markdown, trạng thái xử lý
│       │   │   ├── problems/        # Hiển thị bài toán, lời giải, đáp án
│       │   │   ├── search/          # Tìm kiếm semantic/formula/metadata
│       │   │   ├── generation/      # Sinh câu hỏi mới
│       │   │   ├── taxonomy/        # Chủ đề, dạng toán, kỹ năng, độ khó
│       │   │   ├── validation/      # Kiểm tra chất lượng/trùng lặp
│       │   │   ├── review/          # Duyệt câu hỏi
│       │   │   └── analytics/       # Thống kê
│       │   │
│       │   ├── components/          # Component dùng chung
│       │   │   ├── layout/
│       │   │   ├── forms/
│       │   │   ├── tables/
│       │   │   ├── modals/
│       │   │   ├── math/
│       │   │   └── ui/
│       │   │
│       │   ├── services/            # Gọi API backend
│       │   │   ├── apiClient.js
│       │   │   ├── ingestionApi.js
│       │   │   ├── problemApi.js
│       │   │   ├── searchApi.js
│       │   │   ├── generationApi.js
│       │   │   ├── validationApi.js
│       │   │   └── analyticsApi.js
│       │   │
│       │   ├── hooks/               # Custom React hooks
│       │   │   ├── useUpload.js
│       │   │   ├── useSearch.js
│       │   │   └── useDebounce.js
│       │   │
│       │   ├── store/               # State management nếu cần
│       │   │   ├── authStore.js
│       │   │   ├── searchStore.js
│       │   │   └── uiStore.js
│       │   │
│       │   ├── types/               # Nếu dùng JS: JSDoc/types nội bộ; nếu TS: đổi sang .ts
│       │   │   ├── problem.js
│       │   │   ├── document.js
│       │   │   └── api.js
│       │   │
│       │   ├── utils/
│       │   │   ├── formatDate.js
│       │   │   ├── formatMath.js
│       │   │   └── fileUtils.js
│       │   │
│       │   ├── constants/
│       │   │   ├── routes.js
│       │   │   ├── apiEndpoints.js
│       │   │   └── difficultyLevels.js
│       │   │
│       │   ├── styles/
│       │   │   ├── globals.css
│       │   │   └── variables.css
│       │   │
│       │   └── main.jsx
│       │
│       ├── .env.example
│       ├── index.html
│       ├── package.json
│       ├── vite.config.js
│       └── README.md
│
├── core/                            # Core backend hiện tại
├── modules/                         # Logic nghiệp vụ backend hiện tại
├── infra/                           # DB, vector DB, queue, storage
├── data/                            # Dữ liệu local/dev nếu có
├── scripts/                         # Script hỗ trợ
├── tests/
│   ├── api/
│   ├── worker/
│   ├── modules/
│   └── frontend/                    # Test frontend nếu muốn tách ngoài app
│
├── docker-compose.yml
├── Dockerfile                       # Backend Dockerfile hiện tại
├── requirements.txt
├── README.md
├── Overall_design.md
├── Folder_structure.md
└── .env
