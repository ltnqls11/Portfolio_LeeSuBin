import pdfplumber
import re
import pandas as pd
import os
import sys

# 선택적 import (라이브러리가 없어도 실행 가능하도록)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    print("⚠️ scikit-learn이 설치되지 않았습니다. TF-IDF 기능을 사용할 수 없습니다.")
    print("💡 설치 방법: pip install scikit-learn")
    SKLEARN_AVAILABLE = False

try:
    from keybert import KeyBERT
    KEYBERT_AVAILABLE = True
except ImportError:
    print("⚠️ KeyBERT가 설치되지 않았습니다. KeyBERT 기능을 사용할 수 없습니다.")
    print("💡 설치 방법: pip install keybert")
    KEYBERT_AVAILABLE = False

try:
    from konlpy.tag import Okt
    KONLPY_AVAILABLE = True
except ImportError:
    print("⚠️ KoNLPy가 설치되지 않았습니다. 한국어 형태소 분석 기능을 사용할 수 없습니다.")
    print("💡 설치 방법: pip install konlpy")
    KONLPY_AVAILABLE = False

# 1. PDF 텍스트 추출
def extract_text_from_pdf(pdf_path):
    """PDF에서 텍스트를 추출합니다."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
    
    try:
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 PDF 페이지 수: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                    else:
                        print(f"⚠️ {i+1}페이지에서 텍스트를 추출할 수 없습니다.")
                except Exception as e:
                    print(f"⚠️ {i+1}페이지 처리 중 오류: {e}")
                    continue
        
        if not full_text.strip():
            raise ValueError("❌ PDF에서 텍스트를 추출할 수 없습니다.")
        
        print(f"✅ 텍스트 추출 완료 (총 {len(full_text)} 문자)")
        return full_text
        
    except Exception as e:
        raise Exception(f"❌ PDF 처리 중 오류 발생: {e}")

# 2. 단원 기준으로 텍스트 분할
def split_by_chapter(text):
    """텍스트를 단원별로 분할합니다."""
    if not text or not text.strip():
        print("⚠️ 입력 텍스트가 비어있습니다.")
        return [], []
    
    # 다양한 패턴 시도
    patterns = [
        r"\n\d{2} [^\n]+",  # 기본 패턴: "01 단원명"
        r"\n\d{1,2}\. [^\n]+",  # "1. 단원명"
        r"\n제\d{1,2}장 [^\n]+",  # "제1장 단원명"
        r"\n단원 \d{1,2} [^\n]+",  # "단원 1 단원명"
    ]
    
    for pattern in patterns:
        headers = re.findall(pattern, text)
        if headers:
            print(f"✅ 패턴 '{pattern}'으로 {len(headers)}개 단원 발견")
            chapters = re.split(pattern, text)
            # 첫 번째 요소는 보통 빈 문자열이므로 제거
            if chapters and not chapters[0].strip():
                chapters = chapters[1:]
            return headers, chapters
    
    print("⚠️ 단원 패턴을 찾을 수 없습니다. 전체 텍스트를 하나의 단원으로 처리합니다.")
    return ["전체 내용"], [text]

# 3. 요약 및 키워드 추출 (TF-IDF)
def extract_keywords_tfidf(docs, top_k=5):
    """TF-IDF를 사용하여 키워드를 추출합니다."""
    if not SKLEARN_AVAILABLE:
        print("⚠️ scikit-learn이 없어 TF-IDF 키워드 추출을 건너뜁니다.")
        return [["키워드 추출 불가"] for _ in docs]
    
    if not docs or all(not doc.strip() for doc in docs):
        print("⚠️ 문서가 비어있어 키워드를 추출할 수 없습니다.")
        return [["내용 없음"] for _ in docs]
    
    try:
        # 한국어 불용어 확장
        korean_stopwords = [
            "것", "수", "등", "이", "그", "의", "가", "을", "를", "에", "와", "과", 
            "도", "는", "은", "한", "하다", "있다", "되다", "같다", "때문", "통해",
            "위해", "대한", "관한", "따라", "위한", "대해", "년", "월", "일"
        ]
        
        tfidf = TfidfVectorizer(
            max_features=500, 
            stop_words=korean_stopwords,
            min_df=1,  # 최소 문서 빈도
            max_df=0.8,  # 최대 문서 빈도
            ngram_range=(1, 2)  # 1-2 단어 조합
        )
        
        tfidf_matrix = tfidf.fit_transform(docs)
        feature_names = tfidf.get_feature_names_out()
        
        keywords = []
        for i in range(tfidf_matrix.shape[0]):
            row = tfidf_matrix[i].toarray().flatten()
            top_indices = row.argsort()[-top_k:][::-1]
            top_keywords = [feature_names[idx] for idx in top_indices if row[idx] > 0]
            
            if not top_keywords:
                top_keywords = ["키워드 없음"]
            
            keywords.append(top_keywords)
        
        print(f"✅ TF-IDF 키워드 추출 완료")
        return keywords
        
    except Exception as e:
        print(f"⚠️ TF-IDF 키워드 추출 중 오류: {e}")
        return [["오류 발생"] for _ in docs]

# 4. KeyBERT 키워드 추출 (선택 사항)
def extract_keywords_keybert(docs, top_k=5):
    """KeyBERT를 사용하여 키워드를 추출합니다."""
    if not KEYBERT_AVAILABLE:
        print("⚠️ KeyBERT가 없어 KeyBERT 키워드 추출을 건너뜁니다.")
        return [["KeyBERT 불가"] for _ in docs]
    
    try:
        kw_model = KeyBERT()
        korean_stopwords = ["것", "수", "등", "이", "그", "의", "가"]
        
        keywords = []
        for doc in docs:
            if not doc.strip():
                keywords.append(["내용 없음"])
                continue
                
            try:
                kw_list = kw_model.extract_keywords(
                    doc, 
                    top_n=top_k, 
                    stop_words=korean_stopwords,
                    use_mmr=True,  # 다양성 증가
                    diversity=0.5
                )
                extracted = [kw[0] for kw in kw_list] if kw_list else ["키워드 없음"]
                keywords.append(extracted)
            except Exception as e:
                print(f"⚠️ KeyBERT 처리 중 오류: {e}")
                keywords.append(["오류 발생"])
        
        print(f"✅ KeyBERT 키워드 추출 완료")
        return keywords
        
    except Exception as e:
        print(f"⚠️ KeyBERT 키워드 추출 중 오류: {e}")
        return [["오류 발생"] for _ in docs]

# 5. 메인 실행 함수
def main():
    """메인 실행 함수"""
    print("📚 한국사 PDF 분석 시작")
    print("=" * 50)
    
    # PDF 파일 경로 설정
    pdf_path = "2026 수능특강_ 한국사.pdf"
    
    try:
        # 1. PDF 텍스트 추출
        print("1️⃣ PDF 텍스트 추출 중...")
        text = extract_text_from_pdf(pdf_path)
        
        # 2. 단원별 분할
        print("2️⃣ 단원별 텍스트 분할 중...")
        headers, chapters = split_by_chapter(text)
        
        if not headers or not chapters:
            print("❌ 단원을 찾을 수 없습니다.")
            return
        
        print(f"✅ {len(headers)}개 단원 발견")
        
        # 3. 텍스트 전처리
        print("3️⃣ 텍스트 전처리 중...")
        chapters_cleaned = []
        for i, chapter in enumerate(chapters):
            if chapter and chapter.strip():
                cleaned = re.sub(r"\s+", " ", chapter.strip())
                chapters_cleaned.append(cleaned)
            else:
                print(f"⚠️ {i+1}번째 단원이 비어있습니다.")
                chapters_cleaned.append("내용 없음")
        
        # 4. 키워드 추출
        print("4️⃣ 키워드 추출 중...")
        keywords = extract_keywords_tfidf(chapters_cleaned)
        
        # 5. 결과 정리
        print("5️⃣ 결과 정리 중...")
        
        # 데이터 길이 맞추기
        min_length = min(len(headers), len(chapters_cleaned), len(keywords))
        
        df = pd.DataFrame({
            "단원 제목": [h.strip() for h in headers[:min_length]],
            "요약 (100자 이내)": [c[:100] + "..." if len(c) > 100 else c 
                              for c in chapters_cleaned[:min_length]],
            "키워드": keywords[:min_length]
        })
        
        # 6. CSV 저장
        output_file = "한국사_단원요약_키워드.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        
        print(f"✅ 분석 완료!")
        print(f"📁 저장된 파일: {output_file}")
        print(f"📊 처리된 단원 수: {len(df)}")
        
        # 결과 미리보기
        print("\n📋 결과 미리보기:")
        print(df.head())
        
    except FileNotFoundError as e:
        print(f"❌ 파일 오류: {e}")
        print("💡 PDF 파일이 현재 디렉토리에 있는지 확인하세요.")
    except Exception as e:
        print(f"❌ 프로그램 실행 오류: {e}")
        import traceback
        traceback.print_exc()

# 실행
if __name__ == "__main__":
    main()
