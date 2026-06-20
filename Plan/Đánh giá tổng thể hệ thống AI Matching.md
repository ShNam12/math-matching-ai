# Đánh giá tổng thể hệ thống AI Matching

## 1. Mục đích đánh giá

Tài liệu này tổng hợp kết quả đánh giá hiện tại của hệ thống AI Matching câu hỏi vào cây tri thức Giải tích 1. Nội dung được dùng làm cơ sở cho phần đánh giá hiệu quả hệ thống trong báo cáo đồ án.

Hệ thống được đánh giá theo các nhóm chính:

- Khả năng phân loại câu hỏi vào cây tri thức.
- Khả năng sinh mã taxonomy hợp lệ.
- Khả năng đánh giá độ khó.
- Khả năng tìm kiếm và xếp hạng kết quả bằng Hybrid Matching.
- Độ ổn định của backend và frontend sau khi tích hợp.

## 2. Phạm vi hệ thống được đánh giá

Hệ thống hiện tại đã có các thành phần chính của một pipeline AI Matching:

- Bộ não tri thức Giải tích 1: `core/taxonomy/calculus_1_taxonomy.json`
- Module phân loại câu hỏi: `modules/question_classification`
- Module kiểm tra taxonomy hợp lệ.
- Module lưu kết quả phân loại vào database.
- API phân loại lại câu hỏi và tài liệu.
- API cây tri thức và thống kê taxonomy.
- Semantic Search kết hợp Hybrid Matching.
- Frontend hiển thị kết quả phân loại, cây tri thức, tìm kiếm và chi tiết câu hỏi.

Vì vậy, ở thời điểm hiện tại có thể xem hệ thống là một hệ thống AI Matching ở mức MVP hoàn chỉnh về chức năng lõi.

## 3. Dataset đánh giá

Dataset đánh giá được lưu tại:

```text
tests/fixtures/calculus_1_classification_eval.json
```

Thông tin dataset:

| Thành phần | Giá trị |
|---|---:|
| Tổng số mẫu | 30 |
| Số mẫu Chương 1 | 10 |
| Số mẫu Chương 2 | 11 |
| Số mẫu Chương 3 | 9 |
| Số mẫu easy | 10 |
| Số mẫu medium | 15 |
| Số mẫu hard | 5 |

Mỗi mẫu gồm:

- Nội dung câu hỏi.
- Công thức LaTeX nếu có.
- Mã chương kỳ vọng.
- Mã chủ đề kỳ vọng.
- Mã dạng bài kỳ vọng.
- Độ khó kỳ vọng.

Trước khi chạy evaluation, dataset đã được kiểm tra:

- JSON hợp lệ.
- Không có mã taxonomy kỳ vọng nào bị sai hoặc không tồn tại.
- Unit test evaluator chạy thành công.

## 4. Kết quả AI Matching vào cây tri thức

Script đánh giá:

```text
scripts/evaluate_taxonomy_matching.py
```

Model sử dụng:

```text
gemini-2.5-pro
```

Kết quả trên 30 mẫu:

| Chỉ số | Kết quả |
|---|---:|
| Total | 30 |
| Chapter accuracy | 100.00% |
| Topic accuracy | 100.00% |
| Problem type accuracy | 96.67% |
| Difficulty accuracy | 70.00% |
| Low confidence rate | 0.00% |
| Invalid code rate | 0.00% |
| Failed count | 0 |

## 5. Nhận xét kết quả phân loại

### 5.1. Điểm mạnh

Hệ thống đạt độ chính xác rất cao ở ba cấp quan trọng nhất của bài toán AI Matching:

- Đúng chương: 30/30 mẫu.
- Đúng chủ đề: 30/30 mẫu.
- Đúng dạng bài: 29/30 mẫu.

Đây là kết quả tốt vì ba cấp này là phần cốt lõi của yêu cầu matching câu hỏi vào cây tri thức.

Đặc biệt:

```text
Invalid code rate = 0.00%
Failed count = 0
```

Điều này cho thấy model không sinh mã taxonomy không tồn tại và pipeline xử lý ổn định, không bị lỗi parse, lỗi validate hoặc lỗi runtime trong quá trình đánh giá.

### 5.2. Trường hợp lệch dạng bài

Trường hợp sai duy nhất là `eval_018`.

Kết quả:

```text
Expected problem type: GT1_C2_03_T04_Convergence_Divergence
Predicted problem type: GT1_C2_03_T08_Parameter_Improper_Integral
```

Câu hỏi:

```text
Xét sự hội tụ của tích phân suy rộng int_1^infty 1/x^p dx với tham số p.
```

Nhận xét: dự đoán của model hợp lý hơn nhãn ban đầu vì câu hỏi có tham số `p`. Do đó trường hợp này có khả năng là lỗi gán nhãn trong dataset, không phải lỗi thực sự của mô hình.

Nếu cập nhật nhãn kỳ vọng của `eval_018` sang:

```text
GT1_C2_03_T08_Parameter_Improper_Integral
```

thì chỉ số problem type accuracy có khả năng đạt 100%.

### 5.3. Nhận xét về độ khó

Difficulty accuracy đạt:

```text
70.00%
```

Chỉ số này thấp hơn các chỉ số taxonomy. Nguyên nhân chính là độ khó là tiêu chí mềm, phụ thuộc vào rubric đánh giá.

Một số ví dụ:

- Câu hỏi có ghi rõ phương pháp đổi biến có thể được model xem là `easy` vì áp dụng trực tiếp.
- Câu hỏi dùng Taylor có thể được model xem là `hard` vì cần khai triển và xử lý dạng vô định.
- Câu hỏi tìm tham số để liên tục có thể được model xem là `medium` thay vì `hard` nếu chỉ cần so giới hạn trái, phải.

Vì vậy, phần đánh giá độ khó cần được chuẩn hóa thêm bằng rubric rõ hơn, ví dụ:

- `easy`: áp dụng trực tiếp công thức hoặc quy tắc cơ bản.
- `medium`: cần chọn phương pháp và biến đổi vài bước.
- `hard`: có tham số, biện luận, chứng minh, chia trường hợp hoặc kết hợp nhiều kiến thức.

## 6. Kết quả Hybrid Matching

Hệ thống đã bổ sung cơ chế Hybrid Matching trong semantic search.

Module chính:

```text
modules/semantic_search/hybrid_matching.py
```

Các thành phần điểm:

- `semantic_score`: điểm tương đồng vector.
- `taxonomy_score`: điểm khớp chương, chủ đề, dạng bài.
- `formula_score`: điểm công thức, hiện đã thiết kế sẵn để mở rộng.
- `difficulty_score`: điểm khớp độ khó.
- `skill_score`: điểm khớp kỹ năng.
- `score`: điểm tổng hợp cuối cùng.

Công thức khi có hybrid context:

```text
final_score =
    0.50 * semantic_score
  + 0.20 * taxonomy_score
  + 0.15 * formula_score
  + 0.10 * difficulty_score
  + 0.05 * skill_score
```

Khi người dùng tìm kiếm tự do và không chọn taxonomy, difficulty hoặc skill:

```text
final_score = semantic_score
```

Quy tắc này giúp điểm hiển thị trên frontend không bị giảm bất thường trong trường hợp tìm kiếm ngữ nghĩa thông thường.

## 7. Kiểm thử tự động

Backend full test:

```text
247 passed in 7.60s
```

Frontend lint:

```text
npm run lint
```

Kết quả: pass, không còn lỗi lint.

Frontend build:

```text
npm run build
```

Kết quả: build thành công.

Vite có cảnh báo chunk lớn hơn 500 kB, nhưng đây là cảnh báo tối ưu hiệu năng, không phải lỗi chức năng.

## 8. Đánh giá mức độ hoàn thiện

So với mục tiêu xây dựng hệ thống AI Matching câu hỏi vào cây tri thức Giải tích 1, hệ thống hiện tại đã đạt các yêu cầu lõi:

| Tiêu chí | Trạng thái |
|---|---|
| Có cây tri thức Giải tích 1 chính thức | Đạt |
| Có mã taxonomy tiếng Anh và hiển thị tiếng Việt | Đạt |
| Có phân loại chương | Đạt |
| Có phân loại chủ đề | Đạt |
| Có phân loại dạng bài | Đạt |
| Có gán độ khó và kỹ năng | Đạt |
| Có lưu metadata phân loại vào database | Đạt |
| Có API phân loại lại câu hỏi | Đạt |
| Có API phân loại tài liệu | Đạt |
| Có kiểm tra chất lượng taxonomy | Đạt |
| Có tìm kiếm ngữ nghĩa | Đạt |
| Có Hybrid Matching | Đạt |
| Có frontend hiển thị kết quả matching | Đạt |
| Có evaluation dataset và script đánh giá | Đạt |
| Có test backend và frontend build | Đạt |

Kết luận: hệ thống đã đủ cơ sở để gọi là một hệ thống AI Matching ở mức MVP hoàn chỉnh.

## 9. Hạn chế hiện tại

Mặc dù kết quả hiện tại tốt, hệ thống vẫn còn một số hạn chế:

- Dataset đánh giá mới có 30 mẫu, chưa đủ lớn để kết luận độ chính xác tổng quát trên toàn bộ ngân hàng câu hỏi.
- Một số nhãn độ khó trong dataset còn có thể tranh luận.
- `formula_score` trong Hybrid Matching hiện mới là phần thiết kế mở rộng, chưa phải matching công thức chuyên sâu.
- Chưa có đánh giá riêng theo từng chủ đề hoặc từng dạng bài.
- Chưa có confusion matrix để xem các dạng bài nào dễ bị nhầm với nhau.
- Frontend đã hiển thị score breakdown nhưng chưa có dashboard đánh giá hiệu quả matching.

## 10. Hướng cải thiện tiếp theo

Các bước nên làm tiếp:

1. Rà soát lại nhãn `eval_018` và các nhãn độ khó bị lệch.
2. Mở rộng evaluation dataset lên 50 mẫu.
3. Bổ sung nhiều câu hỏi gây nhiễu giữa các dạng bài gần nhau.
4. Tính thêm chỉ số theo từng chương và từng cấp taxonomy.
5. Bổ sung confusion matrix cho problem type.
6. Hoàn thiện `formula_score` nếu muốn nhấn mạnh matching theo công thức toán học.
7. Viết báo cáo thực nghiệm dựa trên các chỉ số đã đo được.

## 11. Kết luận tổng thể

Hệ thống hiện tại đã đạt mục tiêu chính của bài toán: đưa câu hỏi Giải tích 1 vào cây tri thức theo các cấp chương, chủ đề và dạng bài bằng AI.

Kết quả evaluation 30 mẫu cho thấy:

```text
Chapter accuracy: 100.00%
Topic accuracy: 100.00%
Problem type accuracy: 96.67%
Invalid code rate: 0.00%
Failed count: 0
```

Các chỉ số này cho thấy pipeline AI Matching đã hoạt động ổn định và có độ chính xác cao ở phần taxonomy. Phần độ khó cần tiếp tục chuẩn hóa, nhưng không làm giảm bản chất của hệ thống là một hệ thống AI Matching.

Vì vậy, hệ thống có thể được trình bày trong báo cáo như một hệ thống AI Matching câu hỏi vào cây tri thức Giải tích 1, có đầy đủ các thành phần: bộ não tri thức, mô hình phân loại, kiểm tra mã taxonomy, lưu metadata, tìm kiếm hybrid và đánh giá thực nghiệm.
