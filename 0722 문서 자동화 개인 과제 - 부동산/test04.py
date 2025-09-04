# 1️⃣ 라이브러리 설치
# pip install pandas openpyxl matplotlib seaborn

import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import glob
import platform
import matplotlib.font_manager as fm

def setup_korean_font():
    """한글 폰트 설정 함수"""
    system = platform.system()
    
    # 사용 가능한 한글 폰트 목록
    korean_fonts = [
        'Malgun Gothic',      # Windows 기본
        'NanumGothic',        # 나눔고딕
        'NanumBarunGothic',   # 나눔바른고딕
        'AppleGothic',        # macOS
        'Noto Sans CJK KR',   # Linux
        'DejaVu Sans'         # 대체 폰트
    ]
    
    # 시스템에 설치된 폰트 확인
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 사용 가능한 한글 폰트 찾기
    selected_font = None
    for font in korean_fonts:
        if font in available_fonts:
            selected_font = font
            break
    
    if selected_font:
        plt.rcParams['font.family'] = selected_font
        print(f"한글 폰트 설정 완료: {selected_font}")
    else:
        # 대체 방법: 시스템 기본 폰트 사용
        if system == 'Windows':
            plt.rcParams['font.family'] = ['Malgun Gothic', 'sans-serif']
        elif system == 'Darwin':  # macOS
            plt.rcParams['font.family'] = ['AppleGothic', 'sans-serif']
        else:  # Linux
            plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
        print(f"기본 폰트 설정 완료 ({system})")
    
    # 마이너스 기호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False
    
    # 폰트 캐시 새로고침
    plt.rcParams['font.size'] = 10
    plt.rcParams['figure.titlesize'] = 16
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 11
    
    return selected_font

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

def load_and_clean_data(file_path):
    """CSV 데이터 로드 및 정리"""
    try:
        # CSV 불러오기
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"데이터 로드 완료: {len(df)}행")
        
        # 데이터 확인
        print("\n=== 원본 데이터 구조 ===")
        print(df.head())
        print(f"컬럼: {list(df.columns)}")
        
        # 컬럼명 정리 (실제 CSV 구조에 맞게)
        column_mapping = {
            '구': '구명',
            '월': '날짜',
            '매매 평균 (억원)': '매매 평균',
            '전세 평균 (억원)': '전세 평균'
        }
        
        # 컬럼명 변경
        df = df.rename(columns=column_mapping)
        
        # 필요한 컬럼이 있는지 확인
        required_columns = ['구명', '날짜', '매매 평균', '전세 평균']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"누락된 컬럼: {missing_columns}")
            print("사용 가능한 컬럼:", list(df.columns))
            # 대체 컬럼명 시도
            if '구' in df.columns:
                df['구명'] = df['구']
            if '월' in df.columns:
                df['날짜'] = df['월']
        
        # 숫자 데이터 변환
        df['매매 평균'] = pd.to_numeric(df['매매 평균'], errors='coerce')
        df['전세 평균'] = pd.to_numeric(df['전세 평균'], errors='coerce')
        
        # 날짜 형식 확인 및 정리
        df['날짜'] = df['날짜'].astype(str)
        
        print("\n=== 정리된 데이터 구조 ===")
        print(df.head())
        print(f"구별 데이터 수: {df['구명'].value_counts()}")
        
        return df
        
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        raise

def calculate_change_rates(df):
    """전월 대비 변동률 계산"""
    
    # 3️⃣ 월별 / 구별 평균값 계산
    df_grouped = df.groupby(['구명', '날짜']).agg({
        '매매 평균': 'mean',
        '전세 평균': 'mean',
        '매매 건수': 'sum' if '매매 건수' in df.columns else lambda x: len(x),
        '전세 건수': 'sum' if '전세 건수' in df.columns else lambda x: len(x)
    }).reset_index()
    
    df_grouped = df_grouped.sort_values(['구명', '날짜'])
    
    # 4️⃣ 전월 대비 상승률 계산
    def calc_pct(group):
        group = group.sort_values('날짜').copy()
        group['매매변동률(%)'] = group['매매 평균'].pct_change() * 100
        group['전세변동률(%)'] = group['전세 평균'].pct_change() * 100
        return group
    
    df_result = df_grouped.groupby('구명').apply(calc_pct).reset_index(drop=True)
    
    # 5️⃣ 최종 컬럼 정리
    final_columns = ['날짜', '구명', '매매 평균', '매매변동률(%)', '전세 평균', '전세변동률(%)']
    if '매매 건수' in df_result.columns:
        final_columns.extend(['매매 건수', '전세 건수'])
    
    df_result = df_result[final_columns]
    
    # NaN 값을 0으로 대체 (첫 달은 변동률 계산 불가)
    df_result['매매변동률(%)'] = df_result['매매변동률(%)'].fillna(0)
    df_result['전세변동률(%)'] = df_result['전세변동률(%)'].fillna(0)
    
    return df_result

def create_visualizations(df_result):
    """데이터 시각화 생성 - 한글 폰트 완전 해결"""
    
    print("🔧 한글 폰트 문제 해결 중...")
    
    # matplotlib 완전 초기화
    import matplotlib
    matplotlib.rcdefaults()
    plt.close('all')
    
    # 한글 폰트 강제 설정 - 가장 확실한 방법
    import matplotlib.font_manager as fm
    import warnings
    warnings.filterwarnings('ignore')
    
    # Windows 환경에서 한글 폰트 직접 설정
    plt.rcParams.update({
        'font.family': ['Malgun Gothic', 'Microsoft YaHei', 'SimHei', 'sans-serif'],
        'axes.unicode_minus': False,
        'font.size': 12,
        'figure.titlesize': 20,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'legend.fontsize': 13,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11
    })
    
    print("✅ 한글 폰트 설정 완료: Malgun Gothic")
    
    # 시각화 생성
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    
    # 색상 팔레트 설정
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    # 메인 타이틀 설정
    fig.suptitle('수원시 구별 부동산 가격 분석', fontsize=22, fontweight='bold', y=0.95)
    
    # 1. 구별 매매 평균가 추이
    ax1 = axes[0, 0]
    for i, gu in enumerate(df_result['구명'].unique()):
        gu_data = df_result[df_result['구명'] == gu]
        ax1.plot(gu_data['날짜'], gu_data['매매 평균'], 
                marker='o', label=gu, linewidth=2.5, 
                color=colors[i % len(colors)], markersize=6)
    
    ax1.set_title('구별 매매 평균가 추이', fontsize=16, fontweight='bold', pad=15)
    ax1.set_xlabel('월', fontsize=14)
    ax1.set_ylabel('평균가 (억원)', fontsize=14)
    ax1.legend(fontsize=13, frameon=True, fancybox=True, shadow=True)
    
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45, labelsize=11)
    ax1.tick_params(axis='y', labelsize=11)
    
    # 2. 구별 전세 평균가 추이
    ax2 = axes[0, 1]
    for i, gu in enumerate(df_result['구명'].unique()):
        gu_data = df_result[df_result['구명'] == gu]
        ax2.plot(gu_data['날짜'], gu_data['전세 평균'], 
                marker='s', label=gu, linewidth=2.5, 
                color=colors[i % len(colors)], markersize=6)
    
    ax2.set_title('구별 전세 평균가 추이', fontsize=16, fontweight='bold', pad=15)
    ax2.set_xlabel('월', fontsize=14)
    ax2.set_ylabel('평균가 (억원)', fontsize=14)
    ax2.legend(fontsize=13, frameon=True, fancybox=True, shadow=True)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45, labelsize=11)
    ax2.tick_params(axis='y', labelsize=11)
    
    # 3. 매매 변동률 히트맵
    ax3 = axes[1, 0]
    pivot_trade = df_result.pivot(index='구명', columns='날짜', values='매매변동률(%)')
    
    # 히트맵 생성
    sns.heatmap(pivot_trade, annot=True, fmt='.1f', cmap='RdYlBu_r', 
                center=0, ax=ax3, cbar_kws={'label': '변동률 (%)'})
    
    ax3.set_title('매매 변동률 히트맵 (%)', fontsize=16, fontweight='bold', pad=15)
    ax3.set_xlabel('월', fontsize=14)
    ax3.set_ylabel('구', fontsize=14)
    ax3.tick_params(axis='x', rotation=45, labelsize=11)
    ax3.tick_params(axis='y', rotation=0, labelsize=11)
    
    # 4. 전세 변동률 히트맵
    ax4 = axes[1, 1]
    pivot_rent = df_result.pivot(index='구명', columns='날짜', values='전세변동률(%)')
    
    # 히트맵 생성
    sns.heatmap(pivot_rent, annot=True, fmt='.1f', cmap='RdYlBu_r', 
                center=0, ax=ax4, cbar_kws={'label': '변동률 (%)'})
    
    ax4.set_title('전세 변동률 히트맵 (%)', fontsize=16, fontweight='bold', pad=15)
    ax4.set_xlabel('월', fontsize=14)
    ax4.set_ylabel('구', fontsize=14)
    ax4.tick_params(axis='x', rotation=45, labelsize=11)
    ax4.tick_params(axis='y', rotation=0, labelsize=11)
    
    # 레이아웃 조정
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # 이미지 저장 (한글 폰트 포함)
    chart_filename = f'수원시_부동산_분석_차트_{datetime.now().strftime("%Y%m%d")}.png'
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    print(f"차트가 저장되었습니다: {chart_filename}")
    
    # 메모리 정리
    plt.close()
    
    return chart_filename

def generate_summary_report(df_result):
    """요약 보고서 생성"""
    
    print("\n=== 수원시 부동산 시장 분석 보고서 ===")
    
    # 최신 월 데이터
    latest_month = df_result['날짜'].max()
    latest_data = df_result[df_result['날짜'] == latest_month]
    
    print(f"\n📅 분석 기간: {df_result['날짜'].min()} ~ {latest_month}")
    print(f"📍 분석 지역: {', '.join(df_result['구명'].unique())}")
    
    print(f"\n💰 최신 월({latest_month}) 평균가:")
    for _, row in latest_data.iterrows():
        print(f"  {row['구명']}: 매매 {row['매매 평균']:.2f}억원, 전세 {row['전세 평균']:.2f}억원")
    
    # 변동률 분석
    print(f"\n📈 최신 월 변동률:")
    for _, row in latest_data.iterrows():
        trade_change = "📈" if row['매매변동률(%)'] > 0 else "📉" if row['매매변동률(%)'] < 0 else "➡️"
        rent_change = "📈" if row['전세변동률(%)'] > 0 else "📉" if row['전세변동률(%)'] < 0 else "➡️"
        print(f"  {row['구명']}: 매매 {trade_change} {row['매매변동률(%)']:+.2f}%, 전세 {rent_change} {row['전세변동률(%)']:+.2f}%")
    
    # 전체 기간 통계
    print(f"\n📊 전체 기간 통계:")
    print(f"  매매 최고가: {df_result['매매 평균'].max():.2f}억원")
    print(f"  매매 최저가: {df_result['매매 평균'].min():.2f}억원")
    print(f"  전세 최고가: {df_result['전세 평균'].max():.2f}억원")
    print(f"  전세 최저가: {df_result['전세 평균'].min():.2f}억원")
    
    return latest_data

def main():
    """메인 실행 함수"""
    try:
        print("=== 수원시 부동산 변동률 분석 시작 ===")
        
        # 1. CSV 파일 찾기 및 데이터 로드
        csv_file = find_csv_file()
        df = load_and_clean_data(csv_file)
        
        # 2. 변동률 계산
        df_result = calculate_change_rates(df)
        
        # 3. 엑셀 저장
        excel_filename = f'수원시_1년_구별_월별_변동률_{datetime.now().strftime("%Y%m%d")}.xlsx'
        
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            # 메인 데이터
            df_result.to_excel(writer, sheet_name='변동률_분석', index=False)
            
            # 요약 통계
            summary_stats = df_result.groupby('구명').agg({
                '매매 평균': ['mean', 'min', 'max'],
                '전세 평균': ['mean', 'min', 'max'],
                '매매변동률(%)': ['mean', 'min', 'max'],
                '전세변동률(%)': ['mean', 'min', 'max']
            }).round(2)
            summary_stats.to_excel(writer, sheet_name='구별_요약통계')
        
        print(f"엑셀 파일이 저장되었습니다: {excel_filename}")
        
        # 4. 시각화 생성
        chart_file = create_visualizations(df_result)
        
        # 5. 요약 보고서
        latest_data = generate_summary_report(df_result)
        
        print(f"\n✅ 분석 완료!")
        print(f"📁 생성된 파일:")
        print(f"  - {excel_filename}")
        print(f"  - {chart_file}")
        
        return df_result
        
    except FileNotFoundError as e:
        print(f"파일 오류: {e}")
        print("해결 방법: test02.py 또는 test02_demo.py를 먼저 실행하세요.")
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    result = main()