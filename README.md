# 설비 센서 경보 데모

CSV 기반 설비 센서 데이터를 처리하는 작은 CLI 예제. [`dev-nobiya`](https://github.com/csw9261/dev-nobiya)의 GitHub Issue 처리 과정을 재현하고 결과를 독립 테스트로 검증하기 위한 시연 대상.

`data/equipment_readings.csv`는 기능 시연을 위해 생성한 합성 데이터.

## 현재 기능

CSV 파일을 읽고 설비별 측정 건수를 JSON으로 출력하는 CLI.

```bash
python3 app.py --input data/equipment_readings.csv
python3 -m unittest discover -s tests -v
```

## 예정된 이슈

연속 고온 측정에 대한 경보 탐지 기능 추가 예정. 상세 요구사항은 GitHub Issue로 등록.

수락 테스트는 `acceptance/`에 별도 보관. 현재 버전에서 실패하는 것이 정상이며, 이슈 구현 후 통과 여부 확인에 사용.

```bash
PYTHONPATH=. python3 -m unittest discover -s acceptance -v
```
