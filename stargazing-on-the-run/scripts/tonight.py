"""Pre-run briefing: tonight preview, glance card, audio script, optional weather."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pyproj

from scripts.sky import compass_facing, observe_viewpoint, wonder_line
from scripts.utils import FOV_MAX, Point, load_points, load_raw_track

WeatherFetcher = Callable[[float, float, datetime, datetime], dict[str, Any] | None]


def shift_points_to_start(points: list[Point], start: datetime) -> list[Point]:
    if not points:
        return []
    times = [datetime.strptime(p.time, "%Y-%m-%dT%H:%M:%S") for p in points]
    t0 = min(times)
    shifted: list[Point] = []
    for p, t in zip(points, times, strict=True):
        new_t = start + (t - t0)
        shifted.append(
            Point(
                time=new_t.strftime("%Y-%m-%dT%H:%M:%S"),
                timestamp=new_t.strftime("%s"),
                lat=p.lat,
                lon=p.lon,
                az=p.az,
                alt=p.alt,
                fov=p.fov,
            )
        )
    return shifted


def _km_along_track(track: list[Point], target: Point) -> float:
    if not track:
        return 0.0
    geod = pyproj.Geod(ellps="WGS84")
    # Find nearest track point by lat/lon
    best_i = 0
    best_d = float("inf")
    for i, p in enumerate(track):
        _, _, dist = geod.inv(p.lon, p.lat, target.lon, target.lat)
        if dist < best_d:
            best_d = dist
            best_i = i
    km = 0.0
    for a, b in zip(track[: best_i + 1], track[1 : best_i + 1], strict=False):
        _, _, dist = geod.inv(a.lon, a.lat, b.lon, b.lat)
        km += dist / 1000.0
    return km


def _moon_rise_set_approx(lat: float, lon: float, day: datetime) -> dict[str, str | None]:
    """Sample hourly altitudes; coarse rise/set for the briefing card."""
    samples: list[tuple[datetime, float]] = []
    for hour in range(24):
        for minute in (0, 30):
            t = day.replace(hour=hour, minute=minute, second=0)
            p = Point(
                time=t.strftime("%Y-%m-%dT%H:%M:%S"),
                timestamp=t.strftime("%s"),
                lat=lat,
                lon=lon,
                az=180.0,
                alt=0.0,
                fov=FOV_MAX,
            )
            sky = observe_viewpoint(p)
            alt = sky.moon.alt if sky.moon else -90.0
            samples.append((t, alt))

    rise: str | None = None
    set_: str | None = None
    for (_t0, a0), (t1, a1) in zip(samples, samples[1:], strict=False):
        if a0 < 0 <= a1 and rise is None:
            rise = t1.strftime("%H:%M")
        if a0 >= 0 > a1 and set_ is None:
            set_ = t1.strftime("%H:%M")
    return {"rise": rise, "set": set_}


def select_highlights(viewpoints: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    """Pick up to `limit` distinct segment highlights (prefer bright / high)."""
    scored: list[tuple[float, dict[str, Any]]] = []
    for vp in viewpoints:
        h = vp["sky"].get("highlight")
        if not h:
            continue
        mag = h.get("magnitude")
        mag_s = float(mag) if mag is not None else 3.0
        score = -mag_s + 0.02 * float(h.get("alt") or 0)
        scored.append((score, vp))

    scored.sort(key=lambda x: x[0], reverse=True)
    chosen: list[dict[str, Any]] = []
    seen: set[str] = set()
    for _, vp in scored:
        name = vp["sky"]["highlight"]["name"]
        if name in seen:
            continue
        seen.add(name)
        chosen.append(vp)
        if len(chosen) >= limit:
            break
    # Keep run order for the card
    chosen.sort(key=lambda v: v["minute_into_run"])
    return chosen


def build_tonight(
    gpx_file: str,
    start: datetime,
    *,
    weather: bool = False,
    weather_fetcher: WeatherFetcher | None = None,
) -> dict[str, Any]:
    points = load_points(gpx_file, with_zoom=False)
    track = load_raw_track(gpx_file)
    shifted = shift_points_to_start(points, start)
    if not shifted:
        return {"gpx": gpx_file, "start": start.isoformat(timespec="seconds"), "highlights": []}

    viewpoints: list[dict[str, Any]] = []
    for p in shifted:
        sky = observe_viewpoint(p)
        t0 = datetime.strptime(shifted[0].time, "%Y-%m-%dT%H:%M:%S")
        t = datetime.strptime(p.time, "%Y-%m-%dT%H:%M:%S")
        minute = max(0, int((t - t0).total_seconds() // 60))
        km = _km_along_track(track, p) if track else 0.0
        viewpoints.append(
            {
                "time_local": p.time,
                "minute_into_run": minute,
                "km": round(km, 2),
                "lat": p.lat,
                "lon": p.lon,
                "az": round(p.az, 1),
                "alt": p.alt,
                "facing": compass_facing(p.az),
                "sky": sky.to_dict(),
                "wonder": wonder_line(sky.highlight),
            }
        )

    highlights = select_highlights(viewpoints)
    lat0, lon0 = shifted[0].lat, shifted[0].lon
    moon_rs = _moon_rise_set_approx(lat0, lon0, start)

    planets: list[str] = []
    seen_p: set[str] = set()
    for vp in viewpoints:
        for pl in vp["sky"].get("planets", []):
            if pl["name"] not in seen_p:
                seen_p.add(pl["name"])
                planets.append(pl["name"])

    end = datetime.strptime(shifted[-1].time, "%Y-%m-%dT%H:%M:%S")
    weather_data = None
    if weather:
        fetcher = weather_fetcher or fetch_open_meteo_clouds
        weather_data = fetcher(lat0, lon0, start, end)

    return {
        "gpx": gpx_file,
        "start": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%S"),
        "moon": moon_rs,
        "planets": planets,
        "highlights": [
            {
                "minute": h["minute_into_run"],
                "km": h["km"],
                "facing": h["facing"],
                "name": h["sky"]["highlight"]["name"],
                "wonder": h.get("wonder"),
            }
            for h in highlights
        ],
        "viewpoints": viewpoints,
        "weather": weather_data,
    }


def fetch_open_meteo_clouds(
    lat: float,
    lon: float,
    start: datetime,
    end: datetime,
) -> dict[str, Any] | None:
    params = urllib.parse.urlencode(
        {
            "latitude": f"{lat:.4f}",
            "longitude": f"{lon:.4f}",
            "hourly": "cloud_cover",
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "timezone": "auto",
        }
    )
    url = f"https://api.open-meteo.com/v1/forecast?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:  # noqa: S310
            payload = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"error": str(exc)}

    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    clouds = hourly.get("cloud_cover", [])
    window: list[dict[str, Any]] = []
    for t_str, cover in zip(times, clouds, strict=False):
        try:
            t = datetime.fromisoformat(t_str)
        except ValueError:
            continue
        if start - timedelta(hours=1) <= t <= end + timedelta(hours=1):
            window.append({"time": t_str, "cloud_cover": cover})

    if not window:
        return {"hourly": [], "summary": "No cloud data for run window."}

    avg = sum(w["cloud_cover"] for w in window if w["cloud_cover"] is not None) / max(
        1, len([w for w in window if w["cloud_cover"] is not None])
    )
    if avg < 30:
        summary = f"Mostly clear (avg cloud cover ~{avg:.0f}%). Good night for stars."
    elif avg < 70:
        summary = f"Partly cloudy (avg ~{avg:.0f}%). Planets and bright stars still worth a look."
    else:
        summary = f"Cloudy (avg ~{avg:.0f}%). Consider another night or enjoy the Moon if visible."

    return {"hourly": window, "summary": summary, "avg_cloud_cover": round(avg, 1)}


def render_glance_card(preview: dict[str, Any]) -> str:
    lines = [
        "# Tonight's run — glance card",
        "",
        f"**Start:** {preview['start']}  ",
        f"**Route:** `{preview['gpx']}`",
        "",
        "## Moon",
        "",
        f"- Rise: {preview['moon'].get('rise') or '—'}  ",
        f"- Set: {preview['moon'].get('set') or '—'}",
        "",
        "## Planets in view along the route",
        "",
    ]
    if preview.get("planets"):
        lines.append(", ".join(preview["planets"]))
    else:
        lines.append("None of the bright planets land in selected viewpoints.")
    lines.extend(["", "## Look for this", ""])
    if not preview.get("highlights"):
        lines.append("_No strong highlights — still a good night to learn the bright stars._")
    for h in preview.get("highlights", []):
        lines.append(
            f"- **km {h['km']:.1f}** (minute {h['minute']}): look **{h['facing']}** for **{h['name']}**"
        )
        if h.get("wonder"):
            lines.append(f"  - _{h['wonder']}_")
    if preview.get("weather") and preview["weather"].get("summary"):
        lines.extend(["", "## Skies", "", preview["weather"]["summary"]])
    lines.append("")
    return "\n".join(lines)


def render_audio_script(preview: dict[str, Any]) -> str:
    lines = [
        "Sky for tonight's run.",
        "",
        f"You start at {preview['start']}.",
    ]
    moon = preview.get("moon", {})
    if moon.get("rise") or moon.get("set"):
        lines.append(
            f"The Moon rises around {moon.get('rise') or 'unknown'} "
            f"and sets around {moon.get('set') or 'unknown'}."
        )
    if preview.get("planets"):
        lines.append(
            "Planets that may appear along your route: " + ", ".join(preview["planets"]) + "."
        )
    lines.append("")
    lines.append("Here is what to look for, one thing at a time.")
    lines.append("")
    if not preview.get("highlights"):
        lines.append(
            "No single object dominates. Notice the brightest light in each direction as you turn."
        )
    for i, h in enumerate(preview.get("highlights", []), start=1):
        lines.append(
            f"Highlight {i}. Near kilometer {h['km']:.1f}, about minute {h['minute']}, "
            f"look {h['facing']} for {h['name']}."
        )
        if h.get("wonder"):
            lines.append(h["wonder"])
        lines.append("")
    if preview.get("weather") and preview["weather"].get("summary"):
        lines.append(preview["weather"]["summary"])
    lines.append("")
    lines.append("Run easy. Look up when it is safe. One light is enough.")
    lines.append("")
    return "\n".join(lines)


def write_tonight(preview: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "tonight.json").write_text(json.dumps(preview, indent=2))
    (out_dir / "glance_card.md").write_text(render_glance_card(preview))
    (out_dir / "tonight_script.md").write_text(render_audio_script(preview))
    print(f"Tonight briefing → {out_dir}")


def _parse_start(value: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise SystemExit(f"Could not parse START time: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a pre-run sky briefing")
    parser.add_argument("--gpx", required=True, help="Route GPX")
    parser.add_argument("--start", required=True, help="Planned start (local) YYYY-MM-DDTHH:MM")
    parser.add_argument("--out", default=None, help="Output directory")
    parser.add_argument("--weather", action="store_true", help="Fetch Open-Meteo cloud cover")
    args = parser.parse_args()

    start = _parse_start(args.start)
    preview = build_tonight(args.gpx, start, weather=args.weather)
    run_id = Path(args.gpx).stem
    out = Path(args.out) if args.out else Path("data/sky-logs") / run_id / "tonight"
    write_tonight(preview, out)


if __name__ == "__main__":
    main()
