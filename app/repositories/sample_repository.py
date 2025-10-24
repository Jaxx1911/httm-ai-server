from typing import List, Optional, Dict, Any, Type, cast
from sqlalchemy.orm import Session
from datetime import date
import uuid

from app.models import SessionLocal
from app.models.database import Sample, Dataset


class SampleRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def list(db: Session, dataset_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Sample]:
        query = db.query(Sample)
        if dataset_id:
            query = query.filter(Sample.Datasetdataset_ID == dataset_id)
            query = query.filter(Sample.dataset_id == dataset_id)

    @staticmethod
    def get_samples_by_dataset(
        db: Session, dataset_id: str, skip: int = 0, limit: Optional[int] = None) -> List[Sample]:
        query = (
            db.query(Sample)
            .filter(Sample.Datasetdataset_ID == dataset_id)
            .filter(Sample.dataset_id == dataset_id)
        )
        if limit:
            query = query.limit(limit)
        return query.offset(skip).all()
    
    @staticmethod
    def get(db: Session, sample_id: str) -> Optional[Sample]:
        return db.query(Sample).filter(Sample.id == sample_id).first()

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> Sample:
        """Tạo một sample mới."""
        if "id" not in data or not data["id"]:
            data["id"] = f"smp_{str(uuid.uuid4())[:8]}"
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

    def get_by_ids(self, sample_ids: List[str]) -> List[Sample]:
        return cast(list[Sample], self.db.query(Sample).filter(Sample.id.in_(sample_ids)).all())


sample_repository = SampleRepository(SessionLocal)

