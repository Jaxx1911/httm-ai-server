"""Train routes - API endpoints for training"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List
import datetime
import json
from ..models.database import TrainSession, SessionLocal
from ..models.vit5_model import vit5_model

router = APIRouter(prefix="/train", tags=["train"])

# Request models
class TrainRequest(BaseModel):
    train_data: List[Dict[str, str]]  # List các dict chứa 'input_text' và 'target_text'
    parameters: Dict[str, Any]

# --- Logic được di chuyển từ train_controller ---
def create_train_session(train_data: List[Dict[str, str]], parameters: Dict[str, Any]) -> int:
    """
    Tạo phiên train mới trong database
    
    Args:
        train_data: Dữ liệu train
        parameters: Thông số train
        
    Returns:
        ID của phiên train
    """
    db = SessionLocal()
    try:
        train_session = TrainSession(
            status="running",
            parameters=json.dumps(parameters)
        )
        db.add(train_session)
        db.commit()
        db.refresh(train_session)
        return train_session.id
    finally:
        db.close()

def train_model_background(session_id: int, train_data: List[Dict[str, str]], parameters: Dict[str, Any]):
    """
    Thực hiện train model trong background
    
    Args:
        session_id: ID phiên train
        train_data: Dữ liệu train
        parameters: Thông số train
    """
    db = SessionLocal()
    try:
        # Train model
        result = vit5_model.train_model(train_data, parameters)
        
        # Lấy metrics từ kết quả train
        metrics = result.get('metrics', {})
        
        # Cập nhật kết quả
        train_session = db.query(TrainSession).filter(TrainSession.id == session_id).first()
        if train_session:
            train_session.status = "finished"
            train_session.finished_at = datetime.datetime.utcnow()
            train_session.result = json.dumps(result)
            
            # Lưu metrics vào database
            train_session.accuracy = metrics.get('accuracy')
            train_session.precision = metrics.get('precision')
            train_session.recall = metrics.get('recall')
            train_session.f1_score = metrics.get('f1_score')
            
            db.commit()
    except Exception as e:
        # Xử lý lỗi
        train_session = db.query(TrainSession).filter(TrainSession.id == session_id).first()
        if train_session:
            train_session.status = "failed"
            train_session.finished_at = datetime.datetime.utcnow()
            train_session.result = json.dumps({"error": str(e)})
            db.commit()
    finally:
        db.close()

def get_train_status_internal(session_id: int) -> Dict[str, Any]:
    """
    Lấy thông tin trạng thái phiên train
    
    Args:
        session_id: ID phiên train
        
    Returns:
        Thông tin phiên train
    """
    db = SessionLocal()
    try:
        train_session = db.query(TrainSession).filter(TrainSession.id == session_id).first()
        
        if not train_session:
            return {"error": "Train session not found"}
        
        response = {
            "train_session_id": train_session.id,
            "status": train_session.status,
            "started_at": train_session.started_at,
            "finished_at": train_session.finished_at,
            "parameters": json.loads(train_session.parameters) if train_session.parameters else {},
            "result": json.loads(train_session.result) if train_session.result else {}
        }
        
        # Thêm metrics nếu có
        if train_session.status == "finished":
            response["metrics"] = {
                "accuracy": train_session.accuracy,
                "precision": train_session.precision,
                "recall": train_session.recall,
                "f1_score": train_session.f1_score
            }
        
        return response
    finally:
        db.close()
# --- Kết thúc logic từ controller ---

@router.post("")
def train_model(request: TrainRequest, background_tasks: BackgroundTasks):
    """
    Endpoint để train/re-train model ViT5 với dữ liệu được cung cấp
    """
    # Tạo phiên train mới
    session_id = create_train_session(request.train_data, request.parameters)
    
    # Thực hiện train trong background
    background_tasks.add_task(
        train_model_background,
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
    return get_train_status_internal(session_id)
