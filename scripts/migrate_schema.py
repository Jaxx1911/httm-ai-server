"""
Migration script to update database schema from old structure to new structure
This script will:
1. Rename tables to lowercase
2. Rename columns (dataset_ID -> id, admin_id -> id, etc.)
3. Rename Model table to ModelVersion
4. Update foreign keys
"""

from sqlalchemy import create_engine, text
from app.config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    """Migrate database from old schema to new schema"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        try:
            logger.info("Starting database migration...")

            # Start transaction
            trans = conn.begin()

            try:
                # 1. Rename Admin table and columns
                logger.info("Migrating Admin table...")
                conn.execute(text('ALTER TABLE IF EXISTS "Admin" RENAME TO admin;'))
                conn.execute(text('ALTER TABLE admin RENAME COLUMN admin_id TO id;'))

                # 2. Rename Dataset table and columns
                logger.info("Migrating Dataset table...")
                conn.execute(text('ALTER TABLE IF EXISTS "Dataset" RENAME TO dataset;'))
                conn.execute(text('ALTER TABLE dataset RENAME COLUMN dataset_ID TO id;'))
                conn.execute(text('ALTER TABLE dataset RENAME COLUMN "Adminadmin_id" TO created_by;'))
                conn.execute(text('ALTER TABLE dataset ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();'))

                # 3. Rename Model table to ModelVersion and update columns
                logger.info("Migrating Model table to ModelVersion...")
                conn.execute(text('ALTER TABLE IF EXISTS "Model" RENAME TO model_version;'))
                conn.execute(text('ALTER TABLE model_version RENAME COLUMN model_id TO id;'))
                conn.execute(text('ALTER TABLE model_version RENAME COLUMN "F1Score" TO f1_score;'))
                conn.execute(text('ALTER TABLE model_version RENAME COLUMN "Adminadmin_id" TO created_by;'))
                conn.execute(text('ALTER TABLE model_version RENAME COLUMN path TO model_path;'))
                conn.execute(text('ALTER TABLE model_version RENAME COLUMN finetune_time TO training_duration;'))
                conn.execute(text('ALTER TABLE model_version RENAME COLUMN parameter TO parameters;'))
                conn.execute(text('ALTER TABLE model_version RENAME COLUMN baseModel TO base_model_id;'))

                # Add new columns to ModelVersion
                conn.execute(text('ALTER TABLE model_version ADD COLUMN IF NOT EXISTS version VARCHAR(255);'))
                conn.execute(text('ALTER TABLE model_version ADD COLUMN IF NOT EXISTS name VARCHAR(255);'))
                conn.execute(text('ALTER TABLE model_version ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT FALSE;'))
                conn.execute(text('ALTER TABLE model_version ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();'))
                conn.execute(text('ALTER TABLE model_version ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;'))

                # Update training_duration to integer (seconds)
                conn.execute(text('ALTER TABLE model_version ALTER COLUMN training_duration TYPE INTEGER USING EXTRACT(EPOCH FROM training_duration)::INTEGER;'))

                # 4. Rename Sample table and columns
                logger.info("Migrating Sample table...")
                conn.execute(text('ALTER TABLE IF EXISTS "Sample" RENAME TO sample;'))
                conn.execute(text('ALTER TABLE sample RENAME COLUMN sample_id TO id;'))
                conn.execute(text('ALTER TABLE sample RENAME COLUMN "Datasetdataset_ID" TO dataset_id;'))

                # 5. Rename ModelDataset table and columns
                logger.info("Migrating ModelDataset table...")
                conn.execute(text('ALTER TABLE IF EXISTS "ModelDataset" RENAME TO model_dataset;'))
                conn.execute(text('ALTER TABLE model_dataset RENAME COLUMN "Datasetdataset_ID" TO dataset_id;'))
                conn.execute(text('ALTER TABLE model_dataset RENAME COLUMN "Modelmodel_id" TO model_version_id;'))
                conn.execute(text('ALTER TABLE model_dataset ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY;'))
                conn.execute(text('ALTER TABLE model_dataset ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();'))

                # 6. Drop old TrainSession table if exists (replaced by ModelVersion)
                logger.info("Dropping TrainSession table if exists...")
                conn.execute(text('DROP TABLE IF EXISTS train_sessions;'))

                # Commit transaction
                trans.commit()
                logger.info("Database migration completed successfully!")

            except Exception as e:
                trans.rollback()
                logger.error(f"Migration failed: {str(e)}")
                raise e

        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            raise e


if __name__ == "__main__":
    migrate_database()

