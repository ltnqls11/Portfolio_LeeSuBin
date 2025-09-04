# 필요 라이브러리 설치
# pip install pandas openpyxl

import smtplib
from email.message import EmailMessage
from pathlib import Path
import os
import glob
from datetime import datetime
import sys

def find_all_report_files():
    """모든 보고서 파일을 찾는 함수"""
    print("\n=== 첨부 파일 검색 중 ===")
    
    # 찾을 파일 패턴들
    file_patterns = {
        'excel': [
            '수원시_부동산_종합보고서_*.xlsx',
            '수원시_부동산_보고서_*.xlsx', 
            '수원시_1년_구별_월별_변동률_*.xlsx',
            '수원시_1년_매매_전세_평균가_*.csv'
        ],
        'charts': [
            '수원시_구별_종합비교_*.png',
            '수원시_부동산_분석_차트_*.png',
            '*구_최근1년_매매_전세_추이_*.png'
        ]
    }
    
    found_files = []
    
    # 엑셀 및 CSV 파일 찾기
    for pattern in file_patterns['excel']:
        files = glob.glob(pattern)
        for file in files:
            if os.path.exists(file):
                found_files.append(file)
                print(f"📊 발견: {file}")
    
    # 차트 파일 찾기
    for pattern in file_patterns['charts']:
        files = glob.glob(pattern)
        for file in files:
            if os.path.exists(file):
                found_files.append(file)
                print(f"📈 발견: {file}")
    
    if not found_files:
        raise FileNotFoundError(
            "첨부할 파일을 찾을 수 없습니다.\n"
            "다음 파일들을 먼저 생성하세요:\n"
            "- test02_demo.py (CSV 데이터)\n"
            "- test04.py (변동률 분석 차트)\n"
            "- test05.py (구별 개별 차트)\n"
            "- test06.py (종합 엑셀 보고서)"
        )
    
    # 파일 크기 순으로 정렬 (큰 파일 먼저)
    found_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
    
    print(f"\n✅ 총 {len(found_files)}개 파일 발견")
    return found_files

def validate_email_config():
    """이메일 설정 검증"""
    print("\n=== 이메일 설정 확인 ===")
    
    # 발신자 Gmail 주소 입력
    email_address = input("발신자 Gmail 주소를 입력하세요: ").strip()
    if not email_address or '@gmail.com' not in email_address:
        raise ValueError("올바른 Gmail 주소를 입력해주세요.")
    
    # 앱 비밀번호 (미리 설정된 값 사용)
    email_password = "tpwsmfafqmuizrgu"
    print(f"✅ 앱 비밀번호: 설정 완료")
    
    # 수신자 이메일 (미리 설정된 값 사용)
    to_email = "ltnqls11@gmail.com"
    print(f"✅ 수신자: {to_email}")
    
    return email_address, email_password, to_email

def create_email_content(attachment_files):
    """이메일 내용 생성"""
    total_size = sum(os.path.getsize(file) for file in attachment_files) / (1024 * 1024)  # MB 단위
    
    content = f"""
안녕하세요,

수원시 주요 구들의 최근 1년간 평균 전세/매매가 분석 보고서를 첨부하여 보내드립니다.

📊 첨부 파일 목록 ({len(attachment_files)}개):
"""
    
    # 파일별 정보 추가
    for i, file_path in enumerate(attachment_files, 1):
        file_name = Path(file_path).name
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        file_type = "📊" if file_path.endswith(('.xlsx', '.csv')) else "📈"
        content += f"{file_type} {i}. {file_name} ({file_size:.2f}MB)\n"
    
    content += f"""
📋 분석 내용:
- 수원시 4개 구별 부동산 가격 분석 (장안구, 권선구, 팔달구, 영통구)
- 최근 1년간 매매/전세 가격 추이 및 변동률
- 구별 비교 차트 및 상세 통계
- 전세가율 분석 및 투자 지표
- 월별 가격 변동 히트맵

💾 총 첨부 파일 크기: {total_size:.2f}MB

첨부된 파일들을 확인해주시기 바랍니다.

감사합니다.
"""
    return content.strip()

def send_email_with_attachments(email_address, email_password, to_email, attachment_files):
    """이메일 전송 함수 (다중 첨부파일 지원)"""
    try:
        print(f"\n=== 이메일 전송 시작 ===")
        
        # 파일 존재 확인 및 크기 검증
        total_size = 0
        valid_files = []
        
        for file_path in attachment_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                total_size += file_size
                valid_files.append(file_path)
                print(f"📎 첨부 준비: {Path(file_path).name} ({file_size:.2f}MB)")
            else:
                print(f"⚠️ 파일 없음: {file_path}")
        
        if not valid_files:
            raise FileNotFoundError("첨부할 파일이 없습니다.")
        
        # 총 파일 크기 확인 (25MB 제한)
        if total_size > 25:
            print(f"⚠️ 총 파일 크기: {total_size:.2f}MB")
            print("📧 Gmail 첨부파일 제한: 25MB")
            # 큰 파일들만 선택 (엑셀 파일 우선)
            valid_files = [f for f in valid_files if f.endswith(('.xlsx', '.csv'))][:3]
            total_size = sum(os.path.getsize(f) for f in valid_files) / (1024 * 1024)
            print(f"📊 주요 파일만 선택: {len(valid_files)}개 ({total_size:.2f}MB)")
        
        # 이메일 메시지 생성
        msg = EmailMessage()
        msg['Subject'] = '수원시 주요 구들의 최근 1년간 평균 전세/매매가'
        msg['From'] = email_address
        msg['To'] = to_email
        
        # 이메일 내용 설정
        email_content = create_email_content(valid_files)
        msg.set_content(email_content)
        
        # 첨부파일 추가
        for file_path in valid_files:
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    file_name = Path(file_path).name
                    
                    # 파일 형식에 따른 MIME 타입 설정
                    if file_path.endswith('.xlsx'):
                        maintype = 'application'
                        subtype = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    elif file_path.endswith('.csv'):
                        maintype = 'text'
                        subtype = 'csv'
                    elif file_path.endswith('.png'):
                        maintype = 'image'
                        subtype = 'png'
                    else:
                        maintype = 'application'
                        subtype = 'octet-stream'
                    
                    msg.add_attachment(
                        file_data,
                        maintype=maintype,
                        subtype=subtype,
                        filename=file_name
                    )
                    print(f"✅ 첨부 완료: {file_name}")
                    
            except Exception as e:
                print(f"❌ 첨부 실패 ({file_name}): {e}")
                continue
        
        # Gmail SMTP 서버 연결 및 발송
        print("📧 Gmail 서버 연결 중...")
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            print("🔐 로그인 중...")
            smtp.login(email_address, email_password)
            
            print("📤 이메일 전송 중...")
            smtp.send_message(msg)
        
        print("✅ 이메일 전송 완료!")
        print(f"📧 발신자: {email_address}")
        print(f"📧 수신자: {to_email}")
        print(f"📎 첨부파일: {len(valid_files)}개 ({total_size:.2f}MB)")
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ 인증 오류: Gmail 계정 정보를 확인해주세요.")
        print("💡 해결 방법:")
        print("1. Gmail 주소가 정확한지 확인")
        print("2. 앱 비밀번호가 올바른지 확인 (일반 비밀번호 아님)")
        print("3. 2단계 인증이 활성화되어 있는지 확인")
        return False
        
    except smtplib.SMTPRecipientsRefused:
        print("❌ 수신자 오류: 받는 사람 이메일 주소를 확인해주세요.")
        return False
        
    except smtplib.SMTPServerDisconnected:
        print("❌ 서버 연결 오류: 네트워크 연결을 확인해주세요.")
        return False
        
    except Exception as e:
        print(f"❌ 이메일 전송 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    try:
        print("=== 수원시 부동산 보고서 이메일 전송 ===")
        
        # 1. 모든 보고서 파일 찾기
        attachment_files = find_all_report_files()
        
        # 2. 이메일 설정 입력
        email_address, email_password, to_email = validate_email_config()
        
        # 3. 전송 확인
        print(f"\n=== 전송 정보 확인 ===")
        print(f"📧 발신자: {email_address}")
        print(f"📧 수신자: {to_email}")
        print(f"📎 첨부파일: {len(attachment_files)}개")
        
        # 첨부파일 목록 표시
        for i, file_path in enumerate(attachment_files[:10], 1):  # 최대 10개만 표시
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            print(f"   {i}. {Path(file_path).name} ({file_size:.2f}MB)")
        
        if len(attachment_files) > 10:
            print(f"   ... 외 {len(attachment_files) - 10}개 파일")
        
        confirm = input("\n이메일을 전송하시겠습니까? (y/n): ").lower().strip()
        if confirm != 'y':
            print("이메일 전송이 취소되었습니다.")
            return
        
        # 4. 이메일 전송
        success = send_email_with_attachments(email_address, email_password, to_email, attachment_files)
        
        if success:
            print("\n🎉 보고서 이메일 전송이 완료되었습니다!")
        else:
            print("\n💥 이메일 전송에 실패했습니다.")
            print("설정을 확인하고 다시 시도해주세요.")
        
        return success
        
    except FileNotFoundError as e:
        print(f"파일 오류: {e}")
    except ValueError as e:
        print(f"설정 오류: {e}")
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        import traceback
     

if __name__ == "__main__":
    result = main()