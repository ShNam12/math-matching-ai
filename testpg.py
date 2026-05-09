import os
import psycopg2
from dotenv import load_dotenv # Import kiểu này cho gọn nhé

# 3. Load trực tiếp từ đường dẫn đã chỉ định
load_dotenv()

# DATABASE_URL = "postgresql://postgres:Nam012345@localhost:5432/datn" # In ra lại để check chắc chắn đã có URL chưa

DATABASE_URL = os.getenv("DATABASE_URL") # Lấy URL từ biến môi trường
print(f"Đường dẫn kết nối đến database: {DATABASE_URL}") # In ra để kiểm tradef test_connection():
def test_connection():
    try:
        # Thử mở kết nối tới database
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Kết nối đến database 'datn' thành công rực rỡ!")
        
        # Test thử một query đơn giản: Lấy phiên bản PostgreSQL đang chạy
        cur = conn.cursor()
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(f"Phiên bản DB đang dùng: {db_version[0]}")
        
        # Nhớ đóng kết nối sau khi dùng xong
        cur.close()
        conn.close()
        
    except Exception as e:
        print("❌ Kết nối thất bại. Xem chi tiết lỗi dưới đây:")
        print(e)

if __name__ == "__main__":
    test_connection()