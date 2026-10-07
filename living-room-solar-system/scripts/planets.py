import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import radians, tan
from pathlib import Path
from typing import Any, TypedDict
from zoneinfo import ZoneInfo

import numpy as np
from astral import LocationInfo
from astral.sun import sun
from skyfield.api import Topos, load

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = REPO_ROOT / "config.json"
EPHEMERIS_PATH = REPO_ROOT / "de421.bsp"


@dataclass(frozen=True)
class Settings:
    city_name: str
    country: str
    latitude: float
    longitude: float
    timezone_str: str
    sample_interval_minutes: int
    elevation_m: float


class VisibilitySummary(TypedDict):
    planet: str
    visible: bool
    avg_alt: float | None
    avg_az: float | None
    rise_time: datetime | None
    set_time: datetime | None


def _require_key(config: dict[str, Any], key: str) -> Any:
    value = config.get(key)
    if value is None or value == "":
        raise ValueError(f"Missing required setting: {key}")
    return value


def _as_float(config: dict[str, Any], key: str) -> float:
    value = _require_key(config, key)
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid float for {key}") from exc


def _as_int(config: dict[str, Any], key: str) -> int:
    value = _require_key(config, key)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid int for {key}") from exc


def load_settings(config_path: Path = DEFAULT_CONFIG_PATH) -> Settings:
    with open(config_path) as f:
        config: dict[str, Any] = json.load(f)

    sample_interval_minutes = _as_int(config, "sample_interval_minutes")
    if sample_interval_minutes <= 0:
        raise ValueError("sample_interval_minutes must be positive")

    return Settings(
        city_name=str(_require_key(config, "city_name")),
        country=str(_require_key(config, "country")),
        latitude=_as_float(config, "latitude"),
        longitude=_as_float(config, "longitude"),
        timezone_str=str(_require_key(config, "timezone")),
        sample_interval_minutes=sample_interval_minutes,
        elevation_m=_as_float(config, "elevation_m"),
    )


def get_wall_distance_for_azimuth(
    azimuth_deg: float, wall_distances: dict[int, float]
) -> tuple[float, int]:
    """
    Get wall distance for a given azimuth based on the closest direction.
    """

    def angular_diff(direction: int) -> float:
        diff = abs(azimuth_deg - direction)
        return 360 - diff if diff > 180 else diff

    closest_direction = min(wall_distances, key=angular_diff)
    return wall_distances[closest_direction], closest_direction


def get_cardinal_direction(azimuth: float) -> str:
    """Convert azimuth to cardinal direction description."""
    directions = [
        (0, "North"),
        (22.5, "NNE"),
        (45, "NE"),
        (67.5, "ENE"),
        (90, "East"),
        (112.5, "ESE"),
        (135, "SE"),
        (157.5, "SSE"),
        (180, "South"),
        (202.5, "SSW"),
        (225, "SW"),
        (247.5, "WSW"),
        (270, "West"),
        (292.5, "WNW"),
        (315, "NW"),
        (337.5, "NNW"),
        (360, "North"),
    ]

    for i in range(len(directions) - 1):
        if directions[i][0] <= azimuth < directions[i + 1][0]:
            return directions[i][1]
    return "North"


def group_visible_planets_by_azimuth(
    visible_planets: list[VisibilitySummary],
) -> dict[int, list[VisibilitySummary]]:
    azimuth_groups: dict[int, list[VisibilitySummary]] = {}
    for r in visible_planets:
        az = r["avg_az"]
        assert az is not None
        # Round to nearest 15 degrees for grouping
        rounded_az = round(az / 15) * 15
        if rounded_az >= 360:
            rounded_az = 0
        azimuth_groups.setdefault(rounded_az, []).append(r)
    return azimuth_groups


def summarize_visibility(
    planet_name: str,
    altitudes: list[float],
    azimuths: list[float],
    times: list[datetime],
) -> VisibilitySummary:
    visible_altitudes = [a for a in altitudes if a > 0]
    visible_azimuths = [azimuths[i] for i, a in enumerate(altitudes) if a > 0]
    visibility_times = [times[i] for i, a in enumerate(altitudes) if a > 0]

    avg_alt: float | None
    avg_az: float | None
    rise_time: datetime | None
    set_time: datetime | None

    if visible_altitudes:
        avg_alt = float(np.mean(visible_altitudes))
        avg_az = float(np.mean(visible_azimuths))
        rise_time = visibility_times[0]
        set_time = visibility_times[-1]
    else:
        avg_alt = avg_az = None
        rise_time = set_time = None

    return {
        "planet": planet_name,
        "visible": bool(visible_altitudes),
        "avg_alt": avg_alt,
        "avg_az": avg_az,
        "rise_time": rise_time,
        "set_time": set_time,
    }


def compute_wall_projection_height(altitude_deg: float, wall_distance_cm: float) -> float:
    return tan(radians(altitude_deg)) * wall_distance_cm


# Planets to track
PLANET_NAMES = [
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter barycenter",
    "Saturn barycenter",
    "Uranus barycenter",
    "Neptune barycenter",
]

# Map simplified names with unique symbols
NAME_MAP = {
    "Mercury": "Mercury",
    "Venus": "Venus",
    "Mars": "Mars",
    "Jupiter barycenter": "Jupiter",
    "Saturn barycenter": "Saturn",
    "Uranus barycenter": "Uranus",
    "Neptune barycenter": "Neptune",
}

# Unique planet symbols/logos
PLANET_SYMBOLS = {
    "Mercury": "☿️",  # Mercury symbol
    "Venus": "♀️",  # Venus symbol
    "Mars": "♂️",  # Mars symbol
    "Jupiter": "♃",  # Jupiter symbol
    "Saturn": "♄",  # Saturn symbol
    "Uranus": "♅",  # Uranus symbol
    "Neptune": "♆",  # Neptune symbol
}


def main() -> None:
    settings = load_settings()

    # Load ephemeris and timescale
    eph = load(str(EPHEMERIS_PATH))
    ts = load.timescale()

    # Define observer and location
    observer = Topos(
        latitude_degrees=settings.latitude,
        longitude_degrees=settings.longitude,
        elevation_m=settings.elevation_m,
    )
    earth = eph["earth"]
    location = earth + observer

    # Astral: get sunset today and sunrise tomorrow
    today = datetime.now(ZoneInfo(settings.timezone_str)).date()
    tomorrow = today + timedelta(days=1)
    city = LocationInfo(
        settings.city_name,
        settings.country,
        settings.timezone_str,
        settings.latitude,
        settings.longitude,
    )
    tz = ZoneInfo(settings.timezone_str)

    sun_today = sun(city.observer, date=today, tzinfo=tz)
    sun_tomorrow = sun(city.observer, date=tomorrow, tzinfo=tz)
    sunset = sun_today["sunset"]
    sunrise = sun_tomorrow["sunrise"]

    # Generate sample times (Skyfield) and corresponding native datetimes
    dt_list = []
    sample_times = []
    current_dt = sunset
    while current_dt <= sunrise:
        dt_list.append(current_dt)
        sample_times.append(ts.from_datetime(current_dt))
        current_dt += timedelta(minutes=settings.sample_interval_minutes)

    # Store results
    results = []

    # Loop through each planet
    for key in PLANET_NAMES:
        planet = eph[key]
        altitudes = []
        azimuths = []
        visibility_times = []

        for dt, t in zip(dt_list, sample_times, strict=False):
            astrometric = location.at(t).observe(planet).apparent()
            alt, az, _ = astrometric.altaz()
            alt_deg = alt.degrees
            altitudes.append(alt_deg)
            azimuths.append(az.degrees)

            if alt_deg > 0:
                visibility_times.append(dt)

        results.append(summarize_visibility(NAME_MAP[key], altitudes, azimuths, dt_list))

    # ========== OUTPUT ==========
    print("=" * 60)
    print(f"PLANET VISIBILITY REPORT FOR {settings.city_name.upper()}")
    print("=" * 60)
    print(f"Sunset:  {sunset.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Sunrise: {sunrise.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Duration: {(sunrise - sunset).total_seconds() / 3600:.1f} hours")
    print()

    visible_planets = [r for r in results if r["visible"]]
    non_visible_planets = [r for r in results if not r["visible"]]

    print("--- VISIBLE PLANETS AND THEIR DIRECTIONS ---")
    print()

    if not visible_planets:
        print("❌ No planets are visible between sunset and sunrise.")
        print()
    else:
        print("✅ The following planets will be visible:")
        print()

        for r in visible_planets:
            assert r["avg_az"] is not None
            assert r["rise_time"] is not None
            assert r["set_time"] is not None
            cardinal = get_cardinal_direction(r["avg_az"])
            symbol = PLANET_SYMBOLS[r["planet"]]
            print(
                f"{symbol} {r['planet']:>8}: {r['avg_alt']:5.1f}° altitude, {r['avg_az']:5.1f}° azimuth ({cardinal})"
            )
            print(
                f"{'':>12} Visible from {r['rise_time'].strftime('%H:%M')} to {r['set_time'].strftime('%H:%M')}"
            )
            print()

        # Show azimuth reference
        print("📍 DIRECTION REFERENCE:")
        print("   0° = North, 90° = East, 180° = South, 270° = West")
        print()

        azimuth_groups = group_visible_planets_by_azimuth(visible_planets)

        print("--- WALL DISTANCE INPUT NEEDED ---")
        print()
        print("You need to measure wall distances in these directions:")

        for grouped_az in sorted(azimuth_groups.keys()):
            planets_in_group = azimuth_groups[grouped_az]
            planet_names_with_symbols = ", ".join(
                [f"{PLANET_SYMBOLS[p['planet']]} {p['planet']}" for p in planets_in_group]
            )
            cardinal = get_cardinal_direction(grouped_az)
            print(f"📏 ~{grouped_az:3.0f}° ({cardinal:>3}) for: {planet_names_with_symbols}")

        print()
        print("Now measuring wall distances...")
        print("-" * 40)

        # Get wall distances
        wall_distances: dict[int, float] = {}

        for grouped_az in sorted(azimuth_groups.keys()):
            planets_in_group = azimuth_groups[grouped_az]
            planet_names_with_symbols = ", ".join(
                [f"{PLANET_SYMBOLS[p['planet']]} {p['planet']}" for p in planets_in_group]
            )
            cardinal = get_cardinal_direction(grouped_az)

            print(f"\n🎯 Direction: {grouped_az}° ({cardinal}) - for {planet_names_with_symbols}")
            while True:
                try:
                    distance_input = input("   Wall distance (in cm): ").strip()
                    distance = float(distance_input)
                    if distance <= 0:
                        print("   ❌ Distance must be positive. Please try again.")
                        continue
                    wall_distances[grouped_az] = distance
                    print(f"   ✅ Recorded: {distance} cm")
                    break
                except ValueError:
                    print("   ❌ Please enter a valid number.")

        # Calculate wall heights for visible planets
        print()
        print("=" * 60)
        print("PLANET WALL PROJECTION RESULTS")
        print("=" * 60)

        for r in visible_planets:
            assert r["avg_az"] is not None
            assert r["avg_alt"] is not None
            assert r["rise_time"] is not None
            assert r["set_time"] is not None
            # Find closest wall distance
            wall_distance_cm, closest_direction = get_wall_distance_for_azimuth(
                r["avg_az"], wall_distances
            )
            vertical_offset_cm = compute_wall_projection_height(r["avg_alt"], wall_distance_cm)
            cardinal = get_cardinal_direction(r["avg_az"])
            symbol = PLANET_SYMBOLS[r["planet"]]

            print(f"\n{symbol} {r['planet']:>8}:")
            print(
                f"   Position: {r['avg_alt']:5.1f}° altitude, {r['avg_az']:5.1f}° azimuth ({cardinal})"
            )
            print(f"   Using wall: {wall_distance_cm:.0f} cm at ~{closest_direction:.0f}°")
            print(f"   📐 Wall projection height: {vertical_offset_cm:.1f} cm")
            print(
                f"   ⏰ Visible: {r['rise_time'].strftime('%H:%M')} to {r['set_time'].strftime('%H:%M')}"
            )

    if non_visible_planets:
        print()
        print("--- NON-VISIBLE PLANETS ---")
        for r in non_visible_planets:
            symbol = PLANET_SYMBOLS[r["planet"]]
            print(f"⭕ {symbol} {r['planet']:>8}: Not visible between sunset and sunrise")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
