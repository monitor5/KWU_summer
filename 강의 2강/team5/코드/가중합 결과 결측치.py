from pathlib import Path
import pandas as pd

# CSV 경로 설정
csv_path = Path("result.csv")  # ← 여기에 실제 파일 이름 입력

# CSV 불러오기
df = pd.read_csv(csv_path, parse_dates=["일시"])

# 일시 정렬
df = df.sort_values("일시").reset_index(drop=True)

# 시간 차이 계산
time_diff = df["일시"].diff().dropna()

# 1시간 간격인지 확인 (결측 시간 탐지)
missing_times = df["일시"].shift() + pd.Timedelta(hours=1)
gap_mask = df["일시"] != missing_times

# 결측 시간 출력
for prev, curr in zip(df["일시"].shift()[gap_mask], df["일시"][gap_mask]):
    if pd.notnull(prev) and (curr - prev) > pd.Timedelta(hours=1):
        missing_range = pd.date_range(prev + pd.Timedelta(hours=1), curr - pd.Timedelta(hours=1), freq="H")
        for missing in missing_range:
            print(f"❌ 결측된 시간: {missing}")