# Kiến trúc MVC - HTTM Project

## Tổng quan

HTTM sử dụng kiến trúc **Model-View-Controller (MVC)** để tổ chức code một cách rõ ràng, dễ maintain và mở rộng.

## Cấu trúc MVC

### 1. Models (`app/models/`)

**Trách nhiệm**: Quản lý dữ liệu và business logic cấp thấp

#### `database.py` - Database Models
```python
# Định nghĩa bảng train_sessions với SQLAlchemy
class TrainSession(Base):
    __tablename__ = "train_sessions"
    id = Column(Integer, primary_key=True)
    status = Column(String)
    accuracy = Column(Float)
    # ...
```

**Chức năng**:
- Định nghĩa schema database
- Kết nối với PostgreSQL
- ORM mapping

#### `vit5_model.py` - ML Model
```python
# ViT5 model cho text summarization
class ViT5Model:
    def train_model(self, train_data, parameters):
        # Logic train model
        
    def evaluate_model(self, eval_data):
        # Logic đánh giá model
        
    def summarize_text(self, text):
        # Logic tóm tắt văn bản
```

**Chức năng**:
- Load và quản lý ViT5 model
- Train/re-train model
- Evaluate model với ROUGE metrics
- Generate summaries

---

### 2. Controllers (`app/controllers/`)

**Trách nhiệm**: Business logic và xử lý dữ liệu

#### `train_controller.py` - Training Logic
```python
class TrainController:
    @staticmethod
    def create_train_session(train_data, parameters):
        # Tạo phiên train mới trong DB
        
    @staticmethod
    def train_model_background(session_id, train_data, parameters):
        # Thực hiện train và lưu kết quả
        
    @staticmethod
    def get_train_status(session_id):
        # Lấy thông tin phiên train
```

**Chức năng**:
- Tạo và quản lý train sessions
- Orchestrate training process
- Lưu kết quả và metrics vào DB
- Error handling

#### `summarize_controller.py` - Summarization Logic
```python
class SummarizeController:
    @staticmethod
    def summarize_text(text):
        # Gọi model để tóm tắt
```

**Chức năng**:
- Wrapper cho summarization
- Validation input
- Format output

---

### 3. Routes/Views (`app/routes/`)

**Trách nhiệm**: API endpoints và request/response handling

#### `train_routes.py` - Training Endpoints
```python
router = APIRouter(prefix="/train", tags=["train"])

@router.post("")
def train_model(request: TrainRequest, background_tasks: BackgroundTasks):
    # POST /train - Start training
    
@router.get("/{session_id}")
def get_train_status(session_id: int):
    # GET /train/{id} - Check status
```

**Chức năng**:
- Define API endpoints
- Request validation (Pydantic models)
- Call controllers
- Return responses

#### `summarize_routes.py` - Summarization Endpoints
```python
router = APIRouter(prefix="/summarize", tags=["summarize"])

@router.post("", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    # POST /summarize - Summarize text
```

**Chức năng**:
- Summarization endpoint
- Input/output validation
- Response formatting

---

### 4. Config (`app/config/`)

**Trách nhiệm**: Application configuration

#### `settings.py` - Settings Management
```python
class Settings:
    DATABASE_URL: str
    MODEL_NAME: str
    HOST: str
    PORT: int
    # ...
    
settings = Settings()
```

**Chức năng**:
- Centralized configuration
- Environment variables
- Default values
- Type safety

---

## Data Flow

### 1. Request Flow (Summarization)

```
Client → Route → Controller → Model → Controller → Route → Client
         ↓         ↓            ↓         ↑         ↑
      Validate  Process    Generate   Format   Return
                           Summary
```

**Chi tiết**:
1. Client gửi POST request đến `/summarize`
2. **Route** (`summarize_routes.py`):
   - Validate request với `SummarizeRequest` model
   - Call `SummarizeController.summarize_text()`
3. **Controller** (`summarize_controller.py`):
   - Process input
   - Call `vit5_model.summarize_text()`
4. **Model** (`vit5_model.py`):
   - Generate title và summary
   - Return dict
5. **Controller** → **Route**:
   - Format response
   - Return `SummarizeResponse`
6. Client nhận kết quả

### 2. Request Flow (Training)

```
Client → Route → Controller → Database → Background Task
         ↓         ↓            ↓             ↓
      Validate  Create      Save Session  Train Model
                Session                        ↓
                                          Evaluate
                                              ↓
                                         Update DB
```

**Chi tiết**:
1. Client gửi POST request đến `/train`
2. **Route** (`train_routes.py`):
   - Validate request với `TrainRequest` model
   - Call `TrainController.create_train_session()`
3. **Controller** (`train_controller.py`):
   - Tạo `TrainSession` trong database
   - Return session_id
4. **Route**:
   - Start background task `train_model_background()`
   - Return response ngay lập tức
5. **Background Task**:
   - Call `vit5_model.train_model()`
   - Call `vit5_model.evaluate_model()`
   - Update database với kết quả và metrics
6. Client có thể check status qua GET `/train/{id}`

---

## Separation of Concerns

### Models
- ❌ KHÔNG biết về HTTP requests
- ❌ KHÔNG biết về routing
- ✅ CHỈ lo về data và ML logic

### Controllers
- ❌ KHÔNG biết về HTTP details
- ✅ CHỈ lo về business logic
- ✅ Orchestrate models và database

### Routes
- ❌ KHÔNG có business logic
- ✅ CHỈ lo về HTTP layer
- ✅ Validation và routing

### Config
- ✅ Centralized settings
- ✅ Environment management

---

## Ưu điểm của MVC

### 1. Separation of Concerns
Mỗi layer có trách nhiệm riêng biệt, không overlap

### 2. Maintainability
- Dễ tìm bug (biết bug ở layer nào)
- Dễ sửa code (chỉ sửa 1 nơi)

### 3. Testability
```python
# Test model riêng
def test_vit5_summarize():
    model = ViT5Model()
    result = model.summarize_text("test")
    assert "title" in result

# Test controller riêng
def test_train_controller():
    session_id = TrainController.create_train_session(data, params)
    assert session_id > 0

# Test controller riêng
def test_summarize_endpoint():
    response = client.post("/summarize", json={"text": "test"})
    assert response.status_code == 200
```

### 4. Scalability
- Dễ thêm endpoints mới
- Dễ thêm models mới
- Dễ thêm controllers mới

### 5. Code Reusability
```python
# Controller có thể được dùng bởi nhiều controller
from app.controllers import TrainController

# Route 1
@router.post("/train")
def train():
    return TrainController.create_train_session(...)

# Route 2 (CLI)
def cli_train():
    return TrainController.create_train_session(...)
```

---

## Best Practices

### 1. Keep Routes Thin
```python
# ✅ GOOD - Route chỉ validate và delegate
@router.post("/train")
def train_model(request: TrainRequest):
    return TrainController.create_train_session(
        request.train_data, 
        request.parameters
    )

# ❌ BAD - Route có business logic
@router.post("/train")
def train_model(request: TrainRequest):
    db = SessionLocal()
    session = TrainSession(...)
    db.add(session)
    # ... nhiều logic
```

### 2. Controllers Contain Business Logic
```python
# ✅ GOOD - Controller chứa logic
class TrainController:
    @staticmethod
    def train_model_background(session_id, data, params):
        try:
            result = vit5_model.train_model(data, params)
            metrics = result.get('metrics', {})
            # Update database
        except Exception as e:
            # Handle errors
```

### 3. Models Are Independent
```python
# ✅ GOOD - Model không depend vào FastAPI
class ViT5Model:
    def summarize_text(self, text: str) -> Dict[str, str]:
        # Pure Python logic
        
# ❌ BAD - Model depend vào FastAPI
class ViT5Model:
    def summarize_text(self, request: Request):
        # Don't use FastAPI objects in models
```

### 4. Use Dependency Injection
```python
# Settings injection
from app.config.settings import settings

class ViT5Model:
    def __init__(self):
        self.model_name = settings.MODEL_NAME
```

---

## File Organization Rules

```
app/
├── models/              # Data layer
│   ├── database.py     # 1 file per database concern
│   └── vit5_model.py   # 1 file per ML model
├── controllers/         # Business logic layer
│   ├── train_controller.py      # 1 file per domain
│   └── summarize_controller.py
├── routes/              # Presentation layer
│   ├── train_routes.py          # 1 file per resource
│   └── summarize_routes.py
└── config/              # Configuration
    └── settings.py
```

---

## Migration từ Old Structure

### Old Structure
```
HTTM/
├── db.py           # Database
├── model.py        # ViT5 Model
├── server.py       # Everything
```

### New Structure (MVC)
```
HTTM/
├── app/
│   ├── models/
│   │   ├── database.py     # From db.py
│   │   └── vit5_model.py   # From model.py
│   ├── controllers/
│   │   ├── train_controller.py      # Extracted from server.py
│   │   └── summarize_controller.py  # Extracted from server.py
│   └── routes/
│       ├── train_routes.py          # Extracted from server.py
│       └── summarize_routes.py      # Extracted from server.py
└── app.py          # Main entry point
```

---

## Testing Structure

```
tests/
├── test_models/
│   ├── test_database.py
│   └── test_vit5_model.py
├── test_controllers/
│   ├── test_train_controller.py
│   └── test_summarize_controller.py
└── test_routes/
    ├── test_train_routes.py
    └── test_summarize_routes.py
```

---

## Kết luận

MVC giúp HTTM project:
- ✅ Organized và professional
- ✅ Dễ hiểu và maintain
- ✅ Dễ test
- ✅ Dễ mở rộng
- ✅ Theo best practices
