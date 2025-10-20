"""
Migration script để thêm các cột metrics vào bảng train_sessions
Chạy script này nếu bạn đã có database từ trước và muốn thêm tính năng đánh giá metrics
"""
import sys
import os

# Thêm thư mục cha vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.models.database import engine

def migrate_database():
    """Thêm các cột metrics vào bảng train_sessions"""
    try:
        print("Đang thêm các cột metrics vào bảng train_sessions...")
        
        with engine.connect() as conn:
            # Kiểm tra xem cột đã tồn tại chưa
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='train_sessions' AND column_name='accuracy'
            """)
            result = conn.execute(check_query)
            
            if result.fetchone():
                print("✓ Các cột metrics đã tồn tại, không cần migration.")
                return
            
            # Thêm các cột mới
            queries = [
                "ALTER TABLE train_sessions ADD COLUMN accuracy FLOAT",
                "ALTER TABLE train_sessions ADD COLUMN precision FLOAT",
                "ALTER TABLE train_sessions ADD COLUMN recall FLOAT",
                "ALTER TABLE train_sessions ADD COLUMN f1_score FLOAT"
            ]
            
            for query in queries:
                conn.execute(text(query))
            
            conn.commit()
            
        print("✓ Đã thêm thành công các cột metrics:")
        print("  - accuracy")
        print("  - precision")
        print("  - recall")
        print("  - f1_score")
        print("\nDatabase đã được cập nhật!")
        
    except Exception as e:
        print(f"✗ Lỗi khi migration:")
        print(f"  {str(e)}")
        print("\nNếu đây là database mới, hãy chạy:")
        print("  python scripts/init_db.py")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 50)
    print("Database Migration - Thêm Metrics Columns")
    print("=" * 50)
    migrate_database()
