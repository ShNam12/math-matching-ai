# Update trắc nghiệm - Thiết kế chuyển hệ thống AI Matching sang ngân hàng câu hỏi trắc nghiệm có Neuro-symbolic Validation

Ngày cập nhật: 2026-06-21

## 1. Mục tiêu

Tài liệu này thiết kế lộ trình chuyển hệ thống hiện tại từ hướng xử lý câu hỏi tự luận/tự do sang hệ thống ngân hàng câu hỏi trắc nghiệm Toán học.

Hệ thống sau cập nhật cần đạt được:

- Lưu trữ được câu hỏi trắc nghiệm chuẩn gồm đề bài, các lựa chọn A/B/C/D, đáp án đúng, lời giải và metadata.
- Tận dụng tiếp pipeline hiện có: ingestion, question segmentation, taxonomy classification, semantic search, formula search, AI matching, generation và quality check.
- Tích hợp logic từ dự án cũ `MathBank-main`: solver Symbolic/SymPy, sinh đáp án nhiễu, rule-based validation.
- Chuyển trọng tâm đồ án tốt nghiệp thành:

```text
Hệ thống ngân hàng câu hỏi trắc nghiệm Toán học
tích hợp AI Matching, Semantic Search, Taxonomy Classification
và Neuro-symbolic Validation.
```

Nguyên tắc quan trọng:

> Không đập bỏ hệ thống hiện tại. Mở rộng schema và pipeline để hỗ trợ trắc nghiệm, sau đó dần đặt trắc nghiệm làm dạng câu hỏi chính.

## 2. Bối cảnh hệ thống hiện tại

Hệ thống hiện tại đã có các phần nền:

- Ingestion tài liệu PDF/Markdown.
- Chuẩn hóa nội dung và tách câu hỏi.
- Lưu câu hỏi vào database.
- Phân loại câu hỏi theo taxonomy Giải tích 1.
- Embedding, semantic search và formula search.
- Sinh biến thể câu hỏi bằng AI.
- Quality check cho câu hỏi sinh ra.
- Frontend gồm Dashboard, Upload Document, Semantic Search, Problem Detail, GenVariants, QA Rules, Analytics.

Schema câu hỏi hiện tại thiên về tự luận:

```text
statement
solution
answer
formulas
subject
chapter
difficulty
skills
taxonomy metadata
embedding metadata
classification metadata
```

Dự án cũ `MathBank-main` có các phần cần kế thừa:

```text
SolverService
DistractorService
QuestionGenerationService.generate_batch
_validate_quality
ALL_SOLVERS
```

Ý nghĩa khi tích hợp:

- Hệ thống hiện tại cung cấp data pipeline, AI matching, search và UI.
- Dự án cũ cung cấp lõi sinh trắc nghiệm, solver symbolic và sinh đáp án nhiễu.
- Bản tốt nghiệp kết hợp hai phần thành hệ thống hoàn chỉnh hơn.

## 3. Pipeline đích sau cập nhật

Pipeline tổng thể:

```text
Upload tài liệu
-> Ingestion/OCR/Markdown normalization
-> Segment câu hỏi hoặc đoạn kiến thức
-> Taxonomy classification
-> Lưu corpus có metadata
-> Embedding câu hỏi + công thức + lựa chọn đáp án
-> Semantic search / AI matching
-> Sinh câu hỏi trắc nghiệm
-> Tính đáp án đúng bằng solver hoặc AI
-> Sinh đáp án nhiễu
-> Neuro-symbolic validation
-> Quality report
-> Review/chỉnh sửa
-> Lưu vào ngân hàng câu hỏi
```

Pipeline sinh câu hỏi trắc nghiệm:

```text
Source question hoặc taxonomy target
-> MCQ generation prompt
-> Candidate MCQ
-> Parse/normalize choices
-> Symbolic solver check nếu có solver phù hợp
-> Distractor validation
-> Duplicate/semantic/taxonomy quality check
-> Preview trên UI
-> Save nếu không có blocking issue
```

## 4. Dữ liệu đích

### 4.1. Schema câu hỏi trắc nghiệm

Mỗi câu hỏi trắc nghiệm cần có tối thiểu:

```json
{
  "id": "...",
  "question_type": "multiple_choice",
  "statement": "Tính tích phân ...",
  "choices": [
    {
      "key": "A",
      "text": "...",
      "latex": "...",
      "is_correct": false,
      "distractor_type": "sign_error",
      "rationale": "Sai do đổi dấu."
    },
    {
      "key": "B",
      "text": "...",
      "latex": "...",
      "is_correct": true,
      "distractor_type": null,
      "rationale": null
    }
  ],
  "correct_choice": "B",
  "answer": "...",
  "solution": "Lời giải chi tiết",
  "formulas": [],
  "subject": "Calculus 1",
  "chapter": "...",
  "topic_code": "...",
  "problem_type_code": "...",
  "difficulty": "medium",
  "skills": ["integration_by_parts"],
  "generation_method": "ai_symbolic",
  "solver_code": "INT_XN_EXP",
  "validation_report": {
    "can_save": true,
    "warnings": [],
    "blocking_issues": [],
    "symbolic_checks": []
  }
}
```

### 4.2. Giữ tương thích với dữ liệu cũ

Không xóa các field cũ:

```text
statement
solution
answer
formulas
subject
chapter
difficulty
skills
```

Lý do:

- Không phá API, tests và UI hiện tại.
- Câu hỏi tự luận đã ingest trước đó vẫn dùng được.
- Search và embedding hiện tại vẫn có nguồn text ổn định.
- Cho phép chuyển đổi từng bước thay vì migration lớn một lần.

Quy ước:

- `question_type = "free_response"` cho câu cũ hoặc câu tự luận.
- `question_type = "multiple_choice"` cho câu trắc nghiệm.
- `answer` vẫn lưu đáp án đúng dạng text/math.
- `correct_choice` lưu nhãn A/B/C/D.
- `choices` lưu toàn bộ lựa chọn.

## 5. Nguyên tắc test bắt buộc

Mỗi giai đoạn phải có:

- Unit test cho logic thuần.
- Service test cho workflow chính.
- Repository/migration test nếu đụng database.
- API test nếu thay đổi endpoint/request/response.
- Frontend lint/build nếu thay đổi UI.
- Regression test để đảm bảo flow cũ không hỏng.

Lệnh kiểm tra backend:

```text
.venv/Scripts/python.exe -m pytest -q
```

Lệnh kiểm tra frontend:

```text
cd apps/frontend
npm run lint
npm run build
```

Tiêu chí qua mỗi bước:

- Test mới của bước đó pass.
- Toàn bộ test cũ pass.
- API cũ không bị phá.
- Dữ liệu tự luận cũ vẫn đọc được.
- Nếu bước có migration, migration chạy được trên database trống và database đã có dữ liệu.

## 6. Giai đoạn 1 - Thiết kế và mở rộng schema dữ liệu trắc nghiệm

### Mục tiêu

Thêm khả năng lưu câu hỏi trắc nghiệm vào database mà không làm hỏng câu hỏi cũ.

### Vì sao cần làm trước

Mọi phần phía sau đều phụ thuộc vào schema:

- Generation cần trả về choices.
- Quality check cần kiểm tra choices.
- Search cần index choices.
- Frontend cần hiển thị A/B/C/D.
- Save API cần lưu `correct_choice`.

Nếu không chuẩn hóa schema trước, các bước sau sẽ phải sửa đi sửa lại.

### Bước 1.1 - Định nghĩa model dữ liệu MCQ nội bộ

Việc cần làm:

1. Tạo schema/dataclass cho lựa chọn đáp án:

```text
MultipleChoiceOption
```

Field đề xuất:

```text
key: A/B/C/D
text
latex
is_correct
distractor_type
rationale
metadata
```

2. Tạo schema/dataclass cho validation report:

```text
QuestionValidationReport
QualityIssue
SymbolicCheckResult
```

3. Mở rộng candidate sinh câu hỏi:

```text
GeneratedQuestionCandidate
```

Thêm:

```text
question_type
choices
correct_choice
symbolic_answer
generation_method
solver_code
validation_report
```

Module dự kiến:

```text
modules/question_generation/schemas.py
modules/question_quality/schemas.py
```

Test bắt buộc:

```text
tests/modules/question_generation/test_schemas.py
tests/modules/question_quality/test_schemas.py
```

Test cần có:

- Tạo candidate tự luận cũ vẫn hợp lệ.
- Tạo candidate trắc nghiệm có 4 choices hợp lệ.
- Choice thiếu key bị phát hiện.
- Choice có `is_correct` không phải boolean bị phát hiện nếu dùng schema validate.
- `validation_report.can_save = false` khi có blocking issue.
- Serialize/deserialize candidate không mất choices.

Tiêu chí qua bước:

- Schema mới tồn tại.
- Code cũ dùng `GeneratedQuestionCandidate` không hỏng.
- Test schema pass.

### Bước 1.2 - Mở rộng database model

Việc cần làm:

1. Cập nhật `infra/db/models.py`, bảng `questions`.
2. Thêm các field:

```text
question_type: Text, default "free_response"
choices: JSON, default []
correct_choice: Text, nullable
validation_report: JSON, default {}
generation_method: Text, nullable
solver_code: Text, nullable
distractor_metadata: JSON, default {}
```

3. Tạo migration script theo style hiện tại trong `scripts/`.

Tên gợi ý:

```text
scripts/migrate_step_mcq_fields.py
```

4. Đảm bảo dữ liệu cũ sau migration có:

```text
question_type = "free_response"
choices = []
validation_report = {}
```

Lý do:

- JSON field giúp lưu choices linh hoạt, chưa cần tách bảng option riêng.
- MVP nhanh hơn, ít phá repository hiện tại.
- Sau này nếu cần thống kê lựa chọn chi tiết có thể tách bảng `question_choices`.

Test bắt buộc:

```text
tests/modules/question_storage/test_service.py
tests/api/test_questions.py
```

Nếu có test repository integration:

```text
tests/modules/question_storage/test_repository_mcq.py
```

Test cần có:

- Tạo question tự luận không truyền choices vẫn lưu được.
- Tạo question trắc nghiệm với choices và correct_choice lưu được.
- Đọc question trắc nghiệm trả đủ choices.
- Migration chạy được khi bảng đã có dữ liệu cũ.
- Migration idempotent hoặc fail rõ nếu chạy lại.
- API question detail trả field mới nhưng không làm hỏng response cũ.

Tiêu chí qua bước:

- Database có field MCQ.
- Question cũ vẫn đọc được.
- Question mới lưu được choices.
- Test backend pass.

### Bước 1.3 - Cập nhật repository và API models

Việc cần làm:

1. Cập nhật repository:

```text
infra/db/repositories/questions.py
```

2. Cập nhật API response/request:

```text
apps/api/v1/models/questions.py
apps/api/v1/models/search.py
apps/api/v1/models/generation.py
```

3. Cập nhật endpoint question detail/search/generation save trả thêm:

```text
question_type
choices
correct_choice
validation_report
generation_method
solver_code
```

Lý do:

- Frontend cần dữ liệu này.
- Search result cần hiển thị trắc nghiệm.
- Generation save cần lưu candidate MCQ.

Test bắt buộc:

```text
tests/api/test_questions.py
tests/api/test_search.py
tests/api/test_generation_models.py
tests/api/test_generation_save_endpoint.py
```

Test cần có:

- Question detail có choices.
- Search result có choices.
- Save generated MCQ trả correct_choice.
- Save generated tự luận cũ vẫn pass.
- Request thiếu choices với `question_type = multiple_choice` bị reject hoặc quality blocking.

Tiêu chí qua bước:

- API contract hỗ trợ MCQ.
- Frontend có thể đọc dữ liệu mới.
- Regression test API pass.

## 7. Giai đoạn 2 - Chuẩn hóa quality rules cho câu hỏi trắc nghiệm

### Mục tiêu

Tạo bộ rule kiểm định câu hỏi trắc nghiệm trước khi tích hợp sinh câu hỏi.

### Vì sao cần làm trước generation

Nếu sinh trước nhưng chưa có validator, hệ thống sẽ lưu câu hỏi lỗi:

- Thiếu đáp án.
- Có nhiều đáp án đúng.
- Đáp án đúng không nằm trong choices.
- Đáp án nhiễu trùng nhau.
- Lỗi LaTeX hoặc thiếu formula payload.

Quality rules là hàng rào để mọi nguồn sinh, dù AI hay symbolic, đều phải đi qua cùng một chuẩn.

### Bước 2.1 - Thêm MCQ structural validation

Rule cần có:

```text
mcq_missing_choices
mcq_invalid_choice_count
mcq_invalid_choice_key
mcq_duplicate_choice_key
mcq_missing_correct_choice
mcq_correct_choice_not_found
mcq_multiple_correct_choices
mcq_no_correct_choice_flagged
mcq_empty_choice_text
```

Module:

```text
modules/question_quality/service.py
```

Lý do:

- Đây là kiểm tra hình thức cơ bản.
- Không phụ thuộc AI, solver, database.
- Dễ test và phải chạy rất nhanh.

Test bắt buộc:

```text
tests/modules/question_quality/test_mcq_structure.py
```

Test cần có:

- MCQ hợp lệ 4 lựa chọn pass.
- Chỉ có 3 lựa chọn bị warning hoặc error theo policy.
- Thiếu choices bị blocking.
- Hai lựa chọn cùng key bị blocking.
- Hai lựa chọn đúng bị blocking.
- `correct_choice = E` bị blocking.
- Choice text rỗng bị blocking.
- Free response không bị ép phải có choices.

Tiêu chí qua bước:

- Quality service phân biệt được tự luận và trắc nghiệm.
- MCQ lỗi cấu trúc bị chặn.
- Test pass.

### Bước 2.2 - Thêm duplicate validation cho đáp án nhiễu

Rule cần có:

```text
mcq_duplicate_choice_content
mcq_distractor_equals_correct_answer
mcq_all_choices_too_similar
```

Logic đề xuất:

- Normalize text: lower, strip, gộp whitespace.
- Normalize LaTeX: dùng `normalize_formula` hiện có nếu có.
- So sánh text và latex.
- Nếu có thể parse bằng SymPy thì so sánh symbolic.

Lý do:

- Trong trắc nghiệm, đáp án nhiễu trùng đáp án đúng là lỗi nghiêm trọng.
- Hai lựa chọn khác chữ nhưng cùng giá trị toán học cũng là lỗi.

Test bắt buộc:

```text
tests/modules/question_quality/test_mcq_distractors.py
```

Test cần có:

- Hai lựa chọn text giống nhau bị blocking.
- Hai lựa chọn LaTeX giống nhau bị blocking.
- `x+1` và `1+x` bị phát hiện trùng nếu symbolic parser xử lý được.
- Distractor bằng đáp án đúng bị blocking.
- Các distractor khác nhau pass.
- Parser lỗi thì không crash, chuyển thành warning nếu cần.

Tiêu chí qua bước:

- Không lưu được MCQ có đáp án nhiễu trùng.
- Test pass.

### Bước 2.3 - Tích hợp quality report vào generation preview/save

Việc cần làm:

1. Cập nhật `QuestionQualityService.assess_candidate`.
2. Trả về `warnings`, `blocking_issues`, `quality_warnings`.
3. Với save:
   - Nếu có blocking issue thì không lưu.
   - Nếu chỉ có warning thì cho lưu nhưng lưu report.

Lý do:

- Preview cần cho người dùng xem lỗi.
- Save phải là chốt chặn cuối.

Test bắt buộc:

```text
tests/modules/question_generation/test_service.py
tests/api/test_generation_quality_endpoint.py
tests/api/test_generation_save_endpoint.py
```

Test cần có:

- Preview MCQ trả quality_warnings.
- Save MCQ hợp lệ thành công.
- Save MCQ có duplicate choice fail 400.
- Save free response cũ vẫn hoạt động.
- Quality endpoint trả chi tiết field lỗi.

Tiêu chí qua bước:

- Quality report đi xuyên suốt preview -> quality endpoint -> save.
- Test pass toàn bộ.

## 8. Giai đoạn 3 - Chuyển generation sang sinh câu hỏi trắc nghiệm

### Mục tiêu

Mở rộng pipeline sinh câu hỏi hiện tại để sinh MCQ thay vì chỉ sinh `statement/solution/answer`.

### Vì sao làm sau quality rules

Generation là nguồn có độ bất định cao. Cần validator trước để chặn output sai của AI.

### Bước 3.1 - Cập nhật prompt builder sinh MCQ

File:

```text
modules/question_generation/prompt_builder.py
```

Prompt output schema mới:

```json
{
  "items": [
    {
      "question_type": "multiple_choice",
      "statement": "...",
      "choices": [
        {"key": "A", "text": "...", "latex": "...", "is_correct": false, "rationale": "..."},
        {"key": "B", "text": "...", "latex": "...", "is_correct": true, "rationale": null}
      ],
      "correct_choice": "B",
      "answer": "...",
      "solution": "...",
      "difficulty": "medium",
      "skills": [],
      "generation_method": "ai"
    }
  ]
}
```

Prompt phải yêu cầu:

- Luôn tạo 4 lựa chọn A/B/C/D.
- Chỉ một lựa chọn đúng.
- Đáp án nhiễu phải hợp lý, cùng dạng biểu thức.
- Không tạo lựa chọn "Tất cả đều đúng" hoặc "Không đáp án nào đúng" trong MVP.
- `correct_choice` phải khớp với choice có `is_correct = true`.
- Giữ style công thức LaTeX.
- Nếu có source question, tạo biến thể cùng taxonomy/difficulty nếu người dùng yêu cầu.

Lý do:

- Ép model trả JSON có cấu trúc.
- Giảm lỗi parse.
- Phù hợp UI và quality rules.

Test bắt buộc:

```text
tests/modules/question_generation/test_prompt_builder.py
```

Test cần có:

- Prompt chứa schema choices.
- Prompt yêu cầu exactly 4 choices.
- Prompt yêu cầu single correct answer.
- Prompt chứa source question.
- Prompt giữ taxonomy/difficulty.
- Prompt không mất backslash LaTeX.

Tiêu chí qua bước:

- Prompt deterministic.
- Test pass.

### Bước 3.2 - Parse output MCQ từ model

File:

```text
modules/question_generation/service.py
```

Việc cần làm:

1. Mở rộng `_parse_candidate`.
2. Parse `question_type`.
3. Parse `choices`.
4. Normalize key A/B/C/D.
5. Tự suy `correct_choice` nếu missing nhưng có đúng một `is_correct`.
6. Nếu `answer` thiếu, lấy text/latex của correct choice.
7. Extract formulas từ statement, solution, answer và choices.

Lý do:

- Output AI có thể thiếu một vài field.
- Parser nên giúp normalize lỗi nhẹ, còn lỗi nặng để quality service chặn.

Test bắt buộc:

```text
tests/modules/question_generation/test_service.py
```

Test cần có:

- Parse MCQ hợp lệ.
- Parse output markdown fenced JSON.
- Missing answer được lấy từ correct choice.
- Missing correct_choice nhưng có đúng một `is_correct` thì tự suy.
- Missing choices gây quality warning/blocking, không crash preview.
- Choices có formula được extract vào formulas.

Tiêu chí qua bước:

- Preview sinh được MCQ candidate.
- Output lỗi nhẹ vẫn trả về report.
- Test pass.

### Bước 3.3 - Save generated MCQ

Việc cần làm:

1. Cập nhật `save_generated_question`.
2. Lưu:

```text
question_type
choices
correct_choice
validation_report
generation_method
solver_code
distractor_metadata
```

3. Khi lưu xong, embedding document/question phải tính cả choices.

Lý do:

- Search MCQ cần tìm theo cả đề và đáp án.
- Lưu report giúp audit khi bảo vệ đồ án.

Test bắt buộc:

```text
tests/api/test_generation_save_endpoint.py
tests/modules/embeddings/test_text_builder.py
tests/modules/embeddings/test_service.py
```

Test cần có:

- Save MCQ lưu choices.
- Saved question có correct_choice.
- Embedding text chứa statement và choices.
- Save MCQ lỗi bị chặn.
- Save free response regression pass.

Tiêu chí qua bước:

- Có thể sinh, preview và lưu MCQ bằng AI.
- Embedding không bỏ sót choices.
- Test pass.

## 9. Giai đoạn 4 - Tích hợp lõi Neuro-symbolic từ MathBank-main

### Mục tiêu

Đưa solver, distractor và symbolic validation từ dự án cũ vào kiến trúc hiện tại.

### Vì sao không copy nguyên dự án cũ

Source cũ có database, model và service riêng. Nếu bê nguyên vào sẽ:

- Trùng kiến trúc với backend hiện tại.
- Khó test.
- Khó bảo trì.
- Dễ lệch schema.

Cách đúng là trích lõi thuật toán:

```text
solver definitions
solver execution
distractor strategies
symbolic comparison
quality validation rules
```

### Bước 4.1 - Tạo module neuro_symbolic

Module đề xuất:

```text
modules/neuro_symbolic/
  __init__.py
  schemas.py
  solver_registry.py
  solver_executor.py
  distractors.py
  symbolic_validator.py
  template_matcher.py
```

Lý do:

- Tách riêng logic symbolic với generation AI.
- Dễ test độc lập.
- Sau này có thể thêm nhiều solver.

Test bắt buộc:

```text
tests/modules/neuro_symbolic/test_solver_registry.py
tests/modules/neuro_symbolic/test_solver_executor.py
```

Test cần có:

- Registry list được solver.
- Lấy solver theo code.
- Solver không tồn tại trả lỗi rõ.
- Execute solver tích phân mẫu đúng kết quả.
- Execute solver đạo hàm mẫu đúng kết quả nếu được port.
- Solver exception không làm crash service tổng.

Tiêu chí qua bước:

- Module mới import được.
- Solver mẫu chạy được.
- Test pass.

### Bước 4.2 - Port solver mẫu từ MathBank-main

Nguồn:

```text
MathBank-main/backend/solvers.py
```

Solver nên port trước:

```text
INT_XN_EXP
INT_XN_LN
INT_RATIONAL
DET_2X2
DET_3X3
LIMIT_ZERO_ZERO
DERIV_COMPOSITE
```

Mỗi solver cần có:

```text
code
name
problem_type_code hoặc taxonomy_hint
param_schema
statement_template
solution_template
answer_expression
test_cases
```

Lý do:

- Đây là các dạng toán rõ ràng, dễ kiểm chứng bằng SymPy.
- Phù hợp demo tốt nghiệp.
- Không cần bao phủ toàn bộ Giải tích 1 ngay.

Test bắt buộc:

```text
tests/modules/neuro_symbolic/test_builtin_solvers.py
```

Test cần có:

- Mỗi solver có code duy nhất.
- Mỗi solver có param_schema.
- Mỗi solver chạy được ít nhất 2 test case.
- Kết quả symbolic simplify về 0 khi so với expected.
- LaTeX answer sinh được nếu cần.

Tiêu chí qua bước:

- Có bộ solver demo ổn định.
- Test pass.

### Bước 4.3 - Port DistractorService

Nguồn:

```text
MathBank-main/backend/services.py
```

Các strategy nên port:

```text
sign_error
coefficient_error
missing_bound
adjacent_param
random_variation
partial_result
swap_operands
```

Việc cần làm:

1. Tách logic sinh nhiễu khỏi model cũ.
2. Input:

```text
correct_answer
params
strategy list
count
solver_func optional
```

3. Output:

```text
DistractorCandidate(value, latex, text, error_type, rationale)
```

4. Dùng symbolic comparison để loại nhiễu trùng đáp án đúng.

Lý do:

- Đáp án nhiễu là điểm khác biệt quan trọng của hệ trắc nghiệm.
- Strategy dựa trên lỗi sai thường gặp giúp câu hỏi tốt hơn nhiễu ngẫu nhiên.

Test bắt buộc:

```text
tests/modules/neuro_symbolic/test_distractors.py
```

Test cần có:

- Sinh đủ 3 distractor khi có thể.
- Distractor không bằng correct answer.
- Distractor không trùng nhau.
- `sign_error` hoạt động với số và biểu thức.
- `coefficient_error` tạo khác đáp án đúng.
- Nếu strategy fail thì service bỏ qua và tiếp tục strategy khác.
- Không crash với answer dạng string.

Tiêu chí qua bước:

- Sinh được đáp án nhiễu symbolic.
- Test pass.

### Bước 4.4 - Symbolic validator cho MCQ

Module:

```text
modules/neuro_symbolic/symbolic_validator.py
```

Rule cần có:

```text
symbolic_correct_answer_verified
symbolic_correct_answer_mismatch
symbolic_distractor_equals_correct
symbolic_distractor_duplicate
symbolic_parse_failed
solver_not_available
```

Logic:

1. Nếu candidate có `solver_code` và `params`, chạy solver.
2. So sánh solver result với correct choice.
3. So sánh từng distractor với solver result.
4. So sánh distractor với nhau.
5. Trả về report.

Lý do:

- Đây là phần Neuro-symbolic cốt lõi.
- AI sinh ra sẽ được kiểm lại bằng symbolic rules.

Test bắt buộc:

```text
tests/modules/neuro_symbolic/test_symbolic_validator.py
```

Test cần có:

- Correct choice khớp solver pass.
- Correct choice sai bị blocking.
- Distractor bằng đáp án đúng bị blocking.
- Hai distractor symbolic-equivalent bị blocking.
- Không có solver_code thì trả warning `solver_not_available`, không crash.
- Parse lỗi trả warning hoặc blocking theo policy.

Tiêu chí qua bước:

- Validator phát hiện được lỗi toán học cơ bản.
- Test pass.

### Bước 4.5 - Tích hợp symbolic validator vào QuestionQualityService

Việc cần làm:

1. `QuestionQualityService.assess_candidate` gọi symbolic validator nếu candidate là MCQ.
2. Merge symbolic issues vào quality report.
3. Blocking issue nếu:

```text
correct answer mismatch
distractor equals correct
duplicate symbolic distractor
```

4. Warning nếu:

```text
solver not available
symbolic parse failed nhưng structural validation vẫn ổn
```

Lý do:

- Quality service là cổng chung trước khi lưu.
- Không nên để generation tự quyết câu nào đúng.

Test bắt buộc:

```text
tests/modules/question_quality/test_service.py
tests/modules/question_quality/test_mcq_symbolic_quality.py
tests/api/test_generation_quality_endpoint.py
```

Test cần có:

- Candidate có solver và đáp án đúng pass.
- Candidate có solver và đáp án sai fail.
- Candidate không solver chỉ warning.
- API quality trả symbolic issues.
- Save endpoint chặn candidate symbolic mismatch.

Tiêu chí qua bước:

- Neuro-symbolic validation chạy trong pipeline thật.
- Test pass.

## 10. Giai đoạn 5 - Sinh trắc nghiệm bằng solver/template

### Mục tiêu

Không chỉ dựa vào AI, hệ thống có thể sinh MCQ trực tiếp từ solver template.

### Vì sao cần giai đoạn này

Đây là phần thể hiện rõ hệ thống được phát triển từ đồ án cũ:

- Sinh tham số.
- Tính đáp án bằng SymPy.
- Sinh đáp án nhiễu theo lỗi sai.
- Tạo câu hỏi MCQ.
- Validate rồi lưu.

### Bước 5.1 - Template matcher hoặc selector

Module:

```text
modules/neuro_symbolic/template_matcher.py
```

Nhiệm vụ:

- Chọn solver/template phù hợp với taxonomy hoặc source question.
- MVP có thể chọn thủ công bằng `solver_code`.
- Bản tốt hơn tự map `problem_type_code -> solver_code`.

Mapping ví dụ:

```text
GT1_C2_01_T03_Integration_By_Parts -> INT_XN_EXP hoặc INT_XN_LN
GT1_C1_05_T02_Algebraic_Transformation_Limit -> LIMIT_ZERO_ZERO
```

Lý do:

- Không phải mọi câu hỏi đều có solver.
- Hệ thống cần biết khi nào dùng symbolic generation, khi nào dùng AI generation.

Test bắt buộc:

```text
tests/modules/neuro_symbolic/test_template_matcher.py
```

Test cần có:

- Map problem_type_code sang solver.
- Không có mapping trả None.
- Ưu tiên solver theo requested strategy nếu có.
- Mapping không chứa solver code không tồn tại.

Tiêu chí qua bước:

- Có cách chọn solver rõ ràng.
- Test pass.

### Bước 5.2 - Sinh tham số hợp lệ

Module:

```text
modules/neuro_symbolic/parameter_sampler.py
```

Nhiệm vụ:

- Đọc `param_schema`.
- Sinh tham số theo min/max/choice/exclude/default.
- Tránh tham số gây lỗi solver.
- Có seed để test deterministic.

Lý do:

- Solver cần input hợp lệ.
- Sinh tham số ngẫu nhiên nhưng phải test được.

Test bắt buộc:

```text
tests/modules/neuro_symbolic/test_parameter_sampler.py
```

Test cần có:

- Integer range đúng.
- Exclude hoạt động.
- Choice hoạt động.
- Default được dùng khi min=max hoặc schema yêu cầu.
- Seed tạo kết quả ổn định.
- Params sinh ra chạy solver không lỗi với solver mẫu.

Tiêu chí qua bước:

- Sinh được params hợp lệ.
- Test pass.

### Bước 5.3 - Symbolic MCQ generation service

Module:

```text
modules/question_generation/symbolic_mcq_generator.py
```

Input:

```text
solver_code
generation_count
difficulty
taxonomy metadata
```

Output:

```text
GeneratedQuestionCandidate question_type=multiple_choice
```

Workflow:

```text
sample params
-> execute solver
-> render statement
-> render correct answer
-> generate distractors
-> shuffle choices
-> build solution
-> run quality service
```

Lý do:

- Đây là pipeline sinh MCQ có kiểm chứng mạnh nhất.
- Dùng để demo rõ Neuro-symbolic AI.

Test bắt buộc:

```text
tests/modules/question_generation/test_symbolic_mcq_generator.py
```

Test cần có:

- Sinh được 1 MCQ từ solver.
- Sinh được nhiều MCQ không trùng params.
- Mỗi MCQ có 4 choices.
- Chỉ một correct choice.
- Đáp án đúng khớp solver.
- Distractors không trùng đáp án đúng.
- Quality report can_save true với candidate hợp lệ.

Tiêu chí qua bước:

- Có thể sinh MCQ không cần gọi AI.
- Test pass.

### Bước 5.4 - API endpoint sinh MCQ symbolic

Endpoint đề xuất:

```text
POST /generation/mcq/symbolic/preview
POST /generation/mcq/symbolic/save
GET /generation/mcq/solvers
```

Request preview:

```json
{
  "solver_code": "INT_XN_EXP",
  "generation_count": 3,
  "difficulty": "medium",
  "taxonomy": {
    "chapter_code": "...",
    "topic_code": "...",
    "problem_type_code": "..."
  }
}
```

Lý do:

- UI cần danh sách solver.
- Người dùng có thể sinh theo dạng bài.
- Tách endpoint symbolic khỏi endpoint biến thể AI hiện tại để dễ kiểm soát.

Test bắt buộc:

```text
tests/api/test_symbolic_mcq_generation_endpoint.py
```

Test cần có:

- GET solvers trả danh sách solver.
- Preview solver hợp lệ trả candidates.
- Preview solver không tồn tại trả 400.
- Save candidate hợp lệ lưu question.
- Save candidate lỗi quality trả 400.

Tiêu chí qua bước:

- Backend expose được symbolic MCQ generation.
- Test pass.

## 11. Giai đoạn 6 - Cập nhật ingestion và chuyển data sang trắc nghiệm

### Mục tiêu

Dữ liệu trong hệ thống dần trở thành ngân hàng câu hỏi trắc nghiệm.

### Vì sao làm sau khi schema và generation ổn định

Nếu chuyển data quá sớm, dữ liệu MCQ có thể thiếu field hoặc sai quality. Cần có:

- Schema.
- Validator.
- Save API.
- UI đọc được choices.

### Bước 6.1 - Chính sách dữ liệu câu hỏi

Quy định:

```text
question_type = free_response
```

cho câu hỏi ingest từ tài liệu chưa có choices.

```text
question_type = multiple_choice
```

cho câu hỏi:

- Đã có A/B/C/D trong tài liệu.
- Được sinh từ AI MCQ generation.
- Được sinh từ symbolic MCQ generator.
- Được convert từ tự luận sang MCQ.

Lý do:

- Không ép mọi dữ liệu cũ thành MCQ ngay.
- Tránh mất thông tin tự luận.
- Có thể dùng câu tự luận làm nguồn sinh MCQ.

Test bắt buộc:

```text
tests/modules/question_segmenter/test_segmenter.py
tests/modules/question_storage/test_service.py
```

Test cần có:

- Segment câu tự luận tạo free_response.
- Segment câu có A/B/C/D tạo multiple_choice nếu parser hỗ trợ.
- Store document không có MCQ vẫn pass.
- Store document có MCQ lưu choices.

Tiêu chí qua bước:

- Hệ thống phân biệt được dữ liệu cũ và mới.
- Test pass.

### Bước 6.2 - Parser nhận diện câu hỏi trắc nghiệm từ tài liệu

Module:

```text
modules/question_segmenter/mcq_parser.py
```

Dạng cần nhận:

```text
A. ...
B. ...
C. ...
D. ...
Đáp án: B
```

Hoặc:

```text
(A) ...
(B) ...
(C) ...
(D) ...
```

Nhiệm vụ:

- Tách statement.
- Tách choices.
- Nhận correct_choice nếu tài liệu có đáp án.
- Nếu không có đáp án, lưu choices nhưng `correct_choice = null`, đưa vào QA.

Lý do:

- Nếu data đầu vào sau này là đề trắc nghiệm, hệ thống phải ingest được trực tiếp.

Test bắt buộc:

```text
tests/modules/question_segmenter/test_mcq_parser.py
```

Test cần có:

- Parse A/B/C/D dạng dấu chấm.
- Parse A/B/C/D dạng ngoặc.
- Parse đáp án đúng.
- Không có đáp án thì không crash.
- Lựa chọn chứa LaTeX vẫn giữ nguyên.
- Text tự luận không bị nhận nhầm là MCQ.

Tiêu chí qua bước:

- Ingest được tài liệu trắc nghiệm cơ bản.
- Test pass.

### Bước 6.3 - Convert free response sang MCQ

Endpoint/service đề xuất:

```text
POST /generation/questions/{question_id}/convert-to-mcq/preview
POST /generation/questions/{question_id}/convert-to-mcq/save
```

Workflow:

```text
free_response question
-> AI tạo choices
-> nếu có solver phù hợp thì symbolic validate
-> quality report
-> save as new multiple_choice question
```

Lý do:

- Tận dụng corpus tự luận đã có.
- Chuyển đổi dần data sang MCQ.

Test bắt buộc:

```text
tests/api/test_convert_to_mcq_endpoint.py
tests/modules/question_generation/test_convert_to_mcq_service.py
```

Test cần có:

- Convert question tồn tại thành candidate MCQ.
- Question không tồn tại trả 404.
- Candidate MCQ có choices.
- Save tạo question mới, không ghi đè question gốc.
- Quality lỗi thì không lưu.

Tiêu chí qua bước:

- Data cũ có thể trở thành nguồn sinh MCQ.
- Test pass.

## 12. Giai đoạn 7 - Cập nhật semantic search, embedding và AI matching cho MCQ

### Mục tiêu

Search và matching phải hiểu câu hỏi trắc nghiệm.

### Bước 7.1 - Cập nhật text builder cho embedding

File:

```text
modules/embeddings/text_builder.py
```

Embedding text nên gồm:

```text
Question type
Statement
Choices A-D
Correct answer nếu được phép index
Solution
Taxonomy metadata
Skills
Difficulty
```

Lưu ý:

- Với search dành cho giáo viên/admin, có thể index đáp án đúng.
- Nếu sau này có chế độ học sinh, API cần ẩn đáp án đúng ở response phù hợp.

Lý do:

- Search theo nội dung đáp án hoặc nhiễu cũng hữu ích.
- Matching câu hỏi trắc nghiệm cần so sánh cả cấu trúc lựa chọn.

Test bắt buộc:

```text
tests/modules/embeddings/test_text_builder.py
tests/modules/embeddings/test_service.py
```

Test cần có:

- Embedding text MCQ chứa choices.
- Embedding text tự luận không đổi.
- Không crash nếu choices rỗng.
- Formula embedding lấy được công thức trong choices.

Tiêu chí qua bước:

- Embedding MCQ giàu thông tin hơn.
- Test pass.

### Bước 7.2 - Cập nhật search response và filter

Files:

```text
modules/semantic_search/service.py
apps/api/v1/models/search.py
apps/api/v1/endpoints/search.py
```

Việc cần làm:

- Search response trả `question_type`, `choices`, `correct_choice`.
- Filter thêm `question_type`.
- Cho phép tìm chỉ MCQ.

Lý do:

- Khi corpus có cả tự luận và trắc nghiệm, người dùng cần lọc.

Test bắt buộc:

```text
tests/modules/semantic_search/test_service.py
tests/api/test_search.py
```

Test cần có:

- Search trả MCQ fields.
- Filter `question_type=multiple_choice`.
- Search không filter vẫn trả cả hai loại.
- Formula search trên choices hoạt động nếu có formula.

Tiêu chí qua bước:

- Search hỗ trợ MCQ đầy đủ.
- Test pass.

### Bước 7.3 - Hybrid matching có tính MCQ

Cập nhật scoring:

```text
final_score =
  0.45 * semantic_score
  + 0.20 * taxonomy_score
  + 0.15 * formula_score
  + 0.10 * difficulty_score
  + 0.05 * skill_score
  + 0.05 * choice_structure_score
```

`choice_structure_score` xét:

- Cùng question_type.
- Cùng số lựa chọn.
- Cùng kiểu đáp án: số, biểu thức, mệnh đề, ma trận.

Lý do:

- Hai câu cùng đề bài nhưng một câu tự luận, một câu trắc nghiệm không hoàn toàn tương đương.
- MCQ có thêm cấu trúc đáp án cần được xét.

Test bắt buộc:

```text
tests/modules/semantic_search/test_hybrid_matching.py
```

Test cần có:

- Cùng question_type tăng score.
- MCQ với MCQ cao hơn MCQ với free_response nếu các yếu tố khác tương đương.
- Thiếu choices không crash.
- Final score vẫn trong [0, 1].

Tiêu chí qua bước:

- Hybrid matching nhận biết MCQ.
- Test pass.

## 13. Giai đoạn 8 - Cập nhật frontend hiển thị trắc nghiệm

### Mục tiêu

Người dùng nhìn thấy hệ thống là ngân hàng câu hỏi trắc nghiệm, không còn giao diện thiên về tự luận.

### Bước 8.1 - Cập nhật ProblemDetail

File:

```text
apps/frontend/src/pages/ProblemDetail.jsx
```

Hiển thị:

```text
Câu hỏi
A. ...
B. ...
C. ...
D. ...
Đáp án đúng
Lời giải
Taxonomy
Skills
Difficulty
Validation report
Similar questions
```

Lý do:

- Đây là trang xem chi tiết câu hỏi, cần phản ánh schema MCQ.

Test bắt buộc:

```text
cd apps/frontend
npm run lint
npm run build
```

Manual test:

- Mở câu tự luận cũ không lỗi.
- Mở câu MCQ thấy A/B/C/D.
- Đáp án đúng hiển thị rõ cho admin.
- Formula trong choices render đúng.

Tiêu chí qua bước:

- Detail page đọc được cả hai loại câu hỏi.
- Frontend build pass.

### Bước 8.2 - Cập nhật GenVariants thành sinh trắc nghiệm

File:

```text
apps/frontend/src/pages/GenVariants.jsx
```

Thay đổi UI:

- Đổi trọng tâm từ "Sinh biến thể" sang "Sinh trắc nghiệm".
- Card candidate hiển thị:

```text
Statement
A/B/C/D
Correct choice
QA score
Validation status
Warnings/blocking issues
Solver code nếu có
Generation method: AI / Symbolic / AI + Symbolic
```

Thêm mode:

```text
AI MCQ
Symbolic MCQ
Convert from source
```

Lý do:

- Đây là màn hình demo quan trọng nhất cho đồ án.
- Cần thể hiện rõ Neuro-symbolic validation.

Test bắt buộc:

```text
cd apps/frontend
npm run lint
npm run build
```

Manual test:

- Sinh MCQ từ câu nguồn.
- Candidate có choices hiển thị đúng.
- Candidate lỗi quality hiển thị lỗi.
- Không cho lưu candidate có blocking issue.
- Save thành công hiển thị question_id.

Tiêu chí qua bước:

- UI demo được pipeline sinh MCQ.
- Build pass.

### Bước 8.3 - Cập nhật Semantic Search

File:

```text
apps/frontend/src/pages/SemanticSearch.jsx
```

Hiển thị search result:

- Badge `Trắc nghiệm` hoặc `Tự luận`.
- Preview choices nếu là MCQ.
- Filter `Loại câu hỏi`.

Lý do:

- Khi corpus hỗn hợp, search phải giúp người dùng lọc đúng loại.

Test bắt buộc:

```text
cd apps/frontend
npm run lint
npm run build
```

Manual test:

- Search MCQ.
- Filter chỉ MCQ.
- Mở detail từ result.
- Formula trong choices không vỡ layout.

Tiêu chí qua bước:

- Search UI hỗ trợ MCQ.
- Build pass.

### Bước 8.4 - Cập nhật QA Rules

File:

```text
apps/frontend/src/pages/QARules.jsx
```

Nội dung cần hiển thị:

```text
Structural rules
Distractor rules
Symbolic rules
Taxonomy rules
Semantic duplicate rules
Save policy
```

Ví dụ:

```text
MCQ phải có 4 lựa chọn.
Chỉ một lựa chọn đúng.
Đáp án nhiễu không được trùng đáp án đúng.
Nếu có solver, đáp án đúng phải khớp kết quả symbolic.
Taxonomy code phải hợp lệ.
```

Lý do:

- Trang này giúp bảo vệ đồ án: giải thích rõ hệ kiểm định.

Test bắt buộc:

```text
cd apps/frontend
npm run lint
npm run build
```

Manual test:

- Các rule hiển thị rõ.
- Không có text tràn layout.
- Trạng thái rule tương ứng với backend quality codes.

Tiêu chí qua bước:

- QA page thể hiện được Neuro-symbolic validation.
- Build pass.

### Bước 8.5 - Cập nhật Dashboard và Analytics

Files:

```text
apps/frontend/src/pages/Dashboard.jsx
apps/frontend/src/pages/Analytics.jsx
apps/api/v1/endpoints/analytics.py
```

Thống kê cần có:

```text
Tổng số câu hỏi
Số câu trắc nghiệm
Số câu tự luận
Số câu MCQ đã kiểm định
Số câu MCQ có lỗi blocking
Số câu có symbolic validation
Phân bố theo chapter/topic/difficulty
Tỷ lệ distractor lỗi
Tỷ lệ câu sinh bằng AI/Symbolic
```

Lý do:

- Dashboard phải phản ánh hướng đồ án mới.
- Analytics là phần chứng minh hệ thống hoạt động trên dữ liệu thật.

Test bắt buộc:

```text
tests/api/test_analytics.py
cd apps/frontend
npm run lint
npm run build
```

Manual test:

- Dashboard hiển thị số MCQ.
- Analytics có phân bố question_type.
- Không hỏng nếu chưa có MCQ nào.

Tiêu chí qua bước:

- Giao diện tổng quan thể hiện hệ thống trắc nghiệm.
- Test/build pass.

## 14. Giai đoạn 9 - Review workflow và quyền hiển thị đáp án

### Mục tiêu

Tách rõ câu hỏi đang ở trạng thái draft, cần duyệt, đạt kiểm định hoặc bị lỗi.

### Bước 9.1 - Chuẩn hóa review_status cho MCQ

Trạng thái đề xuất:

```text
draft
generated
validated
needs_review
approved
rejected
```

Policy:

- `validated`: không có blocking issue.
- `needs_review`: có warning hoặc confidence thấp.
- `rejected`: có blocking issue nếu người dùng từ chối sửa.
- `approved`: giảng viên/admin duyệt.

Lý do:

- Không phải câu nào can_save cũng nên auto approve.
- Đồ án cần workflow quản lý ngân hàng câu hỏi.

Test bắt buộc:

```text
tests/modules/question_storage/test_service.py
tests/api/test_questions.py
```

Test cần có:

- Save generated MCQ hợp lệ có review_status đúng.
- Candidate có warning vào needs_review.
- Approve chuyển approved.
- Reject chuyển rejected.
- Question cũ không có review_status vẫn đọc được.

Tiêu chí qua bước:

- Có workflow duyệt câu hỏi rõ ràng.
- Test pass.

### Bước 9.2 - Chính sách ẩn/hiện đáp án

Đối tượng:

```text
admin/teacher: xem correct_choice và solution
student/demo practice: có thể ẩn đáp án
```

MVP:

- Chưa cần auth đầy đủ.
- Nhưng API/UI nên có khả năng không hiển thị đáp án ở một số view nếu cần.

Lý do:

- Ngân hàng câu hỏi trắc nghiệm thường cần bảo mật đáp án.
- Đồ án có thể nói đã thiết kế sẵn policy.

Test bắt buộc:

```text
tests/api/test_questions.py
```

Test cần có:

- Admin response có correct_choice.
- Public/practice response nếu triển khai không trả correct_choice.
- Search result có thể ẩn đáp án theo flag.

Tiêu chí qua bước:

- Có định hướng bảo mật đáp án.
- Test pass nếu có endpoint public.

## 15. Giai đoạn 10 - Evaluation dataset và báo cáo chất lượng

### Mục tiêu

Chứng minh hệ thống MCQ hoạt động bằng số liệu, không chỉ demo cảm tính.

### Bước 10.1 - Tạo bộ dữ liệu đánh giá MCQ

File đề xuất:

```text
tests/fixtures/calculus_1_mcq_eval.json
```

Mỗi mẫu:

```json
{
  "id": "mcq_eval_001",
  "statement": "...",
  "choices": [],
  "correct_choice": "B",
  "expected_answer": "...",
  "expected_problem_type_code": "...",
  "expected_difficulty": "medium",
  "solver_code": "INT_XN_EXP",
  "params": {}
}
```

Nhóm dữ liệu:

```text
20 câu generated symbolic
20 câu AI generated
20 câu convert từ tự luận
20 câu ingest từ tài liệu trắc nghiệm nếu có
```

Lý do:

- Có dataset giúp đo quality pipeline.
- Dễ viết phần thực nghiệm trong báo cáo.

Test bắt buộc:

```text
tests/modules/question_quality/test_mcq_eval_fixture.py
```

Test cần có:

- Fixture load được.
- Mỗi mẫu có statement.
- MCQ mẫu có 4 choices nếu đã hoàn chỉnh.
- correct_choice nằm trong choices.
- solver_code nếu có phải tồn tại.

Tiêu chí qua bước:

- Có dataset đánh giá.
- Test fixture pass.

### Bước 10.2 - Script đánh giá MCQ quality

Script:

```text
scripts/evaluate_mcq_quality.py
```

Chỉ số:

```text
valid_structure_rate
single_correct_rate
distractor_distinct_rate
symbolic_correct_rate
taxonomy_valid_rate
semantic_duplicate_rate
can_save_rate
warning_rate
blocking_issue_rate
```

Lý do:

- Đây là phần định lượng cho báo cáo tốt nghiệp.
- Cho thấy Neuro-symbolic validation có tác dụng.

Test bắt buộc:

```text
tests/modules/question_quality/test_mcq_evaluator.py
```

Test cần có:

- Tính valid_structure_rate đúng.
- Tính symbolic_correct_rate đúng.
- Tính blocking_issue_rate đúng.
- Dataset rỗng không crash.
- Report có đầy đủ key.

Tiêu chí qua bước:

- Chạy được evaluator.
- Có report số liệu.
- Test pass.

### Bước 10.3 - Dashboard analytics cho quality

Backend:

```text
apps/api/v1/endpoints/analytics.py
```

Frontend:

```text
apps/frontend/src/pages/Analytics.jsx
```

Hiển thị:

```text
Tỷ lệ MCQ hợp lệ
Tỷ lệ lỗi đáp án đúng
Tỷ lệ lỗi distractor
Tỷ lệ solver unavailable
Tỷ lệ câu cần review
Phân bố theo generation_method
```

Lý do:

- Thể hiện hệ thống không chỉ sinh mà còn đo được chất lượng.

Test bắt buộc:

```text
tests/api/test_analytics.py
cd apps/frontend
npm run lint
npm run build
```

Tiêu chí qua bước:

- Analytics phản ánh quality MCQ.
- Test/build pass.

## 16. Thứ tự triển khai khuyến nghị

Không nên làm frontend trước khi backend schema ổn định. Thứ tự nên là:

```text
1. Schema dataclass/API cho MCQ
2. Database fields + migration
3. Repository/API response
4. Quality structural rules
5. Quality distractor duplicate rules
6. Generation prompt/parser MCQ
7. Save MCQ + embedding choices
8. Module neuro_symbolic
9. Port solvers
10. Port distractors
11. Symbolic validator
12. Tích hợp symbolic validator vào quality service
13. Symbolic MCQ generator
14. API symbolic generation
15. MCQ parser từ tài liệu
16. Convert free response sang MCQ
17. Search/embedding/hybrid matching cho MCQ
18. Frontend ProblemDetail
19. Frontend GenVariants
20. Frontend Search/QA/Dashboard/Analytics
21. Review workflow
22. Evaluation dataset + evaluator
```

## 17. Definition of Done toàn hệ thống

Hệ thống được xem là hoàn thành cập nhật trắc nghiệm khi:

- Database lưu được `multiple_choice` và `free_response`.
- API trả được choices và correct_choice.
- Search lọc được theo `question_type`.
- Generation preview sinh được MCQ.
- Save chặn MCQ lỗi bằng quality rules.
- Symbolic solver chạy được ít nhất vài dạng toán demo.
- Distractor generator sinh được đáp án nhiễu hợp lệ.
- Symbolic validator kiểm tra được đáp án đúng.
- GenVariants hiển thị A/B/C/D và validation report.
- ProblemDetail hiển thị đầy đủ câu trắc nghiệm.
- QA Rules giải thích được structural, distractor và symbolic rules.
- Dashboard/Analytics có thống kê MCQ.
- Có evaluation dataset và script đánh giá.
- Toàn bộ backend test pass.
- Frontend lint/build pass.

## 18. Kịch bản demo bảo vệ

Kịch bản 1 - Upload và phân loại:

```text
1. Upload tài liệu bài tập Giải tích 1.
2. Hệ thống ingestion và segment câu hỏi.
3. Hệ thống classify vào taxonomy.
4. Search theo topic/difficulty.
```

Kịch bản 2 - Convert tự luận sang trắc nghiệm:

```text
1. Chọn một câu tự luận đã ingest.
2. Bấm chuyển sang trắc nghiệm.
3. AI sinh A/B/C/D.
4. Quality service kiểm tra structural rules.
5. Nếu có solver, symbolic validator kiểm tra đáp án.
6. Lưu câu hỏi vào ngân hàng.
```

Kịch bản 3 - Sinh bằng Neuro-symbolic:

```text
1. Chọn dạng bài: tích phân từng phần.
2. Chọn solver INT_XN_EXP.
3. Hệ thống sinh tham số.
4. Solver SymPy tính đáp án đúng.
5. Distractor generator tạo 3 đáp án nhiễu.
6. Symbolic validator kiểm tra lại.
7. UI hiển thị câu hỏi, A/B/C/D, đáp án đúng và validation report.
8. Lưu vào question bank.
```

Kịch bản 4 - Search và analytics:

```text
1. Search câu hỏi cùng topic.
2. Filter chỉ trắc nghiệm.
3. Mở Analytics xem tỷ lệ câu đã kiểm định.
4. Mở QA Rules xem các rule kiểm định.
```

## 19. Rủi ro và kiểm soát

### Rủi ro 1 - Migration làm hỏng dữ liệu cũ

Kiểm soát:

- Field mới có default.
- Không xóa field cũ.
- Test migration với database có dữ liệu.
- Backup trước khi chạy migration thật.

### Rủi ro 2 - AI sinh MCQ sai cấu trúc

Kiểm soát:

- Prompt schema chặt.
- Parser normalize lỗi nhẹ.
- Quality structural rules chặn lỗi nặng.
- Không save nếu có blocking issue.

### Rủi ro 3 - Đáp án nhiễu trùng đáp án đúng

Kiểm soát:

- Normalize text/latex.
- Symbolic comparison bằng SymPy khi có thể.
- Blocking issue trước khi save.

### Rủi ro 4 - Không phải dạng nào cũng có solver

Kiểm soát:

- `solver_not_available` là warning, không crash.
- Chỉ symbolic validate khi có solver.
- AI generation vẫn dùng được cho dạng chưa có solver.
- Báo cáo rõ phạm vi solver demo.

### Rủi ro 5 - UI phức tạp hơn

Kiểm soát:

- Giữ tương thích free_response.
- Component hiển thị choices riêng.
- Build/lint sau mỗi thay đổi.
- Không đổi toàn bộ giao diện trong một bước.

### Rủi ro 6 - Search lộ đáp án đúng

Kiểm soát:

- Có policy view admin/public.
- API có thể thêm flag ẩn đáp án.
- MVP dùng admin view cho đồ án.

## 20. Kết luận

Cập nhật trắc nghiệm không phải là đổi đề tài hoàn toàn. Đây là hướng phát triển tự nhiên từ đồ án cũ:

```text
Đồ án 2:
Sinh ngân hàng câu hỏi trắc nghiệm bằng AI + symbolic checking.

Đồ án tốt nghiệp:
Hệ thống ngân hàng câu hỏi trắc nghiệm hoàn chỉnh,
có ingestion, taxonomy, semantic search, AI matching,
generation và Neuro-symbolic Validation.
```

Điểm mạnh khi trình bày:

- Hệ thống không chỉ gọi AI để sinh câu hỏi.
- Có taxonomy để tổ chức tri thức.
- Có semantic/formula search để khai thác ngân hàng câu hỏi.
- Có solver symbolic và rule-based validator để kiểm chứng.
- Có quality report và evaluation metrics để đánh giá.

Nguyên tắc xuyên suốt:

> Mỗi bước triển khai phải có test. Chỉ chuyển bước khi test hiện tại và regression test đều pass.
