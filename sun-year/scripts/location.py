"""Load site location from repo-root config.json — the only place site is defined."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import TypedDict
from zoneinfo import ZoneInfo


class Location(TypedDict):
    name: str
    latitude: float
    longitude: float
    timezone: str


REQUIRED_KEYS = ("name", "latitude", "longitude", "timezone")

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config.json"


def load_location(path: Path | None = None) -> Location:
    """Read name / lat / lon / timezone from config.json."""
    config_path = path or CONFIG_PATH
    with open(config_path) as f:
        cfg = json.load(f)

    missing = [k for k in REQUIRED_KEYS if k not in cfg]
    if missing:
        raise KeyError(f"{config_path} missing keys: {', '.join(missing)}")

    lat = float(cfg["latitude"])
    lon = float(cfg["longitude"])
    if not -90.0 <= lat <= 90.0:
        raise ValueError(f"latitude out of range: {lat}")
    if not -180.0 <= lon <= 180.0:
        raise ValueError(f"longitude out of range: {lon}")

    tz_name = str(cfg["timezone"])
    ZoneInfo(tz_name)  # fail fast on bad IANA names

    return {
        "name": str(cfg["name"]),
        "latitude": lat,
        "longitude": lon,
        "timezone": tz_name,
    }


def format_lat_lon(latitude: float, longitude: float, *, precision: int = 4) -> str:
    """Hemisphere-aware coordinates, e.g. 10.8113°N, 106.6743°E."""
    ns = "N" if latitude >= 0 else "S"
    ew = "E" if longitude >= 0 else "W"
    return (
        f"{abs(latitude):.{precision}f}°{ns}, "
        f"{abs(longitude):.{precision}f}°{ew}"
    )


def format_site(loc: Location, *, precision: int = 4) -> str:
    """Label for plot titles: Name · lat, lon."""
    return f"{loc['name']} · {format_lat_lon(loc['latitude'], loc['longitude'], precision=precision)}"


def zone(loc: Location) -> ZoneInfo:
    return ZoneInfo(loc["timezone"])


def today_local(loc: Location) -> datetime:
    """Midnight today in the site timezone (naive local wall time for ephem)."""
    now = datetime.now(zone(loc))
    return now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)


def today_date_local(loc: Location) -> date:
    return datetime.now(zone(loc)).date()
