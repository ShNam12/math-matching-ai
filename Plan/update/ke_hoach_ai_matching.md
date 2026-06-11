# Kế hoạch AI Matching câu hỏi vào cây tri thức Giải tích

Ngày lập: 2026-06-11

## 1. Mục tiêu

Mục tiêu của hướng phát triển này là biến hệ thống hiện tại thành một hệ thống **AI Matching câu hỏi Giải tích vào cây tri thức**.

Hệ thống sau khi hoàn thiện cần làm được:

- Nhận tài liệu PDF/Markdown.
- Chuyển tài liệu thành Markdown chuẩn.
- Tách tài liệu thành các câu hỏi riêng.
- Dùng **bộ não tri thức Giải tích** để AI phân loại từng câu hỏi.
- Gán câu hỏi vào đúng chương, chủ đề, dạng bài, kỹ năng và độ khó.
- Lưu kết quả phân loại vào database.
- Dùng metadata phân loại để tìm kiếm, lọc, thống kê, sinh biến thể và gợi ý bài tương tự.

Định nghĩa ngắn gọn:

> AI Matching trong dự án này là quá trình dùng AI để đọc hiểu câu hỏi Giải tích, đối chiếu với cây tri thức đã xây dựng, sau đó tự động match câu hỏi vào mục kiến thức phù hợp nhất.

## 2. Lý do cần cập nhật

Dự án hiện tại đã có nền tảng tốt:

- Upload tài liệu.
- Xử lý tài liệu đầu vào.
- Tách câu hỏi.
- Lưu câu hỏi.
- Tạo embedding.
- Tìm kiếm ngữ nghĩa.
- Tìm kiếm công thức.
- Sinh biến thể câu hỏi.
- Kiểm định chất lượng câu hỏi sinh.
- Giao diện Taxonomy.

Tuy nhiên, hệ thống hiện chưa có bước bắt buộc để được gọi chắc là AI Matching theo hướng thầy yêu cầu:

```text
Câu hỏi -> AI đọc hiểu -> đối chiếu cây tri thức -> match vào mục kiến thức
```

Hiện tại các trường metadata như `subject`, `chapter`, `difficulty`, `skills` đã tồn tại trong bảng `questions`, nhưng chưa có cơ chế AI tự động gán đầy đủ sau khi tách câu hỏi.

Vì vậy cần bổ sung một lớp mới: **AI Taxonomy Matching**.

## 3. Bộ não tri thức của hệ thống

Đây là phần bắt buộc và quan trọng nhất của hướng phát triển này.

### 3.1. Vai trò của bộ não tri thức

Bộ não tri thức là file Markdown chứa toàn bộ cấu trúc kiến thức Giải tích mà hệ thống dùng để match câu hỏi.

File hiện tại:

```text
Plan/calculus_knowledge_taxonomy.md
```

File này đóng vai trò như:

- Cây kiến thức Giải tích.
- Ontology/taxonomy cho hệ thống.
- Tài liệu chuẩn để AI classifier đối chiếu.
- Nguồn dữ liệu để hiển thị trên giao diện Taxonomy.
- Chuẩn metadata cho search, analytics và generation.

Nói đơn giản:

> Nếu AI classifier là người phân loại, thì `calculus_knowledge_taxonomy.md` là giáo trình/khung kiến thức mà AI phải bám theo.

### 3.2. Nội dung cần có trong bộ não tri thức

File tri thức cần có các phần sau:

- Danh sách chương lớn.
- Danh sách topic trong từng chương.
- Danh sách subtopic/dạng bài.
- Dấu hiệu nhận diện từng dạng bài.
- Danh sách kỹ năng chuẩn.
- Quy tắc đánh giá độ khó.
- Schema JSON đầu ra.
- Ví dụ phân loại mẫu.
- Prompt template để gọi AI.

Ví dụ cấu trúc:

```text
GT03_Integrals
  GT03.03_Integration_By_Parts
    GT03.03.01_Basic_By_Parts
    GT03.03.02_Repeated_By_Parts
    GT03.03.03_Cyclic_By_Parts
```

Ví dụ một câu hỏi:

```text
Tính tích phân ∫ x^2 e^x dx.
```

Kết quả match mong muốn:

```json
{
  "subject": "Calculus",
  "chapter": "GT03_Integrals",
  "topic": "GT03.03_Integration_By_Parts",
  "subtopic": "GT03.03.02_Repeated_By_Parts",
  "skills": ["integration_by_parts", "indefinite_integral"],
  "difficulty": "medium",
  "confidence": 0.92,
  "reason": "Bài có dạng tích của đa thức và hàm mũ, cần dùng tích phân từng phần lặp lại."
}
```

### 3.3. Yêu cầu đối với bộ não tri thức

Bộ não tri thức cần đảm bảo:

- Không quá chung chung.
- Mỗi topic/subtopic có mã định danh rõ ràng.
- Tên mã ổn định để lưu database.
- Có dấu hiệu nhận diện để AI dễ phân loại.
- Có skill vocabulary thống nhất.
- Có rubric độ khó để AI không gán tùy tiện.
- Có ví dụ để tăng độ ổn định khi gọi model.

### 3.4. Vai trò khi bảo vệ đồ án

Khi bảo vệ, bộ não tri thức giúp chứng minh:

- Hệ thống có cơ sở tri thức rõ ràng.
- AI không phân loại ngẫu nhiên.
- Mỗi câu hỏi được match vào một mục kiến thức có định nghĩa.
- Có thể giải thích vì sao câu hỏi thuộc mục đó.
- Có thể thống kê số lượng câu hỏi theo từng mục kiến thức.

Đây là điểm giúp dự án khác với một hệ thống semantic search thông thường.

## 4. Kiến trúc tổng thể sau cập nhật

Flow hiện tại:

```text
Upload tài liệu
-> Ingestion
-> Segment câu hỏi
-> Embedding
-> Semantic Search
```

Flow cần cập nhật:

```text
Upload tài liệu
-> Ingestion
-> Segment câu hỏi
-> AI Taxonomy Matching
-> Save metadata
-> Embedding
-> Semantic Search / Formula Search / Taxonomy Search
```

Trong đó bước mới là:

```text
AI Taxonomy Matching
```

Bước này sẽ:

- Đọc câu hỏi.
- Đọc bộ não tri thức.
- Gọi AI classifier.
- Nhận JSON phân loại.
- Validate kết quả.
- Lưu metadata vào database.

## 5. Các module cần bổ sung

### 5.1. Module taxonomy

Đề xuất thêm module:

```text
modules/taxonomy/
```

Chức năng:

- Đọc file `calculus_knowledge_taxonomy.md`.
- Trích xuất nội dung taxonomy.
- Cung cấp taxonomy cho AI classifier.
- Có thể parse một phần thành cấu trúc dùng cho UI/API.

Các file dự kiến:

```text
modules/taxonomy/__init__.py
modules/taxonomy/loader.py
modules/taxonomy/schemas.py
```

### 5.2. Module question classification

Đề xuất thêm module:

```text
modules/question_classification/
```

Chức năng:

- Nhận `Question`.
- Build prompt từ câu hỏi và taxonomy.
- Gọi Gemini.
- Parse JSON.
- Validate schema.
- Trả kết quả classification.

Các file dự kiến:

```text
modules/question_classification/__init__.py
modules/question_classification/schemas.py
modules/question_classification/prompt_builder.py
modules/question_classification/gemini_classifier.py
modules/question_classification/service.py
```

Output chính:

```json
{
  "subject": "Calculus",
  "chapter": "GT03_Integrals",
  "topic": "GT03.03_Integration_By_Parts",
  "subtopic": "GT03.03.02_Repeated_By_Parts",
  "skills": ["integration_by_parts", "indefinite_integral"],
  "difficulty": "medium",
  "confidence": 0.92,
  "reason": "..."
}
```

### 5.3. Tích hợp vào question storage

Hiện có service:

```text
modules/question_storage/service.py
```

Service này đang làm:

```text
segment_document -> embed_document
```

Cần đổi thành:

```text
segment_document -> classify_questions -> embed_document
```

Đây là điểm tích hợp tự nhiên nhất vì nó nằm đúng giữa tách câu hỏi và embedding.

## 6. Cập nhật database

### 6.1. Phương án tối thiểu

Không sửa database nhiều, tận dụng field có sẵn:

- `subject`: lưu `Calculus`.
- `chapter`: lưu chapter hoặc topic code.
- `difficulty`: lưu `easy`, `medium`, `hard`.
- `skills`: lưu danh sách kỹ năng.

Ưu điểm:

- Ít thay đổi.
- Làm nhanh.
- Phù hợp MVP.

Nhược điểm:

- Không lưu được đầy đủ topic/subtopic.
- Không lưu được confidence/reason.
- Khó chứng minh khả năng explainable matching.

### 6.2. Phương án khuyến nghị

Nên bổ sung thêm các field:

```text
topic
subtopic
taxonomy_confidence
taxonomy_reason
taxonomy_version
classified_at
classification_model
```

Ý nghĩa:

- `topic`: topic AI match được.
- `subtopic`: dạng bài cụ thể.
- `taxonomy_confidence`: độ tin cậy.
- `taxonomy_reason`: lý do AI chọn mục đó.
- `taxonomy_version`: phiên bản file tri thức.
- `classified_at`: thời điểm phân loại.
- `classification_model`: model đã dùng.

Ưu điểm:

- Rõ ràng hơn khi bảo vệ.
- UI hiển thị được lý do match.
- Có thể đánh giá chất lượng matching.
- Dễ re-classify khi taxonomy thay đổi.

Khuyến nghị: dùng phương án này nếu còn đủ thời gian.

## 7. API cần bổ sung

### 7.1. Classify một câu hỏi

```text
POST /questions/{question_id}/classify
```

Chức năng:

- Chạy AI matching cho một câu hỏi.
- Cập nhật metadata.
- Trả kết quả classification.

Dùng cho:

- Nút "Re-match" ở trang chi tiết câu hỏi.
- Kiểm tra từng câu khi demo.

### 7.2. Classify toàn bộ câu hỏi trong document

```text
POST /documents/{document_id}/classify
```

Chức năng:

- Lấy tất cả câu hỏi của document.
- Chạy AI matching từng câu.
- Lưu metadata.
- Trả số lượng thành công/thất bại.

Dùng cho:

- Tài liệu đã tách câu hỏi nhưng chưa phân loại.
- Chạy lại classification khi cập nhật taxonomy.

### 7.3. Store document full pipeline

Endpoint hiện tại:

```text
POST /documents/{document_id}/store
```

Cần cập nhật ý nghĩa thành:

```text
segment + classify + embed
```

Đây sẽ là pipeline chính.

### 7.4. Lấy taxonomy

```text
GET /taxonomy
```

Chức năng:

- Trả cây tri thức từ file Markdown hoặc bản parse.
- Dùng cho frontend Taxonomy page.

### 7.5. Lấy thống kê taxonomy

```text
GET /taxonomy/stats
```

Chức năng:

- Đếm số câu hỏi theo chapter/topic/subtopic.
- Đếm số câu theo difficulty.
- Đếm số câu thiếu classification.
- Đếm số câu confidence thấp.

## 8. Cập nhật frontend

### 8.1. Trang Upload Document

Hiện đã có nút store document.

Cần cập nhật:

- Nút này nên thể hiện rõ:

```text
Tách câu hỏi + AI match kiến thức + tạo embedding
```

- Sau khi chạy xong, hiển thị:

```text
Đã tách: 50 câu
Đã match taxonomy: 48 câu
Confidence thấp: 2 câu
Đã tạo embedding: 50 câu
```

### 8.2. Trang Calculus Taxonomy

Hiện trang này đang giống ảnh thầy mong muốn nhưng dữ liệu còn static.

Cần cập nhật:

- Lấy cây tri thức từ backend.
- Lấy thống kê thật từ database.
- Mỗi topic hiển thị:
  - tổng số câu hỏi
  - số easy
  - số medium
  - số hard
  - số confidence thấp

Khi click một topic:

- Hiển thị mô tả topic.
- Hiển thị kỹ năng yêu cầu.
- Hiển thị danh sách câu hỏi thuộc topic.
- Có nút xem câu hỏi.
- Có nút tìm bài tương tự trong topic.

### 8.3. Trang Problem Detail

Cần hiển thị kết quả AI Matching:

- Chapter.
- Topic.
- Subtopic.
- Skills.
- Difficulty.
- Confidence.
- Reason.
- Classification model.
- Classified time.

Cần thêm nút:

```text
Re-match taxonomy
```

Nút này gọi:

```text
POST /questions/{question_id}/classify
```

### 8.4. Trang Semantic Search

Cần bổ sung filter theo taxonomy:

- Chapter.
- Topic.
- Subtopic.
- Difficulty.
- Skill.

Kết quả search nên hiển thị:

- score semantic.
- matched topic.
- difficulty.
- skills.

### 8.5. Trang QA Rules

Cần thêm nhóm kiểm định taxonomy:

- Câu hỏi chưa được match.
- Câu hỏi confidence thấp.
- Câu hỏi có topic nhưng thiếu skill.
- Câu hỏi có difficulty không hợp lệ.
- Câu hỏi bị nghi ngờ match sai.

## 9. Hybrid AI Matching

Để hệ thống mạnh hơn, nên định nghĩa điểm match tổng hợp.

Ví dụ:

```text
final_score =
  0.50 * semantic_score
  + 0.20 * taxonomy_score
  + 0.15 * formula_score
  + 0.10 * difficulty_score
  + 0.05 * skill_score
```

Trong đó:

- `semantic_score`: độ tương tự embedding.
- `taxonomy_score`: cùng chapter/topic/subtopic.
- `formula_score`: độ tương tự công thức.
- `difficulty_score`: cùng độ khó hoặc gần độ khó.
- `skill_score`: trùng kỹ năng.

Giai đoạn đầu có thể chưa cần làm đầy đủ. Nhưng khi trình bày đồ án, đây là hướng mở rộng rất tốt để chứng minh hệ thống là AI Matching chứ không chỉ semantic search.

## 10. Quy trình triển khai đề xuất

### Giai đoạn 1: Chuẩn hóa bộ não tri thức

Mục tiêu:

- Hoàn thiện `Plan/calculus_knowledge_taxonomy.md`.
- Chuẩn hóa mã chapter/topic/subtopic.
- Chuẩn hóa skill vocabulary.
- Chuẩn hóa difficulty rubric.

Kết quả:

- Có file tri thức dùng được cho classifier.

### Giai đoạn 2: Xây dựng AI classifier

Mục tiêu:

- Tạo module classification.
- Đọc taxonomy.
- Build prompt.
- Gọi Gemini.
- Parse JSON.
- Validate kết quả.

Kết quả:

- Có service phân loại một câu hỏi.

### Giai đoạn 3: Lưu metadata classification

Mục tiêu:

- Cập nhật database nếu chọn phương án đầy đủ.
- Thêm repository method để cập nhật classification.
- Lưu `chapter`, `topic`, `subtopic`, `skills`, `difficulty`, `confidence`, `reason`.

Kết quả:

- Câu hỏi sau khi classify có metadata rõ ràng.

### Giai đoạn 4: Tích hợp vào document pipeline

Mục tiêu:

- Cập nhật `QuestionStorageService`.
- Sau segment thì chạy classify.
- Sau classify thì chạy embed.

Kết quả:

- Một tài liệu sau khi store sẽ sẵn sàng cho AI Matching/Search.

### Giai đoạn 5: API classify/rematch

Mục tiêu:

- Thêm endpoint classify question.
- Thêm endpoint classify document.
- Cập nhật endpoint store document.

Kết quả:

- Có thể chạy match tự động hoặc thủ công.

### Giai đoạn 6: Cập nhật UI

Mục tiêu:

- Upload page hiển thị trạng thái classify.
- Taxonomy page dùng dữ liệu thật.
- Problem detail hiển thị kết quả matching.
- Semantic search filter theo taxonomy.

Kết quả:

- Người dùng nhìn thấy rõ hệ thống đang match câu hỏi vào cây tri thức.

### Giai đoạn 7: Đánh giá chất lượng AI Matching

Mục tiêu:

- Tạo bộ test 30-50 câu hỏi mẫu.
- Gán nhãn đúng thủ công.
- Chạy AI classifier.
- So sánh kết quả.

Chỉ số nên có:

- Accuracy theo chapter.
- Accuracy theo topic.
- Accuracy theo difficulty.
- Tỷ lệ confidence thấp.
- Ví dụ đúng/sai.

Kết quả:

- Có bằng chứng định lượng để bảo vệ đồ án.

## 11. Tiêu chí hoàn thành

Hệ thống được xem là đạt hướng AI Matching khi có đủ:

- Có file bộ não tri thức Giải tích.
- AI tự động match câu hỏi vào cây tri thức.
- Kết quả match được lưu vào database.
- Có confidence và reason hoặc ít nhất có metadata rõ ràng.
- Taxonomy page hiển thị dữ liệu thật.
- Problem detail hiển thị câu hỏi thuộc mục kiến thức nào.
- Search có thể lọc theo mục kiến thức.
- Có demo end-to-end từ upload tài liệu đến câu hỏi được match.

## 12. Demo bảo vệ đề xuất

Kịch bản demo:

1. Upload một file Markdown/PDF có nhiều câu hỏi Giải tích.
2. Hệ thống xử lý tài liệu.
3. Bấm store document.
4. Hệ thống tách câu hỏi.
5. Hệ thống AI match từng câu vào cây tri thức.
6. Mở một câu hỏi cụ thể.
7. Hiển thị:

```text
Matched chapter: GT03_Integrals
Matched topic: GT03.03_Integration_By_Parts
Matched subtopic: GT03.03.02_Repeated_By_Parts
Skills: integration_by_parts, indefinite_integral
Difficulty: medium
Confidence: 0.92
Reason: ...
```

8. Mở Taxonomy page.
9. Thấy topic tương ứng tăng số lượng câu hỏi.
10. Tìm bài tương tự trong cùng topic.
11. Sinh biến thể từ câu hỏi đã match.

Kịch bản này chứng minh rõ:

- Có bộ não tri thức.
- Có AI Matching.
- Có lưu metadata.
- Có sử dụng metadata để search, taxonomy và generation.

## 13. Những rủi ro và cách xử lý

### 13.1. AI trả JSON sai

Cách xử lý:

- Parse JSON chặt chẽ.
- Nếu lỗi, retry một lần.
- Nếu vẫn lỗi, lưu trạng thái classification failed.

### 13.2. AI match sai topic

Cách xử lý:

- Lưu confidence.
- Nếu confidence thấp, đưa vào QA.
- Cho người dùng chỉnh metadata thủ công.
- Có nút re-match.

### 13.3. File taxonomy quá dài

Cách xử lý:

- Giai đoạn đầu đưa toàn bộ taxonomy vào prompt.
- Giai đoạn sau có thể tách taxonomy theo chapter.
- Có thể dùng embedding để chọn các topic ứng viên trước, rồi mới gọi AI classify.

### 13.4. Chi phí gọi AI cao

Cách xử lý:

- Chỉ classify sau khi segment xong.
- Cache kết quả theo checksum câu hỏi.
- Batch classification nếu model hỗ trợ.
- Chỉ re-classify khi taxonomy version thay đổi.

### 13.5. Metadata thay đổi sau khi embedding

Cách xử lý:

- Pipeline chuẩn là classify trước, embed sau.
- Nếu re-match sau này, cần re-embed document hoặc cập nhật payload vector.

## 14. Phạm vi MVP

Nếu cần làm nhanh để chắc chắn đúng hướng, MVP nên gồm:

- Dùng `calculus_knowledge_taxonomy.md` làm bộ não tri thức.
- Classify từng câu hỏi bằng Gemini.
- Lưu `subject`, `chapter`, `difficulty`, `skills`.
- Có API classify document.
- Store document chạy `segment + classify + embed`.
- Problem Detail hiển thị metadata AI match.
- Taxonomy page hiển thị số lượng thật theo chapter/topic ở mức đơn giản.

MVP này đã đủ để gọi là:

> AI Matching câu hỏi Giải tích vào cây tri thức.

## 15. Phạm vi bản hoàn thiện

Bản hoàn thiện nên có thêm:

- Lưu `topic`, `subtopic`, `confidence`, `reason`.
- Taxonomy stats đầy đủ.
- Re-match từng câu.
- QA taxonomy.
- Evaluation dataset.
- Hybrid matching score.
- Tìm bài tương tự ưu tiên cùng topic/subtopic.

## 16. Kết luận

Hướng phát triển này khả thi vì tận dụng tối đa code hiện tại.

Phần cần thêm không phải là xây lại toàn bộ hệ thống, mà là bổ sung một lớp mới:

```text
AI Taxonomy Matching
```

Lớp này dựa trên bộ não tri thức:

```text
Plan/calculus_knowledge_taxonomy.md
```

Sau khi bổ sung, hệ thống sẽ chuyển từ:

```text
Kho câu hỏi + semantic search
```

thành:

```text
Hệ thống AI Matching câu hỏi Giải tích vào cây tri thức,
kết hợp semantic search, formula search và sinh biến thể câu hỏi.
```

Đây là hướng rõ ràng, đúng yêu cầu, dễ demo và có cơ sở để bảo vệ trước giảng viên.

