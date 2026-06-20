# Đánh giá hệ thống thông qua bước 13 - Hybrid Matching

## 1. Mục tiêu của bước 13

Bước 13 được thực hiện nhằm nâng cấp chức năng tìm kiếm ngữ nghĩa thành cơ chế Hybrid Matching. Thay vì chỉ xếp hạng câu hỏi theo độ tương đồng vector, hệ thống bổ sung thêm các tín hiệu từ cây tri thức Giải tích 1 và metadata của câu hỏi.

Các tín hiệu được sử dụng gồm:

- `semantic_score`: điểm tương đồng ngữ nghĩa từ vector search.
- `taxonomy_score`: điểm khớp theo chương, chủ đề và dạng bài trong cây tri thức.
- `formula_score`: điểm khớp theo công thức, được thiết kế sẵn để mở rộng.
- `difficulty_score`: điểm khớp theo độ khó.
- `skill_score`: điểm khớp theo kỹ năng yêu cầu.
- `final_score`: điểm tổng hợp dùng để xếp hạng kết quả cuối cùng.

Mục tiêu quan trọng của bước này là tách rõ hai luồng nghiệp vụ:

- Semantic Search: tìm câu hỏi gần nghĩa và xếp hạng lại bằng Hybrid Matching.
- Taxonomy Browse: xem chính xác các câu hỏi thuộc một mục trong cây tri thức.

Thiết kế này giúp hệ thống không biến semantic search thành bộ lọc cứng theo taxonomy, đồng thời vẫn tận dụng cây tri thức để ưu tiên các câu hỏi phù hợp hơn.

## 2. Thành phần đã triển khai

### 2.1. Module Hybrid Matching

Đã bổ sung module:

```text
modules/semantic_search/hybrid_matching.py
```

Module này định nghĩa các thành phần chính:

- `HybridMatchingContext`: biểu diễn ngữ cảnh tìm kiếm do người dùng chọn, ví dụ topic, problem type, difficulty hoặc skill.
- `HybridMatchingCandidate`: biểu diễn metadata của câu hỏi ứng viên được trả về từ vector search.
- `HybridScoreBreakdown`: biểu diễn các điểm thành phần và điểm tổng hợp.
- `calculate_hybrid_score()`: hàm tính điểm Hybrid Matching.
- `calculate_taxonomy_score()`: tính điểm khớp cây tri thức.
- `calculate_difficulty_score()`: tính điểm khớp độ khó.
- `calculate_skill_score()`: tính điểm khớp kỹ năng.
- `has_hybrid_context()`: kiểm tra search có sử dụng ngữ cảnh hybrid hay không.

### 2.2. Cơ chế tính điểm

Công thức tổng hợp điểm khi có hybrid context:

```text
final_score =
    0.50 * semantic_score
  + 0.20 * taxonomy_score
  + 0.15 * formula_score
  + 0.10 * difficulty_score
  + 0.05 * skill_score
```

Trong đó:

- Nếu khớp đúng `problem_type_code`, `taxonomy_score = 1.0`.
- Nếu khớp đúng `topic_code`, `taxonomy_score = 0.7`.
- Nếu chỉ khớp đúng `chapter_code`, `taxonomy_score = 0.4`.
- Nếu không khớp taxonomy, `taxonomy_score = 0.0`.

Riêng với search tự do, khi người dùng không chọn taxonomy, difficulty hoặc skill, hệ thống áp dụng quy tắc:

```text
final_score = semantic_score
```

Quy tắc này giúp giao diện không hiển thị điểm match bị tụt bất thường. Ví dụ, nếu semantic score là 0.69 thì frontend vẫn hiển thị 69%, thay vì bị giảm còn khoảng 34% do thiếu các tín hiệu hybrid.

### 2.3. Tích hợp vào Semantic Search

Đã cập nhật:

```text
modules/semantic_search/service.py
```

Các thay đổi chính:

- Vector search vẫn tìm ứng viên theo ngữ nghĩa.
- Taxonomy, difficulty và skill không còn bị dùng như bộ lọc cứng trong semantic search.
- Các metadata này được dùng làm context để tính `taxonomy_score`, `difficulty_score` và `skill_score`.
- Kết quả được sắp xếp theo `final_score`.

Điều này giúp một câu hỏi có semantic score thấp hơn một chút nhưng khớp taxonomy tốt hơn vẫn có thể được đẩy lên cao hơn.

### 2.4. Cập nhật API Search

API search đã trả thêm các điểm thành phần:

```text
score
semantic_score
taxonomy_score
formula_score
difficulty_score
skill_score
```

Trong đó `score` là `final_score`, được frontend sử dụng làm điểm match chính.

### 2.5. Cập nhật Frontend

Trang Semantic Search đã hiển thị ngắn gọn breakdown score trên từng card kết quả:

```text
Sem xx% · Tax yy% · Skill zz%
```

Mục đích là giúp người dùng thấy rõ điểm kết quả không chỉ đến từ semantic search, mà còn có thể đến từ taxonomy và kỹ năng.

## 3. Kết quả test tự động

Sau khi hoàn thành bước 13, các nhóm test chính đã được chạy lại.

### 3.1. Test Hybrid Matching

Lệnh chạy:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\modules\semantic_search\test_hybrid_matching.py -q
```

Kết quả:

```text
9 passed
```

Các test xác nhận:

- Khớp đúng problem type cho `taxonomy_score = 1.0`.
- Khớp đúng topic cho `taxonomy_score = 0.7`.
- Khớp đúng chapter cho `taxonomy_score = 0.4`.
- Không khớp taxonomy cho `taxonomy_score = 0.0`.
- Độ khó khớp làm tăng điểm cuối.
- Skill khớp làm tăng điểm cuối.
- Điểm cuối được chặn trong khoảng `[0, 1]`.
- Thiếu metadata taxonomy không làm hệ thống lỗi.
- Không có hybrid context thì `final_score = semantic_score`.

### 3.2. Test Semantic Search Service

Lệnh chạy:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\modules\semantic_search\test_service.py -q
```

Kết quả:

```text
6 passed
```

Các test xác nhận:

- Search trả kết quả có metadata đầy đủ.
- Search reject query rỗng.
- Search reject limit không hợp lệ.
- Bỏ qua câu hỏi chưa embedding thành công.
- Taxonomy metadata được dùng làm hybrid context.
- Kết quả được rerank theo hybrid score.

### 3.3. Full Backend Test

Lệnh chạy:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Kết quả:

```text
247 passed
```

Kết quả này cho thấy việc bổ sung Hybrid Matching không làm hỏng các module cũ như:

- Question classification.
- Taxonomy validation.
- Repository.
- API search.
- Question quality.
- Question storage.
- Evaluation dataset.

### 3.4. Frontend Build

Lệnh chạy:

```powershell
cd apps\frontend
npm run build
```

Kết quả:

```text
Build thành công
```

Build có cảnh báo bundle lớn hơn 500 kB, nhưng đây là cảnh báo tối ưu hiệu năng, không phải lỗi chức năng.

## 4. Kết quả test tay

### 4.1. Kiểm tra API taxonomy

Endpoint:

```text
GET /taxonomy
```

Kết quả:

- Backend trả cây tri thức Giải tích 1 đầy đủ.
- Có `taxonomy_id`, `version`, `chapters`, `topics`, `problem_types`.
- Xác nhận cây tri thức vẫn hoạt động sau khi thêm Hybrid Matching.

### 4.2. Kiểm tra search tự do không có hybrid context

Endpoint:

```text
POST /search/questions
```

Request mẫu:

```json
{
  "query": "dao ham co ban",
  "limit": 5
}
```

Kết quả quan sát:

```text
score = semantic_score = 0.69139314
taxonomy_score = 0
formula_score = 0
difficulty_score = 0
skill_score = 0
```

Điều này xác nhận rule:

```text
Không có hybrid context thì final_score = semantic_score
```

hoạt động đúng.

### 4.3. Kiểm tra Semantic Search trên frontend

Query:

```text
dao ham co ban
```

Kết quả:

- Frontend hiển thị 5 kết quả.
- Score chính hiển thị khoảng 69%, 68%, 61%, 60%, 58%.
- Kết quả đã phân loại hiển thị được chương, chủ đề, dạng bài và độ tin cậy AI.
- Breakdown score hiển thị ngắn gọn: `Sem`, `Tax`, `Skill`.
- Không xảy ra lỗi trắng màn hình.

### 4.4. Kiểm tra Taxonomy Browse

Thao tác:

- Vào Calculus Taxonomy.
- Chọn dạng bài `Tính đạo hàm cơ bản`.
- Bấm `Xem bài tập trong mục này`.

Kết quả:

- Trang Semantic Search mở danh sách bài theo taxonomy.
- Hiển thị badge `Taxonomy: Tính đạo hàm cơ bản`.
- Hiển thị badge `Danh sách bài theo taxonomy`.
- Trả về 2 câu hỏi thuộc đúng dạng bài `Tính đạo hàm cơ bản`.
- Không cần nhập query.

Kết quả này xác nhận luồng Taxonomy Browse vẫn lọc chính xác theo cây tri thức, tách biệt với semantic search.

### 4.5. Kiểm tra Problem Detail

Khi mở một câu hỏi từ kết quả search, trang chi tiết hiển thị đầy đủ metadata AI Matching:

- Chương.
- Chủ đề.
- Dạng bài.
- Độ tin cậy.
- Trạng thái.
- Lý do phân loại.
- Nút `AI Matching lại`.
- Nút `Kiểm định taxonomy`.

### 4.6. Kiểm tra AI Matching lại

Thao tác:

- Bấm `AI Matching lại` trong Problem Detail.

Kết quả:

- Hệ thống xử lý thành công.
- Có thông báo `Đã AI Matching lại câu hỏi`.
- Trạng thái vẫn là `completed`.
- Chương, chủ đề, dạng bài và lý do phân loại được cập nhật đầy đủ.

## 5. Đánh giá kết quả bước 13

### 5.1. Điểm mạnh

Hybrid Matching đã giúp hệ thống tiến gần hơn tới một hệ thống AI Matching đúng nghĩa. Trước bước này, semantic search chủ yếu dựa vào vector similarity. Sau bước này, kết quả tìm kiếm được xếp hạng bằng nhiều tín hiệu hơn, gồm ngữ nghĩa, cây tri thức, độ khó và kỹ năng.

Thiết kế hiện tại cũng tách rõ hai nghiệp vụ:

- Tìm kiếm thông minh: dùng semantic search và hybrid rerank.
- Xem bài theo cây tri thức: dùng taxonomy browse và lọc chính xác.

Điều này giúp hệ thống vừa mềm dẻo khi tìm kiếm, vừa chính xác khi khai thác cây tri thức.

### 5.2. Điểm còn hạn chế

Hiện tại `formula_score` đã có trong cấu trúc điểm nhưng chưa được tích hợp sâu vào pipeline search câu hỏi. Đây là phần có thể mở rộng trong các bước tiếp theo để kết hợp tìm kiếm công thức với tìm kiếm ngữ nghĩa.

Ngoài ra, corpus kiểm thử tay hiện còn ít dữ liệu. Do đó, khi search các query như `tich phan tung phan`, hệ thống có thể vẫn trả về câu đạo hàm nếu trong cơ sở dữ liệu chưa có nhiều câu tích phân phù hợp. Đây không phải lỗi của Hybrid Matching mà là giới hạn của dữ liệu hiện tại.

### 5.3. Ý nghĩa đối với báo cáo

Bước 13 là một mốc quan trọng để chứng minh hệ thống không chỉ là semantic search đơn thuần. Hệ thống đã có cơ chế phối hợp nhiều nguồn tín hiệu để xếp hạng câu hỏi, phù hợp với định hướng AI Matching câu hỏi vào cây tri thức Giải tích 1.

Trong báo cáo, có thể trình bày bước này như phần nâng cấp từ:

```text
Vector Search
```

sang:

```text
Hybrid AI Matching
```

với điểm tổng hợp dựa trên:

```text
semantic similarity + taxonomy alignment + formula signal + difficulty + skill
```

## 6. Kết luận

Bước 13 đã hoàn thành.

Các tiêu chí hoàn thành đều đạt:

- Có module Hybrid Matching riêng.
- Có test riêng cho hybrid score.
- Semantic search trả đủ score breakdown.
- Search rerank theo `final_score`.
- Search tự do không bị tụt điểm bất thường.
- Taxonomy Browse vẫn hoạt động đúng.
- Problem Detail hiển thị metadata AI Matching đầy đủ.
- AI Matching lại hoạt động.
- Backend full test pass.
- Frontend build pass.

Kết quả này cho thấy pipeline AI Matching đã có nền tảng tốt để tiếp tục mở rộng sang đánh giá chất lượng, thống kê hiệu quả và cải thiện giao diện giải thích điểm matching.
