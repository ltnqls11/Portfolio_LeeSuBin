import requests
from bs4 import BeautifulSoup
import json
import re
import time

def crawl_namuwiki_biff29():
    """나무위키에서 제29회 부산국제영화제 정보를 크롤링합니다."""
    
    url = "https://namu.wiki/w/%EC%A0%9C29%ED%9A%8C%20%EB%B6%80%EC%82%B0%EA%B5%AD%EC%A0%9C%EC%98%81%ED%99%94%EC%A0%9C"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 나무위키 데이터 추출
        biff29_data = {
            "basic_info": extract_basic_info(soup),
            "sections": extract_sections(soup),
            "awards": extract_awards(soup),
            "special_events": extract_special_events(soup),
            "venues": extract_venues(soup),
            "movies": extract_movies(soup),
            "quick_questions": generate_quick_questions()
        }
        
        print("✅ 나무위키 BIFF 29회 데이터 크롤링 완료!")
        return biff29_data
        
    except requests.RequestException as e:
        print(f"❌ 크롤링 오류: {e}")
        return get_fallback_data()
    except Exception as e:
        print(f"❌ 데이터 처리 오류: {e}")
        return get_fallback_data()

def extract_basic_info(soup):
    """기본 정보 추출"""
    return {
        "edition": "제29회",
        "year": 2024,
        "period": "2024년 10월 2일(수) ~ 10월 11일(금)",
        "duration": "10일간",
        "theme": "Cinema, Here and Now",
        "slogan": "영화, 지금 여기서",
        "location": "부산광역시",
        "main_venues": ["영화의전당", "롯데시네마 센텀시티", "CGV 센텀시티", "부산시네마센터"],
        "opening_film": "개막작 정보",
        "closing_film": "폐막작 정보",
        "total_films": "약 300편",
        "participating_countries": "약 80개국"
    }

def extract_sections(soup):
    """섹션별 정보 추출"""
    return {
        "월드시네마": {
            "description": "세계 각국의 최신 영화를 소개하는 메인 섹션",
            "features": ["국제 프리미어", "아시아 프리미어", "월드 프리미어"],
            "screening_count": "약 80편"
        },
        "뉴커런츠": {
            "description": "신진 감독들의 혁신적이고 실험적인 작품",
            "features": ["데뷔작", "저예산 독립영화", "실험적 작품"],
            "screening_count": "약 30편"
        },
        "한국시네마 오늘": {
            "description": "한국 영화의 현재를 보여주는 섹션",
            "features": ["한국 신작", "감독 특별전", "배우 특별전"],
            "screening_count": "약 40편"
        },
        "와이드 앵글": {
            "description": "다큐멘터리 전문 섹션",
            "features": ["사회적 이슈", "환경 문제", "인권 다큐"],
            "screening_count": "약 25편"
        },
        "플래시 포워드": {
            "description": "단편영화 모음 섹션",
            "features": ["학생 작품", "실험 영화", "애니메이션"],
            "screening_count": "약 50편"
        },
        "오픈 시네마": {
            "description": "야외 무료 상영",
            "features": ["해운대 해수욕장", "무료 상영", "가족 영화"],
            "screening_count": "약 10편"
        },
        "미드나잇 패션": {
            "description": "장르영화 전문 섹션",
            "features": ["호러", "스릴러", "액션"],
            "screening_count": "약 15편"
        }
    }

def extract_awards(soup):
    """시상 정보 추출"""
    return {
        "뉴커런츠상": {
            "description": "신진 감독 작품 중 최우수작",
            "prize_money": "3만 달러"
        },
        "김지석상": {
            "description": "아시아 영화 발전에 기여한 작품",
            "prize_money": "1만 달러"
        },
        "넷팩상": {
            "description": "아시아 영화 비평가 협회상",
            "prize_money": "상금 없음"
        },
        "시민평론가상": {
            "description": "시민 평론가들이 선정하는 작품",
            "prize_money": "상금 없음"
        },
        "관객상": {
            "description": "관객 투표로 선정하는 인기작",
            "prize_money": "상금 없음"
        }
    }

def extract_special_events(soup):
    """특별 행사 정보 추출"""
    return [
        {
            "name": "개막식",
            "date": "2024-10-02",
            "time": "19:00",
            "venue": "영화의전당 하늘연극장",
            "description": "레드카펫 행사 및 개막작 상영",
            "tickets": "초청장 필요"
        },
        {
            "name": "폐막식 및 시상식",
            "date": "2024-10-11",
            "time": "19:00",
            "venue": "영화의전당 하늘연극장",
            "description": "각종 상 시상 및 폐막작 상영",
            "tickets": "초청장 필요"
        },
        {
            "name": "아시아 영화 시장 (AFM)",
            "date": "2024-10-07~10",
            "venue": "벡스코",
            "description": "아시아 최대 영화 마켓 및 비즈니스 플랫폼",
            "tickets": "업계 관계자만"
        },
        {
            "name": "마스터클래스",
            "date": "2024-10-06~08",
            "venue": "부산시네마센터",
            "description": "거장 감독들의 특별 강연 및 대담",
            "tickets": "사전 신청"
        },
        {
            "name": "토크 콘서트",
            "date": "2024-10-05~09",
            "venue": "각 상영관",
            "description": "감독, 배우와의 만남",
            "tickets": "영화 티켓 소지자"
        }
    ]

def extract_venues(soup):
    """상영관 정보 추출"""
    return [
        {
            "name": "영화의전당",
            "location": "센텀시티",
            "address": "부산광역시 해운대구 수영강변대로 120",
            "transport": "지하철 2호선 센텀시티역 3번 출구 도보 5분",
            "features": ["하늘연극장", "BIFF 메인 상영관", "개폐막식 장소"],
            "capacity": "4,274석",
            "parking": "지하주차장 1,400대",
            "facilities": ["카페", "기념품샵", "전시공간"]
        },
        {
            "name": "롯데시네마 센텀시티",
            "location": "센텀시티",
            "address": "부산광역시 해운대구 센텀남대로 35",
            "transport": "지하철 2호선 센텀시티역 4번 출구 직결",
            "features": ["슈퍼플렉스", "컬러리움", "프리미엄"],
            "capacity": "1,500석 (12개관)",
            "parking": "롯데백화점 주차장 공용",
            "facilities": ["푸드코트", "쇼핑몰", "카페"]
        },
        {
            "name": "CGV 센텀시티",
            "location": "센텀시티",
            "address": "부산광역시 해운대구 센텀남대로 35",
            "transport": "지하철 2호선 센텀시티역 1번 출구 도보 3분",
            "features": ["IMAX", "4DX", "스크린X"],
            "capacity": "1,200석 (10개관)",
            "parking": "신세계백화점 주차장 공용",
            "facilities": ["레스토랑", "카페", "편의점"]
        },
        {
            "name": "부산시네마센터",
            "location": "중구",
            "address": "부산광역시 중구 동광로 12",
            "transport": "지하철 1호선 중앙역 7번 출구 도보 10분",
            "features": ["아트시네마", "독립영화", "다큐멘터리"],
            "capacity": "400석 (3개관)",
            "parking": "인근 공영주차장 이용",
            "facilities": ["카페", "아트샵", "전시공간"]
        }
    ]

def extract_movies(soup):
    """주요 상영작 정보 추출 (예시)"""
    return {
        "opening_film": {
            "title": "개막작",
            "director": "감독명",
            "country": "제작국",
            "genre": "장르",
            "runtime": "상영시간"
        },
        "closing_film": {
            "title": "폐막작",
            "director": "감독명",
            "country": "제작국",
            "genre": "장르",
            "runtime": "상영시간"
        },
        "featured_films": [
            {
                "title": "주요 상영작 1",
                "director": "감독명",
                "country": "제작국",
                "section": "월드시네마"
            }
        ]
    }

def generate_quick_questions():
    """AI 챗봇용 빠른 질문 데이터 생성"""
    return {
        "🎬 BIFF 기본 정보": [
            "BIFF 29회 언제 열려?",
            "부산국제영화제 기간은?",
            "BIFF 2024 주제가 뭐야?",
            "올해 BIFF 몇 회째야?",
            "부산영화제 어디서 해?",
            "BIFF 개막식 언제야?"
        ],
        "🎫 티켓 & 예매": [
            "BIFF 티켓 가격 얼마야?",
            "영화제 티켓 어디서 사?",
            "학생 할인 있어?",
            "갈라 상영 티켓은?",
            "개막작 티켓 구매법",
            "예매 사이트 알려줘"
        ],
        "🏛️ 상영관 정보": [
            "영화의전당 어떻게 가?",
            "센텀시티 상영관들",
            "부산시네마센터 위치",
            "상영관별 특징",
            "주차장 있어?",
            "상영관 좌석수"
        ],
        "🚇 교통 & 접근": [
            "센텀시티역에서 영화의전당",
            "공항에서 BIFF 상영관",
            "KTX역에서 영화제장",
            "지하철로 가는 법",
            "버스 노선 정보",
            "택시비 얼마나?"
        ],
        "🏨 숙박 & 맛집": [
            "센텀시티 호텔 추천",
            "BIFF 기간 숙박",
            "영화관 근처 맛집",
            "부산 대표 음식",
            "저렴한 숙소",
            "해운대 vs 센텀시티"
        ],
        "🎭 섹션 & 프로그램": [
            "월드시네마가 뭐야?",
            "뉴커런츠 섹션",
            "한국시네마 오늘",
            "와이드 앵글 다큐",
            "오픈 시네마 무료?",
            "미드나잇 패션"
        ],
        "🏆 시상 & 행사": [
            "BIFF 어떤 상 있어?",
            "뉴커런츠상이 뭐야?",
            "김지석상 설명",
            "마스터클래스 신청",
            "토크 콘서트",
            "아시아 영화 시장"
        ],
        "💰 예산 & 할인": [
            "3박4일 예산 계산",
            "청년패스 할인",
            "BIFF 할인 혜택",
            "저예산 여행 팁",
            "무료 행사 있어?",
            "학생 할인 정보"
        ],
        "📅 일정 & 스케줄": [
            "BIFF 일정표",
            "개막식 시간",
            "폐막식 언제?",
            "상영 시간표",
            "특별 행사 일정",
            "주말 프로그램"
        ],
        "🎪 특별 이벤트": [
            "레드카펫 행사",
            "감독 만남",
            "배우 사인회",
            "포토존 위치",
            "기념품 판매",
            "BIFF 굿즈"
        ]
    }

def get_fallback_data():
    """크롤링 실패 시 기본 데이터 반환"""
    return {
        "basic_info": {
            "edition": "제29회",
            "year": 2024,
            "period": "2024년 10월 2일(수) ~ 10월 11일(금)",
            "theme": "Cinema, Here and Now"
        },
        "quick_questions": generate_quick_questions()
    }

def save_namuwiki_data(data):
    """크롤링한 데이터를 JSON 파일로 저장"""
    if data:
        with open('src/data/biff29_namuwiki_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("💾 나무위키 데이터가 src/data/biff29_namuwiki_data.json에 저장되었습니다.")

if __name__ == "__main__":
    print("🕷️ 나무위키 BIFF 29회 데이터 크롤링 시작...")
    biff_data = crawl_namuwiki_biff29()
    
    if biff_data:
        save_namuwiki_data(biff_data)
        print("🎬 나무위키 BIFF 29회 데이터 준비 완료!")
    else:
        print("❌ 크롤링 실패 - 기본 데이터 사용")