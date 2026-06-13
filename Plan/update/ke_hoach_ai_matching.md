# Kế hoạch triển khai pipeline AI Matching câu hỏi vào cây tri thức Giải tích 1

Ngày cập nhật: 2026-06-12

## 1. Mục tiêu

Mục tiêu là hiện thực hóa pipeline:

```text
Upload tài liệu
-> Ingestion
-> Segment câu hỏi
-> AI Taxonomy Matching
-> Lưu metadata phân loại
-> Embedding
-> Semantic Search / Taxonomy Search / Generation
```

Hệ thống sau khi hoàn thiện phải chứng minh được:

- Có bộ não tri thức Giải tích 1 làm chuẩn phân loại.
- AI tự động match câu hỏi vào `chapter -> topic -> subtopic`.
- Kết quả match có `skills`, `difficulty`, `confidence`, `reason`.
- Metadata được lưu vào database.
- Search, taxonomy UI, problem detail và generation dùng được metadata này.
- Mỗi bước triển khai đều có test đầy đủ trước khi chuyển sang bước tiếp theo.

Nguyên tắc bắt buộc:

> Không chuyển sang bước tiếp theo nếu test của bước hiện tại chưa pass.

## 2. Tài liệu nền

Bộ não tri thức chính thức:

```text
Plan/update/buoc4_bo_nao_tri_thuc_giai_tich_1.md
```

Các tài liệu nguồn:

```text
Plan/update/buoc1_cay_kien_thuc_de_cuong.md
Plan/update/buoc2_doi_chieu_giao_trinh_slide.md
Plan/update/buoc3_trich_dang_bai_tu_bai_tap.md
Giải tích 1/Đề cương/2025.1_BTTK_MI1111.md
```

Quy ước:

- Taxonomy code dùng tiếng Anh, không dấu, ổn định cho backend.
- Tên hiển thị dùng tiếng Việt.
- Mức phân loại: chương + chủ đề + dạng bài.
- Độ khó: `easy`, `medium`, `hard`.

## 3. Pipeline đích

Pipeline hiện tại:

```text
Document upload
-> Ingestion
-> Question segmentation
-> Embedding
-> Search
```

Pipeline cần đạt:

```text
Document upload
-> Ingestion
-> Question segmentation
-> Taxonomy classification
-> Classification validation
-> Save classification metadata
-> Embedding with taxonomy metadata
-> Search/filter/statistics/generation
```

## 4. Nguyên tắc test bắt buộc

Mỗi bước phải có tối thiểu:

- Unit test cho logic thuần.
- Service test cho workflow chính.
- API test nếu có endpoint mới.
- Regression test để đảm bảo flow cũ không hỏng.
- Test case lỗi: input rỗng, output AI sai JSON, taxonomy code không tồn tại, confidence thấp.

Trước khi hoàn thành một bước phải chạy:

```text
.venv/Scripts/python.exe -m pytest -q
```

Tiêu chí qua bước:

- Toàn bộ test cũ pass.
- Test mới của bước hiện tại pass.
- Không phá vỡ API hiện có.
- Không làm mất khả năng upload, segment, embed, search hiện tại.

## 5. Bước 1 - Chuẩn hóa bộ não tri thức thành nguồn dùng được cho hệ thống

### Mục tiêu

Biến bộ não tri thức ở Markdown thành nguồn taxonomy ổn định để backend có thể sử dụng.

Nguồn chính:

```text
Plan/update/buoc4_bo_nao_tri_thuc_giai_tich_1.md
```

Đích triển khai khuyến nghị:

```text
core/taxonomy/calculus_1_taxonomy.yaml
```

hoặc:

```text
core/taxonomy/calculus_1_taxonomy.json
```

### Việc cần làm

1. Tạo bản taxonomy machine-readable.
2. Mỗi node cần có:
   - `code`
   - `display_name`
   - `level`
   - `parent`
   - `aliases`
   - `positive_signals`
   - `negative_signals`
   - `skills`
   - `default_difficulty`
   - `confusable_with`
   - `examples`
3. Giữ Markdown làm tài liệu giải thích cho người đọc.
4. Backend chỉ validate bằng YAML/JSON để tránh parse bảng Markdown phức tạp.

### Module dự kiến

```text
modules/taxonomy/
  __init__.py
  schemas.py
  loader.py
  validator.py
```

### Test bắt buộc

Tạo test:

```text
tests/modules/taxonomy/test_loader.py
tests/modules/taxonomy/test_validator.py
```

Test cần có:

- Load taxonomy thành công.
- Không có code trùng.
- Mọi `parent` đều tồn tại.
- Mọi `confusable_with` đều tồn tại.
- Mọi skill đều nằm trong skill vocabulary.
- Mỗi subtopic có `display_name`, `parent`, `default_difficulty`.
- Difficulty chỉ thuộc `easy`, `medium`, `hard`.
- Taxonomy có đủ 3 chương chính.

### Tiêu chí qua bước

- Taxonomy load được bằng code.
- Validator pass.
- Test taxonomy pass.
- Toàn bộ test project cũ vẫn pass.

## 6. Bước 2 - Thiết kế schema classification

### Mục tiêu

Tạo schema chuẩn cho kết quả AI Matching.

Output chuẩn:

```json
{
  "subject": "Calculus 1",
  "chapter": "GT1_C1_Differential_Calculus_One_Variable",
  "chapter_name": "Chương 1: Phép tính vi phân hàm một biến số",
  "topic": "GT1_C1_05_Function_Limits",
  "topic_name": "Giới hạn hàm số",
  "subtopic": "GT1_C1_05_T02_Algebraic_Transformation_Limit",
  "subtopic_name": "Tính giới hạn bằng biến đổi đại số",
  "skills": ["function_limit", "algebraic_transformation"],
  "difficulty": "medium",
  "confidence": 0.88,
  "reason": "Đề bài yêu cầu tính giới hạn hàm số và cần biến đổi biểu thức."
}
```

### Module dự kiến

```text
modules/question_classification/
  __init__.py
  schemas.py
```

### Việc cần làm

1. Tạo `QuestionClassificationResult`.
2. Tạo `QuestionClassificationRequest`.
3. Tạo `ClassificationIssue` nếu cần báo lỗi validate.
4. Tạo validator:
   - code tồn tại trong taxonomy
   - parent chain đúng
   - skill hợp lệ
   - difficulty hợp lệ
   - confidence trong `[0, 1]`

### Test bắt buộc

Tạo test:

```text
tests/modules/question_classification/test_schemas.py
tests/modules/question_classification/test_validation.py
```

Test cần có:

- Classification hợp lệ pass.
- Sai `chapter` fail.
- Sai `topic` fail.
- Sai `subtopic` fail.
- Topic không thuộc chapter fail.
- Subtopic không thuộc topic fail.
- Skill không tồn tại fail.
- Difficulty sai fail.
- Confidence âm hoặc lớn hơn 1 fail.
- Reason rỗng bị cảnh báo hoặc fail theo quy định.

### Tiêu chí qua bước

- Có schema rõ ràng.
- Validator chặn được output AI sai.
- Test pass toàn bộ.

## 7. Bước 3 - Xây prompt builder cho AI Matching

### Mục tiêu

Tạo prompt ổn định để gọi Gemini hoặc model AI classifier.

### Module dự kiến

```text
modules/question_classification/prompt_builder.py
```

### Việc cần làm

1. Nhận câu hỏi gồm:
   - statement
   - solution nếu có
   - answer nếu có
   - formulas nếu có
2. Nhận taxonomy context.
3. Build prompt chứa:
   - nhiệm vụ classifier
   - output schema
   - quy tắc chọn nhãn
   - confidence policy
   - danh sách topic/subtopic ứng viên
   - câu hỏi cần phân loại
4. Không để prompt quá dài ở MVP:
   - MVP có thể đưa toàn bộ taxonomy.
   - Bản tốt hơn chọn candidate topics trước.

### Test bắt buộc

Tạo test:

```text
tests/modules/question_classification/test_prompt_builder.py
```

Test cần có:

- Prompt chứa statement.
- Prompt chứa output schema.
- Prompt chứa taxonomy code quan trọng.
- Prompt chứa quy tắc không invent code.
- Prompt chứa difficulty rubric.
- Prompt không rỗng khi thiếu solution/answer.
- Prompt xử lý công thức LaTeX không làm mất backslash.

### Tiêu chí qua bước

- Prompt builder deterministic.
- Không phụ thuộc network.
- Test pass.

## 8. Bước 4 - Xây AI classifier adapter

### Mục tiêu

Tạo lớp gọi model AI để nhận JSON classification.

### Module dự kiến

```text
modules/question_classification/gemini_classifier.py
modules/question_classification/json_parser.py
```

### Việc cần làm

1. Gọi Gemini bằng API hiện có trong dự án.
2. Parse output JSON.
3. Hỗ trợ output có hoặc không có markdown fence.
4. Retry một lần nếu JSON lỗi.
5. Trả lỗi rõ ràng nếu model trả sai schema.

### Test bắt buộc

Không gọi network trong unit test. Dùng fake classifier.

Tạo test:

```text
tests/modules/question_classification/test_json_parser.py
tests/modules/question_classification/test_gemini_classifier.py
```

Test cần có:

- Parse JSON sạch.
- Parse JSON bọc trong ```json.
- JSON thiếu field bị fail.
- JSON có taxonomy code sai bị fail.
- Retry khi lần đầu JSON lỗi.
- Không retry vô hạn.
- Lỗi model được chuyển thành exception có message rõ.

### Tiêu chí qua bước

- Adapter có test bằng fake model.
- Parser ổn định.
- Test toàn project pass.

## 9. Bước 5 - Xây service phân loại một câu hỏi

### Mục tiêu

Tạo service chính:

```text
QuestionClassificationService.classify_question(question)
```

### Module dự kiến

```text
modules/question_classification/service.py
```

### Việc cần làm

1. Nhận `Question`.
2. Build input từ statement/solution/answer/formulas.
3. Load taxonomy.
4. Build prompt.
5. Gọi classifier.
6. Validate result.
7. Trả classification result.
8. Không tự commit database ở service này nếu muốn test dễ; phần lưu để repository xử lý.

### Test bắt buộc

Tạo test:

```text
tests/modules/question_classification/test_service.py
```

Test cần có:

- Classify câu "Tính tích phân từng phần" ra đúng expected với fake classifier.
- Classify câu "Tìm tập xác định" ra đúng expected với fake classifier.
- Nếu classifier trả code không tồn tại thì service fail.
- Nếu confidence thấp thì service vẫn trả result nhưng đánh dấu QA flag nếu có.
- Nếu question statement rỗng thì fail.

### Tiêu chí qua bước

- Service hoạt động độc lập với DB thật.
- Có fake classifier test đủ nhánh.
- Test pass.

## 10. Bước 6 - Cập nhật database để lưu kết quả matching

### Mục tiêu

Lưu đầy đủ kết quả AI Matching vào bảng `questions`.

### Field khuyến nghị

Thêm vào model `Question`:

```text
topic
subtopic
chapter_name
topic_name
subtopic_name
taxonomy_confidence
taxonomy_reason
taxonomy_version
classification_model
classified_at
classification_status
classification_error
```

Giữ field cũ:

```text
subject
chapter
difficulty
skills
```

### Việc cần làm

1. Cập nhật SQLAlchemy model.
2. Tạo migration Alembic hoặc script migration theo style hiện tại.
3. Cập nhật repository:
   - `update_classification`
   - `mark_classification_failed`
   - `list_unclassified_by_document`
   - `count_by_taxonomy`
4. Cập nhật response model nếu cần.

### Test bắt buộc

Tạo/cập nhật test:

```text
tests/modules/question_storage/test_service.py
tests/modules/question_classification/test_repository_integration.py
tests/api/test_questions.py
```

Test cần có:

- Update classification lưu đủ field.
- Mark failed lưu status/error.
- List unclassified trả đúng câu chưa classify.
- Count by taxonomy đúng theo chapter/topic/subtopic.
- Existing question API không hỏng.

### Tiêu chí qua bước

- Migration chạy được.
- Model/repository test pass.
- API cũ vẫn pass.

## 11. Bước 7 - Tích hợp classify vào document storage pipeline

### Mục tiêu

Cập nhật pipeline chính:

```text
segment_document -> classify_questions -> embed_document
```

### File liên quan

```text
modules/question_storage/service.py
```

### Việc cần làm

1. Sau khi `QuestionCatalogService.segment_document`, gọi classification cho từng câu.
2. Lưu metadata classification.
3. Nếu một câu classify lỗi:
   - lưu `classification_status = failed`
   - tiếp tục câu khác hoặc fail cả document tùy cấu hình
4. Sau khi classify xong, chạy embedding.
5. Embedding text nên có thêm taxonomy metadata nếu phù hợp:
   - chapter/topic/subtopic
   - skills
   - difficulty

### Test bắt buộc

Cập nhật/tạo test:

```text
tests/modules/question_storage/test_service.py
tests/modules/embeddings/test_text_builder.py
```

Test cần có:

- Store document gọi segment, classify, embed theo đúng thứ tự.
- Nếu không có câu hỏi thì fail như hiện tại.
- Nếu classifier thành công, question có metadata trước khi embed.
- Nếu classifier lỗi một câu, status failed được lưu.
- Embed vẫn chạy cho các câu hợp lệ nếu policy cho phép.
- Text builder có chứa taxonomy metadata nếu được cập nhật.

### Tiêu chí qua bước

- Pipeline unit test pass.
- Không phá flow store document hiện tại.
- Embedding vẫn pass test.

## 12. Bước 8 - API classify/rematch

### Mục tiêu

Expose chức năng AI Matching qua API.

### Endpoint cần có

```text
POST /questions/{question_id}/classify
POST /documents/{document_id}/classify
GET /taxonomy
GET /taxonomy/stats
```

Endpoint hiện có cần cập nhật:

```text
POST /documents/{document_id}/store
```

Ý nghĩa mới:

```text
segment + classify + embed
```

### Test bắt buộc

Tạo/cập nhật test:

```text
tests/api/test_question_classification_endpoint.py
tests/api/test_document_classification_endpoint.py
tests/api/test_taxonomy_endpoint.py
tests/api/test_documents_store_endpoint.py
```

Test cần có:

- Classify question trả classification result.
- Classify question 404 nếu question không tồn tại.
- Classify document trả số lượng success/failed.
- GET taxonomy trả đủ 3 chương.
- GET taxonomy stats đếm đúng mock DB.
- Store document chạy full pipeline.
- API trả lỗi 400 nếu document chưa completed.

### Tiêu chí qua bước

- API test pass.
- Swagger/API contract rõ.
- Frontend có thể gọi được.

## 13. Bước 9 - Cập nhật Semantic Search theo taxonomy

### Mục tiêu

Search tận dụng taxonomy metadata.

### Việc cần làm

1. Mở rộng search request:
   - `chapter`
   - `topic`
   - `subtopic`
   - `skill`
   - `difficulty`
2. Cập nhật Qdrant payload khi embed:
   - `chapter`
   - `topic`
   - `subtopic`
   - `skills`
   - `difficulty`
3. Cập nhật vector repository filter.
4. Cập nhật search response trả classification metadata.

### Test bắt buộc

Cập nhật test:

```text
tests/modules/semantic_search/test_service.py
tests/modules/embeddings/test_service.py
tests/modules/embeddings/test_vector_search_repository.py
tests/api/test_search.py
```

Test cần có:

- Search filter theo chapter.
- Search filter theo topic.
- Search filter theo subtopic.
- Search filter theo difficulty.
- Search response có topic/subtopic.
- Không có filter vẫn search như cũ.

### Tiêu chí qua bước

- Search cũ không hỏng.
- Search taxonomy filter hoạt động.
- Test pass toàn bộ.

## 14. Bước 10 - Frontend Upload/Problem Detail/Taxonomy/Search

### Mục tiêu

Người dùng nhìn thấy rõ pipeline AI Matching.

### Trang Upload Document

Cần hiển thị:

```text
Tách câu hỏi + AI match kiến thức + tạo embedding
```

Sau khi store:

```text
Đã tách: n câu
Match thành công: x câu
Confidence thấp: y câu
Embedding: z câu
```

### Trang Problem Detail

Cần hiển thị:

- chapter/topic/subtopic name
- difficulty
- skills
- confidence
- reason
- classification status
- nút `Re-match taxonomy`

### Trang Calculus Taxonomy

Cần dùng dữ liệu thật:

- GET taxonomy
- GET taxonomy stats
- danh sách câu hỏi theo topic/subtopic nếu có

### Trang Semantic Search

Cần filter theo:

- chapter
- topic
- subtopic
- difficulty
- skill

### Test bắt buộc

Nếu project frontend đã có test framework thì thêm test component/service. Nếu chưa có, tối thiểu phải kiểm tra build.

Test cần có:

```text
cd apps/frontend
npm run lint
npm run build
```

Nếu thêm test framework:

```text
apps/frontend/src/services/taxonomyApi.test.js
apps/frontend/src/services/questionApi.test.js
```

Manual test bắt buộc:

- Upload document.
- Store document.
- Mở Problem Detail thấy metadata.
- Re-match một question.
- Taxonomy page có số liệu thật.
- Search filter theo topic.

### Tiêu chí qua bước

- Frontend build pass.
- Lint pass.
- Không còn màn taxonomy chỉ dùng mock cho dữ liệu chính.

## 15. Bước 11 - QA taxonomy

### Mục tiêu

Phát hiện các câu hỏi chưa match tốt.

### Rule cần có

- Missing classification.
- Invalid taxonomy code.
- Low confidence.
- Missing skills.
- Invalid difficulty.
- Classification failed.
- Topic/subtopic mismatch.

### Test bắt buộc

Tạo test:

```text
tests/modules/question_quality/test_taxonomy_quality.py
tests/api/test_taxonomy_quality_endpoint.py
```

Test cần có:

- Câu chưa classify bị flag.
- Confidence thấp bị warning.
- Code sai bị error.
- Difficulty sai bị error.
- Missing skill bị warning.

### Tiêu chí qua bước

- QA phát hiện được lỗi taxonomy.
- QA page/API hiển thị được lỗi.
- Test pass.

## 16. Bước 12 - Evaluation dataset

### Mục tiêu

Chứng minh AI Matching hoạt động bằng số liệu.

### Dataset

Tạo file:

```text
tests/fixtures/calculus_1_classification_eval.json
```

Nên lấy tối thiểu 50 câu/ý từ:

```text
Giải tích 1/Đề cương/2025.1_BTTK_MI1111.md
```

Mỗi mẫu gồm:

```json
{
  "id": "Bai_58_a",
  "statement": "Tính int (x+2)ln x dx",
  "expected_chapter": "...",
  "expected_topic": "...",
  "expected_subtopic": "...",
  "expected_difficulty": "medium"
}
```

### Script đánh giá

Tạo script:

```text
scripts/evaluate_taxonomy_matching.py
```

Chỉ số:

```text
chapter_accuracy
topic_accuracy
subtopic_accuracy
difficulty_accuracy
low_confidence_rate
invalid_code_rate
```

### Test bắt buộc

Unit test cho evaluator:

```text
tests/modules/question_classification/test_evaluator.py
```

Test cần có:

- Tính accuracy đúng.
- Invalid code rate đúng.
- Low confidence rate đúng.
- Report không crash khi dataset rỗng.

### Tiêu chí qua bước

MVP mục tiêu:

```text
chapter_accuracy >= 95%
topic_accuracy >= 85%
subtopic_accuracy >= 75%
invalid_code_rate = 0%
```

Bản tốt:

```text
chapter_accuracy >= 98%
topic_accuracy >= 90%
subtopic_accuracy >= 82%
invalid_code_rate = 0%
```

## 17. Bước 13 - Hybrid Matching

### Mục tiêu

Nâng search từ semantic search thành matching tổng hợp.

### Công thức đề xuất

```text
final_score =
  0.50 * semantic_score
  + 0.20 * taxonomy_score
  + 0.15 * formula_score
  + 0.10 * difficulty_score
  + 0.05 * skill_score
```

### Việc cần làm

1. Tính taxonomy score:
   - cùng subtopic: cao nhất
   - cùng topic: trung bình
   - cùng chapter: thấp hơn
2. Tính skill overlap.
3. Tính difficulty compatibility.
4. Kết hợp với formula score nếu có.
5. Trả `final_score` và các thành phần score.

### Test bắt buộc

Tạo test:

```text
tests/modules/semantic_search/test_hybrid_matching.py
```

Test cần có:

- Cùng subtopic tăng score.
- Cùng topic nhưng khác subtopic tăng vừa.
- Khác chapter không tăng taxonomy score.
- Difficulty match tăng score.
- Skill overlap tăng score.
- Final score nằm trong khoảng hợp lệ.

### Tiêu chí qua bước

- Hybrid score deterministic.
- Search vẫn hoạt động nếu thiếu taxonomy metadata.
- Test pass.

## 18. Thứ tự triển khai khuyến nghị

Không làm song song quá nhiều. Thứ tự đề xuất:

```text
1. Taxonomy YAML/JSON + loader + validator
2. Classification schema + validator
3. Prompt builder
4. AI classifier adapter
5. Classification service
6. Database fields + repository
7. Integrate into QuestionStorageService
8. API classify/taxonomy/stats
9. Search filter by taxonomy
10. Frontend integration
11. QA taxonomy
12. Evaluation dataset
13. Hybrid Matching
```

Mỗi bước phải có test pass trước khi chuyển bước.

## 19. Definition of Done toàn hệ thống

Hệ thống được xem là hoàn thành pipeline AI Matching khi:

- Upload tài liệu được.
- Ingestion hoàn thành.
- Segment tách được câu hỏi.
- Mỗi câu hỏi được AI classify vào `chapter/topic/subtopic`.
- Classification được validate.
- Metadata được lưu DB.
- Embedding chứa taxonomy metadata.
- Search lọc được theo taxonomy.
- Problem Detail hiển thị kết quả match.
- Taxonomy page hiển thị thống kê thật.
- QA phát hiện câu chưa match hoặc confidence thấp.
- Có evaluation dataset và báo cáo accuracy.
- Toàn bộ backend test pass.
- Frontend lint/build pass.

## 20. Kịch bản demo bảo vệ

1. Upload một file bài tập Giải tích 1.
2. Chạy store document.
3. Hệ thống hiển thị:

```text
Segmented: n questions
Classified: x questions
Low confidence: y questions
Embedded: z questions
```

4. Mở một câu hỏi.
5. Xem:

```text
Chapter: Chương 2: Phép tính tích phân hàm một biến số
Topic: Tích phân bất định
Subtopic: Tích phân từng phần
Skills: integration_by_parts, indefinite_integral
Difficulty: medium
Confidence: 0.98
Reason: Đề bài nêu trực tiếp phương pháp tích phân từng phần.
```

6. Mở Taxonomy page.
7. Thấy số lượng câu hỏi theo topic/subtopic.
8. Search theo topic.
9. Tìm bài tương tự cùng subtopic.
10. Sinh biến thể từ câu đã match.

## 21. Rủi ro và kiểm soát

### AI trả JSON sai

Kiểm soát:

- JSON parser chặt.
- Retry một lần.
- Validate taxonomy code.
- Test parser đầy đủ.

### Match sai subtopic

Kiểm soát:

- Confidence policy.
- QA low confidence.
- Re-match thủ công.
- Evaluation dataset.

### Taxonomy quá dài

Kiểm soát:

- MVP dùng full taxonomy.
- Sau đó chọn candidate topics bằng keyword/embedding.

### Chi phí AI cao

Kiểm soát:

- Cache theo checksum statement.
- Chỉ re-classify khi taxonomy version đổi.
- Batch classify nếu cần.

### Metadata thay đổi sau embedding

Kiểm soát:

- Pipeline chuẩn: classify trước, embed sau.
- Nếu re-match thì update vector payload hoặc re-embed document.

## 22. Kết luận

Kế hoạch này biến dự án hiện tại từ:

```text
Kho câu hỏi + semantic search
```

thành:

```text
Hệ thống AI Matching câu hỏi Giải tích 1 vào cây tri thức,
kết hợp taxonomy matching, semantic search, formula search và generation.
```

Điều kiện bắt buộc xuyên suốt:

> Mọi bước code và triển khai phải có test đầy đủ. Chỉ được chuyển sang bước tiếp theo khi test của bước hiện tại và toàn bộ regression test đều pass.
