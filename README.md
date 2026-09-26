# 설비 센서 경보 데모

CSV 기반 설비 센서 데이터를 처리하는 작은 CLI 예제. [`dev-nobiya`](https://github.com/csw9261/dev-nobiya)의 GitHub Issue 처리 과정을 재현하고 결과를 독립 테스트로 검증하기 위한 시연 대상.

`data/equipment_readings.csv`는 기능 시연을 위해 생성한 합성 데이터.

## 현재 기능

CSV 파일을 읽고 설비별 측정 건수를 JSON으로 출력하는 CLI. `--alerts` 지정 시 연속 고온 경보 목록을 JSON으로 출력.

```bash
python3 app.py --input data/equipment_readings.csv
python3 app.py --input data/equipment_readings.csv --alerts
python3 -m unittest discover -s tests -v
```

경보 규칙:

- 설비별로 `timestamp` 순서에 따라 판정
- 85도 이상 측정이 3건 이상 연속되면 구간당 경보 1건 생성
- 빈 온도값 또는 85도 미만 측정에서 연속 구간 종료

## 경보 탐지 이슈

연속 고온 측정에 대한 경보 탐지 기능 구현 완료. 상세 요구사항은 GitHub Issue 참조.

수락 테스트는 `acceptance/`에 별도 보관. 이슈 구현 결과의 통과 여부 확인에 사용.

```bash
PYTHONPATH=. python3 -m unittest discover -s acceptance -v
```
