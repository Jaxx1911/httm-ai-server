from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.models.database import SessionLocal
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


@router.post("/train", response_model=dict)
def train_model(
    request: TrainRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Endpoint to train/re-train ViT5 model with provided dataset
    Training runs in background and returns immediately with model version ID
    """
    # TODO: Get actual admin_id from authentication
    created_by = "admin_001"  # Placeholder

    # Validate dataset exists
    from app.repositories.dataset_repository import get_dataset
    dataset = get_dataset(db, request.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset {request.dataset_id} not found")

    # Check if version already exists
    from app.repositories.model_repository import ModelRepository
    repo = ModelRepository()
    existing = repo.get_model_version_by_version(db, request.version)
    if existing:
        raise HTTPException(status_code=400, detail=f"Model version {request.version} already exists")

    # Start training in background
    background_tasks.add_task(
        train_model_background,
        db=SessionLocal(),  # New session for background task
        train_request=request,
        created_by=created_by
    )
    
    return {
        "version": request.version,
        "name": request.name,
        "status": "training",
        "message": "Model training started in background"
    }


@router.get("/status/{model_version_id}", response_model=ModelStatusResponse)
def get_model_status(model_version_id: str, db: Session = Depends(get_db)):
    """
    Get training status and metrics of a model version by ID
    """
    # TODO: Get actual admin_id from authentication
    created_by = "admin_001"

    service = ModelService(db=db, created_by=created_by)
    status = service.get_model_status(model_version_id)

    if not status:
        raise HTTPException(status_code=404, detail=f"Model version {model_version_id} not found")

    return ModelStatusResponse(
        **status,
        message=f"Model is currently {status['status']}"
    )


@router.get("/list", response_model=List[ModelVersionResponse])
def list_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get list of all model versions
    """
    # TODO: Get actual admin_id from authentication
    created_by = "admin_001"

    service = ModelService(db=db, created_by=created_by)
    models = service.get_all_models(skip=skip, limit=limit)

    return models


@router.get("/active", response_model=dict)
def get_active_model(db: Session = Depends(get_db)):
    """
    Get information about the currently active model
    """
    # TODO: Get actual admin_id from authentication
    created_by = "admin_001"

    service = ModelService(db=db, created_by=created_by)
    active_model = service.get_active_model_info()

    if not active_model:
        raise HTTPException(status_code=404, detail="No active model found")

    return active_model


@router.post("/activate")
def activate_model(request: ActivateModelRequest, db: Session = Depends(get_db)):
    """
    Activate a specific model version
    """
    # TODO: Get actual admin_id from authentication
    created_by = "admin_001"

    service = ModelService(db=db, created_by=created_by)
    success = service.activate_model_version(request.model_version_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Model version {request.model_version_id} not found")

    return {
        "message": f"Model version {request.model_version_id} activated successfully",
        "model_version_id": request.model_version_id
    }

