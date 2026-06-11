# Bước 3 - Trích dạng bài thực tế từ bộ bài tập MI1111

Nguồn xử lý:

```text
Giải tích 1/Đề cương/2025.1_BTTK_MI1111.md
```

Mục tiêu của bước này:

- Đọc bộ bài tập theo đề cương.
- Rút ra các dạng bài thật sự xuất hiện.
- Map từng cụm bài vào taxonomy đã chốt ở bước 1 và bước 2.
- Xác định các dạng bài cần có trong "bộ não tri thức" để AI Matching hoạt động sát với môn Giải tích 1.

Kết quả đọc tài liệu:

- Tổng số bài: 111 bài.
- Chương 1: Bài 1 đến Bài 56.
- Chương 2: Bài 57 đến Bài 86.
- Chương 3: Bài 87 đến Bài 111.

## 1. Kết luận nhanh

Bộ bài tập xác nhận rằng taxonomy chính nên bám rất sát cấu trúc đề cương:

```text
Giải tích 1
├── Chương 1: Phép tính vi phân hàm một biến số
├── Chương 2: Phép tính tích phân hàm một biến số
└── Chương 3: Hàm số nhiều biến số
```

Bộ bài tập cũng xác nhận một số điểm quan trọng:

- Tích phân từng phần là dạng bài thực tế rõ ràng, dù đề cương ảnh không tách thành mục riêng.
- Đạo hàm hàm ngược, vi phân, đạo hàm cấp cao đều có bài riêng.
- Taylor/Maclaurin là dạng bài quan trọng.
- L'Hospital xuất hiện qua nhóm bài tính giới hạn trong mục 1.9.
- Tích phân suy rộng có nhiều bài về hội tụ, phân kỳ, tiêu chuẩn so sánh và điều kiện tham số.
- Chương 3 có đầy đủ các dạng: miền xác định, giới hạn nhiều biến, liên tục, đạo hàm riêng, hàm hợp, vi phân, hàm ẩn, đạo hàm cấp cao, Taylor nhiều biến, cực trị và GTLN/GTNN.
- Bài tập không thể hiện rõ dạng nhân tử Lagrange bằng tên gọi, nhưng Bài 110 là cực trị có điều kiện trên elip, có thể giải bằng tham số hóa hoặc Lagrange. Taxonomy nên giữ `Lagrange_Multiplier` như dạng bài có điều kiện, nhưng đánh dấu là "nếu phương pháp được dùng".

## 2. Chương 1 - Phép tính vi phân hàm một biến số

### 2.1. Mục 1.1-1.4 - Dãy số, hàm số

Nguồn bài tập:

```text
Bài 1 -> Bài 9
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 1 | Tìm tập xác định của hàm số | `GT1_C1_02_Function_Basics` | `GT1_C1_02_T01_Domain_And_Range` |
| 2 | Chứng minh đẳng thức hyperbolic | `GT1_C1_03_Elementary_Functions` | `GT1_C1_03_T03_Hyperbolic_Function` |
| 3 | Tìm miền giá trị của hàm số | `GT1_C1_02_Function_Basics` | `GT1_C1_02_T01_Domain_And_Range` |
| 4 | Lập hàm số mô tả tiền điện theo bậc thang | `GT1_C1_02_Function_Basics` | `GT1_C1_02_T05_Piecewise_Function_Modeling` |
| 5 | Xét tính chẵn lẻ | `GT1_C1_02_Function_Basics` | `GT1_C1_02_T02_Monotonicity_Boundedness_Parity` |
| 6 | Tính hàm hợp, tìm hàm thỏa điều kiện hợp | `GT1_C1_02_Function_Basics` | `GT1_C1_02_T03_Function_Composition` |
| 7 | Tìm hàm ngược | `GT1_C1_02_Function_Basics` | `GT1_C1_02_T04_Inverse_Function` |
| 8 | Xét tính tuần hoàn và chu kỳ | `GT1_C1_02_Function_Basics` | `GT1_C1_02_T06_Periodicity` |
| 9 | Xét hội tụ và tìm giới hạn dãy số | `GT1_C1_04_Sequences` | `GT1_C1_04_T01_Compute_Sequence_Limit` |

Dạng bài cần bổ sung so với bước 2:

```text
GT1_C1_02_T05_Piecewise_Function_Modeling
GT1_C1_02_T06_Periodicity
```

Nhận xét:

- Phần hàm số không chỉ có bài lý thuyết mà còn có bài mô hình hóa hàm từng khúc qua bảng giá điện.
- AI classifier cần nhận diện các cụm từ như "viết hàm số", "biểu diễn", "theo bậc", "theo khoảng" để match vào dạng mô hình hóa/hàm từng khúc.

### 2.2. Mục 1.5-1.6 - Giới hạn hàm số

Nguồn bài tập:

```text
Bài 10 -> Bài 14
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 10 | Tính giới hạn bằng định nghĩa | `GT1_C1_05_Function_Limits` | `GT1_C1_05_T07_Proof_By_Definition` |
| 11 | Tính các giới hạn cơ bản, vô cực, một phía, dao động | `GT1_C1_05_Function_Limits` | `GT1_C1_05_T02_Algebraic_Transformation_Limit`, `GT1_C1_05_T03_One_Sided_Limit`, `GT1_C1_05_T04_Limit_At_Infinity` |
| 12 | Hàm từng phần, giới hạn và hành vi gần điểm đặc biệt | `GT1_C1_05_Function_Limits` | `GT1_C1_05_T08_Piecewise_Function_Limit` |
| 13 | So sánh các cặp vô cùng bé | `GT1_C1_06_Infinitesimal_Infinite` | `GT1_C1_06_T01_Compare_Infinitesimal` |
| 14 | Tính giới hạn bằng VCB/VCL và biến đổi | `GT1_C1_06_Infinitesimal_Infinite` | `GT1_C1_06_T02_Equivalent_Infinitesimal`, `GT1_C1_06_T04_Asymptotic_Simplification` |

Dạng bài cần bổ sung:

```text
GT1_C1_05_T08_Piecewise_Function_Limit
```

Dấu hiệu nhận diện:

- "bằng định nghĩa" -> proof by definition.
- "so sánh các cặp VCB" -> compare infinitesimal.
- Các biểu thức chứa căn, log, lượng giác, hàm mũ gần 0 -> thường là biến đổi giới hạn hoặc VCB tương đương.

### 2.3. Mục 1.7 - Hàm số liên tục

Nguồn bài tập:

```text
Bài 15 -> Bài 23
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 15 | Xác định và phân loại điểm gián đoạn | `GT1_C1_07_Continuity` | `GT1_C1_07_T05_Classify_Discontinuity` |
| 16 | Tìm tham số để liên tục tại điểm | `GT1_C1_07_Continuity` | `GT1_C1_07_T04_Find_Parameter_For_Continuity` |
| 17 | Xác định các điểm liên tục của hàm | `GT1_C1_07_Continuity` | `GT1_C1_07_T01_Continuity_At_Point` |
| 18 | Phân loại điểm gián đoạn | `GT1_C1_07_Continuity` | `GT1_C1_07_T05_Classify_Discontinuity` |
| 19 | Tìm tham số để điểm là gián đoạn theo loại yêu cầu | `GT1_C1_07_Continuity` | `GT1_C1_07_T07_Parameter_For_Discontinuity_Type` |
| 20 | Chứng minh phương trình có nghiệm bằng liên tục | `GT1_C1_07_Continuity` | `GT1_C1_07_T06_Use_Continuity_Theorems` |
| 21 | Ví dụ phản ví dụ về hàm liên tục và GTLN/GTNN | `GT1_C1_07_Continuity` | `GT1_C1_07_T08_Construct_Continuity_Counterexample` |
| 22 | Tính giới hạn liên quan liên tục/điểm đặc biệt | `GT1_C1_05_Function_Limits` hoặc `GT1_C1_07_Continuity` | `GT1_C1_05_T02_Algebraic_Transformation_Limit` |
| 23 | Bài toán giao điểm dựa trên định lý giá trị trung gian | `GT1_C1_07_Continuity` | `GT1_C1_07_T06_Use_Continuity_Theorems` |

Dạng bài cần bổ sung:

```text
GT1_C1_07_T07_Parameter_For_Discontinuity_Type
GT1_C1_07_T08_Construct_Continuity_Counterexample
```

Nhận xét:

- Mục liên tục có nhiều bài proof/application hơn chỉ "xét liên tục".
- AI Matching cần phân biệt:
  - tìm tham số để liên tục
  - phân loại gián đoạn
  - dùng định lý giá trị trung gian
  - dựng ví dụ/phản ví dụ

### 2.4. Mục 1.8 - Đạo hàm và vi phân

Nguồn bài tập:

```text
Bài 24 -> Bài 35
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 24 | Tìm đạo hàm | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T01_Basic_Derivative` |
| 25 | Tìm `f'(x)` từ biểu thức/quan hệ | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T01_Basic_Derivative` |
| 26 | Tìm tham số để liên tục, khả vi, đạo hàm có tính chất tại điểm | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T03_Derivative_Existence`, `GT1_C1_08_T10_Parameter_For_Differentiability` |
| 27 | Tính đạo hàm hàm hợp/phức hợp | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T04_Chain_Rule` |
| 28 | Đạo hàm hàm ngược | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T05_Inverse_Function_Derivative` |
| 29 | Chứng minh hàm không khả vi tại điểm | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T03_Derivative_Existence` |
| 30 | Tìm vi phân | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T06_Differential` |
| 31 | Bài toán liên quan vi phân/đạo hàm | `GT1_C1_08_Derivatives_Differentials` | Cần xem chi tiết khi xây ví dụ |
| 32 | Dùng vi phân tính gần đúng | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T07_Linear_Approximation` |
| 33 | Đạo hàm cấp cao | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T08_Higher_Order_Derivative` |
| 34 | Đạo hàm cấp `n` | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T11_Nth_Derivative` |
| 35 | Vi phân cấp cao | `GT1_C1_08_Derivatives_Differentials` | `GT1_C1_08_T09_Higher_Order_Differential` |

Dạng bài cần bổ sung:

```text
GT1_C1_08_T10_Parameter_For_Differentiability
GT1_C1_08_T11_Nth_Derivative
```

Nhận xét:

- Phần này có nhiều bài kiểm tra điều kiện tồn tại đạo hàm/khả vi tại điểm, không chỉ tính đạo hàm.
- Nên để AI ưu tiên nhận diện các từ khóa: "khả vi", "liên tục tại", "không khả vi", "đạo hàm cấp n".

### 2.5. Mục 1.9 - Các định lý về hàm khả vi và ứng dụng

Nguồn bài tập:

```text
Bài 36 -> Bài 54
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 36-39 | Chứng minh phương trình/nghiệm/điều kiện bằng định lý hàm khả vi | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T01_Fermat_Rolle_Lagrange_Cauchy`, `GT1_C1_09_T02_Proof_Using_Mean_Value_Theorem` |
| 40-41 | Chứng minh bất đẳng thức hoặc chứng minh không tồn tại hàm | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T02_Proof_Using_Mean_Value_Theorem` |
| 42 | Bài tham số/điều kiện liên quan đạo hàm hoặc định lý | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T10_Parameter_Problem_Differentiable_Theorem` |
| 43-44 | Tính giới hạn bằng công cụ mục 1.9 | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T05_LHopital_Rule`, `GT1_C1_09_T04_Limit_By_Taylor` |
| 45-46 | Bài về hàm số/định lý/tính chất nâng cao | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | Cần đưa vào nhóm proof/analysis |
| 47 | Khai triển Maclaurin đến cấp 4 | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T03_Taylor_Maclaurin_Expansion` |
| 48 | Khai triển Taylor đến cấp 4 | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T03_Taylor_Maclaurin_Expansion` |
| 49 | Phân tích phân thức và đạo hàm cấp cao | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T11_Partial_Fraction_And_Nth_Derivative` |
| 50 | Tìm tham số để giới hạn hữu hạn | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T10_Parameter_Problem_Differentiable_Theorem` |
| 51 | Khảo sát tính đơn điệu | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T06_Monotonicity_By_Derivative` |
| 52 | Chứng minh bất đẳng thức | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T07_Convexity_Concavity`, `GT1_C1_09_T02_Proof_Using_Mean_Value_Theorem` |
| 53 | Tìm GTLN/GTNN trên đoạn | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T12_Max_Min_On_Closed_Interval` |
| 54 | Tìm cực trị hàm một biến | `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | `GT1_C1_09_T08_One_Variable_Extrema` |

Dạng bài cần bổ sung:

```text
GT1_C1_09_T10_Parameter_Problem_Differentiable_Theorem
GT1_C1_09_T11_Partial_Fraction_And_Nth_Derivative
GT1_C1_09_T12_Max_Min_On_Closed_Interval
```

Nhận xét:

- Đây là cụm khó nhất của chương 1 vì nhiều bài proof/parameter.
- Difficulty mặc định:
  - Tính Taylor/Maclaurin cơ bản: `medium`
  - L'Hospital trực tiếp: `medium`
  - Chứng minh bằng định lý giá trị trung bình: `hard`
  - Bài tham số/điều kiện: `hard`

### 2.6. Mục 1.10 - Khảo sát hàm số, đường cong

Nguồn bài tập:

```text
Bài 55 -> Bài 56
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 55 | Tìm tiệm cận của đường cong | `GT1_C1_10_Curve_Function_Graph_Survey` | `GT1_C1_10_T02_Asymptote_Analysis` |
| 56 | Mở rộng bài giao điểm cho đường cong tham số | `GT1_C1_10_Curve_Function_Graph_Survey` | `GT1_C1_10_T05_Parametric_Curve`, `GT1_C1_07_T06_Use_Continuity_Theorems` |

Nhận xét:

- Bộ bài tập không có nhiều bài khảo sát toàn bộ đồ thị, nhưng có tiệm cận và đường cong tham số.
- Taxonomy vẫn nên giữ các dạng khảo sát đầy đủ vì đề cương có mục này.

## 3. Chương 2 - Phép tính tích phân hàm một biến số

### 3.1. Mục 2.1 - Tích phân bất định

Nguồn bài tập:

```text
Bài 57 -> Bài 63
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 57 | Tích phân bất định bằng đổi biến | `GT1_C2_01_Indefinite_Integrals` | `GT1_C2_01_T02_Substitution_Method` |
| 58 | Tích phân từng phần | `GT1_C2_01_Indefinite_Integrals` | `GT1_C2_01_T03_Integration_By_Parts` |
| 59 | Tích phân phân thức hữu tỷ | `GT1_C2_01_Indefinite_Integrals` | `GT1_C2_01_T04_Rational_Function_Integral`, `GT1_C2_01_T05_Partial_Fractions` |
| 60 | Tích phân hàm vô tỷ | `GT1_C2_01_Indefinite_Integrals` | `GT1_C2_01_T07_Irrational_Integral` |
| 61 | Tích phân hỗn hợp: đổi biến, từng phần, phân thức, lượng giác, vô tỷ | `GT1_C2_01_Indefinite_Integrals` | `GT1_C2_01_T09_Mixed_Indefinite_Integral_Methods` |
| 62 | Tích phân lượng giác chứa `sin(nx)`, `cos(mx)` | `GT1_C2_01_Indefinite_Integrals` | `GT1_C2_01_T06_Trigonometric_Integral` |
| 63 | Công thức truy hồi cho tích phân | `GT1_C2_01_Indefinite_Integrals` | `GT1_C2_01_T10_Reduction_Formula` |

Dạng bài cần bổ sung:

```text
GT1_C2_01_T09_Mixed_Indefinite_Integral_Methods
GT1_C2_01_T10_Reduction_Formula
```

Nhận xét:

- Tích phân từng phần chắc chắn phải có trong bộ não tri thức.
- Công thức truy hồi là một dạng bài riêng, thường có độ khó `hard` nếu phải thiết lập công thức tổng quát.

### 3.2. Mục 2.2 - Tích phân xác định

Nguồn bài tập:

```text
Bài 64 -> Bài 74
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 64 | Tổng tích phân/Riemann sum | `GT1_C2_02_Definite_Integrals` | `GT1_C2_02_T08_Riemann_Sum_Definition` |
| 65 | Đạo hàm tích phân theo cận | `GT1_C2_02_Definite_Integrals` | `GT1_C2_02_T07_Differentiation_Under_Variable_Limits` |
| 66 | Tính giới hạn bằng tổng tích phân | `GT1_C2_02_Definite_Integrals` | `GT1_C2_02_T09_Limit_As_Definite_Integral` |
| 67-68 | VCB/VCL qua tích phân xác định | `GT1_C2_02_Definite_Integrals` | `GT1_C2_02_T10_Asymptotic_Integral_Function` |
| 69 | Giới hạn có tích phân phụ thuộc cận | `GT1_C2_02_Definite_Integrals` | `GT1_C2_02_T10_Asymptotic_Integral_Function` |
| 70 | Tính tích phân xác định trên đoạn, gồm hàm từng phần | `GT1_C2_02_Definite_Integrals` | `GT1_C2_02_T04_Newton_Leibniz`, `GT1_C2_02_T11_Piecewise_Definite_Integral` |
| 71-72 | Tính tích phân xác định bằng phương pháp phù hợp | `GT1_C2_02_Definite_Integrals` | `GT1_C2_02_T05_Substitution_Definite_Integral`, `GT1_C2_02_T06_By_Parts_Definite_Integral` |
| 73 | Chứng minh và áp dụng tính chất đối xứng tích phân | `GT1_C2_02_Definite_Integrals` | `GT1_C2_02_T12_Symmetry_Property_Definite_Integral` |
| 74 | Bất đẳng thức Cauchy-Schwarz cho tích phân | `GT1_C2_02_Definite_Integrals` | `GT1_C2_02_T13_Integral_Inequality` |

Dạng bài cần bổ sung:

```text
GT1_C2_02_T08_Riemann_Sum_Definition
GT1_C2_02_T09_Limit_As_Definite_Integral
GT1_C2_02_T10_Asymptotic_Integral_Function
GT1_C2_02_T11_Piecewise_Definite_Integral
GT1_C2_02_T12_Symmetry_Property_Definite_Integral
GT1_C2_02_T13_Integral_Inequality
```

Nhận xét:

- Mục tích phân xác định không chỉ là tính tích phân.
- Có các dạng rất đặc trưng: tổng Riemann, giới hạn chuyển thành tích phân, tích phân có cận biến thiên, bất đẳng thức tích phân.

### 3.3. Mục 2.3 - Tích phân suy rộng

Nguồn bài tập:

```text
Bài 75 -> Bài 80
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 75 | Xét hội tụ và tính giá trị tích phân suy rộng | `GT1_C2_03_Improper_Integrals` | `GT1_C2_03_T03_Compute_Improper_Integral`, `GT1_C2_03_T04_Convergence_Divergence` |
| 76 | Xét hội tụ của nhiều tích phân suy rộng | `GT1_C2_03_Improper_Integrals` | `GT1_C2_03_T04_Convergence_Divergence`, `GT1_C2_03_T05_Comparison_Test` |
| 77 | Khảo sát hội tụ theo tham số `alpha`, `beta` | `GT1_C2_03_Improper_Integrals` | `GT1_C2_03_T08_Parameter_Improper_Integral` |
| 78 | Chứng minh điều kiện hội tụ khi và chỉ khi | `GT1_C2_03_Improper_Integrals` | `GT1_C2_03_T08_Parameter_Improper_Integral`, `GT1_C2_03_T09_Proof_Improper_Integral_Condition` |
| 79 | Phản ví dụ/điều kiện cần về giới hạn hàm dưới dấu tích phân | `GT1_C2_03_Improper_Integrals` | `GT1_C2_03_T10_Counterexample_Improper_Integral` |
| 80 | Điều kiện phân kỳ khi giới hạn hàm khác 0 | `GT1_C2_03_Improper_Integrals` | `GT1_C2_03_T09_Proof_Improper_Integral_Condition` |

Dạng bài cần bổ sung:

```text
GT1_C2_03_T08_Parameter_Improper_Integral
GT1_C2_03_T09_Proof_Improper_Integral_Condition
GT1_C2_03_T10_Counterexample_Improper_Integral
```

Nhận xét:

- Tích phân suy rộng trong bộ bài tập có độ lý thuyết khá cao.
- Các bài tham số và phản ví dụ nên mặc định là `hard`.

### 3.4. Mục 2.4 - Ứng dụng của tích phân xác định

Nguồn bài tập:

```text
Bài 81 -> Bài 86
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 81 | Diện tích hình phẳng | `GT1_C2_04_Applications_Definite_Integrals` | `GT1_C2_04_T01_Area_Plane_Region` |
| 82 | Thể tích vật thể là phần chung hai hình trụ | `GT1_C2_04_Applications_Definite_Integrals` | `GT1_C2_04_T03_Volume_Of_Solid` |
| 83 | Thể tích vật thể giới hạn bởi mặt cong/mặt phẳng | `GT1_C2_04_Applications_Definite_Integrals` | `GT1_C2_04_T03_Volume_Of_Solid` |
| 84 | Thể tích khối tròn xoay quanh trục | `GT1_C2_04_Applications_Definite_Integrals` | `GT1_C2_04_T04_Volume_Of_Revolution` |
| 85 | Độ dài cung phẳng, cả dạng tham số | `GT1_C2_04_Applications_Definite_Integrals` | `GT1_C2_04_T02_Arc_Length` |
| 86 | Diện tích mặt tròn xoay | `GT1_C2_04_Applications_Definite_Integrals` | `GT1_C2_04_T05_Surface_Area_Of_Revolution` |

Nhận xét:

- Các bài ứng dụng đều có dấu hiệu nhận diện rõ qua từ khóa "diện tích", "thể tích", "tròn xoay", "độ dài", "mặt tròn xoay".
- Đây là nhóm dễ match bằng keyword + công thức.

## 4. Chương 3 - Hàm số nhiều biến số

### 4.1. Mục 3.1 - Các khái niệm cơ bản

Nguồn bài tập:

```text
Bài 87 -> Bài 91
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 87 | Tìm miền xác định hàm nhiều biến | `GT1_C3_01_Multivariable_Basics` | `GT1_C3_01_T01_Domain_Of_Multivariable_Function` |
| 88 | Tính hàm hợp nhiều biến | `GT1_C3_01_Multivariable_Basics` | `GT1_C3_01_T07_Multivariable_Function_Composition` |
| 89 | Tìm giới hạn hàm nhiều biến | `GT1_C3_01_Multivariable_Basics` | `GT1_C3_01_T03_Multivariable_Limit`, `GT1_C3_01_T04_Path_Dependent_Limit` |
| 90 | Xét liên tục của hàm nhiều biến từng phần | `GT1_C3_01_Multivariable_Basics` | `GT1_C3_01_T05_Multivariable_Continuity` |
| 91 | So sánh giới hạn lặp và giới hạn hai biến | `GT1_C3_01_Multivariable_Basics` | `GT1_C3_01_T08_Iterated_And_Joint_Limit` |

Dạng bài cần bổ sung:

```text
GT1_C3_01_T07_Multivariable_Function_Composition
GT1_C3_01_T08_Iterated_And_Joint_Limit
```

### 4.2. Mục 3.2 - Đạo hàm riêng và vi phân

Nguồn bài tập:

```text
Bài 92 -> Bài 108
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 92 | Tính đạo hàm riêng | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T01_First_Order_Partial_Derivative` |
| 93 | Khảo sát liên tục và tồn tại đạo hàm riêng | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T10_Continuity_And_Partial_Derivative_Existence` |
| 94 | Chứng minh đẳng thức chứa đạo hàm riêng | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T11_Identity_With_Partial_Derivatives` |
| 95 | Đạo hàm riêng hàm hợp | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T04_Multivariable_Chain_Rule` |
| 96 | Chứng minh phương trình đạo hàm riêng | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T12_Partial_Differential_Equation_Verification` |
| 97 | Vi phân toàn phần | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T02_Total_Differential` |
| 98 | Ứng dụng vi phân tính gần đúng | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T03_Approximation_By_Differential` |
| 99 | Vi phân hàm ẩn để tính gần đúng | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T08_Implicit_Function_Derivative`, `GT1_C3_02_T03_Approximation_By_Differential` |
| 100-104 | Đạo hàm hàm ẩn một biến/nhiều biến/hệ hàm ẩn | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T08_Implicit_Function_Derivative` |
| 105 | Đạo hàm riêng cấp hai | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T05_Higher_Order_Partial_Derivative` |
| 106 | Vi phân cấp hai | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T13_Second_Order_Differential` |
| 107 | Đạo hàm riêng cấp hai không liên tục, thứ tự đạo hàm hỗn hợp | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T06_Schwarz_Theorem` |
| 108 | Taylor/Maclaurin nhiều biến | `GT1_C3_02_Partial_Derivatives_Differentials` | `GT1_C3_02_T09_Multivariable_Taylor` |

Dạng bài cần bổ sung:

```text
GT1_C3_02_T10_Continuity_And_Partial_Derivative_Existence
GT1_C3_02_T11_Identity_With_Partial_Derivatives
GT1_C3_02_T12_Partial_Differential_Equation_Verification
GT1_C3_02_T13_Second_Order_Differential
```

Nhận xét:

- Bài tập chương 3 phần đạo hàm riêng phong phú hơn đề cương ngắn gọn.
- AI cần nhận diện các mẫu "chứng minh rằng biểu thức đạo hàm thỏa mãn..." và "phương trình truyền sóng" để không nhầm sang topic khác.

### 4.3. Mục 3.3 - Cực trị của hàm số nhiều biến số

Nguồn bài tập:

```text
Bài 109 -> Bài 111
```

| Bài | Nội dung thực tế | Taxonomy topic | Dạng bài taxonomy |
| --- | --- | --- | --- |
| 109 | Tìm cực trị hàm nhiều biến | `GT1_C3_03_Multivariable_Extrema` | `GT1_C3_03_T02_Unconstrained_Extrema`, `GT1_C3_03_T03_Hessian_Test` |
| 110 | Tìm điểm trên elip xa điểm cho trước nhất | `GT1_C3_03_Multivariable_Extrema` | `GT1_C3_03_T04_Constrained_Extrema`, `GT1_C3_03_T05_Lagrange_Multiplier` |
| 111 | Tìm GTLN/GTNN trên miền đóng bị chặn | `GT1_C3_03_Multivariable_Extrema` | `GT1_C3_03_T06_Global_Maximum_Minimum` |

Nhận xét:

- Dạng `Lagrange_Multiplier` nên được giữ trong taxonomy vì Bài 110 là dạng cực trị có điều kiện.
- Nếu slide không dùng tên Lagrange, có thể hiển thị tiếng Việt là "Cực trị có điều kiện", còn code vẫn giữ `Lagrange_Multiplier` như phương pháp.

## 5. Danh sách dạng bài mới cần đưa vào bộ não tri thức

So với bước 2, bộ bài tập yêu cầu bổ sung các dạng sau:

### Chương 1

```text
GT1_C1_02_T05_Piecewise_Function_Modeling
GT1_C1_02_T06_Periodicity
GT1_C1_05_T08_Piecewise_Function_Limit
GT1_C1_07_T07_Parameter_For_Discontinuity_Type
GT1_C1_07_T08_Construct_Continuity_Counterexample
GT1_C1_08_T10_Parameter_For_Differentiability
GT1_C1_08_T11_Nth_Derivative
GT1_C1_09_T10_Parameter_Problem_Differentiable_Theorem
GT1_C1_09_T11_Partial_Fraction_And_Nth_Derivative
GT1_C1_09_T12_Max_Min_On_Closed_Interval
```

### Chương 2

```text
GT1_C2_01_T09_Mixed_Indefinite_Integral_Methods
GT1_C2_01_T10_Reduction_Formula
GT1_C2_02_T08_Riemann_Sum_Definition
GT1_C2_02_T09_Limit_As_Definite_Integral
GT1_C2_02_T10_Asymptotic_Integral_Function
GT1_C2_02_T11_Piecewise_Definite_Integral
GT1_C2_02_T12_Symmetry_Property_Definite_Integral
GT1_C2_02_T13_Integral_Inequality
GT1_C2_03_T08_Parameter_Improper_Integral
GT1_C2_03_T09_Proof_Improper_Integral_Condition
GT1_C2_03_T10_Counterexample_Improper_Integral
```

### Chương 3

```text
GT1_C3_01_T07_Multivariable_Function_Composition
GT1_C3_01_T08_Iterated_And_Joint_Limit
GT1_C3_02_T10_Continuity_And_Partial_Derivative_Existence
GT1_C3_02_T11_Identity_With_Partial_Derivatives
GT1_C3_02_T12_Partial_Differential_Equation_Verification
GT1_C3_02_T13_Second_Order_Differential
```

## 6. Gợi ý độ khó mặc định theo dạng bài

### easy

Các dạng thường là `easy` nếu đề bài chỉ yêu cầu áp dụng công thức trực tiếp:

- Tìm tập xác định cơ bản.
- Tính đạo hàm cơ bản.
- Tính vi phân trực tiếp.
- Tính nguyên hàm cơ bản.
- Tính đạo hàm riêng cấp một trực tiếp.
- Tính miền xác định hàm nhiều biến đơn giản.

### medium

Các dạng thường là `medium` nếu cần chọn phương pháp và biến đổi vài bước:

- Tính giới hạn bằng biến đổi đại số.
- Dùng VCB tương đương.
- Xét liên tục hàm từng phần.
- Tính đạo hàm hàm hợp.
- Đạo hàm hàm ngược.
- Tích phân đổi biến.
- Tích phân từng phần.
- Tích phân phân thức hữu tỷ.
- Tính tích phân xác định bằng phương pháp phù hợp.
- Tính đạo hàm hàm ẩn.
- Tìm cực trị tự do nhiều biến.

### hard

Các dạng thường là `hard` nếu cần biện luận, chia trường hợp, tham số, chứng minh hoặc kết hợp nhiều kiến thức:

- Chứng minh bằng định lý Rolle/Lagrange/Cauchy.
- Bài tham số để liên tục/khả vi/giới hạn hữu hạn.
- Dựng phản ví dụ.
- Chứng minh bất đẳng thức.
- Khai triển Taylor/Maclaurin có yêu cầu cao.
- Công thức truy hồi tích phân.
- Tích phân suy rộng có tham số.
- Bài hội tụ suy rộng dạng chứng minh điều kiện cần và đủ.
- Bài về đạo hàm riêng cấp hai không liên tục hoặc định lý Schwarz.
- Cực trị có điều kiện.
- Tìm GTLN/GTNN trên miền đóng có biên.

## 7. Ví dụ matching mẫu từ bộ bài tập

### Ví dụ 1

Câu hỏi:

```text
Tìm tập xác định của y = sqrt[4]((2x-1)/(1+3x)).
```

Kết quả match:

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

Kết quả match:

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
Khảo sát sự hội tụ của tích phân suy rộng ∫_0^1 x^alpha (ln x)^beta dx.
```

Kết quả match:

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

Kết quả match:

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

## 8. Kết luận bước 3

Bộ bài tập `2025.1_BTTK_MI1111.md` đã xác nhận và làm giàu đáng kể taxonomy.

Sau bước này, "bộ não tri thức" không nên chỉ là cây chương/mục từ đề cương, mà cần có tầng thứ ba là **dạng bài thực tế**.

Cấu trúc mục tiêu:

```text
Chương -> Chủ đề -> Dạng bài -> dấu hiệu nhận diện -> skills -> difficulty mặc định -> ví dụ
```

Bước tiếp theo nên là:

```text
Bước 4 - Viết lại Plan/calculus_knowledge_taxonomy.md thành bộ não tri thức chính thức cho Giải tích 1
```

