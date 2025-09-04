import streamlit as st
import pandas as pd
from datetime import date

st.title("🏥 병원 관리 시스템 테스트")

# 간단한 CSV 로딩 테스트
try:
    st.write("CSV 파일 로딩 테스트 중...")
    
    # 환자 데이터 로딩
    patients_df = pd.read_csv('patients_data.csv', encoding='utf-8')
    st.success(f"✅ 환자 데이터 로딩 성공: {len(patients_df)}명")
    
    # 의사 데이터 로딩
    doctors_df = pd.read_csv('doctors_data.csv', encoding='utf-8')
    st.success(f"✅ 의사 데이터 로딩 성공: {len(doctors_df)}명")
    
    # 예약 데이터 로딩
    appointments_df = pd.read_csv('appointments_data.csv', encoding='utf-8')
    st.success(f"✅ 예약 데이터 로딩 성공: {len(appointments_df)}건")
    
    # 데이터 표시
    st.subheader("📋 환자 목록")
    st.dataframe(patients_df.head())
    
    st.subheader("👨‍⚕️ 의료진 목록")
    st.dataframe(doctors_df.head())
    
    st.subheader("📅 예약 목록")
    st.dataframe(appointments_df.head())
    
except Exception as e:
    st.error(f"오류 발생: {e}")
    st.write("오류 세부사항:")
    st.exception(e)

st.write("테스트 완료!")