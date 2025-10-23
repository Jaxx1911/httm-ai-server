# Database Schema Migration Guide

## Tổng quan

Dự án đã được refactor với các thay đổi chính sau:

### 1. Thay đổi tên bảng (Uppercase → lowercase)
- `Admin` → `admin`
- `Dataset` → `dataset`
- `Model` → `model_version` (đổi tên)
- `Sample` → `sample`
- `ModelDataset` → `model_dataset`

### 2. Thay đổi tên cột ID
Tất cả các trường ID giờ đều tên là `id` thay vì `table_name_id`:
- `admin_id` → `id`
- `dataset_ID` → `id`
- `model_id` → `id`
- `sample_id` → `id`

### 3. Thay đổi tên Foreign Keys
- `Adminadmin_id` → `created_by`
- `Datasetdataset_ID` → `dataset_id`
- `Modelmodel_id` → `model_version_id`

### 4. Bảng ModelVersion (từ Model)
Các thay đổi:
- Đổi tên từ `Model` → `model_version`
- `model_id` → `id`
- `F1Score` → `f1_score`
- `path` → `model_path`
- `finetune_time` → `training_duration` (đổi từ TIME → INTEGER seconds)
- `parameter` → `parameters`
- `baseModel` → `base_model_id`
- Thêm: `version` (VARCHAR - version identifier)
- Thêm: `name` (VARCHAR - model name)
- Thêm: `is_active` (BOOLEAN - active model flag)
- Thêm: `created_at` (TIMESTAMP)
- Thêm: `completed_at` (TIMESTAMP)

### 5. Các bảng khác
**Dataset:**
- Thêm `created_at` (TIMESTAMP)

**ModelDataset:**
- Thêm `id` (SERIAL PRIMARY KEY)
- Thêm `created_at` (TIMESTAMP)
- `weight` và `notes` giờ là optional (nullable)

**Sample:**
- `language` có default value là "vi"

## Cách Migration

### Option 1: Sử dụng script migration (Khuyến nghị)
```bash
python scripts/migrate_schema.py
```

### Option 2: Drop và recreate database (Mất dữ liệu)
```bash
# Drop tất cả tables
psql -U your_user -d your_database -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Chạy lại init_db
python scripts/init_db.py
```

### Option 3: Manual migration
Chạy các câu lệnh SQL trong file `scripts/migrate_schema.py` thủ công.

## API Changes

### New Model Endpoints

**POST /model/train**
- Train model mới với dataset_id
- Request body:
```json
{
  "version": "v1.0.0",
  "name": "Model ViT5 V1",
  "dataset_id": "ds_12345678",
  "is_retrain": false,
  "base_model_id": null,
  "parameters": {}
}
```

**GET /model/status/{model_version_id}**
- Lấy trạng thái training của model theo ID
- Response: training status, metrics, duration, etc.

**GET /model/list**
- Lấy danh sách tất cả model versions
- Query params: skip, limit

**GET /model/active**
- Lấy thông tin model đang active

**POST /model/activate**
- Activate một model version
- Request body: `{"model_version_id": "mv_12345678"}`

## Code Changes

### 1. Import changes
```python
# Old
from app.models.database import Model, Dataset, Sample, Admin

# New
from app.models.database import ModelVersion, Dataset, Sample, Admin
```

### 2. Repository usage
```python
# Old
model = db.query(Model).filter(Model.model_id == id).first()

# New
model = db.query(ModelVersion).filter(ModelVersion.id == id).first()
```

### 3. Service usage
```python
# Old - train_model gọi trực tiếp
result = train_model(data, params)

# New - sử dụng ModelService
service = ModelService(db=db, created_by=admin_id)
result = service.train_model(train_request)
```

## Các file mới được tạo

1. `constant/constants.py` - Training configurations
2. `app/repositories/model_repository.py` - Model version repository
3. `app/schemas/model_schemas.py` - Model API schemas
4. `scripts/migrate_schema.py` - Migration script

## Lưu ý quan trọng

1. **Backup database trước khi migration!**
2. Tất cả datetime fields giờ sử dụng timezone-aware datetime
3. Training giờ chạy ở background task
4. Model status: "training", "completed", "failed", "active"
5. Chỉ có 1 model được active tại một thời điểm

## Testing

Sau khi migration, test các API:
```bash
# Test train model
curl -X POST http://localhost:8000/model/train \
  -H "Content-Type: application/json" \
  -d '{"version": "v1.0", "name": "Test Model", "dataset_id": "ds_xxx"}'

# Test get status
curl http://localhost:8000/model/status/mv_12345678

# Test list models
curl http://localhost:8000/model/list

# Test get active model
curl http://localhost:8000/model/active
```

