from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from ..models.database import SessionLocal, Admin
from ..repositories import dataset_repository, sample_repository
from ..repositories.sample_repository import sample_repository  # Import thể hiện từ bên trong module
from ..schemas.dataset_schemas import DatasetCreate, DatasetUpdate
from ..schemas.sample_schemas import Sample
from ..controller.auth_controllers import get_current_user as get_current_admin

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/datasets", summary="Get all datasets with statistics")
def get_datasets_with_stats(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    """
    Retrieves a list of all datasets, including statistics about the samples
    they contain (count, min/max/avg lengths).
    """
    if not admin:
        raise HTTPException(status_code=401, detail="Authentication required")
    datasets = dataset_repository.get_datasets_with_stats(db)
    return datasets

@router.post("/api/datasets", summary="Create a new dataset")
def create_dataset(dataset: DatasetCreate, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    """
    Creates a new dataset.
    """
    if not admin:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    dataset_dict = dataset.dict()

    new_dataset = dataset_repository.create_dataset(db=db, dataset_data=dataset_dict, admin_id=admin.id)
    return new_dataset

@router.put("/api/datasets/{dataset_id}", summary="Update a dataset")
def update_dataset(dataset_id: str, dataset: DatasetUpdate, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    """
    Updates an existing dataset's information.
    """
    if not admin:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    db_dataset = dataset_repository.get_dataset(db, dataset_id=dataset_id)
    if db_dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    updated_dataset = dataset_repository.update_dataset(db=db, dataset_id=dataset_id, dataset_data=dataset.dict(exclude_unset=True))
    return updated_dataset

@router.delete("/api/datasets/{dataset_id}", summary="Delete a dataset")
def delete_dataset(dataset_id: str, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    """
    Deletes a dataset and all its associated samples.
    """
    if not admin:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    db_dataset = dataset_repository.get_dataset(db, dataset_id=dataset_id)
    if db_dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    success = dataset_repository.delete_dataset(db=db, dataset_id=dataset_id)
    if not success:
        # This case might be redundant due to the check above, but it's good practice
        raise HTTPException(status_code=404, detail="Dataset not found during deletion")
        
    return {"message": "Dataset and associated samples deleted successfully"}

@router.get("/api/datasets/{dataset_id}/samples", response_model=List[Sample], summary="Get samples for a specific dataset")
def get_samples_for_dataset(dataset_id: str, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    """
    Retrieves all samples belonging to a specific dataset.
    """
    if not admin:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    samples = sample_repository.get_samples_by_dataset(db, dataset_id)
    if not samples:
        return []
    return samples
