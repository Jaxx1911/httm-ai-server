"""Schemas for Model Version API"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TrainRequest(BaseModel):
    """Request schema for training a model"""
    version: str = Field(..., description="Version identifier for the model")
    name: str = Field(..., description="Name of the model")
    dataset_id: str = Field(..., description="Dataset ID to use for training")
    is_retrain: bool = Field(default=False, description="Whether this is a retrain operation")
    base_model_id: Optional[str] = Field(None, description="Base model ID for retraining")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Training parameters")


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

