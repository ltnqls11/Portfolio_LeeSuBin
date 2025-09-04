# 1️⃣ 설치 (터미널에 입력)
# pip install streamlit pandas matplotlib openpyxl seaborn plotly

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os
import glob
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="수원시 부동산 분석 대시보드",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def load_sample_data():
    """샘플 데이터 로드 함수"""
    try:
        # 기존 CSV 파일 찾기
        csv_files = glob.glob('수원시_*_매매_전세_평균가_*.csv')
        if not csv_files:
            csv_files = glob.glob('수원시_1년_매매_전세_평균가.csv')
        
        if csv_files:
            latest_file = max(csv_files, key=os.path.getctime)
            df = pd.read_csv(latest_file, encoding='utf-8-sig')
            return df, latest_file
        else:
            return None, None
    except Exception as e:
        st.error(f"샘플 데이터 로드 오류: {e}")
        return None, None

def preprocess_data(df):
    """데이터 전처리 함수"""
    try:
        # 컬럼명 정리
        column_mapping = {
            '구': '구명',
            '월': '날짜',
            '매매 평균 (억원)': '매매 평균',
            '전세 평균 (억원)': '전세 평균'
        }
        df = df.rename(columns=column_mapping)
        
        # 필요한 컬럼 확인
        if '구명' not in df.columns and '구' in df.columns:
            df['구명'] = df['구']
        if '날짜' not in df.columns and '월' in df.columns:
            df['날짜'] = df['월']
        
        # 숫자 컬럼 변환
        df['매매 평균'] = pd.to_numeric(df['매매 평균'], errors='coerce')
        df['전세 평균'] = pd.to_numeric(df['전세 평균'], errors='coerce')
        
        # 날짜 형식 처리
        df['날짜'] = df['날짜'].astype(str)
        
        # 날짜를 YYYY-MM 형식으로 변환
        def format_date(date_str):
            try:
                if len(date_str) == 6 and date_str.isdigit():
                    year = date_str[:4]
                    month = date_str[4:6]
                    return f"{year}-{month}"
                elif '-' in date_str and len(date_str) == 7:
                    return date_str
                else:
                    return date_str
            except:
                return date_str
        
        df['날짜_표시'] = df['날짜'].apply(format_date)
        df = df.sort_values(['구명', '날짜'])
        
        # 전세가율 계산
        df['전세가율'] = (df['전세 평균'] / df['매매 평균'] * 100).fillna(0)
        
        return df
        
    except Exception as e:
        st.error(f"데이터 전처리 오류: {e}")
        return df

def create_price_trend_chart(df):
    """가격 추이 차트 생성"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('매매 가격 추이', '전세 가격 추이', '전세가율 추이', '구별 비교'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    # 1. 매매 가격 추이
    for i, gu in enumerate(df['구명'].unique()):
        gu_data = df[df['구명'] == gu]
        fig.add_trace(
            go.Scatter(x=gu_data['날짜_표시'], y=gu_data['매매 평균'],
                      mode='lines+markers', name=f'{gu} 매매',
                      line=dict(color=colors[i % len(colors)], width=2),
                      marker=dict(size=6)),
            row=1, col=1
        )
    
    # 2. 전세 가격 추이
    for i, gu in enumerate(df['구명'].unique()):
        gu_data = df[df['구명'] == gu]
        fig.add_trace(
            go.Scatter(x=gu_data['날짜_표시'], y=gu_data['전세 평균'],
                      mode='lines+markers', name=f'{gu} 전세',
                      line=dict(color=colors[i % len(colors)], width=2, dash='dash'),
                      marker=dict(size=6)),
            row=1, col=2
        )
    
    # 3. 전세가율 추이
    for i, gu in enumerate(df['구명'].unique()):
        gu_data = df[df['구명'] == gu]
        fig.add_trace(
            go.Scatter(x=gu_data['날짜_표시'], y=gu_data['전세가율'],
                      mode='lines+markers', name=f'{gu} 전세가율',
                      line=dict(color=colors[i % len(colors)], width=2),
                      marker=dict(size=6)),
            row=2, col=1
        )
    
    # 4. 최신 월 구별 비교
    latest_month = df['날짜'].max()
    latest_data = df[df['날짜'] == latest_month]
    
    fig.add_trace(
        go.Bar(x=latest_data['구명'], y=latest_data['매매 평균'],
               name='매매 평균', marker_color='#2E86AB'),
        row=2, col=2
    )
    fig.add_trace(
        go.Bar(x=latest_data['구명'], y=latest_data['전세 평균'],
               name='전세 평균', marker_color='#A23B72'),
        row=2, col=2
    )
    
    fig.update_layout(
        height=800,
        title_text="수원시 구별 부동산 가격 분석",
        title_x=0.5,
        showlegend=True
    )
    
    # Y축 레이블 설정
    fig.update_yaxes(title_text="가격 (억원)", row=1, col=1)
    fig.update_yaxes(title_text="가격 (억원)", row=1, col=2)
    fig.update_yaxes(title_text="전세가율 (%)", row=2, col=1)
    fig.update_yaxes(title_text="가격 (억원)", row=2, col=2)
    
    return fig

def create_heatmap(df):
    """히트맵 생성"""
    # 월별 변동률 계산
    df_pivot = df.pivot_table(
        index='구명', 
        columns='날짜_표시', 
        values='매매 평균', 
        aggfunc='mean'
    )
    
    # 변동률 계산
    change_rates = df_pivot.pct_change(axis=1) * 100
    
    fig = px.imshow(
        change_rates.fillna(0),
        labels=dict(x="월", y="구", color="변동률 (%)"),
        title="월별 매매가격 변동률 히트맵",
        color_continuous_scale="RdYlBu_r"
    )
    
    fig.update_layout(height=400)
    return fig

def main():
    """메인 함수"""
    # 제목
    st.title('🏠 수원시 부동산 분석 대시보드')
    st.markdown("---")
    
    # 사이드바
    st.sidebar.header("📊 데이터 설정")
    
    # 자동으로 특정 CSV 파일 로드
    target_csv = "수원시_1년_매매_전세_평균가_20250722.csv"
    
    df = None
    
    # 1. 먼저 지정된 파일 찾기
    if os.path.exists(target_csv):
        try:
            df = pd.read_csv(target_csv, encoding='utf-8-sig')
            st.sidebar.success(f"✅ 자동 로드 완료!")
            st.sidebar.info(f"📁 파일: {target_csv}")
        except Exception as e:
            st.sidebar.error(f"❌ 파일 읽기 오류: {e}")
    
    # 2. 지정된 파일이 없으면 다른 CSV 파일 찾기
    if df is None:
        df, sample_file = load_sample_data()
        if df is not None:
            st.sidebar.success(f"✅ 대체 파일 로드 완료!")
            st.sidebar.info(f"📁 파일: {os.path.basename(sample_file)}")
    
    # 3. 그래도 없으면 파일 업로드 옵션 제공
    if df is None:
        st.sidebar.warning("⚠️ CSV 파일을 찾을 수 없습니다.")
        st.sidebar.markdown("---")
        
        # 파일 업로드 옵션
        uploaded_file = st.sidebar.file_uploader(
            '📤 CSV 파일 업로드', 
            type=['csv'],
            help="수원시 부동산 데이터 CSV 파일을 업로드하세요."
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                st.sidebar.success("✅ 업로드 완료!")
            except Exception as e:
                st.sidebar.error(f"❌ 파일 읽기 오류: {e}")
        else:
            st.sidebar.info("""
            💡 **파일 준비 방법:**
            1. `test02_demo.py` 실행
            2. 또는 CSV 파일 직접 업로드
            """)
    
    if df is not None:
        # 데이터 전처리
        df = preprocess_data(df)
        
        # 기본 정보 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 총 데이터 수", len(df))
        with col2:
            st.metric("🏘️ 분석 지역", len(df['구명'].unique()))
        with col3:
            st.metric("📅 분석 기간", f"{df['날짜_표시'].min()} ~ {df['날짜_표시'].max()}")
        with col4:
            avg_price = df['매매 평균'].mean()
            st.metric("💰 평균 매매가", f"{avg_price:.2f}억원")
        
        st.markdown("---")
        
        # 탭 생성
        tab1, tab2, tab3, tab4 = st.tabs(["📈 가격 추이", "🔥 히트맵", "📊 상세 데이터", "📋 통계 요약"])
        
        with tab1:
            st.subheader("📈 구별 가격 추이 분석")
            
            # 구 선택
            selected_gu = st.multiselect(
                "분석할 구 선택:",
                df['구명'].unique(),
                default=df['구명'].unique()
            )
            
            if selected_gu:
                filtered_df = df[df['구명'].isin(selected_gu)]
                
                # Plotly 차트
                fig = create_price_trend_chart(filtered_df)
                st.plotly_chart(fig, use_container_width=True)
                
                # 개별 구 상세 차트
                st.subheader("🏘️ 구별 상세 분석")
                
                for gu in selected_gu:
                    with st.expander(f"{gu} 상세 분석"):
                        gu_data = df[df['구명'] == gu]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # 매매/전세 가격 차트
                            fig_price = go.Figure()
                            fig_price.add_trace(go.Scatter(
                                x=gu_data['날짜_표시'], 
                                y=gu_data['매매 평균'],
                                mode='lines+markers',
                                name='매매 평균',
                                line=dict(color='#2E86AB', width=3)
                            ))
                            fig_price.add_trace(go.Scatter(
                                x=gu_data['날짜_표시'], 
                                y=gu_data['전세 평균'],
                                mode='lines+markers',
                                name='전세 평균',
                                line=dict(color='#A23B72', width=3)
                            ))
                            fig_price.update_layout(
                                title=f"{gu} 가격 추이",
                                xaxis_title="월",
                                yaxis_title="가격 (억원)",
                                height=400
                            )
                            st.plotly_chart(fig_price, use_container_width=True)
                        
                        with col2:
                            # 전세가율 차트
                            fig_ratio = go.Figure()
                            fig_ratio.add_trace(go.Bar(
                                x=gu_data['날짜_표시'],
                                y=gu_data['전세가율'],
                                name='전세가율',
                                marker_color='#F18F01'
                            ))
                            fig_ratio.update_layout(
                                title=f"{gu} 전세가율",
                                xaxis_title="월",
                                yaxis_title="전세가율 (%)",
                                height=400
                            )
                            st.plotly_chart(fig_ratio, use_container_width=True)
                        
                        # 통계 정보
                        col3, col4, col5 = st.columns(3)
                        with col3:
                            st.metric("평균 매매가", f"{gu_data['매매 평균'].mean():.2f}억원")
                        with col4:
                            st.metric("평균 전세가", f"{gu_data['전세 평균'].mean():.2f}억원")
                        with col5:
                            st.metric("평균 전세가율", f"{gu_data['전세가율'].mean():.1f}%")
        
        with tab2:
            st.subheader("🔥 가격 변동 히트맵")
            
            # 히트맵 생성
            heatmap_fig = create_heatmap(df)
            st.plotly_chart(heatmap_fig, use_container_width=True)
            
            # 상관관계 히트맵
            st.subheader("📊 구별 가격 상관관계")
            pivot_df = df.pivot_table(
                index='날짜_표시',
                columns='구명',
                values='매매 평균',
                aggfunc='mean'
            )
            
            corr_matrix = pivot_df.corr()
            
            fig_corr = px.imshow(
                corr_matrix,
                labels=dict(color="상관계수"),
                title="구별 매매가격 상관관계",
                color_continuous_scale="RdYlBu"
            )
            fig_corr.update_layout(height=500)
            st.plotly_chart(fig_corr, use_container_width=True)
        
        with tab3:
            st.subheader("📊 상세 데이터")
            
            # 필터링 옵션
            col1, col2 = st.columns(2)
            with col1:
                filter_gu = st.multiselect(
                    "구 필터:",
                    df['구명'].unique(),
                    default=df['구명'].unique()
                )
            with col2:
                filter_months = st.multiselect(
                    "월 필터:",
                    sorted(df['날짜_표시'].unique()),
                    default=sorted(df['날짜_표시'].unique())
                )
            
            # 필터링된 데이터
            filtered_data = df[
                (df['구명'].isin(filter_gu)) & 
                (df['날짜_표시'].isin(filter_months))
            ]
            
            # 데이터 표시
            st.dataframe(
                filtered_data[['구명', '날짜_표시', '매매 평균', '전세 평균', '전세가율']],
                use_container_width=True
            )
            
            # 다운로드 버튼
            csv = filtered_data.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 필터링된 데이터 다운로드",
                data=csv,
                file_name=f'수원시_부동산_데이터_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv'
            )
        
        with tab4:
            st.subheader("📋 통계 요약")
            
            # 구별 통계
            stats_df = df.groupby('구명').agg({
                '매매 평균': ['mean', 'min', 'max', 'std'],
                '전세 평균': ['mean', 'min', 'max', 'std'],
                '전세가율': ['mean', 'min', 'max']
            }).round(2)
            
            st.subheader("🏘️ 구별 통계")
            st.dataframe(stats_df, use_container_width=True)
            
            # 월별 통계
            monthly_stats = df.groupby('날짜_표시').agg({
                '매매 평균': 'mean',
                '전세 평균': 'mean',
                '전세가율': 'mean'
            }).round(2)
            
            st.subheader("📅 월별 평균")
            st.line_chart(monthly_stats)
            
            # 최고가/최저가 정보
            st.subheader("💰 가격 순위")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**매매 최고가 TOP 5**")
                top_trade = df.nlargest(5, '매매 평균')[['구명', '날짜_표시', '매매 평균']]
                st.dataframe(top_trade, use_container_width=True)
            
            with col2:
                st.write("**전세 최고가 TOP 5**")
                top_rent = df.nlargest(5, '전세 평균')[['구명', '날짜_표시', '전세 평균']]
                st.dataframe(top_rent, use_container_width=True)
    
    else:
        # 데이터가 없는 경우
        st.warning("⚠️ 데이터를 로드해주세요.")
        st.info("""
        📋 **데이터 준비 방법:**
        1. **샘플 데이터 생성**: `test02_demo.py` 실행
        2. **파일 업로드**: CSV 파일을 직접 업로드
        
        🔧 **필요한 CSV 컬럼:**
        - 구명 (또는 구)
        - 날짜 (또는 월)
        - 매매 평균 (또는 매매 평균 (억원))
        - 전세 평균 (또는 전세 평균 (억원))
        """)

if __name__ == "__main__":
    main()