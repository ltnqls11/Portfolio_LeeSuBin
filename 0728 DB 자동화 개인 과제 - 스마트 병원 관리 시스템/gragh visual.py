import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 기본 한글 폰트
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

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
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

# 시각화 데이터 준비
dates = df["date"]
rom_values = [90, 120]  # 굴곡 각도 (예시)
pain_values = [6, 3]    # VAS 통증 점수

# 시각화: ROM & VAS
fig, ax1 = plt.subplots(figsize=(10, 5))

# ROM - 선 그래프 (왼쪽 축)
color = 'tab:blue'
ax1.set_xlabel('진료일')
ax1.set_ylabel('ROM (도)', color=color)
ax1.plot(dates, rom_values, color=color, marker='o', label='ROM')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(0, 150)

# VAS - 선 그래프 (오른쪽 축)
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('통증 점수 (VAS)', color=color)
ax2.plot(dates, pain_values, color=color, marker='s', linestyle='--', label='VAS')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(0, 10)

# 제목 및 그리드
plt.title('진료 경과 비교 (ROM & 통증)')
fig.tight_layout()
plt.grid(True)
plt.show()
