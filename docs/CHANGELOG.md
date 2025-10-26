# Changelog - Thêm tính năng đánh giá Metrics

## Ngày: 20/10/2025

### ✨ Tính năng mới

#### 1. Tự động đánh giá model sau khi train
- Model được tự động đánh giá trên validation set (20% dữ liệu)
- Tính các metrics: Accuracy, Precision, Recall, F1 Score
- Sử dụng ROUGE scores - tiêu chuẩn cho text summarization

#### 2. Lưu metrics vào database
- Thêm 4 cột mới vào bảng `train_sessions`:
  - `accuracy` (FLOAT)
  - `precision` (FLOAT)
  - `recall` (FLOAT)
  - `f1_score` (FLOAT)

#### 3. API trả về metrics
- Endpoint `GET /train/{id}` giờ trả về metrics trong response
- Hiển thị metrics chi tiết khi train hoàn thành

### 📝 Files đã thay đổi

#### db.py
- Thêm 4 cột metrics vào model `TrainSession`
- Hỗ trợ đọc DATABASE_URL từ biến môi trường

#### model.py
- Thêm hàm `evaluate_model()` để đánh giá model
- Cập nhật hàm `train_model()`:
  - Tự động chia dữ liệu train/validation (80/20)
  - Gọi evaluate sau khi train
  - Trả về metrics trong result
- Sử dụng ROUGE scores để đánh giá:
  - ROUGE-1 → Accuracy
  - ROUGE-2 → Precision
  - ROUGE-L → Recall & F1

#### server.py
- Cập nhật `train_in_background()` để lưu metrics vào DB
- Cập nhật `get_train_status()` để trả về metrics

#### test_api.py
- Hiển thị metrics khi test train endpoint

#### requirements.txt
- Thêm: scikit-learn, rouge-score, nltk, numpy

### 📚 Files mới

#### migrate_db.py
- Script để migration database cũ
- Thêm các cột metrics nếu chưa có

#### METRICS_GUIDE.md
- Hướng dẫn chi tiết về các metrics
- Giải thích ROUGE scores
- Cách hiểu và cải thiện kết quả
- Benchmark cho tiếng Việt

### 🔧 Cách sử dụng

#### Cho database mới:
```bash
python init_db.py
```

#### Cho database đã có:
```bash
python migrate_db.py
```

#### Train với đánh giá tự động:
```bash
# Gửi request với ít nhất 5 samples
# Dữ liệu sẽ tự động chia 80% train / 20% validation
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "train_data": [
      {"input_text": "...", "target_text": "..."},
      {"input_text": "...", "target_text": "..."},
      ...
    ],
    "parameters": {"epochs": 3}
  }'
```

#### Xem metrics:
```bash
curl "http://localhost:8000/train/1"
```

Response:
```json
{
  "metrics": {
    "accuracy": 0.75,
    "precision": 0.65,
    "recall": 0.70,
    "f1_score": 0.70
  }
}
```

### 📊 Ý nghĩa Metrics

- **Accuracy (ROUGE-1)**: Tỷ lệ từ được giữ lại đúng (> 0.4 là tốt)
- **Precision (ROUGE-2)**: Chất lượng cặp từ liên tiếp (> 0.2 là tốt)
- **Recall (ROUGE-L)**: Giữ lại thông tin quan trọng (> 0.3 là tốt)
- **F1 Score**: Điểm tổng hợp chất lượng tóm tắt

### 🎯 Lưu ý

1. **Dữ liệu tối thiểu**: Cần ít nhất 5 samples để chia train/val
2. **Validation set**: Tự động lấy 20% dữ liệu
3. **ROUGE scores**: Metrics chuẩn cho text summarization
4. **Database**: Metrics được lưu cùng phiên train

### 📖 Tài liệu

- `METRICS_GUIDE.md` - Giải thích chi tiết về metrics
- `README.md` - Đã cập nhật với thông tin metrics
- `QUICKSTART.md` - Đã cập nhật với metrics

### 🚀 Migration

Nếu bạn đã có database từ phiên bản cũ:

```bash
# Bước 1: Backup database (khuyến nghị)
pg_dump httm_db > backup.sql

# Bước 2: Chạy migration
python migrate_db.py

# Bước 3: Verify
python init_db.py
```

### 🐛 Troubleshooting

**Lỗi: column "accuracy" does not exist**
→ Chạy: `python migrate_db.py`

**Metrics = null trong response**
→ Đảm bảo có ít nhất 5 samples trong train_data

**ROUGE scores thấp**
→ Xem `METRICS_GUIDE.md` để biết cách cải thiện

### 💡 Tips

1. Càng nhiều dữ liệu train, metrics càng chính xác
2. Validation set giúp phát hiện overfitting
3. F1 score là metric chính để so sánh các phiên train
4. Xem database để tìm model tốt nhất:
   ```sql
   SELECT id, f1_score FROM train_sessions 
   WHERE status='finished' 
   ORDER BY f1_score DESC 
   LIMIT 5;
   ```
