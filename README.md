# HTTM - ViT5 Text Summarization Server

Server API để train/re-train model ViT5 và tóm tắt văn bản tiếng Việt với kiến trúc MVC.

## 🏗️ Kiến trúc MVC

Project được tổ chức theo mô hình Model-View-Controller:

```
HTTM/
├── app/                      # Main application package
│   ├── __init__.py
│   ├── models/              # Models (Database + ML Model)
│   │   ├── __init__.py
│   │   ├── database.py      # SQLAlchemy models
│   │   └── vit5_model.py    # ViT5 ML model
│   ├── controllers/         # Business Logic
│   │   ├── __init__.py
│   │   ├── train_controller.py
│   │   └── summarize_controller.py
│   ├── routes/              # API Routes (View layer)
│   │   ├── __init__.py
│   │   ├── train_routes.py
│   │   └── summarize_routes.py
│   └── config/              # Configuration
│       ├── __init__.py
│       └── settings.py
├── scripts/                 # Utility scripts
│   ├── init_db.py          # Initialize database
│   ├── migrate_db.py       # Database migration
│   └── test_api.py         # API testing
├── docs/                    # Documentation
│   ├── README.md           # Full documentation
│   ├── QUICKSTART.md       # Quick start guide
│   ├── POSTGRES_SETUP.md   # PostgreSQL setup
│   ├── METRICS_GUIDE.md    # Metrics explanation
│   └── CHANGELOG.md        # Change log
├── app.py                   # Main application entry
├── requirements.txt         # Dependencies
├── .env.example            # Environment variables template
└── .env                    # Environment variables (create from .env.example)
```

## 🚀 Quick Start

### 1. Cài đặt PostgreSQL

```bash
brew install postgresql@15
brew services start postgresql@15
createdb httm_db
```

### 2. Cấu hình

```bash
cp .env.example .env
# Chỉnh sửa .env với thông tin database của bạn
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Khởi tạo database

```bash
python scripts/init_db.py
```

### 5. Chạy server

```bash
python app.py
```

Server chạy tại: http://localhost:8000
API docs: http://localhost:8000/docs

## 📚 API Endpoints

### POST /summarize
Tóm tắt văn bản, trả về title và summary

```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Văn bản cần tóm tắt..."}'
```

### POST /train
Train/re-train model ViT5

```bash
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "train_data": [...],
    "parameters": {"epochs": 3}
  }'
```

### GET /train/{id}
Kiểm tra trạng thái train và xem metrics

```bash
curl "http://localhost:8000/train/1"
```

## 🧪 Testing

```bash
python scripts/test_api.py
```

## 📖 Documentation

- **[docs/README.md](docs/README.md)** - Full documentation
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Quick start guide
- **[docs/POSTGRES_SETUP.md](docs/POSTGRES_SETUP.md)** - PostgreSQL setup
- **[docs/METRICS_GUIDE.md](docs/METRICS_GUIDE.md)** - Metrics explanation
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Change log

## 🏛️ Kiến trúc MVC

### Models (`app/models/`)
- **database.py**: SQLAlchemy models cho database
- **vit5_model.py**: ViT5 model cho text summarization

### Controllers (`app/controllers/`)
- **train_controller.py**: Business logic cho train/re-train
- **summarize_controller.py**: Business logic cho summarization

### Routes (`app/routes/`)
- **train_routes.py**: API endpoints cho training
- **summarize_routes.py**: API endpoints cho summarization

### Config (`app/config/`)
- **settings.py**: Application settings và configuration

## 🔧 Scripts

### Initialize Database
```bash
python scripts/init_db.py
```

### Migrate Database (thêm metrics columns)
```bash
python scripts/migrate_db.py
```

### Test API
```bash
python scripts/test_api.py
```

## 🌟 Features

1. ✅ Train/Re-train ViT5 model với dữ liệu tùy chỉnh
2. ✅ Tự động đánh giá model (Accuracy, Precision, Recall, F1)
3. ✅ Tóm tắt văn bản với tiêu đề tự động
4. ✅ Background training
5. ✅ PostgreSQL database
6. ✅ RESTful API với FastAPI
7. ✅ MVC architecture
8. ✅ Comprehensive documentation

## 📦 Dependencies

- FastAPI - Web framework
- SQLAlchemy - ORM
- PostgreSQL - Database
- Transformers - ViT5 model
- PyTorch - ML framework
- ROUGE - Evaluation metrics

## 🤝 Contributing

Xem [docs/CHANGELOG.md](docs/CHANGELOG.md) để biết lịch sử thay đổi.

## 📄 License

MIT
