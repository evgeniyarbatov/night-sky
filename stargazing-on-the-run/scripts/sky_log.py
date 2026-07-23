"""Build per-run sky logs (JSON + Markdown) from GPX viewpoints."""

from __future__ import annotations

import argparse
import glob
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.sky import compass_facing, observe_viewpoint, wonder_line
from scripts.utils import Point, load_points


def _run_id(gpx_file: str) -> str:
    return Path(gpx_file).stem


def _minute_into_run(points: list[Point], point: Point) -> int:
    times = [datetime.strptime(p.time, "%Y-%m-%dT%H:%M:%S") for p in points]
    t0 = min(times)
    t = datetime.strptime(point.time, "%Y-%m-%dT%H:%M:%S")
    return max(0, int((t - t0).total_seconds() // 60))


def build_viewpoint_record(point: Point, all_points: list[Point]) -> dict[str, Any]:
    sky = observe_viewpoint(point)
    highlight = sky.highlight
    return {
        "timestamp": point.timestamp,
        "time_local": point.time,
        "minute_into_run": _minute_into_run(all_points, point),
        "lat": point.lat,
        "lon": point.lon,
        "az": round(point.az, 1),
        "alt": point.alt,
        "fov": point.fov,
        "facing": compass_facing(point.az),
        "sky": sky.to_dict(),
        "wonder": wonder_line(highlight),
    }


def build_sky_log(gpx_file: str, *, with_zoom: bool = True) -> dict[str, Any]:
    points = load_points(gpx_file, with_zoom=with_zoom)
    viewpoints = [build_viewpoint_record(p, points) for p in points]
    run_id = _run_id(gpx_file)
    return {
        "run_id": run_id,
        "gpx": gpx_file,
        "viewpoint_count": len(viewpoints),
        "viewpoints": viewpoints,
    }


def render_markdown(log: dict[str, Any]) -> str:
    lines: list[str] = [
        f"# Sky log — {log['run_id']}",
        "",
        f"Source: `{log['gpx']}` · {log['viewpoint_count']} viewpoints",
        "",
        "| Minute | Facing | Alt | FOV | Highlight | Also visible |",
        "|---:|:---:|---:|---:|:---|:---|",
    ]
    for vp in log["viewpoints"]:
        sky = vp["sky"]
        highlight = sky.get("highlight")
        h_name = highlight["name"] if highlight else "—"
        also: list[str] = []
        for s in sky.get("stars", [])[:4]:
            if not highlight or s["name"] != highlight["name"]:
                also.append(s["name"])
        for p in sky.get("planets", []):
            if not highlight or p["name"] != highlight["name"]:
                also.append(p["name"])
        moon = sky.get("moon")
        if moon and moon.get("in_fov"):
            label = f"Moon ({moon['phase_name']})"
            if not highlight or highlight.get("kind") != "moon":
                also.append(label)
        also_s = ", ".join(also[:5]) if also else "—"
        lines.append(
            f"| {vp['minute_into_run']} | {vp['facing']} | {vp['alt']:.0f}° | "
            f"{vp['fov']:.0f}° | **{h_name}** | {also_s} |"
        )

    lines.extend(["", "## Viewpoints", ""])
    for vp in log["viewpoints"]:
        sky = vp["sky"]
        highlight = sky.get("highlight")
        h_name = highlight["name"] if highlight else "nothing named"
        lines.append(
            f"### Minute {vp['minute_into_run']} — facing {vp['facing']} "
            f"(alt {vp['alt']:.0f}°, FOV {vp['fov']:.0f}°)"
        )
        lines.append("")
        lines.append(f"- **Time:** {vp['time_local']}")
        lines.append(f"- **Highlight:** {h_name}")
        if vp.get("wonder"):
            lines.append(f"- **Wonder:** {vp['wonder']}")
        if sky.get("constellations"):
            lines.append(f"- **Constellations:** {', '.join(sky['constellations'])}")
        if sky.get("stars"):
            star_bits = ", ".join(f"{s['name']} (mag {s['magnitude']})" for s in sky["stars"][:8])
            lines.append(f"- **Stars:** {star_bits}")
        if sky.get("planets"):
            lines.append(f"- **Planets:** {', '.join(p['name'] for p in sky['planets'])}")
        moon = sky.get("moon")
        if moon:
            vis = "in view" if moon["in_fov"] else "not in this FOV"
            lines.append(
                f"- **Moon:** {moon['phase_name']}, {moon['illumination'] * 100:.0f}% lit, {vis}"
            )
        lines.append("")

    return "\n".join(lines)


def write_sky_log(log: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "sky_log.json"
    md_path = out_dir / "sky_log.md"
    with open(json_path, "w") as f:
        json.dump(log, f, indent=2)
    with open(md_path, "w") as f:
        f.write(render_markdown(log))
    print(f"Wrote {json_path} and {md_path}")


def process_gpx(gpx_file: str, sky_logs_dir: str, *, with_zoom: bool = True) -> dict[str, Any]:
    log = build_sky_log(gpx_file, with_zoom=with_zoom)
    write_sky_log(log, Path(sky_logs_dir) / log["run_id"])
    return log


def main(
    gpx_dir: str = "data/gpx",
    sky_logs_dir: str = "data/sky-logs",
    *,
    with_zoom: bool = True,
) -> None:
    gpx_files = sorted(glob.glob(os.path.join(gpx_dir, "*.gpx")))
    if not gpx_files:
        print(f"No GPX files found in {gpx_dir}")
        print("Drop a .gpx into data/gpx/ or run: make gpx")
        return
    for gpx_file in gpx_files:
        process_gpx(gpx_file, sky_logs_dir, with_zoom=with_zoom)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sky logs from GPX files")
    parser.add_argument("gpx_dir", nargs="?", default="data/gpx")
    parser.add_argument("sky_logs_dir", nargs="?", default="data/sky-logs")
    parser.add_argument("--no-zoom", action="store_true", help="Skip intentional FOV zoom points")
    args = parser.parse_args()
    main(args.gpx_dir, args.sky_logs_dir, with_zoom=not args.no_zoom)
