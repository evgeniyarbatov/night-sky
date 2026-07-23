"""Sky identity: bright stars, planets, moon, constellations in a viewpoint FOV."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import pytz
from skyfield.api import Star, load, wgs84
from skyfield.constellationlib import load_constellation_map, load_constellation_names
from timezonefinder import TimezoneFinder

from scripts.bright_stars import BRIGHT_STARS
from scripts.utils import Point

# Notable enough to become a highlight or drive intentional zoom.
HIGHLIGHT_MAG_LIMIT = 1.5
ZOOM_FOV = 20.0
ZOOM_CENTER_DEG = 12.0  # object must be this close to view center
STAR_MAG_LIMIT = 2.5
PLANET_NAMES = (
    "mercury",
    "venus",
    "mars",
    "jupiter barycenter",
    "saturn barycenter",
)
PLANET_LABELS = {
    "mercury": "Mercury",
    "venus": "Venus",
    "mars": "Mars",
    "jupiter barycenter": "Jupiter",
    "saturn barycenter": "Saturn",
}


@dataclass
class SkyObject:
    name: str
    kind: str  # star | planet | moon
    magnitude: float | None
    az: float
    alt: float
    constellation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "magnitude": self.magnitude,
            "az": round(self.az, 2),
            "alt": round(self.alt, 2),
            "constellation": self.constellation,
        }


@dataclass
class MoonInfo:
    az: float
    alt: float
    phase_name: str
    illumination: float
    in_fov: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "az": round(self.az, 2),
            "alt": round(self.alt, 2),
            "phase_name": self.phase_name,
            "illumination": round(self.illumination, 3),
            "in_fov": self.in_fov,
        }


@dataclass
class ViewpointSky:
    stars: list[SkyObject] = field(default_factory=list)
    planets: list[SkyObject] = field(default_factory=list)
    moon: MoonInfo | None = None
    constellations: list[str] = field(default_factory=list)
    highlight: SkyObject | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stars": [s.to_dict() for s in self.stars],
            "planets": [p.to_dict() for p in self.planets],
            "moon": self.moon.to_dict() if self.moon else None,
            "constellations": self.constellations,
            "highlight": self.highlight.to_dict() if self.highlight else None,
        }


def angular_separation_deg(az1: float, alt1: float, az2: float, alt2: float) -> float:
    """Great-circle distance between two alt/az directions, in degrees."""
    az1_r, alt1_r = math.radians(az1), math.radians(alt1)
    az2_r, alt2_r = math.radians(az2), math.radians(alt2)
    cos_d = math.sin(alt1_r) * math.sin(alt2_r) + math.cos(alt1_r) * math.cos(alt2_r) * math.cos(
        az1_r - az2_r
    )
    cos_d = max(-1.0, min(1.0, cos_d))
    return math.degrees(math.acos(cos_d))


def in_fov(
    obj_az: float,
    obj_alt: float,
    view_az: float,
    view_alt: float,
    fov: float,
) -> bool:
    if obj_alt < -0.5:
        return False
    return angular_separation_deg(obj_az, obj_alt, view_az, view_alt) <= fov / 2.0


def compass_facing(az: float) -> str:
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[int((az + 22.5) % 360 // 45)]


def parse_local_time(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")


@lru_cache(maxsize=1)
def _timescale() -> Any:
    return load.timescale()


@lru_cache(maxsize=1)
def _ephemeris() -> Any:
    cache = Path("data") / ".skyfield"
    cache.mkdir(parents=True, exist_ok=True)
    loader = load
    loader.directory = str(cache)
    return loader("de421.bsp")


@lru_cache(maxsize=1)
def _constellation_at() -> Any:
    return load_constellation_map()


@lru_cache(maxsize=1)
def _constellation_names() -> dict[str, str]:
    raw = load_constellation_names()
    if isinstance(raw, dict):
        return raw
    return {pair[0]: pair[1] for pair in raw}


@lru_cache(maxsize=1)
def _timezone_finder() -> TimezoneFinder:
    return TimezoneFinder()


def constellation_full_name(abbr: str) -> str:
    names = _constellation_names()
    return names.get(abbr, abbr)


def local_to_skyfield_time(time_str: str, lat: float, lon: float) -> Any:
    """Interpret Point.time as civil local time at lat/lon → Skyfield UTC time."""
    naive = parse_local_time(time_str)
    tz_name = _timezone_finder().timezone_at(lat=lat, lng=lon) or "UTC"
    local = pytz.timezone(tz_name).localize(naive)
    utc = local.astimezone(pytz.UTC)
    ts = _timescale()
    return ts.utc(utc.year, utc.month, utc.day, utc.hour, utc.minute, utc.second)


def _topocentric(lat: float, lon: float) -> Any:
    """Earth + geographic position; call .at(t).observe(...)."""
    eph = _ephemeris()
    return eph["earth"] + wgs84.latlon(lat, lon)


def _altaz(observer_at_t: Any, target: Any) -> tuple[float, float]:
    alt, az, _ = observer_at_t.observe(target).apparent().altaz()
    return float(alt.degrees), float(az.degrees)


def _moon_phase(eph: Any, t: Any) -> tuple[str, float]:
    earth = eph["earth"]
    sun = eph["sun"]
    moon = eph["moon"]
    e = earth.at(t)
    _, sun_lon, _ = e.observe(sun).apparent().ecliptic_latlon()
    _, moon_lon, _ = e.observe(moon).apparent().ecliptic_latlon()
    phase_angle = (moon_lon.degrees - sun_lon.degrees) % 360.0
    illumination = 0.5 * (1.0 - math.cos(math.radians(phase_angle)))
    if phase_angle < 22.5 or phase_angle >= 337.5:
        name = "new"
    elif phase_angle < 67.5:
        name = "waxing crescent"
    elif phase_angle < 112.5:
        name = "first quarter"
    elif phase_angle < 157.5:
        name = "waxing gibbous"
    elif phase_angle < 202.5:
        name = "full"
    elif phase_angle < 247.5:
        name = "waning gibbous"
    elif phase_angle < 292.5:
        name = "last quarter"
    else:
        name = "waning crescent"
    return name, illumination


def observe_viewpoint(point: Point) -> ViewpointSky:
    t = local_to_skyfield_time(point.time, point.lat, point.lon)
    constellation_at = _constellation_at()
    eph = _ephemeris()
    observer_at_t = _topocentric(point.lat, point.lon).at(t)

    stars: list[SkyObject] = []
    constellations: set[str] = set()

    for catalog_star in BRIGHT_STARS:
        if catalog_star.magnitude > STAR_MAG_LIMIT:
            continue
        star = Star(ra_hours=catalog_star.ra_hours, dec_degrees=catalog_star.dec_degrees)
        alt, az = _altaz(observer_at_t, star)
        if not in_fov(az, alt, point.az, point.alt, point.fov):
            continue
        stars.append(
            SkyObject(
                name=catalog_star.name,
                kind="star",
                magnitude=catalog_star.magnitude,
                az=az,
                alt=alt,
                constellation=catalog_star.constellation,
            )
        )
        constellations.add(catalog_star.constellation)

    planets: list[SkyObject] = []
    for key in PLANET_NAMES:
        body = eph[key]
        alt_d, az_d = _altaz(observer_at_t, body)
        if not in_fov(az_d, alt_d, point.az, point.alt, point.fov):
            continue
        planets.append(
            SkyObject(
                name=PLANET_LABELS[key],
                kind="planet",
                magnitude=None,
                az=az_d,
                alt=alt_d,
            )
        )

    moon = eph["moon"]
    m_alt_d, m_az_d = _altaz(observer_at_t, moon)
    phase_name, illumination = _moon_phase(eph, t)
    moon_apparent = observer_at_t.observe(moon).apparent()
    abbr = constellation_at(moon_apparent)
    if abbr:
        constellations.add(abbr)
    moon_info = MoonInfo(
        az=m_az_d,
        alt=m_alt_d,
        phase_name=phase_name,
        illumination=illumination,
        in_fov=in_fov(m_az_d, m_alt_d, point.az, point.alt, point.fov),
    )

    for catalog_star in BRIGHT_STARS:
        if catalog_star.name not in {s.name for s in stars}:
            continue
        star_obj = Star(ra_hours=catalog_star.ra_hours, dec_degrees=catalog_star.dec_degrees)
        abbr = constellation_at(observer_at_t.observe(star_obj).apparent())
        if abbr:
            constellations.add(abbr)

    highlight = _pick_highlight(stars, planets, moon_info, point)
    full_names = sorted({constellation_full_name(a) for a in constellations})

    return ViewpointSky(
        stars=sorted(stars, key=lambda s: s.magnitude if s.magnitude is not None else 99),
        planets=planets,
        moon=moon_info,
        constellations=full_names,
        highlight=highlight,
    )


def _pick_highlight(
    stars: list[SkyObject],
    planets: list[SkyObject],
    moon: MoonInfo | None,
    point: Point,
) -> SkyObject | None:
    candidates: list[SkyObject] = []

    if moon and moon.in_fov and moon.alt > 0:
        candidates.append(
            SkyObject(
                name=f"Moon ({moon.phase_name})",
                kind="moon",
                magnitude=-10.0 + (1.0 - moon.illumination) * 5.0,
                az=moon.az,
                alt=moon.alt,
            )
        )

    for p in planets:
        if p.alt > 0:
            # Prefer bright naked-eye planets; Venus/Jupiter often dominate
            mag = {"Venus": -4.0, "Jupiter": -2.2, "Mars": 0.5, "Saturn": 0.8, "Mercury": 0.0}.get(
                p.name, 1.0
            )
            candidates.append(
                SkyObject(name=p.name, kind="planet", magnitude=mag, az=p.az, alt=p.alt)
            )

    for s in stars:
        if s.magnitude is not None and s.magnitude <= HIGHLIGHT_MAG_LIMIT:
            candidates.append(s)

    if not candidates:
        return stars[0] if stars else (planets[0] if planets else None)

    def score(obj: SkyObject) -> tuple[float, float]:
        sep = angular_separation_deg(obj.az, obj.alt, point.az, point.alt)
        mag = obj.magnitude if obj.magnitude is not None else 5.0
        return (mag, sep)

    return min(candidates, key=score)


def should_add_zoom(view: ViewpointSky, point: Point) -> bool:
    if point.fov <= ZOOM_FOV + 1:
        return False
    if view.highlight is None:
        return False
    h = view.highlight
    if h.alt < 0:
        return False
    sep = angular_separation_deg(h.az, h.alt, point.az, point.alt)
    return sep <= ZOOM_CENTER_DEG


def make_zoom_point(point: Point) -> Point:
    return Point(
        time=point.time,
        timestamp=f"{point.timestamp}_zoom",
        lat=point.lat,
        lon=point.lon,
        az=point.az,
        alt=point.alt,
        fov=ZOOM_FOV,
    )


def enrich_with_zoom(points: list[Point]) -> list[Point]:
    """Add intentional tighter-FOV points when a highlight sits near view center."""
    enriched: list[Point] = []
    for point in points:
        enriched.append(point)
        if point.fov > ZOOM_FOV + 1:
            view = observe_viewpoint(point)
            if should_add_zoom(view, point):
                enriched.append(make_zoom_point(point))
    return enriched


def wonder_line(highlight: SkyObject | None) -> str | None:
    if highlight is None:
        return None
    if highlight.kind == "moon":
        return "The same Moon that lit prehistoric night runs is over your route tonight."
    if highlight.kind == "planet":
        return f"{highlight.name} is a world, not a star — sunlight on a neighbor in our solar system."
    if highlight.name == "Sirius":
        return "Sirius is the brightest star in Earth's night sky — its light left only ~8.6 years ago."
    if highlight.name == "Polaris":
        return "Polaris holds nearly still while the rest of the northern sky wheels around it."
    if highlight.name == "Betelgeuse":
        return (
            "Betelgeuse is a red supergiant; if it sat where the Sun does, it would swallow Earth."
        )
    return f"{highlight.name}: a fixed light that outlasts any single run."
