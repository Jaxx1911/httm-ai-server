"""Repository for handling ModelVersion-related database operations"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
from app.models.database import ModelVersion


class ModelRepository:
    @staticmethod
    def create_model_version(
        db: Session,
        version: str,
        name: str,
        model_path: str,
        created_by: str,
        accuracy: Optional[float] = None,
        precision: Optional[float] = None,
        recall: Optional[float] = None,
        f1_score: Optional[float] = None,
        parameters: Optional[str] = None,
        base_model_id: Optional[str] = None
    ) -> ModelVersion:
        """Create a new model version"""
        model_version = ModelVersion(
            id=f"mv_{str(uuid.uuid4())[:8]}",
            version=version,
            name=name,
            model_path=model_path,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            parameters=parameters,
            base_model_id=base_model_id,
            created_by=created_by,
            status="training"
        )
        db.add(model_version)
        db.commit()
        db.refresh(model_version)
        return model_version

    @staticmethod
    def get_model_version_by_id(db: Session, model_version_id: str) -> Optional[ModelVersion]:
        """Get a model version by ID"""
        return db.query(ModelVersion).filter(ModelVersion.id == model_version_id).first()

    @staticmethod
    def get_model_version_by_version(db: Session, version: str) -> Optional[ModelVersion]:
        """Get a model version by version string"""
        return db.query(ModelVersion).filter(ModelVersion.version == version).first()

    @staticmethod
    def get_all_model_versions(db: Session, skip: int = 0, limit: int = 100) -> List[ModelVersion]:
        """Get all model versions"""
        return (
            db.query(ModelVersion)
            .order_by(desc(ModelVersion.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_active_model(db: Session) -> Optional[ModelVersion]:
        """Get the currently active model"""
        return db.query(ModelVersion).filter(ModelVersion.is_active == True).first()

    @staticmethod
    def set_active_model(db: Session, model_version_id: str) -> Optional[ModelVersion]:
        """Set a model version as active (deactivate all others)"""
        # Deactivate all models
        db.query(ModelVersion).update({"is_active": False})

        # Activate the specified model
        model = db.query(ModelVersion).filter(ModelVersion.id == model_version_id).first()
        if model:
            model.is_active = True
            model.status = "active"
            db.commit()
            db.refresh(model)
        return model

    @staticmethod
    def update_model_version(
        db: Session,
        model_version_id: str,
        **kwargs
    ) -> Optional[ModelVersion]:
        """Update a model version"""
        model = db.query(ModelVersion).filter(ModelVersion.id == model_version_id).first()
        if model:
            for key, value in kwargs.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            db.commit()
            db.refresh(model)
        return model

    @staticmethod
    def delete_model_version(db: Session, model_version_id: str) -> bool:
        """Delete a model version"""
        model = db.query(ModelVersion).filter(ModelVersion.id == model_version_id).first()
        if model:
            db.delete(model)
            db.commit()
            return True
        return False


model_repository = ModelRepository()

__all__ = ['ModelRepository', 'model_repository']

