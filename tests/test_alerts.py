"""연속 고온 경보 탐지 규칙 검증."""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402


def make_rows(machine_id: str, temperatures: list[str], start_minute: int = 0) -> list[dict[str, str]]:
    """5분 간격 timestamp를 붙인 측정 행 목록 생성."""
    return [
        {
            "machine_id": machine_id,
            "timestamp": f"2026-09-26T09:{start_minute + index * 5:02d}:00",
            "temperature_c": temperature,
        }
        for index, temperature in enumerate(temperatures)
    ]


class DetectAlertsTest(unittest.TestCase):
    """`detect_alerts`의 구간 판정·필드·정렬 검증."""

    def test_exact_threshold_counts_as_high(self) -> None:
        """정확히 85인 값의 고온 포함 검증."""
        alerts = app.detect_alerts(make_rows("EQ-01", ["85", "85", "85"]))
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["consecutive_count"], 3)
        self.assertEqual(alerts[0]["peak_temperature_c"], 85.0)

    def test_below_threshold_ends_streak(self) -> None:
        """84.9 측정에서 구간 종료 검증."""
        rows = make_rows("EQ-01", ["90", "90", "84.9", "90"])
        self.assertEqual(app.detect_alerts(rows), [])

    def test_long_streak_yields_single_alert(self) -> None:
        """4건 이상 연속 시 경보 1건과 정확한 건수·필드 검증."""
        rows = make_rows("EQ-01", ["80", "86", "92", "88", "87", "70"])
        self.assertEqual(
            app.detect_alerts(rows),
            [{
                "machine_id": "EQ-01",
                "start_at": "2026-09-26T09:05:00",
                "end_at": "2026-09-26T09:20:00",
                "consecutive_count": 4,
                "peak_temperature_c": 92.0,
            }],
        )

    def test_two_streaks_on_same_machine(self) -> None:
        """85 미만으로 분리된 두 구간의 경보 2건 생성 검증."""
        rows = make_rows("EQ-01", ["86", "87", "88", "80", "89", "90", "91"])
        alerts = app.detect_alerts(rows)
        self.assertEqual(
            [(alert["start_at"], alert["end_at"]) for alert in alerts],
            [
                ("2026-09-26T09:00:00", "2026-09-26T09:10:00"),
                ("2026-09-26T09:20:00", "2026-09-26T09:30:00"),
            ],
        )

    def test_results_sorted_by_machine_then_start(self) -> None:
        """여러 설비 결과의 `machine_id`→`start_at` 정렬 검증."""
        rows = (
            make_rows("EQ-02", ["90", "90", "90"])
            + make_rows("EQ-01", ["90", "90", "90"], start_minute=30)
            + make_rows("EQ-01", ["90", "90", "90"])
        )
        # EQ-01의 두 구간 사이를 85 미만 측정으로 분리
        rows.append({"machine_id": "EQ-01", "timestamp": "2026-09-26T09:15:00", "temperature_c": "70"})
        alerts = app.detect_alerts(list(reversed(rows)))
        self.assertEqual(
            [(alert["machine_id"], alert["start_at"]) for alert in alerts],
            [
                ("EQ-01", "2026-09-26T09:00:00"),
                ("EQ-01", "2026-09-26T09:30:00"),
                ("EQ-02", "2026-09-26T09:00:00"),
            ],
        )

    def test_whitespace_only_value_treated_as_missing(self) -> None:
        """공백만 있는 온도값의 빈 값 처리 검증."""
        rows = make_rows("EQ-01", ["90", "90", "   ", "90"])
        self.assertEqual(app.detect_alerts(rows), [])

    def test_empty_input(self) -> None:
        """빈 입력의 빈 경보 목록 반환 검증."""
        self.assertEqual(app.detect_alerts([]), [])

    def test_streak_ending_at_data_end(self) -> None:
        """데이터 끝에서 끝나는 구간의 경보 생성 검증."""
        rows = make_rows("EQ-01", ["70", "86", "87", "88"])
        alerts = app.detect_alerts(rows)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["start_at"], "2026-09-26T09:05:00")
        self.assertEqual(alerts[0]["end_at"], "2026-09-26T09:15:00")


if __name__ == "__main__":
    unittest.main()
