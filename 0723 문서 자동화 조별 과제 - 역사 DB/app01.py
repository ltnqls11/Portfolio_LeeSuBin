import streamlit as st
import pandas as pd
import datetime
import re
import matplotlib.pyplot as plt
import os

# ------------------
# 📦 데이터 정의
# ------------------
@st.cache_data
def load_data():
    """history1.csv 파일에서 데이터를 로드합니다."""
    try:
        # CSV 파일 읽기
        df = pd.read_csv("history1.csv", encoding="utf-8")
        
        # 연도 추출 함수
        def extract_year(date_str):
            if pd.isna(date_str):
                return 2000  # 기본값
            match = re.search(r"(\d{4})년", str(date_str))
            return int(match.group(1)) if match else 2000
        
        # 연도 컬럼 추가
        df["연도"] = df["날짜"].apply(extract_year)
        
        # 인물 정보 추출 (제목과 내용에서)
        def extract_people(row):
            people = []
            title = str(row.get("제목", ""))
            content = str(row.get("내용", ""))
            
            # 주요 인물들 패턴 매칭
            famous_people = [
                "세종", "세종대왕", "이순신", "정조", "영조", "태종", "태조", "선조",
                "방정환", "김종직", "전봉준", "안중근", "윤봉길", "김구", "이승만",
                "박정희", "김대중", "노무현", "문재인", "임연", "세자", "왕", "대왕",
                "지학순", "홍석현", "김영란", "최종영", "이현세", "이태복"
            ]
            
            for person in famous_people:
                if person in title or person in content:
                    people.append(person)
            
            return ", ".join(list(set(people))) if people else ""
        
        # 시대 분류 함수
        def classify_period(year):
            if year < 1392:
                return "고려시대"
            elif year < 1598:
                return "조선전기"
            elif year < 1800:
                return "조선중기"
            elif year < 1897:
                return "조선후기"
            elif year < 1910:
                return "대한제국"
            elif year < 1945:
                return "일제강점기"
            elif year < 1988:
                return "현대"
            else:
                return "현재"
        
        # 테마 분류 함수
        def classify_theme(row):
            title = str(row.get("제목", "")).lower()
            content = str(row.get("내용", "")).lower()
            text = title + " " + content
            
            if any(word in text for word in ["전쟁", "전투", "해전", "침입", "방어", "군사"]):
                return "전쟁"
            elif any(word in text for word in ["문화", "학교", "교육", "서원", "책", "문학", "예술"]):
                return "문화"
            elif any(word in text for word in ["정치", "왕", "즉위", "정부", "조약", "법", "제도"]):
                return "정치"
            elif any(word in text for word in ["경제", "세금", "농업", "상업", "무역", "화폐"]):
                return "경제"
            elif any(word in text for word in ["사회", "민중", "농민", "운동", "시위", "봉기"]):
                return "사회운동"
            elif any(word in text for word in ["독립", "항일", "저항", "해방", "광복"]):
                return "독립운동"
            elif any(word in text for word in ["재해", "홍수", "지진", "화재", "사고"]):
                return "재해"
            else:
                return "기타"
        
        # 새로운 컬럼들 추가
        df["인물"] = df.apply(extract_people, axis=1)
        df["시대"] = df["연도"].apply(classify_period)
        df["테마"] = df.apply(classify_theme, axis=1)
        df["즐겨찾기"] = False
        
        # 결측값 처리
        df = df.fillna("")
        
        return df
        
    except FileNotFoundError:
        st.error("❌ history1.csv 파일을 찾을 수 없습니다.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()

df = load_data()

# ------------------
# 📌 사이드바 필터
# ------------------
st.sidebar.header("🔎 필터 설정")

# 키워드 검색
search = st.sidebar.text_input("🔍 키워드 검색", "")

# 연도 범위 선택 (전체 데이터 범위로 확장)
min_year = df["연도"].min()
max_year = df["연도"].max()
year_range = st.sidebar.slider("📅 연도 범위 선택", min_year, max_year, (min_year, max_year))

# 특정 인물 필터링
st.sidebar.subheader("👤 인물별 필터")
all_people = []
for people_str in df["인물"]:
    if people_str:  # 빈 문자열이 아닌 경우
        people_list = [p.strip() for p in people_str.split(",")]
        all_people.extend(people_list)

unique_people = ["전체"] + sorted(list(set(all_people)))
selected_person = st.sidebar.selectbox("🎭 특정 인물 선택", unique_people)

# 시대별 필터
st.sidebar.subheader("🏛️ 시대별 필터")
unique_periods = ["전체"] + sorted(df["시대"].unique().tolist())
selected_period = st.sidebar.selectbox("⏰ 시대 선택", unique_periods)

# 테마별 필터
st.sidebar.subheader("🎯 테마별 필터")
unique_themes = ["전체"] + sorted(df["테마"].unique().tolist())
selected_theme = st.sidebar.selectbox("🏷️ 테마 선택", unique_themes)

# ------------------
# 📊 필터 적용
# ------------------
# 1. 연도 범위 필터
filtered = df[df["연도"].between(year_range[0], year_range[1])]

# 2. 키워드 검색 필터
if search:
    filtered = filtered[
        filtered["제목"].str.contains(search, case=False, na=False) | 
        filtered["내용"].str.contains(search, case=False, na=False) |
        filtered["인물"].str.contains(search, case=False, na=False)
    ]

# 3. 인물 필터
if selected_person != "전체":
    filtered = filtered[filtered["인물"].str.contains(selected_person, case=False, na=False)]

# 4. 시대 필터
if selected_period != "전체":
    filtered = filtered[filtered["시대"] == selected_period]

# 5. 테마 필터
if selected_theme != "전체":
    filtered = filtered[filtered["테마"] == selected_theme]

# ------------------
# 🧠 GPT 요약 (모의)
# ------------------
def gpt_summary(text):
    return "🧠 요약: 세자가 쿠데타 소식을 듣고 귀국을 중단하고 몽고로 되돌아갔음."

# ------------------
# 🎨 UI 구성
# ------------------
st.title("📜 한국사 역사 기록 대시보드")

# 필터링 결과 요약 표시
st.info(f"🔍 총 {len(filtered)}개의 기록이 검색되었습니다. (전체 {len(df)}개 중)")

# 현재 적용된 필터 표시
filter_info = []
if selected_person != "전체":
    filter_info.append(f"👤 인물: {selected_person}")
if selected_period != "전체":
    filter_info.append(f"🏛️ 시대: {selected_period}")
if selected_theme != "전체":
    filter_info.append(f"🎯 테마: {selected_theme}")
if search:
    filter_info.append(f"🔍 키워드: '{search}'")

if filter_info:
    st.markdown("**적용된 필터:** " + " | ".join(filter_info))

st.markdown("---")

# 📑 테이블 출력
st.subheader("🗂️ 역사 기록 목록")

if len(filtered) == 0:
    st.warning("검색 조건에 맞는 기록이 없습니다. 필터를 조정해보세요.")
else:
    for idx, row in filtered.iterrows():
        # 카드 형태로 표시
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {row['제목']}")
                st.markdown(f"📅 **날짜:** {row['날짜']}")
                
                # 인물, 시대, 테마 태그 표시
                tags = []
                if row['인물']:
                    tags.append(f"👤 {row['인물']}")
                tags.append(f"🏛️ {row['시대']}")
                tags.append(f"🎯 {row['테마']}")
                
                st.markdown("**태그:** " + " | ".join(tags))
                st.markdown(f"📝 **내용:** {row['내용']}")
                st.markdown(f"🔗 [원문 링크 바로가기]({row['링크']})")
            
            with col2:
                # GPT 요약 버튼
                if st.button(f"🧠 GPT 요약", key=f"summary_{idx}"):
                    st.success(gpt_summary(row["내용"]))
                
                # 즐겨찾기 토글
                new_fav = st.checkbox("📖 책갈피", value=row["즐겨찾기"], key=f"fav_{idx}")
                df.at[idx, "즐겨찾기"] = new_fav
        
        st.markdown("---")

# 📌 책갈피 목록
st.subheader("📖 책갈피")
fav_df = df[df["즐겨찾기"]]
if not fav_df.empty:
    st.dataframe(fav_df[["날짜", "제목", "내용", "링크"]])
else:
    st.info("책갈피에 저장된 사건이 없습니다.")