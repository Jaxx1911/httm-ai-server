"""Train routes - API endpoints for training"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List
from ..controllers.train_controller import TrainController

router = APIRouter(prefix="/train", tags=["train"])

# Request models
class TrainRequest(BaseModel):
    train_data: List[Dict[str, str]]  # List các dict chứa 'input_text' và 'target_text'
    parameters: Dict[str, Any]

@router.post("")
def train_model(request: TrainRequest, background_tasks: BackgroundTasks):
    """
    Endpoint để train/re-train model ViT5 với dữ liệu được cung cấp
    """
    # Tạo phiên train mới
    session_id = TrainController.create_train_session(request.train_data, request.parameters)
    
    # Thực hiện train trong background
    background_tasks.add_task(
        TrainController.train_model_background,
        session_id,
        request.train_data,
        request.parameters
    )
    
    return {
        "train_session_id": session_id,
        "status": "running",
        "message": "Training started in background"
    }

@router.get("/{session_id}")
def get_train_status(session_id: int):
    """
    Lấy trạng thái của phiên train
    """
    return TrainController.get_train_status(session_id)
