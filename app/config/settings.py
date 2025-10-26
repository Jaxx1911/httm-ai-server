"""Application settings and configuration"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://vbs_platform:vbs_platform@localhost:5432/httm"
    )
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Model
    MODEL_NAME: str = os.getenv("MODEL_NAME", "VietAI/vit5-base")
    MAX_SUMMARY_LENGTH: int = int(os.getenv("MAX_SUMMARY_LENGTH", "128"))
    MAX_TITLE_LENGTH: int = int(os.getenv("MAX_TITLE_LENGTH", "32"))
    
    # Training
    DEFAULT_LEARNING_RATE: float = 5e-5
    DEFAULT_EPOCHS: int = 3
    DEFAULT_BATCH_SIZE: int = 4
    TRAIN_VAL_SPLIT: float = 0.8
    
    # Paths
    MODEL_CHECKPOINT_DIR: str = "./model_checkpoints"
    TRAINED_MODEL_DIR: str = "./trained_model"
    LOGS_DIR: str = "./logs"

# Global settings instance
settings = Settings()
