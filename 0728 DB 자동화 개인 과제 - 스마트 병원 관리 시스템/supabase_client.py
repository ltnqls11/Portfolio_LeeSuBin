"""
Supabase 연동 모듈 - Streamlit 앱용
"""

import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client
from datetime import datetime, date
from typing import List, Dict, Optional

class SupabaseClient:
    def __init__(self):
        """Supabase 클라이언트 초기화"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            st.error("Supabase 설정이 필요합니다. 환경변수 SUPABASE_URL과 SUPABASE_KEY를 설정해주세요.")
            return
        
        try:
            self.supabase: Client = create_client(self.url, self.key)
            st.success("✅ Supabase 연결 성공!")
        except Exception as e:
            st.error(f"❌ Supabase 연결 실패: {e}")
            self.supabase = None
    
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self.supabase is not None
    
    # 환자 관련 메서드
    def get_patients(self) -> List[Dict]:
        """모든 환자 조회"""
        try:
            result = self.supabase.table('patients').select('*').execute()
            return result.data
        except Exception as e:
            st.error(f"환자 데이터 조회 실패: {e}")
            return []
    
    def add_patient(self, patient_data: Dict) -> bool:
        """환자 추가"""
        try:
            result = self.supabase.table('patients').insert(patient_data).execute()
            st.success("환자가 성공적으로 등록되었습니다!")
            return True
        except Exception as e:
            st.error(f"환자 등록 실패: {e}")
            return False
    
    def update_patient(self, patient_id: int, patient_data: Dict) -> bool:
        """환자 정보 수정"""
        try:
            result = self.supabase.table('patients').update(patient_data).eq('id', patient_id).execute()
            st.success("환자 정보가 수정되었습니다!")
            return True
        except Exception as e:
            st.error(f"환자 정보 수정 실패: {e}")
            return False
    
    # 의료진 관련 메서드
    def get_doctors(self) -> List[Dict]:
        """모든 의료진 조회"""
        try:
            result = self.supabase.table('doctors').select('*').execute()
            return result.data
        except Exception as e:
            st.error(f"의료진 데이터 조회 실패: {e}")
            return []
    
    def add_doctor(self, doctor_data: Dict) -> bool:
        """의료진 추가"""
        try:
            result = self.supabase.table('doctors').insert(doctor_data).execute()
            st.success("의료진이 성공적으로 등록되었습니다!")
            return True
        except Exception as e:
            st.error(f"의료진 등록 실패: {e}")
            return False
    
    # 예약 관련 메서드
    def get_appointments(self, date_filter: Optional[str] = None) -> List[Dict]:
        """예약 조회 (날짜 필터 옵션)"""
        try:
            query = self.supabase.table('appointments').select('''
                *,
                patients(name, phone),
                doctors(name, specialty)
            ''')
            
            if date_filter:
                query = query.eq('date', date_filter)
            
            result = query.execute()
            return result.data
        except Exception as e:
            st.error(f"예약 데이터 조회 실패: {e}")
            return []
    
    def add_appointment(self, appointment_data: Dict) -> bool:
        """예약 추가"""
        try:
            result = self.supabase.table('appointments').insert(appointment_data).execute()
            st.success("예약이 성공적으로 등록되었습니다!")
            return True
        except Exception as e:
            st.error(f"예약 등록 실패: {e}")
            return False
    
    def update_appointment_status(self, appointment_id: int, status: str) -> bool:
        """예약 상태 업데이트"""
        try:
            result = self.supabase.table('appointments').update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', appointment_id).execute()
            st.success(f"예약 상태가 '{status}'로 변경되었습니다!")
            return True
        except Exception as e:
            st.error(f"예약 상태 변경 실패: {e}")
            return False
    
    # 진료 기록 관련 메서드
    def get_medical_records(self, patient_id: Optional[int] = None) -> List[Dict]:
        """진료 기록 조회"""
        try:
            query = self.supabase.table('medical_records').select('''
                *,
                patients(name),
                doctors(name, specialty)
            ''')
            
            if patient_id:
                query = query.eq('patient_id', patient_id)
            
            result = query.execute()
            return result.data
        except Exception as e:
            st.error(f"진료 기록 조회 실패: {e}")
            return []
    
    def add_medical_record(self, record_data: Dict) -> bool:
        """진료 기록 추가"""
        try:
            result = self.supabase.table('medical_records').insert(record_data).execute()
            st.success("진료 기록이 저장되었습니다!")
            return True
        except Exception as e:
            st.error(f"진료 기록 저장 실패: {e}")
            return False
    
    # SMS 로그 관련 메서드
    def get_sms_logs(self, date_filter: Optional[str] = None) -> List[Dict]:
        """SMS 로그 조회"""
        try:
            query = self.supabase.table('sms_log').select('*').order('timestamp', desc=True)
            
            if date_filter:
                query = query.gte('timestamp', f'{date_filter} 00:00:00').lte('timestamp', f'{date_filter} 23:59:59')
            
            result = query.execute()
            return result.data
        except Exception as e:
            st.error(f"SMS 로그 조회 실패: {e}")
            return []
    
    def add_sms_log(self, sms_data: Dict) -> bool:
        """SMS 로그 추가"""
        try:
            result = self.supabase.table('sms_log').insert(sms_data).execute()
            return True
        except Exception as e:
            st.error(f"SMS 로그 저장 실패: {e}")
            return False
    
    # 대기 시간 관련 메서드
    def get_waiting_times(self) -> List[Dict]:
        """현재 대기 시간 조회"""
        try:
            result = self.supabase.table('waiting_times').select('*').eq('current_status', '대기중').execute()
            return result.data
        except Exception as e:
            st.error(f"대기 시간 조회 실패: {e}")
            return []
    
    def update_waiting_time(self, waiting_id: int, wait_minutes: int) -> bool:
        """대기 시간 업데이트"""
        try:
            result = self.supabase.table('waiting_times').update({
                'estimated_wait_minutes': wait_minutes,
                'last_updated': datetime.now().isoformat()
            }).eq('id', waiting_id).execute()
            return True
        except Exception as e:
            st.error(f"대기 시간 업데이트 실패: {e}")
            return False
    
    # 의료진 스케줄 관련 메서드
    def get_doctor_schedules(self, date_filter: Optional[str] = None) -> List[Dict]:
        """의료진 스케줄 조회"""
        try:
            query = self.supabase.table('doctor_schedules').select('*')
            
            if date_filter:
                query = query.eq('date', date_filter)
            
            result = query.execute()
            return result.data
        except Exception as e:
            st.error(f"스케줄 조회 실패: {e}")
            return []
    
    def update_schedule_patients(self, schedule_id: int, current_patients: int) -> bool:
        """스케줄의 현재 환자 수 업데이트"""
        try:
            result = self.supabase.table('doctor_schedules').update({
                'current_patients': current_patients,
                'updated_at': datetime.now().isoformat()
            }).eq('id', schedule_id).execute()
            return True
        except Exception as e:
            st.error(f"스케줄 업데이트 실패: {e}")
            return False
    
    # 통계 관련 메서드
    def get_dashboard_stats(self) -> Dict:
        """대시보드용 통계 데이터"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            
            # 오늘 예약 수
            today_appointments = self.supabase.table('appointments').select('*').eq('date', today).execute()
            
            # 총 환자 수
            total_patients = self.supabase.table('patients').select('id').execute()
            
            # 진료 완료 수
            completed_today = self.supabase.table('appointments').select('*').eq('date', today).eq('status', '진료완료').execute()
            
            # 대기 중 수
            waiting_today = self.supabase.table('appointments').select('*').eq('date', today).eq('status', '예약완료').execute()
            
            return {
                'today_appointments': len(today_appointments.data),
                'total_patients': len(total_patients.data),
                'completed_today': len(completed_today.data),
                'waiting_today': len(waiting_today.data)
            }
        except Exception as e:
            st.error(f"통계 데이터 조회 실패: {e}")
            return {
                'today_appointments': 0,
                'total_patients': 0,
                'completed_today': 0,
                'waiting_today': 0
            }

# 전역 Supabase 클라이언트 인스턴스
@st.cache_resource
def get_supabase_client():
    """캐시된 Supabase 클라이언트 반환"""
    return SupabaseClient()

# 편의 함수들
def format_date_for_db(date_obj) -> str:
    """날짜 객체를 DB 형식으로 변환"""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime('%Y-%m-%d')

def format_datetime_for_db(datetime_obj) -> str:
    """날짜시간 객체를 DB 형식으로 변환"""
    if isinstance(datetime_obj, str):
        return datetime_obj
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')