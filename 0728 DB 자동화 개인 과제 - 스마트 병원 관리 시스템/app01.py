import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# DB 연결
conn = sqlite3.connect('soap_records.db', check_same_thread=False)
cursor = conn.cursor()

# 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS soap_note (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    visit_date TEXT,
    subjective TEXT,
    objective TEXT,
    assessment TEXT,
    plan TEXT
)
''')
conn.commit()

# Streamlit UI
st.set_page_config(page_title="스마트 병원 SOAP 기록 시스템", layout="wide")
st.title("🏥 물리치료사용 SOAP 진료 기록 시스템")

menu = ["SOAP 기록 작성", "기록 조회"]
choice = st.sidebar.selectbox("메뉴 선택", menu)

if choice == "SOAP 기록 작성":
    st.subheader("📄 SOAP 기록 입력")

    with st.form(key='soap_form'):
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("환자 이름")
        with col2:
            visit_date = st.date_input("방문일", value=datetime.today())

        subjective = st.text_area("🗣️ S (Subjective)", height=100)
        objective = st.text_area("🔍 O (Objective)", height=100)
        assessment = st.text_area("🧠 A (Assessment)", height=100)
        plan = st.text_area("📅 P (Plan)", height=100)

        submitted = st.form_submit_button("기록 저장")

        if submitted:
            if patient_name:  # 환자 이름이 입력되었는지 확인
                cursor.execute('''
                    INSERT INTO soap_note (patient_name, visit_date, subjective, objective, assessment, plan)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (patient_name, visit_date.strftime('%Y-%m-%d'), subjective, objective, assessment, plan))
                conn.commit()
                st.success("기록이 저장되었습니다!")
            else:
                st.error("환자 이름을 입력해주세요.")

elif choice == "기록 조회":
    st.subheader("📁 SOAP 기록 조회")

    df = pd.read_sql_query("SELECT * FROM soap_note ORDER BY visit_date DESC", conn)
    st.dataframe(df)

    with st.expander("🔍 상세 조회"):
        selected_id = st.number_input("기록 ID 입력", min_value=1, step=1)
        if st.button("조회"):
            result = cursor.execute("SELECT * FROM soap_note WHERE id = ?", (selected_id,))
            row = result.fetchone()
            if row:
                st.markdown(f"**🧾 ID:** {row[0]}")
                st.markdown(f"**👤 환자명:** {row[1]}")
                st.markdown(f"**📅 방문일:** {row[2]}")
                st.markdown("**🗣️ S (Subjective):**")
                st.info(row[3])
                st.markdown("**🔍 O (Objective):**")
                st.info(row[4])
                st.markdown("**🧠 A (Assessment):**")
                st.info(row[5])
                st.markdown("**📅 P (Plan):**")
                st.info(row[6])
            else:
                st.warning("해당 ID의 기록이 없습니다.")
