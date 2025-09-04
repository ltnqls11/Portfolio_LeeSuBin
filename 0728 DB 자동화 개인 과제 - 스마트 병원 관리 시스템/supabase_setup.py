"""
Supabase 연동 및 CSV 데이터 업로드 스크립트
"""

import pandas as pd
import os
from supabase import create_client, Client
from datetime import datetime
import json

class SupabaseManager:
    def __init__(self, url: str, key: str):
        """
        Supabase 클라이언트 초기화
        
        Args:
            url: Supabase 프로젝트 URL
            key: Supabase anon key
        """
        self.url = url
        self.key = key
        self.supabase: Client = create_client(url, key)
    
    def create_tables(self):
        """
        필요한 테이블들을 생성합니다.
        실제로는 Supabase 대시보드에서 SQL로 실행해야 합니다.
        """
        
        sql_commands = {
            "patients": """
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                birth_date DATE,
                gender VARCHAR(10),
                phone VARCHAR(20),
                address TEXT,
                medical_history TEXT,
                emergency_contact VARCHAR(20),
                insurance VARCHAR(50),
                registration_date DATE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """,
            
            "doctors": """
            CREATE TABLE IF NOT EXISTS doctors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                specialty VARCHAR(100),
                license_num VARCHAR(50),
                phone VARCHAR(20),
                email VARCHAR(100),
                work_hours VARCHAR(50),
                experience_years INTEGER,
                education TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """,
            
            "appointments": """
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER REFERENCES patients(id),
                doctor_id INTEGER REFERENCES doctors(id),
                date DATE NOT NULL,
                time TIME NOT NULL,
                status VARCHAR(50) DEFAULT '예약완료',
                treatment_type VARCHAR(100),
                notes TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """,
            
            "medical_records": """
            CREATE TABLE IF NOT EXISTS medical_records (
                id SERIAL PRIMARY KEY,
                appointment_id INTEGER REFERENCES appointments(id),
                patient_id INTEGER REFERENCES patients(id),
                doctor_id INTEGER REFERENCES doctors(id),
                chief_complaint TEXT,
                diagnosis TEXT,
                treatment TEXT,
                prescription TEXT,
                next_visit DATE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """,
            
            "sms_log": """
            CREATE TABLE IF NOT EXISTS sms_log (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT NOW(),
                recipient VARCHAR(20),
                message TEXT,
                status VARCHAR(20) DEFAULT '발송완료',
                message_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            
            "waiting_times": """
            CREATE TABLE IF NOT EXISTS waiting_times (
                id SERIAL PRIMARY KEY,
                appointment_id INTEGER REFERENCES appointments(id),
                patient_name VARCHAR(100),
                doctor_name VARCHAR(100),
                scheduled_time TIME,
                estimated_wait_minutes INTEGER,
                current_status VARCHAR(50) DEFAULT '대기중',
                last_updated TIMESTAMP DEFAULT NOW(),
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            
            "doctor_schedules": """
            CREATE TABLE IF NOT EXISTS doctor_schedules (
                id SERIAL PRIMARY KEY,
                doctor_id INTEGER REFERENCES doctors(id),
                doctor_name VARCHAR(100),
                date DATE,
                start_time TIME,
                end_time TIME,
                max_patients INTEGER DEFAULT 10,
                current_patients INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT '정상',
                notes TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """
        }
        
        return sql_commands
    
    def upload_csv_to_table(self, csv_file: str, table_name: str):
        """
        CSV 파일을 Supabase 테이블에 업로드
        
        Args:
            csv_file: CSV 파일 경로
            table_name: 대상 테이블 이름
        """
        try:
            # CSV 파일 읽기
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            # 데이터 전처리
            df = self.preprocess_dataframe(df, table_name)
            
            # 데이터를 딕셔너리 리스트로 변환
            data = df.to_dict('records')
            
            # Supabase에 데이터 삽입
            result = self.supabase.table(table_name).insert(data).execute()
            
            print(f"✅ {table_name} 테이블에 {len(data)}개 레코드 업로드 완료")
            return result
            
        except Exception as e:
            print(f"❌ {table_name} 업로드 실패: {e}")
            return None
    
    def preprocess_dataframe(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        테이블별 데이터 전처리
        """
        # 공통 전처리: NaN 값을 None으로 변경
        df = df.where(pd.notnull(df), None)
        
        # 테이블별 특별 처리
        if table_name == 'patients':
            # 날짜 형식 변환
            if 'birth_date' in df.columns:
                df['birth_date'] = pd.to_datetime(df['birth_date']).dt.strftime('%Y-%m-%d')
            if 'registration_date' in df.columns:
                df['registration_date'] = pd.to_datetime(df['registration_date']).dt.strftime('%Y-%m-%d')
                
        elif table_name == 'appointments':
            # 날짜 및 시간 형식 변환
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
        elif table_name == 'medical_records':
            # 날짜 형식 변환
            if 'next_visit' in df.columns:
                df['next_visit'] = pd.to_datetime(df['next_visit']).dt.strftime('%Y-%m-%d')
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
        elif table_name == 'sms_log':
            # 타임스탬프 형식 변환
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
        elif table_name == 'waiting_times':
            # 타임스탬프 형식 변환
            if 'last_updated' in df.columns:
                df['last_updated'] = pd.to_datetime(df['last_updated']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
        elif table_name == 'doctor_schedules':
            # 날짜 형식 변환
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        return df
    
    def fetch_all_data(self, table_name: str):
        """
        테이블의 모든 데이터 조회
        """
        try:
            result = self.supabase.table(table_name).select("*").execute()
            return result.data
        except Exception as e:
            print(f"❌ {table_name} 데이터 조회 실패: {e}")
            return None
    
    def clear_table(self, table_name: str):
        """
        테이블의 모든 데이터 삭제 (주의: 복구 불가능)
        """
        try:
            # 모든 레코드 조회
            all_data = self.fetch_all_data(table_name)
            if all_data:
                # 각 레코드의 ID로 삭제
                for record in all_data:
                    self.supabase.table(table_name).delete().eq('id', record['id']).execute()
                print(f"✅ {table_name} 테이블 초기화 완료")
            else:
                print(f"ℹ️ {table_name} 테이블이 이미 비어있습니다")
        except Exception as e:
            print(f"❌ {table_name} 테이블 초기화 실패: {e}")

def main():
    """
    메인 실행 함수
    """
    # Supabase 설정 (실제 값으로 변경 필요)
    SUPABASE_URL = "YOUR_SUPABASE_URL"  # 예: https://xxxxx.supabase.co
    SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"  # anon key
    
    # 환경변수에서 읽기 (권장)
    SUPABASE_URL = os.getenv('SUPABASE_URL', SUPABASE_URL)
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', SUPABASE_KEY)
    
    if SUPABASE_URL == "YOUR_SUPABASE_URL" or SUPABASE_KEY == "YOUR_SUPABASE_ANON_KEY":
        print("❌ Supabase URL과 KEY를 설정해주세요!")
        print("1. 환경변수 설정: SUPABASE_URL, SUPABASE_KEY")
        print("2. 또는 코드에서 직접 수정")
        return
    
    # Supabase 매니저 초기화
    sb_manager = SupabaseManager(SUPABASE_URL, SUPABASE_KEY)
    
    # CSV 파일과 테이블 매핑
    csv_table_mapping = {
        'patients_data.csv': 'patients',
        'doctors_data.csv': 'doctors',
        'appointments_data.csv': 'appointments',
        'medical_records_data.csv': 'medical_records',
        'sms_log_data.csv': 'sms_log',
        'waiting_times_data.csv': 'waiting_times',
        'doctor_schedules_data.csv': 'doctor_schedules'
    }
    
    print("🚀 Supabase 데이터 업로드 시작...")
    
    # 테이블 생성 SQL 출력
    print("\n📋 다음 SQL을 Supabase 대시보드에서 실행하세요:")
    print("=" * 50)
    sql_commands = sb_manager.create_tables()
    for table_name, sql in sql_commands.items():
        print(f"\n-- {table_name} 테이블")
        print(sql)
    print("=" * 50)
    
    # 사용자 확인
    response = input("\n테이블 생성을 완료했나요? (y/n): ")
    if response.lower() != 'y':
        print("테이블을 먼저 생성해주세요.")
        return
    
    # CSV 파일들을 순서대로 업로드
    upload_order = [
        'patients_data.csv',
        'doctors_data.csv', 
        'appointments_data.csv',
        'medical_records_data.csv',
        'sms_log_data.csv',
        'waiting_times_data.csv',
        'doctor_schedules_data.csv'
    ]
    
    for csv_file in upload_order:
        if os.path.exists(csv_file):
            table_name = csv_table_mapping[csv_file]
            print(f"\n📤 {csv_file} → {table_name} 업로드 중...")
            sb_manager.upload_csv_to_table(csv_file, table_name)
        else:
            print(f"⚠️ {csv_file} 파일을 찾을 수 없습니다.")
    
    print("\n✅ 모든 데이터 업로드 완료!")
    
    # 업로드 결과 확인
    print("\n📊 업로드 결과 확인:")
    for table_name in csv_table_mapping.values():
        data = sb_manager.fetch_all_data(table_name)
        if data:
            print(f"  - {table_name}: {len(data)}개 레코드")
        else:
            print(f"  - {table_name}: 데이터 없음")

if __name__ == "__main__":
    main()