"""Route sky profile, seasonal rotation, and constellation cards."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from scripts.sky import compass_facing, observe_viewpoint
from scripts.sky_log import build_sky_log, process_gpx
from scripts.utils import Point, load_points

CONTENT_PATH = Path("data/content/constellations.yaml")


def _urban_note(lat: float, lon: float) -> str:
    # Lightweight heuristic: mid-latitudes coastal/urban-dense bands get a soft note.
    # No tile network; emphasizes naked-eye targets.
    _ = lon
    if abs(lat) < 60:
        return (
            "Assuming typical urban/suburban skies: lean on the Moon, planets, "
            "and stars of magnitude ~1.5 or brighter."
        )
    return "At higher latitudes winter nights are long — give bright circumpolar patterns extra attention."


def build_route_profile(gpx_file: str, *, with_zoom: bool = False) -> dict[str, Any]:
    log = build_sky_log(gpx_file, with_zoom=with_zoom)
    viewpoints = log["viewpoints"]
    if not viewpoints:
        return {
            "run_id": log["run_id"],
            "gpx": gpx_file,
            "summary": "No viewpoints selected.",
            "by_facing": {},
            "constellations": [],
            "light_pollution_note": "",
        }

    by_facing: dict[str, list[str]] = {}
    constellation_counts: Counter[str] = Counter()
    for vp in viewpoints:
        facing = vp["facing"]
        sky = vp["sky"]
        highlight = sky.get("highlight")
        label = highlight["name"] if highlight else "—"
        by_facing.setdefault(facing, []).append(label)
        for c in sky.get("constellations", []):
            constellation_counts[c] += 1

    facing_summary = {face: Counter(names).most_common(3) for face, names in by_facing.items()}
    lat = viewpoints[0]["lat"]
    lon = viewpoints[0]["lon"]
    time0 = viewpoints[0]["time_local"]
    dt0 = datetime.strptime(time0, "%Y-%m-%dT%H:%M:%S")
    month = dt0.strftime("%B")
    hour = dt0.strftime("%H:%M")

    top_faces = []
    for face, commons in sorted(facing_summary.items()):
        names = ", ".join(n for n, _ in commons)
        top_faces.append(f"facing {face}: {names}")

    summary = f"On this route around {hour} in {month}, " + "; ".join(top_faces) + "."

    return {
        "run_id": log["run_id"],
        "gpx": gpx_file,
        "summary": summary,
        "by_facing": {
            face: [{"name": n, "count": c} for n, c in commons]
            for face, commons in facing_summary.items()
        },
        "constellations": [{"name": n, "count": c} for n, c in constellation_counts.most_common()],
        "light_pollution_note": _urban_note(lat, lon),
        "viewpoints": viewpoints,
    }


def render_profile_markdown(profile: dict[str, Any]) -> str:
    lines = [
        f"# Route sky profile — {profile['run_id']}",
        "",
        profile["summary"],
        "",
        f"*{profile['light_pollution_note']}*",
        "",
        "## By direction",
        "",
    ]
    for face, items in sorted(profile.get("by_facing", {}).items()):
        bits = ", ".join(f"{i['name']} ({i['count']}×)" for i in items)
        lines.append(f"- **{face}:** {bits}")
    lines.extend(["", "## Constellations met", ""])
    for c in profile.get("constellations", []):
        lines.append(f"- {c['name']} ({c['count']} viewpoints)")
    lines.append("")
    return "\n".join(lines)


def seasonal_rotation(
    gpx_file: str,
    *,
    months: int = 12,
    sample_index: int = 0,
) -> dict[str, Any]:
    points = load_points(gpx_file, with_zoom=False)
    if not points:
        return {"gpx": gpx_file, "months": []}

    base = points[min(sample_index, len(points) - 1)]
    # Prefer a horizon view for seasonal comparison
    horizon = next((p for p in points if p.alt == 0.0), base)
    base_dt = datetime.strptime(horizon.time, "%Y-%m-%dT%H:%M:%S")

    months_out: list[dict[str, Any]] = []
    for month in range(1, months + 1):
        try:
            dt = base_dt.replace(month=month)
        except ValueError:
            dt = base_dt.replace(month=month, day=28)
        sample = Point(
            time=dt.strftime("%Y-%m-%dT%H:%M:%S"),
            timestamp=f"season_{month:02d}",
            lat=horizon.lat,
            lon=horizon.lon,
            az=horizon.az,
            alt=horizon.alt,
            fov=horizon.fov,
        )
        sky = observe_viewpoint(sample)
        highlight = sky.highlight
        months_out.append(
            {
                "month": month,
                "month_name": dt.strftime("%B"),
                "facing": compass_facing(sample.az),
                "highlight": highlight.name if highlight else None,
                "constellations": sky.constellations,
                "stars": [s.name for s in sky.stars[:5]],
                "planets": [p.name for p in sky.planets],
            }
        )

    return {
        "gpx": gpx_file,
        "anchor": {
            "lat": horizon.lat,
            "lon": horizon.lon,
            "az": horizon.az,
            "alt": horizon.alt,
            "time_of_day": base_dt.strftime("%H:%M"),
        },
        "months": months_out,
    }


def render_seasonal_markdown(season: dict[str, Any]) -> str:
    a = season["anchor"]
    lines = [
        "# Seasonal rotation",
        "",
        f"Same spot ({a['lat']:.4f}, {a['lon']:.4f}), facing az {a['az']:.0f}° "
        f"at {a['time_of_day']} local, month by month.",
        "",
        "| Month | Highlight | Constellations |",
        "|---|---|---|",
    ]
    for m in season["months"]:
        consts = ", ".join(m["constellations"][:4]) or "—"
        lines.append(f"| {m['month_name']} | {m['highlight'] or '—'} | {consts} |")
    lines.append("")
    return "\n".join(lines)


def load_constellation_content(path: Path = CONTENT_PATH) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        return {}
    constellations = data.get("constellations", data)
    return constellations if isinstance(constellations, dict) else {}


def write_constellation_cards(
    profile: dict[str, Any],
    out_dir: Path,
    content: dict[str, Any] | None = None,
) -> list[Path]:
    content = content if content is not None else load_constellation_content()
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for entry in profile.get("constellations", []):
        name = entry["name"]
        card = content.get(name) or content.get(name.split()[0])
        path = out_dir / f"{_slug(name)}.md"
        if card:
            myth = card.get("myth", "")
            science = card.get("science", "")
            wonder = card.get("wonder", "")
            body = (
                f"# {name}\n\n**Myth.** {myth}\n\n**Science.** {science}\n\n**Wonder.** {wonder}\n"
            )
        else:
            body = (
                f"# {name}\n\n"
                f"Met on this route ({entry['count']} viewpoints). "
                f"Add a three-line card to `data/content/constellations.yaml`.\n"
            )
        path.write_text(body)
        written.append(path)
    return written


def _slug(name: str) -> str:
    return name.lower().replace(" ", "-")


def write_profile_bundle(gpx_file: str, out_root: str = "data/sky-logs") -> Path:
    profile = build_route_profile(gpx_file)
    season = seasonal_rotation(gpx_file)
    run_id = profile["run_id"]
    out = Path(out_root) / run_id
    out.mkdir(parents=True, exist_ok=True)

    (out / "route_profile.json").write_text(json.dumps(profile, indent=2))
    (out / "route_profile.md").write_text(render_profile_markdown(profile))
    (out / "seasonal.json").write_text(json.dumps(season, indent=2))
    (out / "seasonal.md").write_text(render_seasonal_markdown(season))
    write_constellation_cards(profile, out / "cards")
    print(f"Profile + seasonal + cards → {out}")
    return Path(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Route sky profile and seasonal rotation")
    parser.add_argument("gpx", nargs="?", help="Single GPX file")
    parser.add_argument("--gpx-dir", default="data/gpx")
    parser.add_argument("--out", default="data/sky-logs")
    parser.add_argument(
        "--also-sky-log",
        action="store_true",
        help="Also write sky_log.json/md for each run",
    )
    args = parser.parse_args()

    files: list[str] = (
        [args.gpx] if args.gpx else sorted(str(p) for p in Path(args.gpx_dir).glob("*.gpx"))
    )

    if not files:
        print(f"No GPX files found (tried {args.gpx_dir})")
        return

    for gpx in files:
        if args.also_sky_log:
            process_gpx(gpx, args.out)
        write_profile_bundle(gpx, args.out)


if __name__ == "__main__":
    main()
