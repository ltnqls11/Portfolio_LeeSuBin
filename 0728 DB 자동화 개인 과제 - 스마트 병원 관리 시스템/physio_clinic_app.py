import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# ----------------------------
# 초기 설정 및 데이터
# ----------------------------

st.set_page_config(page_title="스마트 물리치료 예약 시스템", layout="wide")
st.title("🏥 스마트 물리치료 예약 및 기록 시스템")

# 가상 환자/치료사 데이터
patients = ["김철수", "이영희", "박민수"]
therapists = ["홍길동", "이도윤"]
treatments = {"도수치료": 50, "운동치료": 30}

# 세션 상태 저장용 DB (데모용)
if "records" not in st.session_state:
    st.session_state.records = []

# ----------------------------
# 진료 기록 (SOAP)
# ----------------------------

st.subheader("📝 SOAP 진료 기록")
with st.form("soap_form"):
    selected_patient = st.selectbox("환자 선택", patients)
    selected_treatment = st.selectbox("치료 종류", list(treatments.keys()))
    s = st.text_area("S (Subjective)", placeholder="환자 주관적 증상")
    o = st.text_area("O (Objective)", placeholder="치료사의 객관적 소견")
    a = st.text_area("A (Assessment)", placeholder="진단 및 평가")
    p = st.text_area("P (Plan)", placeholder="치료 계획")
    submit_btn = st.form_submit_button("기록 저장")

if submit_btn:
    st.session_state.records.append({
        "환자": selected_patient,
        "치료": selected_treatment,
        "날짜": datetime.datetime.now(),
        "S": s, "O": o, "A": a, "P": p
    })
    st.success("기록이 저장되었습니다.")

# ----------------------------
# 치료 예약 시스템 (자동 시간 반영)
# ----------------------------

st.subheader("📅 예약 등록")
with st.form("reservation_form"):
    res_patient = st.selectbox("예약 환자", patients, key="res_patient")
    res_treatment = st.selectbox("예약 치료 종류", list(treatments.keys()), key="res_treatment")
    res_therapist = st.selectbox("담당 치료사", therapists)
    start_time = st.time_input("시작 시간", value=datetime.time(9, 0))
    base_date = st.date_input("예약일", value=datetime.date.today())

    submit_res = st.form_submit_button("예약 등록")

if submit_res:
    duration = treatments[res_treatment]
    start_dt = datetime.datetime.combine(base_date, start_time)
    end_dt = start_dt + datetime.timedelta(minutes=duration)
    
    # 충돌 검사: 간단한 동시 예약 1건 제한 로직 (도수치료 1:1 / 운동치료 1:2 미적용)
    conflict = False
    for rec in st.session_state.records:
        if rec["환자"] == res_patient and "예약" in rec:
            existing = rec["예약"]
            existing_start = existing["start"]
            existing_end = existing["end"]
            if (start_dt < existing_end and end_dt > existing_start):
                conflict = True
                break
    
    if conflict:
        st.error("❗ 예약 시간이 기존 예약과 겹칩니다.")
    else:
        st.session_state.records.append({
            "환자": res_patient,
            "치료": res_treatment,
            "치료사": res_therapist,
            "예약": {
                "start": start_dt,
                "end": end_dt
            }
        })
        st.success(f"{res_patient}님의 예약이 {start_dt.strftime('%H:%M')} ~ {end_dt.strftime('%H:%M')}로 등록되었습니다.")

# ----------------------------
# 시각화 (ROM/Pain before-after 비교)
# ----------------------------

st.subheader("📈 치료 전후 변화 (ROM / Pain)")
data = pd.DataFrame({
    "날짜": ["7/1", "7/5", "7/10", "7/15"],
    "ROM(도)": [50, 60, 70, 85],
    "통증(NRS)": [7, 6, 4, 2]
})
col1, col2 = st.columns(2)
with col1:
    st.markdown("**ROM 변화**")
    fig1 = px.line(data, x="날짜", y="ROM(도)", markers=True, title="ROM 변화 추이")
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.markdown("**통증 변화**")
    fig2 = px.line(data, x="날짜", y="통증(NRS)", markers=True, title="통증 감소 추이", color_discrete_sequence=["red"])
    st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# 리마인드 (추적검사 알림)
# ----------------------------

st.subheader("📩 추적검사 리마인드 알림")

base_followup = st.date_input("기준 예약일", datetime.date.today())
remind_after = st.slider("며칠 후 알림 전송", min_value=7, max_value=90, value=30)
remind_date = base_followup + datetime.timedelta(days=remind_after)
st.info(f"📅 리마인드 전송 예정일: `{remind_date}` (SMS 자동 전송)")

# ----------------------------
# 진료 기록 전체 보기
# ----------------------------

with st.expander("📋 전체 진료 기록 보기"):
    st.dataframe(pd.DataFrame(st.session_state.records))
