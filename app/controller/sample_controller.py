from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.repositories.sample_repository import sample_repository
from datetime import date

router = APIRouter(prefix="/api/samples", tags=["Sample Management"])

# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_login(req: Request):
    """Dependency để yêu cầu đăng nhập."""
    if "user" not in req.session:
        raise HTTPException(status_code=401, detail="Yêu cầu đăng nhập để thực hiện")
    return req.session["user"]

# --- Pydantic Models ---
class SampleBase(BaseModel):
    title: str
    input_text: str
    target_summary: str
    category: str
    source: Optional[str] = None
    dataset_id: str

class SampleUpdate(BaseModel):
    title: Optional[str] = None
    input_text: Optional[str] = None
    target_summary: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    dataset_id: Optional[str] = None

class SampleOut(SampleBase):
    id: str
    language: str
    created_at: date
    class Config:
        from_attributes = True

class DatasetOut(BaseModel):
    id: str
    name: str
    class Config:
        from_attributes = True

# --- API Endpoints ---
@router.get("", response_model=List[SampleOut])
def list_samples(
    dataset_id: Optional[str] = Query(None),
    db: Session = Depends(get_db), 
    _=Depends(require_login)
):
    return sample_repository.list(db, dataset_id=dataset_id)

@router.post("", response_model=SampleOut, status_code=201)
def create_sample(payload: SampleBase, db: Session = Depends(get_db), _=Depends(require_login)):
    try:
        return sample_repository.create(db, payload.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{sample_id}", response_model=SampleOut)
def update_sample(sample_id: str, payload: SampleUpdate, db: Session = Depends(get_db), _=Depends(require_login)):
    updated = sample_repository.update(db, sample_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Sample không tồn tại")
    return updated

@router.delete("/{sample_id}", status_code=204)
def delete_sample(sample_id: str, db: Session = Depends(get_db), _=Depends(require_login)):
    if not sample_repository.delete(db, sample_id):
        raise HTTPException(status_code=404, detail="Sample không tồn tại")

@router.get("/datasets/all", response_model=List[DatasetOut])
def list_datasets(db: Session = Depends(get_db), _=Depends(require_login)):
    return sample_repository.list_datasets(db)
