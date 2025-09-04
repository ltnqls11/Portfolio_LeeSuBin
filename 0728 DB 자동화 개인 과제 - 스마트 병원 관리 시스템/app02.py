import streamlit as st
from datetime import datetime, time, timedelta, date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import json
import time as time_module
import random

# 데이터베이스 import를 try-except로 처리
try:
    from database import SessionLocal, Patient, Doctor, Appointment
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    st.warning("데이터베이스 연결을 사용할 수 없습니다. CSV 데이터만 사용합니다.")

try:
    st.set_page_config(page_title="스마트 병원 종합 관리 시스템", layout="wide")
    st.title("🏥 스마트 병원 종합 관리 시스템 (물리치료 특화)")
except Exception as e:
    st.error(f"페이지 설정 중 오류: {e}")
    st.title("🏥 스마트 병원 종합 관리 시스템")

# CSV 데이터 로딩 함수
@st.cache_data
def load_csv_data():
    """CSV 파일들을 로드하여 시뮬레이션 데이터로 사용"""
    try:
        # 여러 인코딩 방식을 시도
        encodings = ['utf-8', 'cp949', 'euc-kr', 'latin-1']
        
        def safe_read_csv(filename):
            for encoding in encodings:
                try:
                    return pd.read_csv(filename, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            # 모든 인코딩이 실패하면 기본값으로 시도
            return pd.read_csv(filename)
        
        patients_df = safe_read_csv('patients_data.csv')
        doctors_df = safe_read_csv('doctors_data.csv')
        appointments_df = safe_read_csv('appointments_data.csv')
        medical_records_df = safe_read_csv('medical_records_data.csv')
        sms_log_df = safe_read_csv('sms_log_data.csv')
        waiting_times_df = safe_read_csv('waiting_times_data.csv')
        schedules_df = safe_read_csv('doctor_schedules_data.csv')
        
        return {
            'patients': patients_df,
            'doctors': doctors_df,
            'appointments': appointments_df,
            'medical_records': medical_records_df,
            'sms_log': sms_log_df,
            'waiting_times': waiting_times_df,
            'schedules': schedules_df
        }
    except Exception as e:
        st.error(f"CSV 파일 로딩 중 오류가 발생했습니다: {e}")
        return None

# 데이터 로드
csv_data = load_csv_data()

# 세션 상태 초기화
if 'waiting_times' not in st.session_state:
    st.session_state.waiting_times = {}
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'sms_log' not in st.session_state:
    if csv_data and 'sms_log' in csv_data:
        st.session_state.sms_log = csv_data['sms_log'].to_dict('records')
    else:
        st.session_state.sms_log = []

# 데이터베이스 세션 초기화
if DB_AVAILABLE:
    session = SessionLocal()
else:
    session = None

# 사이드바 메뉴
menu = st.sidebar.selectbox("🔧 기능 선택", [
    "📊 대시보드", 
    "👤 환자 등록", 
    "👨‍⚕️ 의료진 등록", 
    "📅 예약 관리", 
    "📋 진료 기록", 
    "⏰ 실시간 대기현황", 
    "📱 SMS 알림 관리",
    "🗓️ 의료진 스케줄",
    "📈 통계 및 리포트"
])

# 실시간 업데이트를 위한 자동 새로고침
if st.sidebar.button("🔄 실시간 업데이트"):
    st.rerun()

# 대시보드
if menu == "📊 대시보드":
    st.header("📊 병원 운영 현황 대시보드")
    
    if csv_data:
        # CSV 데이터 활용
        appointments_df = csv_data['appointments']
        patients_df = csv_data['patients']
        waiting_df = csv_data['waiting_times']
        
        # 오늘 날짜로 필터링
        today_str = date.today().strftime('%Y-%m-%d')
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
        if len(waiting_df) > 0:
            # 대기 시간에 따른 색상 코딩
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
        
        # 일일 예약 현황 차트
        st.subheader("📈 일일 예약 현황")
        if len(today_appointments) > 0:
            hourly_appointments = today_appointments.copy()
            hourly_appointments['hour'] = pd.to_datetime(hourly_appointments['time']).dt.hour
            hourly_count = hourly_appointments.groupby('hour').size().reset_index(name='count')
            
            fig = px.bar(hourly_count, x='hour', y='count', 
                        title="시간대별 예약 현황",
                        labels={'hour': '시간', 'count': '예약 수'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("CSV 데이터를 로드할 수 없습니다.")

# 실시간 대기현황
elif menu == "⏰ 실시간 대기현황":
    st.header("⏰ 실시간 대기현황")
    
    if csv_data:
        waiting_df = csv_data['waiting_times']
        appointments_df = csv_data['appointments']
        
        # 현재 시간 표시
        current_time = datetime.now()
        st.info(f"🕐 현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if len(waiting_df) > 0:
            st.subheader("📋 현재 대기 환자 목록")
            
            # 대기시간별 정렬
            waiting_sorted = waiting_df.sort_values('estimated_wait_minutes')
            
            for idx, row in waiting_sorted.iterrows():
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1, 1])
                    
                    with col1:
                        st.write(f"👤 **{row['patient_name']}**")
                    with col2:
                        st.write(f"👨‍⚕️ {row['doctor_name']}")
                    with col3:
                        st.write(f"🕐 {row['scheduled_time']}")
                    with col4:
                        # 대기시간에 따른 색상 표시
                        wait_minutes = row['estimated_wait_minutes']
                        if wait_minutes <= 10:
                            st.success(f"{wait_minutes}분")
                        elif wait_minutes <= 20:
                            st.warning(f"{wait_minutes}분")
                        else:
                            st.error(f"{wait_minutes}분")
                    with col5:
                        # 상태 업데이트 버튼
                        if st.button("완료", key=f"complete_{idx}"):
                            st.success("진료 완료 처리됨")
                    
                    st.divider()
            
            # 대기 현황 요약
            st.subheader("📊 대기 현황 요약")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 대기 환자", len(waiting_df))
            with col2:
                avg_wait = waiting_df['estimated_wait_minutes'].mean()
                st.metric("평균 대기시간", f"{avg_wait:.1f}분")
            with col3:
                max_wait = waiting_df['estimated_wait_minutes'].max()
                st.metric("최대 대기시간", f"{max_wait}분")
            with col4:
                urgent_count = len(waiting_df[waiting_df['estimated_wait_minutes'] > 20])
                st.metric("긴급 대기", urgent_count, delta_color="inverse")
            
            # 대기시간 분포 차트
            st.subheader("📈 대기시간 분포")
            fig = px.histogram(waiting_df, x='estimated_wait_minutes', 
                             title="대기시간 분포", 
                             labels={'estimated_wait_minutes': '대기시간(분)', 'count': '환자 수'},
                             nbins=10)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("🎉 현재 대기 중인 환자가 없습니다!")
        
        # 실시간 알림 시뮬레이션
        st.subheader("🔔 실시간 알림")
        
        # 알림 생성 (시뮬레이션)
        if st.button("🔄 알림 새로고침"):
            sample_notifications = [
                "📱 김민수님께 예약 알림 SMS 발송 완료",
                "⚠️ 물리치료실 A 대기시간이 30분을 초과했습니다",
                "✅ 이영희님 진료가 완료되었습니다",
                "📞 박철수님이 예약 변경을 요청했습니다",
                "🏥 오늘 예약률이 95%에 도달했습니다"
            ]
            
            # 랜덤하게 1-3개의 알림 선택
            selected_notifications = random.sample(sample_notifications, random.randint(1, 3))
            
            for notification in selected_notifications:
                st.info(f"🕐 {current_time.strftime('%H:%M')} - {notification}")
        
        # 자동 새로고침 옵션
        auto_refresh = st.checkbox("⚡ 자동 새로고침 (30초)", value=False)
        if auto_refresh:
            time_module.sleep(30)
            st.rerun()
    
    else:
        st.error("대기현황 데이터를 로드할 수 없습니다.")

# SMS 알림 관리
elif menu == "📱 SMS 알림 관리":
    st.header("📱 SMS 알림 관리 시스템")
    
    tab1, tab2, tab3 = st.tabs(["📤 발송 내역", "⚙️ 자동 알림 설정", "📝 수동 발송"])
    
    with tab1:
        st.subheader("SMS 발송 내역")
        if csv_data and 'sms_log' in csv_data:
            sms_df = csv_data['sms_log'].copy()
            
            # 날짜 필터
            col1, col2 = st.columns(2)
            with col1:
                filter_date = st.date_input("날짜 선택", value=date.today())
            with col2:
                message_types = sms_df['message_type'].unique()
                selected_type = st.selectbox("메시지 유형", ['전체'] + list(message_types))
            
            # 필터링
            filtered_sms = sms_df.copy()
            if selected_type != '전체':
                filtered_sms = filtered_sms[filtered_sms['message_type'] == selected_type]
            
            # 표시할 컬럼 선택
            display_cols = ['timestamp', 'recipient', 'message', 'status', 'message_type']
            filtered_sms = filtered_sms[display_cols]
            filtered_sms.columns = ['발송시간', '수신자', '메시지 내용', '상태', '유형']
            
            st.dataframe(filtered_sms, use_container_width=True)
            
            # 통계
            st.subheader("📊 SMS 발송 통계")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 발송 건수", len(sms_df))
            with col2:
                success_count = len(sms_df[sms_df['status'] == '발송완료'])
                st.metric("발송 성공", success_count)
            with col3:
                success_rate = (success_count / len(sms_df) * 100) if len(sms_df) > 0 else 0
                st.metric("성공률", f"{success_rate:.1f}%")
        else:
            st.info("발송된 SMS가 없습니다.")
    
    with tab2:
        st.subheader("자동 알림 설정")
        
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("예약 확인 SMS", value=True, help="예약 등록 시 자동 발송")
            st.checkbox("예약 전날 알림", value=True, help="예약 전날 19시 발송")
            st.checkbox("예약 당일 알림", value=True, help="예약 2시간 전 발송")
        with col2:
            st.checkbox("정기 검진 알림", value=False, help="정기 검진 1주일 전 알림")
            st.checkbox("치료 완료 알림", value=True, help="치료 완료 시 발송")
            st.checkbox("예약 변경 알림", value=True, help="예약 변경 시 발송")
    
    with tab3:
        st.subheader("수동 SMS 발송")
        with st.form("manual_sms_form"):
            recipient = st.text_input("수신자 번호", placeholder="010-1234-5678")
            message = st.text_area("메시지 내용", placeholder="발송할 메시지를 입력하세요")
            
            submitted = st.form_submit_button("SMS 발송")
            
            if submitted and recipient and message:
                st.session_state.sms_log.append({
                    "시간": datetime.now().strftime("%H:%M:%S"),
                    "수신자": recipient,
                    "내용": message,
                    "상태": "발송완료"
                })
                st.success("SMS가 발송되었습니다!")

# 통계 및 리포트
elif menu == "📈 통계 및 리포트":
    st.header("📈 통계 및 리포트")
    
    if csv_data:
        appointments_df = csv_data['appointments']
        patients_df = csv_data['patients']
        
        # 월별 예약 현황
        appointments_df['date'] = pd.to_datetime(appointments_df['date'])
        appointments_df['month'] = appointments_df['date'].dt.to_period('M')
        monthly_stats = appointments_df.groupby('month').size().reset_index(name='예약 수')
        monthly_stats['월'] = monthly_stats['month'].astype(str)
        
        fig1 = px.line(monthly_stats, x='월', y='예약 수', 
                      title="📈 월별 예약 현황", markers=True)
        fig1.update_layout(xaxis_title="월", yaxis_title="예약 수")
        st.plotly_chart(fig1, use_container_width=True)
        
        # 환자 성별 분포
        gender_stats = patients_df['gender'].value_counts()
        fig_gender = px.pie(values=gender_stats.values, 
                          names=gender_stats.index, 
                          title="👥 환자 성별 분포")
        st.plotly_chart(fig_gender, use_container_width=True)
        
        # 치료 유형별 통계
        if 'treatment_type' in appointments_df.columns:
            treatment_stats = appointments_df['treatment_type'].value_counts().reset_index()
            treatment_stats.columns = ['치료유형', '건수']
            
            fig3 = px.pie(treatment_stats, values='건수', names='치료유형',
                         title="🏥 치료 유형별 분포")
            st.plotly_chart(fig3, use_container_width=True)
        
        # 주요 통계 지표
        st.subheader("📊 주요 지표")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_appointments = len(appointments_df)
            st.metric("총 예약 건수", total_appointments)
        with col2:
            completed_rate = len(appointments_df[appointments_df['status'] == '진료완료']) / total_appointments * 100 if total_appointments > 0 else 0
            st.metric("진료 완료율", f"{completed_rate:.1f}%")
        with col3:
            total_patients = len(patients_df)
            st.metric("총 환자 수", total_patients)
        with col4:
            avg_daily_appointments = total_appointments / 30  # 월평균 기준
            st.metric("일평균 예약", f"{avg_daily_appointments:.1f}건")
            
    else:
        st.error("통계 데이터를 로드할 수 없습니다.")

# 환자 등록
elif menu == "👤 환자 등록":
    st.header("👤 환자 등록")
    
    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("환자 이름")
            birth_date = st.date_input("생년월일")
            gender = st.selectbox("성별", ["남", "여"])
        with col2:
            phone = st.text_input("연락처", placeholder="010-1234-5678")
            address = st.text_area("주소")
            medical_history = st.text_area("병력", placeholder="기존 질환이나 수술 이력")
        
        emergency_contact = st.text_input("응급연락처", placeholder="보호자 연락처")
        insurance = st.selectbox("보험 유형", ["건강보험", "의료급여", "산재보험", "자동차보험", "기타"])
        
        submitted = st.form_submit_button("환자 등록")

        if submitted and name:
            if DB_AVAILABLE and session:
                try:
                    patient = Patient(
                        name=name, 
                        birth_date=birth_date, 
                        gender=gender
                    )
                    session.add(patient)
                    session.commit()
                    st.success(f"✅ {name} 환자 등록이 완료되었습니다!")
                    
                    # SMS 알림 시뮬레이션
                    sms_msg = f"[병원] {name}님, 환자 등록이 완료되었습니다. 예약 문의: 02-1234-5678"
                    st.session_state.sms_log.append({
                        "시간": datetime.now().strftime("%H:%M:%S"),
                        "수신자": phone if phone else "연락처 미등록",
                        "내용": sms_msg,
                        "상태": "발송완료"
                    })
                except Exception as e:
                    st.error(f"환자 등록 중 오류가 발생했습니다: {e}")
            else:
                st.success(f"✅ {name} 환자 정보가 입력되었습니다! (데모 모드)")
                st.info("실제 데이터베이스 연결이 필요합니다.")

# 의료진 등록
elif menu == "👨‍⚕️ 의료진 등록":
    st.header("👨‍⚕️ 의료진 등록")
    
    with st.form("doctor_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("의료진 이름")
            specialty = st.selectbox("전문 분야", [
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
        
        submitted = st.form_submit_button("의료진 등록")

        if submitted and name:
            if DB_AVAILABLE and session:
                try:
                    doctor = Doctor(name=name, specialty=specialty)
                    session.add(doctor)
                    session.commit()
                    st.success(f"✅ {name} 의료진 등록이 완료되었습니다!")
                except Exception as e:
                    st.error(f"의료진 등록 중 오류가 발생했습니다: {e}")
            else:
                st.success(f"✅ {name} 의료진 정보가 입력되었습니다! (데모 모드)")
                st.info("실제 데이터베이스 연결이 필요합니다.")

# 예약 관리
elif menu == "📅 예약 관리":
    st.header("📅 예약 관리 시스템")
    
    if csv_data:
        appointments_df = csv_data['appointments']
        patients_df = csv_data['patients']
        doctors_df = csv_data['doctors']
        
        # 오늘 예약 현황
        today_str = date.today().strftime('%Y-%m-%d')
        today_appointments = appointments_df[appointments_df['date'] == today_str]
        
        st.subheader("📋 오늘의 예약 현황")
        if len(today_appointments) > 0:
            # 환자명과 의사명 매핑
            patient_names = dict(zip(patients_df['id'], patients_df['name']))
            doctor_names = dict(zip(doctors_df['id'], doctors_df['name']))
            
            display_appointments = today_appointments.copy()
            display_appointments['환자명'] = display_appointments['patient_id'].map(patient_names)
            display_appointments['의사명'] = display_appointments['doctor_id'].map(doctor_names)
            
            display_cols = ['환자명', '의사명', 'time', 'status', 'treatment_type']
            final_df = display_appointments[display_cols]
            final_df.columns = ['환자명', '담당의', '시간', '상태', '치료유형']
            
            st.dataframe(final_df, use_container_width=True)
        else:
            st.info("오늘 예약된 환자가 없습니다.")
        
        # 예약 통계
        st.subheader("📊 예약 통계")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_today = len(today_appointments)
            st.metric("오늘 총 예약", total_today)
        with col2:
            completed_today = len(today_appointments[today_appointments['status'] == '진료완료'])
            st.metric("완료된 진료", completed_today)
        with col3:
            waiting_today = len(today_appointments[today_appointments['status'] == '예약완료'])
            st.metric("대기 중", waiting_today)
    else:
        st.error("예약 데이터를 로드할 수 없습니다.")

# 진료 기록
elif menu == "📋 진료 기록":
    st.header("📋 진료 기록 관리")
    
    if csv_data and 'medical_records' in csv_data:
        medical_records_df = csv_data['medical_records']
        patients_df = csv_data['patients']
        doctors_df = csv_data['doctors']
        
        st.subheader("📝 진료 기록 목록")
        
        if len(medical_records_df) > 0:
            # 환자명과 의사명 매핑
            patient_names = dict(zip(patients_df['id'], patients_df['name']))
            doctor_names = dict(zip(doctors_df['id'], doctors_df['name']))
            
            display_records = medical_records_df.copy()
            display_records['환자명'] = display_records['patient_id'].map(patient_names)
            display_records['의사명'] = display_records['doctor_id'].map(doctor_names)
            
            display_cols = ['환자명', '의사명', 'chief_complaint', 'diagnosis', 'treatment', 'created_at']
            final_df = display_records[display_cols]
            final_df.columns = ['환자명', '담당의', '주증상', '진단', '치료내용', '작성일시']
            
            st.dataframe(final_df, use_container_width=True)
        else:
            st.info("등록된 진료 기록이 없습니다.")
    else:
        st.info("진료 기록 데이터를 로드할 수 없습니다.")

# 의료진 스케줄
elif menu == "🗓️ 의료진 스케줄":
    st.header("🗓️ 의료진 스케줄 관리")
    
    if csv_data and 'schedules' in csv_data:
        schedules_df = csv_data['schedules']
        
        st.subheader("📅 의료진 스케줄 현황")
        
        if len(schedules_df) > 0:
            # 오늘 날짜 기준으로 필터링
            today_str = date.today().strftime('%Y-%m-%d')
            today_schedules = schedules_df[schedules_df['date'] == today_str]
            
            if len(today_schedules) > 0:
                display_cols = ['doctor_name', 'start_time', 'end_time', 'current_patients', 'max_patients', 'status']
                final_df = today_schedules[display_cols]
                final_df.columns = ['의료진', '시작시간', '종료시간', '현재환자', '최대환자', '상태']
                
                st.dataframe(final_df, use_container_width=True)
            else:
                st.info("오늘 스케줄이 없습니다.")
        else:
            st.info("스케줄 데이터가 없습니다.")
    else:
        st.info("스케줄 데이터를 로드할 수 없습니다.")

else:
    st.info("해당 메뉴는 간소화된 버전에서 제외되었습니다. 전체 기능을 사용하려면 원본 파일을 수정해주세요.")