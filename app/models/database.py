"""Database models and configuration"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Date, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime, timezone
from ..config.settings import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Bảng Admin
class Admin(Base):
    __tablename__ = "admin"
    id = Column(String(255), primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(255), nullable=False)

    datasets = relationship("Dataset", back_populates="admin")
    models = relationship("Model", back_populates="creator")

# Bảng Dataset
class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    created_by = Column(String(255), ForeignKey("admin.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    admin = relationship("Admin", back_populates="datasets")
    samples = relationship("Sample", back_populates="dataset", cascade="all, delete-orphan")
    model_associations = relationship("ModelDataset", back_populates="dataset", cascade="all, delete-orphan")

class Model(Base):
    __tablename__ = "model"
    id = Column(String(255), primary_key=True)
    version = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    model_path = Column(String(500), nullable=False)
    status = Column(String(50), nullable=False, default="training")  # training, completed, failed, active
    is_active = Column(Boolean, default=False)
    training_duration = Column(Integer, nullable=True)  # seconds
    base_model_id = Column(String(255), ForeignKey("model.id"), nullable=True)
    created_by = Column(String(255), ForeignKey("admin.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    creator = relationship("Admin", back_populates="models")
    base_model = relationship("Model", remote_side="Model.id", backref="derived_models")
    dataset_associations = relationship("ModelDataset", back_populates="model", cascade="all, delete-orphan")

# Bảng Sample
class Sample(Base):
    __tablename__ = "sample"
    id = Column(String(255), primary_key=True)
    input_text = Column(Text, nullable=False)
    target_summary = Column(Text, nullable=False)
    category = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    language = Column(String(255), nullable=False, default="vi")
    created_at = Column(Date, nullable=False)
    source = Column(String(255), nullable=True)
    dataset_id = Column(String(255), ForeignKey("dataset.id"), nullable=False)

    dataset = relationship("Dataset", back_populates="samples")

# Bảng ModelDataset (bảng trung gian - many-to-many)
class ModelDataset(Base):
    __tablename__ = "model_dataset"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String(255), ForeignKey("dataset.id"), nullable=False)
    model_id = Column(String(255), ForeignKey("model.id"), nullable=False)
    weight = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    dataset = relationship("Dataset", back_populates="model_associations")
    model = relationship("Model", back_populates="dataset_associations")

# Tạo bảng nếu chưa tồn tại
Base.metadata.create_all(bind=engine)
