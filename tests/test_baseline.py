"""현재 제공되는 CSV 집계 동작 검증."""

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BaselineCliTest(unittest.TestCase):
    """기본 CLI의 사용자 관찰 결과 검증."""

    def test_sample_summary(self) -> None:
        """샘플 CSV의 전체·설비별 건수 출력 검증."""
        result = subprocess.run(
            [sys.executable, str(ROOT / "app.py"), "--input", str(ROOT / "data/equipment_readings.csv")],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            json.loads(result.stdout),
            {"rows": 6, "machines": {"EQ-01": 4, "EQ-02": 2}},
        )


if __name__ == "__main__":
    unittest.main()
