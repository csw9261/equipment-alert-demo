"""합성 설비 로그의 기본 집계 및 연속 고온 경보 탐지 CLI."""

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ALERT_THRESHOLD_C = 85.0
"""고온으로 판정하는 최소 온도(섭씨, 이상 포함)."""

ALERT_MIN_CONSECUTIVE = 3
"""경보를 생성하는 최소 연속 고온 측정 건수."""


def load_readings(path: Path) -> list[dict[str, str]]:
    """CSV 측정값을 행별 딕셔너리로 로드."""
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def summarize(readings: list[dict[str, str]]) -> dict[str, object]:
    """전체 측정 건수와 설비별 건수를 집계."""
    counts = Counter(row["machine_id"] for row in readings)
    return {"rows": len(readings), "machines": dict(sorted(counts.items()))}


def detect_alerts(readings: list[dict[str, str]]) -> list[dict[str, object]]:
    """설비별 시간순으로 연속 고온 구간을 찾아 경보 목록 반환.

    `ALERT_THRESHOLD_C` 이상 측정이 `ALERT_MIN_CONSECUTIVE`건 이상 이어지면
    구간당 경보 1건 생성. 빈 값이나 임계값 미만 측정에서 구간 종료.
    결과는 `(machine_id, start_at)` 기준 정렬.
    """
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in readings:
        groups[row["machine_id"]].append(row)

    alerts: list[dict[str, object]] = []
    for machine_id, rows in groups.items():
        # ISO 8601 동일 형식 문자열이므로 문자열 정렬이 시간순과 일치
        rows.sort(key=lambda row: row["timestamp"])
        streak: list[tuple[str, float]] = []

        def flush() -> None:
            if len(streak) >= ALERT_MIN_CONSECUTIVE:
                alerts.append({
                    "machine_id": machine_id,
                    "start_at": streak[0][0],
                    "end_at": streak[-1][0],
                    "consecutive_count": len(streak),
                    "peak_temperature_c": max(value for _, value in streak),
                })
            streak.clear()

        for row in rows:
            raw = row["temperature_c"].strip()
            if raw and float(raw) >= ALERT_THRESHOLD_C:
                streak.append((row["timestamp"], float(raw)))
            else:
                flush()
        flush()

    alerts.sort(key=lambda alert: (alert["machine_id"], alert["start_at"]))
    return alerts


def main() -> None:
    """입력 CSV의 기본 집계를 JSON으로 출력. `--alerts` 지정 시 경보 목록 출력."""
    parser = argparse.ArgumentParser(description="합성 설비 로그 집계")
    parser.add_argument("--input", type=Path, required=True, help="측정 CSV 파일")
    parser.add_argument(
        "--alerts", action="store_true", help="집계 대신 연속 고온 경보 목록 출력"
    )
    args = parser.parse_args()
    readings = load_readings(args.input)
    result = detect_alerts(readings) if args.alerts else summarize(readings)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
