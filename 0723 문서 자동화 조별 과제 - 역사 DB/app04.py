import streamlit as st
import pandas as pd

st.set_page_config(page_title="한국사 주요 사건 대시보드", layout="wide")

# ------------------
# 데이터 로드
# ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("history_textbook.csv")
    df["연도"] = df["날짜"].astype(int)
    return df

df = load_data()

# ------------------
# 사이드바 필터
# ------------------
st.sidebar.header("🔎 필터 설정")

# 연도 범위
min_year, max_year = df["연도"].min(), df["연도"].max()
year_range = st.sidebar.slider("📅 연도 범위", min_year, max_year, (min_year, max_year))

# 키워드 검색
search = st.sidebar.text_input("🔍 키워드 검색", "")

# ------------------
# 필터링
# ------------------
filtered = df[df["연도"].between(year_range[0], year_range[1])]

if search:
    filtered = filtered[
        filtered["제목"].str.contains(search, case=False) |
        filtered["내용"].str.contains(search, case=False)
    ]

# ------------------
# 메인 UI
# ------------------
st.title("📜 한국사 교과서 주요 사건 대시보드")
st.markdown("초중고 한국사에서 배우는 핵심 사건들을 시기순으로 확인할 수 있습니다.")

st.info(f"총 {len(filtered)}건의 사건이 검색되었습니다.")

# 카드 형태로 출력
for _, row in filtered.iterrows():
    with st.container():
        st.markdown(f"### 📌 {row['제목']} ({row['연도']}년)")
        st.markdown(f"📝 {row['내용']}")
        if row["링크"]:
            st.markdown(f"[🔗 관련 링크]({row['링크']})")
        st.markdown("---")
