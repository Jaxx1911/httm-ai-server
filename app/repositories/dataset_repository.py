"""Repository for handling Dataset-related database operations"""
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from ..models import database as models

def get_datasets_with_stats(db: Session):
    """
    Retrieves all datasets with aggregated statistics about their samples.
    """
    # Using a raw SQL query for complex aggregation
    query = text("""
        SELECT
            d."dataset_ID",
            d.name,
            d.status,
            d.description,
            d."Adminadmin_id",
            COUNT(s."sample_id") AS sample_count,
            MIN(CHAR_LENGTH(s."input_text")) AS min_input_length,
            MAX(CHAR_LENGTH(s."input_text")) AS max_input_length,
            ROUND(AVG(CHAR_LENGTH(s."input_text"))::numeric, 2) AS avg_input_length,
            MIN(CHAR_LENGTH(s."target_summary")) AS min_target_length,
            MAX(CHAR_LENGTH(s."target_summary")) AS max_target_length,
            ROUND(AVG(CHAR_LENGTH(s."target_summary"))::numeric, 2) AS avg_target_length
        FROM "Dataset" d
        LEFT JOIN "Sample" s ON d."dataset_ID" = s."Datasetdataset_ID"
        GROUP BY
            d."dataset_ID",
            d.name,
            d.status,
            d.description,
            d."Adminadmin_id"
        ORDER BY d.name;
    """)
    result = db.execute(query).fetchall()
    
    # Convert the raw result to a list of dictionaries
    datasets = []
    for row in result:
        datasets.append({
            "dataset_ID": row[0],
            "name": row[1],
            "status": row[2],
            "description": row[3],
            "Adminadmin_id": row[4],
            "sample_count": row[5],
            "min_input_length": row[6],
            "max_input_length": row[7],
            "avg_input_length": round(row[8] if row[8] else 0, 2),
            "min_target_length": row[9],
            "max_target_length": row[10],
            "avg_target_length": round(row[11] if row[11] else 0, 2),
        })
    return datasets

def create_dataset(db: Session, dataset_data: dict, admin_id: str):
    """
    Creates a new dataset.
    """
    new_dataset = models.Dataset(
        **dataset_data,
        Adminadmin_id=admin_id
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)
    return new_dataset

def update_dataset(db: Session, dataset_id: str, dataset_data: dict):
    """
    Updates an existing dataset.
    """
    dataset = db.query(models.Dataset).filter(models.Dataset.dataset_ID == dataset_id).first()
    if dataset:
        for key, value in dataset_data.items():
            setattr(dataset, key, value)
        db.commit()
        db.refresh(dataset)
    return dataset

def delete_dataset(db: Session, dataset_id: str):
    """
    Deletes a dataset and its associated samples.
    """
    # First, delete associated samples
    db.query(models.Sample).filter(models.Sample.Datasetdataset_ID == dataset_id).delete(synchronize_session=False)
    
    # Then, delete the dataset
    dataset = db.query(models.Dataset).filter(models.Dataset.dataset_ID == dataset_id).first()
    if dataset:
        db.delete(dataset)
        db.commit()
        return True
    return False

def get_dataset(db: Session, dataset_id: str):
    """
    Retrieves a single dataset by its ID.
    """
    return db.query(models.Dataset).filter(models.Dataset.dataset_ID == dataset_id).first()

