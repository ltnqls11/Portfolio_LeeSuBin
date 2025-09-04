
import streamlit as st
import pandas as pd

# 데이터 불러오기
df = pd.read_csv("history2.csv")

# Sidebar 필터
st.sidebar.header("필터")
unique_era = df['시대'].dropna().unique()
unique_category = df['카테고리'].dropna().unique()

selected_era = st.sidebar.multiselect("시대 선택", sorted(unique_era))
selected_category = st.sidebar.multiselect("카테고리 선택", sorted(unique_category))

# 필터 적용
filtered_df = df.copy()
if selected_era:
    filtered_df = filtered_df[filtered_df['시대'].isin(selected_era)]
if selected_category:
    filtered_df = filtered_df[filtered_df['카테고리'].isin(selected_category)]

# 제목
st.title("📜 역사 대시보드")
st.markdown("시대와 카테고리를 선택해 아래에서 역사 사건을 탐색해보세요.")

# 리스트 형태로 보여주기
for idx, row in filtered_df.iterrows():
    with st.expander(row["제목"].strip()):
        st.markdown(f"**날짜:** {row['날짜']}")
        st.markdown(f"**시대:** {row['시대']}")
        st.markdown(f"**카테고리:** {row['카테고리']}")
        st.markdown(f"**인물:** {row['인물']}")
        st.markdown(f"**요약:** {row['요약']}")
        st.markdown(f"**내용:** {row['내용']}")
        st.markdown(f"[🔗 원문 보기]({row['링크']})")
