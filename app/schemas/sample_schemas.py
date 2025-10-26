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
    id: str
    dataset_id: str
    created_at: Optional[date] = None
    language: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True
