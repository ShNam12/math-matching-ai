# Bước 4 - Bộ não tri thức chính thức cho Giải tích 1

Tài liệu này tổng hợp từ:

- `Plan/update/buoc1_cay_kien_thuc_de_cuong.md`
- `Plan/update/buoc2_doi_chieu_giao_trinh_slide.md`
- `Plan/update/buoc3_trich_dang_bai_tu_bai_tap.md`

Mục tiêu:

- Xây dựng bộ não tri thức chính thức cho môn **Giải tích 1**.
- Làm nguồn chuẩn để AI Matching phân loại câu hỏi vào cây kiến thức.
- Dùng làm cơ sở cho backend classifier, giao diện Taxonomy, Semantic Search, QA và thống kê.

## 1. Phạm vi bộ não tri thức

Thông tin môn học:

- Môn học: Giải tích 1
- Đối tượng: Sinh viên ngành Toán Tin, Đại học Bách Khoa Hà Nội
- Nguồn tri thức chính: đề cương, giáo trình, slide bài giảng, bộ bài tập MI1111
- Độ sâu phân loại: chương + chủ đề + dạng bài

Cấu trúc chính thức:

```text
Giải tích 1
├── Chương 1: Phép tính vi phân hàm một biến số
├── Chương 2: Phép tính tích phân hàm một biến số
└── Chương 3: Hàm số nhiều biến số
```

Không đưa các phần sau làm nhánh chính nếu không xuất hiện trong đề cương Giải tích 1:

- Chuỗi số
- Chuỗi hàm
- Chuỗi Fourier
- Tích phân bội nhiều lớp
- Phương trình vi phân

## 2. Quy ước taxonomy

### 2.1. Mã và tên hiển thị

Quy ước đã chốt:

- Mã taxonomy dùng tiếng Anh, không dấu, ổn định cho backend.
- Tên hiển thị dùng tiếng Việt, đúng theo đề cương/giáo trình/slide.

Ví dụ:

```json
{
  "chapter": "GT1_C2_Integral_Calculus_One_Variable",
  "chapter_name": "Chương 2: Phép tính tích phân hàm một biến số",
  "topic": "GT1_C2_03_Improper_Integrals",
  "topic_name": "Tích phân suy rộng",
  "subtopic": "GT1_C2_03_T08_Parameter_Improper_Integral",
  "subtopic_name": "Tích phân suy rộng có tham số"
}
```

### 2.2. Cấp phân loại

Mỗi câu hỏi nên được phân loại theo 3 cấp:

```text
chapter -> topic -> subtopic
```

Trong đó:

- `chapter`: chương lớn trong đề cương.
- `topic`: chủ đề/mục học trong chương.
- `subtopic`: dạng bài cụ thể xuất hiện trong bài tập, slide hoặc giáo trình.

### 2.3. Nguyên tắc chọn nhãn

Nếu một câu hỏi có thể thuộc nhiều mục:

1. Chọn topic theo **phương pháp giải chính**.
2. Nếu đề bài nêu rõ phương pháp, ưu tiên phương pháp được nêu.
3. Nếu câu hỏi kết hợp nhiều kiến thức, chọn topic ở nơi đóng vai trò quyết định kết quả.
4. Nếu câu hỏi là bài chứng minh/biện luận, ưu tiên topic chứa định lý hoặc kỹ thuật chứng minh chính.
5. Có thể lưu thêm `secondary_topics` ở các phiên bản sau, nhưng bản MVP chỉ cần nhãn chính.

Ví dụ:

- Câu hỏi tính giới hạn bằng L'Hospital nên vào `GT1_C1_09_T05_LHopital_Rule`, không chỉ vào giới hạn hàm số.
- Câu hỏi tìm tham số để hàm liên tục nên vào `GT1_C1_07_T04_Find_Parameter_For_Continuity`.
- Câu hỏi tích phân bất định nêu "theo phương pháp từng phần" nên vào `GT1_C2_01_T03_Integration_By_Parts`.

## 3. Output schema cho AI Matching

AI classifier phải trả về JSON hợp lệ theo schema:

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
  "reason": "Đề bài yêu cầu tính giới hạn hàm số và cần biến đổi biểu thức trước khi thay giới hạn."
}
```

Yêu cầu:

- `subject` luôn là `Calculus 1`.
- `chapter`, `topic`, `subtopic` phải lấy từ taxonomy trong tài liệu này.
- `skills` chỉ dùng tên trong skill vocabulary.
- `difficulty` chỉ nhận `easy`, `medium`, `hard`.
- `confidence` trong khoảng 0 đến 1.
- `reason` giải thích ngắn gọn vì sao chọn nhãn đó.

## 4. Rubric độ khó

### 4.1. easy

Gán `easy` nếu câu hỏi:

- Áp dụng trực tiếp công thức.
- Ít hoặc không cần chọn phương pháp.
- Không cần chia trường hợp.
- Không có tham số cần biện luận.
- Thường chỉ cần 1-2 bước tính toán.

Ví dụ:

- Tìm tập xác định hàm số cơ bản.
- Tính đạo hàm trực tiếp.
- Tính vi phân trực tiếp.
- Tính nguyên hàm cơ bản.
- Tính đạo hàm riêng cấp một đơn giản.

### 4.2. medium

Gán `medium` nếu câu hỏi:

- Cần chọn phương pháp phù hợp.
- Cần biến đổi vài bước.
- Có thể kết hợp 2 kỹ thuật trong cùng một chủ đề.
- Có hàm hợp, hàm ẩn, hàm từng phần hoặc biểu thức phức tạp vừa phải.

Ví dụ:

- Tính giới hạn bằng biến đổi đại số.
- Dùng vô cùng bé tương đương.
- Xét liên tục hàm từng phần.
- Tính đạo hàm hàm hợp.
- Tính tích phân đổi biến hoặc từng phần.
- Tính đạo hàm hàm ẩn.
- Tìm cực trị tự do của hàm nhiều biến.

### 4.3. hard

Gán `hard` nếu câu hỏi:

- Cần biện luận.
- Cần chia trường hợp.
- Có tham số.
- Có chứng minh.
- Kết hợp nhiều kiến thức.
- Cần dựng ví dụ hoặc phản ví dụ.
- Cần phân tích điều kiện cần và đủ.

Ví dụ:

- Chứng minh bằng định lý Rolle/Lagrange/Cauchy.
- Tìm tham số để liên tục/khả vi/giới hạn hữu hạn.
- Chứng minh bất đẳng thức.
- Khai triển Taylor/Maclaurin có yêu cầu cao.
- Công thức truy hồi tích phân.
- Tích phân suy rộng có tham số.
- Kiểm tra định lý Schwarz hoặc đạo hàm hỗn hợp không liên tục.
- Cực trị có điều kiện.
- Tìm giá trị lớn nhất, nhỏ nhất trên miền đóng có biên.

## 5. Skill vocabulary

Danh sách skill chuẩn:

```text
function_domain_range
piecewise_function_modeling
function_composition
inverse_function
periodicity
elementary_functions
inverse_trigonometric_functions
hyperbolic_functions
sequence_limit
squeeze_theorem
monotone_bounded_sequence
cauchy_criterion
function_limit
one_sided_limit
limit_at_infinity
infinite_limit
algebraic_transformation
piecewise_function_limit
infinitesimal_equivalent
infinite_comparison
asymptotic_comparison
continuity_analysis
piecewise_function
discontinuity_classification
parameter_analysis
intermediate_value_theorem
counterexample_construction
derivative_computation
one_sided_derivative
differentiability_analysis
chain_rule
inverse_function_derivative
differential
linear_approximation
higher_order_derivative
nth_derivative
higher_order_differential
rolle_theorem
lagrange_mean_value_theorem
cauchy_mean_value_theorem
taylor_maclaurin_expansion
l_hopital_rule
monotonicity_analysis
convexity_concavity
one_variable_extrema
max_min_closed_interval
newton_method
asymptote_analysis
parametric_curve
polar_curve
indefinite_integral
substitution_method
integration_by_parts
rational_function_integral
partial_fraction_decomposition
trigonometric_integral
irrational_integral
euler_substitution
reduction_formula
definite_integral
riemann_sum
newton_leibniz_formula
differentiation_under_integral_limit
limit_as_integral
integral_symmetry
integral_inequality
improper_integral_convergence
comparison_test
absolute_convergence
conditional_convergence
area_by_integral
volume_by_integral
volume_of_revolution
arc_length
surface_area_of_revolution
multivariable_domain
multivariable_function_composition
multivariable_limit
path_limit_counterexample
iterated_limit
multivariable_continuity
partial_derivative
total_differential
multivariable_approximation
multivariable_chain_rule
implicit_function_derivative
higher_order_partial_derivative
second_order_differential
schwarz_theorem
partial_differential_equation_verification
multivariable_taylor_expansion
critical_point
hessian_extrema_test
unconstrained_extrema
constrained_extrema
lagrange_multiplier
global_maximum_minimum
proof
application
case_analysis
```

## 6. Cây tri thức chính thức

## GT1_C1_Differential_Calculus_One_Variable

Tên hiển thị:

```text
Chương 1: Phép tính vi phân hàm một biến số
```

Mô tả:

Chương này bao gồm hàm số một biến, dãy số, giới hạn, vô cùng bé/vô cùng lớn, liên tục, đạo hàm, vi phân, các định lý hàm khả vi và ứng dụng khảo sát hàm số.

### GT1_C1_02_Function_Basics

Tên hiển thị:

```text
Hàm số và các khái niệm cơ bản
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C1_02_T01_Domain_And_Range` | Tìm tập xác định, tập giá trị | "tìm tập xác định", "miền giá trị", hàm chứa căn, log, lượng giác ngược | `function_domain_range`, `algebraic_transformation` | `easy` |
| `GT1_C1_02_T02_Monotonicity_Boundedness_Parity` | Xét tính chất cơ bản của hàm số | "chẵn lẻ", "đơn điệu", "bị chặn" | `algebraic_transformation` | `easy` |
| `GT1_C1_02_T03_Function_Composition` | Hàm hợp | "tính f(g(x))", "hàm hợp", "f(h(x))=g(x)" | `function_composition` | `easy` |
| `GT1_C1_02_T04_Inverse_Function` | Hàm ngược | "tìm hàm ngược", "hàm số ngược" | `inverse_function` | `medium` |
| `GT1_C1_02_T05_Piecewise_Function_Modeling` | Mô hình hóa hàm từng khúc | "viết hàm số", bảng bậc thang, theo khoảng | `piecewise_function_modeling`, `application` | `medium` |
| `GT1_C1_02_T06_Periodicity` | Tính tuần hoàn và chu kỳ | "xét tính tuần hoàn", "tìm chu kỳ" | `periodicity` | `medium` |

Ví dụ từ bài tập:

- Bài 1: tìm tập xác định.
- Bài 4: lập hàm giá tiền điện theo bậc.
- Bài 6: tính hàm hợp.
- Bài 7: tìm hàm ngược.

### GT1_C1_03_Elementary_Functions

Tên hiển thị:

```text
Các hàm số sơ cấp
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C1_03_T01_Identify_Elementary_Function` | Nhận diện hàm sơ cấp | "hàm sơ cấp", các hàm cơ bản | `elementary_functions` | `easy` |
| `GT1_C1_03_T02_Inverse_Trigonometric_Function` | Hàm lượng giác ngược | `arcsin`, `arccos`, `arctan`, `arccot` | `inverse_trigonometric_functions` | `medium` |
| `GT1_C1_03_T03_Hyperbolic_Function` | Hàm hyperbolic | `sinh`, `cosh`, `tanh`, chứng minh đẳng thức hyperbolic | `hyperbolic_functions`, `proof` | `medium` |

Ví dụ từ bài tập:

- Bài 2: chứng minh đẳng thức hyperbolic.

### GT1_C1_04_Sequences

Tên hiển thị:

```text
Dãy số
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C1_04_T01_Compute_Sequence_Limit` | Tính giới hạn dãy số | `u_n`, `n -> infinity`, "xét sự hội tụ" | `sequence_limit` | `medium` |
| `GT1_C1_04_T02_Squeeze_Theorem_Sequence` | Tiêu chuẩn kẹp cho dãy | "kẹp", đánh giá trên dưới | `squeeze_theorem`, `proof` | `medium` |
| `GT1_C1_04_T03_Monotone_Bounded_Sequence` | Dãy đơn điệu bị chặn | "đơn điệu", "bị chặn" | `monotone_bounded_sequence`, `proof` | `hard` |
| `GT1_C1_04_T04_Cauchy_Criterion_Sequence` | Tiêu chuẩn Cauchy | "Cauchy", chứng minh hội tụ | `cauchy_criterion`, `proof` | `hard` |
| `GT1_C1_04_T05_Recursive_Sequence` | Dãy truy hồi | `u_{n+1}`, truy hồi | `sequence_limit`, `case_analysis` | `hard` |

Ví dụ từ bài tập:

- Bài 9: xét hội tụ và tìm giới hạn dãy số.

### GT1_C1_05_Function_Limits

Tên hiển thị:

```text
Giới hạn hàm số
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C1_05_T01_Direct_Limit` | Tính giới hạn trực tiếp | thay trực tiếp, hàm liên tục đơn giản | `function_limit` | `easy` |
| `GT1_C1_05_T02_Algebraic_Transformation_Limit` | Tính giới hạn bằng biến đổi đại số | căn thức, phân thức, hữu tỉ hóa, rút gọn | `function_limit`, `algebraic_transformation` | `medium` |
| `GT1_C1_05_T03_One_Sided_Limit` | Giới hạn một phía | `x -> a+`, `x -> a-`, hàm từng phần | `one_sided_limit` | `medium` |
| `GT1_C1_05_T04_Limit_At_Infinity` | Giới hạn tại vô cực | `x -> +infinity`, `x -> -infinity` | `limit_at_infinity` | `medium` |
| `GT1_C1_05_T05_Infinite_Limit` | Giới hạn vô cực | kết quả `infinity`, tiệm cận đứng | `infinite_limit` | `medium` |
| `GT1_C1_05_T06_Composite_Function_Limit` | Giới hạn hàm hợp | hàm lồng nhau | `function_limit`, `function_composition` | `medium` |
| `GT1_C1_05_T07_Proof_By_Definition` | Chứng minh giới hạn bằng định nghĩa | "bằng định nghĩa" | `function_limit`, `proof` | `hard` |
| `GT1_C1_05_T08_Piecewise_Function_Limit` | Giới hạn của hàm từng phần | `cases`, xét hai phía | `piecewise_function_limit`, `one_sided_limit` | `medium` |

Ví dụ từ bài tập:

- Bài 10: tính giới hạn bằng định nghĩa.
- Bài 11: tính các giới hạn.
- Bài 12: giới hạn của hàm từng phần.

### GT1_C1_06_Infinitesimal_Infinite

Tên hiển thị:

```text
Vô cùng bé, vô cùng lớn
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C1_06_T01_Compare_Infinitesimal` | So sánh vô cùng bé | "so sánh các cặp VCB", bậc VCB | `infinitesimal_equivalent`, `asymptotic_comparison` | `medium` |
| `GT1_C1_06_T02_Equivalent_Infinitesimal` | Dùng VCB tương đương | `sin x`, `ln(1+x)`, `e^x-1`, `x -> 0` | `infinitesimal_equivalent`, `function_limit` | `medium` |
| `GT1_C1_06_T03_Compare_Infinite` | So sánh vô cùng lớn | "VCL", `x -> infinity` | `infinite_comparison` | `medium` |
| `GT1_C1_06_T04_Asymptotic_Simplification` | Ngắt bỏ VCB/VCL | bỏ hạng bậc thấp/cao | `asymptotic_comparison`, `algebraic_transformation` | `medium` |

Ví dụ từ bài tập:

- Bài 13: so sánh các cặp VCB.
- Bài 14: tìm giới hạn bằng VCB/VCL.

### GT1_C1_07_Continuity

Tên hiển thị:

```text
Hàm số liên tục
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C1_07_T01_Continuity_At_Point` | Xét liên tục tại điểm | "liên tục tại" | `continuity_analysis` | `medium` |
| `GT1_C1_07_T02_Continuity_On_Set` | Xét liên tục trên khoảng/đoạn | "liên tục trên" | `continuity_analysis` | `medium` |
| `GT1_C1_07_T03_Piecewise_Continuity` | Liên tục của hàm từng phần | `cases`, nhiều nhánh | `piecewise_function`, `continuity_analysis` | `medium` |
| `GT1_C1_07_T04_Find_Parameter_For_Continuity` | Tìm tham số để liên tục | "tìm a", "tìm tham số để liên tục" | `parameter_analysis`, `continuity_analysis` | `hard` |
| `GT1_C1_07_T05_Classify_Discontinuity` | Phân loại điểm gián đoạn | "phân loại điểm gián đoạn" | `discontinuity_classification` | `medium` |
| `GT1_C1_07_T06_Use_Continuity_Theorems` | Dùng định lý hàm liên tục | chứng minh nghiệm, giao điểm | `intermediate_value_theorem`, `proof` | `hard` |
| `GT1_C1_07_T07_Parameter_For_Discontinuity_Type` | Tham số theo loại gián đoạn | tìm tham số để gián đoạn loại 1/2 | `parameter_analysis`, `discontinuity_classification` | `hard` |
| `GT1_C1_07_T08_Construct_Continuity_Counterexample` | Dựng ví dụ/phản ví dụ liên tục | "tìm một hàm", "ví dụ", "phản ví dụ" | `counterexample_construction` | `hard` |

Ví dụ từ bài tập:

- Bài 16: tìm tham số để liên tục.
- Bài 18: phân loại điểm gián đoạn.
- Bài 20, 23: dùng định lý giá trị trung gian.

### GT1_C1_08_Derivatives_Differentials

Tên hiển thị:

```text
Đạo hàm và vi phân
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C1_08_T01_Basic_Derivative` | Tính đạo hàm cơ bản | "tìm đạo hàm", `f'(x)` | `derivative_computation` | `easy` |
| `GT1_C1_08_T02_One_Sided_Derivative` | Đạo hàm một phía | `f'_+(a)`, `f'_-(a)`, một phía | `one_sided_derivative` | `medium` |
| `GT1_C1_08_T03_Derivative_Existence` | Xét tồn tại đạo hàm/khả vi | "khả vi", "không khả vi", "tồn tại đạo hàm" | `differentiability_analysis` | `medium` |
| `GT1_C1_08_T04_Chain_Rule` | Đạo hàm hàm hợp | hàm lồng nhau, `ln`, `sin`, `exp` phức hợp | `chain_rule` | `medium` |
| `GT1_C1_08_T05_Inverse_Function_Derivative` | Đạo hàm hàm ngược | "hàm số ngược", `g'(x)` với `g=f^{-1}` | `inverse_function_derivative` | `medium` |
| `GT1_C1_08_T06_Differential` | Tính vi phân | "tìm vi phân", `dy`, `df` | `differential` | `easy` |
| `GT1_C1_08_T07_Linear_Approximation` | Vi phân tính gần đúng | "tính gần đúng" | `linear_approximation`, `differential` | `medium` |
| `GT1_C1_08_T08_Higher_Order_Derivative` | Đạo hàm cấp cao | `f''`, `f'''` | `higher_order_derivative` | `medium` |
| `GT1_C1_08_T09_Higher_Order_Differential` | Vi phân cấp cao | "vi phân cấp cao" | `higher_order_differential` | `medium` |
| `GT1_C1_08_T10_Parameter_For_Differentiability` | Tham số để liên tục/khả vi | "tìm n để khả vi", tham số | `parameter_analysis`, `differentiability_analysis` | `hard` |
| `GT1_C1_08_T11_Nth_Derivative` | Đạo hàm cấp n | `f^{(n)}`, "đạo hàm cấp n" | `nth_derivative` | `hard` |

Ví dụ từ bài tập:

- Bài 24-25: tìm đạo hàm.
- Bài 26: tham số để liên tục/khả vi.
- Bài 32: vi phân tính gần đúng.
- Bài 34: đạo hàm cấp n.

### GT1_C1_09_Theorems_Applications_Differentiable_Functions

Tên hiển thị:

```text
Các định lý về hàm khả vi và ứng dụng
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C1_09_T01_Fermat_Rolle_Lagrange_Cauchy` | Định lý Fermat, Rolle, Lagrange, Cauchy | tên định lý, nghiệm, đạo hàm | `rolle_theorem`, `lagrange_mean_value_theorem`, `cauchy_mean_value_theorem`, `proof` | `hard` |
| `GT1_C1_09_T02_Proof_Using_Mean_Value_Theorem` | Chứng minh bằng định lý giá trị trung bình | chứng minh bất đẳng thức, phương trình có nghiệm | `proof`, `lagrange_mean_value_theorem` | `hard` |
| `GT1_C1_09_T03_Taylor_Maclaurin_Expansion` | Khai triển Taylor/Maclaurin | "khai triển Taylor", "Maclaurin" | `taylor_maclaurin_expansion` | `medium` |
| `GT1_C1_09_T04_Limit_By_Taylor` | Tính giới hạn bằng Taylor | giới hạn dạng vô định, yêu cầu khai triển | `taylor_maclaurin_expansion`, `function_limit` | `hard` |
| `GT1_C1_09_T05_LHopital_Rule` | Quy tắc L'Hospital | "L'Hospital", dạng `0/0`, `infinity/infinity` | `l_hopital_rule` | `medium` |
| `GT1_C1_09_T06_Monotonicity_By_Derivative` | Xét đơn điệu bằng đạo hàm | "khảo sát tính đơn điệu" | `monotonicity_analysis` | `medium` |
| `GT1_C1_09_T07_Convexity_Concavity` | Hàm lồi/lõm, bất đẳng thức | "lồi", "lõm", bất đẳng thức | `convexity_concavity`, `proof` | `hard` |
| `GT1_C1_09_T08_One_Variable_Extrema` | Cực trị hàm một biến | "tìm cực trị" | `one_variable_extrema` | `medium` |
| `GT1_C1_09_T09_Newton_Method` | Phương pháp Newton | "Newton" | `newton_method` | `medium` |
| `GT1_C1_09_T10_Parameter_Problem_Differentiable_Theorem` | Bài toán tham số trong hàm khả vi | "tìm điều kiện", "tham số", "giới hạn hữu hạn" | `parameter_analysis`, `case_analysis` | `hard` |
| `GT1_C1_09_T11_Partial_Fraction_And_Nth_Derivative` | Phân thức và đạo hàm cấp cao | phân tích phân thức, đạo hàm cấp k/n | `partial_fraction_decomposition`, `nth_derivative` | `hard` |
| `GT1_C1_09_T12_Max_Min_On_Closed_Interval` | GTLN/GTNN trên đoạn | "giá trị lớn nhất", "giá trị nhỏ nhất", "trên đoạn" | `max_min_closed_interval` | `medium` |

Ví dụ từ bài tập:

- Bài 36-41: chứng minh bằng định lý hàm khả vi.
- Bài 47-48: Taylor/Maclaurin.
- Bài 51: đơn điệu.
- Bài 53-54: GTLN/GTNN, cực trị.

### GT1_C1_10_Curve_Function_Graph_Survey

Tên hiển thị:

```text
Khảo sát hàm số, đường cong
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C1_10_T01_Function_Graph_Survey` | Khảo sát và vẽ đồ thị hàm số | "khảo sát hàm số", "vẽ đồ thị" | `monotonicity_analysis`, `convexity_concavity` | `hard` |
| `GT1_C1_10_T02_Asymptote_Analysis` | Tìm tiệm cận | "tìm tiệm cận" | `asymptote_analysis`, `function_limit` | `medium` |
| `GT1_C1_10_T03_Variation_Table` | Bảng biến thiên | "bảng biến thiên" | `monotonicity_analysis` | `medium` |
| `GT1_C1_10_T04_Convexity_Inflection` | Lồi/lõm và điểm uốn | "điểm uốn", "lồi", "lõm" | `convexity_concavity` | `medium` |
| `GT1_C1_10_T05_Parametric_Curve` | Đường cong tham số | `x(t)`, `y(t)`, "tham số" | `parametric_curve` | `hard` |
| `GT1_C1_10_T06_Polar_Curve` | Đường cong tọa độ cực | "tọa độ cực", `r`, `theta` | `polar_curve` | `hard` |

Ví dụ từ bài tập:

- Bài 55: tìm tiệm cận.
- Bài 56: đường cong tham số.

## GT1_C2_Integral_Calculus_One_Variable

Tên hiển thị:

```text
Chương 2: Phép tính tích phân hàm một biến số
```

Mô tả:

Chương này gồm tích phân bất định, tích phân xác định, tích phân suy rộng và các ứng dụng của tích phân xác định.

### GT1_C2_01_Indefinite_Integrals

Tên hiển thị:

```text
Tích phân bất định
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C2_01_T01_Basic_Antiderivative` | Nguyên hàm cơ bản | tích phân trực tiếp | `indefinite_integral` | `easy` |
| `GT1_C2_01_T02_Substitution_Method` | Phương pháp đổi biến | "đổi biến", dạng `f'(x)g(f(x))` | `substitution_method`, `indefinite_integral` | `medium` |
| `GT1_C2_01_T03_Integration_By_Parts` | Tích phân từng phần | "từng phần", tích đa thức với log/mũ/lượng giác | `integration_by_parts`, `indefinite_integral` | `medium` |
| `GT1_C2_01_T04_Rational_Function_Integral` | Tích phân phân thức hữu tỉ | phân thức hữu tỉ | `rational_function_integral` | `medium` |
| `GT1_C2_01_T05_Partial_Fractions` | Phân tích phân thức đơn giản | mẫu đa thức, phân tích thành phân thức | `partial_fraction_decomposition` | `medium` |
| `GT1_C2_01_T06_Trigonometric_Integral` | Tích phân lượng giác | `sin`, `cos`, `tan`, tích lượng giác | `trigonometric_integral` | `medium` |
| `GT1_C2_01_T07_Irrational_Integral` | Tích phân hàm vô tỉ | căn thức, biểu thức vô tỉ | `irrational_integral` | `medium` |
| `GT1_C2_01_T08_Euler_Substitution` | Đổi biến Euler | căn bậc hai của tam thức bậc hai | `euler_substitution` | `hard` |
| `GT1_C2_01_T09_Mixed_Indefinite_Integral_Methods` | Tích phân phối hợp nhiều phương pháp | đề không nêu phương pháp, cần chọn | `case_analysis`, `indefinite_integral` | `hard` |
| `GT1_C2_01_T10_Reduction_Formula` | Công thức truy hồi tích phân | `I_n`, "lập công thức truy hồi" | `reduction_formula`, `integration_by_parts` | `hard` |

Ví dụ từ bài tập:

- Bài 57: đổi biến.
- Bài 58: tích phân từng phần.
- Bài 59: phân thức hữu tỉ.
- Bài 63: công thức truy hồi.

### GT1_C2_02_Definite_Integrals

Tên hiển thị:

```text
Tích phân xác định
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C2_02_T01_Definition_And_Geometric_Meaning` | Định nghĩa và ý nghĩa tích phân xác định | định nghĩa, ý nghĩa hình học/cơ học | `definite_integral` | `easy` |
| `GT1_C2_02_T02_Integrability_Criterion` | Tiêu chuẩn khả tích | "khả tích", tiêu chuẩn | `definite_integral`, `proof` | `hard` |
| `GT1_C2_02_T03_Integral_Properties` | Tính chất tích phân xác định | dùng tính chất | `definite_integral` | `medium` |
| `GT1_C2_02_T04_Newton_Leibniz` | Công thức Newton-Leibniz | tính tích phân xác định bằng nguyên hàm | `newton_leibniz_formula` | `medium` |
| `GT1_C2_02_T05_Substitution_Definite_Integral` | Đổi biến trong tích phân xác định | đổi biến có cận | `substitution_method`, `definite_integral` | `medium` |
| `GT1_C2_02_T06_By_Parts_Definite_Integral` | Từng phần trong tích phân xác định | từng phần có cận | `integration_by_parts`, `definite_integral` | `medium` |
| `GT1_C2_02_T07_Differentiation_Under_Variable_Limits` | Đạo hàm tích phân theo cận | `d/dx int`, cận biến thiên | `differentiation_under_integral_limit` | `medium` |
| `GT1_C2_02_T08_Riemann_Sum_Definition` | Tổng tích phân/Riemann sum | "tổng tích phân", phép chia, điểm chọn | `riemann_sum`, `definite_integral` | `medium` |
| `GT1_C2_02_T09_Limit_As_Definite_Integral` | Giới hạn dưới dạng tích phân xác định | tổng có `n`, giới hạn khi `n -> infinity` | `limit_as_integral`, `riemann_sum` | `hard` |
| `GT1_C2_02_T10_Asymptotic_Integral_Function` | VCB/VCL qua hàm tích phân | tích phân phụ thuộc cận trong giới hạn | `asymptotic_comparison`, `differentiation_under_integral_limit` | `hard` |
| `GT1_C2_02_T11_Piecewise_Definite_Integral` | Tích phân xác định của hàm từng phần | `cases`, chia khoảng | `piecewise_function`, `definite_integral` | `medium` |
| `GT1_C2_02_T12_Symmetry_Property_Definite_Integral` | Tính chất đối xứng tích phân | `f(sin x)`, `f(cos x)`, đối xứng | `integral_symmetry`, `proof` | `hard` |
| `GT1_C2_02_T13_Integral_Inequality` | Bất đẳng thức tích phân | Cauchy-Schwarz, chứng minh bất đẳng thức | `integral_inequality`, `proof` | `hard` |

Ví dụ từ bài tập:

- Bài 64: tổng tích phân.
- Bài 65: đạo hàm theo cận.
- Bài 66: giới hạn dưới dạng tích phân.
- Bài 74: bất đẳng thức Cauchy-Schwarz.

### GT1_C2_03_Improper_Integrals

Tên hiển thị:

```text
Tích phân suy rộng
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C2_03_T01_Type_One_Infinite_Interval` | Tích phân suy rộng loại 1 | cận vô hạn | `improper_integral_convergence` | `medium` |
| `GT1_C2_03_T02_Type_Two_Unbounded_Function` | Tích phân suy rộng loại 2 | hàm không bị chặn tại điểm/cận | `improper_integral_convergence` | `medium` |
| `GT1_C2_03_T03_Compute_Improper_Integral` | Tính giá trị tích phân suy rộng | "tính trong trường hợp hội tụ" | `improper_integral_convergence`, `limit_computation` | `medium` |
| `GT1_C2_03_T04_Convergence_Divergence` | Xét hội tụ/phân kỳ | "xét sự hội tụ" | `improper_integral_convergence` | `medium` |
| `GT1_C2_03_T05_Comparison_Test` | Tiêu chuẩn so sánh | "so sánh", gần 0/vô cực | `comparison_test` | `hard` |
| `GT1_C2_03_T06_Absolute_Convergence` | Hội tụ tuyệt đối | "hội tụ tuyệt đối" | `absolute_convergence` | `hard` |
| `GT1_C2_03_T07_Conditional_Convergence` | Bán hội tụ | "bán hội tụ", hội tụ không tuyệt đối | `conditional_convergence` | `hard` |
| `GT1_C2_03_T08_Parameter_Improper_Integral` | Tích phân suy rộng có tham số | `alpha`, `beta`, "khi và chỉ khi" | `parameter_analysis`, `comparison_test` | `hard` |
| `GT1_C2_03_T09_Proof_Improper_Integral_Condition` | Chứng minh điều kiện hội tụ | "chứng minh", "khi và chỉ khi" | `proof`, `improper_integral_convergence` | `hard` |
| `GT1_C2_03_T10_Counterexample_Improper_Integral` | Phản ví dụ tích phân suy rộng | "có suy ra được không", "ví dụ" | `counterexample_construction` | `hard` |

Ví dụ từ bài tập:

- Bài 75-76: hội tụ/phân kỳ.
- Bài 77-78: tích phân suy rộng có tham số.
- Bài 79: phản ví dụ.

### GT1_C2_04_Applications_Definite_Integrals

Tên hiển thị:

```text
Ứng dụng của tích phân xác định
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C2_04_T01_Area_Plane_Region` | Diện tích hình phẳng | "diện tích", miền phẳng, giới hạn bởi đường | `area_by_integral`, `application` | `medium` |
| `GT1_C2_04_T02_Arc_Length` | Độ dài cung phẳng | "độ dài cung" | `arc_length`, `application` | `medium` |
| `GT1_C2_04_T03_Volume_Of_Solid` | Thể tích vật thể | "thể tích vật thể", mặt cong, mặt phẳng | `volume_by_integral`, `application` | `hard` |
| `GT1_C2_04_T04_Volume_Of_Revolution` | Thể tích khối tròn xoay | "quay quanh trục", "khối tròn xoay" | `volume_of_revolution`, `application` | `medium` |
| `GT1_C2_04_T05_Surface_Area_Of_Revolution` | Diện tích mặt tròn xoay | "diện tích mặt tròn xoay" | `surface_area_of_revolution`, `application` | `medium` |

Ví dụ từ bài tập:

- Bài 81: diện tích hình phẳng.
- Bài 84: thể tích khối tròn xoay.
- Bài 86: diện tích mặt tròn xoay.

## GT1_C3_Multivariable_Functions

Tên hiển thị:

```text
Chương 3: Hàm số nhiều biến số
```

Mô tả:

Chương này gồm các khái niệm cơ bản về hàm nhiều biến, giới hạn, liên tục, đạo hàm riêng, vi phân, hàm ẩn, Taylor nhiều biến và cực trị.

### GT1_C3_01_Multivariable_Basics

Tên hiển thị:

```text
Các khái niệm cơ bản
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C3_01_T01_Domain_Of_Multivariable_Function` | Miền xác định hàm nhiều biến | `z=f(x,y)`, "tìm miền xác định" | `multivariable_domain` | `easy` |
| `GT1_C3_01_T02_Open_Closed_Bounded_Set` | Miền mở, đóng, bị chặn | "mở", "đóng", "bị chặn", "biên" | `multivariable_domain` | `medium` |
| `GT1_C3_01_T03_Multivariable_Limit` | Giới hạn hàm nhiều biến | `(x,y)->(a,b)`, "tìm giới hạn" | `multivariable_limit` | `medium` |
| `GT1_C3_01_T04_Path_Dependent_Limit` | Chứng minh không tồn tại giới hạn bằng đường đi | nhiều đường đi, kết quả khác nhau | `path_limit_counterexample` | `hard` |
| `GT1_C3_01_T05_Multivariable_Continuity` | Liên tục hàm nhiều biến | "liên tục tại", hàm từng phần hai biến | `multivariable_continuity` | `medium` |
| `GT1_C3_01_T06_Parameter_For_Continuity` | Tham số để liên tục nhiều biến | tham số trong hàm nhiều biến | `parameter_analysis`, `multivariable_continuity` | `hard` |
| `GT1_C3_01_T07_Multivariable_Function_Composition` | Hàm hợp nhiều biến | `x(t)`, `y(t)`, `u(r,theta)`, `v(r,theta)` | `multivariable_function_composition` | `easy` |
| `GT1_C3_01_T08_Iterated_And_Joint_Limit` | Giới hạn lặp và giới hạn hai biến | `lim_x lim_y`, `lim_y lim_x`, joint limit | `iterated_limit`, `multivariable_limit` | `medium` |

Ví dụ từ bài tập:

- Bài 87: miền xác định.
- Bài 89: giới hạn hai biến.
- Bài 91: giới hạn lặp và giới hạn đồng thời.

### GT1_C3_02_Partial_Derivatives_Differentials

Tên hiển thị:

```text
Đạo hàm riêng và vi phân
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C3_02_T01_First_Order_Partial_Derivative` | Đạo hàm riêng cấp một | `z'_x`, `z'_y`, partial derivative | `partial_derivative` | `easy` |
| `GT1_C3_02_T02_Total_Differential` | Vi phân toàn phần | "vi phân toàn phần", `dz` | `total_differential` | `easy` |
| `GT1_C3_02_T03_Approximation_By_Differential` | Vi phân tính gần đúng | "ứng dụng vi phân, tính gần đúng" | `multivariable_approximation`, `total_differential` | `medium` |
| `GT1_C3_02_T04_Multivariable_Chain_Rule` | Đạo hàm hàm hợp nhiều biến | hàm hợp nhiều biến | `multivariable_chain_rule` | `medium` |
| `GT1_C3_02_T05_Higher_Order_Partial_Derivative` | Đạo hàm riêng cấp cao | đạo hàm riêng cấp hai/cấp cao | `higher_order_partial_derivative` | `medium` |
| `GT1_C3_02_T06_Schwarz_Theorem` | Định lý Schwarz, đạo hàm hỗn hợp | `f''xy`, `f''yx`, tính liên tục | `schwarz_theorem` | `hard` |
| `GT1_C3_02_T07_Directional_Derivative_Gradient` | Đạo hàm theo hướng, gradient | "gradient", "đạo hàm theo hướng" | `partial_derivative` | `medium` |
| `GT1_C3_02_T08_Implicit_Function_Derivative` | Đạo hàm hàm ẩn | phương trình ẩn, `z=z(x,y)`, `y(x)` | `implicit_function_derivative` | `medium` |
| `GT1_C3_02_T09_Multivariable_Taylor` | Taylor/Maclaurin nhiều biến | "Taylor", "Maclaurin" với `f(x,y)` | `multivariable_taylor_expansion` | `hard` |
| `GT1_C3_02_T10_Continuity_And_Partial_Derivative_Existence` | Liên tục và tồn tại đạo hàm riêng | "khảo sát sự liên tục và sự tồn tại các đạo hàm riêng" | `multivariable_continuity`, `partial_derivative` | `hard` |
| `GT1_C3_02_T11_Identity_With_Partial_Derivatives` | Chứng minh đẳng thức đạo hàm riêng | "chứng minh rằng", biểu thức chứa `z'_x`, `z'_y` | `partial_derivative`, `proof` | `hard` |
| `GT1_C3_02_T12_Partial_Differential_Equation_Verification` | Kiểm tra phương trình đạo hàm riêng | "thỏa mãn phương trình", PDE | `partial_differential_equation_verification`, `proof` | `hard` |
| `GT1_C3_02_T13_Second_Order_Differential` | Vi phân cấp hai | "vi phân cấp hai" | `second_order_differential` | `medium` |

Ví dụ từ bài tập:

- Bài 92: đạo hàm riêng.
- Bài 95: đạo hàm hàm hợp.
- Bài 100-104: hàm ẩn.
- Bài 107: đạo hàm hỗn hợp và Schwarz.
- Bài 108: Taylor/Maclaurin nhiều biến.

### GT1_C3_03_Multivariable_Extrema

Tên hiển thị:

```text
Cực trị của hàm số nhiều biến số
```

Dạng bài:

| Mã dạng bài | Tên hiển thị | Dấu hiệu nhận diện | Skills | Độ khó mặc định |
| --- | --- | --- | --- | --- |
| `GT1_C3_03_T01_Critical_Point` | Tìm điểm dừng/điểm tới hạn | hệ `f'_x=0`, `f'_y=0` | `critical_point` | `medium` |
| `GT1_C3_03_T02_Unconstrained_Extrema` | Cực trị tự do | "tìm cực trị" không ràng buộc | `unconstrained_extrema` | `medium` |
| `GT1_C3_03_T03_Hessian_Test` | Phân loại cực trị bằng Hessian | đạo hàm cấp hai, định thức Hessian | `hessian_extrema_test` | `medium` |
| `GT1_C3_03_T04_Constrained_Extrema` | Cực trị có điều kiện | ràng buộc như elip, đường cong, mặt | `constrained_extrema` | `hard` |
| `GT1_C3_03_T05_Lagrange_Multiplier` | Nhân tử Lagrange | "cực trị có điều kiện", ràng buộc `g(x,y)=0` | `lagrange_multiplier` | `hard` |
| `GT1_C3_03_T06_Global_Maximum_Minimum` | GTLN/GTNN trên miền | "giá trị lớn nhất", "giá trị nhỏ nhất", miền đóng | `global_maximum_minimum`, `case_analysis` | `hard` |

Ví dụ từ bài tập:

- Bài 109: cực trị tự do.
- Bài 110: cực trị có điều kiện trên elip.
- Bài 111: GTLN/GTNN trên miền bị chặn.

## 7. Prompt template cho AI classifier

```text
You are a Calculus 1 taxonomy classifier for students in Applied Mathematics and Informatics at Hanoi University of Science and Technology.

Classify the given question into exactly one taxonomy path:
chapter -> topic -> subtopic.

Use only the taxonomy codes, Vietnamese display names, skills, and difficulty rubric provided in the knowledge base.

Return valid JSON only.

Required JSON schema:
{
  "subject": "Calculus 1",
  "chapter": "...",
  "chapter_name": "...",
  "topic": "...",
  "topic_name": "...",
  "subtopic": "...",
  "subtopic_name": "...",
  "skills": ["..."],
  "difficulty": "easy|medium|hard",
  "confidence": 0.0,
  "reason": "..."
}

Rules:
- Choose the most specific subtopic.
- Prefer the main solving method.
- If the problem states a method explicitly, use that method as the subtopic.
- Use only skills listed in the skill vocabulary.
- Difficulty must follow the rubric.
- If uncertain, choose the closest subtopic and lower confidence.
- Do not invent taxonomy codes.

Question:
{question_statement}

Solution if available:
{question_solution}

Answer if available:
{question_answer}

Extracted formulas:
{question_formulas}
```

## 8. Ví dụ matching chuẩn

### Ví dụ 1

Câu hỏi:

```text
Tìm tập xác định của y = sqrt[4]((2x-1)/(1+3x)).
```

Kết quả:

```json
{
  "subject": "Calculus 1",
  "chapter": "GT1_C1_Differential_Calculus_One_Variable",
  "chapter_name": "Chương 1: Phép tính vi phân hàm một biến số",
  "topic": "GT1_C1_02_Function_Basics",
  "topic_name": "Hàm số và các khái niệm cơ bản",
  "subtopic": "GT1_C1_02_T01_Domain_And_Range",
  "subtopic_name": "Tìm tập xác định, tập giá trị",
  "skills": ["function_domain_range", "algebraic_transformation"],
  "difficulty": "easy",
  "confidence": 0.95,
  "reason": "Đề bài yêu cầu tìm tập xác định của hàm số một biến."
}
```

### Ví dụ 2

Câu hỏi:

```text
Tính các tích phân bất định sau theo phương pháp tích phân từng phần.
```

Kết quả:

```json
{
  "subject": "Calculus 1",
  "chapter": "GT1_C2_Integral_Calculus_One_Variable",
  "chapter_name": "Chương 2: Phép tính tích phân hàm một biến số",
  "topic": "GT1_C2_01_Indefinite_Integrals",
  "topic_name": "Tích phân bất định",
  "subtopic": "GT1_C2_01_T03_Integration_By_Parts",
  "subtopic_name": "Tích phân từng phần",
  "skills": ["integration_by_parts", "indefinite_integral"],
  "difficulty": "medium",
  "confidence": 0.98,
  "reason": "Đề bài nêu trực tiếp phương pháp tích phân từng phần."
}
```

### Ví dụ 3

Câu hỏi:

```text
Khảo sát sự hội tụ của tích phân suy rộng int_0^1 x^alpha (ln x)^beta dx.
```

Kết quả:

```json
{
  "subject": "Calculus 1",
  "chapter": "GT1_C2_Integral_Calculus_One_Variable",
  "chapter_name": "Chương 2: Phép tính tích phân hàm một biến số",
  "topic": "GT1_C2_03_Improper_Integrals",
  "topic_name": "Tích phân suy rộng",
  "subtopic": "GT1_C2_03_T08_Parameter_Improper_Integral",
  "subtopic_name": "Tích phân suy rộng có tham số",
  "skills": ["improper_integral_convergence", "parameter_analysis", "comparison_test"],
  "difficulty": "hard",
  "confidence": 0.94,
  "reason": "Đề yêu cầu khảo sát hội tụ của tích phân suy rộng phụ thuộc tham số alpha và beta."
}
```

### Ví dụ 4

Câu hỏi:

```text
Tìm cực trị của z = 4x^3 + 6x^2 - 4xy - y^2 - 8x + 2.
```

Kết quả:

```json
{
  "subject": "Calculus 1",
  "chapter": "GT1_C3_Multivariable_Functions",
  "chapter_name": "Chương 3: Hàm số nhiều biến số",
  "topic": "GT1_C3_03_Multivariable_Extrema",
  "topic_name": "Cực trị của hàm số nhiều biến số",
  "subtopic": "GT1_C3_03_T02_Unconstrained_Extrema",
  "subtopic_name": "Cực trị tự do",
  "skills": ["critical_point", "hessian_extrema_test"],
  "difficulty": "medium",
  "confidence": 0.93,
  "reason": "Đề yêu cầu tìm cực trị của hàm hai biến không kèm ràng buộc."
}
```

## 9. Tiêu chí dùng trong hệ thống AI Matching

Một câu hỏi được xem là đã match thành công nếu:

- Có `chapter`, `topic`, `subtopic` hợp lệ.
- Có `difficulty` hợp lệ.
- Có ít nhất một skill.
- Có `confidence`.
- Có `reason` giải thích ngắn gọn.

Câu hỏi cần đưa vào QA nếu:

- `confidence < 0.65`.
- Không tìm được `subtopic`.
- AI trả mã taxonomy không tồn tại.
- `difficulty` không thuộc `easy`, `medium`, `hard`.
- Câu hỏi có nhiều khả năng thuộc nhiều topic khác nhau nhưng chỉ match confidence thấp.

## 10. Ghi chú triển khai

Khi đưa vào backend:

- Có thể lưu mã taxonomy trong database:
  - `chapter`
  - `topic`
  - `subtopic`
- Có thể lưu tên hiển thị để cache:
  - `chapter_name`
  - `topic_name`
  - `subtopic_name`
- Nên lưu thêm:
  - `taxonomy_confidence`
  - `taxonomy_reason`
  - `taxonomy_version`
  - `classification_model`
  - `classified_at`

Khi đưa vào frontend:

- Hiển thị tên tiếng Việt.
- Chỉ dùng mã tiếng Anh cho filter/API.
- Trang Taxonomy nên đếm số câu hỏi theo `topic` và `subtopic`.
- Trang Problem Detail nên hiển thị confidence và reason.

## 11. Kết luận

Tài liệu này là bản bộ não tri thức chính thức cho hướng:

```text
AI Matching câu hỏi vào cây tri thức Giải tích 1
```

Cấu trúc đã đủ để phục vụ:

- AI classifier.
- Matching câu hỏi vào chương/chủ đề/dạng bài.
- Thống kê taxonomy.
- Search/filter theo kiến thức.
- QA các câu chưa match hoặc confidence thấp.
- Sinh biến thể cùng dạng bài.

## 12. Bổ sung alias và dấu hiệu nhận diện

Mục này giúp AI classifier ổn định hơn khi đề bài dùng nhiều cách gọi khác nhau cho cùng một dạng kiến thức.

Nguyên tắc:

- `aliases` là các cách gọi tương đương bằng tiếng Việt hoặc ký hiệu toán.
- `positive_signals` là dấu hiệu nên match vào dạng bài.
- `negative_signals` là dấu hiệu cần cẩn thận để không match nhầm.

### 12.1. Nhóm giới hạn và liên tục

| Taxonomy code | Aliases | Positive signals | Negative signals |
| --- | --- | --- | --- |
| `GT1_C1_05_T02_Algebraic_Transformation_Limit` | giới hạn, khử dạng vô định, hữu tỉ hóa, rút gọn | căn thức, phân thức, `0/0`, `infinity - infinity`, cần biến đổi đại số | nếu đề/lời giải nêu L'Hospital hoặc Taylor thì ưu tiên dạng tương ứng |
| `GT1_C1_05_T03_One_Sided_Limit` | giới hạn một phía, giới hạn trái, giới hạn phải | `x -> a+`, `x -> a-`, hàm từng phần tại điểm nối | nếu câu hỏi chính là liên tục thì ưu tiên `Continuity` |
| `GT1_C1_06_T02_Equivalent_Infinitesimal` | VCB tương đương, vô cùng bé tương đương, tương đương khi x -> 0 | `sin x ~ x`, `ln(1+x) ~ x`, `e^x-1 ~ x`, so sánh bậc nhỏ | nếu yêu cầu khai triển đến cấp cụ thể thì ưu tiên Taylor/Maclaurin |
| `GT1_C1_07_T04_Find_Parameter_For_Continuity` | tìm a để liên tục, chọn tham số để liên tục | hàm từng phần, tham số tại điểm nối, yêu cầu liên tục tại `x=0` hoặc `x=a` | nếu yêu cầu khả vi thì ưu tiên `Parameter_For_Differentiability` |
| `GT1_C1_07_T05_Classify_Discontinuity` | phân loại gián đoạn, gián đoạn loại 1, gián đoạn loại 2, khử được | yêu cầu xác định/phân loại điểm gián đoạn | nếu chỉ hỏi giới hạn tại điểm thì ưu tiên nhóm giới hạn |

### 12.2. Nhóm đạo hàm, vi phân và định lý hàm khả vi

| Taxonomy code | Aliases | Positive signals | Negative signals |
| --- | --- | --- | --- |
| `GT1_C1_08_T01_Basic_Derivative` | đạo hàm, tính `f'(x)`, đạo hàm thường | đề yêu cầu tính đạo hàm trực tiếp | nếu có hàm ngược hoặc hàm hợp rõ thì ưu tiên subtopic cụ thể |
| `GT1_C1_08_T03_Derivative_Existence` | khả vi, tồn tại đạo hàm, không khả vi | giá trị tuyệt đối, hàm từng phần, xét tại điểm | nếu có tham số cần tìm thì ưu tiên `Parameter_For_Differentiability` |
| `GT1_C1_08_T07_Linear_Approximation` | tính gần đúng, xấp xỉ, vi phân | số gần 1 hoặc gần giá trị đặc biệt, yêu cầu dùng vi phân | nếu là Taylor cấp cao thì ưu tiên Taylor/Maclaurin |
| `GT1_C1_09_T01_Fermat_Rolle_Lagrange_Cauchy` | Rolle, Lagrange, Cauchy, Fermat, định lý giá trị trung bình | chứng minh tồn tại nghiệm/điểm, có đạo hàm trên khoảng | nếu chỉ xét đơn điệu/cực trị thì ưu tiên dạng ứng dụng cụ thể |
| `GT1_C1_09_T05_LHopital_Rule` | L'Hospital, L'Hopital, quy tắc Hospital | dạng `0/0`, `infinity/infinity`, dùng đạo hàm tử/mẫu | nếu đề dùng VCB/Taylor rõ ràng thì không chọn L'Hospital |
| `GT1_C1_09_T03_Taylor_Maclaurin_Expansion` | Taylor, Maclaurin, khai triển | yêu cầu khai triển đến cấp `n`, lân cận điểm | nếu chỉ dùng khai triển để tính giới hạn thì có thể chọn `Limit_By_Taylor` |

### 12.3. Nhóm tích phân

| Taxonomy code | Aliases | Positive signals | Negative signals |
| --- | --- | --- | --- |
| `GT1_C2_01_T01_Basic_Antiderivative` | nguyên hàm, tích phân bất định, họ nguyên hàm | `int f(x) dx` không có cận, công thức trực tiếp | nếu đề nêu phương pháp đổi biến/từng phần thì ưu tiên phương pháp đó |
| `GT1_C2_01_T02_Substitution_Method` | đổi biến, đặt `u`, phép thế | dạng `f'(x)g(f(x))`, đề nêu "theo phương pháp đổi biến" | nếu có cận thì có thể thuộc tích phân xác định đổi biến |
| `GT1_C2_01_T03_Integration_By_Parts` | tích phân từng phần, từng phần | tích đa thức với log/mũ/lượng giác, đề nêu "từng phần" | nếu là tích phân xác định có cận thì chọn bản definite nếu trọng tâm là cận |
| `GT1_C2_01_T10_Reduction_Formula` | công thức truy hồi, lập công thức `I_n` | xuất hiện `I_n`, yêu cầu lập công thức tổng quát | nếu chỉ tính một tích phân cụ thể thì không chọn |
| `GT1_C2_02_T08_Riemann_Sum_Definition` | tổng tích phân, tổng Riemann, phép chia | `x_i`, `Delta x`, điểm chọn, giới hạn tổng | nếu chỉ tính tích phân bằng Newton-Leibniz thì không chọn |
| `GT1_C2_02_T09_Limit_As_Definite_Integral` | giới hạn tổng thành tích phân, tổng Riemann | tổng có `n`, `lim n -> infinity` | nếu không có tổng hữu hạn thì không chọn |
| `GT1_C2_03_T08_Parameter_Improper_Integral` | tích phân suy rộng có tham số, khảo sát theo alpha/beta | `alpha`, `beta`, "hội tụ khi nào" | nếu không có tham số thì chọn hội tụ/phân kỳ thông thường |

### 12.4. Nhóm hàm nhiều biến

| Taxonomy code | Aliases | Positive signals | Negative signals |
| --- | --- | --- | --- |
| `GT1_C3_01_T03_Multivariable_Limit` | giới hạn hàm hai biến, giới hạn nhiều biến | `(x,y)->(0,0)`, `f(x,y)` | nếu cần chứng minh không tồn tại bằng đường đi thì chọn `Path_Dependent_Limit` |
| `GT1_C3_01_T08_Iterated_And_Joint_Limit` | giới hạn lặp, giới hạn riêng, giới hạn đồng thời | `lim_x lim_y`, `lim_y lim_x`, so sánh với giới hạn hai biến | nếu chỉ có joint limit thì không chọn |
| `GT1_C3_02_T08_Implicit_Function_Derivative` | hàm ẩn, đạo hàm hàm ẩn, hệ hàm ẩn | phương trình xác định `y(x)` hoặc `z(x,y)` | nếu chỉ là đạo hàm riêng trực tiếp thì không chọn |
| `GT1_C3_02_T06_Schwarz_Theorem` | Schwarz, đạo hàm hỗn hợp, `f''xy`, `f''yx` | so sánh đạo hàm hỗn hợp, tính liên tục đạo hàm cấp hai | nếu chỉ tính đạo hàm cấp hai trực tiếp thì chọn higher order |
| `GT1_C3_03_T04_Constrained_Extrema` | cực trị có điều kiện, ràng buộc | elip, đường cong, điều kiện `g(x,y)=0` | nếu đề nói rõ Lagrange thì chọn `Lagrange_Multiplier` |
| `GT1_C3_03_T06_Global_Maximum_Minimum` | GTLN, GTNN, max/min trên miền | miền tam giác, miền elip, miền đóng bị chặn | không nhầm với cực trị tự do trong toàn mặt phẳng |

## 13. Quy tắc xử lý trường hợp dễ nhầm

### 13.1. Giới hạn thường, VCB, Taylor và L'Hospital

Thứ tự ưu tiên:

1. Nếu đề/lời giải yêu cầu hoặc nêu rõ L'Hospital, chọn `GT1_C1_09_T05_LHopital_Rule`.
2. Nếu đề yêu cầu khai triển Taylor/Maclaurin hoặc cần khai triển đến cấp cụ thể, chọn `GT1_C1_09_T04_Limit_By_Taylor` hoặc `GT1_C1_09_T03_Taylor_Maclaurin_Expansion`.
3. Nếu dấu hiệu chính là VCB tương đương, chọn `GT1_C1_06_T02_Equivalent_Infinitesimal`.
4. Nếu chỉ cần rút gọn/hữu tỉ hóa/biến đổi đại số, chọn `GT1_C1_05_T02_Algebraic_Transformation_Limit`.

Ví dụ:

```text
lim (sin x - x)/x^3
```

Nên match vào Taylor/Maclaurin hoặc VCB bậc cao, không nên match vào giới hạn đại số thường.

### 13.2. Liên tục và giới hạn

Nếu đề hỏi:

- "Tính giới hạn" -> ưu tiên topic giới hạn.
- "Hàm có liên tục tại..." -> ưu tiên topic liên tục.
- "Tìm tham số để liên tục" -> ưu tiên `GT1_C1_07_T04_Find_Parameter_For_Continuity`.
- "Phân loại điểm gián đoạn" -> ưu tiên `GT1_C1_07_T05_Classify_Discontinuity`.

### 13.3. Đạo hàm, khả vi và liên tục

Nếu đề đồng thời hỏi liên tục và khả vi:

- Nếu mục tiêu cuối cùng là khả vi/đạo hàm tồn tại, chọn topic đạo hàm.
- Nếu chỉ yêu cầu liên tục, chọn topic liên tục.
- Nếu có tham số để khả vi, chọn `GT1_C1_08_T10_Parameter_For_Differentiability`.

### 13.4. Tích phân bất định và tích phân xác định

Quy tắc:

- Không có cận: ưu tiên `GT1_C2_01_Indefinite_Integrals`.
- Có cận hữu hạn: ưu tiên `GT1_C2_02_Definite_Integrals`.
- Có cận vô hạn hoặc hàm không bị chặn tại cận/điểm trong miền: ưu tiên `GT1_C2_03_Improper_Integrals`.
- Có từ khóa diện tích/thể tích/độ dài/mặt tròn xoay: ưu tiên `GT1_C2_04_Applications_Definite_Integrals`.

### 13.5. Cực trị nhiều biến, cực trị có điều kiện và GTLN/GTNN

Quy tắc:

- "Tìm cực trị" không có ràng buộc -> `GT1_C3_03_T02_Unconstrained_Extrema`.
- Có ràng buộc `g(x,y)=0`, elip, đường cong -> `GT1_C3_03_T04_Constrained_Extrema`.
- Có từ "Lagrange" hoặc dùng nhân tử -> `GT1_C3_03_T05_Lagrange_Multiplier`.
- Có "giá trị lớn nhất/nhỏ nhất" trên miền đóng -> `GT1_C3_03_T06_Global_Maximum_Minimum`.

## 14. Quy tắc xử lý bài nhiều ý

Nhiều bài tập trong MI1111 có dạng:

```text
Bài X. ...
a) ...
b) ...
c) ...
```

Hệ thống nên xử lý theo quy tắc:

1. Nếu pipeline tách được từng ý a/b/c, hãy match từng ý riêng.
2. Nếu chưa tách được từng ý, match theo tiêu đề bài nếu tiêu đề nêu rõ dạng.
3. Nếu tiêu đề không rõ, chọn dạng bài chiếm đa số trong các ý.
4. Nếu các ý thuộc nhiều topic khác nhau, gán:
   - `subtopic`: dạng chính
   - `secondary_subtopics`: các dạng phụ, nếu database/API hỗ trợ
5. Nếu không hỗ trợ `secondary_subtopics`, ghi trong `reason` rằng bài có nhiều ý và nhãn được chọn theo dạng chiếm ưu thế.

Ví dụ:

```text
Bài 61. Tính các tích phân bất định sau:
```

Các ý có thể dùng đổi biến, từng phần, phân thức, lượng giác, vô tỉ. Nếu phân loại cả bài, nên chọn:

```text
GT1_C2_01_T09_Mixed_Indefinite_Integral_Methods
```

Nếu tách từng ý, mỗi ý nên được match vào phương pháp cụ thể hơn.

## 15. Chính sách confidence

AI classifier phải gán confidence theo quy tắc sau:

| Khoảng confidence | Ý nghĩa | Cách xử lý |
| --- | --- | --- |
| `0.90 - 1.00` | Dạng bài rất rõ, đề nêu trực tiếp hoặc dấu hiệu mạnh | Tự động lưu |
| `0.75 - 0.89` | Đúng topic, subtopic khá chắc nhưng cần suy luận | Tự động lưu, có thể cho phép người dùng sửa |
| `0.60 - 0.74` | Đúng chapter/topic nhưng subtopic chưa chắc | Đưa vào QA mềm |
| `< 0.60` | Không chắc hoặc có nhiều topic cạnh tranh | Đưa vào QA bắt buộc |

Giảm confidence nếu:

- Câu hỏi thiếu dữ liệu hoặc OCR lỗi.
- Công thức bị hỏng.
- Có nhiều ý thuộc nhiều dạng khác nhau.
- Không tìm được dấu hiệu nhận diện rõ.
- Dạng bài có thể thuộc nhiều topic gần nhau.

Tăng confidence nếu:

- Tiêu đề bài nêu trực tiếp dạng/phương pháp.
- Có từ khóa rất đặc trưng như "tích phân từng phần", "L'Hospital", "GTLN/GTNN", "hàm ẩn".
- Công thức khớp rõ với dấu hiệu nhận diện.

## 16. Ví dụ bổ sung theo từng nhóm trọng tâm

### 16.1. VCB tương đương

Câu hỏi:

```text
Tính giới hạn lim_{x->0} (ln(1+x)-x)/x^2.
```

Expected:

```json
{
  "subtopic": "GT1_C1_06_T02_Equivalent_Infinitesimal",
  "subtopic_name": "Dùng VCB tương đương",
  "skills": ["infinitesimal_equivalent", "function_limit"],
  "difficulty": "medium"
}
```

### 16.2. Tìm tham số để liên tục

Câu hỏi:

```text
Tìm a để hàm số từng phần liên tục tại x=0.
```

Expected:

```json
{
  "subtopic": "GT1_C1_07_T04_Find_Parameter_For_Continuity",
  "subtopic_name": "Tìm tham số để liên tục",
  "skills": ["parameter_analysis", "continuity_analysis"],
  "difficulty": "hard"
}
```

### 16.3. Đạo hàm hàm ngược

Câu hỏi:

```text
Cho g(x) là hàm số ngược của f(x)=sinh x. Tính g'(x).
```

Expected:

```json
{
  "subtopic": "GT1_C1_08_T05_Inverse_Function_Derivative",
  "subtopic_name": "Đạo hàm hàm ngược",
  "skills": ["inverse_function_derivative"],
  "difficulty": "medium"
}
```

### 16.4. Tổng Riemann

Câu hỏi:

```text
Viết tổng tích phân của f(x)=e^x trên [0,1] với phép chia x_i=i/n và tính giới hạn của tổng.
```

Expected:

```json
{
  "subtopic": "GT1_C2_02_T08_Riemann_Sum_Definition",
  "subtopic_name": "Tổng tích phân/Riemann sum",
  "skills": ["riemann_sum", "definite_integral"],
  "difficulty": "medium"
}
```

### 16.5. Tích phân suy rộng có tham số

Câu hỏi:

```text
Khảo sát sự hội tụ của int_0^1 x^alpha (ln x)^beta dx với alpha,beta thuộc R.
```

Expected:

```json
{
  "subtopic": "GT1_C2_03_T08_Parameter_Improper_Integral",
  "subtopic_name": "Tích phân suy rộng có tham số",
  "skills": ["parameter_analysis", "improper_integral_convergence", "comparison_test"],
  "difficulty": "hard"
}
```

### 16.6. Giới hạn nhiều biến không tồn tại

Câu hỏi:

```text
Tìm giới hạn nếu có của f(x,y)=xy/(x^2+y^2) khi (x,y)->(0,0).
```

Expected:

```json
{
  "subtopic": "GT1_C3_01_T04_Path_Dependent_Limit",
  "subtopic_name": "Chứng minh không tồn tại giới hạn bằng đường đi",
  "skills": ["path_limit_counterexample", "multivariable_limit"],
  "difficulty": "medium"
}
```

### 16.7. Hàm ẩn nhiều biến

Câu hỏi:

```text
Phương trình x+y+z=e^z xác định z=z(x,y). Tính z'_x, z'_y.
```

Expected:

```json
{
  "subtopic": "GT1_C3_02_T08_Implicit_Function_Derivative",
  "subtopic_name": "Đạo hàm hàm ẩn",
  "skills": ["implicit_function_derivative", "partial_derivative"],
  "difficulty": "medium"
}
```

### 16.8. GTLN/GTNN trên miền đóng

Câu hỏi:

```text
Tính giá trị lớn nhất và nhỏ nhất của z=x^2+y^2+xy-7x-8y trong tam giác x=0, y=0, x+y=6.
```

Expected:

```json
{
  "subtopic": "GT1_C3_03_T06_Global_Maximum_Minimum",
  "subtopic_name": "GTLN/GTNN trên miền",
  "skills": ["global_maximum_minimum", "case_analysis"],
  "difficulty": "hard"
}
```

## 17. Bộ test đánh giá AI Matching đề xuất

Bộ test nhãn tay nên lấy từ `2025.1_BTTK_MI1111.md`.

Mục tiêu:

- Kiểm tra AI match đúng chapter.
- Kiểm tra AI match đúng topic.
- Kiểm tra AI match đúng subtopic.
- Kiểm tra độ khó và confidence có hợp lý không.

### 17.1. Tập test tối thiểu

Nên chọn ít nhất 50 câu/ý:

| Nhóm | Số mẫu | Mục tiêu |
| --- | ---: | --- |
| Chương 1 | 20 | Hàm số, giới hạn, liên tục, đạo hàm, định lý khả vi |
| Chương 2 | 15 | Tích phân bất định, xác định, suy rộng, ứng dụng |
| Chương 3 | 15 | Hàm nhiều biến, đạo hàm riêng, hàm ẩn, cực trị |

### 17.2. Bộ mẫu đề xuất

| Mẫu | Nguồn | Expected subtopic |
| --- | --- | --- |
| 1 | Bài 1a | `GT1_C1_02_T01_Domain_And_Range` |
| 2 | Bài 4b | `GT1_C1_02_T05_Piecewise_Function_Modeling` |
| 3 | Bài 7a | `GT1_C1_02_T04_Inverse_Function` |
| 4 | Bài 9a | `GT1_C1_04_T01_Compute_Sequence_Limit` |
| 5 | Bài 10 | `GT1_C1_05_T07_Proof_By_Definition` |
| 6 | Bài 13a | `GT1_C1_06_T01_Compare_Infinitesimal` |
| 7 | Bài 16 | `GT1_C1_07_T04_Find_Parameter_For_Continuity` |
| 8 | Bài 18 | `GT1_C1_07_T05_Classify_Discontinuity` |
| 9 | Bài 26 | `GT1_C1_08_T10_Parameter_For_Differentiability` |
| 10 | Bài 28 | `GT1_C1_08_T05_Inverse_Function_Derivative` |
| 11 | Bài 32 | `GT1_C1_08_T07_Linear_Approximation` |
| 12 | Bài 34 | `GT1_C1_08_T11_Nth_Derivative` |
| 13 | Bài 40 | `GT1_C1_09_T02_Proof_Using_Mean_Value_Theorem` |
| 14 | Bài 47 | `GT1_C1_09_T03_Taylor_Maclaurin_Expansion` |
| 15 | Bài 51 | `GT1_C1_09_T06_Monotonicity_By_Derivative` |
| 16 | Bài 55 | `GT1_C1_10_T02_Asymptote_Analysis` |
| 17 | Bài 57a | `GT1_C2_01_T02_Substitution_Method` |
| 18 | Bài 58a | `GT1_C2_01_T03_Integration_By_Parts` |
| 19 | Bài 59a | `GT1_C2_01_T04_Rational_Function_Integral` |
| 20 | Bài 63a | `GT1_C2_01_T10_Reduction_Formula` |
| 21 | Bài 64 | `GT1_C2_02_T08_Riemann_Sum_Definition` |
| 22 | Bài 65c | `GT1_C2_02_T07_Differentiation_Under_Variable_Limits` |
| 23 | Bài 66a | `GT1_C2_02_T09_Limit_As_Definite_Integral` |
| 24 | Bài 73 | `GT1_C2_02_T12_Symmetry_Property_Definite_Integral` |
| 25 | Bài 74 | `GT1_C2_02_T13_Integral_Inequality` |
| 26 | Bài 75a | `GT1_C2_03_T03_Compute_Improper_Integral` |
| 27 | Bài 77 | `GT1_C2_03_T08_Parameter_Improper_Integral` |
| 28 | Bài 79 | `GT1_C2_03_T10_Counterexample_Improper_Integral` |
| 29 | Bài 81a | `GT1_C2_04_T01_Area_Plane_Region` |
| 30 | Bài 84 | `GT1_C2_04_T04_Volume_Of_Revolution` |
| 31 | Bài 87a | `GT1_C3_01_T01_Domain_Of_Multivariable_Function` |
| 32 | Bài 88a | `GT1_C3_01_T07_Multivariable_Function_Composition` |
| 33 | Bài 89a | `GT1_C3_01_T04_Path_Dependent_Limit` |
| 34 | Bài 91 | `GT1_C3_01_T08_Iterated_And_Joint_Limit` |
| 35 | Bài 92a | `GT1_C3_02_T01_First_Order_Partial_Derivative` |
| 36 | Bài 93a | `GT1_C3_02_T10_Continuity_And_Partial_Derivative_Existence` |
| 37 | Bài 95a | `GT1_C3_02_T04_Multivariable_Chain_Rule` |
| 38 | Bài 96 | `GT1_C3_02_T12_Partial_Differential_Equation_Verification` |
| 39 | Bài 98a | `GT1_C3_02_T03_Approximation_By_Differential` |
| 40 | Bài 100b | `GT1_C3_02_T08_Implicit_Function_Derivative` |
| 41 | Bài 105a | `GT1_C3_02_T05_Higher_Order_Partial_Derivative` |
| 42 | Bài 107 | `GT1_C3_02_T06_Schwarz_Theorem` |
| 43 | Bài 108 | `GT1_C3_02_T09_Multivariable_Taylor` |
| 44 | Bài 109a | `GT1_C3_03_T02_Unconstrained_Extrema` |
| 45 | Bài 110 | `GT1_C3_03_T04_Constrained_Extrema` |
| 46 | Bài 111a | `GT1_C3_03_T06_Global_Maximum_Minimum` |

### 17.3. Chỉ số đánh giá

Nên báo cáo các chỉ số:

```text
chapter_accuracy = số câu đúng chapter / tổng số câu
topic_accuracy = số câu đúng topic / tổng số câu
subtopic_accuracy = số câu đúng subtopic / tổng số câu
difficulty_accuracy = số câu đúng difficulty / tổng số câu
low_confidence_rate = số câu confidence < 0.65 / tổng số câu
invalid_code_rate = số câu trả mã không tồn tại / tổng số câu
```

Mục tiêu MVP:

```text
chapter_accuracy >= 95%
topic_accuracy >= 85%
subtopic_accuracy >= 75%
invalid_code_rate = 0%
```

Mục tiêu bản tốt:

```text
chapter_accuracy >= 98%
topic_accuracy >= 90%
subtopic_accuracy >= 82%
invalid_code_rate = 0%
```

## 18. Cải tiến tiếp theo để production-ready

Để bộ não tri thức tiến gần production hơn, nên tách thêm một bản dữ liệu máy đọc được:

```text
Plan/update/taxonomy_giai_tich_1.yaml
```

Mỗi node nên có dạng:

```yaml
code: GT1_C2_01_T03_Integration_By_Parts
display_name: Tích phân từng phần
level: subtopic
parent: GT1_C2_01_Indefinite_Integrals
aliases:
  - tích phân từng phần
  - từng phần
positive_signals:
  - tích của đa thức với logarit
  - tích của đa thức với hàm mũ
skills:
  - integration_by_parts
  - indefinite_integral
default_difficulty: medium
confusable_with:
  - GT1_C2_01_T02_Substitution_Method
examples:
  - statement: "Tính int (x+2)ln x dx."
    expected_difficulty: medium
```

Bản Markdown hiện tại dùng tốt cho con người, báo cáo và prompt. Bản YAML/JSON sẽ tốt hơn cho backend, kiểm thử và UI.
