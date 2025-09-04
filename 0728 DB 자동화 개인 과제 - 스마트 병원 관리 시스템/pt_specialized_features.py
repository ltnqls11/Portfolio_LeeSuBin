"""
물리치료 특화 기능 추가 모듈
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

# 물리치료 특화 데이터 구조
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

def create_pt_assessment_form():
    """물리치료 평가 폼"""
    st.subheader("🔍 물리치료 평가")
    
    with st.form("pt_assessment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**관절가동범위 (ROM)**")
            rom_data = {}
            for joint in PT_ASSESSMENTS["ROM"]:
                rom_data[joint] = st.number_input(f"{joint} (도)", 0, 180, 0)
        
        with col2:
            st.write("**근력검사 (MMT)**")
            mmt_data = {}
            for muscle in PT_ASSESSMENTS["MMT"]:
                mmt_data[muscle] = st.selectbox(f"{muscle}", 
                    ["0 (Zero)", "1 (Trace)", "2 (Poor)", "3 (Fair)", "4 (Good)", "5 (Normal)"])
        
        pain_score = st.slider("통증 점수 (VAS)", 0, 10, 0)
        functional_score = st.number_input("기능점수", 0, 100, 0)
        
        assessment_notes = st.text_area("평가 소견")
        
        submitted = st.form_submit_button("평가 저장")
        
        if submitted:
            assessment_data = {
                "rom": rom_data,
                "mmt": mmt_data,
                "pain": pain_score,
                "function": functional_score,
                "notes": assessment_notes,
                "date": datetime.now()
            }
            st.success("평가가 저장되었습니다!")
            return assessment_data
    
    return None

def create_exercise_prescription():
    """운동처방 시스템"""
    st.subheader("🏃‍♂️ 운동처방")
    
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
    
    if st.button("운동처방 저장"):
        prescription = {
            "diagnosis": diagnosis,
            "phase": phase,
            "exercises": selected_exercises,
            "sets": sets,
            "reps": reps,
            "frequency": frequency,
            "date": datetime.now()
        }
        st.success("운동처방이 저장되었습니다!")
        
        # 처방전 출력
        st.subheader("📋 운동처방전")
        st.write(f"**진단**: {diagnosis}")
        st.write(f"**치료단계**: {phase}")
        st.write("**처방 운동**:")
        for exercise in selected_exercises:
            st.write(f"- {exercise}: {sets}세트 × {reps}회, {frequency}")

def create_physical_agent_record():
    """물리적 인자 치료 기록"""
    st.subheader("⚡ 물리적 인자 치료")
    
    with st.form("physical_agent_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            agent_type = st.selectbox("치료 분류", list(PHYSICAL_AGENTS.keys()))
            agent = st.selectbox("치료 방법", PHYSICAL_AGENTS[agent_type])
        
        with col2:
            intensity = st.text_input("강도/온도")
            duration = st.number_input("시간 (분)", 1, 60, 15)
        
        body_part = st.text_input("적용 부위")
        response = st.text_area("환자 반응")
        
        submitted = st.form_submit_button("치료 기록 저장")
        
        if submitted:
            treatment_record = {
                "type": agent_type,
                "agent": agent,
                "intensity": intensity,
                "duration": duration,
                "body_part": body_part,
                "response": response,
                "date": datetime.now()
            }
            st.success("치료 기록이 저장되었습니다!")

def create_progress_tracking():
    """치료 진행도 추적"""
    st.subheader("📈 치료 진행도 추적")
    
    # 샘플 데이터 (실제로는 DB에서 가져옴)
    progress_data = pd.DataFrame({
        "날짜": pd.date_range("2024-07-01", periods=10, freq="3D"),
        "통증점수": [8, 7, 6, 5, 4, 4, 3, 3, 2, 2],
        "ROM_어깨굴곡": [90, 95, 100, 110, 120, 125, 130, 135, 140, 145],
        "기능점수": [30, 35, 40, 45, 50, 55, 60, 65, 70, 75]
    })
    
    # 진행도 차트
    import plotly.express as px
    
    fig_pain = px.line(progress_data, x="날짜", y="통증점수", 
                      title="통증 점수 변화", markers=True)
    fig_pain.update_layout(yaxis_title="VAS 점수", xaxis_title="날짜")
    st.plotly_chart(fig_pain, use_container_width=True)
    
    fig_rom = px.line(progress_data, x="날짜", y="ROM_어깨굴곡", 
                     title="관절가동범위 개선", markers=True)
    fig_rom.update_layout(yaxis_title="각도 (도)", xaxis_title="날짜")
    st.plotly_chart(fig_rom, use_container_width=True)
    
    fig_function = px.line(progress_data, x="날짜", y="기능점수", 
                          title="기능 점수 향상", markers=True)
    fig_function.update_layout(yaxis_title="기능 점수", xaxis_title="날짜")
    st.plotly_chart(fig_function, use_container_width=True)

def create_home_program():
    """홈 프로그램 관리"""
    st.subheader("🏠 홈 프로그램")
    
    st.write("**환자 맞춤 홈케어 프로그램**")
    
    with st.form("home_program_form"):
        program_type = st.selectbox("프로그램 유형", 
            ["자가 운동", "일상생활 지침", "자세 교정", "통증 관리"])
        
        if program_type == "자가 운동":
            st.write("**자가 운동 프로그램**")
            exercises = st.multiselect("운동 선택", [
                "목 스트레칭", "어깨 돌리기", "벽 팔굽혀펴기", 
                "스쿼트", "종아리 스트레칭", "허리 신전 운동"
            ])
            
        elif program_type == "일상생활 지침":
            st.write("**일상생활 주의사항**")
            guidelines = st.multiselect("지침 선택", [
                "올바른 앉기 자세", "무거운 물건 들기", "수면 자세",
                "컴퓨터 작업 자세", "운전 시 주의사항"
            ])
        
        frequency = st.selectbox("실시 빈도", 
            ["1일 1회", "1일 2회", "1일 3회", "주 3회", "주 5회"])
        
        duration_weeks = st.number_input("프로그램 기간 (주)", 1, 12, 4)
        
        special_notes = st.text_area("특별 지시사항")
        
        submitted = st.form_submit_button("홈 프로그램 생성")
        
        if submitted:
            st.success("홈 프로그램이 생성되었습니다!")
            
            # 프로그램 출력
            st.subheader("📋 환자용 홈 프로그램")
            st.write(f"**프로그램 유형**: {program_type}")
            st.write(f"**실시 빈도**: {frequency}")
            st.write(f"**프로그램 기간**: {duration_weeks}주")
            
            if program_type == "자가 운동" and 'exercises' in locals():
                st.write("**운동 내용**:")
                for exercise in exercises:
                    st.write(f"- {exercise}")
            
            if special_notes:
                st.write(f"**특별 지시사항**: {special_notes}")

# 메인 물리치료 특화 페이지
def main_pt_features():
    """물리치료 특화 기능 메인 페이지"""
    st.title("🏥 물리치료 특화 시스템")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 평가", "🏃‍♂️ 운동처방", "⚡ 물리치료", "📈 진행도", "🏠 홈프로그램"
    ])
    
    with tab1:
        create_pt_assessment_form()
    
    with tab2:
        create_exercise_prescription()
    
    with tab3:
        create_physical_agent_record()
    
    with tab4:
        create_progress_tracking()
    
    with tab5:
        create_home_program()

if __name__ == "__main__":
    main_pt_features()