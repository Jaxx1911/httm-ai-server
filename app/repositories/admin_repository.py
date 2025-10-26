from sqlalchemy.orm import Session
from app.models.database import Admin
from typing import Optional
import uuid


class AdminRepository:
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[Admin]:
        return db.query(Admin).filter(Admin.username == username).first()

    @staticmethod
    def get_by_id(db: Session, admin_id: str) -> Optional[Admin]:
        return db.query(Admin).filter(Admin.id == admin_id).first()

    @staticmethod
    def verify_password(plain_password: str, stored_password: str) -> bool:
        return plain_password == stored_password

    @staticmethod
    def create(db: Session, username: str, password: str, name: str, email: str, phone: str) -> Admin:
        admin = Admin(
            id=f"adm_{str(uuid.uuid4())[:8]}",
            username=username,
            password=password,
            name=name,
            email=email,
            phone=phone
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin


admin_repository = AdminRepository()
