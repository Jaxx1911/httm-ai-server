from typing import List, Optional, Type, cast
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
from app.models.database import Model


class ModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Model]:
        return cast(list[Model], self.db.query(Model).all())

    def get_active_model(self) -> Optional[Model]:
        return self.db.query(Model).filter(Model.is_active == True).first()

    def set_active(self, model: Model):
        self.db.query(Model).update({Model.is_active: False})

        model.is_active = True
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_by_id(self, id: int) -> Optional[Type[Model]]:
        return self.db.query(Model).filter(Model.id == id).first()

    def insert(self, model: Model):
        model.id = f"{str(uuid.uuid4())[:8]}"
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model