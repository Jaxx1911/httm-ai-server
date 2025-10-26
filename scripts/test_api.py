"""Test script for API endpoints"""

import sys
import os
import requests
import json
import time

# Thêm thư mục cha vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import settings

BASE_URL = f"http://{settings.HOST}:{settings.PORT}"

def test_summarize():
    """Test endpoint tóm tắt văn bản"""
    print("\n=== Test Summarize Endpoint ===")
    
    data = {
        "text": """
        Việt Nam, tên chính thức là Cộng hòa Xã hội chủ nghĩa Việt Nam, 
        là một quốc gia nằm ở phía đông bán đảo Đông Dương thuộc khu vực Đông Nam Á. 
        Việt Nam có diện tích khoảng 331.212 km² và dân số khoảng 98 triệu người, 
        là quốc gia đông dân thứ 15 trên thế giới.
        """
    }
    
    response = requests.post(f"{BASE_URL}/summarize", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Summarize thành công!")
        print(f"  Title: {result['title']}")
        print(f"  Summary: {result['summary']}")
    else:
        print(f"✗ Lỗi: {response.status_code}")
        print(f"  {response.text}")

def test_train():
    """Test endpoint train model"""
    print("\n=== Test Train Endpoint ===")
    
    data = {
        "train_data": [
            {
                "input_text": "Hôm nay trời đẹp, tôi đi dạo công viên với bạn bè.",
                "target_text": "Đi dạo công viên cùng bạn trong ngày đẹp trời"
            },
            {
                "input_text": "Tôi đã học Python được 3 năm và hiện đang làm việc tại một công ty công nghệ.",
                "target_text": "Làm việc tại công ty công nghệ sau 3 năm học Python"
            }
        ],
        "parameters": {
            "learning_rate": 5e-5,
            "epochs": 1,
            "batch_size": 2,
            "save_steps": 100
        }
    }
    
    response = requests.post(f"{BASE_URL}/train", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Train đã bắt đầu!")
        print(f"  Session ID: {result['train_session_id']}")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result['message']}")
        
        # Kiểm tra trạng thái train
        session_id = result['train_session_id']
        print(f"\n  Đang kiểm tra trạng thái train...")
        
        for i in range(5):
            time.sleep(5)
            status_response = requests.get(f"{BASE_URL}/train/{session_id}")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"  [{i+1}/5] Status: {status['status']}")
                
                if status['status'] == 'finished':
                    print(f"  ✓ Train hoàn thành!")
                    print(f"    Result: {json.dumps(status['result'], indent=2, ensure_ascii=False)}")
                    if 'metrics' in status:
                        print(f"\n  📊 Metrics đánh giá:")
                        print(f"    - Accuracy (ROUGE-1): {status['metrics']['accuracy']:.4f}")
                        print(f"    - Precision (ROUGE-2): {status['metrics']['precision']:.4f}")
                        print(f"    - Recall (ROUGE-L): {status['metrics']['recall']:.4f}")
                        print(f"    - F1 Score: {status['metrics']['f1_score']:.4f}")
                    break
                elif status['status'] == 'failed':
                    print(f"  ✗ Train thất bại!")
                    print(f"    Error: {status['result']}")
                    break
    else:
        print(f"✗ Lỗi: {response.status_code}")
        print(f"  {response.text}")

def test_server_health():
    """Kiểm tra server có chạy không"""
    print("\n=== Test Server Health ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Server đang chạy tại", BASE_URL)
            print(f"  API docs: {BASE_URL}/docs")
            return True
        else:
            print("✗ Server không phản hồi đúng")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Không thể kết nối đến server")
        print("  Hãy chạy: python app.py")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("HTTM API Test Script")
    print("=" * 50)
    
    # Kiểm tra server
    if not test_server_health():
        print("\nVui lòng khởi động server trước khi chạy test!")
        exit(1)
    
    # Test summarize
    test_summarize()
    
    # Test train (uncomment nếu muốn test)
    # print("\n" + "=" * 50)
    # choice = input("\nBạn có muốn test train endpoint? (y/n): ")
    # if choice.lower() == 'y':
    #     test_train()
    
    print("\n" + "=" * 50)
    print("Test hoàn thành!")
    print("=" * 50)
