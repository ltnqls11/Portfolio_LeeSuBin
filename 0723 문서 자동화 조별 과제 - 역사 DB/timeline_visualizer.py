import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

def load_history_data(date):
    file_path = f"history_{date.month:02d}_{date.day:02d}.csv"
    if not os.path.exists(file_path):
        st.error("해당 날짜의 데이터가 없습니다. 먼저 크롤링하세요.")
        return None
    df = pd.read_csv(file_path)
    return df

def plot_event_timeline(df):
    # 연도 숫자만 필터 (정수형만)
    df["연도"] = pd.to_numeric(df["연도"], errors="coerce")
    df = df.dropna(subset=["연도"])
    df["연도"] = df["연도"].astype(int)

    counts = df["연도"].value_counts().reset_index()
    counts.columns = ["연도", "사건수"]
    counts = counts.sort_values("연도")

    fig = px.line(counts, x="연도", y="사건수", markers=True, title="연도별 사건 분포")
    fig.update_layout(xaxis=dict(dtick=50))  # 연도 간격 설정
    st.plotly_chart(fig)

def main():
    st.title("📜 오늘의 역사 타임라인 시각화")

    # 날짜 선택
    selected_date = st.date_input("날짜를 선택하세요", value=datetime.date.today())
    df = load_history_data(selected_date)

    if df is not None:
        st.success(f"{selected_date.month}월 {selected_date.day}일 사건 수: {len(df)}개")
        plot_event_timeline(df)

        if st.checkbox("데이터 미리보기"):
            st.dataframe(df)

if __name__ == "__main__":
    main()
