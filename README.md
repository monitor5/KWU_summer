# Team 5 전력수요 예측 프로젝트 분석 패키지

## 기준 산출물

- [`team5_analysis_report.md`](team5_analysis_report.md): 확장 데이터 분석·코드감사·의사결정 해석 보고서
- [`team5_expanded_analysis.ipynb`](team5_expanded_analysis.ipynb): 실행 완료된 재현 노트북
- [`analysis_outputs/tables/`](analysis_outputs/tables/): 노트북이 생성한 분석표 25개
- [`analysis_outputs/figures/`](analysis_outputs/figures/): 노트북이 생성한 시각화 10개
- `sample_data.csv`: 패키지에 실제 포함된 96시간 샘플
- `requirements.txt`: 노트북 실행 의존성

기존 `team5_source_analysis_report.docx`, PDF, `reproduce_analysis.py`, `tables/`, `figures/`는 초안 비교용으로 보존했다. 새 분석의 기준은 Markdown 보고서와 IPYNB다.

## 재현

```bash
python -m pip install -r requirements.txt
jupyter lab team5_expanded_analysis.ipynb
```

노트북에서 **Kernel Restart → Run All**을 실행하면 `analysis_outputs/`가 다시 생성된다.

## 핵심 검증값

- 표본: 2025-04-21 00:00 ~ 2025-04-24 23:00, 96시간
- 입력 SHA-256: `fb214f92f1ea57ff0f5ce5f64f6be61ee139f2d89f1041fff1a4f3b47f3b82a4`
- `sample_data.csv`와 팀 폴더의 `data.csv`는 바이트 단위로 동일하다.
- 24h seasonal naive 3-fold 전체 sMAPE: 6.5255%
- fold sMAPE: 10.2297%, 6.7035%, 2.6433%
- 실행 완료 코드 셀: 15개, 오류 출력 0건

## 해석 주의

- 전체 학습 데이터와 원시·중간 파일이 없어 기존 XGBoost 결과는 독립 재현되지 않았다.
- 수요 단위·배율과 타임스탬프 시간대는 패키지만으로 확정할 수 없다.
- 샘플은 월~목 4일뿐이므로 계절·휴일·주말·극한기상 일반화가 불가능하다.
- 실제 미래 관측기상을 사용한 결과는 운영 성능이 아니라 oracle/스트레스 실험이다.
