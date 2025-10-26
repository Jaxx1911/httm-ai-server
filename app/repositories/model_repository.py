from typing import List, Optional, Type, cast
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
import uuid
from app.models.database import Model, ModelSample, Sample
from datetime import date, datetime
from sqlalchemy import text, insert, delete

class ModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        query = text("""
                select m1.id, m1.name, m1.version, m1.status, m1.is_active, m1.created_at, m1.accuracy, m1.precision, m1.recall, m1.f1_score, m2.name
                from model m1
                left join model m2 on m1.base_model_id = m2.id
        """)
        models = []
        for row in self.db.execute(query).all():
            dt = datetime.strptime(str(row[5]), "%Y-%m-%d %H:%M:%S.%f")
            if row[10] is None:
                base_model_name = "VietAI/vit5-base"
            else:
                base_model_name = row[10]
            models.append({
                "id": row[0],
                "name": row[1],
                "version": row[2],
                "status": row[3],
                "is_active": row[4],
                "created_at": dt.isoformat(),
                "accuracy": row[6],
                "precision": row[7],
                "recall": row[8],
                "f1_score": row[9],
                "base_model_name": base_model_name,
            })

        return models

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

    def insert(self, model: Model, sample_ids: List[str], is_select_all: bool) -> Model:        
        model.id = f"{str(uuid.uuid4())[:8]}"
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        
        if is_select_all:
            # lấy all sample_id not in sample_ids
            query = self.db.query(Sample.id)
            if sample_ids:
                query = query.filter(Sample.id.notin_(sample_ids))
            selected_sample_ids = [s[0] for s in query.all()]
        else:
            selected_sample_ids = sample_ids

        if selected_sample_ids:
            associations = [
                {"model_id": model.id, "sample_id": sid}
                for sid in selected_sample_ids
            ]
            self.db.execute(insert(ModelSample), associations)
        
        self.db.commit()
        return model
    
    def update(self, model: Model, sample_ids: List[str], is_select_all: bool) -> Model:
        self.db.merge(model)
        self.db.commit()
        self.db.refresh(model)
        
        self.db.execute(
            delete(ModelSample).where(ModelSample.model_id == model.id)
        )
        
        if is_select_all:
            # lấy all sample_id not in sample_ids
            query = self.db.query(Sample.id)
            if sample_ids:
                query = query.filter(Sample.id.notin_(sample_ids))
            selected_sample_ids = [s[0] for s in query.all()]
        else:
            selected_sample_ids = sample_ids

        if selected_sample_ids:
            associations = [
                {"model_id": model.id, "sample_id": sid}
                for sid in selected_sample_ids
            ]
            self.db.execute(insert(ModelSample), associations)
        
        self.db.commit()
        return model