"""
Supabase 연동 병원 관리 시스템 (간단 버전)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import os
from dotenv import load_dotenv
import json

# 환경변수 로드
load_dotenv()

# 물리치료 특화 데이터
PT_ASSESSMENTS = {
    "ROM": ["어깨 굴곡", "어깨 신전", "무릎 굴곡", "무릎 신전", "발목 배굴", "발목 저굴"],
    "MMT": ["상지근력", "하지근력", "체간근력", "목근력"],
    "기능평가": ["Berg Balance Scale", "Timed Up and Go", "6분 보행검사", "FIM"],
    "통증평가": ["VAS", "NRS", "McGill Pain Questionnaire"]
}

EXERCISE_PROGRAMS = {
    "어깨질환": {
        "급성기": ["Pendulum exercise", "PROM", "Isometric exercise"],
        "아급성기": ["AROM", "Strengthening", "Stretching"],
        "만성기": ["Functional training", "Sport-specific exercise"]
    },
    "무릎질환": {
        "급성기": ["Quad setting", "SLR", "Ankle pumping"],
        "아급성기": ["Closed chain exercise", "Balance training"],
        "만성기": ["Plyometric", "Return to sport"]
    },
    "요통": {
        "급성기": ["Williams exercise", "McKenzie exercise"],
        "아급성기": ["Core strengthening", "Postural training"],
        "만성기": ["Functional movement", "Work hardening"]
    }
}

PHYSICAL_AGENTS = {
    "열치료": ["Hot pack", "Paraffin bath", "Ultrasound", "Diathermy"],
    "냉치료": ["Cold pack", "Ice massage", "Contrast bath"],
    "전기치료": ["TENS", "FES", "IFC", "Russian current"],
    "견인치료": ["Cervical traction", "Lumbar traction"],
    "마사지": ["Swedish massage", "Deep friction massage", "Myofascial release"]
}

# 페이지 설정
st.set_page_config(
    page_title="스마트 병원 관리 시스템 (Supabase)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 스마트 병원 관리 시스템 (Supabase 연동)")

# Supabase 설정 확인
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

# 오프라인 모드 체크
offline_mode = st.sidebar.checkbox("🔌 오프라인 모드 (CSV 데이터 사용)", value=False)

if offline_mode:
    st.info("🔌 오프라인 모드: CSV 데이터를 사용합니다.")
    supabase = None
elif not supabase_url or not supabase_key or supabase_key == 'your-anon-key-here':
    st.error("🔧 Supabase 설정이 필요합니다!")
    
    with st.expander("설정 방법"):
        st.markdown("""
        ### 1단계: Supabase 프로젝트 생성
        1. [Supabase](https://supabase.com)에 가입
        2. 새 프로젝트 생성
        3. Settings → API에서 URL과 anon key 복사
        
        ### 2단계: .env 파일 설정
        ```
        SUPABASE_URL=https://your-project-id.supabase.co
        SUPABASE_KEY=your-actual-anon-key
        ```
        
        ### 또는 오프라인 모드 사용
        사이드바에서 "오프라인 모드" 체크박스를 선택하세요.
        """)
    
    st.stop()
else:
    supabase = None  # 일단 None으로 설정

# Supabase 연결 시도 (오프라인 모드가 아닐 때만)
if not offline_mode:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        st.success("✅ Supabase 연결 성공!")
    except Exception as e:
        st.error(f"❌ Supabase 연결 실패: {e}")
        st.warning("🔌 오프라인 모드로 전환하거나 네트워크 연결을 확인해주세요.")
        offline_mode = True
        supabase = None

# 샘플 데이터 생성 함수
def create_sample_data():
    """하드코딩된 샘플 데이터 생성"""
    
    # 샘플 환자 데이터
    patients_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['김민수', '이영희', '박철수', '최수진', '정대호'],
        'birth_date': ['1985-03-15', '1990-07-22', '1978-11-08', '1995-05-30', '1982-12-03'],
        'gender': ['남', '여', '남', '여', '남'],
        'phone': ['010-1234-5678', '010-2345-6789', '010-3456-7890', '010-4567-8901', '010-5678-9012'],
        'address': ['서울시 강남구', '서울시 서초구', '경기도 성남시', '서울시 송파구', '인천시 남동구'],
        'medical_history': ['어깨 탈구 병력', '무릎 인대 손상', '허리디스크 수술 이력', '목 디스크', '발목 골절 병력'],
        'insurance': ['건강보험', '건강보험', '의료급여', '건강보험', '산재보험']
    })
    
    # 샘플 의료진 데이터
    doctors_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['김재현', '박소영', '이동훈', '최민정', '정우성'],
        'specialty': ['물리치료', '정형외과', '재활의학과', '도수치료', '스포츠의학'],
        'phone': ['010-1111-2222', '010-2222-3333', '010-3333-4444', '010-4444-5555', '010-5555-6666'],
        'email': ['kim.pt@hospital.com', 'park.os@hospital.com', 'lee.rm@hospital.com', 'choi.mt@hospital.com', 'jung.sm@hospital.com'],
        'work_hours': ['09:00-18:00', '08:00-17:00', '10:00-19:00', '09:00-18:00', '14:00-22:00'],
        'experience_years': [6, 9, 7, 5, 8]
    })
    
    # 샘플 예약 데이터 (오늘과 내일 날짜로)
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    appointments_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'patient_id': [1, 2, 3, 4, 5],
        'doctor_id': [1, 2, 3, 1, 4],
        'date': [today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), 
                today.strftime('%Y-%m-%d'), tomorrow.strftime('%Y-%m-%d'), 
                tomorrow.strftime('%Y-%m-%d')],
        'time': ['09:00', '10:30', '14:00', '09:30', '11:00'],
        'status': ['예약완료', '진료완료', '예약완료', '예약완료', '예약완료'],
        'treatment_type': ['물리치료', '초진', '재진', '물리치료', '도수치료'],
        'notes': ['어깨 재활 치료', '무릎 통증 검사', '허리 재활 상담', '목 디스크 치료', '발목 관절 가동술']
    })
    
    # 샘플 대기시간 데이터
    waiting_times_data = pd.DataFrame({
        'id': [1, 2, 3],
        'patient_name': ['김민수', '박철수', '정대호'],
        'doctor_name': ['김재현', '이동훈', '최민정'],
        'scheduled_time': ['09:00', '14:00', '11:00'],
        'estimated_wait_minutes': [15, 8, 25],
        'current_status': ['대기중', '대기중', '대기중']
    })
    
    return {
        'patients': patients_data,
        'doctors': doctors_data,
        'appointments': appointments_data,
        'waiting_times': waiting_times_data
    }

# CSV 데이터 로딩 함수 (오프라인 모드용)
@st.cache_data
def load_csv_data():
    """CSV 파일들을 로드하거나 샘플 데이터 사용"""
    try:
        data = {}
        
        # CSV 파일이 있으면 로드, 없으면 샘플 데이터 사용
        if os.path.exists('patients_data.csv'):
            data['patients'] = pd.read_csv('patients_data.csv', encoding='utf-8')
        else:
            sample_data = create_sample_data()
            data['patients'] = sample_data['patients']
        
        if os.path.exists('doctors_data.csv'):
            data['doctors'] = pd.read_csv('doctors_data.csv', encoding='utf-8')
        else:
            if 'sample_data' not in locals():
                sample_data = create_sample_data()
            data['doctors'] = sample_data['doctors']
        
        if os.path.exists('appointments_data.csv'):
            data['appointments'] = pd.read_csv('appointments_data.csv', encoding='utf-8')
        else:
            if 'sample_data' not in locals():
                sample_data = create_sample_data()
            data['appointments'] = sample_data['appointments']
        
        if os.path.exists('waiting_times_data.csv'):
            data['waiting_times'] = pd.read_csv('waiting_times_data.csv', encoding='utf-8')
        else:
            if 'sample_data' not in locals():
                sample_data = create_sample_data()
            data['waiting_times'] = sample_data['waiting_times']
        
        return data
        
    except Exception as e:
        st.error(f"데이터 로딩 실패: {e}")
        # 오류 발생 시 샘플 데이터 반환
        return create_sample_data()

# 테이블 존재 여부 확인 및 생성
def check_and_create_tables():
    """테이블 존재 여부를 확인하고 없으면 생성"""
    try:
        # 테이블 존재 여부 확인
        result = supabase.table('patients').select('id').limit(1).execute()
        return True
    except Exception as e:
        if "does not exist" in str(e):
            st.warning("⚠️ 데이터베이스 테이블이 존재하지 않습니다.")
            
            with st.expander("🔧 테이블 생성 방법", expanded=True):
                st.markdown("**Supabase 대시보드에서 다음 SQL을 실행해주세요:**")
                
                sql_code = """
-- 환자 테이블
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
    registration_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 의료진 테이블
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
    created_at TIMESTAMP DEFAULT NOW()
);

-- 예약 테이블
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    doctor_id INTEGER REFERENCES doctors(id),
    date DATE NOT NULL,
    time TIME NOT NULL,
    status VARCHAR(50) DEFAULT '예약완료',
    treatment_type VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 진료 기록 테이블
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
    created_at TIMESTAMP DEFAULT NOW()
);

-- SMS 로그 테이블
CREATE TABLE IF NOT EXISTS sms_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    recipient VARCHAR(20),
    message TEXT,
    status VARCHAR(20) DEFAULT '발송완료',
    message_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
"""
                
                st.code(sql_code, language='sql')
                
                st.markdown("""
                **실행 방법:**
                1. [Supabase 대시보드](https://app.supabase.com) 접속
                2. 프로젝트 선택
                3. 왼쪽 메뉴에서 'SQL Editor' 클릭
                4. 위 SQL 코드를 복사해서 붙여넣기
                5. 'Run' 버튼 클릭
                6. 이 페이지를 새로고침
                """)
                
                # CSV 데이터 로딩 버튼
                if st.button("📊 샘플 데이터 로드 (테이블 생성 후)"):
                    load_sample_data()
            
            return False
        else:
            st.error(f"데이터베이스 연결 오류: {e}")
            return False

def load_sample_data():
    """CSV 파일에서 샘플 데이터 로드"""
    try:
        # 환자 데이터 로드
        if os.path.exists('patients_data.csv'):
            patients_df = pd.read_csv('patients_data.csv', encoding='utf-8')
            patients_data = patients_df.to_dict('records')
            
            for patient in patients_data:
                # ID 컬럼 제거 (자동 생성)
                if 'id' in patient:
                    del patient['id']
                
                try:
                    supabase.table('patients').insert(patient).execute()
                except:
                    pass  # 중복 데이터 무시
            
            st.success(f"✅ 환자 데이터 {len(patients_data)}건 로드 완료")
        
        # 의료진 데이터 로드
        if os.path.exists('doctors_data.csv'):
            doctors_df = pd.read_csv('doctors_data.csv', encoding='utf-8')
            doctors_data = doctors_df.to_dict('records')
            
            for doctor in doctors_data:
                if 'id' in doctor:
                    del doctor['id']
                
                try:
                    supabase.table('doctors').insert(doctor).execute()
                except:
                    pass
            
            st.success(f"✅ 의료진 데이터 {len(doctors_data)}건 로드 완료")
        
        # 예약 데이터 로드
        if os.path.exists('appointments_data.csv'):
            appointments_df = pd.read_csv('appointments_data.csv', encoding='utf-8')
            appointments_data = appointments_df.to_dict('records')
            
            for appointment in appointments_data:
                if 'id' in appointment:
                    del appointment['id']
                
                try:
                    supabase.table('appointments').insert(appointment).execute()
                except:
                    pass
            
            st.success(f"✅ 예약 데이터 {len(appointments_data)}건 로드 완료")
        
        st.success("🎉 모든 샘플 데이터 로드가 완료되었습니다!")
        st.info("페이지를 새로고침하여 데이터를 확인하세요.")
        
    except Exception as e:
        st.error(f"샘플 데이터 로드 실패: {e}")

# 테이블 확인
if not check_and_create_tables():
    st.stop()

# 사이드바 메뉴
menu = st.sidebar.selectbox("🔧 기능 선택", [
    "📊 대시보드",
    "👤 환자 관리",
    "👨‍⚕️ 의료진 관리", 
    "📅 예약 관리",
    "📋 진료 기록",
    "🏥 물리치료 특화",
    "📈 통계 및 리포트"
])

# 실시간 업데이트 버튼
if st.sidebar.button("🔄 새로고침"):
    st.rerun()

# 대시보드
if menu == "📊 대시보드":
    st.header("📊 병원 운영 현황 대시보드")
    
    if offline_mode or not supabase:
        # 오프라인 모드: CSV 데이터 또는 샘플 데이터 사용
        st.info("🔌 오프라인 모드: 샘플 데이터를 사용합니다.")
        csv_data = load_csv_data()
        
        if csv_data:
            appointments_df = csv_data['appointments']
            patients_df = csv_data['patients']
            waiting_df = csv_data['waiting_times']
            
            today_str = date.today().strftime('%Y-%m-%d')
            if not appointments_df.empty:
                today_appointments = appointments_df[appointments_df['date'] == today_str]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("오늘 예약", len(today_appointments))
                with col2:
                    completed = len(today_appointments[today_appointments['status'] == '진료완료'])
                    st.metric("진료 완료", completed)
                with col3:
                    waiting = len(today_appointments[today_appointments['status'] == '예약완료'])
                    st.metric("대기 중", waiting)
                with col4:
                    st.metric("총 환자 수", len(patients_df))
                
                # 오늘 예약 현황 표시
                if len(today_appointments) > 0:
                    st.subheader("📋 오늘 예약 현황")
                    
                    # 환자명과 의사명 매핑
                    patient_names = dict(zip(patients_df['id'], patients_df['name']))
                    doctor_names = dict(zip(csv_data['doctors']['id'], csv_data['doctors']['name']))
                    
                    display_appointments = today_appointments.copy()
                    display_appointments['환자명'] = display_appointments['patient_id'].map(patient_names)
                    display_appointments['의사명'] = display_appointments['doctor_id'].map(doctor_names)
                    
                    display_cols = ['환자명', '의사명', 'time', 'status', 'treatment_type']
                    final_df = display_appointments[display_cols]
                    final_df.columns = ['환자명', '담당의', '시간', '상태', '치료유형']
                    
                    st.dataframe(final_df, use_container_width=True)
                
                # 실시간 대기 현황
                st.subheader("⏰ 실시간 대기 현황")
                if not waiting_df.empty:
                    def get_wait_color(minutes):
                        if minutes <= 10:
                            return "🟢"
                        elif minutes <= 20:
                            return "🟡"
                        else:
                            return "🔴"
                    
                    waiting_display = waiting_df.copy()
                    waiting_display['상태'] = waiting_display['estimated_wait_minutes'].apply(
                        lambda x: f"{get_wait_color(x)} {x}분"
                    )
                    
                    display_cols = ['patient_name', 'doctor_name', 'scheduled_time', '상태']
                    display_df = waiting_display[display_cols]
                    display_df.columns = ['환자명', '담당의', '예약시간', '예상대기시간']
                    
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.info("현재 대기 중인 환자가 없습니다.")
            else:
                st.info("오늘 예약이 없습니다.")
        else:
            st.error("데이터를 로드할 수 없습니다.")
    else:
        # 온라인 모드: Supabase 사용
        try:
            # 통계 데이터 가져오기
            today = date.today().strftime('%Y-%m-%d')
            
            # 오늘 예약 수
            today_appointments = supabase.table('appointments').select('*').eq('date', today).execute()
            
            # 총 환자 수
            total_patients = supabase.table('patients').select('id').execute()
            
            # 진료 완료 수
            completed_today = supabase.table('appointments').select('*').eq('date', today).eq('status', '진료완료').execute()
            
            # 대기 중 수
            waiting_today = supabase.table('appointments').select('*').eq('date', today).eq('status', '예약완료').execute()
        
            # 메트릭 표시
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("오늘 예약", len(today_appointments.data))
            with col2:
                st.metric("진료 완료", len(completed_today.data))
            with col3:
                st.metric("대기 중", len(waiting_today.data))
            with col4:
                st.metric("총 환자 수", len(total_patients.data))
            
            # 오늘 예약 현황
            if today_appointments.data:
                st.subheader("📋 오늘 예약 현황")
                
                # 환자와 의료진 정보 조인
                appointments_with_details = supabase.table('appointments').select('''
                    *,
                    patients(name, phone),
                    doctors(name, specialty)
                ''').eq('date', today).execute()
                
                if appointments_with_details.data:
                    appointment_data = []
                    for apt in appointments_with_details.data:
                        appointment_data.append({
                            'ID': apt['id'],
                            '환자': apt['patients']['name'] if apt.get('patients') else 'N/A',
                            '의료진': apt['doctors']['name'] if apt.get('doctors') else 'N/A',
                            '전문분야': apt['doctors']['specialty'] if apt.get('doctors') else 'N/A',
                            '시간': apt['time'],
                            '상태': apt['status'],
                            '치료유형': apt.get('treatment_type', 'N/A')
                        })
                    
                    df_appointments = pd.DataFrame(appointment_data)
                    st.dataframe(df_appointments, use_container_width=True)
                else:
                    st.info("오늘 예약 상세 정보를 불러올 수 없습니다.")
            else:
                st.info("오늘 예약이 없습니다.")
                
        except Exception as e:
            st.error(f"대시보드 데이터 로딩 실패: {e}")

# 환자 관리
elif menu == "👤 환자 관리":
    st.header("👤 환자 관리")
    
    tab1, tab2 = st.tabs(["👤 환자 등록", "📋 환자 목록"])
    
    with tab1:
        st.subheader("새 환자 등록")
        
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("환자 이름*")
                birth_date = st.date_input("생년월일*")
                gender = st.selectbox("성별*", ["남", "여"])
            with col2:
                phone = st.text_input("연락처", placeholder="010-1234-5678")
                address = st.text_area("주소")
                insurance = st.selectbox("보험 유형", [
                    "건강보험", "의료급여", "산재보험", "자동차보험", "기타"
                ])
            
            medical_history = st.text_area("병력", placeholder="기존 질환이나 수술 이력")
            emergency_contact = st.text_input("응급연락처", placeholder="보호자 연락처")
            
            submitted = st.form_submit_button("환자 등록")
            
            if submitted and name:
                try:
                    patient_data = {
                        'name': name,
                        'birth_date': birth_date.strftime('%Y-%m-%d'),
                        'gender': gender,
                        'phone': phone,
                        'address': address,
                        'medical_history': medical_history,
                        'emergency_contact': emergency_contact,
                        'insurance': insurance,
                        'registration_date': date.today().strftime('%Y-%m-%d')
                    }
                    
                    result = supabase.table('patients').insert(patient_data).execute()
                    st.success("✅ 환자가 성공적으로 등록되었습니다!")
                    
                except Exception as e:
                    st.error(f"환자 등록 실패: {e}")
    
    with tab2:
        st.subheader("등록된 환자 목록")
        
        if offline_mode or not supabase:
            # 오프라인 모드: 샘플 데이터 사용
            csv_data = load_csv_data()
            if csv_data and not csv_data['patients'].empty:
                df_patients = csv_data['patients']
                
                # 검색 기능
                search_term = st.text_input("환자 검색", placeholder="이름으로 검색...")
                if search_term:
                    df_patients = df_patients[df_patients['name'].str.contains(search_term, na=False)]
                
                # 환자 목록 표시
                display_cols = ['id', 'name', 'birth_date', 'gender', 'phone', 'insurance']
                available_cols = [col for col in display_cols if col in df_patients.columns]
                
                if available_cols:
                    display_df = df_patients[available_cols]
                    column_names = {
                        'id': 'ID',
                        'name': '이름',
                        'birth_date': '생년월일',
                        'gender': '성별',
                        'phone': '연락처',
                        'insurance': '보험'
                    }
                    display_df.columns = [column_names.get(col, col) for col in available_cols]
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.dataframe(df_patients, use_container_width=True)
            else:
                st.info("등록된 환자가 없습니다.")
        else:
            # 온라인 모드: Supabase 사용
            try:
                patients = supabase.table('patients').select('*').execute()
                
                if patients.data:
                    df_patients = pd.DataFrame(patients.data)
                    
                    # 검색 기능
                    search_term = st.text_input("환자 검색", placeholder="이름으로 검색...")
                    if search_term:
                        df_patients = df_patients[df_patients['name'].str.contains(search_term, na=False)]
                    
                    # 환자 목록 표시
                    display_cols = ['id', 'name', 'birth_date', 'gender', 'phone', 'insurance', 'registration_date']
                    if all(col in df_patients.columns for col in display_cols):
                        display_df = df_patients[display_cols]
                        display_df.columns = ['ID', '이름', '생년월일', '성별', '연락처', '보험', '등록일']
                        st.dataframe(display_df, use_container_width=True)
                    else:
                        st.dataframe(df_patients, use_container_width=True)
                else:
                    st.info("등록된 환자가 없습니다.")
                    
            except Exception as e:
                st.error(f"환자 목록 조회 실패: {e}")

# 의료진 관리
elif menu == "👨‍⚕️ 의료진 관리":
    st.header("👨‍⚕️ 의료진 관리")
    
    tab1, tab2 = st.tabs(["👨‍⚕️ 의료진 등록", "📋 의료진 목록"])
    
    with tab1:
        st.subheader("새 의료진 등록")
        
        with st.form("doctor_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("의료진 이름*")
                specialty = st.selectbox("전문 분야*", [
                    "물리치료", "정형외과", "재활의학과", "신경외과",
                    "스포츠의학", "도수치료", "운동치료"
                ])
                license_num = st.text_input("면허번호")
            with col2:
                phone = st.text_input("연락처")
                email = st.text_input("이메일")
                work_hours = st.selectbox("근무시간", [
                    "09:00-18:00", "08:00-17:00", "10:00-19:00",
                    "14:00-22:00", "교대근무"
                ])
            
            experience_years = st.number_input("경력 (년)", min_value=0, max_value=50, value=0)
            education = st.text_area("학력", placeholder="졸업 대학 및 전공")
            
            submitted = st.form_submit_button("의료진 등록")
            
            if submitted and name:
                try:
                    doctor_data = {
                        'name': name,
                        'specialty': specialty,
                        'license_num': license_num,
                        'phone': phone,
                        'email': email,
                        'work_hours': work_hours,
                        'experience_years': experience_years,
                        'education': education
                    }
                    
                    result = supabase.table('doctors').insert(doctor_data).execute()
                    st.success("✅ 의료진이 성공적으로 등록되었습니다!")
                    
                except Exception as e:
                    st.error(f"의료진 등록 실패: {e}")
    
    with tab2:
        st.subheader("등록된 의료진 목록")
        
        if offline_mode or not supabase:
            # 오프라인 모드: 샘플 데이터 사용
            csv_data = load_csv_data()
            if csv_data and not csv_data['doctors'].empty:
                df_doctors = csv_data['doctors']
                
                display_cols = ['id', 'name', 'specialty', 'phone', 'email', 'work_hours', 'experience_years']
                available_cols = [col for col in display_cols if col in df_doctors.columns]
                
                if available_cols:
                    display_df = df_doctors[available_cols]
                    column_names = {
                        'id': 'ID',
                        'name': '이름',
                        'specialty': '전문분야',
                        'phone': '연락처',
                        'email': '이메일',
                        'work_hours': '근무시간',
                        'experience_years': '경력'
                    }
                    display_df.columns = [column_names.get(col, col) for col in available_cols]
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.dataframe(df_doctors, use_container_width=True)
            else:
                st.info("등록된 의료진이 없습니다.")
        else:
            # 온라인 모드: Supabase 사용
            try:
                doctors = supabase.table('doctors').select('*').execute()
                
                if doctors.data:
                    df_doctors = pd.DataFrame(doctors.data)
                    
                    display_cols = ['id', 'name', 'specialty', 'phone', 'email', 'work_hours', 'experience_years']
                    if all(col in df_doctors.columns for col in display_cols):
                        display_df = df_doctors[display_cols]
                        display_df.columns = ['ID', '이름', '전문분야', '연락처', '이메일', '근무시간', '경력']
                        st.dataframe(display_df, use_container_width=True)
                    else:
                        st.dataframe(df_doctors, use_container_width=True)
                else:
                    st.info("등록된 의료진이 없습니다.")
                    
            except Exception as e:
                st.error(f"의료진 목록 조회 실패: {e}")

# 예약 관리
elif menu == "📅 예약 관리":
    st.header("📅 예약 관리")
    
    tab1, tab2 = st.tabs(["📅 새 예약", "📋 예약 현황"])
    
    with tab1:
        st.subheader("새 예약 등록")
        
        try:
            # 환자와 의료진 데이터 가져오기
            patients = supabase.table('patients').select('*').execute()
            doctors = supabase.table('doctors').select('*').execute()
            
            if not patients.data or not doctors.data:
                st.warning("환자와 의료진을 먼저 등록해주세요.")
            else:
                with st.form("appointment_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        patient_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in patients.data}
                        selected_patient = st.selectbox("환자 선택*", list(patient_options.keys()))
                        
                        doctor_options = {f"{d['name']} - {d['specialty']} (ID: {d['id']})": d['id'] for d in doctors.data}
                        selected_doctor = st.selectbox("의료진 선택*", list(doctor_options.keys()))
                    
                    with col2:
                        appt_date = st.date_input("진료 날짜*", min_value=date.today())
                        appt_time = st.time_input("진료 시간*")
                    
                    treatment_type = st.selectbox("치료 유형", [
                        "초진", "재진", "물리치료", "도수치료", "운동치료", "검사"
                    ])
                    notes = st.text_area("특이사항")
                    
                    submitted = st.form_submit_button("예약 등록")
                    
                    if submitted:
                        try:
                            appointment_data = {
                                'patient_id': patient_options[selected_patient],
                                'doctor_id': doctor_options[selected_doctor],
                                'date': appt_date.strftime('%Y-%m-%d'),
                                'time': appt_time.strftime('%H:%M:%S'),
                                'status': '예약완료',
                                'treatment_type': treatment_type,
                                'notes': notes
                            }
                            
                            result = supabase.table('appointments').insert(appointment_data).execute()
                            st.success("✅ 예약이 성공적으로 등록되었습니다!")
                            
                        except Exception as e:
                            st.error(f"예약 등록 실패: {e}")
                            
        except Exception as e:
            st.error(f"데이터 로딩 실패: {e}")
    
    with tab2:
        st.subheader("예약 현황")
        
        # 날짜 필터
        filter_date = st.date_input("날짜 선택", value=date.today())
        
        try:
            appointments = supabase.table('appointments').select('''
                *,
                patients(name, phone),
                doctors(name, specialty)
            ''').eq('date', filter_date.strftime('%Y-%m-%d')).execute()
            
            if appointments.data:
                # 예약 목록 표시
                appointment_data = []
                for apt in appointments.data:
                    appointment_data.append({
                        'ID': apt['id'],
                        '환자': apt['patients']['name'] if apt.get('patients') else 'N/A',
                        '의료진': apt['doctors']['name'] if apt.get('doctors') else 'N/A',
                        '전문분야': apt['doctors']['specialty'] if apt.get('doctors') else 'N/A',
                        '시간': apt['time'],
                        '상태': apt['status'],
                        '치료유형': apt.get('treatment_type', 'N/A')
                    })
                
                df_appointments = pd.DataFrame(appointment_data)
                st.dataframe(df_appointments, use_container_width=True)
                
                # 상태 변경
                st.subheader("예약 상태 변경")
                col1, col2, col3 = st.columns(3)
                with col1:
                    appt_id = st.selectbox("예약 선택", [apt['id'] for apt in appointments.data])
                with col2:
                    new_status = st.selectbox("새 상태", ["예약완료", "진료중", "진료완료", "취소", "노쇼"])
                with col3:
                    if st.button("상태 변경"):
                        try:
                            result = supabase.table('appointments').update({
                                'status': new_status
                            }).eq('id', appt_id).execute()
                            st.success(f"예약 상태가 '{new_status}'로 변경되었습니다!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"상태 변경 실패: {e}")
            else:
                st.info("선택한 날짜에 예약이 없습니다.")
                
        except Exception as e:
            st.error(f"예약 조회 실패: {e}")

# 물리치료 특화 기능
elif menu == "🏥 물리치료 특화":
    st.header("🏥 물리치료 특화 시스템")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 평가", "🏃‍♂️ 운동처방", "⚡ 물리치료", "📈 진행도", "🏠 홈프로그램"
    ])
    
    with tab1:
        st.subheader("🔍 물리치료 평가")
        
        # 환자 선택
        try:
            patients = supabase.table('patients').select('*').execute()
            doctors = supabase.table('doctors').select('*').execute()
            
            if patients.data and doctors.data:
                patient_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in patients.data}
                doctor_options = {f"{d['name']} - {d['specialty']} (ID: {d['id']})": d['id'] for d in doctors.data}
                
                with st.form("pt_assessment_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_patient = st.selectbox("환자 선택", list(patient_options.keys()))
                        selected_doctor = st.selectbox("담당 치료사", list(doctor_options.keys()))
                    
                    st.write("**관절가동범위 (ROM) 측정**")
                    rom_data = {}
                    rom_cols = st.columns(3)
                    for i, joint in enumerate(PT_ASSESSMENTS["ROM"]):
                        with rom_cols[i % 3]:
                            rom_data[joint] = st.number_input(f"{joint} (도)", 0, 180, 90, key=f"rom_{i}")
                    
                    st.write("**근력검사 (MMT)**")
                    mmt_data = {}
                    mmt_cols = st.columns(2)
                    for i, muscle in enumerate(PT_ASSESSMENTS["MMT"]):
                        with mmt_cols[i % 2]:
                            mmt_data[muscle] = st.selectbox(f"{muscle}", 
                                ["0 (Zero)", "1 (Trace)", "2 (Poor)", "3 (Fair)", "4 (Good)", "5 (Normal)"],
                                index=4, key=f"mmt_{i}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        pain_score = st.slider("통증 점수 (VAS)", 0, 10, 0)
                    with col2:
                        functional_score = st.number_input("기능점수", 0, 100, 50)
                    
                    assessment_notes = st.text_area("평가 소견")
                    
                    submitted = st.form_submit_button("평가 저장")
                    
                    if submitted:
                        try:
                            assessment_data = {
                                'patient_id': patient_options[selected_patient],
                                'doctor_id': doctor_options[selected_doctor],
                                'rom_data': json.dumps(rom_data),
                                'mmt_data': json.dumps(mmt_data),
                                'pain_score': pain_score,
                                'functional_score': functional_score,
                                'assessment_notes': assessment_notes,
                                'assessment_date': date.today().strftime('%Y-%m-%d')
                            }
                            
                            result = supabase.table('pt_assessments').insert(assessment_data).execute()
                            st.success("✅ 물리치료 평가가 저장되었습니다!")
                            
                        except Exception as e:
                            st.error(f"평가 저장 실패: {e}")
                            st.info("💡 pt_additional_tables.sql을 먼저 실행해주세요.")
            else:
                st.warning("환자와 의료진을 먼저 등록해주세요.")
                
        except Exception as e:
            st.error(f"데이터 로딩 실패: {e}")
    
    with tab2:
        st.subheader("🏃‍♂️ 운동처방")
        
        try:
            patients = supabase.table('patients').select('*').execute()
            doctors = supabase.table('doctors').select('*').execute()
            
            if patients.data and doctors.data:
                patient_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in patients.data}
                doctor_options = {f"{d['name']} - {d['specialty']} (ID: {d['id']})": d['id'] for d in doctors.data}
                
                with st.form("exercise_prescription_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_patient = st.selectbox("환자 선택", list(patient_options.keys()), key="ex_patient")
                        selected_doctor = st.selectbox("처방 치료사", list(doctor_options.keys()), key="ex_doctor")
                    
                    diagnosis = st.selectbox("진단명", list(EXERCISE_PROGRAMS.keys()))
                    phase = st.selectbox("치료 단계", list(EXERCISE_PROGRAMS[diagnosis].keys()))
                    
                    st.write(f"**{diagnosis} - {phase} 권장 운동**")
                    exercises = EXERCISE_PROGRAMS[diagnosis][phase]
                    selected_exercises = st.multiselect("처방할 운동 선택", exercises, default=exercises)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        sets = st.number_input("세트", 1, 10, 3)
                    with col2:
                        reps = st.number_input("반복", 1, 50, 10)
                    with col3:
                        frequency = st.selectbox("빈도", ["1일 1회", "1일 2회", "1일 3회"])
                    
                    duration_weeks = st.number_input("처방 기간 (주)", 1, 12, 4)
                    special_instructions = st.text_area("특별 지시사항")
                    
                    submitted = st.form_submit_button("운동처방 저장")
                    
                    if submitted:
                        try:
                            prescription_data = {
                                'patient_id': patient_options[selected_patient],
                                'doctor_id': doctor_options[selected_doctor],
                                'diagnosis': diagnosis,
                                'treatment_phase': phase,
                                'prescribed_exercises': json.dumps(selected_exercises),
                                'sets': sets,
                                'reps': reps,
                                'frequency': frequency,
                                'duration_weeks': duration_weeks,
                                'special_instructions': special_instructions,
                                'prescription_date': date.today().strftime('%Y-%m-%d')
                            }
                            
                            result = supabase.table('exercise_prescriptions').insert(prescription_data).execute()
                            st.success("✅ 운동처방이 저장되었습니다!")
                            
                            # 처방전 출력
                            st.subheader("📋 운동처방전")
                            st.write(f"**환자**: {selected_patient.split(' (')[0]}")
                            st.write(f"**진단**: {diagnosis}")
                            st.write(f"**치료단계**: {phase}")
                            st.write("**처방 운동**:")
                            for exercise in selected_exercises:
                                st.write(f"- {exercise}: {sets}세트 × {reps}회, {frequency}")
                            if special_instructions:
                                st.write(f"**특별 지시사항**: {special_instructions}")
                            
                        except Exception as e:
                            st.error(f"운동처방 저장 실패: {e}")
                            st.info("💡 pt_additional_tables.sql을 먼저 실행해주세요.")
            else:
                st.warning("환자와 의료진을 먼저 등록해주세요.")
                
        except Exception as e:
            st.error(f"데이터 로딩 실패: {e}")
    
    with tab3:
        st.subheader("⚡ 물리적 인자 치료")
        
        try:
            patients = supabase.table('patients').select('*').execute()
            doctors = supabase.table('doctors').select('*').execute()
            
            if patients.data and doctors.data:
                patient_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in patients.data}
                doctor_options = {f"{d['name']} - {d['specialty']} (ID: {d['id']})": d['id'] for d in doctors.data}
                
                with st.form("physical_agent_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_patient = st.selectbox("환자 선택", list(patient_options.keys()), key="pa_patient")
                        selected_doctor = st.selectbox("치료사", list(doctor_options.keys()), key="pa_doctor")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        agent_type = st.selectbox("치료 분류", list(PHYSICAL_AGENTS.keys()))
                        agent_method = st.selectbox("치료 방법", PHYSICAL_AGENTS[agent_type])
                    
                    with col2:
                        intensity = st.text_input("강도/온도", placeholder="예: 40°C, Medium")
                        duration = st.number_input("시간 (분)", 1, 60, 15)
                    
                    body_part = st.text_input("적용 부위", placeholder="예: 우측 어깨")
                    response = st.text_area("환자 반응", placeholder="치료 중 환자의 반응이나 특이사항")
                    
                    submitted = st.form_submit_button("치료 기록 저장")
                    
                    if submitted:
                        try:
                            treatment_data = {
                                'patient_id': patient_options[selected_patient],
                                'doctor_id': doctor_options[selected_doctor],
                                'agent_type': agent_type,
                                'agent_method': agent_method,
                                'intensity': intensity,
                                'duration_minutes': duration,
                                'body_part': body_part,
                                'patient_response': response,
                                'treatment_date': date.today().strftime('%Y-%m-%d')
                            }
                            
                            result = supabase.table('physical_agent_treatments').insert(treatment_data).execute()
                            st.success("✅ 물리적 인자 치료 기록이 저장되었습니다!")
                            
                        except Exception as e:
                            st.error(f"치료 기록 저장 실패: {e}")
                            st.info("💡 pt_additional_tables.sql을 먼저 실행해주세요.")
            else:
                st.warning("환자와 의료진을 먼저 등록해주세요.")
                
        except Exception as e:
            st.error(f"데이터 로딩 실패: {e}")
    
    with tab4:
        st.subheader("📈 치료 진행도 추적")
        
        try:
            patients = supabase.table('patients').select('*').execute()
            
            if patients.data:
                patient_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in patients.data}
                selected_patient = st.selectbox("환자 선택", list(patient_options.keys()), key="progress_patient")
                patient_id = patient_options[selected_patient]
                
                # 진행도 데이터 조회
                progress_data = supabase.table('treatment_progress').select('*').eq('patient_id', patient_id).order('measurement_date').execute()
                
                if progress_data.data:
                    df_progress = pd.DataFrame(progress_data.data)
                    df_progress['measurement_date'] = pd.to_datetime(df_progress['measurement_date'])
                    
                    # 통증 점수 변화
                    if 'pain_score' in df_progress.columns:
                        fig_pain = px.line(df_progress, x='measurement_date', y='pain_score',
                                         title="통증 점수 변화", markers=True)
                        fig_pain.update_layout(yaxis_title="VAS 점수", xaxis_title="날짜")
                        st.plotly_chart(fig_pain, use_container_width=True)
                    
                    # 기능 점수 변화
                    if 'functional_score' in df_progress.columns:
                        fig_function = px.line(df_progress, x='measurement_date', y='functional_score',
                                             title="기능 점수 향상", markers=True)
                        fig_function.update_layout(yaxis_title="기능 점수", xaxis_title="날짜")
                        st.plotly_chart(fig_function, use_container_width=True)
                    
                    # 데이터 테이블
                    st.subheader("📊 진행도 데이터")
                    display_cols = ['measurement_date', 'pain_score', 'functional_score', 'notes']
                    available_cols = [col for col in display_cols if col in df_progress.columns]
                    if available_cols:
                        display_df = df_progress[available_cols]
                        column_names = {
                            'measurement_date': '측정일',
                            'pain_score': '통증점수',
                            'functional_score': '기능점수',
                            'notes': '메모'
                        }
                        display_df.columns = [column_names.get(col, col) for col in available_cols]
                        st.dataframe(display_df, use_container_width=True)
                else:
                    st.info("해당 환자의 진행도 데이터가 없습니다.")
                    
                    # 새 진행도 데이터 입력
                    st.subheader("📝 새 진행도 기록")
                    with st.form("progress_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            pain_score = st.slider("통증 점수", 0, 10, 0, key="progress_pain")
                        with col2:
                            functional_score = st.number_input("기능 점수", 0, 100, 50, key="progress_function")
                        
                        notes = st.text_area("메모", key="progress_notes")
                        
                        submitted = st.form_submit_button("진행도 기록 저장")
                        
                        if submitted:
                            try:
                                progress_record = {
                                    'patient_id': patient_id,
                                    'measurement_date': date.today().strftime('%Y-%m-%d'),
                                    'pain_score': pain_score,
                                    'functional_score': functional_score,
                                    'notes': notes
                                }
                                
                                result = supabase.table('treatment_progress').insert(progress_record).execute()
                                st.success("✅ 진행도 기록이 저장되었습니다!")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"진행도 기록 저장 실패: {e}")
                                st.info("💡 pt_additional_tables.sql을 먼저 실행해주세요.")
            else:
                st.warning("등록된 환자가 없습니다.")
                
        except Exception as e:
            st.error(f"데이터 로딩 실패: {e}")
    
    with tab5:
        st.subheader("🏠 홈 프로그램 관리")
        
        try:
            patients = supabase.table('patients').select('*').execute()
            doctors = supabase.table('doctors').select('*').execute()
            
            if patients.data and doctors.data:
                patient_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in patients.data}
                doctor_options = {f"{d['name']} - {d['specialty']} (ID: {d['id']})": d['id'] for d in doctors.data}
                
                with st.form("home_program_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_patient = st.selectbox("환자 선택", list(patient_options.keys()), key="home_patient")
                        selected_doctor = st.selectbox("처방 치료사", list(doctor_options.keys()), key="home_doctor")
                    
                    program_type = st.selectbox("프로그램 유형", 
                        ["자가 운동", "일상생활 지침", "자세 교정", "통증 관리"])
                    
                    program_content = []
                    if program_type == "자가 운동":
                        st.write("**자가 운동 프로그램**")
                        program_content = st.multiselect("운동 선택", [
                            "목 스트레칭", "어깨 돌리기", "벽 팔굽혀펴기", 
                            "스쿼트", "종아리 스트레칭", "허리 신전 운동"
                        ])
                        
                    elif program_type == "일상생활 지침":
                        st.write("**일상생활 주의사항**")
                        program_content = st.multiselect("지침 선택", [
                            "올바른 앉기 자세", "무거운 물건 들기", "수면 자세",
                            "컴퓨터 작업 자세", "운전 시 주의사항"
                        ])
                    
                    frequency = st.selectbox("실시 빈도", 
                        ["1일 1회", "1일 2회", "1일 3회", "주 3회", "주 5회"])
                    
                    duration_weeks = st.number_input("프로그램 기간 (주)", 1, 12, 4, key="home_duration")
                    special_notes = st.text_area("특별 지시사항", key="home_notes")
                    
                    submitted = st.form_submit_button("홈 프로그램 생성")
                    
                    if submitted:
                        try:
                            end_date = (date.today() + timedelta(weeks=duration_weeks)).strftime('%Y-%m-%d')
                            
                            home_program_data = {
                                'patient_id': patient_options[selected_patient],
                                'doctor_id': doctor_options[selected_doctor],
                                'program_type': program_type,
                                'program_content': json.dumps(program_content),
                                'frequency': frequency,
                                'duration_weeks': duration_weeks,
                                'special_notes': special_notes,
                                'start_date': date.today().strftime('%Y-%m-%d'),
                                'end_date': end_date,
                                'status': '진행중'
                            }
                            
                            result = supabase.table('home_programs').insert(home_program_data).execute()
                            st.success("✅ 홈 프로그램이 생성되었습니다!")
                            
                            # 프로그램 출력
                            st.subheader("📋 환자용 홈 프로그램")
                            st.write(f"**환자**: {selected_patient.split(' (')[0]}")
                            st.write(f"**프로그램 유형**: {program_type}")
                            st.write(f"**실시 빈도**: {frequency}")
                            st.write(f"**프로그램 기간**: {duration_weeks}주")
                            
                            if program_content:
                                st.write("**프로그램 내용**:")
                                for content in program_content:
                                    st.write(f"- {content}")
                            
                            if special_notes:
                                st.write(f"**특별 지시사항**: {special_notes}")
                            
                        except Exception as e:
                            st.error(f"홈 프로그램 생성 실패: {e}")
                            st.info("💡 pt_additional_tables.sql을 먼저 실행해주세요.")
            else:
                st.warning("환자와 의료진을 먼저 등록해주세요.")
                
        except Exception as e:
            st.error(f"데이터 로딩 실패: {e}")

# 통계 및 리포트
elif menu == "📈 통계 및 리포트":
    st.header("📈 통계 및 리포트")
    
    try:
        # 모든 예약 데이터 가져오기
        all_appointments = supabase.table('appointments').select('*').execute()
        
        if all_appointments.data:
            df_all = pd.DataFrame(all_appointments.data)
            df_all['date'] = pd.to_datetime(df_all['date'])
            
            # 월별 예약 현황
            st.subheader("📊 월별 예약 현황")
            df_all['month'] = df_all['date'].dt.to_period('M')
            monthly_stats = df_all.groupby('month').size().reset_index(name='예약 수')
            monthly_stats['월'] = monthly_stats['month'].astype(str)
            
            fig1 = px.line(monthly_stats, x='월', y='예약 수',
                          title="월별 예약 현황", markers=True)
            st.plotly_chart(fig1, use_container_width=True)
            
            # 치료 유형별 분포
            if 'treatment_type' in df_all.columns:
                st.subheader("🏥 치료 유형별 분포")
                treatment_stats = df_all['treatment_type'].value_counts().reset_index()
                treatment_stats.columns = ['치료유형', '건수']
                
                fig2 = px.pie(treatment_stats, values='건수', names='치료유형',
                             title="치료 유형별 분포")
                st.plotly_chart(fig2, use_container_width=True)
            
            # 예약 상태별 분포
            st.subheader("📋 예약 상태별 현황")
            status_stats = df_all['status'].value_counts().reset_index()
            status_stats.columns = ['상태', '건수']
            
            fig3 = px.bar(status_stats, x='상태', y='건수',
                         title="예약 상태별 현황")
            st.plotly_chart(fig3, use_container_width=True)
            
        else:
            st.info("통계를 생성할 예약 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"통계 데이터 조회 실패: {e}")

else:
    st.info("선택한 메뉴의 기능을 구현 중입니다.")

# 푸터
st.markdown("---")
st.markdown("🏥 **스마트 병원 관리 시스템** | Powered by Supabase & Streamlit")