# Bước 2 - Đối chiếu cây đề cương với giáo trình và slide

Mục tiêu của bước này là đối chiếu cây kiến thức đã chốt ở bước 1 với:

- Đề cương học phần Giải tích 1.
- Mục lục giáo trình do người dùng cung cấp qua ảnh.
- Các slide bài giảng theo chương:
  - `Giải tích 1/SAMI_GT1__Chuong1.pdf`
  - `Giải tích 1/SAMI_GT1__Chuong2.pdf`
  - `Giải tích 1/SAMI_GT1__Chuong3.pdf`
- File bài giảng tổng hợp:
  - `Giải tích 1/Đề cương/Bài giảng thầy diệu.pdf`

Quy ước đã chốt:

- Mã taxonomy dùng tiếng Anh, không dấu, ổn định cho backend.
- Tên hiển thị dùng tiếng Việt, bám theo đề cương/giáo trình/slide.
- Độ sâu phân loại: chương + chủ đề + dạng bài.

## 1. Thứ tự ưu tiên nguồn tri thức

Khi có khác biệt giữa các nguồn, hệ thống ưu tiên theo thứ tự:

1. Đề cương học phần.
2. Slide bài giảng.
3. Giáo trình/mục lục sách.
4. Bộ bài tập theo đề cương.

Lý do:

- Đề cương xác định phạm vi chính thức của môn học.
- Slide thể hiện cách thầy/cô giảng và nhấn mạnh dạng bài.
- Giáo trình bổ sung cấu trúc lý thuyết chi tiết.
- Bộ bài tập giúp xác định dạng bài thực tế và ví dụ matching.

## 2. Đối chiếu cấp chương

| Chương theo đề cương | Giáo trình/mục lục sách | Slide tương ứng | Kết luận taxonomy |
| --- | --- | --- | --- |
| Chương 1: Phép tính vi phân hàm một biến số | Chương 1: Hàm số một biến số | `SAMI_GT1__Chuong1.pdf` | Dùng tên đề cương làm tên chương chính; dùng giáo trình để bổ sung các mục hàm số, dãy số, giới hạn, liên tục, đạo hàm, khảo sát |
| Chương 2: Phép tính tích phân hàm một biến số | Chương 2: Phép tính tích phân một biến số | `SAMI_GT1__Chuong2.pdf` | Hai nguồn thống nhất gần như hoàn toàn |
| Chương 3: Hàm số nhiều biến số | Chương 3: Hàm số nhiều biến số | `SAMI_GT1__Chuong3.pdf` | Hai nguồn thống nhất gần như hoàn toàn |

Kết luận:

- Cây chính nên giữ đúng 3 chương theo đề cương.
- Giáo trình có thêm một số mục nền tảng như logic, tập hợp, tập số. Các mục này nên đưa vào phần nền tảng/mở đầu, không nên trở thành nhánh matching chính trừ khi bài tập yêu cầu.

## 3. Đối chiếu Chương 1

### 3.1. Nhận xét chung

Đề cương gọi chương 1 là:

```text
Chương 1: Phép tính vi phân hàm một biến số
```

Mục lục giáo trình gọi là:

```text
Chương 1: Hàm số một biến số
```

Hai cách gọi không mâu thuẫn. Đề cương nhấn mạnh mục tiêu chương là phép tính vi phân, còn giáo trình trình bày từ nền tảng hàm số một biến đến đạo hàm và ứng dụng.

Tên taxonomy nên dùng:

```text
Chương 1: Phép tính vi phân hàm một biến số
```

Mã:

```text
GT1_C1_Differential_Calculus_One_Variable
```

### 3.2. Bảng đối chiếu chủ đề Chương 1

| Đề cương | Mục lục giáo trình tương ứng | Ghi chú taxonomy |
| --- | --- | --- |
| 1.1 Mở đầu | Sơ lược về logic; các tập số; trị tuyệt đối và tính chất | Đưa vào nền tảng, ít dùng để match bài tập chính |
| 1.2 Hàm số | Hàm số; định nghĩa hàm số; hàm số đơn điệu; hàm số bị chặn; hàm số chẵn/lẻ; hàm tuần hoàn; hàm hợp; hàm ngược; hàm số sơ cấp | Nên tách thành topic `Function_Basics` và `Elementary_Functions` |
| 1.3 Các hàm số sơ cấp | Hàm số sơ cấp; các hàm lượng giác ngược, hyperbolic nếu có trong slide | Là topic riêng để match bài nhận diện/biến đổi hàm sơ cấp |
| 1.4 Dãy số | Dãy số; dãy số và giới hạn; tiêu chuẩn tồn tại giới hạn | Topic riêng vì có bài tính/chứng minh giới hạn dãy |
| 1.5 Giới hạn hàm số | Giới hạn hàm số; định nghĩa; phép toán; hàm hợp; giới hạn vô cùng; giới hạn ở cực | Topic riêng, có nhiều dạng bài |
| 1.6 Vô cùng bé, vô cùng lớn | Vô cùng bé; vô cùng lớn; bài tập | Topic riêng vì là kỹ thuật tính giới hạn trọng tâm |
| 1.7 Hàm số liên tục | Hàm số liên tục; định nghĩa; phép toán; liên tục hàm ngược; liên tục hàm hợp; định lý; điểm gián đoạn | Topic riêng |
| 1.8 Đạo hàm và vi phân | Đạo hàm và vi phân; đạo hàm hàm hợp; hàm ngược; đạo hàm cấp cao; vi phân cấp cao | Topic riêng |
| 1.9 Các định lý về hàm khả vi và ứng dụng | Fermat, Rolle, Lagrange, Cauchy; Taylor/Maclaurin; L'Hospital; VCB tương đương; VCL tiêu biểu | Topic riêng, nhiều dạng chứng minh/tính giới hạn |
| 1.10 Khảo sát hàm số, đường cong | Khảo sát đồ thị; đường cong tham số; tọa độ cực | Topic riêng |

### 3.3. Dạng bài chi tiết đề xuất cho Chương 1

#### GT1_C1_02_Function_Basics - Hàm số và các khái niệm cơ bản

Dạng bài:

- `GT1_C1_02_T01_Domain_And_Range`: Tìm tập xác định, tập giá trị.
- `GT1_C1_02_T02_Monotonicity_Boundedness_Parity`: Xét đơn điệu, bị chặn, chẵn lẻ, tuần hoàn ở mức định nghĩa.
- `GT1_C1_02_T03_Function_Composition`: Tìm hoặc phân tích hàm hợp.
- `GT1_C1_02_T04_Inverse_Function`: Tìm hàm ngược, kiểm tra điều kiện có hàm ngược.

#### GT1_C1_03_Elementary_Functions - Các hàm số sơ cấp

Dạng bài:

- `GT1_C1_03_T01_Identify_Elementary_Function`: Nhận diện và phân loại hàm sơ cấp.
- `GT1_C1_03_T02_Inverse_Trigonometric_Function`: Biến đổi/tính toán với hàm lượng giác ngược.
- `GT1_C1_03_T03_Hyperbolic_Function`: Biến đổi/tính toán với hàm hyperbolic.

#### GT1_C1_04_Sequences - Dãy số

Dạng bài:

- `GT1_C1_04_T01_Compute_Sequence_Limit`: Tính giới hạn dãy số.
- `GT1_C1_04_T02_Squeeze_Theorem_Sequence`: Dùng tiêu chuẩn kẹp.
- `GT1_C1_04_T03_Monotone_Bounded_Sequence`: Dùng tiêu chuẩn đơn điệu bị chặn.
- `GT1_C1_04_T04_Cauchy_Criterion_Sequence`: Dùng tiêu chuẩn Cauchy.
- `GT1_C1_04_T05_Recursive_Sequence`: Dãy truy hồi, nếu xuất hiện trong bài tập.

#### GT1_C1_05_Function_Limits - Giới hạn hàm số

Dạng bài:

- `GT1_C1_05_T01_Direct_Limit`: Tính giới hạn trực tiếp.
- `GT1_C1_05_T02_Algebraic_Transformation_Limit`: Tính giới hạn bằng biến đổi đại số.
- `GT1_C1_05_T03_One_Sided_Limit`: Tính giới hạn một phía.
- `GT1_C1_05_T04_Limit_At_Infinity`: Tính giới hạn khi biến tiến ra vô cực.
- `GT1_C1_05_T05_Infinite_Limit`: Tính giới hạn vô cực.
- `GT1_C1_05_T06_Composite_Function_Limit`: Giới hạn hàm hợp.
- `GT1_C1_05_T07_Proof_By_Definition`: Chứng minh giới hạn bằng định nghĩa.

#### GT1_C1_06_Infinitesimal_Infinite - Vô cùng bé, vô cùng lớn

Dạng bài:

- `GT1_C1_06_T01_Compare_Infinitesimal`: So sánh cấp vô cùng bé.
- `GT1_C1_06_T02_Equivalent_Infinitesimal`: Dùng VCB tương đương để tính giới hạn.
- `GT1_C1_06_T03_Compare_Infinite`: So sánh cấp vô cùng lớn.
- `GT1_C1_06_T04_Asymptotic_Simplification`: Ngắt bỏ VCB/VCL bậc thấp.

#### GT1_C1_07_Continuity - Hàm số liên tục

Dạng bài:

- `GT1_C1_07_T01_Continuity_At_Point`: Xét liên tục tại một điểm.
- `GT1_C1_07_T02_Continuity_On_Set`: Xét liên tục trên khoảng/đoạn/miền.
- `GT1_C1_07_T03_Piecewise_Continuity`: Xét liên tục của hàm từng phần.
- `GT1_C1_07_T04_Find_Parameter_For_Continuity`: Tìm tham số để liên tục.
- `GT1_C1_07_T05_Classify_Discontinuity`: Phân loại điểm gián đoạn.
- `GT1_C1_07_T06_Use_Continuity_Theorems`: Dùng định lý hàm liên tục.

#### GT1_C1_08_Derivatives_Differentials - Đạo hàm và vi phân

Dạng bài:

- `GT1_C1_08_T01_Basic_Derivative`: Tính đạo hàm cơ bản.
- `GT1_C1_08_T02_One_Sided_Derivative`: Tính/xét đạo hàm một phía.
- `GT1_C1_08_T03_Derivative_Existence`: Xét tồn tại đạo hàm tại điểm.
- `GT1_C1_08_T04_Chain_Rule`: Đạo hàm hàm hợp.
- `GT1_C1_08_T05_Inverse_Function_Derivative`: Đạo hàm hàm ngược.
- `GT1_C1_08_T06_Differential`: Tính vi phân.
- `GT1_C1_08_T07_Linear_Approximation`: Ứng dụng vi phân để tính gần đúng.
- `GT1_C1_08_T08_Higher_Order_Derivative`: Đạo hàm cấp cao.
- `GT1_C1_08_T09_Higher_Order_Differential`: Vi phân cấp cao.

#### GT1_C1_09_Theorems_Applications_Differentiable_Functions - Các định lý về hàm khả vi và ứng dụng

Dạng bài:

- `GT1_C1_09_T01_Fermat_Rolle_Lagrange_Cauchy`: Áp dụng định lý Fermat, Rolle, Lagrange, Cauchy.
- `GT1_C1_09_T02_Proof_Using_Mean_Value_Theorem`: Chứng minh đẳng thức/bất đẳng thức bằng định lý giá trị trung bình.
- `GT1_C1_09_T03_Taylor_Maclaurin_Expansion`: Khai triển Taylor/Maclaurin.
- `GT1_C1_09_T04_Limit_By_Taylor`: Tính giới hạn bằng khai triển Taylor.
- `GT1_C1_09_T05_LHopital_Rule`: Tính giới hạn bằng quy tắc L'Hospital.
- `GT1_C1_09_T06_Monotonicity_By_Derivative`: Xét đơn điệu bằng đạo hàm.
- `GT1_C1_09_T07_Convexity_Concavity`: Xét lồi/lõm, bất đẳng thức hàm lồi.
- `GT1_C1_09_T08_One_Variable_Extrema`: Tìm cực trị hàm một biến.
- `GT1_C1_09_T09_Newton_Method`: Phương pháp Newton.

#### GT1_C1_10_Curve_Function_Graph_Survey - Khảo sát hàm số, đường cong

Dạng bài:

- `GT1_C1_10_T01_Function_Graph_Survey`: Khảo sát và vẽ đồ thị hàm số `y=f(x)`.
- `GT1_C1_10_T02_Asymptote_Analysis`: Tìm tiệm cận.
- `GT1_C1_10_T03_Variation_Table`: Lập bảng biến thiên.
- `GT1_C1_10_T04_Convexity_Inflection`: Xét lồi/lõm và điểm uốn.
- `GT1_C1_10_T05_Parametric_Curve`: Khảo sát đường cong tham số.
- `GT1_C1_10_T06_Polar_Curve`: Khảo sát đường cong trong tọa độ cực.

## 4. Đối chiếu Chương 2

### 4.1. Nhận xét chung

Đề cương và giáo trình thống nhất ở chương 2:

```text
Chương 2: Phép tính tích phân hàm một biến số
```

Tên taxonomy:

```text
Chương 2: Phép tính tích phân hàm một biến số
```

Mã:

```text
GT1_C2_Integral_Calculus_One_Variable
```

### 4.2. Bảng đối chiếu chủ đề Chương 2

| Đề cương | Mục lục giáo trình tương ứng | Ghi chú taxonomy |
| --- | --- | --- |
| 2.1 Tích phân bất định | Nguyên hàm; các phương pháp tính tích phân bất định; tích phân phân thức hữu tỉ; tích phân hàm lượng giác; tích phân biểu thức vô tỉ | Giáo trình chi tiết hơn đề cương, cần tách dạng bài theo phương pháp |
| 2.2 Tích phân xác định | Định nghĩa; tiêu chuẩn khả tích; tính chất; tích phân với cận biến thiên; phương pháp tính | Topic riêng |
| 2.3 Tích phân suy rộng | Tích phân suy rộng với cận vô hạn; của hàm không bị chặn; tiêu chuẩn hội tụ; hội tụ tuyệt đối/bán hội tụ | Topic riêng, có nhiều dạng bài kiểm tra hội tụ |
| 2.4 Ứng dụng tích phân xác định | Diện tích hình phẳng; độ dài cung; thể tích vật thể; diện tích mặt tròn xoay | Topic riêng |

### 4.3. Dạng bài chi tiết đề xuất cho Chương 2

#### GT1_C2_01_Indefinite_Integrals - Tích phân bất định

Dạng bài:

- `GT1_C2_01_T01_Basic_Antiderivative`: Tính nguyên hàm cơ bản.
- `GT1_C2_01_T02_Substitution_Method`: Tính tích phân bằng phương pháp đổi biến.
- `GT1_C2_01_T03_Integration_By_Parts`: Tính tích phân từng phần.
- `GT1_C2_01_T04_Rational_Function_Integral`: Tích phân hàm phân thức hữu tỉ.
- `GT1_C2_01_T05_Partial_Fractions`: Phân tích phân thức hữu tỉ thành phân thức đơn giản.
- `GT1_C2_01_T06_Trigonometric_Integral`: Tích phân hàm lượng giác.
- `GT1_C2_01_T07_Irrational_Integral`: Tích phân biểu thức vô tỉ.
- `GT1_C2_01_T08_Euler_Substitution`: Tích phân dùng phép đổi biến Euler.

#### GT1_C2_02_Definite_Integrals - Tích phân xác định

Dạng bài:

- `GT1_C2_02_T01_Definition_And_Geometric_Meaning`: Định nghĩa và ý nghĩa hình học/cơ học.
- `GT1_C2_02_T02_Integrability_Criterion`: Tiêu chuẩn khả tích.
- `GT1_C2_02_T03_Integral_Properties`: Dùng tính chất tích phân xác định.
- `GT1_C2_02_T04_Newton_Leibniz`: Tính tích phân bằng Newton-Leibniz.
- `GT1_C2_02_T05_Substitution_Definite_Integral`: Đổi biến trong tích phân xác định.
- `GT1_C2_02_T06_By_Parts_Definite_Integral`: Tích phân từng phần trong tích phân xác định.
- `GT1_C2_02_T07_Differentiation_Under_Variable_Limits`: Đạo hàm tích phân theo cận biến thiên.

#### GT1_C2_03_Improper_Integrals - Tích phân suy rộng

Dạng bài:

- `GT1_C2_03_T01_Type_One_Infinite_Interval`: Tích phân suy rộng loại 1 trên cận vô hạn.
- `GT1_C2_03_T02_Type_Two_Unbounded_Function`: Tích phân suy rộng loại 2 của hàm không bị chặn.
- `GT1_C2_03_T03_Compute_Improper_Integral`: Tính giá trị tích phân suy rộng.
- `GT1_C2_03_T04_Convergence_Divergence`: Xét hội tụ/phân kỳ.
- `GT1_C2_03_T05_Comparison_Test`: Dùng tiêu chuẩn so sánh.
- `GT1_C2_03_T06_Absolute_Convergence`: Xét hội tụ tuyệt đối.
- `GT1_C2_03_T07_Conditional_Convergence`: Xét bán hội tụ.

#### GT1_C2_04_Applications_Definite_Integrals - Ứng dụng của tích phân xác định

Dạng bài:

- `GT1_C2_04_T01_Area_Plane_Region`: Tính diện tích miền phẳng.
- `GT1_C2_04_T02_Arc_Length`: Tính độ dài cung phẳng.
- `GT1_C2_04_T03_Volume_Of_Solid`: Tính thể tích vật thể.
- `GT1_C2_04_T04_Volume_Of_Revolution`: Tính thể tích khối tròn xoay.
- `GT1_C2_04_T05_Surface_Area_Of_Revolution`: Tính diện tích mặt tròn xoay.

## 5. Đối chiếu Chương 3

### 5.1. Nhận xét chung

Đề cương và giáo trình thống nhất:

```text
Chương 3: Hàm số nhiều biến số
```

Mã:

```text
GT1_C3_Multivariable_Functions
```

### 5.2. Bảng đối chiếu chủ đề Chương 3

| Đề cương | Mục lục giáo trình tương ứng | Ghi chú taxonomy |
| --- | --- | --- |
| 3.1 Các khái niệm cơ bản | Giới hạn hàm số nhiều biến; tính liên tục; bài tập | Nên gồm miền xác định, giới hạn, liên tục |
| 3.2 Đạo hàm riêng và vi phân | Đạo hàm riêng; vi phân toàn phần; đạo hàm hàm hợp; đạo hàm và vi phân cấp cao; đạo hàm theo hướng-gradient; hàm ẩn | Giáo trình chi tiết hơn đề cương, cần tách dạng bài |
| 3.3 Cực trị của hàm số nhiều biến | Cực trị tự do; cực trị có điều kiện; giá trị lớn nhất - nhỏ nhất | Topic riêng |

### 5.3. Dạng bài chi tiết đề xuất cho Chương 3

#### GT1_C3_01_Multivariable_Basics - Các khái niệm cơ bản

Dạng bài:

- `GT1_C3_01_T01_Domain_Of_Multivariable_Function`: Tìm miền xác định của hàm nhiều biến.
- `GT1_C3_01_T02_Open_Closed_Bounded_Set`: Xét miền mở, đóng, bị chặn, biên.
- `GT1_C3_01_T03_Multivariable_Limit`: Tính giới hạn hàm nhiều biến.
- `GT1_C3_01_T04_Path_Dependent_Limit`: Chứng minh giới hạn không tồn tại bằng đường đi khác nhau.
- `GT1_C3_01_T05_Multivariable_Continuity`: Xét tính liên tục hàm nhiều biến.
- `GT1_C3_01_T06_Parameter_For_Continuity`: Tìm tham số để liên tục.

#### GT1_C3_02_Partial_Derivatives_Differentials - Đạo hàm riêng và vi phân

Dạng bài:

- `GT1_C3_02_T01_First_Order_Partial_Derivative`: Tính đạo hàm riêng cấp một.
- `GT1_C3_02_T02_Total_Differential`: Tính vi phân toàn phần.
- `GT1_C3_02_T03_Approximation_By_Differential`: Dùng vi phân để tính gần đúng.
- `GT1_C3_02_T04_Multivariable_Chain_Rule`: Đạo hàm hàm hợp nhiều biến.
- `GT1_C3_02_T05_Higher_Order_Partial_Derivative`: Tính đạo hàm riêng cấp cao.
- `GT1_C3_02_T06_Schwarz_Theorem`: Áp dụng/kiểm tra định lý Schwarz.
- `GT1_C3_02_T07_Directional_Derivative_Gradient`: Đạo hàm theo hướng và gradient.
- `GT1_C3_02_T08_Implicit_Function_Derivative`: Đạo hàm hàm ẩn.
- `GT1_C3_02_T09_Multivariable_Taylor`: Khai triển Taylor nhiều biến.

#### GT1_C3_03_Multivariable_Extrema - Cực trị của hàm số nhiều biến

Dạng bài:

- `GT1_C3_03_T01_Critical_Point`: Tìm điểm dừng/điểm tới hạn.
- `GT1_C3_03_T02_Unconstrained_Extrema`: Tìm cực trị tự do.
- `GT1_C3_03_T03_Hessian_Test`: Phân loại cực trị bằng điều kiện đạo hàm cấp hai/Hessian.
- `GT1_C3_03_T04_Constrained_Extrema`: Tìm cực trị có điều kiện.
- `GT1_C3_03_T05_Lagrange_Multiplier`: Phương pháp nhân tử Lagrange nếu slide/bài tập có.
- `GT1_C3_03_T06_Global_Maximum_Minimum`: Tìm giá trị lớn nhất, nhỏ nhất.

## 6. Những điểm cần xác minh trực tiếp từ slide

Các điểm sau cần kiểm tra ở bước đọc slide/bài tập chi tiết:

1. Chương 1:
   - Slide có tách riêng hàm lượng giác ngược/hyperbolic thành dạng bài không.
   - Mức độ bài tập về phương pháp Newton.
   - Mức độ khảo sát đường cong tham số và tọa độ cực.

2. Chương 2:
   - Tích phân từng phần có xuất hiện rõ trong slide không.
   - Phép đổi biến Euler xuất hiện ở mức lý thuyết hay có bài tập thực hành.
   - Tích phân suy rộng có yêu cầu phân biệt hội tụ tuyệt đối/bán hội tụ nhiều không.

3. Chương 3:
   - Có dùng Hessian trong phân loại cực trị không.
   - Có dạy nhân tử Lagrange không.
   - Đạo hàm theo hướng-gradient xuất hiện ở mức trọng tâm hay phụ.
   - Taylor nhiều biến có bài tập riêng hay chỉ giới thiệu.

## 7. Kết luận bước 2

Sau đối chiếu đề cương với mục lục giáo trình và danh sách slide, cây taxonomy nên giữ cấu trúc chính:

```text
Giải tích 1
├── Chương 1: Phép tính vi phân hàm một biến số
├── Chương 2: Phép tính tích phân hàm một biến số
└── Chương 3: Hàm số nhiều biến số
```

Dưới mỗi chương, các topic chính được giữ theo đề cương. Dưới mỗi topic, bổ sung thêm các dạng bài chi tiết theo mục lục giáo trình và các nội dung đã xuất hiện trong kế hoạch giảng dạy.

Bước tiếp theo:

```text
Bước 3 - Trích dạng bài thực tế từ bộ bài tập 2025.1_BTTK_MI1111.pdf
```

Bước 3 sẽ dùng bài tập thật để kiểm chứng và tinh chỉnh danh sách dạng bài ở trên.

