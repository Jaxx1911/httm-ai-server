from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models.database import SessionLocal
from app.repositories.model_repository import ModelRepository
from app.repositories.sample_repository import SampleRepository
from app.service.model_service import ModelService
from app.schemas.model_schemas import (
    TrainRequest,
    ModelVersionResponse,
    ModelStatusResponse,
    ActivateModelRequest
)

router = APIRouter(prefix="/model", tags=["model"])
logger = logging.getLogger(__name__)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def train_model_background(db: Session, train_request: TrainRequest, created_by: str):
    """Background task to train model"""
    try:
        service = ModelService(db=db, created_by=created_by)
        result = service.train_model(train_request)
        logger.info(f"Training completed successfully: {result}")
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
    finally:
        db.close()


class ModelController:
    def __init__(self, model_service: ModelService):
        self.model_service = model_service

    def get_all_models(self) -> List[ModelVersionResponse]:
        return self.model_service.get_models()

    def train_model(self, request: TrainRequest) -> ModelVersionResponse:
        res = self.model_service.train_model(request)
        return ModelVersionResponse(**res)

    def get_model_status(self, model_id: str) -> ModelStatusResponse:
        return self.model_service.get_model_status(model_id)

    def activate_model(self, model_id: str) -> ModelStatusResponse:
        return self.model_service.activate_model(model_id)

model_controller = ModelController(ModelService(ModelRepository(SessionLocal()), SampleRepository(SessionLocal())))

