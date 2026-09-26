"""이슈 구현 전 실패해야 하는 독립 수락 테스트."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

import app


ROOT = Path(__file__).resolve().parents[1]


class AlertAcceptanceTest(unittest.TestCase):
    """고온 경보의 외부 관찰 동작 검증."""

    def test_interleaved_out_of_order_readings(self) -> None:
        """설비별 시간순 정렬 후 연속 고온 탐지 검증."""
        rows = [
            {"machine_id": "EQ-01", "timestamp": "2026-09-26T09:10:00", "temperature_c": "90"},
            {"machine_id": "EQ-02", "timestamp": "2026-09-26T09:05:00", "temperature_c": "88"},
            {"machine_id": "EQ-01", "timestamp": "2026-09-26T09:00:00", "temperature_c": "85"},
            {"machine_id": "EQ-02", "timestamp": "2026-09-26T09:00:00", "temperature_c": "87"},
            {"machine_id": "EQ-01", "timestamp": "2026-09-26T09:05:00", "temperature_c": "86"},
        ]
        self.assertEqual(
            app.detect_alerts(rows),
            [{
                "machine_id": "EQ-01",
                "start_at": "2026-09-26T09:00:00",
                "end_at": "2026-09-26T09:10:00",
                "consecutive_count": 3,
                "peak_temperature_c": 90.0,
            }],
        )

    def test_short_spike_and_missing_value(self) -> None:
        """두 건 이하 고온과 결측값의 경보 제외 검증."""
        rows = [
            {"machine_id": "EQ-01", "timestamp": "2026-09-26T09:00:00", "temperature_c": "85"},
            {"machine_id": "EQ-01", "timestamp": "2026-09-26T09:05:00", "temperature_c": "86"},
            {"machine_id": "EQ-01", "timestamp": "2026-09-26T09:10:00", "temperature_c": ""},
            {"machine_id": "EQ-01", "timestamp": "2026-09-26T09:15:00", "temperature_c": "87"},
        ]
        self.assertEqual(app.detect_alerts(rows), [])

    def test_cli_alert_output(self) -> None:
        """샘플 CSV의 경보 JSON 출력 검증."""
        result = subprocess.run(
            [sys.executable, str(ROOT / "app.py"), "--input", str(ROOT / "data/equipment_readings.csv"), "--alerts"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            json.loads(result.stdout),
            [{
                "machine_id": "EQ-01",
                "start_at": "2026-09-26T09:05:00",
                "end_at": "2026-09-26T09:15:00",
                "consecutive_count": 3,
                "peak_temperature_c": 91.0,
            }],
        )


if __name__ == "__main__":
    unittest.main()
