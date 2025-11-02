from fastapi import APIRouter, Request

from app.controller.model_controller import model_controller
from app.schemas import TrainRequest

router = APIRouter(prefix="/model", tags=["model"])

@router.get("")
def get_all_models():
    models = model_controller.get_all_models()
    return {"models": models}

@router.post("/train")
def train_model(req: Request, body: TrainRequest):
    data = model_controller.train_model(body)
    return {"data": data}

@router.get("/status/{model_id}")
def get_model_status(model_id: str):
    return {"message": f"Trạng thái của mô hình tóm tắt với ID {model_id}"}

@router.post("/activate/{model_id}")
def activate_model(model_id: str):
    model_controller.activate_model(model_id)
    return True

@router.post("/save")
def save_model(model_data: dict):
    model_controller.save_model(model_data)
    return True

