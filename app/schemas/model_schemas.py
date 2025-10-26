from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class TrainRequest(BaseModel):
    id: Optional[str]
    model_name: str
    is_select_all: bool
    sample_ids: List[str]
    is_retrain: bool = Field(default=False)
    base_model_id: Optional[str] = Field(default=None)


class ModelVersionResponse(BaseModel):
    id: Optional[str]
    version: Optional[str]
    name: Optional[str]
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    model_path: Optional[str]
    status: Optional[str]
    base_model_id: Optional[str]
    sample_ids: Optional[List[str]]
    is_select_all: Optional[bool]
    is_retrain: Optional[bool]


class ModelStatusResponse(BaseModel):
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
    model_version_id: str = Field(..., description="Model version ID to activate")


class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float

