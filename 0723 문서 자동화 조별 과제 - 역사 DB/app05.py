import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 페이지 설정
st.set_page_config(
    page_title="한국사 주요 사건 대시보드",
    page_icon="📅",
    layout="wide"
)

def load_data():
    """CSV 데이터 로드"""
    try:
        csv_path = "korean_history_events.csv"
        if not os.path.exists(csv_path):
            st.error(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
            return None
        
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"❌ 데이터 로드 오류: {str(e)}")
        return None

def main():
    """메인 함수"""
    # 제목
    st.title("📅 한국사 주요 사건 대시보드")
    
    # 데이터 로드
    df = load_data()
    if df is None:
        return
    
    # 현재 날짜
    today = datetime.now().strftime("%m-%d")
    st.write(f"**오늘 날짜:** {today}")
    
    # 오늘 날짜와 매칭되는 사건 찾기
    df["is_today"] = df["date"] == today
    events_today = df[df["is_today"]]
    
    # 오늘의 사건 표시
    if not events_today.empty:
        st.subheader("✨ 오늘은 이런 일이 있었습니다!")
        for _, event in events_today.iterrows():
            st.success(f"**{event['event']}**: {event['description']}")
    else:
        st.info("오늘은 등록된 사건이 없습니다.")
    
    st.divider()
    
    # 전체 사건 목록
    st.subheader("🗂 전체 사건 목록")
    
    # 검색 기능
    search_term = st.text_input("🔍 사건 검색", placeholder="사건명이나 설명을 입력하세요...")
    
    # 필터링
    if search_term:
        filtered_df = df[
            df['event'].str.contains(search_term, case=False, na=False) |
            df['description'].str.contains(search_term, case=False, na=False)
        ]
    else:
        filtered_df = df
    
    # 데이터 표시
    if not filtered_df.empty:
        # 오늘 날짜 하이라이트를 위한 스타일링
        def highlight_today(row):
            if row['is_today']:
                return ['background-color: #fffae6'] * len(row)
            return [''] * len(row)
        
        # 표시할 컬럼 선택
        display_df = filtered_df[['event', 'date', 'description']].copy()
        display_df.columns = ['사건', '날짜', '설명']
        
        # 스타일 적용하여 표시
        styled_df = display_df.style.apply(
            lambda row: highlight_today(filtered_df.iloc[row.name]), 
            axis=1
        )
        
        st.dataframe(styled_df, use_container_width=True)
        
        # 통계 정보
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("전체 사건 수", len(df))
        with col2:
            st.metric("검색 결과", len(filtered_df))
        with col3:
            st.metric("오늘의 사건", len(events_today))
    else:
        st.warning("검색 결과가 없습니다.")
    
    # 사이드바에 추가 정보
    with st.sidebar:
        st.header("📊 대시보드 정보")
        st.write("한국사의 주요 사건들을 날짜별로 확인할 수 있습니다.")
        
        st.subheader("🎯 기능")
        st.write("- 오늘 날짜의 역사적 사건 확인")
        st.write("- 전체 사건 목록 조회")
        st.write("- 사건 검색 기능")
        st.write("- 오늘 날짜 하이라이트")
        
        st.subheader("📈 데이터 현황")
        if df is not None:
            st.write(f"총 사건 수: {len(df)}개")
            st.write(f"오늘의 사건: {len(events_today)}개")
            
            # 월별 사건 분포
            df['month'] = df['date'].str[:2]
            month_counts = df['month'].value_counts().sort_index()
            st.bar_chart(month_counts)

if __name__ == "__main__":
    main()