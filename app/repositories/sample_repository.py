from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date
import uuid
from app.models.database import Sample, Dataset

class SampleRepository:
    @staticmethod
    def list(db: Session, dataset_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Sample]:
        """Lấy danh sách các sample, có thể lọc theo dataset."""
        query = db.query(Sample)
        if dataset_id:
            query = query.filter(Sample.Datasetdataset_ID == dataset_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get(db: Session, sample_id: str) -> Optional[Sample]:
        """Lấy một sample theo ID."""
        return db.query(Sample).filter(Sample.sample_id == sample_id).first()

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> Sample:
        """Tạo một sample mới."""
        if "sample_id" not in data or not data["sample_id"]:
            data["sample_id"] = f"smp_{str(uuid.uuid4())[:8]}"
        if "created_at" not in data:
            data["created_at"] = date.today()
        if "language" not in data:
            data["language"] = "vi"
        
        db_sample = Sample(**data)
        db.add(db_sample)
        db.commit()
        db.refresh(db_sample)
        return db_sample

    @staticmethod
    def update(db: Session, sample_id: str, data: Dict[str, Any]) -> Optional[Sample]:
        """Cập nhật một sample."""
        db_sample = SampleRepository.get(db, sample_id)
        if db_sample:
            for key, value in data.items():
                setattr(db_sample, key, value)
            db.commit()
            db.refresh(db_sample)
        return db_sample

    @staticmethod
    def delete(db: Session, sample_id: str) -> bool:
        """Xóa một sample."""
        db_sample = SampleRepository.get(db, sample_id)
        if db_sample:
            db.delete(db_sample)
            db.commit()
            return True
        return False

    @staticmethod
    def list_datasets(db: Session) -> List[Dataset]:
        """Lấy danh sách tất cả dataset."""
        return db.query(Dataset).all()

sample_repository = SampleRepository()
