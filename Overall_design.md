# 1. Tổng quan dự án

**Mục tiêu:**
* Tạo một hệ thống web AI có khả năng nhận diện, phân loại, tìm kiếm, và sinh câu hỏi từ tài liệu (PDF/Markdown) trong lĩnh vực Giải tích.
* Cung cấp khả năng tìm kiếm bài toán theo các tiêu chí như chủ đề, dạng toán, độ khó, giải pháp.
* Hệ thống có thể tự động sinh câu hỏi mới từ câu hỏi mẫu, đồng thời giúp cải thiện chất lượng dữ liệu học của học sinh.

---

# 2. Các Task công việc cần triển khai

## 2.1 Task 1: Xử lý tài liệu đầu vào (Ingestion)
**Mục tiêu:** Tiếp nhận tài liệu PDF/Markdown từ người dùng, chuẩn hóa chúng về dạng Markdown để tiếp tục xử lý.

**Các bước thực hiện:**
* **Xử lý file PDF:**
  * Nhận diện tài liệu PDF từ người dùng.
  * Sử dụng Marker để chuyển đổi PDF sang Markdown.
  * Chạy OCR (nếu cần) để xử lý các công thức toán học hoặc hình ảnh trong tài liệu PDF.
  * Lưu trữ file gốc và file Markdown vào hệ thống lưu trữ.
* **Xử lý file Markdown:**
  * Kiểm tra file nhập vào có đúng chuẩn Markdown không.
  * Tiến hành chuẩn hóa Markdown, đảm bảo cấu trúc, công thức, và các phần tử toán học được xử lý đúng.
  * Chạy các kiểm tra chuẩn hóa: loại bỏ các ký tự sai, thêm các thành phần cần thiết như heading, bullet points, và math blocks.
* **Lưu trữ dữ liệu:**
  * Lưu trữ tài liệu gốc vào hệ thống lưu trữ (MinIO hoặc S3).
  * Lưu trữ dữ liệu đã xử lý vào database.

**Task 1.1 Output:**
* Tài liệu PDF/Markdown được chuẩn hóa và lưu trữ.
* File Markdown có thể xử lý cho các bước tiếp theo.

## 2.2 Task 2: Phân tách và chuẩn hóa bài toán (Segmentation)
**Mục tiêu:** Tách các câu hỏi và phần nội dung trong tài liệu ra các mục riêng biệt như đề bài, lời giải, đáp án, công thức.

**Các bước thực hiện:**
* **Phân tách câu hỏi:**
  * Dùng regex và phân tích cấu trúc tài liệu để nhận diện các câu hỏi (ví dụ: “Bài 1”, “Câu hỏi 2”, “Ví dụ 1”).
  * Dùng AI để nhận diện các trường hợp đặc biệt nếu regex không đủ chính xác.
* **Tách lời giải và đáp án:**
  * Tách phần giải và đáp án từ câu hỏi.
  * Phân tích dạng bài toán: nếu bài toán có đáp án trắc nghiệm hay chỉ có lời giải, hệ thống cần xác định và phân loại.
  * Lưu trữ các câu hỏi đã phân tách vào database.
  * Gắn metadata cho mỗi câu hỏi như chương, môn học, độ khó.

**Task 2.1 Output:**
* Danh sách các câu hỏi được phân tách thành các trường: đề bài, giải pháp, đáp án, công thức.

## 2.3 Task 3: Phân loại và nhận diện bài toán (Classification & Taxonomy)
**Mục tiêu:** Phân loại các câu hỏi theo dạng toán (ví dụ: phương trình bậc hai, đạo hàm, tích phân, v.v.), độ khó và gán các nhãn kỹ năng cần thiết.

**Các bước thực hiện:**
* **Phân loại bài toán:**
  * Xây dựng taxonomy môn học để phân loại câu hỏi vào các chương, chuyên đề, và dạng bài toán.
  * Phân loại dạng bài toán (ví dụ: phương trình bậc hai, đạo hàm, tích phân) bằng cách nhận diện các từ khóa trong câu hỏi.
* **Gán độ khó:**
  * Sử dụng một mô hình đánh giá độ khó dựa trên số lượng bước giải, yêu cầu kiến thức, và độ phức tạp của bài toán.
  * Đánh giá độ khó qua việc kiểm tra dữ liệu lịch sử của người học và thành tích học tập.
* **Gán kỹ năng:**
  * Nhận diện kỹ năng yêu cầu như giải phương trình, tính đạo hàm, phân tích điều kiện tham số, v.v.
  * Gắn nhãn kỹ năng cần thiết cho từng câu hỏi.

**Task 3.1 Output:**
* Các câu hỏi được phân loại vào taxonomy môn học, gắn độ khó và kỹ năng yêu cầu.

## 2.4 Task 4: Tạo embedding cho bài toán và kho dữ liệu (Embedding & Knowledge Base)
**Mục tiêu:** Chuyển các câu hỏi và lời giải thành các vector để phục vụ cho việc tìm kiếm và matching.

**Các bước thực hiện:**
* **Tạo embedding cho câu hỏi:**
  * Sử dụng mô hình embedding (ví dụ: Sentence-BERT, OpenAI Embedding API) để tạo vector cho câu hỏi, lời giải, công thức.
* **Tạo embedding cho công thức toán học:**
  * Sử dụng một công cụ parsing công thức toán học để chuyển đổi công thức thành vector toán học (có thể dùng SymPy hoặc công cụ tương tự).
* **Lưu embedding vào vector DB:**
  * Lưu các vector vào Qdrant hoặc một hệ thống vector database để phục vụ việc tìm kiếm thông minh.

**Task 4.1 Output:**
* Các câu hỏi, giải pháp, và công thức toán học đều có embedding và được lưu trữ trong hệ thống tìm kiếm.

## 2.5 Task 5: Phát triển hệ thống tìm kiếm thông minh (Search & Matching)
**Mục tiêu:** Xây dựng hệ thống tìm kiếm để truy vấn câu hỏi dựa trên ngữ nghĩa, công thức và metadata.

**Các bước thực hiện:**
* **Tìm kiếm theo ngữ nghĩa:**
  * Xây dựng các API tìm kiếm để người dùng có thể tìm kiếm câu hỏi theo từ khóa, chủ đề, độ khó, v.v.
  * Sử dụng embedding từ các câu hỏi để thực hiện tìm kiếm ngữ nghĩa.
* **Tìm kiếm câu hỏi tương tự:**
  * Sử dụng vector DB để tìm kiếm câu hỏi tương tự theo văn bản và công thức.
  * Tìm kiếm bài toán có độ khó tương tự.
* **Lọc kết quả tìm kiếm:**
  * Lọc kết quả theo metadata như chương, chủ đề, độ khó.

**Task 5.1 Output:**
* API tìm kiếm bài toán thông minh, có khả năng tìm kiếm theo ngữ nghĩa và lọc kết quả.

## 2.6 Task 6: Sinh câu hỏi mới từ câu hỏi mẫu (Question Generation)
**Mục tiêu:** Phát triển một hệ thống tự động sinh câu hỏi mới từ câu hỏi mẫu.

**Các bước thực hiện:**
* **Sinh biến thể câu hỏi:**
  * Sử dụng template-based generation để sinh các bài toán có dạng toán giống nhau nhưng thay đổi tham số.
  * Thay đổi tham số, hàm số, hoặc điều kiện để tạo ra câu hỏi mới.
* **Kiểm tra chất lượng câu hỏi sinh:**
  * Kiểm tra tính hợp lệ của câu hỏi mới: đảm bảo bài toán có thể giải được và có đáp án chính xác.
  * Kiểm tra độ khó của câu hỏi mới và đảm bảo chúng nằm trong phạm vi mong muốn.
* **Lưu trữ câu hỏi đã sinh:**
  * Lưu trữ câu hỏi mới vào hệ thống và gắn nhãn metadata.

**Task 6.1 Output:**
* Các câu hỏi mới được sinh ra, có thể phục vụ cho việc luyện tập và làm bài.

## 2.7 Task 7: Chấm điểm và đánh giá chất lượng câu hỏi (Quality Assurance)
**Mục tiêu:** Đảm bảo chất lượng câu hỏi và đảm bảo rằng các bài toán sinh ra không bị lỗi.

**Các bước thực hiện:**
* **Kiểm tra trùng lặp câu hỏi:**
  * Sử dụng hệ thống tìm kiếm để phát hiện câu hỏi trùng lặp.
  * Sử dụng hệ thống duplicate detection để loại bỏ các câu hỏi không cần thiết.
* **Kiểm tra công thức toán học:**
  * Kiểm tra công thức toán học để đảm bảo tính chính xác của nó.
* **Kiểm tra độ khó và yêu cầu:**
  * Đánh giá lại độ khó của câu hỏi và đảm bảo nó phù hợp với mức độ học sinh đang học.

**Task 7.1 Output:**
* Các câu hỏi được đánh giá và kiểm tra chất lượng trước khi đưa vào kho dữ liệu.

## 2.8 Task 8: Phát triển giao diện web và API (Web & API)
**Mục tiêu:** Tạo giao diện người dùng để upload tài liệu, tìm kiếm bài toán, và tương tác với hệ thống.

**Các bước thực hiện:**
* **Giao diện người dùng:**
  * Xây dựng UI với Next.js hoặc React để cho phép người dùng upload file PDF/Markdown, tìm kiếm bài toán và sinh câu hỏi mới.
  * Tạo các biểu mẫu tìm kiếm để lọc bài toán theo độ khó, chủ đề, dạng bài.
* **API Backend (FastAPI):**
  * Tạo các API cho việc upload tài liệu, phân tách câu hỏi, tìm kiếm câu hỏi, sinh câu hỏi mới, và gán metadata.
* **Kiểm tra và triển khai API:**
  * Kiểm tra API bằng Postman hoặc Swagger UI.

**Task 8.1 Output:**
* Giao diện người dùng cho phép tải lên tài liệu, tìm kiếm bài toán, và sinh câu hỏi mới.
* Các API hỗ trợ xử lý và truy vấn dữ liệu.

---

# 3. Lộ trình triển khai dự án

## Phase 1: MVP
* **Task 1-3:** Tiếp nhận và chuẩn hóa tài liệu đầu vào.
* **Task 4-5:** Tạo embedding và xây dựng hệ thống tìm kiếm.
* **Task 6:** Sinh câu hỏi mẫu.
* **Task 8:** Giao diện upload và tìm kiếm cơ bản.

## Phase 2: Tăng cường tính năng
* **Task 7:** Kiểm tra chất lượng câu hỏi.
* **Task 6:** Cải tiến hệ thống sinh câu hỏi.
* **Task 5:** Tinh chỉnh thuật toán tìm kiếm.

## Phase 3: Hoàn thiện và tối ưu
* **Task 8:** Tối ưu giao diện người dùng.
* **Task 7:** Thêm tính năng phát hiện lỗi trong bài toán và đáp án.
* **Task 6:** Tối ưu hệ thống sinh câu hỏi mới.