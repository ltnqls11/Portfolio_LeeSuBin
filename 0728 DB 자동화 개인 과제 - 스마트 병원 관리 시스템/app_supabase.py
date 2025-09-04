"""
Supabase 연동 병원 관리 시스템
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase_client import get_supabase_client, format_date_for_db, format_datetime_for_db

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="스마트 병원 관리 시스템 (Supabase)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 스마트 병원 관리 시스템 (Supabase 연동)")

# Supabase 클라이언트 초기화
sb_client = get_supabase_client()

if not sb_client.is_connected():
    st.error("Supabase 연결이 필요합니다. 환경변수를 설정해주세요.")
    st.info("""
    환경변수 설정 방법:
    1. .env 파일 생성
    2. SUPABASE_URL=https://your-project.supabase.co
    3. SUPABASE_KEY=your-anon-key
    """)
    st.stop()

# 사이드바 메뉴
menu = st.sidebar.selectbox("🔧 기능 선택", [
    "📊 대시보드",
    "👤 환자 관리",
    "👨‍⚕️ 의료진 관리", 
    "📅 예약 관리",
    "📋 진료 기록",
    "⏰ 실시간 대기현황",
    "📱 SMS 관리",
    "🗓️ 스케줄 관리",
    "📈 통계 및 리포트"
])

# 실시간 업데이트 버튼
if st.sidebar.button("🔄 새로고침"):
    st.rerun()

# 대시보드
if menu == "📊 대시보드":
    st.header("📊 병원 운영 현황 대시보드")
    
    # 통계 데이터 가져오기
    stats = sb_client.get_dashboard_stats()
    
    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("오늘 예약", stats['today_appointments'])
    with col2:
        st.metric("진료 완료", stats['completed_today'])
    with col3:
        st.metric("대기 중", stats['waiting_today'])
    with col4:
        st.metric("총 환자 수", stats['total_patients'])
    
    # 실시간 대기 현황
    st.subheader("⏰ 실시간 대기 현황")
    waiting_data = sb_client.get_waiting_times()
    
    if waiting_data:
        df_waiting = pd.DataFrame(waiting_data)
        
        # 대기시간에 따른 색상 표시
        def get_wait_color(minutes):
            if minutes <= 10:
                return "🟢"
            elif minutes <= 20:
                return "🟡"
            else:
                return "🔴"
        
        df_waiting['상태'] = df_waiting['estimated_wait_minutes'].apply(
            lambda x: f"{get_wait_color(x)} {x}분"
        )
        
        display_cols = ['patient_name', 'doctor_name', 'scheduled_time', '상태']
        display_df = df_waiting[display_cols]
        display_df.columns = ['환자명', '담당의', '예약시간', '예상대기시간']
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("현재 대기 중인 환자가 없습니다.")
    
    # 오늘 예약 현황 차트
    st.subheader("📈 오늘 예약 현황")
    today_appointments = sb_client.get_appointments(date.today().strftime('%Y-%m-%d'))
    
    if today_appointments:
        df_appointments = pd.DataFrame(today_appointments)
        
        # 시간대별 예약 현황
        df_appointments['hour'] = pd.to_datetime(df_appointments['time']).dt.hour
        hourly_count = df_appointments.groupby('hour').size().reset_index(name='count')
        
        fig = px.bar(hourly_count, x='hour', y='count',
                    title="시간대별 예약 현황",
                    labels={'hour': '시간', 'count': '예약 수'})
        st.plotly_chart(fig, use_container_width=True)

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
                patient_data = {
                    'name': name,
                    'birth_date': format_date_for_db(birth_date),
                    'gender': gender,
                    'phone': phone,
                    'address': address,
                    'medical_history': medical_history,
                    'emergency_contact': emergency_contact,
                    'insurance': insurance,
                    'registration_date': format_date_for_db(date.today())
                }
                
                if sb_client.add_patient(patient_data):
                    # SMS 알림 시뮬레이션
                    sms_data = {
                        'recipient': phone if phone else '연락처 미등록',
                        'message': f'[병원] {name}님, 환자 등록이 완료되었습니다. 예약 문의: 02-1234-5678',
                        'status': '발송완료',
                        'message_type': '환자등록',
                        'timestamp': format_datetime_for_db(datetime.now())
                    }
                    sb_client.add_sms_log(sms_data)
    
    with tab2:
        st.subheader("등록된 환자 목록")
        
        patients = sb_client.get_patients()
        if patients:
            df_patients = pd.DataFrame(patients)
            
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
                
                sb_client.add_doctor(doctor_data)
    
    with tab2:
        st.subheader("등록된 의료진 목록")
        
        doctors = sb_client.get_doctors()
        if doctors:
            df_doctors = pd.DataFrame(doctors)
            
            display_cols = ['id', 'name', 'specialty', 'phone', 'email', 'work_hours', 'experience_years']
            if all(col in df_doctors.columns for col in display_cols):
                display_df = df_doctors[display_cols]
                display_df.columns = ['ID', '이름', '전문분야', '연락처', '이메일', '근무시간', '경력']
                st.dataframe(display_df, use_container_width=True)
            else:
                st.dataframe(df_doctors, use_container_width=True)
        else:
            st.info("등록된 의료진이 없습니다.")

# 예약 관리
elif menu == "📅 예약 관리":
    st.header("📅 예약 관리")
    
    tab1, tab2 = st.tabs(["📅 새 예약", "📋 예약 현황"])
    
    with tab1:
        st.subheader("새 예약 등록")
        
        # 환자와 의료진 데이터 가져오기
        patients = sb_client.get_patients()
        doctors = sb_client.get_doctors()
        
        if not patients or not doctors:
            st.warning("환자와 의료진을 먼저 등록해주세요.")
        else:
            with st.form("appointment_form"):
                col1, col2 = st.columns(2)
                with col1:
                    patient_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in patients}
                    selected_patient = st.selectbox("환자 선택*", list(patient_options.keys()))
                    
                    doctor_options = {f"{d['name']} - {d['specialty']} (ID: {d['id']})": d['id'] for d in doctors}
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
                    appointment_data = {
                        'patient_id': patient_options[selected_patient],
                        'doctor_id': doctor_options[selected_doctor],
                        'date': format_date_for_db(appt_date),
                        'time': appt_time.strftime('%H:%M:%S'),
                        'status': '예약완료',
                        'treatment_type': treatment_type,
                        'notes': notes
                    }
                    
                    if sb_client.add_appointment(appointment_data):
                        # 예약 확인 SMS 발송
                        patient_name = selected_patient.split(' (')[0]
                        sms_data = {
                            'recipient': '010-****-****',
                            'message': f'[병원] {patient_name}님, {appt_date} {appt_time} 예약이 확정되었습니다.',
                            'status': '발송완료',
                            'message_type': '예약확인',
                            'timestamp': format_datetime_for_db(datetime.now())
                        }
                        sb_client.add_sms_log(sms_data)
    
    with tab2:
        st.subheader("예약 현황")
        
        # 날짜 필터
        filter_date = st.date_input("날짜 선택", value=date.today())
        
        appointments = sb_client.get_appointments(format_date_for_db(filter_date))
        
        if appointments:
            # 예약 목록 표시
            appointment_data = []
            for apt in appointments:
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
                appt_id = st.selectbox("예약 선택", [apt['id'] for apt in appointments])
            with col2:
                new_status = st.selectbox("새 상태", ["예약완료", "진료중", "진료완료", "취소", "노쇼"])
            with col3:
                if st.button("상태 변경"):
                    sb_client.update_appointment_status(appt_id, new_status)
                    st.rerun()
        else:
            st.info("선택한 날짜에 예약이 없습니다.")

# 진료 기록
elif menu == "📋 진료 기록":
    st.header("📋 진료 기록 관리")
    
    tab1, tab2 = st.tabs(["📝 기록 작성", "🔍 기록 조회"])
    
    with tab1:
        st.subheader("진료 기록 작성")
        
        # 진료 완료된 예약 조회
        today_appointments = sb_client.get_appointments(date.today().strftime('%Y-%m-%d'))
        completed_appointments = [apt for apt in today_appointments if apt['status'] == '진료완료']
        
        if completed_appointments:
            with st.form("medical_record_form"):
                appt_options = {
                    f"{apt['patients']['name']} - {apt['time']} ({apt['doctors']['name']})": apt['id']
                    for apt in completed_appointments if apt.get('patients') and apt.get('doctors')
                }
                
                if appt_options:
                    selected_appt = st.selectbox("진료 선택", list(appt_options.keys()))
                    
                    chief_complaint = st.text_area("주 증상 (Chief Complaint)")
                    diagnosis = st.text_area("진단 (Diagnosis)")
                    treatment = st.text_area("치료 내용 (Treatment)")
                    prescription = st.text_area("처방 (Prescription)")
                    next_visit = st.date_input("다음 방문일")
                    
                    submitted = st.form_submit_button("기록 저장")
                    
                    if submitted:
                        # 선택된 예약 정보 찾기
                        selected_appt_id = appt_options[selected_appt]
                        selected_appt_data = next(apt for apt in completed_appointments if apt['id'] == selected_appt_id)
                        
                        record_data = {
                            'appointment_id': selected_appt_id,
                            'patient_id': selected_appt_data['patient_id'],
                            'doctor_id': selected_appt_data['doctor_id'],
                            'chief_complaint': chief_complaint,
                            'diagnosis': diagnosis,
                            'treatment': treatment,
                            'prescription': prescription,
                            'next_visit': format_date_for_db(next_visit)
                        }
                        
                        sb_client.add_medical_record(record_data)
                else:
                    st.info("진료 완료된 예약이 없습니다.")
        else:
            st.info("오늘 진료 완료된 예약이 없습니다.")
    
    with tab2:
        st.subheader("진료 기록 조회")
        
        records = sb_client.get_medical_records()
        if records:
            record_data = []
            for record in records:
                record_data.append({
                    'ID': record['id'],
                    '환자': record['patients']['name'] if record.get('patients') else 'N/A',
                    '의료진': record['doctors']['name'] if record.get('doctors') else 'N/A',
                    '주증상': record.get('chief_complaint', 'N/A'),
                    '진단': record.get('diagnosis', 'N/A'),
                    '치료': record.get('treatment', 'N/A'),
                    '작성일': record.get('created_at', 'N/A')
                })
            
            df_records = pd.DataFrame(record_data)
            st.dataframe(df_records, use_container_width=True)
        else:
            st.info("등록된 진료 기록이 없습니다.")

# SMS 관리
elif menu == "📱 SMS 관리":
    st.header("📱 SMS 관리")
    
    tab1, tab2 = st.tabs(["📤 발송 내역", "📝 수동 발송"])
    
    with tab1:
        st.subheader("SMS 발송 내역")
        
        # 날짜 필터
        filter_date = st.date_input("날짜 선택", value=date.today())
        
        sms_logs = sb_client.get_sms_logs(format_date_for_db(filter_date))
        
        if sms_logs:
            df_sms = pd.DataFrame(sms_logs)
            
            display_cols = ['timestamp', 'recipient', 'message', 'status', 'message_type']
            if all(col in df_sms.columns for col in display_cols):
                display_df = df_sms[display_cols]
                display_df.columns = ['발송시간', '수신자', '메시지', '상태', '유형']
                st.dataframe(display_df, use_container_width=True)
            else:
                st.dataframe(df_sms, use_container_width=True)
        else:
            st.info("선택한 날짜에 발송된 SMS가 없습니다.")
    
    with tab2:
        st.subheader("수동 SMS 발송")
        
        with st.form("manual_sms_form"):
            recipient = st.text_input("수신자 번호", placeholder="010-1234-5678")
            message = st.text_area("메시지 내용", placeholder="발송할 메시지를 입력하세요")
            
            submitted = st.form_submit_button("SMS 발송")
            
            if submitted and recipient and message:
                sms_data = {
                    'recipient': recipient,
                    'message': message,
                    'status': '발송완료',
                    'message_type': '수동발송',
                    'timestamp': format_datetime_for_db(datetime.now())
                }
                
                if sb_client.add_sms_log(sms_data):
                    st.success("SMS가 발송되었습니다!")

# 통계 및 리포트
elif menu == "📈 통계 및 리포트":
    st.header("📈 통계 및 리포트")
    
    # 월별 예약 현황
    st.subheader("📊 월별 예약 현황")
    
    # 모든 예약 데이터 가져오기
    all_appointments = sb_client.get_appointments()
    
    if all_appointments:
        df_all = pd.DataFrame(all_appointments)
        df_all['date'] = pd.to_datetime(df_all['date'])
        df_all['month'] = df_all['date'].dt.to_period('M')
        
        monthly_stats = df_all.groupby('month').size().reset_index(name='예약 수')
        monthly_stats['월'] = monthly_stats['month'].astype(str)
        
        fig1 = px.line(monthly_stats, x='월', y='예약 수',
                      title="월별 예약 현황", markers=True)
        st.plotly_chart(fig1, use_container_width=True)
        
        # 치료 유형별 분포
        if 'treatment_type' in df_all.columns:
            treatment_stats = df_all['treatment_type'].value_counts().reset_index()
            treatment_stats.columns = ['치료유형', '건수']
            
            fig2 = px.pie(treatment_stats, values='건수', names='치료유형',
                         title="치료 유형별 분포")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("통계를 생성할 예약 데이터가 없습니다.")

else:
    st.info("선택한 메뉴의 기능을 구현 중입니다.")