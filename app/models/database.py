"""Database models and configuration"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Date, ForeignKey, Time, REAL, DOUBLE_PRECISION
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import datetime
from ..config.settings import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Bảng Admin
class Admin(Base):
    __tablename__ = "Admin"
    admin_id = Column(String(255), primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(255), nullable=False)

    datasets = relationship("Dataset", back_populates="admin")
    models = relationship("Model", back_populates="admin")

# Bảng Dataset
class Dataset(Base):
    __tablename__ = "Dataset"
    dataset_ID = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    Adminadmin_id = Column(String(255), ForeignKey("Admin.admin_id"), nullable=False)

    admin = relationship("Admin", back_populates="datasets")
    samples = relationship("Sample", back_populates="dataset")
    model_associations = relationship("ModelDataset", back_populates="dataset")

# Bảng Model
class Model(Base):
    __tablename__ = "Model"
    model_id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    accuracy = Column(REAL, nullable=False)
    precision = Column(DOUBLE_PRECISION, nullable=False)
    recall = Column(DOUBLE_PRECISION, nullable=False)
    F1Score = Column(DOUBLE_PRECISION, nullable=False)
    path = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    finetune_time = Column(Time, nullable=False)
    parameter = Column(DOUBLE_PRECISION, nullable=False)
    baseModel = Column(String(255), nullable=False)
    Adminadmin_id = Column(String(255), ForeignKey("Admin.admin_id"), nullable=False)

    admin = relationship("Admin", back_populates="models")
    dataset_associations = relationship("ModelDataset", back_populates="model")

# Bảng Sample
class Sample(Base):
    __tablename__ = "Sample"
    sample_id = Column(String(255), primary_key=True)
    input_text = Column(Text, nullable=False)
    target_summary = Column(Text, nullable=False)
    category = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    language = Column(String(255), nullable=False)
    created_at = Column(Date, nullable=False)
    source = Column(String(255), nullable=True)
    Datasetdataset_ID = Column(String(255), ForeignKey("Dataset.dataset_ID"), nullable=False)

    dataset = relationship("Dataset", back_populates="samples")

# Bảng ModelDataset (bảng trung gian)
class ModelDataset(Base):
    __tablename__ = "ModelDataset"
    Datasetdataset_ID = Column(String(255), ForeignKey("Dataset.dataset_ID"), primary_key=True)
    Modelmodel_id = Column(String(255), ForeignKey("Model.model_id"), primary_key=True)
    weight = Column(REAL, nullable=False)
    notes = Column(String(255), nullable=False)

    dataset = relationship("Dataset", back_populates="model_associations")
    model = relationship("Model", back_populates="dataset_associations")


class TrainSession(Base):
    """Model for storing training session information"""
    __tablename__ = "train_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # pending, running, finished, failed
    parameters = Column(Text)  # JSON string lưu thông số train
    result = Column(Text)      # JSON string lưu kết quả train
    
    # Metrics đánh giá model
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)

# Tạo bảng nếu chưa tồn tại
Base.metadata.create_all(bind=engine)
