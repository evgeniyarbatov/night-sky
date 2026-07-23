import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from ra_utils import ra_hms_to_deg  # noqa: E402


class RaHmsToDegTests(unittest.TestCase):
    def test_converts_hours_minutes_seconds_to_degrees(self) -> None:
        self.assertAlmostEqual(ra_hms_to_deg("6 0 0"), 90.0)

    def test_zero_is_zero_degrees(self) -> None:
        self.assertEqual(ra_hms_to_deg("0 0 0"), 0.0)

    def test_handles_fractional_minutes_and_seconds(self) -> None:
        self.assertAlmostEqual(ra_hms_to_deg("1 30 0"), 22.5)

    def test_strips_surrounding_whitespace(self) -> None:
        self.assertAlmostEqual(ra_hms_to_deg("  6 0 0  "), 90.0)


if __name__ == "__main__":
    unittest.main()
