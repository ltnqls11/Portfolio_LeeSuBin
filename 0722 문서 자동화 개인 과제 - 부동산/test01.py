# 필요 라이브러리 설치
# pip install selenium pandas tqdm webdriver-manager

# 자동 크롬드라이버 관리를 위한 webdriver-manager 사용

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import pandas as pd
from tqdm import tqdm
from statistics import mean
from datetime import datetime, timedelta
import sys
import os

# webdriver-manager 자동 설치 시도
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    print("webdriver-manager가 설치되지 않았습니다. 수동으로 크롬드라이버를 설치해주세요.")

# 1️⃣ 기본 설정
def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("webdriver-manager로 크롬드라이버 자동 설치 완료")
        else:
            driver = webdriver.Chrome(options=options)
            print("기존 크롬드라이버 사용")
        return driver
    except WebDriverException as e:
        print(f"크롬드라이버 실행 오류: {e}")
        print("해결 방법:")
        print("1. Chrome 브라우저가 설치되어 있는지 확인")
        print("2. pip install webdriver-manager 실행")
        print("3. 또는 수동으로 크롬드라이버 다운로드 후 PATH 설정")
        sys.exit(1)
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        sys.exit(1)

driver = setup_driver()

# 2️⃣ 수원시 구별 URL (네이버 부동산 예시 URL, 실거래가 또는 매물가 기준)
base_urls = {
    '장안구': 'https://land.naver.com/article/city/41111118',  # 예시
    '권선구': 'https://land.naver.com/article/city/41113118',
    '팔달구': 'https://land.naver.com/article/city/41113119',
    '영통구': 'https://land.naver.com/article/city/41113120',
}

# 3️⃣ 크롤링 함수
def crawl_prices(url, gu_name):
    prices = []
    try:
        print(f"{gu_name} 데이터 수집 시작...")
        driver.get(url)
        
        # 페이지 로딩 대기 (더 안정적)
        wait = WebDriverWait(driver, 10)
        time.sleep(3)
        
        # 여러 가능한 CSS 셀렉터 시도
        selectors = [
            '.price',
            '.item_price', 
            '.price_area',
            '[class*="price"]',
            '.sale_price',
            '.rent_price'
        ]
        
        price_elements = []
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    price_elements = elements
                    print(f"{gu_name}: '{selector}' 셀렉터로 {len(elements)}개 요소 발견")
                    break
            except Exception:
                continue
        
        if not price_elements:
            print(f"{gu_name}: 가격 요소를 찾을 수 없습니다. 페이지 구조를 확인하세요.")
            return prices
        
        # 가격 데이터 추출 및 검증
        for elem in price_elements:
            try:
                text = elem.text.strip()
                if not text:
                    continue
                    
                # 다양한 가격 형식 처리
                cleaned_text = text.replace('억', '').replace('만', '').replace(',', '').replace(' ', '')
                
                # 숫자만 추출
                import re
                numbers = re.findall(r'\d+\.?\d*', cleaned_text)
                
                for num_str in numbers:
                    try:
                        price = float(num_str)
                        # 합리적인 가격 범위 (0.1억 ~ 100억)
                        if 0.1 <= price <= 100:
                            prices.append(price)
                    except ValueError:
                        continue
                        
            except Exception as e:
                continue
        
        print(f"{gu_name}: {len(prices)}개 가격 데이터 수집 완료")
        
    except TimeoutException:
        print(f"{gu_name}: 페이지 로딩 시간 초과")
    except WebDriverException as e:
        print(f"{gu_name}: 웹드라이버 오류 - {e}")
    except Exception as e:
        print(f"{gu_name}: 예상치 못한 오류 - {e}")
    
    return prices
# 4️⃣ 데이터 수집
result = []
today = datetime.today()

try:
    print("=== 수원시 부동산 데이터 수집 시작 ===")
    
    for gu, url in tqdm(base_urls.items(), desc="구별 데이터 수집"):
        prices = crawl_prices(url, gu)  # gu_name 매개변수 추가
        
        if prices:
            avg_price = mean(prices)
            result.append({
                '구': gu,
                '수집일': today.strftime('%Y-%m-%d'),
                '매물 평균가(억)': round(avg_price, 2),
                '매물수': len(prices),
                '최저가(억)': round(min(prices), 2),
                '최고가(억)': round(max(prices), 2)
            })
            print(f"{gu}: 평균 {round(avg_price, 2)}억원 ({len(prices)}개 매물)")
        else:
            result.append({
                '구': gu,
                '수집일': today.strftime('%Y-%m-%d'),
                '매물 평균가(억)': None,
                '매물수': 0,
                '최저가(억)': None,
                '최고가(억)': None
            })
            print(f"{gu}: 데이터 없음")

    # 5️⃣ 저장 및 결과 출력
    if result:
        df = pd.DataFrame(result)
        
        # CSV 파일 저장
        csv_filename = f'suwon_real_estate_avg_{today.strftime("%Y%m%d")}.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        
        print("\n=== 수집 결과 ===")
        print(df.to_string(index=False))
        print(f"\n데이터가 '{csv_filename}' 파일로 저장되었습니다.")
        
        # 간단한 통계
        valid_data = df[df['매물수'] > 0]
        if not valid_data.empty:
            print(f"\n=== 요약 통계 ===")
            print(f"데이터 수집 성공한 구: {len(valid_data)}개")
            print(f"전체 매물 수: {valid_data['매물수'].sum()}개")
            if valid_data['매물 평균가(억)'].notna().any():
                print(f"전체 평균가: {valid_data['매물 평균가(억)'].mean():.2f}억원")
    else:
        print("수집된 데이터가 없습니다.")

except KeyboardInterrupt:
    print("\n사용자에 의해 중단되었습니다.")
except Exception as e:
    print(f"데이터 수집 중 오류 발생: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("브라우저를 종료합니다...")
    try:
        driver.quit()
    except:
        pass
    print("프로그램 종료")