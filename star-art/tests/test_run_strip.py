import importlib.util
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
spec = importlib.util.spec_from_file_location("run_strip", SCRIPTS_DIR / "star-art-run-strip.py")
assert spec is not None and spec.loader is not None
run_strip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_strip)

GPX = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
 <trk><trkseg>
  <trkpt lat="1.3100020" lon="103.8968450"><time>2022-02-19T21:00:00Z</time></trkpt>
  <trkpt lat="1.3200000" lon="103.9000000"><time>2022-02-19T21:25:00Z</time></trkpt>
  <trkpt lat="1.3300000" lon="103.9100000"><time>2022-02-19T21:50:30Z</time></trkpt>
 </trkseg></trk>
</gpx>
"""


class TestRunStrip(unittest.TestCase):
    def test_read_run_returns_span_and_rounded_location(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".gpx") as f:
            f.write(GPX)
            f.flush()
            start, end, lat, lon = run_strip.read_run(f.name)
        self.assertEqual(start, datetime(2022, 2, 19, 21, 0, tzinfo=UTC))
        self.assertEqual(end, datetime(2022, 2, 19, 21, 50, 30, tzinfo=UTC))
        self.assertEqual((lat, lon), (1, 104))

    def test_select_band_handles_sidereal_wrap(self) -> None:
        lst = (23.5 + np.arange(61) / 60) % 24
        ra = np.array([23.6, 0.2, 0.6, 12.0, 0.2])
        dec = np.array([50.0, 52.0, 47.0, 50.0, 60.0])
        mags = np.array([1.0, 2.0, 3.0, 1.0, 1.0])
        stars = run_strip.select_band(ra, dec, mags, lst, 50)
        self.assertEqual(stars["count"], 2)
        np.testing.assert_allclose(stars["minute"], [6.0, 42.0])
        np.testing.assert_allclose(stars["offset"], [0.0, 2.0])

    def test_select_band_drops_faint_stars(self) -> None:
        lst = np.linspace(10, 11, 61)
        stars = run_strip.select_band(np.array([10.5]), np.array([50.0]), np.array([6.5]), lst, 50)
        self.assertEqual(stars["count"], 0)


if __name__ == "__main__":
    unittest.main()
