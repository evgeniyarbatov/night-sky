import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
)

from analemma import _build_dates, _unwrap_azimuth_compact, verify_ephemeris_file


class BuildDatesTests(unittest.TestCase):
    def test_covers_full_year_at_daily_step(self):
        dates = _build_dates(2026, 1)
        self.assertEqual(dates[0], date(2026, 1, 1))
        self.assertEqual(dates[-1], date(2026, 12, 31))
        self.assertEqual(len(dates), 365)

    def test_step_size_skips_days(self):
        dates = _build_dates(2026, 7)
        self.assertEqual(dates[1], date(2026, 1, 8))


class VerifyEphemerisFileTests(unittest.TestCase):
    def test_missing_file_is_invalid(self):
        self.assertFalse(verify_ephemeris_file("/no/such/ephemeris.bsp"))

    def test_tiny_file_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "corrupt.bsp"
            path.write_bytes(b"x" * 100)
            self.assertFalse(verify_ephemeris_file(str(path)))

    def test_large_enough_file_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "de421.bsp"
            path.write_bytes(b"x" * 2_000_000)
            self.assertTrue(verify_ephemeris_file(str(path)))


class UnwrapAzimuthCompactTests(unittest.TestCase):
    def test_no_wraparound_is_roughly_stable(self):
        az = np.array([170.0, 175.0, 180.0, 185.0, 190.0])
        result = _unwrap_azimuth_compact(az)
        self.assertEqual(len(result), len(az))
        # Monotonic input should stay monotonic after unwrapping.
        self.assertTrue(all(b >= a for a, b in zip(result, result[1:], strict=False)))

    def test_handles_wraparound_near_zero_without_a_jump(self):
        az = np.array([350.0, 355.0, 0.0, 5.0, 10.0])
        result = _unwrap_azimuth_compact(az)
        diffs = np.diff(result)
        # A naive plot of the raw degrees would show a ~350 degree jump here;
        # unwrapping should keep every step small.
        self.assertTrue(all(abs(d) < 30 for d in diffs))


if __name__ == "__main__":
    unittest.main()
