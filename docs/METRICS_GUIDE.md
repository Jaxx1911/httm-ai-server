# Hướng dẫn về Metrics Đánh Giá Model

## Tổng quan

Sau khi train model ViT5, hệ thống tự động đánh giá chất lượng model trên validation set (20% dữ liệu) và tính các metrics:

- **Accuracy** (ROUGE-1 F1)
- **Precision** (ROUGE-2 F1)
- **Recall** (ROUGE-L F1)
- **F1 Score** (ROUGE-L F1)

Các metrics này được lưu vào database cùng với phiên train để theo dõi hiệu suất model qua các lần train.

## ROUGE Scores

ROUGE (Recall-Oriented Understudy for Gisting Evaluation) là tiêu chuẩn đánh giá cho text summarization.

### ROUGE-1 (Accuracy)
- **Định nghĩa**: Đo overlap của unigrams (từ đơn) giữa summary sinh ra và summary tham chiếu
- **Ý nghĩa**: Cao = model giữ được nhiều từ quan trọng từ văn bản gốc
- **Giá trị tốt**: > 0.4

**Ví dụ:**
```
Reference: "Hôm nay trời đẹp"
Generated: "Trời đẹp hôm nay"
ROUGE-1: 1.0 (100% từ match)
```

### ROUGE-2 (Precision)
- **Định nghĩa**: Đo overlap của bigrams (cặp từ liên tiếp)
- **Ý nghĩa**: Cao = model giữ được thứ tự từ và cấu trúc câu tốt
- **Giá trị tốt**: > 0.2

**Ví dụ:**
```
Reference: "hôm nay | nay trời | trời đẹp"
Generated: "trời đẹp | đẹp hôm | hôm nay"
ROUGE-2: 0.33 (1/3 bigrams match)
```

### ROUGE-L (Recall & F1)
- **Định nghĩa**: Đo longest common subsequence (chuỗi con chung dài nhất)
- **Ý nghĩa**: Cao = model giữ được cấu trúc và ý nghĩa tốt
- **Giá trị tốt**: > 0.3

**Ví dụ:**
```
Reference: "A B C D E"
Generated: "A C D F"
LCS: "A C D" (length 3)
ROUGE-L: 0.6 (3/5)
```

## Mapping với Metrics truyền thống

### Accuracy ← ROUGE-1 F1
Đo lường tỷ lệ từ đúng trong tóm tắt

### Precision ← ROUGE-2 F1
Đo lường chất lượng cặp từ liên tiếp (phrase quality)

### Recall ← ROUGE-L F1
Đo lường khả năng giữ lại thông tin quan trọng

### F1 Score ← ROUGE-L F1
Điểm tổng hợp chất lượng tóm tắt

## Cách hiểu kết quả

### Ví dụ kết quả tốt:
```json
{
  "accuracy": 0.75,   // ROUGE-1: Giữ được 75% từ quan trọng
  "precision": 0.65,  // ROUGE-2: 65% cặp từ đúng
  "recall": 0.70,     // ROUGE-L: 70% cấu trúc đúng
  "f1_score": 0.70    // Điểm tổng hợp
}
```

### Ví dụ kết quả chưa tốt:
```json
{
  "accuracy": 0.35,   // Chỉ giữ được 35% từ
  "precision": 0.15,  // Cặp từ không chính xác
  "recall": 0.25,     // Mất nhiều thông tin
  "f1_score": 0.25    // Cần train thêm
}
```

## Benchmark

### Cho tiếng Việt:
- **Tốt**: ROUGE-L > 0.40
- **Chấp nhận được**: ROUGE-L > 0.30
- **Cần cải thiện**: ROUGE-L < 0.30

### So sánh với các model SOTA:
- ViT5-base: ROUGE-L ~ 0.35-0.45
- mBART: ROUGE-L ~ 0.30-0.40
- mT5: ROUGE-L ~ 0.32-0.42

## Cách cải thiện Metrics

### 1. Tăng dữ liệu train
```python
# Cần ít nhất 1000+ samples cho kết quả tốt
train_data = [...]  # More data
```

### 2. Tăng epochs
```python
parameters = {
    "epochs": 5,  # Thay vì 3
}
```

### 3. Điều chỉnh learning rate
```python
parameters = {
    "learning_rate": 3e-5,  # Thử các giá trị khác nhau
}
```

### 4. Tăng batch size (nếu có GPU đủ mạnh)
```python
parameters = {
    "batch_size": 8,  # Thay vì 4
}
```

## Xem Metrics trong Database

```bash
# Xem tất cả phiên train với metrics
psql httm_db -c "SELECT id, status, accuracy, precision, recall, f1_score FROM train_sessions ORDER BY id DESC LIMIT 10;"
```

```bash
# Tìm phiên train tốt nhất
psql httm_db -c "SELECT id, f1_score FROM train_sessions WHERE status='finished' ORDER BY f1_score DESC LIMIT 5;"
```

## API Response với Metrics

Khi gọi `GET /train/{id}` với phiên train đã hoàn thành:

```json
{
  "train_session_id": 1,
  "status": "finished",
  "metrics": {
    "accuracy": 0.75,
    "precision": 0.65,
    "recall": 0.70,
    "f1_score": 0.70
  },
  "result": {
    "metrics": {
      "rouge1_f1": 0.75,
      "rouge2_f1": 0.65,
      "rougeL_f1": 0.70
    }
  }
}
```

## Tài liệu tham khảo

- [ROUGE Paper](https://aclanthology.org/W04-1013/)
- [ViT5 Paper](https://arxiv.org/abs/2205.03457)
- [Evaluation Metrics for Text Summarization](https://arxiv.org/abs/2004.14373)
