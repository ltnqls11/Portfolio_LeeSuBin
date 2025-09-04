import pandas as pd
from datetime import datetime

# 예시 환자 진료 기록 (SOAP 형식)
records = [
    {
        "patient": "홍길동",
        "date": "2025-07-10",
        "subjective": "왼쪽 무릎 통증 (VAS 6)",
        "objective": "ROM 제한, 굴곡 90도",
        "assessment": "슬관절 수술 후 회복 지연",
        "plan": "운동치료 30분 주 3회 (2주), 냉찜질 병행"
    },
    {
        "patient": "홍길동",
        "date": "2025-07-24",
        "subjective": "통증 감소 (VAS 3)",
        "objective": "ROM 120도까지 증가",
        "assessment": "회복 양호, 통증 완화",
        "plan": "운동치료 주 2회로 조정, 고유수용성 훈련 추가"
    }
]

# DataFrame으로 변환
df = pd.DataFrame(records)

# 날짜 순으로 정렬
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

df.reset_index(drop=True, inplace=True)
df.tail(2)  # 최근 두 번의 진료기록 비교용 출력
