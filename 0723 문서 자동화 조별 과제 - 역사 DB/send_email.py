import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import sys

def send_html_email():
    """HTML 이메일을 안전하게 발송합니다."""
    
    # 이메일 설정
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "ltnqls11@gmail.com"
    sender_password = "tpwsmfafqmuizrgu"  # 앱 비밀번호 사용 권장
    recipient_email = "ltnqls11@gmail.com"
    
    # HTML 내용
    html_content = """\
    <html>
      <head>
        <meta charset="utf-8">
        <title>한국사 대시보드 알림</title>
      </head>
      <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h1 style="color: #2c3e50;">📜 한국사 대시보드 알림</h1>
          <p>안녕하세요!</p>
          <p>한국사 대시보드가 성공적으로 실행되었습니다.</p>
          
          <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #495057;">📊 주요 기능</h3>
            <ul>
              <li>🏛️ 시대별 필터링</li>
              <li>👤 인물별 검색</li>
              <li>⚔️ 사건 유형별 분류</li>
              <li>📈 시각화 차트</li>
            </ul>
          </div>
          
          <p style="color: #6c757d; font-size: 14px;">
            이 이메일은 한국사 대시보드 시스템에서 자동으로 발송되었습니다.
          </p>
        </div>
      </body>
    </html>
    """
    
    try:
        # 이메일 메시지 생성
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "📜 한국사 대시보드 - HTML 이메일 테스트"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # HTML 파트 생성
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 텍스트 버전도 추가 (호환성을 위해)
        text_content = """
        한국사 대시보드 알림
        
        안녕하세요!
        한국사 대시보드가 성공적으로 실행되었습니다.
        
        주요 기능:
        - 시대별 필터링
        - 인물별 검색  
        - 사건 유형별 분류
        - 시각화 차트
        
        이 이메일은 한국사 대시보드 시스템에서 자동으로 발송되었습니다.
        """
        
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        msg.attach(text_part)
        
        print("📧 이메일 발송 준비 중...")
        
        # SMTP 서버 연결 및 이메일 발송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("🔐 SMTP 서버 연결 중...")
            server.starttls()  # TLS 암호화 시작
            
            print("🔑 로그인 중...")
            server.login(sender_email, sender_password)
            
            print("📤 이메일 발송 중...")
            server.sendmail(sender_email, recipient_email, msg.as_string())
            
        print("✅ 이메일이 성공적으로 발송되었습니다!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ 인증 오류: 이메일 주소나 비밀번호를 확인하세요.")
        print("💡 Gmail의 경우 앱 비밀번호를 사용해야 합니다.")
        return False
        
    except smtplib.SMTPRecipientsRefused:
        print("❌ 수신자 오류: 받는 사람 이메일 주소를 확인하세요.")
        return False
        
    except smtplib.SMTPServerDisconnected:
        print("❌ 서버 연결 오류: SMTP 서버 설정을 확인하세요.")
        return False
        
    except Exception as e:
        print(f"❌ 이메일 발송 중 오류 발생: {e}")
        return False

def test_email_connection():
    """이메일 서버 연결을 테스트합니다."""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    try:
        print("🔍 SMTP 서버 연결 테스트 중...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            print("✅ SMTP 서버 연결 성공!")
            return True
    except Exception as e:
        print(f"❌ SMTP 서버 연결 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("📧 이메일 발송 프로그램 시작")
    print("=" * 40)
    
    # 연결 테스트
    if not test_email_connection():
        print("⚠️ 서버 연결에 실패했습니다. 네트워크 상태를 확인하세요.")
        return
    
    # 사용자 확인
    choice = input("이메일을 발송하시겠습니까? (y/n): ").lower().strip()
    
    if choice == 'y' or choice == 'yes':
        success = send_html_email()
        
        if success:
            print("\n🎉 이메일 발송 완료!")
        else:
            print("\n❌ 이메일 발송 실패!")
    else:
        print("📧 이메일 발송이 취소되었습니다.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 프로그램 실행 중 오류: {e}")