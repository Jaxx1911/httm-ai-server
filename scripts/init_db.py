"""
Script để khởi tạo database tables
Chạy script này sau khi cấu hình PostgreSQL
"""
import sys
import os

# Thêm thư mục cha vào path để import được app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import Base, engine, SessionLocal, TrainSession

def init_db():
    """Khởi tạo tất cả các bảng trong database"""
    try:
        print("Đang khởi tạo database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Đã tạo thành công các bảng:")
        print("  - train_sessions")
        
        # Kiểm tra kết nối
        db = SessionLocal()
        count = db.query(TrainSession).count()
        db.close()
        print(f"✓ Kết nối database thành công!")
        print(f"  Số phiên train hiện có: {count}")
        
    except Exception as e:
        print(f"✗ Lỗi khi khởi tạo database:")
        print(f"  {str(e)}")
        print("\nHãy kiểm tra:")
        print("  1. PostgreSQL đã được cài đặt và chạy")
        print("  2. Database 'httm_db' đã được tạo")
        print("  3. Chuỗi kết nối DATABASE_URL trong file .env đúng")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
