from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class TrainRequest(BaseModel):
    model_name: str
    sample_ids: List[str]
    is_retrain: bool = Field(default=False)
    base_model_id: Optional[str] = Field(default=None)


class ModelVersionResponse(BaseModel):
    """Response schema for model version"""
    id: str
    version: str
    name: str
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    model_path: str
    status: str
    is_active: bool
    training_duration: Optional[int]
    parameters: Optional[str]
    base_model_id: Optional[str]
    created_by: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ModelStatusResponse(BaseModel):
    """Response schema for model training status"""
    id: str
    version: str
    name: str
    status: str
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    training_duration: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    message: Optional[str]

    class Config:
        from_attributes = True


class ActivateModelRequest(BaseModel):
    """Request schema for activating a model"""
    model_version_id: str = Field(..., description="Model version ID to activate")


class ModelMetrics(BaseModel):
    """Metrics for model evaluation"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float

