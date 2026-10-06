from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from location import format_lat_lon, format_site, load_location


def write_config(cfg: dict[str, object]) -> Path:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(cfg, f)
    return Path(f.name)


VALID = {"name": "Saigon", "latitude": 10.8, "longitude": 106.7, "timezone": "Asia/Ho_Chi_Minh"}


class LoadLocationTest(unittest.TestCase):
    def test_repo_config_loads(self) -> None:
        loc = load_location()
        self.assertTrue(loc["name"])
        self.assertTrue(-90 <= loc["latitude"] <= 90)

    def test_valid_config(self) -> None:
        self.assertEqual(load_location(write_config(VALID)), VALID)

    def test_missing_keys(self) -> None:
        with self.assertRaises(KeyError):
            load_location(write_config({"name": "x"}))

    def test_latitude_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            load_location(write_config({**VALID, "latitude": 91}))

    def test_longitude_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            load_location(write_config({**VALID, "longitude": -181}))

    def test_bad_timezone(self) -> None:
        with self.assertRaises(Exception):  # noqa: B017 - ZoneInfoNotFoundError subclasses KeyError
            load_location(write_config({**VALID, "timezone": "Not/AZone"}))


class FormatTest(unittest.TestCase):
    def test_hemispheres(self) -> None:
        self.assertEqual(format_lat_lon(10.81133, 106.67427), "10.8113°N, 106.6743°E")
        self.assertEqual(format_lat_lon(-33.8688, -70.6693, precision=1), "33.9°S, 70.7°W")

    def test_site_label(self) -> None:
        self.assertEqual(format_site(VALID, precision=1), "Saigon · 10.8°N, 106.7°E")


if __name__ == "__main__":
    unittest.main()
