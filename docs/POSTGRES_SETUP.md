# Hướng dẫn cấu hình PostgreSQL

## Cài đặt PostgreSQL trên macOS

### 1. Cài đặt PostgreSQL
```bash
brew install postgresql@15
```

### 2. Khởi động PostgreSQL
```bash
brew services start postgresql@15
```

### 3. Tạo database
```bash
# Tạo database tên httm_db
createdb httm_db
```

### 4. Tạo user và cấp quyền (tuỳ chọn)

Nếu muốn tạo user riêng:

```bash
# Mở psql
psql postgres

# Trong psql, chạy các lệnh sau:
CREATE USER httm_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE httm_db TO httm_user;
\q
```

### 5. Cấu hình connection string

Tạo file `.env` từ `.env.example`:
```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:
```
# Nếu dùng user mặc định (không có password)
DATABASE_URL=postgresql://your_username@localhost:5432/httm_db

# Nếu tạo user riêng
DATABASE_URL=postgresql://httm_user:your_password@localhost:5432/httm_db
```

Thay `your_username` bằng username macOS của bạn (chạy `whoami` để xem).

### 6. Kiểm tra kết nối

```bash
psql httm_db
```

Nếu kết nối thành công, bạn sẽ thấy prompt:
```
httm_db=#
```

Gõ `\q` để thoát.

## Troubleshooting

### Lỗi: role không tồn tại
```bash
createuser -s your_username
```

### Lỗi: không kết nối được
```bash
# Kiểm tra PostgreSQL có chạy không
brew services list | grep postgresql

# Restart PostgreSQL
brew services restart postgresql@15
```

### Lỗi: database đã tồn tại
```bash
# Xóa database cũ
dropdb httm_db

# Tạo lại
createdb httm_db
```

## Xem danh sách databases
```bash
psql -l
```

## Kiểm tra tables trong database
```bash
psql httm_db

# Trong psql:
\dt

# Xem cấu trúc bảng train_sessions
\d train_sessions
```
