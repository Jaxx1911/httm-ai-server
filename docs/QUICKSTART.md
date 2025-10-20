# Quick Start Guide

Hướng dẫn khởi động nhanh HTTM Server

## Bước 1: Cài đặt PostgreSQL

### macOS:
```bash
brew install postgresql@15
brew services start postgresql@15
createdb httm_db
```

Chi tiết xem file `POSTGRES_SETUP.md`

## Bước 2: Cấu hình Database

Tạo file `.env` từ template:
```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:
```bash
# Thay your_username bằng username macOS của bạn (chạy 'whoami')
DATABASE_URL=postgresql://your_username@localhost:5432/httm_db
```

## Bước 3: Khởi tạo Database Tables

```bash
python init_db.py
```

Kết quả thành công:
```
✓ Đã tạo thành công các bảng:
  - train_sessions
✓ Kết nối database thành công!
```

## Bước 4: Khởi động Server

```bash
python server.py
```

Server sẽ chạy tại: http://localhost:8000

Mở trình duyệt và truy cập API docs: http://localhost:8000/docs

## Bước 5: Test API

### Mở terminal mới và chạy:
```bash
python test_api.py
```

### Hoặc dùng cURL để test tóm tắt văn bản:
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Việt Nam là một quốc gia nằm ở phía đông bán đảo Đông Dương thuộc khu vực Đông Nam Á. Việt Nam có diện tích khoảng 331.212 km² và dân số khoảng 98 triệu người."
  }'
```

## Các lệnh hữu ích

### Kiểm tra PostgreSQL
```bash
brew services list | grep postgresql
psql httm_db
```

### Xem danh sách train sessions
```bash
psql httm_db -c "SELECT * FROM train_sessions;"
```

### Restart server
```bash
# Ctrl+C để dừng server
python server.py  # Khởi động lại
```

## Cấu trúc Project

```
HTTM/
├── db.py                 # Database models và connection
├── model.py              # ViT5 model logic (train + evaluate + summarize)
├── server.py             # FastAPI server
├── init_db.py            # Script khởi tạo database
├── migrate_db.py         # Script migration (thêm metrics columns)
├── test_api.py           # Script test API
├── requirements.txt      # Python dependencies
├── .env                  # Cấu hình (tạo từ .env.example)
├── README.md             # Documentation đầy đủ
├── POSTGRES_SETUP.md     # Hướng dẫn PostgreSQL chi tiết
├── METRICS_GUIDE.md      # Hướng dẫn về metrics đánh giá
└── QUICKSTART.md         # File này
```

## Endpoints

1. **POST /summarize** - Tóm tắt văn bản (trả về title + summary)
2. **POST /train** - Train/re-train model ViT5 (tự động đánh giá metrics)
3. **GET /train/{id}** - Kiểm tra trạng thái train và xem metrics

Xem chi tiết tại: http://localhost:8000/docs

## Metrics Đánh Giá

Sau khi train, model được tự động đánh giá với các metrics:
- **Accuracy** (ROUGE-1 F1): Tỷ lệ từ đúng
- **Precision** (ROUGE-2 F1): Chất lượng cặp từ
- **Recall** (ROUGE-L F1): Giữ lại thông tin quan trọng
- **F1 Score**: Điểm tổng hợp

Xem chi tiết tại: `METRICS_GUIDE.md`

## Troubleshooting

### Lỗi kết nối database
```bash
# Kiểm tra PostgreSQL có chạy
brew services list | grep postgresql

# Restart
brew services restart postgresql@15
```

### Lỗi import model
Lần đầu chạy, model ViT5 sẽ tự động tải về (khoảng 1GB).
Đảm bảo có kết nối internet.

### Lỗi memory khi train
Giảm batch_size trong parameters:
```json
{
  "parameters": {
    "batch_size": 2
  }
}
```

## Next Steps

- Đọc `README.md` để hiểu chi tiết API
- Xem `POSTGRES_SETUP.md` để cấu hình nâng cao
- Tùy chỉnh model trong `model.py`
- Thêm authentication nếu deploy production
