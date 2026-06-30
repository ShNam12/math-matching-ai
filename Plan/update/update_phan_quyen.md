# Update phân quyền đăng nhập Admin/User

Ngày cập nhật: 2026-06-29

## 1. Mục tiêu

Triển khai chức năng đăng nhập và phân quyền ở mức đủ demo đồ án cho hệ thống AI Matching.

Thiết kế đã chốt:

- Đăng nhập bằng `username`.
- Seed sẵn 4 tài khoản demo: `admin`, `user1`, `user2`, `user3`.
- Dữ liệu dùng chung cho toàn hệ thống.
- Admin có quyền quản trị, vận hành hệ thống và xem `Analytics`.
- User có quyền khai thác hệ thống, tìm kiếm và xem chi tiết câu hỏi.
- Không làm frontend quản lý tài khoản.
- Tài khoản được tạo bằng seed script hoặc script quản trị.
- Phạm vi triển khai ưu tiên: gọn, rõ, dễ demo và dễ giải thích trong báo cáo.

## 2. Mô hình dữ liệu và phân quyền

Hệ thống sử dụng mô hình dữ liệu tập trung. Tất cả tài liệu, câu hỏi, taxonomy, embedding, kết quả phân loại và kết quả xử lý AI được lưu trong kho dữ liệu chung. Cơ chế phân quyền RBAC được dùng để kiểm soát thao tác của từng vai trò.

Admin và user không có database riêng. Hai vai trò cùng đọc từ một nguồn dữ liệu, nhưng khác nhau ở quyền truy cập chức năng.

Diễn giải dùng trong báo cáo:

> Hệ thống sử dụng mô hình dữ liệu tập trung. Tất cả câu hỏi, tài liệu, taxonomy và kết quả xử lý AI được lưu trong kho dữ liệu chung. Cơ chế phân quyền RBAC được áp dụng để kiểm soát thao tác của từng vai trò: quản trị viên có quyền quản lý và vận hành dữ liệu, trong khi người dùng chỉ có quyền khai thác, tra cứu và xem chi tiết câu hỏi.

## 3. Ma trận quyền

| Chức năng | Admin | User |
| --- | --- | --- |
| Đăng nhập hệ thống | Có | Có |
| Xem Dashboard tổng quan | Có | Có, nếu dashboard chỉ hiển thị thông tin khai thác cơ bản |
| Upload tài liệu | Có | Không |
| Xem trạng thái xử lý tài liệu | Có | Không |
| Xem danh sách câu hỏi | Có | Có |
| Xem chi tiết câu hỏi | Có | Có |
| Xem lời giải/đáp án | Có | Có |
| Semantic Search | Có | Có |
| Formula Search | Có | Có |
| Xem cây tri thức/taxonomy | Có | Có |
| Phân loại taxonomy bằng AI | Có | Không |
| Sinh câu hỏi trắc nghiệm bằng AI | Có | Không |
| Kiểm định chất lượng câu hỏi | Có | Không |
| Xem Analytics | Có | Không |
| Settings | Có | Không |
| Quản lý tài khoản trên frontend | Không triển khai | Không triển khai |

Ghi chú:

- Nếu muốn giảm phạm vi demo, `Dashboard` có thể cho cả hai vai trò xem nhưng ẩn các chỉ số quản trị nhạy cảm.
- `Analytics` nên chỉ admin xem để thể hiện rõ ràng phân quyền.
- User được xem `Problem Detail` vì yêu cầu đã chốt là user được xem chi tiết câu hỏi.

## 4. Luồng đăng nhập

Luồng xử lý đề xuất:

```text
Người dùng nhập username/password
-> Frontend gọi POST /api/v1/auth/login
-> Backend kiểm tra username, password_hash, is_active
-> Backend trả về JWT access token và thông tin user
-> Frontend lưu token
-> Frontend gọi API kèm Authorization: Bearer <token>
-> Backend giải mã token và kiểm tra role ở endpoint cần bảo vệ
```

Thông tin trong JWT nên có:

- `sub`: username hoặc user id.
- `role`: `admin` hoặc `user`.
- `exp`: thời điểm hết hạn token.

Với mức demo đồ án, chỉ cần access token là đủ. Không bắt buộc làm refresh token.

## 5. Thiết kế database

Thêm bảng `users`.

Các trường đề xuất:

| Trường | Kiểu dữ liệu | Ghi chú |
| --- | --- | --- |
| `id` | UUID hoặc integer | Khóa chính |
| `username` | string | Unique, dùng để đăng nhập |
| `password_hash` | string | Mật khẩu đã hash, không lưu mật khẩu thô |
| `full_name` | string | Tên hiển thị |
| `role` | string | `admin` hoặc `user` |
| `is_active` | boolean | Cho phép khóa tài khoản nếu cần |
| `created_at` | datetime | Thời điểm tạo |
| `updated_at` | datetime | Thời điểm cập nhật |

Ràng buộc nên có:

- `username` unique.
- `role` chỉ nhận `admin` hoặc `user`.
- `is_active` mặc định là `true`.

Không cần thêm `user_id` vào bảng `documents` hoặc `questions` vì dữ liệu dùng chung.

## 6. Tài khoản demo

Seed sẵn 4 tài khoản:

| Username | Role | Mục đích |
| --- | --- | --- |
| `admin` | `admin` | Quản trị, vận hành, upload, generation, analytics |
| `user1` | `user` | Demo người dùng khai thác hệ thống |
| `user2` | `user` | Demo người dùng khai thác hệ thống |
| `user3` | `user` | Demo người dùng khai thác hệ thống |

Mật khẩu demo nên đặt trong `.env` hoặc seed script, ví dụ:

```text
admin / Admin@123
user1 / User@123
user2 / User@123
user3 / User@123
```

Lưu ý:

- Đây chỉ là mật khẩu demo cho đồ án.
- Khi viết báo cáo, nên nói hệ thống lưu `password_hash`, không lưu mật khẩu gốc.
- Không commit mật khẩu production. Với demo local có thể ghi rõ trong README hoặc tài liệu chạy demo.

## 7. Backend cần triển khai

### 7.1. Thư viện cần dùng

Các thư viện thường dùng:

- `passlib[bcrypt]` hoặc `bcrypt`: hash mật khẩu.
- `python-jose[cryptography]` hoặc `PyJWT`: tạo và kiểm tra JWT.
- `python-multipart`: nếu dùng OAuth2 form login của FastAPI.

Với dự án hiện tại, nên kiểm tra `requirements.txt` trước. Nếu thiếu thì bổ sung tối thiểu:

```text
passlib[bcrypt]
python-jose[cryptography]
```

### 7.2. Cấu hình môi trường

Bổ sung vào `.env.example`:

```text
JWT_SECRET_KEY=change-me-for-demo
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=480
```

Với demo, token hết hạn sau 8 giờ là hợp lý.

### 7.3. Model database

Bổ sung model `User` trong khu vực model database hiện có.

Các điểm cần chú ý:

- `username` unique.
- `password_hash` bắt buộc.
- `role` bắt buộc.
- `is_active` mặc định `true`.

Nếu dự án chưa dùng Alembic, có thể tạo script migration thủ công tương tự các script hiện có trong thư mục `scripts/`.

### 7.4. Repository user

Tạo repository thao tác với bảng `users`:

- Lấy user theo `username`.
- Tạo user nếu chưa tồn tại.
- Kiểm tra username đã tồn tại.

Vì không làm UI quản lý tài khoản, repository chỉ cần đủ cho login và seed.

### 7.5. Service xác thực

Tạo auth service gồm các nhiệm vụ:

- Hash password.
- Verify password.
- Tạo access token.
- Decode token.
- Lấy current user từ token.
- Kiểm tra role.

Các dependency nên có:

- `get_current_user`
- `require_admin`
- `require_roles(["admin", "user"])` nếu muốn tổng quát

### 7.6. API auth

Tạo router auth:

```text
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

`POST /api/v1/auth/login`

Input:

```json
{
  "username": "admin",
  "password": "Admin@123"
}
```

Output:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "full_name": "Administrator",
    "role": "admin"
  }
}
```

`GET /api/v1/auth/me`

Output:

```json
{
  "username": "admin",
  "full_name": "Administrator",
  "role": "admin",
  "is_active": true
}
```

### 7.7. Bảo vệ endpoint hiện có

Nhóm endpoint admin nên yêu cầu `require_admin`:

- Upload tài liệu.
- Xử lý ingestion.
- Phân loại document/question bằng AI.
- Sinh câu hỏi.
- Lưu generated question.
- Kiểm định chất lượng.
- Analytics.
- Settings hoặc endpoint cấu hình nếu có.

Nhóm endpoint user/admin đều xem được:

- Search.
- Taxonomy.
- Danh sách câu hỏi.
- Chi tiết câu hỏi.
- Health/readiness có thể để public hoặc yêu cầu login tùy mục tiêu demo.

Nguyên tắc triển khai:

- Backend vẫn là lớp bảo vệ chính.
- Frontend chỉ ẩn menu và điều hướng, không được coi là bảo mật chính.

## 8. Seed script tài khoản demo

Tạo script, ví dụ:

```text
scripts/seed_demo_users.py
```

Nhiệm vụ:

- Kết nối database theo cấu hình hiện có.
- Tạo bảng nếu cần, hoặc yêu cầu đã chạy migration trước.
- Tạo/cập nhật 4 tài khoản demo.
- Hash mật khẩu trước khi lưu.
- Nếu user đã tồn tại thì không tạo trùng.

Hành vi đề xuất:

```text
python scripts/seed_demo_users.py
```

Output mong muốn:

```text
Created user: admin
Created user: user1
Created user: user2
Created user: user3
Seed demo users completed.
```

Nếu chạy lại:

```text
User already exists: admin
User already exists: user1
User already exists: user2
User already exists: user3
Seed demo users completed.
```

Với demo, script nên idempotent, tức là chạy nhiều lần không làm hỏng dữ liệu.

## 9. Frontend cần triển khai

### 9.1. Trang Login

Thêm màn hình đăng nhập gồm:

- Ô `username`.
- Ô `password`.
- Nút đăng nhập.
- Thông báo lỗi khi sai tài khoản hoặc mật khẩu.

Không cần chức năng đăng ký.

### 9.2. Lưu trạng thái đăng nhập

Frontend cần lưu:

- `access_token`.
- Thông tin user: `username`, `full_name`, `role`.

Với demo, có thể lưu token trong `localStorage`. Khi trình bày báo cáo, có thể ghi đây là giải pháp đơn giản phục vụ demo; nếu production thì cân nhắc httpOnly cookie.

### 9.3. API client

Sửa API client để tự động gắn header:

```text
Authorization: Bearer <access_token>
```

Nếu API trả về `401`, frontend xóa token và chuyển về trang login.

Nếu API trả về `403`, frontend hiển thị thông báo không có quyền hoặc chuyển về trang phù hợp.

### 9.4. Route guard

Các route cần đăng nhập:

- Dashboard.
- Upload Document.
- Semantic Search.
- Calculus Taxonomy.
- QA Rules.
- Problem Detail.
- GenVariants.
- Analytics.
- Settings.

Route chỉ admin:

- Upload Document.
- QA Rules nếu dùng để kiểm định/quản trị.
- GenVariants.
- Analytics.
- Settings.

Route user/admin:

- Dashboard, nếu dashboard không chứa số liệu quản trị nhạy cảm.
- Semantic Search.
- Calculus Taxonomy.
- Problem Detail.

### 9.5. Menu theo role

Admin nhìn thấy:

- Dashboard.
- Upload Document.
- Semantic Search.
- Calculus Taxonomy.
- QA Rules.
- GenVariants.
- Analytics.
- Settings.

User nhìn thấy:

- Dashboard.
- Semantic Search.
- Calculus Taxonomy.
- Problem Detail thông qua kết quả tìm kiếm.

Nên có khu vực nhỏ hiển thị:

```text
admin - Quản trị viên
```

hoặc:

```text
user1 - Người dùng
```

và nút đăng xuất.

## 10. Kiểm thử bắt buộc

### 10.1. Backend unit/service test

Test cần có:

- Hash password không trả về mật khẩu thô.
- Verify password đúng/sai.
- Login đúng trả về token.
- Login sai mật khẩu trả về lỗi.
- Login user không tồn tại trả về lỗi.
- Token hợp lệ lấy được current user.
- Token sai/hết hạn bị từ chối.
- User inactive bị từ chối.

### 10.2. API test phân quyền

Test API nên bao phủ:

- Không có token gọi endpoint cần login -> `401`.
- User gọi endpoint admin -> `403`.
- Admin gọi endpoint admin -> thành công.
- User gọi search/taxonomy/question detail -> thành công.
- Admin gọi analytics -> thành công.
- User gọi analytics -> `403`.

### 10.3. Frontend test thủ công

Checklist demo:

- Đăng nhập bằng `admin` thành công.
- Admin thấy menu Analytics.
- Admin vào Analytics được.
- Đăng xuất.
- Đăng nhập bằng `user1` thành công.
- User không thấy menu Analytics.
- User truy cập trực tiếp URL Analytics bị chặn.
- User tìm kiếm câu hỏi được.
- User xem chi tiết câu hỏi được.

## 11. Kế hoạch triển khai theo bước

### Bước 1 - Thiết kế auth và database

Mục tiêu:

- Thêm model/table `users`.
- Bổ sung cấu hình JWT.
- Chuẩn hóa role `admin`, `user`.

Kết quả:

- Database có bảng `users`.
- Có thể tạo user bằng repository hoặc script.

Ước lượng: 0.5 ngày.

### Bước 2 - Backend login và JWT

Mục tiêu:

- Thêm auth service.
- Thêm endpoint login và me.
- Thêm dependency lấy current user.

Kết quả:

- Đăng nhập bằng username/password.
- Nhận access token.
- Gọi `/auth/me` lấy thông tin người dùng.

Ước lượng: 0.5 - 1 ngày.

### Bước 3 - Seed demo users

Mục tiêu:

- Tạo script seed 1 admin và 3 user.
- Script chạy lại nhiều lần không tạo trùng dữ liệu.

Kết quả:

- Có sẵn tài khoản demo để trình bày.

Ước lượng: 0.5 ngày.

### Bước 4 - Gắn phân quyền backend

Mục tiêu:

- Bảo vệ endpoint quản trị bằng `require_admin`.
- Cho phép user truy cập search, taxonomy và question detail.

Kết quả:

- User không gọi được API admin.
- Admin dùng được toàn bộ chức năng quản trị.

Ước lượng: 0.5 - 1 ngày.

### Bước 5 - Frontend login và route guard

Mục tiêu:

- Thêm trang login.
- Lưu token.
- Gắn token vào API request.
- Ẩn/hiện menu theo role.
- Chặn route theo role.

Kết quả:

- Admin và user có trải nghiệm khác nhau trên giao diện.

Ước lượng: 1 - 1.5 ngày.

### Bước 6 - Test và cập nhật tài liệu

Mục tiêu:

- Chạy test backend.
- Test thủ công frontend.
- Cập nhật README hoặc báo cáo.

Kết quả:

- Có thể demo luồng đăng nhập và phân quyền.

Ước lượng: 0.5 - 1 ngày.

Tổng thời gian đề xuất: 3 - 5 ngày.

Nếu chỉ cần demo nhanh, có thể hoàn thành trong 2 - 3 ngày bằng cách giảm test tự động và chỉ kiểm thử thủ công. Tuy nhiên nên giữ một số test API quan trọng để tránh lỗi phân quyền.

## 12. Tiêu chí hoàn thành

Một bản triển khai được xem là hoàn thành khi:

- Có bảng `users`.
- Có seed script tạo `admin`, `user1`, `user2`, `user3`.
- Đăng nhập bằng username/password thành công.
- API trả về JWT token.
- Frontend lưu token và gọi API kèm token.
- Admin thấy và truy cập được Analytics.
- User không thấy và không truy cập được Analytics.
- User xem được search, taxonomy và chi tiết câu hỏi.
- Endpoint admin bị chặn với user ở backend.
- README hoặc báo cáo có mô tả mô hình dữ liệu dùng chung và RBAC.

## 13. Rủi ro và lưu ý

### 13.1. Chỉ ẩn menu frontend là chưa đủ

Frontend chỉ giúp trải nghiệm người dùng. Bảo mật thật phải nằm ở backend. Nếu chỉ ẩn menu Analytics nhưng API Analytics vẫn cho user gọi trực tiếp thì phân quyền chưa đúng.

### 13.2. Không lưu mật khẩu thô

Mật khẩu phải được hash trước khi lưu vào database. Đây là điểm quan trọng khi bảo vệ báo cáo.

### 13.3. Không mở rộng sang dữ liệu riêng từng user

Không thêm `user_id` vào documents/questions trong phạm vi này. Nếu làm dữ liệu riêng từng user, hệ thống sẽ phức tạp hơn nhiều và không cần thiết cho mục tiêu demo hiện tại.

### 13.4. Không làm quản lý tài khoản frontend

Không cần màn hình thêm/sửa/xóa user. Tài khoản demo được tạo bằng seed script. Đây là quyết định giúp giảm thời gian triển khai và vẫn phù hợp với mô hình demo đồ án.

## 14. Nội dung có thể đưa vào báo cáo

### 14.1. Mô tả tác nhân

| Tác nhân | Vai trò | Quyền chính |
| --- | --- | --- |
| Quản trị viên | Quản lý dữ liệu và vận hành hệ thống | Quản lý tài liệu, câu hỏi, cây tri thức; thực hiện hoặc kiểm tra kết quả AI Matching; xem thống kê và theo dõi trạng thái xử lý |
| Người dùng | Khai thác hệ thống phục vụ tra cứu và học tập | Xem cây tri thức, tìm kiếm ngữ nghĩa câu hỏi, tìm kiếm tương đồng công thức, xem chi tiết câu hỏi và kết quả phân loại |

### 14.2. Mô tả cơ chế xác thực

Hệ thống bổ sung cơ chế đăng nhập bằng username và password. Mật khẩu người dùng được mã hóa một chiều trước khi lưu vào cơ sở dữ liệu. Sau khi đăng nhập thành công, backend cấp JWT access token cho frontend. Token này được gửi kèm trong các request tiếp theo để xác định danh tính và vai trò của người dùng.

### 14.3. Mô tả cơ chế phân quyền

Hệ thống áp dụng RBAC với hai vai trò chính: `admin` và `user`. Admin có quyền quản trị và vận hành toàn bộ pipeline xử lý dữ liệu, bao gồm upload tài liệu, sinh câu hỏi, kiểm định chất lượng và xem analytics. User chỉ có quyền khai thác dữ liệu dùng chung thông qua tìm kiếm, xem taxonomy và xem chi tiết câu hỏi.

### 14.4. Mô tả quản lý tài khoản

Trong phạm vi demo đồ án, hệ thống không xây dựng giao diện quản lý tài khoản riêng. Các tài khoản demo được khởi tạo bằng seed script quản trị, gồm một tài khoản admin và ba tài khoản user. Cách tiếp cận này giúp giảm độ phức tạp giao diện nhưng vẫn chứng minh được cơ chế xác thực và phân quyền.

## 15. Kịch bản demo đề xuất

Kịch bản 1: Admin đăng nhập

```text
1. Mở trang login.
2. Đăng nhập bằng admin.
3. Kiểm tra menu có Upload, Generation, Analytics, Settings.
4. Vào Analytics thành công.
5. Vào Upload Document thành công.
```

Kịch bản 2: User đăng nhập

```text
1. Đăng xuất admin.
2. Đăng nhập bằng user1.
3. Kiểm tra menu không có Analytics, Upload, Settings.
4. Vào Semantic Search và tìm câu hỏi.
5. Mở chi tiết câu hỏi.
6. Thử truy cập trực tiếp URL Analytics và xác nhận bị chặn.
```

Kịch bản 3: Chứng minh dữ liệu dùng chung

```text
1. Admin xem hoặc thêm dữ liệu câu hỏi.
2. User đăng nhập và tìm kiếm trong cùng ngân hàng câu hỏi.
3. Giải thích rằng dữ liệu được dùng chung, còn quyền thao tác được kiểm soát theo vai trò.
```

