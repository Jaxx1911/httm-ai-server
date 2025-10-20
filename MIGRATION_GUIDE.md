# Migration Guide - Từ Old Structure sang MVC

## Files cũ → Files mới

### 1. Database
```
db.py → app/models/database.py
```

### 2. Model
```
model.py → app/models/vit5_model.py
```

### 3. Server/Routes
```
server.py → app/routes/train_routes.py
          → app/routes/summarize_routes.py
          → app/controllers/train_controller.py
          → app/controllers/summarize_controller.py
```

### 4. Scripts
```
init_db.py → scripts/init_db.py
migrate_db.py → scripts/migrate_db.py
test_api.py → scripts/test_api.py
```

### 5. Documentation
```
README.md → docs/README.md
QUICKSTART.md → docs/QUICKSTART.md
POSTGRES_SETUP.md → docs/POSTGRES_SETUP.md
METRICS_GUIDE.md → docs/METRICS_GUIDE.md
CHANGELOG.md → docs/CHANGELOG.md
```

## Cleanup Old Files

Sau khi verify MVC structure hoạt động tốt, xóa các files cũ:

```bash
# CẢNH BÁO: Chỉ chạy sau khi đã test kỹ!
cd /Users/nguyenth/Documents/Py/HTTM

# Xóa files cũ
rm db.py
rm model.py
rm server.py
rm init_db.py
rm migrate_db.py
rm test_api.py
```

## Import Changes

### Old Import
```python
from db import TrainSession, SessionLocal
from model import vit5_model
```

### New Import
```python
from app.models.database import TrainSession, SessionLocal
from app.models.vit5_model import vit5_model
```

## Running Commands

### Old Way
```bash
python server.py
python init_db.py
python test_api.py
```

### New Way (MVC)
```bash
python app.py
python scripts/init_db.py
python scripts/test_api.py
```

## Verification Steps

1. **Test database initialization**
   ```bash
   python scripts/init_db.py
   ```

2. **Start server**
   ```bash
   python app.py
   ```

3. **Test API**
   ```bash
   python scripts/test_api.py
   ```

4. **Verify all endpoints work**
   - http://localhost:8000/docs
   - POST /summarize
   - POST /train
   - GET /train/{id}

5. **If everything works, cleanup old files**
   ```bash
   rm db.py model.py server.py init_db.py migrate_db.py test_api.py
   ```
