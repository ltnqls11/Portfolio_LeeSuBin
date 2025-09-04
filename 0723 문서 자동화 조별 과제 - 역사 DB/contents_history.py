import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import os
import sys
from urllib.parse import urljoin

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://contents.history.go.kr/front/contents/search/results.do"
OUTPUT_CSV = "history_contents.csv"

def fetch_page(query="", page=1, max_retries=3):
    """페이지를 안전하게 가져옵니다."""
    params = {
        "query": query,
        "pageIndex": page,
        "pageUnit": 10,
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"페이지 {page} 요청 시도 {attempt + 1}/{max_retries}")
            
            session = requests.Session()
            session.headers.update(headers)
            
            resp = session.get(BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            
            if resp.status_code == 200:
                logger.info(f"페이지 {page} 성공적으로 가져옴")
                return resp.text
            else:
                logger.warning(f"예상치 못한 상태 코드: {resp.status_code}")
                
        except requests.exceptions.Timeout:
            logger.warning(f"타임아웃 오류 (페이지 {page}, 시도 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"연결 오류 (페이지 {page}, 시도 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP 오류 (페이지 {page}): {e}")
            if e.response.status_code in [404, 403]:
                logger.error(f"페이지 접근 불가: {e.response.status_code}")
                break
            elif attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"요청 오류 (페이지 {page}, 시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        except Exception as e:
            logger.error(f"예상치 못한 오류 (페이지 {page}): {e}")
            break
    
    logger.error(f"페이지 {page} 모든 시도 실패")
    return None

def parse_items(html):
    """HTML에서 아이템들을 안전하게 파싱합니다."""
    if not html:
        logger.warning("HTML이 비어있습니다.")
        return []
    
    try:
        soup = BeautifulSoup(html, "html.parser")
        items = []
        
        # 다양한 선택자 패턴 시도
        card_selectors = [
            "div.cards > div.card",
            "div.card",
            ".card",
            "[class*='card']"
        ]
        
        cards = []
        for selector in card_selectors:
            cards = soup.select(selector)
            if cards:
                logger.info(f"카드 요소 {len(cards)}개 발견 (선택자: {selector})")
                break
        
        if not cards:
            logger.warning("카드 요소를 찾을 수 없습니다.")
            return []
        
        for i, div in enumerate(cards):
            try:
                # 제목 추출
                title_selectors = ["h5.card-title", ".card-title", "h5", ".title"]
                title = ""
                for selector in title_selectors:
                    title_elem = div.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                
                if not title:
                    logger.warning(f"카드 {i+1}: 제목을 찾을 수 없습니다.")
                    continue
                
                # 링크 추출
                link_elem = div.select_one("a")
                if not link_elem or not link_elem.get("href"):
                    logger.warning(f"카드 {i+1}: 링크를 찾을 수 없습니다.")
                    continue
                
                link = link_elem["href"]
                if not link.startswith("http"):
                    link = urljoin("https://contents.history.go.kr", link)
                
                # 날짜 추출
                date_selectors = ["p.card-date", ".card-date", ".date"]
                date = ""
                for selector in date_selectors:
                    date_elem = div.select_one(selector)
                    if date_elem:
                        date = date_elem.get_text(strip=True)
                        break
                
                # 요약 추출
                summary_selectors = ["p.card-text", ".card-text", ".summary", "p"]
                summary = ""
                for selector in summary_selectors:
                    summary_elem = div.select_one(selector)
                    if summary_elem:
                        summary = summary_elem.get_text(strip=True)
                        break
                
                items.append({
                    "title": title,
                    "date": date if date else "날짜 없음",
                    "summary": summary if summary else "요약 없음",
                    "url": link
                })
                
                logger.debug(f"카드 {i+1} 파싱 완료: {title[:30]}...")
                
            except Exception as e:
                logger.warning(f"카드 {i+1} 파싱 중 오류: {e}")
                continue
        
        logger.info(f"총 {len(items)}개 아이템 파싱 완료")
        return items
        
    except Exception as e:
        logger.error(f"HTML 파싱 중 오류: {e}")
        return []

def crawl_all(query="", max_pages=5, delay=1):
    """모든 페이지를 안전하게 크롤링합니다."""
    all_items = []
    consecutive_failures = 0
    max_consecutive_failures = 3
    
    logger.info(f"크롤링 시작 - 검색어: '{query}', 최대 페이지: {max_pages}")
    
    for page in range(1, max_pages + 1):
        try:
            logger.info(f"크롤링 중 - 페이지 {page}/{max_pages}")
            
            html = fetch_page(query=query, page=page)
            
            if not html:
                consecutive_failures += 1
                logger.warning(f"페이지 {page} HTML 가져오기 실패 (연속 실패: {consecutive_failures})")
                
                if consecutive_failures >= max_consecutive_failures:
                    logger.error(f"연속 {max_consecutive_failures}회 실패로 크롤링 중단")
                    break
                
                # 실패 시 더 긴 대기
                time.sleep(delay * 2)
                continue
            
            items = parse_items(html)
            
            if not items:
                consecutive_failures += 1
                logger.warning(f"페이지 {page} 아이템 파싱 실패 (연속 실패: {consecutive_failures})")
                
                if consecutive_failures >= max_consecutive_failures:
                    logger.error(f"연속 {max_consecutive_failures}회 실패로 크롤링 중단")
                    break
                
                # 빈 페이지가 나오면 더 이상 페이지가 없을 수 있음
                if page > 1:
                    logger.info("빈 페이지 발견 - 크롤링 완료")
                    break
                
                time.sleep(delay)
                continue
            
            # 성공 시 연속 실패 카운터 리셋
            consecutive_failures = 0
            all_items.extend(items)
            
            logger.info(f"페이지 {page} 완료 - {len(items)}개 아이템 수집 (총 {len(all_items)}개)")
            
            # 서버 부하 방지를 위한 대기
            if delay > 0:
                time.sleep(delay)
                
        except KeyboardInterrupt:
            logger.info("사용자에 의해 크롤링이 중단되었습니다.")
            break
            
        except Exception as e:
            consecutive_failures += 1
            logger.error(f"페이지 {page} 크롤링 중 예상치 못한 오류: {e}")
            
            if consecutive_failures >= max_consecutive_failures:
                logger.error(f"연속 {max_consecutive_failures}회 실패로 크롤링 중단")
                break
            
            time.sleep(delay * 2)
            continue
    
    logger.info(f"크롤링 완료 - 총 {len(all_items)}개 아이템 수집")
    return all_items

def save_csv(items, filename):
    """CSV 파일을 안전하게 저장합니다."""
    if not items:
        logger.warning("저장할 데이터가 없습니다.")
        return False
    
    try:
        # 디렉토리 확인 및 생성
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"디렉토리 생성: {directory}")
        
        # 백업 파일 생성 (기존 파일이 있는 경우)
        if os.path.exists(filename):
            backup_filename = f"{filename}.backup"
            try:
                os.rename(filename, backup_filename)
                logger.info(f"기존 파일 백업: {backup_filename}")
            except Exception as e:
                logger.warning(f"백업 파일 생성 실패: {e}")
        
        keys = ["title", "date", "summary", "url"]
        
        # 데이터 검증
        valid_items = []
        for i, item in enumerate(items):
            try:
                # 필수 필드 확인
                if not item.get("title"):
                    logger.warning(f"아이템 {i+1}: 제목이 없어 건너뜀")
                    continue
                
                if not item.get("url"):
                    logger.warning(f"아이템 {i+1}: URL이 없어 건너뜀")
                    continue
                
                # 데이터 정리
                clean_item = {}
                for key in keys:
                    value = item.get(key, "")
                    # 특수 문자 및 줄바꿈 정리
                    if isinstance(value, str):
                        value = value.replace('\n', ' ').replace('\r', ' ').strip()
                        # CSV에서 문제가 될 수 있는 문자 처리
                        value = value.replace('"', '""')
                    clean_item[key] = value
                
                valid_items.append(clean_item)
                
            except Exception as e:
                logger.warning(f"아이템 {i+1} 검증 중 오류: {e}")
                continue
        
        if not valid_items:
            logger.error("유효한 데이터가 없습니다.")
            return False
        
        # CSV 파일 저장
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(valid_items)
        
        # 파일 크기 확인
        file_size = os.path.getsize(filename)
        logger.info(f"✅ CSV 저장 완료: {filename}")
        logger.info(f"📊 저장된 데이터: {len(valid_items)}개 아이템")
        logger.info(f"📁 파일 크기: {file_size:,} bytes")
        
        # 백업 파일 정리
        backup_filename = f"{filename}.backup"
        if os.path.exists(backup_filename):
            try:
                os.remove(backup_filename)
                logger.info("백업 파일 정리 완료")
            except Exception as e:
                logger.warning(f"백업 파일 정리 실패: {e}")
        
        return True
        
    except PermissionError:
        logger.error(f"파일 쓰기 권한이 없습니다: {filename}")
        return False
        
    except OSError as e:
        logger.error(f"파일 시스템 오류: {e}")
        return False
        
    except Exception as e:
        logger.error(f"CSV 저장 중 예상치 못한 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    try:
        logger.info("한국사 콘텐츠 크롤러 시작")
        logger.info("=" * 50)
        
        # 사용자 설정
        search_query = input("검색어를 입력하세요 (엔터: 전체 검색): ").strip()
        
        try:
            max_pages = int(input("최대 페이지 수를 입력하세요 (기본값: 10): ") or "10")
            if max_pages <= 0:
                max_pages = 10
        except ValueError:
            max_pages = 10
            logger.warning("잘못된 페이지 수 입력, 기본값 10 사용")
        
        try:
            delay = float(input("페이지 간 대기 시간(초)을 입력하세요 (기본값: 0.5): ") or "0.5")
            if delay < 0:
                delay = 0.5
        except ValueError:
            delay = 0.5
            logger.warning("잘못된 대기 시간 입력, 기본값 0.5초 사용")
        
        logger.info(f"설정 - 검색어: '{search_query}', 최대 페이지: {max_pages}, 대기 시간: {delay}초")
        
        # 크롤링 실행
        data = crawl_all(query=search_query, max_pages=max_pages, delay=delay)
        
        if not data:
            logger.error("크롤링된 데이터가 없습니다.")
            return
        
        # CSV 저장
        success = save_csv(data, OUTPUT_CSV)
        
        if success:
            logger.info("🎉 크롤링 완료!")
            logger.info(f"📁 저장된 파일: {OUTPUT_CSV}")
        else:
            logger.error("❌ 파일 저장 실패")
            
    except KeyboardInterrupt:
        logger.info("⏹️ 사용자에 의해 프로그램이 중단되었습니다.")
        
    except Exception as e:
        logger.error(f"❌ 프로그램 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
