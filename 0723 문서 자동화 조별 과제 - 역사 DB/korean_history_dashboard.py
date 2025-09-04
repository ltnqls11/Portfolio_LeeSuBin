import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

# ------------------
# 🖼️ 이미지 관련 함수
# ------------------
def get_history_image_url(keyword):
    """키워드를 기반으로 한국사 관련 이미지 URL을 생성합니다."""
    image_mapping = {
        "고조선": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Goguryeo_tomb_mural.jpg/300px-Goguryeo_tomb_mural.jpg",
        "구석기": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Stone_tools_Korea.jpg/300px-Stone_tools_Korea.jpg",
        "신석기": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Cheomseongdae.jpg/300px-Cheomseongdae.jpg",
        "청동기": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Baekje_gilt-bronze_incense_burner.jpg/300px-Baekje_gilt-bronze_incense_burner.jpg",
        "철기": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Goryeo_celadon.jpg/300px-Goryeo_celadon.jpg",
        "부여": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Goguryeo_tomb_mural.jpg/300px-Goguryeo_tomb_mural.jpg",
        "고구려": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Goguryeo_tomb_mural.jpg/300px-Goguryeo_tomb_mural.jpg",
        "백제": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Baekje_gilt-bronze_incense_burner.jpg/300px-Baekje_gilt-bronze_incense_burner.jpg",
        "신라": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Cheomseongdae.jpg/300px-Cheomseongdae.jpg",
        "발해": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Goryeo_celadon.jpg/300px-Goryeo_celadon.jpg",
        "통일신라": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Cheomseongdae.jpg/300px-Cheomseongdae.jpg",
        "조선": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Gyeongbokgung_Palace.jpg/300px-Gyeongbokgung_Palace.jpg",
        "세종": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/King_Sejong_the_Great.jpg/300px-King_Sejong_the_Great.jpg",
        "이순신": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Yi_Sun-sin.jpg/300px-Yi_Sun-sin.jpg",
        "임진왜란": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Japanese_invasion_of_Korea_1592-1598.png/300px-Japanese_invasion_of_Korea_1592-1598.png",
        "일제강점기": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Japanese_Government_General_of_Korea.jpg/300px-Japanese_Government_General_of_Korea.jpg",
        "독립운동": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/March_1st_Movement_1919.jpg/300px-March_1st_Movement_1919.jpg",
        "3.1운동": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/March_1st_Movement_1919.jpg/300px-March_1st_Movement_1919.jpg",
        "대한제국": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Liberation_of_Korea_1945.jpg/300px-Liberation_of_Korea_1945.jpg"
    }
    
    for key, url in image_mapping.items():
        if key in keyword:
            return url
    
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Gyeongbokgung_Palace.jpg/300px-Gyeongbokgung_Palace.jpg"

# ------------------
# 📦 데이터 생성 및 로드
# ------------------
def create_sample_data():
    """test2.py의 데이터를 기반으로 샘플 데이터를 생성합니다."""
    
    # 고대~연맹왕국 데이터
    ancient_data = [
        {"시대": "고조선", "분류": "건국", "내용": "고조선 건국(선민사상): 8조법. 왕위세습, 관직 설치", "인물": "단군", "사건유형": "건국/멸망", "연도": -2333},
        {"시대": "구석기", "분류": "도구", "내용": "뗀석기, 사냥도구 주먹도끼, 찍개, 찌르개, 팔매돌", "인물": "", "사건유형": "문화/기술", "연도": -50000},
        {"시대": "구석기", "분류": "경제", "내용": "열매 채집, 사냥, 물고기 잡이", "인물": "", "사건유형": "경제", "연도": -50000},
        {"시대": "구석기", "분류": "사회", "내용": "계급이 없는 평등사회", "인물": "", "사건유형": "사회", "연도": -50000},
        {"시대": "신석기", "분류": "도구", "내용": "간석기(돌보습, 돌화살촉 등), 석기(반달 돌칼 등 생활도구와 농기구)", "인물": "", "사건유형": "문화/기술", "연도": -8000},
        {"시대": "신석기", "분류": "경제", "내용": "농경과 목축 시작(신석기 혁명): 가축 사육. 조·피·수수 등 잡곡류 경작", "인물": "", "사건유형": "경제", "연도": -8000},
        {"시대": "청동기", "분류": "도구", "내용": "청동기(비파형동검. 거친무늬 거울 등)", "인물": "", "사건유형": "문화/기술", "연도": -1500},
        {"시대": "청동기", "분류": "사회", "내용": "계급의 분화 군장 출현, 성 역할 분리, 장인 출현, 사유재산 제도", "인물": "", "사건유형": "사회", "연도": -1500},
        {"시대": "철기", "분류": "사회", "내용": "연맹왕국의 등장 (부여, 고구려, 옥저, 동예, 삼한)", "인물": "", "사건유형": "정치/제도", "연도": -300}
    ]
    
    # 연맹왕국 데이터
    confederated_data = [
        {"시대": "부여", "분류": "정치", "내용": "5부족 연맹 왕국, 5부제 but 왕권미약", "인물": "", "사건유형": "정치/제도", "연도": -100},
        {"시대": "고구려", "분류": "정치", "내용": "5부족 연맹 왕국, 상가, 고추가 등 대가를 둠", "인물": "주몽", "사건유형": "정치/제도", "연도": 37},
        {"시대": "옥저", "분류": "정치", "내용": "왕이 없이 군장(읍군 삼로)이 부족을 통치", "인물": "", "사건유형": "정치/제도", "연도": -100},
        {"시대": "동예", "분류": "정치", "내용": "군장(견지 신지>부례읍차)이 소국 통치", "인물": "", "사건유형": "정치/제도", "연도": -100},
        {"시대": "삼한", "분류": "정치", "내용": "마한(54개국), 변한(12개국), 진한의 연맹체가 등장", "인물": "", "사건유형": "정치/제도", "연도": -200}
    ]
    
    # 삼국시대 데이터
    three_kingdoms_data = [
        {"시대": "삼국시대", "분류": "고구려", "내용": "태조: 옥저·동예 정복, 요동 진출", "인물": "태조", "사건유형": "전쟁/군사", "연도": 53},
        {"시대": "삼국시대", "분류": "고구려", "내용": "광개토대왕: 영락 연호, 한강이북과 요동·만주 장악", "인물": "광개토대왕", "사건유형": "전쟁/군사", "연도": 391},
        {"시대": "삼국시대", "분류": "백제", "내용": "근초고왕: 부자상속, 마한 통합, 평양 공격", "인물": "근초고왕", "사건유형": "전쟁/군사", "연도": 346},
        {"시대": "삼국시대", "분류": "신라", "내용": "법흥왕: 건원 연호, 율령 반포, 골품제 정비, 불교 공인", "인물": "법흥왕, 이차돈", "사건유형": "정치/제도", "연도": 514},
        {"시대": "통일신라", "분류": "통일", "내용": "문무왕: 통일신라(676), 나당 전쟁 승리", "인물": "문무왕", "사건유형": "전쟁/군사", "연도": 676},
        {"시대": "발해", "분류": "건국", "내용": "고왕: 돌궐 연합, 당 견제, 고구려 유민과 말갈족 통합", "인물": "고왕", "사건유형": "건국/멸망", "연도": 698}
    ]
    
    # 조선시대 데이터
    joseon_data = [
        {"시대": "조선", "분류": "태조", "내용": "조선경국전, 경제문감 민본적 통치 규범 마련", "인물": "이성계, 정도전", "사건유형": "정치/제도", "연도": 1392},
        {"시대": "조선", "분류": "태종", "내용": "6조 직계제, 사간원 독립, 사병제 폐지", "인물": "이방원", "사건유형": "정치/제도", "연도": 1400},
        {"시대": "조선", "분류": "세종", "내용": "의정부 서사제, 집현전 설치, 경연 활성화, 훈민정음", "인물": "세종", "사건유형": "문화/교육", "연도": 1418},
        {"시대": "조선", "분류": "세조", "내용": "6조 직계제, 집현전 폐지, 경연 폐지, 계유정난", "인물": "세조", "사건유형": "정치/제도", "연도": 1455},
        {"시대": "조선", "분류": "선조", "내용": "임진왜란(1592): 옥포, 한산도/정유재란: 명량, 노량", "인물": "선조, 이순신", "사건유형": "전쟁/군사", "연도": 1592},
        {"시대": "조선", "분류": "영조", "내용": "탕평책 실시, 탕평비, 신문고, 형벌 완화", "인물": "영조", "사건유형": "정치/제도", "연도": 1724},
        {"시대": "조선", "분류": "정조", "내용": "규장각, 장용영(친위부대), 초계문신제", "인물": "정조", "사건유형": "정치/제도", "연도": 1776}
    ]
    
    # 근현대사 데이터
    modern_data = [
        {"시대": "대한제국", "분류": "병인양요", "내용": "프랑스의 강화도 침략, 외규장각 약탈", "인물": "한성근, 양헌수", "사건유형": "전쟁/군사", "연도": 1866},
        {"시대": "대한제국", "분류": "강화도조약", "내용": "조·일 수호 조규, 최초의 근대적 조약", "인물": "김기수", "사건유형": "정치/제도", "연도": 1876},
        {"시대": "대한제국", "분류": "갑신정변", "내용": "김옥균 차관 도입 실패, 일본 공사관 지원 약속", "인물": "김옥균", "사건유형": "정치/제도", "연도": 1884},
        {"시대": "대한제국", "분류": "동학농민운동", "내용": "고부농민봉기, 조병갑의 만석보 수세 징수", "인물": "전봉준", "사건유형": "사회운동", "연도": 1894},
        {"시대": "일제강점기", "분류": "3.1운동", "내용": "전국적인 독립만세운동 전개", "인물": "손병희, 이승훈", "사건유형": "독립운동", "연도": 1919},
        {"시대": "일제강점기", "분류": "임시정부", "내용": "연해주 대한국민의회 + 서울 한성정부 + 상하이 임시정부", "인물": "이승만, 김구", "사건유형": "독립운동", "연도": 1919},
        {"시대": "일제강점기", "분류": "의열단", "내용": "김원봉의 의열단 조직과 독립운동", "인물": "김원봉", "사건유형": "독립운동", "연도": 1919},
        {"시대": "일제강점기", "분류": "한인애국단", "내용": "이봉창 일왕에 폭탄, 윤봉길 홍커우 공원에 폭탄", "인물": "김구, 이봉창, 윤봉길", "사건유형": "독립운동", "연도": 1932}
    ]
    
    # 모든 데이터 통합
    all_data = ancient_data + confederated_data + three_kingdoms_data + joseon_data + modern_data
    
    return pd.DataFrame(all_data)

@st.cache_data
def load_data():
    """데이터를 로드합니다."""
    return create_sample_data()

def extract_people_from_text(text):
    """텍스트에서 인물명을 추출합니다."""
    if pd.isna(text):
        return ""
    
    # 주요 역사 인물들
    famous_people = [
        "단군", "태조", "태종", "세종", "세조", "성종", "연산군", "중종", "인종", "명종", 
        "선조", "광해군", "인조", "숙종", "영조", "정조", "순조", "헌종", "철종", "고종",
        "이성계", "이방원", "이도", "수양대군", "조광조", "이황", "이이", "허준",
        "이순신", "원효", "의상", "최치원", "김유신", "연개소문", "을지문덕", "양만춘",
        "김구", "안중근", "윤봉길", "이봉창", "김좌진", "홍범도", "신돌석", "전봉준",
        "방정환", "김종직", "정도전", "김홍집", "박영효", "서재필", "안창호", "이승만",
        "광개토대왕", "근초고왕", "법흥왕", "이차돈", "문무왕", "고왕", "주몽",
        "김옥균", "손병희", "이승훈", "김원봉", "한성근", "양헌수", "김기수"
    ]
    
    found_people = []
    text_str = str(text).lower()
    
    for person in famous_people:
        if person in text_str:
            found_people.append(person)
    
    return ", ".join(list(set(found_people)))

# ------------------
# 📊 시각화 함수
# ------------------
def create_timeline_chart(df):
    """시대별 사건 분포 차트를 생성합니다."""
    fig = go.Figure()
    
    # 시대별 사건 수 계산
    era_counts = df['시대'].value_counts()
    
    fig.add_trace(go.Bar(
        x=era_counts.index,
        y=era_counts.values,
        marker_color='lightblue',
        text=era_counts.values,
        textposition='auto',
    ))
    
    fig.update_layout(
        title='시대별 사건 분포',
        xaxis_title='시대',
        yaxis_title='사건 수',
        showlegend=False
    )
    
    return fig

def create_event_type_pie_chart(df):
    """사건 유형별 분포 파이 차트를 생성합니다."""
    event_counts = df['사건유형'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=event_counts.index,
        values=event_counts.values,
        hole=0.3
    )])
    
    fig.update_layout(
        title='사건 유형별 분포',
        showlegend=True
    )
    
    return fig

def create_people_chart(df):
    """주요 인물 언급 빈도 차트를 생성합니다."""
    all_people = []
    for people_str in df['인물']:
        if people_str:
            people_list = [p.strip() for p in people_str.split(",")]
            all_people.extend(people_list)
    
    if all_people:
        people_counter = Counter(all_people)
        top_people = dict(people_counter.most_common(10))
        
        fig = go.Figure(data=[go.Bar(
            x=list(top_people.keys()),
            y=list(top_people.values()),
            marker_color='lightgreen'
        )])
        
        fig.update_layout(
            title='주요 인물 언급 빈도 (상위 10명)',
            xaxis_title='인물',
            yaxis_title='언급 횟수',
            xaxis_tickangle=-45
        )
        
        return fig
    
    return None

# ------------------
# 🎨 메인 UI
# ------------------
def main():
    st.set_page_config(
        page_title="한국사 종합 대시보드",
        page_icon="📜",
        layout="wide"
    )
    
    st.title("📜 한국사 종합 대시보드")
    st.markdown("**고대부터 근현대까지 한국사의 모든 것을 한눈에!**")
    st.markdown("---")
    
    # 데이터 로드
    df = load_data()
    
    if df.empty:
        st.error("데이터를 로드할 수 없습니다.")
        st.stop()
    
    # 사이드바 필터
    st.sidebar.header("🔎 필터 설정")
    
    # 1. 시대별 필터
    st.sidebar.subheader("🏛️ 시대별 필터")
    unique_eras = ["전체"] + sorted(df['시대'].unique().tolist())
    selected_era = st.sidebar.selectbox("시대를 선택하세요:", unique_eras)
    
    # 2. 인물별 필터
    st.sidebar.subheader("👤 인물별 필터")
    all_people = []
    for people_str in df['인물']:
        if people_str:
            people_list = [p.strip() for p in people_str.split(",")]
            all_people.extend(people_list)
    
    unique_people = ["전체"] + sorted(list(set([p for p in all_people if p])))
    selected_person = st.sidebar.selectbox("인물을 선택하세요:", unique_people)
    
    # 3. 사건 유형별 필터
    st.sidebar.subheader("⚔️ 사건 유형별 필터")
    unique_events = ["전체"] + sorted(df['사건유형'].unique().tolist())
    selected_event = st.sidebar.selectbox("사건 유형을 선택하세요:", unique_events)
    
    # 4. 키워드 검색
    st.sidebar.subheader("🔍 키워드 검색")
    search_keyword = st.sidebar.text_input("키워드를 입력하세요:")
    
    # 필터 적용
    filtered_df = df.copy()
    
    if selected_era != "전체":
        filtered_df = filtered_df[filtered_df['시대'] == selected_era]
    
    if selected_person != "전체":
        filtered_df = filtered_df[filtered_df['인물'].str.contains(selected_person, case=False, na=False)]
    
    if selected_event != "전체":
        filtered_df = filtered_df[filtered_df['사건유형'] == selected_event]
    
    if search_keyword:
        mask = (
            filtered_df['내용'].str.contains(search_keyword, case=False, na=False) |
            filtered_df['분류'].str.contains(search_keyword, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # 결과 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔍 검색된 기록", len(filtered_df))
    with col2:
        st.metric("📚 전체 기록", len(df))
    with col3:
        st.metric("📊 필터 적용률", f"{len(filtered_df)/len(df)*100:.1f}%")
    
    # 현재 적용된 필터 표시
    filter_info = []
    if selected_era != "전체":
        filter_info.append(f"🏛️ 시대: {selected_era}")
    if selected_person != "전체":
        filter_info.append(f"👤 인물: {selected_person}")
    if selected_event != "전체":
        filter_info.append(f"⚔️ 사건유형: {selected_event}")
    if search_keyword:
        filter_info.append(f"🔍 키워드: '{search_keyword}'")
    
    if filter_info:
        st.info("**적용된 필터:** " + " | ".join(filter_info))
    
    st.markdown("---")
    
    # 탭으로 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📋 상세 기록", "📊 통계 분석", "🖼️ 시각화", "📈 타임라인"])
    
    with tab1:
        st.subheader("📋 상세 역사 기록")
        
        if filtered_df.empty:
            st.warning("⚠️ 검색 조건에 맞는 기록이 없습니다.")
        else:
            for idx, row in filtered_df.iterrows():
                with st.expander(f"📘 {row['분류']} - {row['시대']}", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        # 관련 이미지 표시
                        try:
                            keyword = row['시대']
                            image_url = get_history_image_url(keyword)
                            st.image(image_url, caption=f"📸 {keyword}", width=200)
                        except:
                            st.info("🖼️ 이미지 없음")
                    
                    with col2:
                        st.markdown(f"**🏛️ 시대:** {row['시대']}")
                        st.markdown(f"**📅 연도:** {row['연도']}년" if row['연도'] > 0 else "**📅 연도:** 기원전")
                        
                        if row['인물']:
                            st.markdown(f"**👤 관련 인물:** {row['인물']}")
                        
                        st.markdown(f"**⚔️ 사건 유형:** {row['사건유형']}")
                        st.markdown(f"**📝 내용:** {row['내용']}")
    
    with tab2:
        st.subheader("📊 통계 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏛️ 시대별 분포")
            era_stats = filtered_df['시대'].value_counts()
            st.bar_chart(era_stats)
        
        with col2:
            st.markdown("#### ⚔️ 사건 유형별 분포")
            event_stats = filtered_df['사건유형'].value_counts()
            st.bar_chart(event_stats)
        
        # 상위 인물 통계
        st.markdown("#### 👤 주요 인물 언급 빈도")
        all_people_in_filtered = []
        for people_str in filtered_df['인물']:
            if people_str:
                people_list = [p.strip() for p in people_str.split(",")]
                all_people_in_filtered.extend(people_list)
        
        if all_people_in_filtered:
            people_counter = Counter(all_people_in_filtered)
            top_people = dict(people_counter.most_common(10))
            st.bar_chart(top_people)
        else:
            st.info("선택된 기록에 인물 정보가 없습니다.")
    
    with tab3:
        st.subheader("🖼️ 시각화")
        
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 시대별 사건 분포")
                timeline_fig = create_timeline_chart(filtered_df)
                st.plotly_chart(timeline_fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 🥧 사건 유형별 분포")
                pie_fig = create_event_type_pie_chart(filtered_df)
                st.plotly_chart(pie_fig, use_container_width=True)
            
            # 인물 차트
            st.markdown("#### 👤 주요 인물 언급 빈도")
            people_fig = create_people_chart(filtered_df)
            if people_fig:
                st.plotly_chart(people_fig, use_container_width=True)
            else:
                st.info("인물 데이터가 없습니다.")
        else:
            st.warning("⚠️ 시각화할 데이터가 없습니다.")
    
    with tab4:
        st.subheader("📈 한국사 타임라인")
        
        # 연도순으로 정렬
        timeline_df = filtered_df[filtered_df['연도'] > -10000].sort_values('연도')
        
        if not timeline_df.empty:
            # 타임라인 시각화
            fig = go.Figure()
            
            for idx, row in timeline_df.iterrows():
                fig.add_trace(go.Scatter(
                    x=[row['연도']],
                    y=[row['시대']],
                    mode='markers+text',
                    text=row['분류'],
                    textposition="top center",
                    marker=dict(size=10, color='red'),
                    name=row['분류'],
                    showlegend=False
                ))
            
            fig.update_layout(
                title='한국사 타임라인',
                xaxis_title='연도',
                yaxis_title='시대',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 타임라인 테이블
            st.markdown("#### 📋 연대순 사건 목록")
            timeline_display = timeline_df[['연도', '시대', '분류', '인물', '내용']].copy()
            timeline_display['연도'] = timeline_display['연도'].apply(lambda x: f"{x}년" if x > 0 else f"기원전 {abs(x)}년")
            st.dataframe(timeline_display, use_container_width=True)
        else:
            st.warning("⚠️ 타임라인에 표시할 데이터가 없습니다.")

if __name__ == "__main__":
    main()