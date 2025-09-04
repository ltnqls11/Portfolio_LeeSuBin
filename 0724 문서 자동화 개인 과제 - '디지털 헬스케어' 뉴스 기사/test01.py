# 1. 뉴스 기사 수집 (크롤링)
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

def get_naver_news_api(query, page=1):
    """네이버 뉴스 API 사용 (더 안정적)"""
    try:
        # 네이버 개발자 센터에서 발급받은 API 키가 필요하지만, 
        # 여기서는 RSS 피드를 사용하는 대안 방법을 시도
        print(f"🔍 네이버 뉴스 RSS 검색 중: {query}")
        
        # 네이버 뉴스 RSS 피드 URL
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=105&listType=title&date=20240724"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml'
        }
        
        # RSS 파싱 시도
        try:
            import feedparser
            feed = feedparser.parse(rss_url)
            
            articles = []
            for entry in feed.entries[:10]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link
                })
            
            if articles:
                print(f"✅ RSS로 {len(articles)}개 기사 수집")
                return articles
                
        except ImportError:
            print("⚠️ feedparser 라이브러리가 없습니다.")
        except Exception as e:
            print(f"⚠️ RSS 파싱 오류: {e}")
        
        return []
        
    except Exception as e:
        print(f"❌ 네이버 뉴스 API 오류: {e}")
        return []

def get_alternative_news_sources(query):
    """대안 뉴스 소스들 시도"""
    articles = []
    
    # 1. 다음 뉴스 시도
    try:
        print(f"🔍 다음 뉴스 검색 시도: {query}")
        encoded_query = urllib.parse.quote(query)
        daum_url = f"https://search.daum.net/search?w=news&q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        response = requests.get(daum_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 다음 뉴스 구조에 맞는 셀렉터
            news_items = soup.select('.c-item-doc')
            
            for item in news_items[:5]:
                try:
                    title_elem = item.select_one('.tit-g')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '')
                        
                        if title and link:
                            articles.append({
                                'title': title,
                                'link': link
                            })
                except:
                    continue
            
            if articles:
                print(f"✅ 다음 뉴스에서 {len(articles)}개 기사 수집")
                return articles
                
    except Exception as e:
        print(f"⚠️ 다음 뉴스 오류: {e}")
    
    # 2. 구글 뉴스 시도
    try:
        print(f"🔍 구글 뉴스 검색 시도: {query}")
        encoded_query = urllib.parse.quote(f"{query} site:news.naver.com OR site:news.joins.com OR site:news.chosun.com")
        google_url = f"https://www.google.com/search?q={encoded_query}&tbm=nws&hl=ko"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9'
        }
        
        response = requests.get(google_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 구글 뉴스 결과 파싱
            news_items = soup.select('div[data-ved]')
            
            for item in news_items[:5]:
                try:
                    title_elem = item.select_one('h3')
                    link_elem = item.select_one('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem.get('href', '')
                        
                        if title and link and 'http' in link:
                            articles.append({
                                'title': title,
                                'link': link
                            })
                except:
                    continue
            
            if articles:
                print(f"✅ 구글 뉴스에서 {len(articles)}개 기사 수집")
                return articles
                
    except Exception as e:
        print(f"⚠️ 구글 뉴스 오류: {e}")
    
    return articles

def get_naver_news(query, page=1):
    """네이버 뉴스 검색 (우회 방법 포함)"""
    print(f"🔍 뉴스 검색 시작: {query}")
    
    # 방법 1: 대안 뉴스 소스 시도
    articles = get_alternative_news_sources(query)
    if articles:
        return articles
    
    # 방법 2: 네이버 뉴스 API/RSS 시도
    articles = get_naver_news_api(query, page)
    if articles:
        return articles
    
    # 방법 3: 간단한 우회 시도 (User-Agent 변경, 딜레이 추가)
    try:
        print("🔄 우회 방법으로 네이버 뉴스 시도...")
        
        # 다양한 User-Agent 시도
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        for ua in user_agents:
            try:
                time.sleep(2)  # 딜레이 추가
                
                encoded_query = urllib.parse.quote(query)
                url = f"https://search.naver.com/search.naver?where=news&query={encoded_query}"
                
                headers = {
                    'User-Agent': ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200 and '차단' not in response.text:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 기사 링크 찾기
                    links = soup.find_all('a', href=True)
                    articles = []
                    
                    for link in links:
                        href = link.get('href', '')
                        title = link.get_text(strip=True)
                        
                        # 뉴스 링크 필터링
                        if ('news.naver.com' in href or 'n.news.naver.com' in href) and len(title) > 10:
                            articles.append({
                                'title': title,
                                'link': href
                            })
                    
                    if articles:
                        print(f"✅ 우회 방법으로 {len(articles[:5])}개 기사 수집")
                        return articles[:5]
                        
            except Exception as e:
                print(f"⚠️ User-Agent {ua[:20]}... 실패: {e}")
                continue
                
    except Exception as e:
        print(f"❌ 우회 시도 실패: {e}")
    
    print("⚠️ 모든 네이버 뉴스 수집 방법 실패")
    return []

# 대안 뉴스 소스 추가
def get_sample_news():
    """샘플 뉴스 데이터 (네이버 접근 불가시 사용)"""
    return [
        {
            'title': '디지털 헬스케어 시장, AI 기술로 급성장',
            'link': 'https://example.com/news1',
            'content': '인공지능 기술을 활용한 디지털 헬스케어 시장이 급속도로 성장하고 있다. 원격 진료, 웨어러블 디바이스, 건강 모니터링 앱 등이 주요 성장 동력이 되고 있으며, 특히 코로나19 이후 비대면 의료 서비스에 대한 수요가 크게 증가했다. 전문가들은 향후 5년간 연평균 25% 이상의 성장률을 보일 것으로 전망한다고 밝혔다.'
        },
        {
            'title': '웨어러블 디바이스로 건강 관리 혁신',
            'link': 'https://example.com/news2', 
            'content': '스마트워치와 피트니스 트래커 등 웨어러블 디바이스가 개인 건강 관리의 새로운 패러다임을 제시하고 있다. 실시간 심박수 모니터링, 수면 패턴 분석, 운동량 측정 등의 기능을 통해 사용자들이 자신의 건강 상태를 지속적으로 관찰할 수 있게 되었다. 의료진들도 이러한 데이터를 활용해 더 정확한 진단과 치료 계획을 수립할 수 있다.'
        },
        {
            'title': '원격 진료 플랫폼 확산으로 의료 접근성 향상',
            'link': 'https://example.com/news3',
            'content': '코로나19 팬데믹을 계기로 원격 진료 서비스가 본격화되면서 의료 접근성이 크게 향상되고 있다. 특히 거동이 불편한 환자나 지방 거주자들에게 큰 도움이 되고 있으며, 의료진 역시 효율적인 환자 관리가 가능해졌다. 정부는 원격 진료 관련 규제를 완화하고 디지털 헬스케어 생태계 조성에 적극 나서고 있다.'
        },
        {
            'title': 'AI 진단 시스템, 의료진 업무 효율성 크게 향상',
            'link': 'https://example.com/news4',
            'content': '인공지능 기반 의료 진단 시스템이 의료진의 업무 효율성을 크게 향상시키고 있다. 영상 판독, 병리 진단, 약물 처방 등 다양한 영역에서 AI가 활용되면서 진단 정확도가 높아지고 의료 오류가 감소하고 있다. 특히 희귀 질환 진단에서 AI의 도움으로 조기 발견율이 30% 이상 증가한 것으로 나타났다.'
        },
        {
            'title': '디지털 치료제 시장 급성장, 새로운 치료 패러다임 제시',
            'link': 'https://example.com/news5',
            'content': '앱 기반 디지털 치료제가 전통적인 약물 치료의 대안으로 주목받고 있다. 정신건강, 중독 치료, 만성질환 관리 등의 분야에서 디지털 치료제의 효과가 입증되면서 시장 규모가 급속히 확대되고 있다. FDA 승인을 받은 디지털 치료제도 늘어나고 있어 향후 의료 패러다임의 변화가 예상된다.'
        }
    ]

def get_google_news(query):
    """구글 뉴스 검색 (대안)"""
    try:
        import feedparser
        
        # 구글 뉴스 RSS 피드 사용
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        print(f"🔍 구글 뉴스 RSS 검색 중: {query}")
        
        feed = feedparser.parse(rss_url)
        articles = []
        
        for entry in feed.entries[:10]:  # 최대 10개
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.get('published', ''),
                'summary': entry.get('summary', '')
            })
        
        print(f"✅ 구글 뉴스에서 {len(articles)}개 기사 수집")
        return articles
        
    except ImportError:
        print("⚠️ feedparser가 설치되지 않았습니다. (pip install feedparser)")
        return []
    except Exception as e:
        print(f"❌ 구글 뉴스 수집 오류: {e}")
        return []

print("🚀 뉴스 수집 시작...")

# 1차 시도: 네이버 뉴스
articles = get_naver_news("디지털 헬스케어", page=1)

# 2차 시도: 구글 뉴스 (네이버 실패시)
if not articles:
    print("⚠️ 네이버 뉴스 수집 실패. 구글 뉴스를 시도합니다...")
    articles = get_google_news("디지털 헬스케어")

# 3차 시도: 샘플 데이터 사용 (모든 방법 실패시)
if not articles:
    print("⚠️ 온라인 뉴스 수집 실패. 샘플 데이터를 사용합니다...")
    sample_articles = get_sample_news()
    
    # 샘플 데이터를 기존 형식에 맞게 변환
    articles = []
    for sample in sample_articles:
        articles.append({
            'title': sample['title'],
            'link': sample['link']
        })
    
    print(f"✅ 샘플 데이터 {len(articles)}개 로드 완료")

if not articles:
    print("❌ 모든 방법으로 기사를 수집할 수 없습니다. 프로그램을 종료합니다.")
    exit()

print(f"🎉 총 {len(articles)}개 기사 수집 성공!")

# 2. 기사 본문 수집
def extract_article_text(url):
    """기사 본문 텍스트 추출"""
    try:
        print(f"📄 본문 추출 중: {url[:50]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 다양한 본문 셀렉터 시도 (매체별로 다름)
        content_selectors = [
            'div#dic_area',           # 네이버 뉴스
            'div.newsct_article',     # 네이버 뉴스 (새 구조)
            'div#articleBodyContents', # 네이버 뉴스 (구 구조)
            'article',                # 일반적인 article 태그
            'div.article_body',       # 일부 언론사
            'div.news_body',          # 일부 언론사
            'div.article-body',       # 일부 언론사
            'div.content',            # 일반적인 content
            'div.post-content',       # 블로그형
            'div.entry-content'       # 워드프레스형
        ]
        
        content_div = None
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                print(f"✅ 본문 발견: {selector}")
                break
        
        if not content_div:
            # 마지막 시도: p 태그들 수집
            paragraphs = soup.find_all('p')
            if paragraphs:
                text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                print(f"✅ p 태그로 본문 추출 ({len(text)} 문자)")
                return text[:2000]  # 최대 2000자
            else:
                print("⚠️ 본문을 찾을 수 없습니다.")
                return ''
        
        # 불필요한 요소 제거
        for unwanted in content_div.find_all(['script', 'style', 'iframe', 'ins', 'aside']):
            unwanted.decompose()
        
        text = content_div.get_text(separator=' ', strip=True)
        
        # 텍스트 정리
        text = ' '.join(text.split())  # 공백 정리
        text = text.replace('\n', ' ').replace('\t', ' ')
        
        print(f"✅ 본문 추출 완료 ({len(text)} 문자)")
        return text[:2000]  # 최대 2000자로 제한
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
        return ''
    except Exception as e:
        print(f"❌ 본문 추출 오류: {e}")
        return ''

# 3. 텍스트 요약 (TextRank)
def summarize_text(text, ratio=0.3):
    """텍스트 요약 (여러 방법 시도)"""
    if not text or len(text.strip()) < 100:
        print("⚠️ 텍스트가 너무 짧아 요약할 수 없습니다.")
        return text[:200] if text else ''
    
    try:
        # 방법 1: gensim 사용
        from gensim.summarization import summarize
        summary = summarize(text, ratio=ratio)
        if summary:
            print(f"✅ gensim으로 요약 완료 ({len(summary)} 문자)")
            return summary
    except ImportError:
        print("⚠️ gensim이 설치되지 않았습니다.")
    except Exception as e:
        print(f"⚠️ gensim 요약 오류: {e}")
    
    try:
        # 방법 2: sumy 사용 (대안)
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.text_rank import TextRankSummarizer
        
        parser = PlaintextParser.from_string(text, Tokenizer("korean"))
        summarizer = TextRankSummarizer()
        sentences = summarizer(parser.document, 3)  # 3문장 요약
        summary = ' '.join([str(sentence) for sentence in sentences])
        
        if summary:
            print(f"✅ sumy로 요약 완료 ({len(summary)} 문자)")
            return summary
    except ImportError:
        print("⚠️ sumy가 설치되지 않았습니다.")
    except Exception as e:
        print(f"⚠️ sumy 요약 오류: {e}")
    
    # 방법 3: 간단한 문장 추출 (백업)
    try:
        sentences = text.split('.')
        # 길이가 적당한 문장들 선택
        good_sentences = [s.strip() for s in sentences if 20 < len(s.strip()) < 200]
        
        if good_sentences:
            # 처음 2-3개 문장 선택
            summary = '. '.join(good_sentences[:3]) + '.'
            print(f"✅ 간단 요약 완료 ({len(summary)} 문자)")
            return summary
        else:
            # 원본 텍스트의 처음 부분 반환
            summary = text[:300] + '...' if len(text) > 300 else text
            print(f"✅ 텍스트 일부 반환 ({len(summary)} 문자)")
            return summary
            
    except Exception as e:
        print(f"❌ 요약 실패: {e}")
        return text[:200] if text else ''

# 4. 키워드 추출 (KeyBERT)
def extract_keywords(text, top_n=5):
    """키워드 추출 (여러 방법 시도)"""
    if not text or len(text.strip()) < 50:
        print("⚠️ 텍스트가 너무 짧아 키워드를 추출할 수 없습니다.")
        return []
    
    try:
        # 방법 1: KeyBERT 사용
        from keybert import KeyBERT
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(text, top_n=top_n, stop_words='english')
        result = [kw[0] for kw in keywords]
        print(f"✅ KeyBERT로 키워드 추출 완료: {result}")
        return result
    except ImportError:
        print("⚠️ KeyBERT가 설치되지 않았습니다.")
    except Exception as e:
        print(f"⚠️ KeyBERT 키워드 추출 오류: {e}")
    
    try:
        # 방법 2: konlpy 사용 (한국어 형태소 분석)
        from konlpy.tag import Okt
        from collections import Counter
        import re
        
        okt = Okt()
        # 한국어 텍스트에서 명사만 추출
        nouns = okt.nouns(text)
        # 길이가 2 이상인 명사만 선택
        filtered_nouns = [noun for noun in nouns if len(noun) >= 2]
        # 빈도수 계산
        noun_counts = Counter(filtered_nouns)
        # 상위 키워드 선택
        keywords = [word for word, count in noun_counts.most_common(top_n)]
        print(f"✅ konlpy로 키워드 추출 완료: {keywords}")
        return keywords
    except ImportError:
        print("⚠️ konlpy가 설치되지 않았습니다.")
    except Exception as e:
        print(f"⚠️ konlpy 키워드 추출 오류: {e}")
    
    try:
        # 방법 3: 간단한 단어 빈도 분석 (백업)
        import re
        from collections import Counter
        
        # 한글 단어만 추출 (2글자 이상)
        korean_words = re.findall(r'[가-힣]{2,}', text)
        
        # 불용어 제거
        stopwords = ['것이', '있는', '하는', '되는', '같은', '많은', '이런', '그런', '저런', 
                    '이것', '그것', '저것', '여기', '거기', '저기', '때문', '통해', '위해',
                    '대한', '관련', '경우', '때문에', '이후', '이전', '현재', '오늘', '어제']
        
        filtered_words = [word for word in korean_words if word not in stopwords]
        
        # 빈도수 계산
        word_counts = Counter(filtered_words)
        keywords = [word for word, count in word_counts.most_common(top_n)]
        
        print(f"✅ 간단 키워드 추출 완료: {keywords}")
        return keywords
        
    except Exception as e:
        print(f"❌ 키워드 추출 실패: {e}")
        return []

# 5. 전체 파이프라인 실행
import pandas as pd
import time
import os

def main():
    """메인 실행 함수"""
    print("\n" + "="*60)
    print("📰 뉴스 기사 분석 파이프라인 시작")
    print("="*60)
    
    if not articles:
        print("❌ 분석할 기사가 없습니다.")
        return
    
    results = []
    total_articles = min(len(articles), 5)  # 최대 5개 기사 처리
    
    print(f"📊 총 {total_articles}개 기사를 처리합니다...\n")
    
    for i, article in enumerate(articles[:total_articles], 1):
        print(f"\n[{i}/{total_articles}] 기사 처리 중...")
        print(f"📰 제목: {article['title'][:50]}...")
        
        try:
            title = article['title']
            link = article['link']
            
            # 본문 추출
            text = extract_article_text(link)
            if not text:
                print("⚠️ 본문을 추출할 수 없어 건너뜁니다.")
                continue
            
            # 요약 생성
            print("📝 요약 생성 중...")
            summary = summarize_text(text)
            
            # 키워드 추출
            print("🔍 키워드 추출 중...")
            keywords = extract_keywords(text)
            
            # 결과 저장
            result = {
                'title': title,
                'link': link,
                'text_length': len(text),
                'summary': summary if summary else '요약 생성 실패',
                'keywords': ', '.join(keywords) if keywords else '키워드 추출 실패'
            }
            
            results.append(result)
            print(f"✅ 기사 {i} 처리 완료")
            
            # 서버 부담 줄이기
            if i < total_articles:
                print("⏳ 1초 대기 중...")
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ 기사 {i} 처리 중 오류: {e}")
            continue
    
    # 결과 저장
    if results:
        try:
            df = pd.DataFrame(results)
            csv_filename = "digital_healthcare_news.csv"
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            
            print(f"\n" + "="*60)
            print("✅ 분석 완료!")
            print(f"📁 결과 파일: {csv_filename}")
            print(f"📊 처리된 기사 수: {len(results)}개")
            print("="*60)
            
            # 결과 미리보기
            print("\n📋 결과 미리보기:")
            for i, result in enumerate(results, 1):
                print(f"\n[{i}] {result['title'][:50]}...")
                print(f"    📝 요약: {result['summary'][:100]}...")
                print(f"    🏷️ 키워드: {result['keywords']}")
                print(f"    📏 본문 길이: {result['text_length']}자")
            
        except Exception as e:
            print(f"❌ CSV 파일 저장 오류: {e}")
            
            # 백업: 텍스트 파일로 저장
            try:
                with open("digital_healthcare_news_backup.txt", "w", encoding="utf-8") as f:
                    f.write("디지털 헬스케어 뉴스 분석 결과\n")
                    f.write("="*50 + "\n\n")
                    
                    for i, result in enumerate(results, 1):
                        f.write(f"[{i}] {result['title']}\n")
                        f.write(f"링크: {result['link']}\n")
                        f.write(f"요약: {result['summary']}\n")
                        f.write(f"키워드: {result['keywords']}\n")
                        f.write("-" * 50 + "\n\n")
                
                print("💾 백업 파일로 저장됨: digital_healthcare_news_backup.txt")
                
            except Exception as backup_error:
                print(f"❌ 백업 파일 저장도 실패: {backup_error}")
    else:
        print("\n❌ 처리된 기사가 없습니다.")

# 프로그램 실행
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 프로그램 실행 중 오류: {e}")
        print("🔧 문제가 지속되면 필요한 라이브러리를 설치해주세요:")
        print("   pip install requests beautifulsoup4 pandas gensim keybert konlpy sumy")
    finally:
        print("\n👋 프로그램을 종료합니다.")
