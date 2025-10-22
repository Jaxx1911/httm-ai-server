from sqlalchemy.orm import Session
from app.models.database import Admin

class AdminRepository:
    @staticmethod
    def get_by_username(db: Session, username: str) -> Admin | None:
        return db.query(Admin).filter(Admin.username == username).first()

    @staticmethod
    def verify_password(plain_password: str, stored_password: str) -> bool:
        return plain_password == stored_password

admin_repository = AdminRepository()
