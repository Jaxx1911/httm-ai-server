# HTTM Project Structure

```
HTTM/
│
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   │
│   ├── models/                  # 📊 DATA LAYER
│   │   ├── __init__.py
│   │   ├── database.py          # PostgreSQL models (SQLAlchemy)
│   │   └── vit5_model.py        # ViT5 ML model (train + summarize)
│   │
│   ├── controllers/             # 🧠 BUSINESS LOGIC LAYER
│   │   ├── __init__.py
│   │   ├── train_controller.py       # Training logic
│   │   └── summarize_controller.py   # Summarization logic
│   │
│   ├── routes/                  # 🌐 PRESENTATION LAYER
│   │   ├── __init__.py
│   │   ├── train_routes.py           # /train endpoints
│   │   └── summarize_routes.py       # /summarize endpoints
│   │
│   └── config/                  # ⚙️ CONFIGURATION
│       ├── __init__.py
│       └── settings.py               # App settings
│
├── scripts/                     # 🔧 UTILITY SCRIPTS
│   ├── init_db.py              # Initialize database tables
│   ├── migrate_db.py           # Database migration
│   └── test_api.py             # API testing script
│
├── docs/                        # 📚 DOCUMENTATION
│   ├── README.md               # Full documentation
│   ├── QUICKSTART.md           # Quick start guide
│   ├── POSTGRES_SETUP.md       # PostgreSQL setup
│   ├── METRICS_GUIDE.md        # Metrics explanation
│   ├── CHANGELOG.md            # Change log
│   └── MVC_ARCHITECTURE.md     # MVC architecture details
│
├── app.py                       # 🚀 MAIN ENTRY POINT
├── requirements.txt             # 📦 Python dependencies
├── .env.example                 # 🔑 Environment template
├── .env                         # 🔑 Environment variables (git-ignored)
├── .gitignore                   # 🚫 Git ignore rules
├── README.md                    # 📖 Project overview
├── MIGRATION_GUIDE.md           # 🔄 Migration from old structure
└── STRUCTURE.md                 # 📁 This file

# Generated folders (git-ignored)
├── __pycache__/                 # Python cache
├── model_checkpoints/           # Training checkpoints
├── trained_model/               # Trained model files
└── logs/                        # Training logs
```

## Layer Responsibilities

### 📊 Models (`app/models/`)
- **database.py**: SQLAlchemy ORM models cho PostgreSQL
  - `TrainSession` model
  - Database connection
  - Schema definition
  
- **vit5_model.py**: ViT5 machine learning model
  - Load pretrained model
  - Train/re-train functionality
  - Evaluation with ROUGE metrics
  - Text summarization

### 🧠 Controllers (`app/controllers/`)
- **train_controller.py**: Business logic cho training
  - Create train sessions
  - Background training
  - Status tracking
  - Error handling
  
- **summarize_controller.py**: Business logic cho summarization
  - Text summarization wrapper
  - Input validation
  - Output formatting

### 🌐 Routes (`app/routes/`)
- **train_routes.py**: Training API endpoints
  - `POST /train` - Start training
  - `GET /train/{id}` - Check status
  
- **summarize_routes.py**: Summarization API endpoints
  - `POST /summarize` - Summarize text

### ⚙️ Config (`app/config/`)
- **settings.py**: Application configuration
  - Database URL
  - Model settings
  - Server settings
  - Default parameters

## File Purposes

### Root Level

#### `app.py`
Main application entry point. Khởi tạo FastAPI app và register routes.

```python
from fastapi import FastAPI
from app.routes import train_router, summarize_router

app = FastAPI(title="HTTM API")
app.include_router(train_router)
app.include_router(summarize_router)
```

#### `requirements.txt`
Python dependencies cần thiết để chạy project.

#### `.env.example`
Template cho environment variables. Copy thành `.env` và điền thông tin.

#### `.gitignore`
Files và folders được git ignore (venv, __pycache__, .env, models, etc.)

### Scripts

#### `scripts/init_db.py`
Khởi tạo database tables lần đầu.
```bash
python scripts/init_db.py
```

#### `scripts/migrate_db.py`
Migration database (thêm metrics columns).
```bash
python scripts/migrate_db.py
```

#### `scripts/test_api.py`
Test API endpoints.
```bash
python scripts/test_api.py
```

### Documentation

#### `docs/README.md`
Full documentation với API examples, configuration, etc.

#### `docs/QUICKSTART.md`
Quick start guide để chạy project nhanh.

#### `docs/POSTGRES_SETUP.md`
Chi tiết cài đặt và cấu hình PostgreSQL.

#### `docs/METRICS_GUIDE.md`
Giải thích ROUGE metrics và cách đánh giá model.

#### `docs/CHANGELOG.md`
Lịch sử thay đổi và updates.

#### `docs/MVC_ARCHITECTURE.md`
Chi tiết về MVC architecture, data flow, best practices.

## Import Patterns

### Importing Models
```python
from app.models.database import TrainSession, SessionLocal
from app.models.vit5_model import vit5_model
```

### Importing Controllers
```python
from app.controllers.train_controller import TrainController
from app.controllers.summarize_controller import SummarizeController
```

### Importing Config
```python
from app.config.settings import settings
```

## Running the Application

### Development
```bash
python app.py
```

### Production
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing
```bash
python scripts/test_api.py
```

## Adding New Features

### Adding a New Endpoint

1. **Create Route** (`app/routes/new_routes.py`)
```python
from fastapi import APIRouter
router = APIRouter(prefix="/new", tags=["new"])

@router.post("")
def new_endpoint():
    return NewController.do_something()
```

2. **Create Controller** (`app/controllers/new_controller.py`)
```python
class NewController:
    @staticmethod
    def do_something():
        # Business logic here
        return model.process()
```

3. **Register in app.py**
```python
from app.routes.new_routes import router as new_router
app.include_router(new_router)
```

### Adding a New Model

1. **Create Model File** (`app/models/new_model.py`)
```python
class NewModel:
    def __init__(self):
        # Initialize
        
    def process(self):
        # Logic
```

2. **Export in `__init__.py`**
```python
from .new_model import NewModel
__all__ = [..., 'NewModel']
```

3. **Use in Controller**
```python
from app.models.new_model import NewModel
```

## Directory Conventions

- Sử dụng **snake_case** cho file names: `train_controller.py`
- Sử dụng **PascalCase** cho class names: `TrainController`
- Sử dụng **snake_case** cho function names: `create_train_session()`
- Mỗi module có `__init__.py` để export public API
- Routes grouped by resource (`/train`, `/summarize`)
- One controller per domain/feature

## Environment Variables

Required in `.env`:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/httm_db
HOST=0.0.0.0
PORT=8000
MODEL_NAME=VietAI/vit5-base
```

Optional (có defaults):
```
MAX_SUMMARY_LENGTH=128
MAX_TITLE_LENGTH=32
DEFAULT_LEARNING_RATE=5e-5
DEFAULT_EPOCHS=3
DEFAULT_BATCH_SIZE=4
```

## Git Workflow

```bash
# Initial setup
git init
git add .
git commit -m "Initial MVC structure"

# Feature branch
git checkout -b feature/new-feature
# Make changes
git add .
git commit -m "Add new feature"
git checkout main
git merge feature/new-feature
```

## Next Steps

1. ✅ MVC structure complete
2. ✅ Documentation complete
3. 🔄 Add unit tests
4. 🔄 Add integration tests
5. 🔄 Add CI/CD pipeline
6. 🔄 Add Docker support
7. 🔄 Add authentication
