# n8n Import 오류 해결 가이드

## 🚨 문제 상황

n8n에서 워크플로우를 import할 때 다음과 같은 오류가 발생합니다:
```
Problem importing workflow
propertyValues[itemName] is not iterable
```

## 🔧 해결 방법

### 방법 1: 수정된 워크플로우 사용 (권장)

`n8n_rest_reminder_workflow_fixed.json` 파일을 사용하세요. 이 파일은 n8n 최신 버전과 호환되도록 수정되었습니다.

### 방법 2: 간단한 버전 사용

`n8n_simple_workflow.json` 파일을 사용하세요. 이 버전은 복잡한 구조를 단순화하여 호환성 문제를 방지합니다.

## 📁 수정된 파일들

1. **`n8n_rest_reminder_workflow_fixed.json`** - 전체 기능 포함, 수정된 버전
2. **`n8n_simple_workflow.json`** - 핵심 기능만 포함, 간단한 버전

## ⚠️ 원본 파일의 문제점

원본 `n8n_rest_reminder_workflow.json`에서 다음 부분들이 n8n 최신 버전과 호환성 문제를 일으켰습니다:

- 복잡한 노드 연결 구조
- 일부 메타데이터 필드
- 태그 정보의 복잡한 구조

## 🚀 수정된 워크플로우 사용법

### 1단계: 파일 선택

- **전체 기능 필요**: `n8n_rest_reminder_workflow_fixed.json` 사용
- **간단한 기능만**: `n8n_simple_workflow.json` 사용

### 2단계: n8n에 Import

1. n8n 웹 인터페이스 접속
2. "Import from file" 클릭
3. 수정된 JSON 파일 선택
4. Import 실행

### 3단계: 환경변수 설정

n8n 웹 인터페이스에서:
1. Settings → Environment Variables
2. 다음 변수 추가:

| 변수명 | 값 |
|--------|-----|
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/services/...` |
| `GMAIL_ADDRESS` | `your-email@gmail.com` |

### 4단계: 인증 설정

#### Slack 설정
- Slack 노드에서 "Add Credential" 클릭
- Webhook URL 입력

#### Gmail 설정
- Gmail 노드에서 "Add Credential" 클릭
- OAuth2 인증 설정

## 🔍 간단 버전 vs 전체 버전

| 기능 | 간단 버전 | 전체 버전 |
|------|-----------|-----------|
| 25분마다 알림 | ✅ | ✅ |
| 업무시간 필터링 | ✅ | ✅ |
| Slack 알림 | ✅ | ✅ |
| Gmail 알림 | ✅ | ✅ |
| 올바른 자세 가이드 | ✅ | ✅ |
| VDT 증후군별 팁 | ✅ | ✅ |
| 복잡한 데이터 처리 | ❌ | ✅ |
| 상세한 로깅 | ❌ | ✅ |

## 💡 권장사항

1. **처음 사용자**: 간단 버전부터 시작
2. **고급 사용자**: 전체 버전 사용
3. **문제 발생 시**: 간단 버전으로 전환

## 🚨 여전히 오류가 발생한다면

### 추가 해결 방법

1. **n8n 버전 확인**
   ```bash
   n8n --version
   ```

2. **최신 버전으로 업데이트**
   ```bash
   npm update -g n8n
   ```

3. **수동으로 워크플로우 생성**
   - 빈 워크플로우 생성
   - 노드들을 하나씩 추가
   - 설정값 복사

### 수동 생성 순서

1. **Cron Trigger 노드**
   - 25분마다 실행 설정

2. **Code 노드**
   - 메시지 생성 로직 복사

3. **Slack 노드**
   - Webhook URL 설정

4. **Gmail 노드**
   - OAuth2 인증 설정

## 📞 지원

여전히 문제가 발생한다면:
1. n8n 버전 정보 확인
2. 오류 메시지 전체 내용 공유
3. 사용 중인 운영체제 정보 제공

## 🔄 워크플로우 업데이트

향후 n8n 버전 업데이트 시:
1. 기존 워크플로우 백업
2. 새 버전에서 테스트
3. 필요시 재생성

---

**💡 팁**: 간단한 버전부터 시작하여 점진적으로 기능을 추가하는 것이 안전합니다!
