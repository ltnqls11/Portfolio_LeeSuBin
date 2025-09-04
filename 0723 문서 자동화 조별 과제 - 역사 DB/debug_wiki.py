import requests
from bs4 import BeautifulSoup
import re

def debug_wikipedia_page():
    """위키백과 8월 15일 페이지 구조 분석"""
    url = "https://ko.wikipedia.org/wiki/8월_15일"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    print(f"페이지 크기: {len(response.text)} 바이트")
    print(f"제목: {soup.title.string}")
    
    # 사건 섹션 주변 HTML 직접 확인
    print("\n=== 사건 섹션 주변 HTML ===")
    html_text = response.text
    
    # 사건 섹션 찾기
    event_start = html_text.find('<h2 id="사건">')
    if event_start == -1:
        event_start = html_text.find('사건</h2>')
    
    if event_start != -1:
        # 사건 섹션부터 다음 h2까지의 HTML 추출
        next_h2 = html_text.find('<h2', event_start + 10)
        if next_h2 == -1:
            section_html = html_text[event_start:event_start + 5000]
        else:
            section_html = html_text[event_start:next_h2]
        
        print("사건 섹션 HTML (처음 2000자):")
        print(section_html[:2000])
        print("...")
        
        # ul 태그 찾기
        ul_matches = re.findall(r'<ul[^>]*>.*?</ul>', section_html, re.DOTALL)
        print(f"\n사건 섹션에서 발견된 ul 태그 수: {len(ul_matches)}")
        
        for i, ul_html in enumerate(ul_matches):
            print(f"\nUL {i+1} (처음 500자):")
            print(ul_html[:500])
    
    # 모든 헤딩 찾기
    print("\n=== 헤딩 구조 ===")
    headings = soup.find_all(['h1', 'h2', 'h3'])
    for h in headings:
        print(f"{h.name}: {h.get_text().strip()}")
    
    # 사건 섹션 찾기
    print("\n=== 사건 섹션 분석 ===")
    for h in soup.find_all(['h2', 'h3']):
        if '사건' in h.get_text():
            print(f"사건 헤더 발견: {h}")
            print(f"헤더 텍스트: {h.get_text()}")
            
            # 다음 형제 요소들 확인
            print("다음 형제 요소들:")
            current = h
            for i in range(20):  # 더 많이 확인
                current = current.find_next_sibling()
                if not current:
                    break
                    
                element_text = current.get_text()[:100] if current.get_text() else 'No text'
                print(f"  {i+1}. {current.name}: {element_text}...")
                
                if current.name == 'ul':
                    items = current.find_all('li')
                    print(f"    ✅ 리스트 발견! 항목 수: {len(items)}")
                    for j, li in enumerate(items[:5]):
                        li_text = li.get_text().strip()
                        print(f"      {j+1}. {li_text[:100]}...")
                        # 연도 패턴 확인
                        if re.search(r'\d{3,4}년?', li_text):
                            print(f"         → 연도 패턴 발견!")
                    break
                elif current.name in ['h2', 'h3'] and current != h:
                    print(f"    다른 섹션 도달: {current.get_text()}")
                    break
            break
    
    # 모든 ul 요소 찾기
    print("\n=== 모든 UL 요소 ===")
    uls = soup.find_all('ul')
    print(f"총 {len(uls)}개의 ul 요소 발견")
    
    for i, ul in enumerate(uls[:5]):
        items = ul.find_all('li')
        if len(items) > 0:
            first_item = items[0].get_text().strip()
            print(f"UL {i+1}: {len(items)}개 항목, 첫 번째: {first_item[:100]}...")
            
            # 연도 패턴이 있는지 확인
            if re.search(r'\d{3,4}년?', first_item):
                print(f"  → 연도 패턴 발견!")

if __name__ == "__main__":
    debug_wikipedia_page()