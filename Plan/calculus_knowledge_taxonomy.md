# Calculus Knowledge Taxonomy

Muc dich cua file nay la lam "ban do kien thuc" cho he thong AI matching bai tap Giai tich.
Khi he thong nhan mot cau hoi moi, AI se doi chieu noi dung cau hoi voi taxonomy nay de gan:

- `subject`: mon hoc/lien mien kien thuc.
- `chapter`: chuong lon.
- `topic`: chu de cu the.
- `subtopic`: dang bai hoac ky thuat giai.
- `skills`: cac ky nang can dung.
- `difficulty`: `easy`, `medium`, hoac `hard`.

Quy uoc chung:

- `subject` mac dinh: `Calculus`.
- Neu cau hoi thuoc nhieu muc, chon muc chinh theo ky thuat giai quan trong nhat.
- Neu de bai chi hoi tinh toan truc tiep, uu tien gan skill `computation`.
- Neu de bai yeu cau giai thich, chung minh, bien luan, uu tien them skill `proof`.
- Neu de bai gan voi dien tich, the tich, toi uu hoa, vat ly, kinh te, uu tien them skill `application`.

## Output Schema

AI classifier phai tra ve JSON theo dung schema:

```json
{
  "subject": "Calculus",
  "chapter": "GT01_Limits_Continuity",
  "topic": "GT01.02_Function_Limits",
  "subtopic": "GT01.02.03_One_Sided_Limits",
  "skills": ["limit_computation", "case_analysis"],
  "difficulty": "medium",
  "confidence": 0.86,
  "reason": "De bai yeu cau tinh gioi han mot phia cua ham so tung doan."
}
```

## Difficulty Rubric

### easy

Cau hoi duoc xem la `easy` neu:

- Chi can ap dung mot cong thuc/qui tac co ban.
- Khong can bien doi dai hoac chia nhieu truong hop.
- Co du lieu truc tiep, it bay nhieu.
- Thuong la bai nhan dien, tinh nhanh, thay so.

### medium

Cau hoi duoc xem la `medium` neu:

- Can 2-4 buoc bien doi.
- Can chon dung phuong phap trong vai kha nang.
- Co the can ket hop 2 kien thuc trong cung chuong.
- Co tham so don gian hoac yeu cau giai thich ngan.

### hard

Cau hoi duoc xem la `hard` neu:

- Can nhieu buoc suy luan, bien luan tham so, hoac chia truong hop.
- Ket hop nhieu chuong/kien thuc.
- Yeu cau chung minh, danh gia, tim dieu kien can va du.
- Co cong thuc phuc tap, mien xac dinh kho, hoac yeu cau sang tao trong phuong phap.

## Skill Vocabulary

Danh sach skill nen dung thong nhat:

- `algebraic_transformation`: bien doi dai so.
- `limit_computation`: tinh gioi han.
- `equivalent_infinitesimal`: dung vo cung be tuong duong.
- `continuity_analysis`: xet tinh lien tuc.
- `derivative_computation`: tinh dao ham.
- `chain_rule`: dao ham ham hop.
- `implicit_differentiation`: dao ham ham an.
- `higher_order_derivative`: dao ham cap cao.
- `monotonicity_extrema`: xet don dieu, cuc tri.
- `function_graph_analysis`: khao sat va ve do thi ham so.
- `l_hopital_rule`: quy tac L'Hopital.
- `differential_approximation`: vi phan va xap xi.
- `indefinite_integral`: tich phan bat dinh.
- `substitution_method`: doi bien so.
- `integration_by_parts`: tich phan tung phan.
- `trigonometric_integral`: tich phan luong giac.
- `rational_integral`: tich phan ham huu ti.
- `definite_integral`: tich phan xac dinh.
- `improper_integral`: tich phan suy rong.
- `area_volume_application`: ung dung dien tich, the tich.
- `multiple_integral`: tich phan boi.
- `series_convergence`: xet hoi tu chuoi so.
- `absolute_conditional_convergence`: hoi tu tuyet doi/co dieu kien.
- `power_series`: chuoi luy thua.
- `taylor_maclaurin`: khai trien Taylor/Maclaurin.
- `fourier_series`: chuoi Fourier.
- `proof`: chung minh.
- `application`: ung dung.
- `case_analysis`: chia truong hop.
- `parameter_analysis`: bien luan tham so.

## GT01_Limits_Continuity

Chuong ve gioi han day so, gioi han ham so, vo cung be/vo cung lon va tinh lien tuc.

### GT01.01_Sequence_Limits

Mo ta: Cac bai toan ve gioi han cua day so.

Dau hieu nhan dien:

- Xuat hien `lim n -> infinity`, day `u_n`, `a_n`.
- Co bieu thuc theo `n`, can tinh gioi han khi `n` tien ra vo cung.

Subtopics:

- `GT01.01.01_Basic_Sequence_Limits`: gioi han day co ban.
- `GT01.01.02_Monotone_Bounded_Sequences`: day don dieu bi chan.
- `GT01.01.03_Recursive_Sequences`: day truy hoi.
- `GT01.01.04_Squeeze_For_Sequences`: nguyen ly kep cho day.

Skills: `limit_computation`, `algebraic_transformation`, `proof`, `case_analysis`.

### GT01.02_Function_Limits

Mo ta: Cac bai toan tinh gioi han ham so.

Dau hieu nhan dien:

- Xuat hien `lim x -> a`, `lim x -> infinity`.
- Cac dang vo dinh `0/0`, `infinity/infinity`, `infinity - infinity`, `0 * infinity`.

Subtopics:

- `GT01.02.01_Basic_Function_Limits`: gioi han ham so co ban.
- `GT01.02.02_Infinite_Limits`: gioi han vo cuc.
- `GT01.02.03_One_Sided_Limits`: gioi han mot phia.
- `GT01.02.04_Indeterminate_Forms`: dang vo dinh.

Skills: `limit_computation`, `algebraic_transformation`, `case_analysis`.

### GT01.03_Infinitesimal_Equivalent

Mo ta: Su dung vo cung be, vo cung lon va cac tuong duong de tinh gioi han.

Dau hieu nhan dien:

- Xuat hien `sin x ~ x`, `ln(1+x) ~ x`, `e^x - 1 ~ x`.
- Bai gioi han tai 0 co luong giac, logarit, ham mu.

Subtopics:

- `GT01.03.01_Equivalent_Infinitesimal`: vo cung be tuong duong.
- `GT01.03.02_Asymptotic_Comparison`: so sanh bac vo cung be/vo cung lon.

Skills: `equivalent_infinitesimal`, `limit_computation`, `algebraic_transformation`.

### GT01.04_Continuity

Mo ta: Tinh lien tuc cua ham so va diem gian doan.

Dau hieu nhan dien:

- Xuat hien yeu cau "xet tinh lien tuc", "tim a de ham lien tuc", "diem gian doan".
- Ham tung phan, can so sanh gioi han trai/phai voi gia tri ham.

Subtopics:

- `GT01.04.01_Continuity_At_Point`: lien tuc tai mot diem.
- `GT01.04.02_Continuity_On_Interval`: lien tuc tren khoang/doan.
- `GT01.04.03_Piecewise_Continuity`: lien tuc cua ham tung phan.
- `GT01.04.04_Intermediate_Value_Theorem`: dinh ly gia tri trung gian.

Skills: `continuity_analysis`, `limit_computation`, `case_analysis`, `proof`.

## GT02_Derivatives_Differentials

Chuong ve dao ham, vi phan, khao sat ham so va cac ung dung cua dao ham.

### GT02.01_Basic_Derivatives

Mo ta: Tinh dao ham bang cong thuc co ban.

Dau hieu nhan dien:

- Yeu cau tinh `f'(x)`, `dy/dx`.
- Ham da thuc, phan thuc don gian, can bac, ham mu, logarit, luong giac.

Subtopics:

- `GT02.01.01_Polynomial_Derivative`: dao ham da thuc.
- `GT02.01.02_Exponential_Log_Derivative`: dao ham ham mu va logarit.
- `GT02.01.03_Trigonometric_Derivative`: dao ham luong giac.
- `GT02.01.04_Product_Quotient_Rules`: quy tac tich/thuong.

Skills: `derivative_computation`, `algebraic_transformation`.

### GT02.02_Chain_Rule

Mo ta: Dao ham ham hop.

Dau hieu nhan dien:

- Ham long nhau: `ln(sin x)`, `e^{x^2}`, `sqrt(1+x^2)`.
- Can ap dung quy tac day chuyen.

Subtopics:

- `GT02.02.01_Simple_Composition`: ham hop co ban.
- `GT02.02.02_Multiple_Composition`: ham hop nhieu tang.
- `GT02.02.03_Composite_Trig_Log_Exp`: ham hop voi luong giac/log/mu.

Skills: `chain_rule`, `derivative_computation`, `algebraic_transformation`.

### GT02.03_Implicit_And_Parametric_Derivatives

Mo ta: Dao ham ham an, ham tham so.

Dau hieu nhan dien:

- Phuong trinh lien he `F(x,y)=0`.
- Ham tham so `x=x(t)`, `y=y(t)`.

Subtopics:

- `GT02.03.01_Implicit_Differentiation`: dao ham ham an.
- `GT02.03.02_Parametric_Derivative`: dao ham ham tham so.

Skills: `implicit_differentiation`, `derivative_computation`, `algebraic_transformation`.

### GT02.04_Higher_Order_Derivatives

Mo ta: Dao ham cap hai, cap n.

Dau hieu nhan dien:

- Yeu cau tinh `f''(x)`, `f^{(n)}(x)`.
- Bai tim cong thuc tong quat dao ham cap n.

Subtopics:

- `GT02.04.01_Second_Derivative`: dao ham cap hai.
- `GT02.04.02_Nth_Derivative`: dao ham cap n.
- `GT02.04.03_Leibniz_Formula`: cong thuc Leibniz cho dao ham cap cao.

Skills: `higher_order_derivative`, `derivative_computation`, `proof`.

### GT02.05_Monotonicity_Extrema_Graph

Mo ta: Ung dung dao ham de xet don dieu, cuc tri, khao sat ham so.

Dau hieu nhan dien:

- Tu khoa: "dong bien", "nghich bien", "cuc tri", "max/min", "khao sat ham so".
- Can lap bang bien thien.

Subtopics:

- `GT02.05.01_Monotonicity`: xet don dieu.
- `GT02.05.02_Local_Extrema`: cuc tri dia phuong.
- `GT02.05.03_Global_Extrema`: gia tri lon nhat/nho nhat.
- `GT02.05.04_Convexity_Concavity`: loi/lom, diem uon.
- `GT02.05.05_Graph_Sketching`: khao sat va ve do thi.

Skills: `monotonicity_extrema`, `function_graph_analysis`, `case_analysis`, `parameter_analysis`.

### GT02.06_LHopital_And_Differentials

Mo ta: Quy tac L'Hopital va vi phan.

Dau hieu nhan dien:

- Gioi han dang `0/0`, `infinity/infinity` co the dung dao ham.
- Yeu cau tinh vi phan, xap xi tuyen tinh, sai so gan dung.

Subtopics:

- `GT02.06.01_LHopital_Rule`: quy tac L'Hopital.
- `GT02.06.02_Differential`: vi phan.
- `GT02.06.03_Linear_Approximation`: xap xi tuyen tinh.

Skills: `l_hopital_rule`, `differential_approximation`, `limit_computation`, `application`.

## GT03_Integrals

Chuong ve nguyen ham, tich phan bat dinh, tich phan xac dinh va ung dung tich phan.

### GT03.01_Indefinite_Integrals

Mo ta: Tinh nguyen ham/tich phan bat dinh bang cong thuc co ban.

Dau hieu nhan dien:

- Xuat hien `int f(x) dx`, "tim nguyen ham", "tich phan bat dinh".
- Co the tinh truc tiep bang bang nguyen ham.

Subtopics:

- `GT03.01.01_Basic_Antiderivative`: nguyen ham co ban.
- `GT03.01.02_Exponential_Log_Integrals`: tich phan ham mu/log.
- `GT03.01.03_Trigonometric_Antiderivative`: nguyen ham luong giac co ban.

Skills: `indefinite_integral`, `algebraic_transformation`.

### GT03.02_Substitution_Method

Mo ta: Tich phan bang phuong phap doi bien.

Dau hieu nhan dien:

- Co cau truc `f'(x) g(f(x))`.
- Can dat `u = ...`.

Subtopics:

- `GT03.02.01_Simple_Substitution`: doi bien co ban.
- `GT03.02.02_Trig_Substitution`: doi bien luong giac.
- `GT03.02.03_Definite_Substitution`: doi bien trong tich phan xac dinh.

Skills: `substitution_method`, `indefinite_integral`, `definite_integral`.

### GT03.03_Integration_By_Parts

Mo ta: Tich phan tung phan.

Dau hieu nhan dien:

- Tich cua hai loai ham: da thuc voi mu/log/luong giac.
- Dang `int x^n e^x dx`, `int x ln x dx`, `int x sin x dx`.

Subtopics:

- `GT03.03.01_Basic_By_Parts`: tung phan mot lan.
- `GT03.03.02_Repeated_By_Parts`: tung phan nhieu lan.
- `GT03.03.03_Cyclic_By_Parts`: tung phan lap lai.

Skills: `integration_by_parts`, `indefinite_integral`, `algebraic_transformation`.

### GT03.04_Special_Integral_Techniques

Mo ta: Cac ky thuat tich phan dac biet.

Dau hieu nhan dien:

- Tich phan luong giac, ham huu ti, can thuc, phan tich thanh phan don gian.

Subtopics:

- `GT03.04.01_Trigonometric_Integrals`: tich phan luong giac.
- `GT03.04.02_Rational_Function_Integrals`: tich phan ham huu ti.
- `GT03.04.03_Partial_Fractions`: phan tich phan thuc don gian.
- `GT03.04.04_Irrational_Integrals`: tich phan chua can thuc.

Skills: `trigonometric_integral`, `rational_integral`, `algebraic_transformation`.

### GT03.05_Definite_And_Improper_Integrals

Mo ta: Tich phan xac dinh, Newton-Leibniz, tich phan suy rong.

Dau hieu nhan dien:

- Co can duoi/can tren `int_a^b`.
- Can xet hoi tu tich phan tren mien vo han hoac ham khong bi chan.

Subtopics:

- `GT03.05.01_Newton_Leibniz`: cong thuc Newton-Leibniz.
- `GT03.05.02_Properties_Of_Definite_Integral`: tinh chat tich phan xac dinh.
- `GT03.05.03_Improper_Integral_Infinite_Interval`: suy rong tren khoang vo han.
- `GT03.05.04_Improper_Integral_Unbounded_Function`: suy rong do ham khong bi chan.

Skills: `definite_integral`, `improper_integral`, `limit_computation`, `proof`.

### GT03.06_Applications_Of_Integrals

Mo ta: Ung dung tich phan tinh dien tich, the tich, do dai, gia tri trung binh.

Dau hieu nhan dien:

- Tu khoa: "dien tich", "the tich", "vat the tron xoay", "do dai cung", "gia tri trung binh".

Subtopics:

- `GT03.06.01_Area_Between_Curves`: dien tich hinh phang.
- `GT03.06.02_Volume_Of_Revolution`: the tich tron xoay.
- `GT03.06.03_Arc_Length`: do dai cung.
- `GT03.06.04_Average_Value`: gia tri trung binh cua ham.

Skills: `area_volume_application`, `definite_integral`, `application`.

## GT04_Multiple_Integrals

Chuong ve tich phan boi va ung dung hinh hoc.

### GT04.01_Double_Integrals

Mo ta: Tich phan kep tren mien phang.

Dau hieu nhan dien:

- Xuat hien `iint_D`, mien `D`, doi thu tu tich phan.
- Can mo ta mien tren mat phang.

Subtopics:

- `GT04.01.01_Rectangular_Region`: mien chu nhat.
- `GT04.01.02_General_Region`: mien tong quat.
- `GT04.01.03_Change_Order`: doi thu tu tich phan.
- `GT04.01.04_Polar_Coordinates`: toa do cuc.

Skills: `multiple_integral`, `area_volume_application`, `case_analysis`.

### GT04.02_Triple_Integrals

Mo ta: Tich phan ba lop trong khong gian.

Dau hieu nhan dien:

- Xuat hien `iiint_E`, mien khong gian `E`.
- Cac toa do tru, cau, hoac mien bi gioi han boi mat.

Subtopics:

- `GT04.02.01_Cartesian_Triple_Integral`: toa do Descartes.
- `GT04.02.02_Cylindrical_Coordinates`: toa do tru.
- `GT04.02.03_Spherical_Coordinates`: toa do cau.

Skills: `multiple_integral`, `area_volume_application`, `application`.

## GT05_Series

Chuong ve chuoi so, chuoi ham, chuoi luy thua va khai trien ham.

### GT05.01_Numerical_Series

Mo ta: Xet hoi tu/phan ky cua chuoi so.

Dau hieu nhan dien:

- Xuat hien `sum`, `sum_{n=1}^{infinity}`.
- Yeu cau "xet su hoi tu", "hoi tu hay phan ky".

Subtopics:

- `GT05.01.01_Basic_Convergence`: chuoi co ban.
- `GT05.01.02_Comparison_Test`: tieu chuan so sanh.
- `GT05.01.03_Ratio_Root_Test`: D'Alembert va Cauchy.
- `GT05.01.04_Integral_Test`: tieu chuan tich phan.

Skills: `series_convergence`, `limit_computation`, `proof`.

### GT05.02_Absolute_Conditional_Alternating

Mo ta: Hoi tu tuyet doi, hoi tu co dieu kien, chuoi dan dau.

Dau hieu nhan dien:

- Xuat hien `(-1)^n`, `(-1)^{n+1}`.
- Yeu cau xet hoi tu tuyet doi/co dieu kien.

Subtopics:

- `GT05.02.01_Alternating_Series`: chuoi dan dau.
- `GT05.02.02_Absolute_Convergence`: hoi tu tuyet doi.
- `GT05.02.03_Conditional_Convergence`: hoi tu co dieu kien.

Skills: `absolute_conditional_convergence`, `series_convergence`, `proof`.

### GT05.03_Power_Series

Mo ta: Chuoi luy thua va mien/ban kinh hoi tu.

Dau hieu nhan dien:

- Xuat hien `sum a_n (x - x0)^n`.
- Yeu cau tim "ban kinh hoi tu", "mien hoi tu".

Subtopics:

- `GT05.03.01_Radius_Of_Convergence`: ban kinh hoi tu.
- `GT05.03.02_Interval_Of_Convergence`: mien hoi tu.
- `GT05.03.03_Operations_On_Power_Series`: dao ham/tich phan chuoi luy thua.

Skills: `power_series`, `series_convergence`, `limit_computation`.

### GT05.04_Taylor_Maclaurin

Mo ta: Khai trien Taylor, Maclaurin va ung dung xap xi.

Dau hieu nhan dien:

- Tu khoa: "Taylor", "Maclaurin", "khai trien", "xap xi".
- Ham can khai trien quanh `x=0` hoac `x=a`.

Subtopics:

- `GT05.04.01_Maclaurin_Series`: khai trien Maclaurin.
- `GT05.04.02_Taylor_Series`: khai trien Taylor.
- `GT05.04.03_Error_Estimation`: uoc luong sai so.

Skills: `taylor_maclaurin`, `higher_order_derivative`, `differential_approximation`, `application`.

### GT05.05_Fourier_Series

Mo ta: Chuoi Fourier cua ham tuan hoan.

Dau hieu nhan dien:

- Tu khoa: "Fourier", "ham chan/le", "chu ky".
- Yeu cau tim he so Fourier.

Subtopics:

- `GT05.05.01_Fourier_Coefficients`: he so Fourier.
- `GT05.05.02_Even_Odd_Functions`: ham chan/le.
- `GT05.05.03_Sine_Cosine_Series`: chuoi sin/cos.

Skills: `fourier_series`, `definite_integral`, `proof`.

## Classification Prompt Template

Co the dua doan prompt sau vao service phan loai:

```text
You are a Calculus question classifier.

Use only the taxonomy below to classify the question.
Return valid JSON only, with this schema:
{
  "subject": "Calculus",
  "chapter": "...",
  "topic": "...",
  "subtopic": "...",
  "skills": ["..."],
  "difficulty": "easy|medium|hard",
  "confidence": 0.0,
  "reason": "..."
}

Rules:
- Choose the most specific matching subtopic.
- Use only skill names from the Skill Vocabulary.
- If multiple topics match, choose the topic required by the main solving method.
- Difficulty must follow the Difficulty Rubric.
- If confidence is below 0.6, still choose the closest topic and explain uncertainty.

Question:
{question_statement}

Solution if available:
{question_solution}

Answer if available:
{question_answer}

Extracted formulas:
{question_formulas}
```

## Example Classifications

### Example 1

Question:

```text
Tinh tich phan bat dinh \int x^2 e^x dx.
```

Expected classification:

```json
{
  "subject": "Calculus",
  "chapter": "GT03_Integrals",
  "topic": "GT03.03_Integration_By_Parts",
  "subtopic": "GT03.03.02_Repeated_By_Parts",
  "skills": ["integration_by_parts", "indefinite_integral", "algebraic_transformation"],
  "difficulty": "medium",
  "confidence": 0.92,
  "reason": "Bai tich phan dang da thuc nhan ham mu, can dung tich phan tung phan lap lai."
}
```

### Example 2

Question:

```text
Cho f(x) = ln(sin^2 x + 1). Tinh f'(x).
```

Expected classification:

```json
{
  "subject": "Calculus",
  "chapter": "GT02_Derivatives_Differentials",
  "topic": "GT02.02_Chain_Rule",
  "subtopic": "GT02.02.03_Composite_Trig_Log_Exp",
  "skills": ["chain_rule", "derivative_computation", "algebraic_transformation"],
  "difficulty": "medium",
  "confidence": 0.9,
  "reason": "Ham logarit long voi ham luong giac va binh phuong, trong tam la dao ham ham hop."
}
```

### Example 3

Question:

```text
Xet su hoi tu cua chuoi \sum_{n=2}^{\infty} (-1)^n/(n ln n).
```

Expected classification:

```json
{
  "subject": "Calculus",
  "chapter": "GT05_Series",
  "topic": "GT05.02_Absolute_Conditional_Alternating",
  "subtopic": "GT05.02.01_Alternating_Series",
  "skills": ["absolute_conditional_convergence", "series_convergence", "proof"],
  "difficulty": "hard",
  "confidence": 0.88,
  "reason": "Chuoi co nhan (-1)^n va can xet hoi tu co dieu kien/tuyet doi."
}
```

