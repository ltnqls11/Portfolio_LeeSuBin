# 필수 라이브러리
# pip install pandas matplotlib openpyxl seaborn

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os
import glob
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정 강화
def setup_korean_font():
    """한글 폰트 설정 함수"""
    plt.rcParams.update({
        'font.family': ['Malgun Gothic', 'Microsoft YaHei', 'SimHei', 'sans-serif'],
        'axes.unicode_minus': False,
        'font.size': 11,
        'figure.titlesize': 16,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'legend.fontsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10
    })
    print("✅ 한글 폰트 설정 완료")

# 한글 폰트 설정 실행
setup_korean_font()

def find_csv_file():
    """최신 CSV 파일을 찾는 함수"""
    csv_files = glob.glob('수원시_*_매매_전세_평균가_*.csv')
    if not csv_files:
        csv_files = glob.glob('수원시_1년_매매_전세_평균가.csv')
    
    if not csv_files:
        raise FileNotFoundError("CSV 파일을 찾을 수 없습니다. test02.py 또는 test02_demo.py를 먼저 실행하세요.")
    
    # 가장 최신 파일 선택
    latest_file = max(csv_files, key=os.path.getctime)
    print(f"사용할 CSV 파일: {latest_file}")
    return latest_file

def load_and_prepare_data(file_path):
    """데이터 로드 및 전처리"""
    try:
        # CSV 불러오기
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"데이터 로드 완료: {len(df)}행")
        
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
        
        # 날짜 형식 처리 및 정리
        df['날짜'] = df['날짜'].astype(str)
        
        # 날짜 형식 확인 및 변환
        print(f"원본 날짜 형식 샘플: {df['날짜'].head().tolist()}")
        
        # 날짜를 YYYY-MM 형식으로 변환
        def format_date(date_str):
            try:
                # YYYYMM 형식인 경우 (예: 202408)
                if len(date_str) == 6 and date_str.isdigit():
                    year = date_str[:4]
                    month = date_str[4:6]
                    return f"{year}-{month}"
                # 이미 YYYY-MM 형식인 경우
                elif '-' in date_str and len(date_str) == 7:
                    return date_str
                # 기타 형식 처리
                else:
                    return date_str
            except:
                return date_str
        
        df['날짜_표시'] = df['날짜'].apply(format_date)
        
        # 날짜 정렬 (원본 날짜 기준)
        df = df.sort_values(['구명', '날짜'])
        
        print(f"변환된 날짜 형식 샘플: {df['날짜_표시'].head().tolist()}")
        print(f"구별 데이터 수: {df['구명'].value_counts().to_dict()}")
        print(f"분석 기간: {df['날짜_표시'].min()} ~ {df['날짜_표시'].max()}")
        
        return df
        
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        raise

def create_individual_charts(df):
    """구별 개별 차트 생성"""
    gu_list = df['구명'].unique()
    chart_files = []
    
    print(f"\n=== 구별 개별 차트 생성 ({len(gu_list)}개) ===")
    
    for gu in gu_list:
        data = df[df['구명'] == gu].copy()
        
        if data.empty:
            print(f"{gu}: 데이터 없음")
            continue
        
        # 날짜 정렬 및 데이터 정리
        data = data.sort_values('날짜').reset_index(drop=True)
        
        # 서브플롯 생성 (중복 plt.figure 제거)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
        
        # 상단: 가격 추이 (데이터 유효성 검사 추가)
        valid_trade = data['매매 평균'].dropna()
        valid_rent = data['전세 평균'].dropna()
        
        if not valid_trade.empty:
            ax1.plot(data['날짜_표시'], data['매매 평균'], marker='o', linewidth=3, 
                    markersize=8, label='매매 평균', color='#2E86AB', alpha=0.8)
        
        if not valid_rent.empty:
            ax1.plot(data['날짜_표시'], data['전세 평균'], marker='s', linewidth=3, 
                    markersize=8, label='전세 평균', color='#A23B72', alpha=0.8)
        
        ax1.set_title(f'{gu} 최근 1년 매매/전세 평균가 추이', fontsize=18, fontweight='bold', pad=25)
        ax1.set_xlabel('연월', fontsize=14)
        ax1.set_ylabel('금액 (억원)', fontsize=14)
        ax1.legend(fontsize=12, loc='upper left', frameon=True, fancybox=True, shadow=True)
        ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax1.tick_params(axis='x', rotation=45, labelsize=11)
        ax1.tick_params(axis='y', labelsize=11)
        
        # Y축 범위 설정 (더 보기 좋게)
        if not valid_trade.empty or not valid_rent.empty:
            all_prices = pd.concat([valid_trade, valid_rent])
            y_min = all_prices.min() * 0.9
            y_max = all_prices.max() * 1.1
            ax1.set_ylim(y_min, y_max)
        
        # 가격 범위 표시 (개선)
        if not valid_trade.empty:
            max_trade = valid_trade.max()
            min_trade = valid_trade.min()
            ax1.axhline(y=max_trade, color='#2E86AB', linestyle='--', alpha=0.6, linewidth=1)
            ax1.axhline(y=min_trade, color='#2E86AB', linestyle='--', alpha=0.6, linewidth=1)
            
            # 최고가/최저가 텍스트 표시
            ax1.text(0.02, 0.98, f'최고가: {max_trade:.2f}억원', transform=ax1.transAxes, 
                    fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
            ax1.text(0.02, 0.02, f'최저가: {min_trade:.2f}억원', transform=ax1.transAxes, 
                    fontsize=10, verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
        
        # 하단: 전세가율 및 가격 변동 분석
        if not data['매매 평균'].isna().all() and not data['전세 평균'].isna().all():
            # 전세가율 계산
            ratio = (data['전세 평균'] / data['매매 평균'] * 100).fillna(0)
            valid_ratio = ratio[ratio > 0]  # 0보다 큰 값만 사용
            
            if not valid_ratio.empty:
                # 막대 그래프 색상 그라데이션
                colors = plt.cm.viridis(np.linspace(0, 1, len(data)))
                bars = ax2.bar(data['날짜_표시'], ratio, color=colors, alpha=0.8, edgecolor='white', linewidth=0.5)
                
                ax2.set_title(f'{gu} 전세가율 추이 (전세/매매 × 100)', fontsize=16, fontweight='bold', pad=20)
                ax2.set_xlabel('연월', fontsize=14)
                ax2.set_ylabel('전세가율 (%)', fontsize=14)
                ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
                ax2.tick_params(axis='x', rotation=45, labelsize=11)
                ax2.tick_params(axis='y', labelsize=11)
                
                # 평균 전세가율 표시 (개선)
                avg_ratio = valid_ratio.mean()
                ax2.axhline(y=avg_ratio, color='red', linestyle='-', alpha=0.9, linewidth=2,
                           label=f'평균: {avg_ratio:.1f}%')
                
                # 전세가율 범위 설정
                y_min = max(0, valid_ratio.min() * 0.9)
                y_max = valid_ratio.max() * 1.1
                ax2.set_ylim(y_min, y_max)
                
                # 최고/최저 전세가율 표시
                max_ratio = valid_ratio.max()
                min_ratio = valid_ratio.min()
                ax2.text(0.98, 0.98, f'최고: {max_ratio:.1f}%', transform=ax2.transAxes, 
                        fontsize=10, verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
                ax2.text(0.98, 0.02, f'최저: {min_ratio:.1f}%', transform=ax2.transAxes, 
                        fontsize=10, verticalalignment='bottom', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
                
                ax2.legend(loc='upper left', fontsize=11, frameon=True, fancybox=True, shadow=True)
            else:
                # 데이터가 없는 경우
                ax2.text(0.5, 0.5, '전세가율 데이터 없음', transform=ax2.transAxes, 
                        fontsize=14, ha='center', va='center',
                        bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.7))
                ax2.set_title(f'{gu} 전세가율 데이터 없음', fontsize=16, fontweight='bold')
        else:
            # 매매/전세 데이터가 없는 경우
            ax2.text(0.5, 0.5, '가격 데이터 없음', transform=ax2.transAxes, 
                    fontsize=14, ha='center', va='center',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.7))
            ax2.set_title(f'{gu} 가격 데이터 없음', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        # 파일 저장
        filename = f'{gu}_최근1년_매매_전세_추이_{datetime.now().strftime("%Y%m%d")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        chart_files.append(filename)
        print(f"✅ {gu} 차트 저장: {filename}")
    
    return chart_files

def create_comparison_charts(df):
    """구별 비교 차트 생성"""
    print(f"\n=== 구별 비교 차트 생성 ===")
    
    # 전체 비교 차트
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('수원시 구별 부동산 가격 종합 분석', fontsize=18, fontweight='bold')
    
    # 1. 매매 가격 비교
    ax1 = axes[0, 0]
    for gu in df['구명'].unique():
        gu_data = df[df['구명'] == gu]
        ax1.plot(gu_data['날짜_표시'], gu_data['매매 평균'], marker='o', label=gu, linewidth=2)
    ax1.set_title('구별 매매 평균가 비교', fontsize=14, fontweight='bold')
    ax1.set_xlabel('연월')
    ax1.set_ylabel('매매 평균가 (억원)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. 전세 가격 비교
    ax2 = axes[0, 1]
    for gu in df['구명'].unique():
        gu_data = df[df['구명'] == gu]
        ax2.plot(gu_data['날짜_표시'], gu_data['전세 평균'], marker='s', label=gu, linewidth=2)
    ax2.set_title('구별 전세 평균가 비교', fontsize=14, fontweight='bold')
    ax2.set_xlabel('연월')
    ax2.set_ylabel('전세 평균가 (억원)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. 최신 월 가격 막대 그래프
    ax3 = axes[1, 0]
    latest_month = df['날짜'].max()
    latest_data = df[df['날짜'] == latest_month]
    
    x = np.arange(len(latest_data))
    width = 0.35
    
    ax3.bar(x - width/2, latest_data['매매 평균'], width, label='매매', color='#2E86AB')
    ax3.bar(x + width/2, latest_data['전세 평균'], width, label='전세', color='#A23B72')
    
    ax3.set_title(f'최신 월({latest_month}) 구별 가격 비교', fontsize=14, fontweight='bold')
    ax3.set_xlabel('구')
    ax3.set_ylabel('평균가 (억원)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(latest_data['구명'])
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 전세가율 비교
    ax4 = axes[1, 1]
    for gu in df['구명'].unique():
        gu_data = df[df['구명'] == gu].copy()
        if not gu_data['매매 평균'].isna().all() and not gu_data['전세 평균'].isna().all():
            ratio = (gu_data['전세 평균'] / gu_data['매매 평균'] * 100).fillna(0)
            ax4.plot(gu_data['날짜_표시'], ratio, marker='d', label=gu, linewidth=2)
    
    ax4.set_title('구별 전세가율 비교', fontsize=14, fontweight='bold')
    ax4.set_xlabel('연월')
    ax4.set_ylabel('전세가율 (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # 파일 저장
    comparison_filename = f'수원시_구별_종합비교_{datetime.now().strftime("%Y%m%d")}.png'
    plt.savefig(comparison_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 종합 비교 차트 저장: {comparison_filename}")
    return comparison_filename

def create_statistical_summary(df):
    """통계 요약 생성"""
    print(f"\n=== 통계 요약 생성 ===")
    
    # 구별 통계
    stats_summary = df.groupby('구명').agg({
        '매매 평균': ['mean', 'min', 'max', 'std'],
        '전세 평균': ['mean', 'min', 'max', 'std']
    }).round(2)
    
    # 전세가율 계산
    df_copy = df.copy()
    df_copy['전세가율'] = (df_copy['전세 평균'] / df_copy['매매 평균'] * 100).fillna(0)
    
    ratio_stats = df_copy.groupby('구명')['전세가율'].agg(['mean', 'min', 'max']).round(1)
    
    print("\n📊 구별 가격 통계 (억원)")
    print(stats_summary)
    
    print("\n📈 구별 전세가율 통계 (%)")
    print(ratio_stats)
    
    return stats_summary, ratio_stats

def main():
    """메인 실행 함수"""
    try:
        print("=== 수원시 부동산 시각화 분석 시작 ===")
        
        # 1. 데이터 로드
        csv_file = find_csv_file()
        df = load_and_prepare_data(csv_file)
        
        # 2. 구별 개별 차트 생성
        individual_charts = create_individual_charts(df)
        
        # 3. 구별 비교 차트 생성
        comparison_chart = create_comparison_charts(df)
        
        # 4. 통계 요약
        stats_summary, ratio_stats = create_statistical_summary(df)
        
        # 5. 결과 요약
        print(f"\n✅ 시각화 분석 완료!")
        print(f"📁 생성된 파일 ({len(individual_charts) + 1}개):")
        print(f"  📊 종합 비교: {comparison_chart}")
        for chart in individual_charts:
            print(f"  📈 개별 차트: {chart}")
        
        print(f"\n📋 분석 요약:")
        print(f"  📅 분석 기간: {df['날짜'].min()} ~ {df['날짜'].max()}")
        print(f"  🏘️ 분석 지역: {', '.join(df['구명'].unique())}")
        print(f"  📊 총 데이터: {len(df)}건")
        
        # 최고가/최저가 지역
        latest_data = df[df['날짜'] == df['날짜'].max()]
        if not latest_data.empty:
            max_trade_gu = latest_data.loc[latest_data['매매 평균'].idxmax(), '구명']
            min_trade_gu = latest_data.loc[latest_data['매매 평균'].idxmin(), '구명']
            print(f"  💰 최고가 지역: {max_trade_gu} ({latest_data['매매 평균'].max():.2f}억원)")
            print(f"  💸 최저가 지역: {min_trade_gu} ({latest_data['매매 평균'].min():.2f}억원)")
        
        return df, individual_charts, comparison_chart
        
    except FileNotFoundError as e:
        print(f"파일 오류: {e}")
        print("해결 방법: test02.py 또는 test02_demo.py를 먼저 실행하세요.")
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    result = main()