from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location("plot_sun", SCRIPTS / "plot-sun.py")
assert spec and spec.loader
plot_sun = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plot_sun)

DAY0 = datetime(2026, 1, 1)
DATES = [DAY0 + timedelta(days=i) for i in range(4)]


class CrossingsTest(unittest.TestCase):
    def test_interpolates_rising_crossing(self) -> None:
        self.assertEqual(plot_sun._crossings([0, 10, 20, 30], DATES, 15), [DAY0 + timedelta(days=1.5)])

    def test_finds_rising_and_falling(self) -> None:
        out = plot_sun._crossings([0, 10, 0, 10], DATES, 5)
        self.assertEqual(len(out), 3)

    def test_flat_series_has_no_crossing(self) -> None:
        self.assertEqual(plot_sun._crossings([5, 5, 5, 5], DATES, 5), [])

    def test_out_of_range_target(self) -> None:
        self.assertEqual(plot_sun._crossings([0, 1, 2, 3], DATES, 99), [])


class SunAzimuthTest(unittest.TestCase):
    def test_equator_rise_set_are_roughly_east_west(self) -> None:
        import ephem

        obs = ephem.Observer()
        obs.lat, obs.lon = "0", "0"
        rise, sett = plot_sun.get_sun_azimuth_at_rise_set(obs, datetime(2026, 3, 20))
        self.assertAlmostEqual(rise, 90, delta=2)
        self.assertAlmostEqual(sett, 270, delta=2)

    def test_polar_night_returns_none(self) -> None:
        import ephem

        obs = ephem.Observer()
        obs.lat, obs.lon = "89", "0"
        self.assertEqual(plot_sun.get_sun_azimuth_at_rise_set(obs, datetime(2026, 12, 21)), (None, None))


if __name__ == "__main__":
    unittest.main()
