# Đánh giá hệ thống thông qua bước 12

## 1. Mục đích đánh giá

Tài liệu này ghi lại kết quả đánh giá bước đầu của pipeline AI Matching câu hỏi vào cây tri thức Giải tích 1. Mục tiêu là kiểm chứng hệ thống có thể phân loại câu hỏi vào đúng các cấp:

- Chương
- Chủ đề
- Dạng bài
- Độ khó

Kết quả trong tài liệu này có thể dùng làm cơ sở cho phần đánh giá hiệu quả hệ thống trong báo cáo đồ án.

## 2. Cấu hình đánh giá

- Dataset: `tests/fixtures/calculus_1_classification_eval.json`
- Số lượng mẫu: 10 câu hỏi
- Môn học: Giải tích 1
- Cây tri thức: `core/taxonomy/calculus_1_taxonomy.json`
- Mô hình phân loại: `gemini-2.5-pro`
- Script đánh giá: `scripts/evaluate_taxonomy_matching.py`

Mỗi mẫu trong dataset gồm:

- Nội dung câu hỏi
- Công thức nếu có
- Mã chương kỳ vọng
- Mã chủ đề kỳ vọng
- Mã dạng bài kỳ vọng
- Độ khó kỳ vọng

## 3. Chỉ số đánh giá

| Chỉ số | Kết quả |
|---|---:|
| Tổng số mẫu đánh giá | 10 |
| Chapter accuracy | 100.00% |
| Topic accuracy | 100.00% |
| Problem type accuracy | 100.00% |
| Difficulty accuracy | 80.00% |
| Low confidence rate | 0.00% |
| Invalid code rate | 0.00% |
| Failed count | 0 |

## 4. Phân tích kết quả

Kết quả cho thấy hệ thống AI Matching đã phân loại chính xác toàn bộ 10 câu hỏi ở ba cấp chính của cây tri thức:

- Đúng chương: 10/10 câu
- Đúng chủ đề: 10/10 câu
- Đúng dạng bài: 10/10 câu

Đây là kết quả tích cực vì ba cấp này là phần cốt lõi của bài toán matching câu hỏi vào cây tri thức. Đặc biệt, `invalid_code_rate = 0.00%` cho thấy mô hình không sinh ra mã taxonomy không tồn tại trong hệ thống.

Độ khó đạt 80.00%, thấp hơn các chỉ số taxonomy. Điều này có thể chấp nhận được ở giai đoạn hiện tại vì độ khó là tiêu chí mềm, phụ thuộc vào cách định nghĩa rubric và có thể khác nhau giữa người gán nhãn và mô hình.

## 5. Các trường hợp lệch độ khó

Trong 10 mẫu đánh giá, có 2 trường hợp độ khó chưa khớp với nhãn kỳ vọng.

### eval_003

- Dạng bài: Đạo hàm hàm ngược
- Expected difficulty: `easy`
- Predicted difficulty: `medium`

Nhận xét: Câu hỏi yêu cầu dùng công thức đạo hàm của hàm ngược. Mô hình xem đây là mức `medium` vì cần áp dụng một phương pháp cụ thể, không chỉ tính đạo hàm trực tiếp. Đây là cách phân loại có thể chấp nhận được.

### eval_004

- Dạng bài: Vi phân
- Expected difficulty: `medium`
- Predicted difficulty: `easy`

Nhận xét: Câu hỏi yêu cầu tính vi phân của hàm `y = x^2 sin x`. Mô hình xem đây là mức `easy` vì áp dụng trực tiếp công thức `dy = f'(x)dx`, dù có sử dụng quy tắc đạo hàm của tích. Sự khác biệt này phản ánh việc tiêu chí độ khó cần được mô tả chặt hơn.

## 6. Đánh giá mức độ đạt yêu cầu

So với tiêu chí MVP trong kế hoạch:

| Tiêu chí MVP | Kết quả hiện tại | Đánh giá |
|---|---:|---|
| Chapter accuracy >= 95% | 100.00% | Đạt |
| Topic accuracy >= 85% | 100.00% | Đạt |
| Problem type accuracy >= 75% | 100.00% | Đạt |
| Invalid code rate = 0% | 0.00% | Đạt |

Hệ thống đã đạt toàn bộ tiêu chí MVP của bước đánh giá AI Matching.

## 7. Ý nghĩa đối với hệ thống

Kết quả này cho thấy pipeline AI Matching đã hoạt động đúng về mặt chức năng và có khả năng phân loại câu hỏi vào cây tri thức Giải tích 1 với độ chính xác cao trên dataset thử nghiệm ban đầu.

Các thành phần đã được kiểm chứng gồm:

- Bộ não tri thức Giải tích 1
- Prompt phân loại
- AI classifier
- Bộ kiểm tra mã taxonomy hợp lệ
- Evaluator tính toán chỉ số
- Script đánh giá end-to-end

## 8. Hạn chế hiện tại

Dataset hiện tại mới có 10 câu hỏi, do đó kết quả chưa đủ lớn để kết luận chắc chắn về độ chính xác tổng quát của toàn hệ thống. Các mẫu hiện tại chủ yếu là câu hỏi rõ ràng, đại diện cho các dạng bài cơ bản.

Các hạn chế chính:

- Số lượng mẫu còn nhỏ.
- Chưa bao phủ đầy đủ toàn bộ taxonomy.
- Chưa có nhiều câu hỏi gây nhiễu hoặc dễ nhầm giữa các dạng bài gần nhau.
- Tiêu chí đánh giá độ khó còn cần chuẩn hóa thêm.

## 9. Hướng mở rộng đánh giá

Để kết quả đánh giá có giá trị hơn trong báo cáo, cần mở rộng dataset theo các hướng:

- Tăng số lượng mẫu lên 30-50 câu.
- Bổ sung câu hỏi ở các chủ đề dễ nhầm lẫn.
- Bổ sung các câu hỏi có tham số, hàm từng phần, chứng minh, biện luận.
- Đánh giá riêng từng chương.
- Ghi lại các case mô hình phân loại sai để cải thiện taxonomy và prompt.

## 10. Kết luận bước 12

Bước 12 đã hoàn thành ở mức MVP tốt. Hệ thống đạt độ chính xác cao khi matching câu hỏi vào cây tri thức ở các cấp chương, chủ đề và dạng bài.

Kết quả baseline hiện tại:

```text
Dataset: 10 câu
Model: gemini-2.5-pro
Chapter accuracy: 100.00%
Topic accuracy: 100.00%
Problem type accuracy: 100.00%
Difficulty accuracy: 80.00%
Low confidence rate: 0.00%
Invalid code rate: 0.00%
Failed count: 0
```

Kết quả này có thể được sử dụng làm số liệu thực nghiệm ban đầu trong báo cáo, đồng thời làm mốc so sánh cho các bước cải tiến tiếp theo như mở rộng dataset hoặc triển khai Hybrid Matching.
