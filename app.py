"""합성 설비 로그의 기본 집계 CLI."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def load_readings(path: Path) -> list[dict[str, str]]:
    """CSV 측정값을 행별 딕셔너리로 로드."""
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def summarize(readings: list[dict[str, str]]) -> dict[str, object]:
    """전체 측정 건수와 설비별 건수를 집계."""
    counts = Counter(row["machine_id"] for row in readings)
    return {"rows": len(readings), "machines": dict(sorted(counts.items()))}


def main() -> None:
    """입력 CSV의 기본 집계를 JSON으로 출력."""
    parser = argparse.ArgumentParser(description="합성 설비 로그 집계")
    parser.add_argument("--input", type=Path, required=True, help="측정 CSV 파일")
    args = parser.parse_args()
    print(json.dumps(summarize(load_readings(args.input)), ensure_ascii=False))


if __name__ == "__main__":
    main()
