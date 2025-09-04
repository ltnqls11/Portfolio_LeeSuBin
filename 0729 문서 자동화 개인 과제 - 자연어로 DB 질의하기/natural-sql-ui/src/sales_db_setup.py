# sales_db_setup.py
import sqlite3
import os

def setup_sales_database():
    """판매 데이터베이스 설정"""
    try:
        # 현재 스크립트가 있는 디렉토리에 DB 파일 생성
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "sales.db")
        
        print(f"📂 현재 디렉토리: {current_dir}")
        print(f"💾 데이터베이스 경로: {db_path}")
        
        # 데이터베이스 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 기존 테이블 삭제 (있다면)
        cursor.execute("DROP TABLE IF EXISTS sales")
        print("🗑️ 기존 sales 테이블 삭제 완료")
        
        # 새 테이블 생성
        cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL,
            date TEXT NOT NULL,
            category TEXT
        )
        """)
        print("📋 새 sales 테이블 생성 완료")
        
        # 샘플 데이터 삽입
        data = [
            ("Keyboard", 10, 25000, "2025-07-01", "Electronics"),
            ("Mouse", 5, 15000, "2025-07-01", "Electronics"),
            ("Keyboard", 20, 25000, "2025-07-15", "Electronics"),
            ("Monitor", 3, 300000, "2025-07-20", "Electronics"),
            ("Laptop", 2, 1200000, "2025-07-22", "Electronics"),
            ("Desk", 1, 150000, "2025-07-25", "Furniture"),
            ("Chair", 4, 80000, "2025-07-26", "Furniture"),
            ("Headphones", 8, 50000, "2025-07-28", "Electronics"),
            ("Webcam", 6, 70000, "2025-07-29", "Electronics"),
            ("Tablet", 3, 400000, "2025-07-30", "Electronics")
        ]
        
        cursor.executemany(
            "INSERT INTO sales (product, quantity, price, date, category) VALUES (?, ?, ?, ?, ?)", 
            data
        )
        print(f"📊 {len(data)}개의 샘플 데이터 삽입 완료")
        
        # 변경사항 저장
        conn.commit()
        
        # 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM sales")
        count = cursor.fetchone()[0]
        print(f"✅ 총 {count}개의 레코드가 저장되었습니다.")
        
        # 샘플 데이터 출력
        print("\n📋 저장된 데이터 미리보기:")
        cursor.execute("SELECT * FROM sales LIMIT 5")
        rows = cursor.fetchall()
        
        print("ID | Product    | Quantity | Price    | Date       | Category")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:2} | {row[1]:10} | {row[2]:8} | {row[3]:8} | {row[4]} | {row[5]}")
        
        # 연결 종료
        conn.close()
        print(f"\n🎉 데이터베이스 설정 완료!")
        print(f"📁 파일 위치: {db_path}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def verify_database():
    """데이터베이스 검증"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "sales.db")
        
        if not os.path.exists(db_path):
            print("❌ 데이터베이스 파일이 존재하지 않습니다.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 존재 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
        if not cursor.fetchone():
            print("❌ sales 테이블이 존재하지 않습니다.")
            return False
        
        # 데이터 개수 확인
        cursor.execute("SELECT COUNT(*) FROM sales")
        count = cursor.fetchone()[0]
        
        print(f"✅ 데이터베이스 검증 완료: {count}개 레코드")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 검증 오류: {e}")
        return False

if __name__ == "__main__":
    print("🚀 판매 데이터베이스 설정 시작...")
    print("=" * 50)
    
    # 데이터베이스 설정
    if setup_sales_database():
        print("\n🔍 데이터베이스 검증 중...")
        if verify_database():
            print("\n✅ 모든 작업이 성공적으로 완료되었습니다!")
        else:
            print("\n⚠️ 데이터베이스 검증에 실패했습니다.")
    else:
        print("\n❌ 데이터베이스 설정에 실패했습니다.")
    
    print("\n💡 사용법:")
    print("   - 같은 폴더의 main.py를 실행하여 웹 인터페이스를 시작하세요.")
    print("   - 또는 다른 Python 스크립트에서 sales.db를 사용하세요.")
    print("\n👋 프로그램을 종료합니다.")
