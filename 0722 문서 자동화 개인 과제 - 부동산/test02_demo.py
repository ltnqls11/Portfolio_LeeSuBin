# 테스트용 데모 버전 - API 키 없이도 실행 가능
# pip install pandas

import pandas as pd
from datetime import datetime
import random

print("=== 수원시 아파트 실거래가 데모 데이터 생성 ===")

# 수원시 구 코드
lawd_codes = {
    '장안구': '41111',
    '권선구': '41113', 
    '팔달구': '41115',
    '영통구': '41117',
}

def get_year_month_list(n_months=12):
    today = datetime.today()
    dates = []
    for i in range(n_months):
        month = today - pd.DateOffset(months=i)
        dates.append(month.strftime('%Y%m'))
    return dates[::-1]

def generate_demo_data():
    """데모용 가상 데이터 생성"""
    months = get_year_month_list(12)
    results = []
    
    for gu_name in lawd_codes.keys():
        for month in months:
            # 가상의 실거래가 데이터 생성
            trade_count = random.randint(10, 50)
            rent_count = random.randint(5, 30)
            
            # 지역별 가격 차이 반영
            base_price = {
                '장안구': 4.5,
                '권선구': 4.2,
                '팔달구': 5.1,
                '영통구': 6.8
            }
            
            trade_avg = base_price[gu_name] + random.uniform(-0.5, 0.5)
            rent_avg = trade_avg * 0.7 + random.uniform(-0.3, 0.3)
            
            results.append({
                '구': gu_name,
                '월': month,
                '매매 평균 (억원)': round(trade_avg, 2),
                '전세 평균 (억원)': round(rent_avg, 2),
                '매매 건수': trade_count,
                '전세 건수': rent_count
            })
            
            print(f"{gu_name} {month}: 매매 {trade_count}건, 전세 {rent_count}건")
    
    return results

# 데모 데이터 생성
results = generate_demo_data()

# 결과 저장
df = pd.DataFrame(results)
filename = f'수원시_1년_매매_전세_평균가_{datetime.now().strftime("%Y%m%d")}.csv'
df.to_csv(filename, index=False, encoding='utf-8-sig')

print("\n=== 수집 결과 ===")
print(df.to_string(index=False))
print(f"\n데이터가 '{filename}' 파일로 저장되었습니다.")

# 간단한 통계
print("\n=== 요약 통계 ===")
total_trade = df['매매 건수'].sum()
total_rent = df['전세 건수'].sum()
print(f"총 매매 건수: {total_trade}건")
print(f"총 전세 건수: {total_rent}건")

avg_trade = df['매매 평균 (억원)'].mean()
avg_rent = df['전세 평균 (억원)'].mean()
print(f"전체 매매 평균가: {avg_trade:.2f}억원")
print(f"전체 전세 평균가: {avg_rent:.2f}억원")

print("\n✅ 데모 데이터 생성 완료!")
print("실제 API를 사용하려면 test02.py에서 API 키를 설정하세요.")