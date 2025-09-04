"""
CSV 데이터만 사용하는 병원 관리 시스템
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import os

# 페이지 설정
st.set_page_config(
    page_title="스마트 병원 관리 시스템 (CSV)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 스마트 병원 관리 시스템 (CSV 데이터)")

# CSV 데이터 로딩 함수
@st.cache_data
def load_csv_data():
    """CSV 파일들을 로드"""
    try:
        data = {}
        
        # 환자 데이터
        if os.path.exists('patients_data.csv'):
            data['patients'] = pd.read_csv('patients_data.csv', encoding='utf-8')
        else:
            data['patients'] = pd.DataFrame()
        
        # 의료진 데이터
        if os.path.exists('doctors_data.csv'):
            data['doctors'] = pd.read_csv('doctors_data.csv', encoding='utf-8')
        else:
            data['doctors'] = pd.DataFrame()
        
        # 예약 데이터
        if os.path.exists('appointments_data.csv'):
            data['appointments'] = pd.read_csv('appointments_data.csv', encoding='utf-8')
        else:
            data['appointments'] = pd.DataFrame()
        
        # 진료 기록 데이터
        if os.path.exists('medical_records_data.csv'):
            data['medical_records'] = pd.read_csv('medical_records_data.csv', encoding='utf-8')
        else:
            data['medical_records'] = pd.DataFrame()
        
        # SMS 로그 데이터
        if os.path.exists('sms_log_data.csv'):
            data['sms_log'] = pd.read_csv('sms_log_data.csv', encoding='utf-8')
        else:
            data['sms_log'] = pd.DataFrame()
        
        # 대기 시간 데이터
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
    st.error("데이터를 로드할 수 없습니다.")
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
    "📈 통계 및 리포트"
])

# 실시간 업데이트 버튼
if st.sidebar.button("🔄 새로고침"):
    st.cache_data.clear()
    st.rerun()

# 대시보드
if menu == "📊 대시보드":
    st.header("📊 병원 운영 현황 대시보드")
    
    # 통계 데이터 계산
    appointments_df = csv_data['appointments']
    patients_df = csv_data['patients']
    waiting_df = csv_data['waiting_times']
    
    # 오늘 날짜로 필터링
    today_str = date.today().strftime('%Y-%m-%d')
    
    if not appointments_df.empty:
        today_appointments = appointments_df[appointments_df['date'] == today_str]
        
        # 메트릭 표시
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
            # 대기시간에 따른 색상 표시
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
        
        # 오늘 예약 현황 차트
        st.subheader("📈 오늘 예약 현황")
        if len(today_appointments) > 0:
            hourly_appointments = today_appointments.copy()
            hourly_appointments['hour'] = pd.to_datetime(hourly_appointments['time']).dt.hour
            hourly_count = hourly_appointments.groupby('hour').size().reset_index(name='count')
            
            fig = px.bar(hourly_count, x='hour', y='count',
                        title="시간대별 예약 현황",
                        labels={'hour': '시간', 'count': '예약 수'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("오늘 예약이 없습니다.")
    else:
        st.info("예약 데이터가 없습니다.")

# 환자 관리
elif menu == "👤 환자 관리":
    st.header("👤 환자 관리")
    
    tab1, tab2 = st.tabs(["👤 환자 등록", "📋 환자 목록"])
    
    with tab1:
        st.subheader("새 환자 등록")
        st.info("💡 이 데모에서는 실제 등록이 되지 않습니다. Supabase 연동 버전을 사용하세요.")
        
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
            
            submitted = st.form_submit_button("환자 등록 (데모)")
            
            if submitted and name:
                st.success("✅ 환자 정보가 입력되었습니다! (데모 모드)")
                st.info("실제 저장을 위해서는 Supabase 연동이 필요합니다.")
    
    with tab2:
        st.subheader("등록된 환자 목록")
        
        patients_df = csv_data['patients']
        if not patients_df.empty:
            # 검색 기능
            search_term = st.text_input("환자 검색", placeholder="이름으로 검색...")
            if search_term:
                patients_df = patients_df[patients_df['name'].str.contains(search_term, na=False)]
            
            # 환자 목록 표시
            display_cols = ['id', 'name', 'birth_date', 'gender', 'phone', 'insurance']
            available_cols = [col for col in display_cols if col in patients_df.columns]
            
            if available_cols:
                display_df = patients_df[available_cols]
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
                st.dataframe(patients_df, use_container_width=True)
        else:
            st.info("등록된 환자가 없습니다.")

# 의료진 관리
elif menu == "👨‍⚕️ 의료진 관리":
    st.header("👨‍⚕️ 의료진 관리")
    
    tab1, tab2 = st.tabs(["👨‍⚕️ 의료진 등록", "📋 의료진 목록"])
    
    with tab1:
        st.subheader("새 의료진 등록")
        st.info("💡 이 데모에서는 실제 등록이 되지 않습니다.")
        
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
            
            submitted = st.form_submit_button("의료진 등록 (데모)")
            
            if submitted and name:
                st.success("✅ 의료진 정보가 입력되었습니다! (데모 모드)")
    
    with tab2:
        st.subheader("등록된 의료진 목록")
        
        doctors_df = csv_data['doctors']
        if not doctors_df.empty:
            display_cols = ['id', 'name', 'specialty', 'phone', 'email', 'work_hours']
            available_cols = [col for col in display_cols if col in doctors_df.columns]
            
            if available_cols:
                display_df = doctors_df[available_cols]
                column_names = {
                    'id': 'ID',
                    'name': '이름',
                    'specialty': '전문분야',
                    'phone': '연락처',
                    'email': '이메일',
                    'work_hours': '근무시간'
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
        
        # 예약 통계
        st.subheader("📊 예약 통계")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_today = len(filtered_appointments)
            st.metric("선택일 총 예약", total_today)
        with col2:
            completed_today = len(filtered_appointments[filtered_appointments['status'] == '진료완료'])
            st.metric("완료된 진료", completed_today)
        with col3:
            waiting_today = len(filtered_appointments[filtered_appointments['status'] == '예약완료'])
            st.metric("대기 중", waiting_today)
    else:
        st.info("예약 데이터가 없습니다.")

# 진료 기록
elif menu == "📋 진료 기록":
    st.header("📋 진료 기록 관리")
    
    medical_records_df = csv_data['medical_records']
    patients_df = csv_data['patients']
    doctors_df = csv_data['doctors']
    
    if not medical_records_df.empty:
        st.subheader("📝 진료 기록 목록")
        
        # 환자명과 의사명 매핑
        if not patients_df.empty and not doctors_df.empty:
            patient_names = dict(zip(patients_df['id'], patients_df['name']))
            doctor_names = dict(zip(doctors_df['id'], doctors_df['name']))
            
            display_records = medical_records_df.copy()
            display_records['환자명'] = display_records['patient_id'].map(patient_names)
            display_records['의사명'] = display_records['doctor_id'].map(doctor_names)
            
            display_cols = ['환자명', '의사명', 'chief_complaint', 'diagnosis', 'treatment', 'created_at']
            available_cols = [col for col in display_cols if col in display_records.columns]
            
            if available_cols:
                final_df = display_records[available_cols]
                column_names = {
                    'chief_complaint': '주증상',
                    'diagnosis': '진단',
                    'treatment': '치료내용',
                    'created_at': '작성일시'
                }
                final_df.columns = [column_names.get(col, col) for col in available_cols]
                st.dataframe(final_df, use_container_width=True)
            else:
                st.dataframe(display_records, use_container_width=True)
        else:
            st.dataframe(medical_records_df, use_container_width=True)
    else:
        st.info("등록된 진료 기록이 없습니다.")

# 실시간 대기현황
elif menu == "⏰ 실시간 대기현황":
    st.header("⏰ 실시간 대기현황")
    
    waiting_df = csv_data['waiting_times']
    
    # 현재 시간 표시
    current_time = datetime.now()
    st.info(f"🕐 현재 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not waiting_df.empty:
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
                    # 상태 업데이트 버튼 (데모용)
                    if st.button("완료", key=f"complete_{idx}"):
                        st.success("진료 완료 처리됨 (데모)")
                
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

# SMS 관리
elif menu == "📱 SMS 관리":
    st.header("📱 SMS 관리")
    
    sms_df = csv_data['sms_log']
    
    if not sms_df.empty:
        st.subheader("📤 SMS 발송 내역")
        
        # 날짜 필터
        filter_date = st.date_input("날짜 선택", value=date.today())
        
        # 메시지 유형 필터
        if 'message_type' in sms_df.columns:
            message_types = sms_df['message_type'].unique()
            selected_type = st.selectbox("메시지 유형", ['전체'] + list(message_types))
            
            filtered_sms = sms_df.copy()
            if selected_type != '전체':
                filtered_sms = filtered_sms[filtered_sms['message_type'] == selected_type]
        else:
            filtered_sms = sms_df.copy()
        
        # SMS 목록 표시
        display_cols = ['timestamp', 'recipient', 'message', 'status']
        if 'message_type' in filtered_sms.columns:
            display_cols.append('message_type')
        
        available_cols = [col for col in display_cols if col in filtered_sms.columns]
        
        if available_cols:
            display_df = filtered_sms[available_cols]
            column_names = {
                'timestamp': '발송시간',
                'recipient': '수신자',
                'message': '메시지 내용',
                'status': '상태',
                'message_type': '유형'
            }
            display_df.columns = [column_names.get(col, col) for col in available_cols]
            st.dataframe(display_df, use_container_width=True)
        else:
            st.dataframe(filtered_sms, use_container_width=True)
        
        # 통계
        st.subheader("📊 SMS 발송 통계")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 발송 건수", len(sms_df))
        with col2:
            if 'status' in sms_df.columns:
                success_count = len(sms_df[sms_df['status'] == '발송완료'])
                st.metric("발송 성공", success_count)
            else:
                st.metric("발송 성공", "N/A")
        with col3:
            if 'status' in sms_df.columns:
                success_rate = (success_count / len(sms_df) * 100) if len(sms_df) > 0 else 0
                st.metric("성공률", f"{success_rate:.1f}%")
            else:
                st.metric("성공률", "N/A")
    else:
        st.info("SMS 발송 내역이 없습니다.")

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
        
        # 예약 상태별 분포
        if 'status' in appointments_df.columns:
            st.subheader("📋 예약 상태별 현황")
            status_stats = appointments_df['status'].value_counts().reset_index()
            status_stats.columns = ['상태', '건수']
            
            fig3 = px.bar(status_stats, x='상태', y='건수',
                         title="예약 상태별 현황")
            st.plotly_chart(fig3, use_container_width=True)
        
        # 환자 성별 분포
        if not patients_df.empty and 'gender' in patients_df.columns:
            st.subheader("👥 환자 성별 분포")
            gender_stats = patients_df['gender'].value_counts()
            fig_gender = px.pie(values=gender_stats.values,
                              names=gender_stats.index,
                              title="환자 성별 분포")
            st.plotly_chart(fig_gender, use_container_width=True)
        
        # 주요 통계 지표
        st.subheader("📊 주요 지표")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_appointments = len(appointments_df)
            st.metric("총 예약 건수", total_appointments)
        with col2:
            if 'status' in appointments_df.columns:
                completed_rate = len(appointments_df[appointments_df['status'] == '진료완료']) / total_appointments * 100 if total_appointments > 0 else 0
                st.metric("진료 완료율", f"{completed_rate:.1f}%")
            else:
                st.metric("진료 완료율", "N/A")
        with col3:
            total_patients = len(patients_df) if not patients_df.empty else 0
            st.metric("총 환자 수", total_patients)
        with col4:
            avg_daily_appointments = total_appointments / 30  # 월평균 기준
            st.metric("일평균 예약", f"{avg_daily_appointments:.1f}건")
            
    else:
        st.info("통계를 생성할 예약 데이터가 없습니다.")

# 푸터
st.markdown("---")
st.markdown("🏥 **스마트 병원 관리 시스템** | CSV 데이터 기반 데모 버전")
st.info("💡 실제 데이터 저장 및 수정을 위해서는 Supabase 연동 버전을 사용하세요.")