# 라이브러리 설치
# pip install requests pandas

# 파이썬 코드

import requests
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import urlencode
from tqdm import tqdm
import xml.etree.ElementTree as ET

# API 키 설정 - 공공데이터포털에서 발급받은 키로 교체하세요
API_KEY = 'YOUR_API_KEY_HERE'  # 실제 API 키로 교체 필요

# API 키 검증
if API_KEY == 'YOUR_API_KEY_HERE':
    print("⚠️  API 키를 설정해주세요!")
    print("1. https://www.data.go.kr 접속")
    print("2. 회원가입 후 로그인")
    print("3. '아파트매매 실거래 상세자료' 서비스 신청")
    print("4. '아파트전월세 실거래 상세자료' 서비스 신청")
    print("5. 발급받은 API 키를 코드에 입력")
    print("\n💡 테스트용으로 test02_demo.py를 실행해보세요!")
    
    # 데모 버전 실행 여부 확인
    choice = input("\n데모 버전을 실행하시겠습니까? (y/n): ").lower()
    if choice == 'y':
        import subprocess
        subprocess.run(['python', '0722 문서 자동화 과제/test02_demo.py'])
    
    import sys
    sys.exit(1)

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
    return dates[::-1]  # 과거부터 순서대로

def fetch_trade_data(lawd_cd, deal_ymd, trade_type='매매'):
    """공공데이터포털 API를 통해 아파트 거래 데이터를 가져오는 함수"""
    
    # 올바른 API URL 설정
    if trade_type == '매매':
        url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade'
    else:
        url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent'

    params = {
        'serviceKey': API_KEY,
        'LAWD_CD': lawd_cd,
        'DEAL_YMD': deal_ymd,
        'numOfRows': '1000',
        'pageNo': '1',
    }

    try:
        print(f"API 호출: {trade_type} - {lawd_cd} - {deal_ymd}")
        
        # API 호출
        response = requests.get(url, params=params, timeout=10)
        
        # 응답 상태 확인
        if response.status_code != 200:
            print(f"HTTP 오류: {response.status_code}")
            return []
        
        # XML 파싱
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            print(f"XML 파싱 오류: {e}")
            print(f"응답 내용: {response.text[:500]}")
            return []
        
        # 에러 코드 확인
        result_code = root.find('.//resultCode')
        if result_code is not None and result_code.text != '00':
            result_msg = root.find('.//resultMsg')
            error_msg = result_msg.text if result_msg is not None else "알 수 없는 오류"
            print(f"API 오류 코드: {result_code.text}, 메시지: {error_msg}")
            
            # 일반적인 오류 해결 방법 제시
            if result_code.text == '01':
                print("해결방법: API 키가 잘못되었습니다. 공공데이터포털에서 새로 발급받으세요.")
            elif result_code.text == '02':
                print("해결방법: 필수 파라미터가 누락되었습니다.")
            elif result_code.text == '03':
                print("해결방법: 데이터가 없습니다. 다른 지역이나 기간을 시도해보세요.")
            elif result_code.text == '99':
                print("해결방법: 서버 오류입니다. 잠시 후 다시 시도해보세요.")
            
            return []
        
        # 데이터 추출
        prices = []
        items = root.findall('.//item')
        
        if not items:
            print(f"데이터 없음: {trade_type} - {lawd_cd} - {deal_ymd}")
            return []
        
        for item in items:
            try:
                if trade_type == '매매':
                    price_elem = item.find('거래금액')
                    if price_elem is not None and price_elem.text:
                        price_text = price_elem.text.strip().replace(',', '').replace(' ', '')
                        if price_text.isdigit():
                            prices.append(int(price_text))
                else:  # 전월세
                    price_elem = item.find('보증금액')
                    if price_elem is not None and price_elem.text:
                        price_text = price_elem.text.strip().replace(',', '').replace(' ', '')
                        if price_text.isdigit() and int(price_text) > 0:
                            prices.append(int(price_text))
            except Exception as e:
                continue
        
        print(f"수집 완료: {len(prices)}건")
        return prices
        
    except requests.exceptions.Timeout:
        print("API 호출 시간 초과")
        return []
    except requests.exceptions.ConnectionError:
        print("네트워크 연결 오류")
        return []
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        return []
# 최근 1년 수집
months = get_year_month_list(12)
results = []

print("=== 수원시 아파트 실거래가 데이터 수집 시작 ===")
print(f"수집 기간: {months[0]} ~ {months[-1]}")
print("API 호출 간격: 1초 (서버 부하 방지)")

import time

for gu_name, gu_code in tqdm(lawd_codes.items(), desc="구별 데이터 수집"):
    for month in tqdm(months, desc=f"{gu_name} 월별 수집", leave=False):
        # API 호출 간격 조절 (서버 부하 방지)
        time.sleep(1)
        
        # 매매
        trade_prices = fetch_trade_data(gu_code, month, '매매')
        time.sleep(0.5)  # 추가 대기
        
        # 전세
        rent_prices = fetch_trade_data(gu_code, month, '전세')
        
        # 평균 계산 (만원 단위로 변환)
        trade_avg = round(pd.Series(trade_prices).mean() / 10000, 2) if trade_prices else None
        rent_avg = round(pd.Series(rent_prices).mean() / 10000, 2) if rent_prices else None
        
        results.append({
            '구': gu_name,
            '월': month,
            '매매 평균 (억원)': trade_avg,
            '전세 평균 (억원)': rent_avg,
            '매매 건수': len(trade_prices),
            '전세 건수': len(rent_prices)
        })
        
        print(f"{gu_name} {month}: 매매 {len(trade_prices)}건, 전세 {len(rent_prices)}건")

# 결과 저장 및 출력
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

if total_trade > 0:
    avg_trade = df[df['매매 평균 (억원)'].notna()]['매매 평균 (억원)'].mean()
    print(f"전체 매매 평균가: {avg_trade:.2f}억원")

if total_rent > 0:
    avg_rent = df[df['전세 평균 (억원)'].notna()]['전세 평균 (억원)'].mean()
    print(f"전체 전세 평균가: {avg_rent:.2f}억원")