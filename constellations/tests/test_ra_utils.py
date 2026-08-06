import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from ra_utils import circular_mean_deg, ra_hms_to_deg, unwrap_degrees  # noqa: E402


class RaHmsToDegTests(unittest.TestCase):
    def test_converts_hours_minutes_seconds_to_degrees(self) -> None:
        self.assertAlmostEqual(ra_hms_to_deg("6 0 0"), 90.0)

    def test_zero_is_zero_degrees(self) -> None:
        self.assertEqual(ra_hms_to_deg("0 0 0"), 0.0)

    def test_handles_fractional_minutes_and_seconds(self) -> None:
        self.assertAlmostEqual(ra_hms_to_deg("1 30 0"), 22.5)

    def test_strips_surrounding_whitespace(self) -> None:
        self.assertAlmostEqual(ra_hms_to_deg("  6 0 0  "), 90.0)


class CircularMeanDegTests(unittest.TestCase):
    def test_ordinary_cluster(self) -> None:
        self.assertAlmostEqual(circular_mean_deg([40.0, 50.0, 45.0]), 45.0)

    def test_straddles_north(self) -> None:
        # Arithmetic mean would wrongly yield ~180° (south)
        mean = circular_mean_deg([10.0, 350.0])
        self.assertTrue(mean < 10.0 or mean > 350.0)
        self.assertAlmostEqual(mean if mean <= 180 else mean - 360, 0.0, places=5)

    def test_single_angle(self) -> None:
        self.assertAlmostEqual(circular_mean_deg([47.0]), 47.0)


class UnwrapDegreesTests(unittest.TestCase):
    def test_crosses_north_toward_northwest(self) -> None:
        series = [14.0, 5.0, 0.5, 358.0, 353.0]
        unwrapped = unwrap_degrees(series)
        self.assertEqual(len(unwrapped), len(series))
        for a, b in zip(unwrapped, unwrapped[1:], strict=False):
            self.assertLess(abs(b - a), 180.0)
        self.assertLess(unwrapped[-1], unwrapped[0])
        self.assertAlmostEqual(unwrapped[-1] % 360.0, 353.0, places=5)


if __name__ == "__main__":
    unittest.main()
