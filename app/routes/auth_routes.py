from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.repositories.admin_repository import admin_repository

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(req: Request, body: LoginRequest, db: Session = Depends(get_db)):
    """Endpoint đăng nhập, tạo session cookie."""
    admin = admin_repository.get_by_username(db, body.username)
    if not admin or not admin_repository.verify_password(body.password, admin.password):
        raise HTTPException(status_code=401, detail="Sai username hoặc password")
    
    req.session["user"] = {"username": admin.username, "admin_id": admin.admin_id}
    return {"message": "Đăng nhập thành công", "user": req.session["user"]}

@router.post("/logout")
def logout(req: Request, res: Response):
    """Endpoint đăng xuất, xóa session."""
    req.session.clear()
    res.delete_cookie("session")
    return {"message": "Đăng xuất thành công"}

@router.get("/me")
def get_current_user(req: Request):
    """Kiểm tra thông tin người dùng đang đăng nhập."""
    user = req.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    return user
