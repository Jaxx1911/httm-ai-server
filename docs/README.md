# HTTM - ViT5 Text Summarization Server

Server API để train/re-train model ViT5 và tóm tắt văn bản tiếng Việt.

## Tính năng

1. **Train/Re-train Model ViT5**: Train model với dữ liệu tùy chỉnh
2. **Tóm tắt văn bản**: Sinh tiêu đề và tóm tắt cho văn bản đầu vào

## Cấu trúc thư mục

```
HTTM/
├── db.py              # Cấu hình PostgreSQL và models
├── model.py           # Logic train và summarize với ViT5
├── server.py          # FastAPI server với các endpoint
├── main.py            # File chính (nếu cần)
└── README.md          # File này
```

## Yêu cầu

- Python 3.8+
- PostgreSQL database
- GPU (khuyến nghị) hoặc CPU

## Cài đặt

### 1. Cài đặt PostgreSQL

Trên macOS:
```bash
brew install postgresql
brew services start postgresql
```

Tạo database:
```bash
createdb httm_db
```

### 2. Cấu hình Database

Mở file `db.py` và cập nhật chuỗi kết nối:
```python
DATABASE_URL = "postgresql://username:password@localhost:5432/httm_db"
```

Thay `username` và `password` bằng thông tin PostgreSQL của bạn.

### 3. Cài đặt thư viện Python

Các thư viện đã được cài đặt:
- fastapi
- uvicorn
- sqlalchemy
- psycopg2-binary
- transformers
- torch
- datasets
- accelerate

## Chạy server

```bash
python server.py
```

Hoặc:
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: http://localhost:8000

## API Endpoints

### 1. POST /train - Train/Re-train Model

Train hoặc re-train model ViT5 với dữ liệu được cung cấp.

**Request:**
```json
{
  "train_data": [
    {
      "input_text": "Văn bản đầy đủ cần tóm tắt...",
      "target_text": "Tóm tắt của văn bản..."
    },
    {
      "input_text": "Văn bản khác...",
      "target_text": "Tóm tắt khác..."
    }
  ],
  "parameters": {
    "learning_rate": 5e-5,
    "epochs": 3,
    "batch_size": 4,
    "save_steps": 500
  }
}
```

**Response:**
```json
{
  "train_session_id": 1,
  "status": "running",
  "message": "Training started in background"
}
```

### 2. GET /train/{session_id} - Kiểm tra trạng thái train

Lấy thông tin trạng thái của phiên train.

**Response:**
```json
{
  "train_session_id": 1,
  "status": "finished",
  "started_at": "2025-10-20T10:00:00",
  "finished_at": "2025-10-20T10:30:00",
  "parameters": {
    "learning_rate": 5e-5,
    "epochs": 3,
    "batch_size": 4
  },
  "result": {
    "train_loss": 0.5,
    "train_runtime": "0:30:00",
    "samples": 100,
    "validation_samples": 20,
    "model_path": "./trained_model",
    "metrics": {
      "accuracy": 0.85,
      "precision": 0.82,
      "recall": 0.88,
      "f1_score": 0.85,
      "rouge1_f1": 0.85,
      "rouge2_f1": 0.82,
      "rougeL_f1": 0.88
    }
  },
  "metrics": {
    "accuracy": 0.85,
    "precision": 0.82,
    "recall": 0.88,
    "f1_score": 0.85
  }
}
```

**Giải thích Metrics:**
- **accuracy**: ROUGE-1 F1 score - đo lường overlap của unigram (từ đơn)
- **precision**: ROUGE-2 F1 score - đo lường overlap của bigram (cặp từ liên tiếp)
- **recall**: ROUGE-L F1 score - đo lường longest common subsequence
- **f1_score**: ROUGE-L F1 score - điểm tổng hợp chất lượng tóm tắt

**Lưu ý về đánh giá:**
- Model được đánh giá trên 20% dữ liệu validation (tự động chia từ train_data)
- Metrics được tính dựa trên ROUGE scores - tiêu chuẩn đánh giá cho text summarization
- Các metrics này được lưu vào database cùng với phiên train

### 3. POST /summarize - Tóm tắt văn bản

Nhận văn bản đầu vào, trả về tiêu đề và tóm tắt. Không lưu vào database.

**Request:**
```json
{
  "text": "Văn bản cần tóm tắt. Đây là nội dung dài cần được rút gọn thành phiên bản ngắn hơn..."
}
```

**Response:**
```json
{
  "title": "Tiêu đề được sinh ra",
  "summary": "Tóm tắt nội dung văn bản..."
}
```

## Ví dụ sử dụng với cURL

### Train model:
```bash
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "train_data": [
      {
        "input_text": "Hôm nay trời đẹp, tôi đi dạo công viên.",
        "target_text": "Đi dạo công viên trong ngày đẹp trời"
      }
    ],
    "parameters": {
      "learning_rate": 5e-5,
      "epochs": 2,
      "batch_size": 2
    }
  }'
```

### Kiểm tra trạng thái train:
```bash
curl "http://localhost:8000/train/1"
```

### Tóm tắt văn bản:
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Việt Nam là một quốc gia nằm ở phía đông bán đảo Đông Dương thuộc khu vực Đông Nam Á. Việt Nam có diện tích khoảng 331.212 km² và dân số khoảng 98 triệu người."
  }'
```

## Lưu ý

1. **Model ViT5**: Lần đầu chạy, model sẽ tự động tải về từ HuggingFace (khoảng 1GB)
2. **Training**: Quá trình train chạy trong background, sử dụng endpoint GET /train/{id} để kiểm tra tiến độ
3. **GPU**: Nếu có GPU, model sẽ tự động sử dụng để tăng tốc
4. **Database**: Chỉ lưu thông tin các phiên train, không lưu kết quả tóm tắt

## Phát triển tiếp

- [ ] Thêm quản lý mẫu/nhãn chi tiết
- [ ] Thêm authentication
- [ ] Thêm validation cho input
- [ ] Thêm logging chi tiết
- [ ] Thêm metrics và monitoring

## License

MIT
