import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import requests
from urllib.parse import quote

# -------------------
# �️ 이미지 관오련 함수
# -------------------
def get_history_image_url(keyword):
    """키워드를 기반으로 한국사 관련 이미지 URL을 생성합니다."""
    # 안정적인 한국사 관련 이미지들 (공개 이미지 사용)
    image_mapping = {
        "고구려": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Goguryeo_tomb_mural.jpg/300px-Goguryeo_tomb_mural.jpg",
        "백제": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Baekje_gilt-bronze_incense_burner.jpg/300px-Baekje_gilt-bronze_incense_burner.jpg",
        "신라": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Cheomseongdae.jpg/300px-Cheomseongdae.jpg",
        "고려": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Goryeo_celadon.jpg/300px-Goryeo_celadon.jpg",
        "조선": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Gyeongbokgung_Palace.jpg/300px-Gyeongbokgung_Palace.jpg",
        "세종": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/King_Sejong_the_Great.jpg/300px-King_Sejong_the_Great.jpg",
        "훈민정음": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Hunmin_jeong-eum.jpg/300px-Hunmin_jeong-eum.jpg",
        "임진왜란": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Japanese_invasion_of_Korea_1592-1598.png/300px-Japanese_invasion_of_Korea_1592-1598.png",
        "이순신": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Yi_Sun-sin.jpg/300px-Yi_Sun-sin.jpg",
        "일제강점기": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Japanese_Government_General_of_Korea.jpg/300px-Japanese_Government_General_of_Korea.jpg",
        "독립운동": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/March_1st_Movement_1919.jpg/300px-March_1st_Movement_1919.jpg",
        "3.1운동": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/March_1st_Movement_1919.jpg/300px-March_1st_Movement_1919.jpg",
        "광복": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Liberation_of_Korea_1945.jpg/300px-Liberation_of_Korea_1945.jpg",
        "한국전쟁": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Korean_War_Montage_2.png/300px-Korean_War_Montage_2.png",
        "경제발전": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Seoul_skyline.jpg/300px-Seoul_skyline.jpg"
    }
    
    # 키워드에 맞는 이미지 찾기
    for key, url in image_mapping.items():
        if key in keyword:
            return url
    
    # 기본 이미지 (한국 전통 이미지)
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Gyeongbokgung_Palace.jpg/300px-Gyeongbokgung_Palace.jpg"

def get_related_keywords(title):
    """단원 제목에서 관련 키워드를 추출합니다."""
    keywords = []
    
    # 시대별 키워드
    if any(word in title for word in ["고구려", "백제", "신라", "삼국"]):
        keywords.extend(["고구려", "백제", "신라"])
    elif "고려" in title:
        keywords.append("고려")
    elif "조선" in title:
        keywords.append("조선")
    
    # 인물별 키워드
    if "세종" in title:
        keywords.append("세종")
    if "이순신" in title:
        keywords.append("이순신")
    
    # 사건별 키워드
    if any(word in title for word in ["훈민정음", "한글"]):
        keywords.append("훈민정음")
    if any(word in title for word in ["임진왜란", "정유재란"]):
        keywords.append("임진왜란")
    if any(word in title for word in ["일제", "강점", "식민"]):
        keywords.append("일제강점기")
    if any(word in title for word in ["독립", "항일"]):
        keywords.append("독립운동")
    if "3.1" in title or "삼일" in title:
        keywords.append("3.1운동")
    if any(word in title for word in ["광복", "해방"]):
        keywords.append("광복")
    if "한국전쟁" in title:
        keywords.append("한국전쟁")
    if any(word in title for word in ["경제", "발전", "산업화"]):
        keywords.append("경제발전")
    
    return keywords[0] if keywords else "한국사"

# -------------------
# 📦 데이터 불러오기
# -------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("한국사_단원요약_키워드.csv")
        df["즐겨찾기"] = False
        
        # 연도 추출 (단원 제목 내에 숫자 연도가 없으면 -1)
        df["연도"] = df["단원 제목"].apply(lambda x: int(re.search(r"\d{3,4}", x).group()) if re.search(r"\d{3,4}", x) else -1)
        
        # 이미지 URL 추가
        df["이미지_URL"] = df["단원 제목"].apply(lambda x: get_history_image_url(get_related_keywords(x)))
        
        return df
    except FileNotFoundError:
        st.error("❌ '한국사_단원요약_키워드.csv' 파일을 찾을 수 없습니다.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()

df = load_data()

# -------------------
# 🎛️ 사이드바 필터
# -------------------
st.sidebar.header("🔍 필터")
search = st.sidebar.text_input("제목 또는 키워드 검색")
min_year = df["연도"].replace(-1, pd.NA).dropna().min()
max_year = df["연도"].replace(-1, pd.NA).dropna().max()
year_range = st.sidebar.slider("연도 범위", int(min_year), int(max_year), (int(min_year), int(max_year)))

# -------------------
# 🔎 필터 적용
# -------------------
filtered = df[(df["연도"] >= year_range[0]) & (df["연도"] <= year_range[1])]

if search:
    filtered = filtered[
        filtered["단원 제목"].str.contains(search, case=False, na=False) |
        filtered["키워드"].str.contains(search, case=False, na=False)
    ]

# -------------------
# 📊 연도별 단원 수 시각화
# -------------------
with st.expander("📈 단원 수 연도별 통계 보기"):
    year_count = df[df["연도"] != -1]["연도"].value_counts().sort_index()
    fig, ax = plt.subplots()
    year_count.plot(kind="bar", ax=ax, color="skyblue")
    ax.set_xlabel("연도")
    ax.set_ylabel("단원 수")
    ax.set_title("📊 연도별 단원 빈도")
    st.pyplot(fig)

st.markdown("---")

# -------------------
# 📄 본문 출력
# -------------------
st.title("📜 한국사 단원 요약 대시보드")

if filtered.empty:
    st.warning("⚠️ 검색 조건에 맞는 단원이 없습니다. 필터를 조정해보세요.")
else:
    st.info(f"🔍 총 {len(filtered)}개의 단원이 검색되었습니다. (전체 {len(df)}개 중)")

for idx, row in filtered.iterrows():
    # 카드 형태로 레이아웃 구성
    with st.container():
        col1, col2 = st.columns([2, 3])
        
        with col1:
            # 이미지 표시
            try:
                st.image(
                    row['이미지_URL'], 
                    caption=f"📸 {get_related_keywords(row['단원 제목'])} 관련 이미지",
                    width=250,
                    use_column_width=True
                )
            except Exception as e:
                st.info("🖼️ 이미지를 불러올 수 없습니다.")
                st.write(f"이미지 URL: {row['이미지_URL']}")
        
        with col2:
            st.markdown(f"### 📘 {row['단원 제목']}")
            st.markdown(f"📝 **요약:** {row['요약 (100자 이내)']}")
            
            # 키워드 처리 (안전하게)
            try:
                keywords = eval(row['키워드']) if isinstance(row['키워드'], str) else row['키워드']
                if isinstance(keywords, list):
                    keyword_str = ', '.join(keywords)
                else:
                    keyword_str = str(keywords)
                st.markdown(f"🏷️ **키워드:** `{keyword_str}`")
            except:
                st.markdown(f"🏷️ **키워드:** `{row['키워드']}`")
            
            # 관련 주제 표시
            related_topic = get_related_keywords(row['단원 제목'])
            st.markdown(f"🎯 **주제:** {related_topic}")
            
            # 버튼들을 같은 행에 배치
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                # GPT 요약 버튼
                if st.button(f"🧠 GPT 요약", key=f"gpt_{idx}"):
                    st.success(f"📋 **AI 요약 결과:**\n{row['요약 (100자 이내)']}")
            
            with col_btn2:
                # 즐겨찾기 추가
                fav = st.checkbox("⭐ 즐겨찾기", value=row["즐겨찾기"], key=f"fav_{idx}")
                df.at[idx, "즐겨찾기"] = fav
    
    st.markdown("---")

# -------------------
# ⭐ 즐겨찾기 섹션
# -------------------
st.subheader("⭐ 즐겨찾기한 단원")
fav_df = df[df["즐겨찾기"] == True]

if not fav_df.empty:
    st.dataframe(fav_df[["단원 제목", "요약 (100자 이내)", "키워드"]])
else:
    st.info("즐겨찾기한 단원이 없습니다.")
