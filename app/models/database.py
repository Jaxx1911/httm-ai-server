"""Database models and configuration"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from ..config.settings import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
