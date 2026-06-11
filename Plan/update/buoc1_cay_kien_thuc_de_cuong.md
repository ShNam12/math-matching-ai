# Bước 1 - Cây kiến thức Giải tích 1 theo đề cương

Mục tiêu của bước này là chốt khung kiến thức chính thức của môn **Giải tích 1** dựa trên đề cương học phần và ảnh nội dung đề cương do người dùng cung cấp.

Thông tin phạm vi:

- Môn học: Giải tích 1
- Đối tượng: Sinh viên ngành Toán Tin, Đại học Bách Khoa Hà Nội
- Mức phân loại mong muốn: chương + chủ đề + dạng bài
- Cách gọi tên: bám theo đề cương, giáo trình và slide bài giảng
- Rubric độ khó:
  - `easy`: áp dụng trực tiếp công thức
  - `medium`: cần chọn phương pháp và biến đổi vài bước
  - `hard`: cần biện luận, chia trường hợp, tham số, chứng minh hoặc kết hợp nhiều kiến thức

## 1. Cấu trúc chương chính thức

Theo đề cương, môn Giải tích 1 gồm 3 chương chính:

```text
Giải tích 1
├── Chương 1: Phép tính vi phân hàm một biến số
├── Chương 2: Phép tính tích phân hàm một biến số
└── Chương 3: Hàm số nhiều biến số
```

Ghi chú quan trọng:

- Các nội dung như chuỗi số, chuỗi hàm, Taylor nâng cao theo chuỗi, Fourier không nằm trong khung đề cương Giải tích 1 này ở bước 1.
- Vì vậy bản taxonomy chính thức cho dự án nên ưu tiên 3 chương trên.
- Nếu giáo trình hoặc slide có phần phụ ngoài đề cương, chỉ nên đưa vào mục mở rộng, không nên đặt làm nhánh chính.

## 2. Chương 1 - Phép tính vi phân hàm một biến số

Mã đề xuất:

```text
GT1_C1_Differential_Calculus_One_Variable
```

Tên hiển thị:

```text
Chương 1: Phép tính vi phân hàm một biến số
```

### 1.1. Mở đầu

Mã đề xuất:

```text
GT1_C1_01_Introduction
```

Vai trò:

- Giới thiệu môn học.
- Giới thiệu cách học và phạm vi kiến thức.

Ghi chú:

- Mục này không phải trọng tâm để match bài tập toán.
- Có thể giữ trong taxonomy nhưng không ưu tiên phân loại câu hỏi vào đây.

### 1.2. Hàm số và các khái niệm cơ bản

Mã đề xuất:

```text
GT1_C1_02_Function_Basics
```

Nội dung theo đề cương:

- Định nghĩa hàm số.
- Một số khái niệm cơ bản về hàm số.
- Hàm hợp.
- Hàm ngược.

Dạng bài dự kiến:

- Xác định tập xác định của hàm số.
- Xác định tập giá trị.
- Xét tính chẵn, lẻ, tuần hoàn, bị chặn nếu có.
- Tìm hàm hợp.
- Tìm hàm ngược.
- Kiểm tra điều kiện tồn tại hàm ngược.

Kỹ năng gợi ý:

- `function_domain_range`
- `function_composition`
- `inverse_function`
- `algebraic_transformation`

### 1.3. Các hàm số sơ cấp

Mã đề xuất:

```text
GT1_C1_03_Elementary_Functions
```

Nội dung theo đề cương:

- Các hàm số sơ cấp cơ bản.
- Hàm lượng giác ngược.
- Hàm hyperbolic.
- Khái niệm hàm sơ cấp.

Dạng bài dự kiến:

- Nhận diện hàm sơ cấp.
- Biến đổi hàm lượng giác ngược.
- Tính giá trị hoặc rút gọn biểu thức chứa hàm sơ cấp.
- Xét tính chất cơ bản của hàm sơ cấp.

Kỹ năng gợi ý:

- `elementary_functions`
- `inverse_trigonometric_functions`
- `hyperbolic_functions`
- `algebraic_transformation`

### 1.4. Dãy số

Mã đề xuất:

```text
GT1_C1_04_Sequences
```

Nội dung theo đề cương:

- Định nghĩa dãy số.
- Các khái niệm cơ bản.
- Các tiêu chuẩn tồn tại giới hạn:
  - tiêu chuẩn kẹp
  - tiêu chuẩn đơn điệu bị chặn
  - tiêu chuẩn Cauchy

Dạng bài dự kiến:

- Tính giới hạn dãy số.
- Chứng minh dãy hội tụ.
- Dùng tiêu chuẩn kẹp.
- Dùng tiêu chuẩn đơn điệu bị chặn.
- Dùng tiêu chuẩn Cauchy.
- Xét dãy truy hồi nếu xuất hiện trong bài tập.

Kỹ năng gợi ý:

- `sequence_limit`
- `squeeze_theorem`
- `monotone_bounded_sequence`
- `cauchy_criterion`
- `proof`

### 1.5. Giới hạn hàm số

Mã đề xuất:

```text
GT1_C1_05_Function_Limits
```

Nội dung theo đề cương:

- Hai định nghĩa tương đương của giới hạn hàm số.
- Các phép toán và tính chất của giới hạn.
- Giới hạn của hàm hợp.
- Giới hạn một phía.
- Giới hạn ở cực.
- Giới hạn vô cực.

Dạng bài dự kiến:

- Tính giới hạn trực tiếp.
- Tính giới hạn bằng biến đổi đại số.
- Tính giới hạn một phía.
- Tính giới hạn hàm hợp.
- Tính giới hạn tại vô cực.
- Tính giới hạn vô cực.
- Chứng minh giới hạn bằng định nghĩa nếu có.

Kỹ năng gợi ý:

- `function_limit`
- `one_sided_limit`
- `infinite_limit`
- `limit_at_infinity`
- `algebraic_transformation`
- `proof`

### 1.6. Vô cùng bé, vô cùng lớn

Mã đề xuất:

```text
GT1_C1_06_Infinitesimal_Infinite
```

Nội dung theo đề cương:

- Vô cùng bé.
- Vô cùng lớn.
- So sánh các vô cùng bé, vô cùng lớn.
- Các tính chất và quy tắc ngắt bỏ vô cùng bé, vô cùng lớn.

Dạng bài dự kiến:

- So sánh cấp vô cùng bé.
- So sánh cấp vô cùng lớn.
- Tìm vô cùng bé tương đương.
- Tính giới hạn bằng vô cùng bé tương đương.
- Rút gọn giới hạn bằng quy tắc ngắt bỏ.

Kỹ năng gợi ý:

- `infinitesimal_equivalent`
- `infinite_comparison`
- `asymptotic_comparison`
- `limit_computation`

### 1.7. Hàm số liên tục

Mã đề xuất:

```text
GT1_C1_07_Continuity
```

Nội dung theo đề cương:

- Hàm số liên tục một phía.
- Hàm số liên tục tại một điểm.
- Các tính chất của hàm liên tục.
- Điểm gián đoạn của hàm số.
- Phân loại điểm gián đoạn.
- Hàm liên tục từng khúc.

Dạng bài dự kiến:

- Xét tính liên tục tại một điểm.
- Xét tính liên tục trên khoảng hoặc đoạn.
- Tìm tham số để hàm liên tục.
- Xét liên tục của hàm từng phần.
- Phân loại điểm gián đoạn.
- Dùng tính chất hàm liên tục để chứng minh tồn tại nghiệm nếu có.

Kỹ năng gợi ý:

- `continuity_analysis`
- `piecewise_function`
- `discontinuity_classification`
- `parameter_analysis`
- `proof`

### 1.8. Đạo hàm và vi phân

Mã đề xuất:

```text
GT1_C1_08_Derivatives_Differentials
```

Nội dung theo đề cương:

- Một số khái niệm cơ bản.
- Đạo hàm một phía.
- Mối quan hệ giữa đạo hàm một phía và đạo hàm.
- Mối quan hệ giữa đạo hàm và liên tục.
- Đạo hàm của hàm hợp.
- Đạo hàm của hàm số ngược.
- Vi phân:
  - định nghĩa
  - ý nghĩa hình học
  - ứng dụng vi phân để tính gần đúng
  - mối liên hệ giữa hàm có đạo hàm và hàm khả vi
  - vi phân của hàm hợp
  - tính bất biến của vi phân cấp một
- Đạo hàm và vi phân cấp cao.

Dạng bài dự kiến:

- Tính đạo hàm bằng công thức cơ bản.
- Tính đạo hàm một phía.
- Xét tồn tại đạo hàm tại một điểm.
- Tính đạo hàm hàm hợp.
- Tính đạo hàm hàm ngược.
- Tính vi phân.
- Dùng vi phân để tính gần đúng.
- Tính đạo hàm cấp cao.
- Tính vi phân cấp cao.

Kỹ năng gợi ý:

- `derivative_computation`
- `one_sided_derivative`
- `chain_rule`
- `inverse_function_derivative`
- `differential`
- `linear_approximation`
- `higher_order_derivative`

### 1.9. Các định lý về hàm khả vi và ứng dụng

Mã đề xuất:

```text
GT1_C1_09_Theorems_Applications_Differentiable_Functions
```

Nội dung theo đề cương:

- Các định lý Fermat, Rolle, Lagrange, Cauchy.
- Công thức khai triển Taylor.
- Công thức khai triển Maclaurin.
- Quy tắc L'Hospital để khử dạng vô định.
- Ứng dụng khai triển hữu hạn để tìm giới hạn.
- Hàm số đơn điệu và các tính chất.
- Bất đẳng thức hàm lồi.
- Cực trị của hàm số.
- Phương pháp Newton.

Dạng bài dự kiến:

- Áp dụng định lý Rolle.
- Áp dụng định lý Lagrange.
- Áp dụng định lý Cauchy.
- Chứng minh bất đẳng thức bằng định lý giá trị trung bình.
- Tính giới hạn bằng L'Hospital.
- Tính giới hạn bằng khai triển Taylor/Maclaurin.
- Xét tính đơn điệu.
- Chứng minh bất đẳng thức hàm lồi.
- Tìm cực trị hàm một biến.
- Dùng phương pháp Newton nếu có bài tập.

Kỹ năng gợi ý:

- `fermat_theorem`
- `rolle_theorem`
- `lagrange_mean_value_theorem`
- `cauchy_mean_value_theorem`
- `taylor_maclaurin_expansion`
- `l_hopital_rule`
- `monotonicity_analysis`
- `convexity_inequality`
- `one_variable_extrema`
- `newton_method`
- `proof`

### 1.10. Khảo sát hàm số, đường cong

Mã đề xuất:

```text
GT1_C1_10_Curve_Function_Graph_Survey
```

Nội dung theo đề cương:

- Khảo sát hàm số `y = f(x)`.
- Đường cong cho dưới dạng tham số.
- Đường cong trong tọa độ cực.

Dạng bài dự kiến:

- Khảo sát và vẽ đồ thị hàm số.
- Tìm tiệm cận.
- Lập bảng biến thiên.
- Xét cực trị, lồi lõm, điểm uốn.
- Khảo sát đường cong tham số.
- Khảo sát đường cong trong tọa độ cực.

Kỹ năng gợi ý:

- `function_graph_survey`
- `asymptote_analysis`
- `monotonicity_analysis`
- `convexity_concavity`
- `parametric_curve`
- `polar_curve`

## 3. Chương 2 - Phép tính tích phân hàm một biến số

Mã đề xuất:

```text
GT1_C2_Integral_Calculus_One_Variable
```

Tên hiển thị:

```text
Chương 2: Phép tính tích phân hàm một biến số
```

### 2.1. Tích phân bất định

Mã đề xuất:

```text
GT1_C2_01_Indefinite_Integrals
```

Nội dung theo đề cương:

- Một số khái niệm cơ bản.
- Tích phân các hàm phân thức hữu tỉ.
- Tích phân các hàm vô tỉ.
- Tích phân các hàm lượng giác.
- Một số ví dụ đơn giản về phép đổi biến Euler.

Dạng bài dự kiến:

- Tính nguyên hàm cơ bản.
- Tính tích phân bằng đổi biến.
- Tính tích phân từng phần nếu xuất hiện trong slide/bài tập.
- Tích phân hàm phân thức hữu tỉ.
- Phân tích phân thức hữu tỉ.
- Tích phân hàm vô tỉ.
- Tích phân hàm lượng giác.
- Tích phân dùng đổi biến Euler.

Kỹ năng gợi ý:

- `indefinite_integral`
- `substitution_method`
- `integration_by_parts`
- `rational_function_integral`
- `partial_fraction_decomposition`
- `irrational_integral`
- `trigonometric_integral`
- `euler_substitution`

### 2.2. Tích phân xác định

Mã đề xuất:

```text
GT1_C2_02_Definite_Integrals
```

Nội dung theo đề cương:

- Định nghĩa tích phân xác định.
- Ý nghĩa hình học, cơ học.
- Tiêu chuẩn khả tích.
- Các tính chất của tích phân xác định.
- Công thức đạo hàm theo cận.
- Công thức Newton-Leibniz.
- Các phương pháp tính tích phân xác định.

Dạng bài dự kiến:

- Tính tích phân xác định bằng Newton-Leibniz.
- Dùng tính chất tích phân xác định.
- Đổi biến trong tích phân xác định.
- Tích phân từng phần trong tích phân xác định nếu xuất hiện.
- Tính đạo hàm của tích phân có cận biến thiên.
- Chứng minh khả tích hoặc dùng tiêu chuẩn khả tích nếu có.

Kỹ năng gợi ý:

- `definite_integral`
- `newton_leibniz_formula`
- `integral_properties`
- `substitution_method`
- `integration_by_parts`
- `differentiation_under_integral_limit`
- `integrability_criterion`

### 2.3. Tích phân suy rộng

Mã đề xuất:

```text
GT1_C2_03_Improper_Integrals
```

Nội dung theo đề cương:

- Tích phân suy rộng loại 1.
- Tích phân suy rộng loại 2.
- Định nghĩa, ý nghĩa hình học.
- Hội tụ, phân kỳ.
- Giá trị của tích phân suy rộng.
- Tích phân suy rộng của hàm số không âm.
- Các định lý so sánh.
- Hội tụ tuyệt đối.
- Bán hội tụ.

Dạng bài dự kiến:

- Xét hội tụ/phân kỳ của tích phân suy rộng loại 1.
- Xét hội tụ/phân kỳ của tích phân suy rộng loại 2.
- Tính giá trị tích phân suy rộng.
- Dùng tiêu chuẩn so sánh.
- Xét hội tụ tuyệt đối.
- Xét bán hội tụ.

Kỹ năng gợi ý:

- `improper_integral_type_1`
- `improper_integral_type_2`
- `improper_integral_convergence`
- `comparison_test`
- `absolute_convergence`
- `conditional_convergence`
- `limit_computation`

### 2.4. Ứng dụng của tích phân xác định

Mã đề xuất:

```text
GT1_C2_04_Applications_Definite_Integrals
```

Nội dung theo đề cương:

- Sơ đồ tổng tích phân, vi phân.
- Tính diện tích miền phẳng.
- Tính diện tích mặt tròn xoay.
- Tính thể tích vật thể.
- Tính độ dài cung phẳng.

Dạng bài dự kiến:

- Tính diện tích hình phẳng.
- Tính diện tích mặt tròn xoay.
- Tính thể tích vật thể.
- Tính thể tích khối tròn xoay.
- Tính độ dài cung phẳng.
- Lập tích phân từ bài toán hình học.

Kỹ năng gợi ý:

- `area_by_integral`
- `surface_area_of_revolution`
- `volume_by_integral`
- `arc_length`
- `application`

## 4. Chương 3 - Hàm số nhiều biến số

Mã đề xuất:

```text
GT1_C3_Multivariable_Functions
```

Tên hiển thị:

```text
Chương 3: Hàm số nhiều biến số
```

### 3.1. Các khái niệm cơ bản

Mã đề xuất:

```text
GT1_C3_01_Multivariable_Basics
```

Nội dung theo đề cương:

- Miền, khoảng cách, lân cận, biên.
- Miền đóng, miền mở, miền bị chặn.
- Định nghĩa hàm nhiều biến.
- Ý nghĩa hình học.
- Tập xác định.
- Tập giá trị.
- Giới hạn của hàm nhiều biến.
- Các phép toán về giới hạn.
- Hàm liên tục:
  - định nghĩa
  - các phép toán
  - tính chất
  - liên tục đều

Dạng bài dự kiến:

- Xác định miền xác định của hàm nhiều biến.
- Xét miền mở, đóng, bị chặn.
- Tính giới hạn hàm nhiều biến.
- Chứng minh giới hạn không tồn tại bằng các đường đi khác nhau.
- Xét tính liên tục của hàm nhiều biến.
- Tìm tham số để hàm nhiều biến liên tục.

Kỹ năng gợi ý:

- `multivariable_domain`
- `open_closed_bounded_set`
- `multivariable_limit`
- `path_limit_counterexample`
- `multivariable_continuity`
- `parameter_analysis`

### 3.2. Đạo hàm riêng và vi phân

Mã đề xuất:

```text
GT1_C3_02_Partial_Derivatives_Differentials
```

Nội dung theo đề cương:

- Đạo hàm riêng:
  - định nghĩa
  - cách tính
- Vi phân toàn phần:
  - định nghĩa
  - mối liên hệ giữa hàm số khả vi và có đạo hàm riêng
  - ứng dụng tính gần đúng
- Đạo hàm riêng và vi phân của hàm hợp.
- Tính bất biến của vi phân cấp một.
- Hàm ẩn:
  - định nghĩa
  - định lý tồn tại
  - cách tính đạo hàm riêng
- Đạo hàm riêng và vi phân cấp cao:
  - định nghĩa
  - định lý Schwarz
  - tính không bất biến của vi phân cấp cao
- Công thức khai triển Taylor.

Dạng bài dự kiến:

- Tính đạo hàm riêng cấp một.
- Tính vi phân toàn phần.
- Dùng vi phân toàn phần để tính gần đúng.
- Tính đạo hàm của hàm hợp nhiều biến.
- Tính đạo hàm hàm ẩn.
- Tính đạo hàm riêng cấp cao.
- Kiểm tra điều kiện định lý Schwarz.
- Khai triển Taylor nhiều biến.

Kỹ năng gợi ý:

- `partial_derivative`
- `total_differential`
- `multivariable_approximation`
- `multivariable_chain_rule`
- `implicit_function_derivative`
- `higher_order_partial_derivative`
- `schwarz_theorem`
- `multivariable_taylor_expansion`

### 3.3. Cực trị của hàm số nhiều biến

Mã đề xuất:

```text
GT1_C3_03_Multivariable_Extrema
```

Nội dung theo đề cương:

- Định nghĩa cực trị.
- Quy tắc tìm cực trị.
- Cực trị có điều kiện.
- Giá trị lớn nhất và nhỏ nhất.

Dạng bài dự kiến:

- Tìm điểm dừng của hàm nhiều biến.
- Phân loại cực trị bằng ma trận Hessian nếu dùng trong slide.
- Tìm cực trị không điều kiện.
- Tìm cực trị có điều kiện.
- Dùng phương pháp nhân tử Lagrange nếu xuất hiện trong slide/bài tập.
- Tìm giá trị lớn nhất, nhỏ nhất trên miền cho trước.

Kỹ năng gợi ý:

- `critical_point`
- `hessian_extrema_test`
- `unconstrained_extrema`
- `constrained_extrema`
- `lagrange_multiplier`
- `global_maximum_minimum`
- `case_analysis`

## 5. Danh sách chương/chủ đề chính thức cho AI Matching

Phiên bản rút gọn dùng làm key chính:

| Mã | Tên mục | Cấp |
| --- | --- | --- |
| `GT1_C1_Differential_Calculus_One_Variable` | Chương 1: Phép tính vi phân hàm một biến số | chapter |
| `GT1_C1_02_Function_Basics` | Hàm số và các khái niệm cơ bản | topic |
| `GT1_C1_03_Elementary_Functions` | Các hàm số sơ cấp | topic |
| `GT1_C1_04_Sequences` | Dãy số | topic |
| `GT1_C1_05_Function_Limits` | Giới hạn hàm số | topic |
| `GT1_C1_06_Infinitesimal_Infinite` | Vô cùng bé, vô cùng lớn | topic |
| `GT1_C1_07_Continuity` | Hàm số liên tục | topic |
| `GT1_C1_08_Derivatives_Differentials` | Đạo hàm và vi phân | topic |
| `GT1_C1_09_Theorems_Applications_Differentiable_Functions` | Các định lý về hàm khả vi và ứng dụng | topic |
| `GT1_C1_10_Curve_Function_Graph_Survey` | Khảo sát hàm số, đường cong | topic |
| `GT1_C2_Integral_Calculus_One_Variable` | Chương 2: Phép tính tích phân hàm một biến số | chapter |
| `GT1_C2_01_Indefinite_Integrals` | Tích phân bất định | topic |
| `GT1_C2_02_Definite_Integrals` | Tích phân xác định | topic |
| `GT1_C2_03_Improper_Integrals` | Tích phân suy rộng | topic |
| `GT1_C2_04_Applications_Definite_Integrals` | Ứng dụng của tích phân xác định | topic |
| `GT1_C3_Multivariable_Functions` | Chương 3: Hàm số nhiều biến số | chapter |
| `GT1_C3_01_Multivariable_Basics` | Các khái niệm cơ bản | topic |
| `GT1_C3_02_Partial_Derivatives_Differentials` | Đạo hàm riêng và vi phân | topic |
| `GT1_C3_03_Multivariable_Extrema` | Cực trị của hàm số nhiều biến | topic |

## 6. Quy ước cho bước tiếp theo

Ở bước 2, cần đối chiếu cây này với mục lục giáo trình và slide để:

- Bổ sung tên gọi chính xác hơn nếu giáo trình dùng cách gọi khác.
- Tách các topic thành subtopic/dạng bài chi tiết hơn.
- Xác định các dạng bài thật sự xuất hiện trong bài giảng.
- Bổ sung dấu hiệu nhận diện cho từng dạng bài.
- Bổ sung ví dụ từ bộ bài tập `2025.1_BTTK_MI1111.pdf`.

Các điểm cần kiểm tra thêm ở bước sau:

- Trong slide có dạy rõ phương pháp nhân tử Lagrange hay không.
- Trong slide có dùng Hessian để phân loại cực trị nhiều biến hay không.
- Trong phần tích phân bất định, phương pháp tích phân từng phần có nằm trong slide/bài tập không, vì đề cương ảnh không ghi riêng nhưng giáo trình thường có.
- Trong phần khảo sát đường cong, mức độ bài tập với tọa độ cực và tham số sâu đến đâu.
- Các mã skill có cần đổi sang tiếng Việt không hay giữ tiếng Anh để ổn định cho backend.

