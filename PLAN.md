# Team 5 전력수요 예측 프로젝트 분석 계획

이 파일은 패키지에 잘못 포함되어 있던 다른 프로젝트 계획을 대체한다. 현재 완료된 96시간 감사 분석과 전체 데이터 복구 후 수행할 작업을 구분한다.

## 현재 완료

- [x] `reproduce_analysis.py`를 확장한 실행형 Jupyter Notebook 작성
- [x] 입력 데이터 SHA-256과 중복 파일 확인
- [x] 스키마·결측·중복·시간간격·물리범위 검사
- [x] 기술통계, 날짜·시간대 패턴, 피크, 램프, 자기상관 분석
- [x] 기상 원상관과 날짜·시간대 보정 민감도 분석
- [x] 가능한 3개 날짜의 동일 24h day-ahead 백테스트
- [x] 편향·과소예측률·피크 MAE·fold 변동성 추가
- [x] 관측기상 외삽 스트레스와 음수예측 점검
- [x] 임시 SAW와 10,000회 가중치 민감도
- [x] Markdown 보고서, 표 25개, 그림 10개 생성
- [x] 빈 커널 순차 실행 검증

## 현재 결론

- 기존 XGBoost 결과는 전체 데이터 누락으로 재현 불가다.
- 24h seasonal naive의 3-fold 전체 sMAPE는 6.5255%이며 날짜별 범위는 2.6433~10.2297%다.
- 복잡한 모델의 우위가 없고, 가중치에 따라 임시 1위가 바뀌므로 모델 승인을 보류한다.

## 전체 데이터 복구 후 작업

1. KPX·AWS·KOSIS 원시자료, 가중치, merged 데이터, 예보기상 vintage를 확보한다.
2. 수요 단위·배율·시간대·잠정치 수정여부를 원천과 대조한다.
3. KPX 시간집계, 관측소 매핑, 공간가중, 결측처리를 재작성하고 단위테스트를 추가한다.
4. 발행시각 이전 정보만 사용하는 feature contract를 만든다.
5. lag-24, lag-168, 동일요일·시간 평균을 필수 기준선으로 둔다.
6. 개발기간 expanding rolling-origin과 마지막 6~12개월 final test를 분리한다.
7. 예보기상과 관측기상 oracle을 분리하고 피크·휴일·계절·극한기상 subgroup을 평가한다.
8. block bootstrap, 충분한 test 길이의 DM 검정, 예측구간 coverage를 보고한다.
9. 실제 비용계수와 모델 운영비로 비용편익을 계산한다.
10. 채택 게이트를 모두 통과한 경우에만 운영모델을 선정한다.

## 고정 산출물

- `team5_expanded_analysis.ipynb`
- `team5_analysis_report.md`
- `analysis_outputs/tables/*.csv`
- `analysis_outputs/figures/*.png`
- `requirements.txt`
