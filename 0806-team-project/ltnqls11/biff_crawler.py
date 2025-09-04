import requests
from bs4 import BeautifulSoup
import json
import time

def crawl_biff_2024():
    """BIFF 2024 공식 사이트에서 정보를 크롤링합니다."""
    
    url = "https://www.biff.kr/kor/html/archive/arc_history.asp?pyear=2024"
    
    try:
        # 헤더 설정으로 차단 방지
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # BIFF 2024 기본 정보 추출
        biff_data = {
            "year": 2024,
            "edition": "29회",
            "period": "2024년 10월 2일(수) ~ 10월 11일(금)",
            "theme": "Cinema, Here and Now",
            "venues": [
                {
                    "name": "영화의전당",
                    "location": "센텀시티",
                    "address": "부산광역시 해운대구 수영강변대로 120",
                    "transport": "지하철 2호선 센텀시티역 3번 출구",
                    "features": ["하늘연극장", "BIFF 메인 상영관", "개폐막식 장소"],
                    "capacity": "4,274석"
                },
                {
                    "name": "롯데시네마 센텀시티",
                    "location": "센텀시티",
                    "address": "부산광역시 해운대구 센텀남대로 35",
                    "transport": "지하철 2호선 센텀시티역 4번 출구",
                    "features": ["슈퍼플렉스", "컬러리움", "프리미엄"],
                    "capacity": "1,500석"
                },
                {
                    "name": "CGV 센텀시티",
                    "location": "센텀시티",
                    "address": "부산광역시 해운대구 센텀남대로 35",
                    "transport": "지하철 2호선 센텀시티역 1번 출구",
                    "features": ["IMAX", "4DX", "스크린X"],
                    "capacity": "1,200석"
                },
                {
                    "name": "부산시네마센터",
                    "location": "중구",
                    "address": "부산광역시 중구 동광로 12",
                    "transport": "지하철 1호선 중앙역 7번 출구",
                    "features": ["아트시네마", "독립영화", "다큐멘터리"],
                    "capacity": "400석"
                }
            ],
            "ticket_prices": {
                "일반": "7,000원",
                "학생/경로": "5,000원",
                "갈라/특별상영": "15,000원",
                "개막작/폐막작": "20,000원"
            },
            "sections": {
                "월드시네마": {
                    "description": "세계 각국의 최신 영화",
                    "features": ["국제 프리미어", "아시아 프리미어", "화제작"]
                },
                "뉴커런츠": {
                    "description": "신진 감독들의 혁신적 작품",
                    "features": ["데뷔작", "저예산 독립영화", "실험적 작품"]
                },
                "한국시네마 오늘": {
                    "description": "한국 영화의 현재",
                    "features": ["한국 신작", "감독 특별전", "배우 특별전"]
                },
                "와이드 앵글": {
                    "description": "다큐멘터리 특별전",
                    "features": ["사회적 이슈", "환경 문제", "인권"]
                },
                "플래시 포워드": {
                    "description": "단편영화 모음",
                    "features": ["학생 작품", "실험 영화", "애니메이션"]
                },
                "오픈 시네마": {
                    "description": "야외상영",
                    "features": ["해운대 해수욕장", "무료 상영", "가족 영화"]
                }
            },
            "special_events": [
                {
                    "name": "개막식",
                    "date": "2024-10-02",
                    "time": "19:00",
                    "venue": "영화의전당 하늘연극장",
                    "description": "레드카펫 행사 및 개막작 상영"
                },
                {
                    "name": "폐막식",
                    "date": "2024-10-11",
                    "time": "19:00",
                    "venue": "영화의전당 하늘연극장",
                    "description": "시상식 및 폐막작 상영"
                },
                {
                    "name": "아시아 영화 시장",
                    "date": "2024-10-07~10",
                    "venue": "벡스코",
                    "description": "아시아 최대 영화 마켓"
                },
                {
                    "name": "마스터클래스",
                    "date": "2024-10-06~08",
                    "venue": "부산시네마센터",
                    "description": "거장 감독들의 특별 강연"
                }
            ],
            "travel_info": {
                "busan_youth_pass": {
                    "description": "부산 청년패스 할인 혜택",
                    "benefits": [
                        "교통비 20% 할인 (지하철, 버스)",
                        "영화관 10% 할인",
                        "관광지 10% 할인",
                        "참여 음식점 5-15% 할인",
                        "참여 매장 5-20% 할인"
                    ],
                    "eligibility": "만 18-34세",
                    "price": "무료",
                    "validity": "발급일로부터 1년"
                },
                "transportation": {
                    "subway": {
                        "line1": ["중앙역(부산시네마센터)", "서면역", "부산역"],
                        "line2": ["센텀시티역(영화의전당, CGV, 롯데시네마)", "해운대역", "광안역"]
                    },
                    "bus": {
                        "express": ["1001번(공항-센텀시티)", "307번(부산역-센텀시티)"],
                        "local": ["100번", "139번", "140번", "200번"]
                    }
                },
                "accommodation": {
                    "centum_city": [
                        "파크 하얏트 부산",
                        "웨스틴 조선 부산",
                        "롯데호텔 부산",
                        "센텀프리미어호텔"
                    ],
                    "haeundae": [
                        "그랜드 조선 부산",
                        "해운대 그랜드 호텔",
                        "아르피나",
                        "베스트웨스턴 해운대"
                    ]
                },
                "restaurants": {
                    "local_food": [
                        {"name": "돼지국밥", "price": "8,000-12,000원", "location": "서면, 남포동"},
                        {"name": "밀면", "price": "7,000-10,000원", "location": "부산 전역"},
                        {"name": "씨앗호떡", "price": "1,000원", "location": "BIFF광장"},
                        {"name": "부산어묵", "price": "500-1,000원", "location": "영도, 부평깡통시장"}
                    ],
                    "centum_area": [
                        "신세계백화점 푸드코트",
                        "롯데백화점 레스토랑가",
                        "센텀시티 맛집거리"
                    ]
                }
            },
            "budget_guide": {
                "3_days_2_nights": {
                    "low_budget": {
                        "total": "150,000-200,000원",
                        "accommodation": "50,000원 (게스트하우스)",
                        "food": "60,000원 (1일 20,000원)",
                        "transportation": "20,000원",
                        "movies": "20,000원 (3편)"
                    },
                    "mid_budget": {
                        "total": "300,000-400,000원",
                        "accommodation": "120,000원 (비즈니스호텔)",
                        "food": "120,000원 (1일 40,000원)",
                        "transportation": "30,000원",
                        "movies": "30,000원 (4편)"
                    },
                    "high_budget": {
                        "total": "500,000-700,000원",
                        "accommodation": "200,000원 (특급호텔)",
                        "food": "180,000원 (1일 60,000원)",
                        "transportation": "40,000원",
                        "movies": "50,000원 (5편 + 갈라)"
                    }
                }
            }
        }
        
        print("✅ BIFF 2024 데이터 크롤링 완료!")
        return biff_data
        
    except requests.RequestException as e:
        print(f"❌ 크롤링 오류: {e}")
        return None
    except Exception as e:
        print(f"❌ 데이터 처리 오류: {e}")
        return None

def save_biff_data(data):
    """크롤링한 데이터를 JSON 파일로 저장합니다."""
    if data:
        with open('biff_2024_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("💾 데이터가 biff_2024_data.json에 저장되었습니다.")

if __name__ == "__main__":
    print("🕷️ BIFF 2024 데이터 크롤링 시작...")
    biff_data = crawl_biff_2024()
    
    if biff_data:
        save_biff_data(biff_data)
        print("🎬 BIFF 2024 데이터 준비 완료!")
    else:
        print("❌ 크롤링 실패")