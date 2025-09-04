import streamlit as st
import pandas as pd

# CSV 파일 경로
CSV_FILE_PATH = 'history1.csv'

def extract_people_from_text(text):
    """텍스트에서 주요 인물들을 추출합니다."""
    if pd.isna(text):
        return []
    
    # 주요 역사 인물들 목록
    famous_people = [
        "세종", "세종대왕", "이순신", "정조", "영조", "태종", "태조", "선조", "고종", "순종",
        "방정환", "김종직", "전봉준", "안중근", "윤봉길", "김구", "이승만", "박정희", 
        "김대중", "노무현", "문재인", "임연", "세자", "왕", "대왕", "지학순", "홍석현", 
        "김영란", "최종영", "이현세", "이태복", "정철", "김일기", "김의지", "유지", 
        "윤사윤", "정괄", "성준", "동청례", "이산옥", "양호", "유상운", "신익상",
        "남구만", "민진장", "정무서", "박윤", "권엄", "민종현", "이의준", "이서구",
        "성대중", "윤형지", "윤황", "남이익", "이응준", "한용귀", "남공철", "임한호"
    ]
    
    found_people = []
    text_str = str(text).lower()
    
    for person in famous_people:
        if person.lower() in text_str:
            found_people.append(person)
    
    return list(set(found_people))  # 중복 제거

def classify_theme(row):
    """제목과 내용을 기반으로 테마를 분류합니다."""
    title = str(row.get("제목", "")).lower()
    content = str(row.get("내용", "")).lower()
    text = title + " " + content
    
    if any(word in text for word in ["전쟁", "전투", "해전", "침입", "방어", "군사", "적병", "왜군", "몽고"]):
        return "전쟁"
    elif any(word in text for word in ["문화", "학교", "교육", "서원", "책", "문학", "예술", "훈민정음", "농사직설"]):
        return "문화/교육"
    elif any(word in text for word in ["정치", "왕", "즉위", "정부", "조약", "법", "제도", "관직", "임명"]):
        return "정치"
    elif any(word in text for word in ["경제", "세금", "농업", "상업", "무역", "화폐", "대동미", "공삼"]):
        return "경제"
    elif any(word in text for word in ["사회", "민중", "농민", "운동", "시위", "봉기", "학생", "유생"]):
        return "사회운동"
    elif any(word in text for word in ["독립", "항일", "저항", "해방", "광복", "척화", "만세"]):
        return "독립운동"
    elif any(word in text for word in ["재해", "홍수", "지진", "화재", "사고", "수재", "침몰", "압사", "익사"]):
        return "재해/사고"
    elif any(word in text for word in ["종교", "불교", "유교", "기독교", "사찰", "교회", "부도", "사리"]):
        return "종교"
    else:
        return "기타"

def load_data():
    """CSV 파일을 로드하고 필요한 전처리를 수행합니다."""
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        # 필요한 컬럼이 있는지 확인
        required_columns = ['날짜', '시대', '제목', '내용', '링크']
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV 파일에 필요한 컬럼(날짜, 시대, 제목, 내용, 링크) 중 일부가 누락되었습니다. 현재 컬럼: {df.columns.tolist()}")
            return pd.DataFrame() # 빈 DataFrame 반환
        
        # 인물과 테마 정보 추가
        df["인물"] = df.apply(lambda row: extract_people_from_text(row["제목"] + " " + row["내용"]), axis=1)
        df["테마"] = df.apply(classify_theme, axis=1)
        
        return df
    except FileNotFoundError:
        st.error(f"파일을 찾을 수 없습니다: {CSV_FILE_PATH}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"파일 로드 중 오류 발생: {e}")
        return pd.DataFrame()

def main():
    st.set_page_config(layout="wide")
    st.title("📜 역사 자료 대시보드")

    df = load_data()

    if df.empty:
        st.stop()

    # 사이드바 필터
    st.sidebar.header("🔎 필터 설정")
    
    # 1. 시대별 필터
    st.sidebar.subheader("🏛️ 시대별 필터")
    eras = ["모두 보기"] + sorted(df['시대'].unique().tolist())
    selected_era = st.sidebar.selectbox("시대를 선택하세요:", eras)

    # 2. 인물별 필터
    st.sidebar.subheader("👤 인물별 필터")
    # 모든 인물 목록 생성
    all_people = []
    for people_list in df['인물']:
        if isinstance(people_list, list):
            all_people.extend(people_list)
    
    unique_people = ["모두 보기"] + sorted(list(set(all_people)))
    selected_person = st.sidebar.selectbox("특정 인물을 선택하세요:", unique_people)

    # 3. 테마별 필터
    st.sidebar.subheader("🎯 테마별 필터")
    themes = ["모두 보기"] + sorted(df['테마'].unique().tolist())
    selected_theme = st.sidebar.selectbox("테마를 선택하세요:", themes)

    # 4. 키워드 검색
    st.sidebar.subheader("🔍 키워드 검색")
    search_keyword = st.sidebar.text_input("키워드를 입력하세요:")

    # 데이터 필터링
    filtered_df = df.copy()
    
    # 시대 필터 적용
    if selected_era != "모두 보기":
        filtered_df = filtered_df[filtered_df['시대'] == selected_era]
    
    # 인물 필터 적용
    if selected_person != "모두 보기":
        filtered_df = filtered_df[filtered_df['인물'].apply(lambda x: selected_person in x if isinstance(x, list) else False)]
    
    # 테마 필터 적용
    if selected_theme != "모두 보기":
        filtered_df = filtered_df[filtered_df['테마'] == selected_theme]
    
    # 키워드 검색 적용
    if search_keyword:
        mask = (
            filtered_df['제목'].str.contains(search_keyword, case=False, na=False) |
            filtered_df['내용'].str.contains(search_keyword, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    # 필터링 결과 표시
    st.info(f"🔍 총 {len(filtered_df)}개의 기록이 검색되었습니다. (전체 {len(df)}개 중)")
    
    # 현재 적용된 필터 표시
    filter_info = []
    if selected_era != "모두 보기":
        filter_info.append(f"🏛️ 시대: {selected_era}")
    if selected_person != "모두 보기":
        filter_info.append(f"👤 인물: {selected_person}")
    if selected_theme != "모두 보기":
        filter_info.append(f"🎯 테마: {selected_theme}")
    if search_keyword:
        filter_info.append(f"🔍 키워드: '{search_keyword}'")
    
    if filter_info:
        st.markdown("**적용된 필터:** " + " | ".join(filter_info))

    st.markdown("---")

    if filtered_df.empty:
        st.warning("⚠️ 검색 조건에 맞는 자료가 없습니다. 필터를 조정해보세요.")
    else:
        # 각 항목을 카드 형태로 표시
        for index, row in filtered_df.iterrows():
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### {row['제목']}")
                    st.write(f"📅 **날짜:** {row['날짜']}")
                    st.write(f"🏛️ **시대:** {row['시대']}")
                    
                    # 인물 정보 표시
                    if isinstance(row['인물'], list) and row['인물']:
                        people_str = ", ".join(row['인물'])
                        st.write(f"👤 **관련 인물:** {people_str}")
                    
                    # 테마 정보 표시
                    st.write(f"🎯 **테마:** {row['테마']}")
                    
                    st.write(f"📝 **내용:** {row['내용']}")
                    st.markdown(f"🔗 [자세히 보기]({row['링크']})")
                
                with col2:
                    # Gemini 요약 버튼 (기능 미구현)
                    if st.button("🤖 Gemini 요약", key=f"summarize_btn_{index}"):
                        st.info("이 기능은 Gemini API 연동이 필요합니다. 현재는 플레이스홀더입니다.")
                        # 여기에 Gemini API 호출 로직이 들어갈 수 있습니다.
                        # 예: summary = call_gemini_api(row['내용'])
                        # st.write(f"**요약:** {summary}")
                
                st.markdown("---")  # 구분선

if __name__ == "__main__":
    main()
