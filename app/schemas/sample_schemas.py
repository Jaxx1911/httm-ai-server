from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class SampleBase(BaseModel):
    title: str
    input_text: str
    target_summary: str

class SampleCreate(SampleBase):
    dataset_id: str

class SampleUpdate(BaseModel):
    title: Optional[str] = None
    input_text: Optional[str] = None
    target_summary: Optional[str] = None

class Sample(SampleBase):
    sample_id: str
    dataset_id: str = Field(alias="Datasetdataset_ID")  # Map từ tên cột DB
    created_at: Optional[date] = None
    language: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True  # Cho phép sử dụng cả alias và tên field gốc