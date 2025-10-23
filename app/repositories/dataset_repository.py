"""Repository for handling Dataset-related database operations"""
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from ..models import database as models
import uuid
from datetime import datetime


def get_datasets_with_stats(db: Session):
    """
    Retrieves all datasets with aggregated statistics about their samples.
    """
    # Using a raw SQL query for complex aggregation
    query = text("""
        SELECT
            d.id,
            d.name,
            d.status,
            d.description,
            d.created_by,
            d.created_at,
            COUNT(s.id) AS sample_count,
            MIN(CHAR_LENGTH(s.input_text)) AS min_input_length,
            MAX(CHAR_LENGTH(s.input_text)) AS max_input_length,
            ROUND(AVG(CHAR_LENGTH(s.input_text))::numeric, 2) AS avg_input_length,
            MIN(CHAR_LENGTH(s.target_summary)) AS min_target_length,
            MAX(CHAR_LENGTH(s.target_summary)) AS max_target_length,
            ROUND(AVG(CHAR_LENGTH(s.target_summary))::numeric, 2) AS avg_target_length
        FROM dataset d
        LEFT JOIN sample s ON d.id = s.dataset_id
        GROUP BY
            d.id,
            d.name,
            d.status,
            d.description,
            d.created_by,
            d.created_at
        ORDER BY d.created_at DESC;
    """)
    result = db.execute(query).fetchall()
    
    # Convert the raw result to a list of dictionaries
    datasets = []
    for row in result:
        datasets.append({
            "id": row[0],
            "name": row[1],
            "status": row[2],
            "description": row[3],
            "created_by": row[4],
            "created_at": row[5],
            "sample_count": row[6],
            "min_input_length": row[7],
            "max_input_length": row[8],
            "avg_input_length": round(row[9] if row[9] else 0, 2),
            "min_target_length": row[10],
            "max_target_length": row[11],
            "avg_target_length": round(row[12] if row[12] else 0, 2),
        })
    return datasets


def create_dataset(db: Session, dataset_data: dict, admin_id: str):
    """
    Creates a new dataset.
    """
    new_dataset = models.Dataset(
        id=f"ds_{str(uuid.uuid4())[:8]}",
        **dataset_data,
        created_by=admin_id,
        created_at=datetime.utcnow()
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)
    return new_dataset


def update_dataset(db: Session, dataset_id: str, dataset_data: dict):
    """
    Updates an existing dataset.
    """
    dataset = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()
    if dataset:
        for key, value in dataset_data.items():
            setattr(dataset, key, value)
        db.commit()
        db.refresh(dataset)
    return dataset


def delete_dataset(db: Session, dataset_id: str):
    """
    Deletes a dataset and its associated samples (cascade delete handled by SQLAlchemy).
    """
    dataset = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()
    if dataset:
        db.delete(dataset)
        db.commit()
        return True
    return False


def get_dataset(db: Session, dataset_id: str):
    """
    Retrieves a single dataset by its ID.
    """
    return db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()

