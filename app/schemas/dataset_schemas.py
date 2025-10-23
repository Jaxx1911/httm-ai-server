from pydantic import BaseModel
from typing import Optional

class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "new"

class DatasetCreate(DatasetBase):
    pass

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Dataset(DatasetBase):
    id: str
    created_by: str
    sample_count: int
    min_input_length: Optional[int]
    max_input_length: Optional[int]
    avg_input_length: Optional[float]
    min_target_length: Optional[int]
    max_target_length: Optional[int]
    avg_target_length: Optional[float]

    class Config:
        from_attributes = True  
