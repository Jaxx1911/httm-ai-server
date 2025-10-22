"""
Script to populate the database with initial data from .jsonl files.
"""
import sys
import os
import json
import datetime
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Admin, Dataset, Sample
from sqlalchemy.orm import Session

# --- CONFIGURATION ---
JSONL_FILES = [
    "dantri_records.jsonl",
    "vietnamnet_records.jsonl",
    "vnexpress_records.jsonl",
]
DEFAULT_ADMIN_ID = "admin1"
DEFAULT_LANGUAGE = "vi"

def create_default_admin(db: Session):
    """Creates a default admin user if one doesn't exist."""
    admin = db.query(Admin).filter(Admin.admin_id == DEFAULT_ADMIN_ID).first()
    if not admin:
        print(f"Creating default admin: {DEFAULT_ADMIN_ID}")
        admin = Admin(
            admin_id=DEFAULT_ADMIN_ID,
            username="admin",
            password="123456", 
            name="Nguyễn Văn A",
            email="admin@example.com",
            phone="123456789"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("✓ Default admin created.")
    else:
        print(f"Admin '{DEFAULT_ADMIN_ID}' already exists.")
    return admin

def get_or_create_dataset(db: Session, category_name: str, admin_id: str):
    """Gets a dataset by category name or creates it if it doesn't exist."""
    dataset_name = f"Dataset {category_name}"
    dataset = db.query(Dataset).filter(Dataset.name == dataset_name).first()
    
    if not dataset:
        print(f"  - Dataset '{dataset_name}' not found. Creating new one...")
        dataset = Dataset(
            dataset_ID=f"ds_{str(uuid.uuid4())[:8]}",
            name=dataset_name,
            status="active",
            description=f"Dataset for category '{category_name}'",
            Adminadmin_id=admin_id
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        print(f"  ✓ New dataset created with ID: {dataset.dataset_ID}")
    return dataset

def populate_data():
    """Main function to populate the database."""
    db = SessionLocal()
    try:
        print("\n--- Starting Database Population ---")
        
        # 1. Create Admin
        admin = create_default_admin(db)
        
        # 2. Process each .jsonl file
        for file_name in JSONL_FILES:
            file_path = os.path.join(os.path.dirname(__file__), '..', file_name)
            if not os.path.exists(file_path):
                print(f"✗ WARNING: File '{file_name}' not found. Skipping.")
                continue
                
            print(f"\nProcessing file: {file_name}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    try:
                        record = json.loads(line)
                        
                        # Get or create the corresponding dataset
                        dataset = get_or_create_dataset(db, record['category'], admin.admin_id)
                        
                        # Create the sample
                        sample = Sample(
                            sample_id=f"smp_{str(uuid.uuid4())[:8]}",
                            input_text=record['input'],
                            target_summary=record['output'],
                            category=record['category'],
                            title=record['title'],
                            language=DEFAULT_LANGUAGE,
                            created_at=datetime.date.today(),
                            source=record.get('source'),
                            Datasetdataset_ID=dataset.dataset_ID
                        )
                        db.add(sample)
                        
                    except json.JSONDecodeError:
                        print(f"  ✗ Error decoding JSON on line {i+1} in {file_name}")
                    except KeyError as e:
                        print(f"  ✗ Missing key {e} in record on line {i+1} in {file_name}")

            # Commit changes for the current file
            db.commit()
            print(f"✓ Finished processing {file_name}.")

        print("\n--- Database Population Complete! ---")

    except Exception as e:
        print(f"\n✗ An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_data()
