"""
오프라인 병원 관리 시스템 (CSV 데이터 전용)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import os
import json

# 페이지 설정
st.set_page_config(
    page_title="스마트 병원 관리 시스템 (오프라인)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 스마트 병원 관리 시스템 (오프라인 모드)")
st.info("🔌 이 버전은 CSV 데이터만 사용하는 오프라인 모드입니다.")

# 물리치료 특화 데이터
PT_ASSESSMENTS = {
    "ROM": ["어깨 굴곡", "어깨 신전", "무릎 굴곡", "무릎 신전", "발목 배굴", "발목 저굴"],
    "MMT": ["상지근력", "하지근력", "체간근력", "목근력"]
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

# CSV 데이터 로딩 함수
@st.cache_data
def load_csv_data():
    """CSV 파일들을 로드"""
    try:
        data = {}
        
        if os.path.exists('patients_data.csv'):
            data['patients'] = pd.read_csv('patients_data.csv', encoding='utf-8')
        else:
            data['patients'] = pd.DataFrame()
        
        if os.path.exists('doctors_data.csv'):
            data['doctors'] = pd.read_csv('doctors_data.csv', encoding='utf-8')
        else:
            data['doctors'] = pd.DataFrame()
        
        if os.path.exists('appointments_data.csv'):
            data['appointments'] = pd.read_csv('appointments_data.csv', encoding='utf-8')
        else:
            data['appointments'] = pd.DataFrame()
        
        if os.path.exists('waiting_times_data.csv'):
            data['waiting_times'] = pd.read_csv('waiting_times_data.csv', encoding='utf-8')
        else:
            data['waiting_times'] = pd.DataFrame()
        
        return data
        
    except Exception as e:
        st.error(f"CSV 파일 로딩 실패: {e}")
        return None

# 데이터 로드
csv_data = load_csv_data()

if not csv_data:
    st.error("CSV 데이터를 로드할 수 없습니다.")
    st.info("patients_data.csv, doctors_data.csv, appointments_data.csv 파일이 필요합니다.")
    st.stop()

# 사이드바 메뉴
menu = st.sidebar.selectbox("🔧 기능 선택", [
    "📊 대시보드",
    "👤 환자 관리",
    "👨‍⚕️ 의료진 관리", 
    "📅 예약 관리",
    "🏥 물리치료 특화",
    "📈 통계 및 리포트"
])

# 실시간 업데이트 버튼
if st.sidebar.button("🔄 새로고침"):
    st.cache_data.clear()
    st.rerun()

# 대시보드
if menu == "📊 대시보드":
    st.header("📊 병원 운영 현황 대시보드")
    
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
        st.info("예약 데이터가 없습니다.")

# 환자 관리
elif menu == "👤 환자 관리":
    st.header("👤 환자 관리")
    
    patients_df = csv_data['patients']
    
    if not patients_df.empty:
        st.subheader("등록된 환자 목록")
        
        # 검색 기능
        search_term = st.text_input("환자 검색", placeholder="이름으로 검색...")
        if search_term:
            patients_df = patients_df[patients_df['name'].str.contains(search_term, na=False)]
        
        # 환자 목록 표시
        display_cols = ['id', 'name', 'birth_date', 'gender', 'phone']
        available_cols = [col for col in display_cols if col in patients_df.columns]
        
        if available_cols:
            display_df = patients_df[available_cols]
            column_names = {
                'id': 'ID',
                'name': '이름',
                'birth_date': '생년월일',
                'gender': '성별',
                'phone': '연락처'
            }
            display_df.columns = [column_names.get(col, col) for col in available_cols]
            st.dataframe(display_df, use_container_width=True)
        else:
            st.dataframe(patients_df, use_container_width=True)
    else:
        st.info("등록된 환자가 없습니다.")

# 의료진 관리
elif menu == "👨‍⚕️ 의료진 관리":
    st.header("👨‍⚕️ 의료진 관리")
    
    doctors_df = csv_data['doctors']
    
    if not doctors_df.empty:
        st.subheader("등록된 의료진 목록")
        
        display_cols = ['id', 'name', 'specialty', 'phone', 'email']
        available_cols = [col for col in display_cols if col in doctors_df.columns]
        
        if available_cols:
            display_df = doctors_df[available_cols]
            column_names = {
                'id': 'ID',
                'name': '이름',
                'specialty': '전문분야',
                'phone': '연락처',
                'email': '이메일'
            }
            display_df.columns = [column_names.get(col, col) for col in available_cols]
            st.dataframe(display_df, use_container_width=True)
        else:
            st.dataframe(doctors_df, use_container_width=True)
    else:
        st.info("등록된 의료진이 없습니다.")

# 예약 관리
elif menu == "📅 예약 관리":
    st.header("📅 예약 관리")
    
    appointments_df = csv_data['appointments']
    patients_df = csv_data['patients']
    doctors_df = csv_data['doctors']
    
    if not appointments_df.empty:
        # 날짜 필터
        filter_date = st.date_input("날짜 선택", value=date.today())
        filter_date_str = filter_date.strftime('%Y-%m-%d')
        
        filtered_appointments = appointments_df[appointments_df['date'] == filter_date_str]
        
        if not filtered_appointments.empty:
            st.subheader(f"📋 {filter_date} 예약 현황")
            
            # 환자명과 의사명 매핑
            if not patients_df.empty and not doctors_df.empty:
                patient_names = dict(zip(patients_df['id'], patients_df['name']))
                doctor_names = dict(zip(doctors_df['id'], doctors_df['name']))
                
                display_appointments = filtered_appointments.copy()
                display_appointments['환자명'] = display_appointments['patient_id'].map(patient_names)
                display_appointments['의사명'] = display_appointments['doctor_id'].map(doctor_names)
                
                display_cols = ['환자명', '의사명', 'time', 'status', 'treatment_type']
                available_cols = [col for col in display_cols if col in display_appointments.columns]
                
                if available_cols:
                    final_df = display_appointments[available_cols]
                    column_names = {
                        'time': '시간',
                        'status': '상태',
                        'treatment_type': '치료유형'
                    }
                    final_df.columns = [column_names.get(col, col) for col in available_cols]
                    st.dataframe(final_df, use_container_width=True)
                else:
                    st.dataframe(filtered_appointments, use_container_width=True)
            else:
                st.dataframe(filtered_appointments, use_container_width=True)
        else:
            st.info("선택한 날짜에 예약이 없습니다.")
    else:
        st.info("예약 데이터가 없습니다.")

# 물리치료 특화 기능
elif menu == "🏥 물리치료 특화":
    st.header("🏥 물리치료 특화 시스템 (데모)")
    
    tab1, tab2, tab3 = st.tabs(["🔍 평가", "🏃‍♂️ 운동처방", "⚡ 물리치료"])
    
    with tab1:
        st.subheader("🔍 물리치료 평가 (데모)")
        
        with st.form("pt_assessment_demo"):
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
            
            submitted = st.form_submit_button("평가 저장 (데모)")
            
            if submitted:
                st.success("✅ 물리치료 평가가 입력되었습니다! (데모 모드)")
                st.json({
                    "ROM": rom_data,
                    "MMT": mmt_data,
                    "통증점수": pain_score,
                    "기능점수": functional_score,
                    "소견": assessment_notes
                })
    
    with tab2:
        st.subheader("🏃‍♂️ 운동처방 (데모)")
        
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
        
        if st.button("운동처방 생성 (데모)"):
            st.success("✅ 운동처방이 생성되었습니다! (데모 모드)")
            
            # 처방전 출력
            st.subheader("📋 운동처방전")
            st.write(f"**진단**: {diagnosis}")
            st.write(f"**치료단계**: {phase}")
            st.write("**처방 운동**:")
            for exercise in selected_exercises:
                st.write(f"- {exercise}: {sets}세트 × {reps}회, {frequency}")
    
    with tab3:
        st.subheader("⚡ 물리적 인자 치료 (데모)")
        
        with st.form("physical_agent_demo"):
            col1, col2 = st.columns(2)
            with col1:
                agent_type = st.selectbox("치료 분류", list(PHYSICAL_AGENTS.keys()))
                agent_method = st.selectbox("치료 방법", PHYSICAL_AGENTS[agent_type])
            
            with col2:
                intensity = st.text_input("강도/온도", placeholder="예: 40°C, Medium")
                duration = st.number_input("시간 (분)", 1, 60, 15)
            
            body_part = st.text_input("적용 부위", placeholder="예: 우측 어깨")
            response = st.text_area("환자 반응", placeholder="치료 중 환자의 반응이나 특이사항")
            
            submitted = st.form_submit_button("치료 기록 저장 (데모)")
            
            if submitted:
                st.success("✅ 물리적 인자 치료 기록이 입력되었습니다! (데모 모드)")
                st.json({
                    "치료분류": agent_type,
                    "치료방법": agent_method,
                    "강도": intensity,
                    "시간": f"{duration}분",
                    "적용부위": body_part,
                    "환자반응": response
                })

# 통계 및 리포트
elif menu == "📈 통계 및 리포트":
    st.header("📈 통계 및 리포트")
    
    appointments_df = csv_data['appointments']
    patients_df = csv_data['patients']
    
    if not appointments_df.empty:
        # 월별 예약 현황
        st.subheader("📊 월별 예약 현황")
        
        appointments_df['date'] = pd.to_datetime(appointments_df['date'])
        appointments_df['month'] = appointments_df['date'].dt.to_period('M')
        monthly_stats = appointments_df.groupby('month').size().reset_index(name='예약 수')
        monthly_stats['월'] = monthly_stats['month'].astype(str)
        
        fig1 = px.line(monthly_stats, x='월', y='예약 수',
                      title="월별 예약 현황", markers=True)
        st.plotly_chart(fig1, use_container_width=True)
        
        # 치료 유형별 분포
        if 'treatment_type' in appointments_df.columns:
            st.subheader("🏥 치료 유형별 분포")
            treatment_stats = appointments_df['treatment_type'].value_counts().reset_index()
            treatment_stats.columns = ['치료유형', '건수']
            
            fig2 = px.pie(treatment_stats, values='건수', names='치료유형',
                         title="치료 유형별 분포")
            st.plotly_chart(fig2, use_container_width=True)
        
        # 환자 성별 분포
        if not patients_df.empty and 'gender' in patients_df.columns:
            st.subheader("👥 환자 성별 분포")
            gender_stats = patients_df['gender'].value_counts()
            fig_gender = px.pie(values=gender_stats.values,
                              names=gender_stats.index,
                              title="환자 성별 분포")
            st.plotly_chart(fig_gender, use_container_width=True)
    else:
        st.info("통계를 생성할 데이터가 없습니다.")

# 푸터
st.markdown("---")
st.markdown("🏥 **스마트 병원 관리 시스템** | 오프라인 데모 버전")
st.info("💡 실제 데이터 저장을 위해서는 Supabase 연동 버전을 사용하세요.")