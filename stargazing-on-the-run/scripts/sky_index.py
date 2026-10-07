"""Personal sky index: objects and constellations met on runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _default_index_path() -> Path:
    return Path("data/sky-index.json")


def load_index(path: Path | None = None) -> dict[str, Any]:
    p = path or _default_index_path()
    if not p.is_file():
        return {"objects": {}, "constellations": {}}
    with open(p) as f:
        data: dict[str, Any] = json.load(f)
    return data


def save_index(index: dict[str, Any], path: Path | None = None) -> None:
    p = path or _default_index_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(index, f, indent=2, sort_keys=True)


def update_index_from_log(
    log: dict[str, Any], index: dict[str, Any] | None = None
) -> dict[str, Any]:
    index = index if index is not None else load_index()
    objects = index.setdefault("objects", {})
    constellations = index.setdefault("constellations", {})
    run_id = log["run_id"]

    for vp in log.get("viewpoints", []):
        date = vp["time_local"][:10]
        facing = vp["facing"]
        sky = vp["sky"]

        for star in sky.get("stars", []):
            _meet(objects, star["name"], "star", date, run_id, facing)
        for planet in sky.get("planets", []):
            _meet(objects, planet["name"], "planet", date, run_id, facing)
        moon = sky.get("moon")
        if moon and moon.get("in_fov"):
            _meet(objects, "Moon", "moon", date, run_id, facing)
        for name in sky.get("constellations", []):
            _meet(constellations, name, "constellation", date, run_id, facing)

    return index


def _meet(
    store: dict[str, Any],
    name: str,
    kind: str,
    date: str,
    run_id: str,
    facing: str,
) -> None:
    if name in store:
        return
    store[name] = {
        "kind": kind,
        "first_seen": date,
        "run_id": run_id,
        "facing": facing,
    }


def rebuild_from_sky_logs(
    sky_logs_dir: str = "data/sky-logs", index_path: Path | None = None
) -> dict[str, Any]:
    root = Path(sky_logs_dir)
    index: dict[str, Any] = {"objects": {}, "constellations": {}}
    if not root.is_dir():
        save_index(index, index_path)
        return index

    logs = sorted(root.glob("*/sky_log.json"))
    # Sort by earliest viewpoint date so first-seen is chronological
    dated: list[tuple[str, dict[str, Any]]] = []
    for path in logs:
        with open(path) as f:
            log = json.load(f)
        times = [vp["time_local"] for vp in log.get("viewpoints", [])]
        key = min(times) if times else path.as_posix()
        dated.append((key, log))
    dated.sort(key=lambda x: x[0])

    for _, log in dated:
        update_index_from_log(log, index)

    save_index(index, index_path)
    return index


def render_index_markdown(index: dict[str, Any]) -> str:
    lines = ["# Personal sky index", ""]
    objects = index.get("objects", {})
    constellations = index.get("constellations", {})

    lines.append(f"Objects met: **{len(objects)}** · Constellations: **{len(constellations)}**")
    lines.append("")
    lines.append("## Objects")
    lines.append("")
    lines.append("| Name | Kind | First seen | Run | Facing |")
    lines.append("|---|---|---|---|---|")
    for name in sorted(objects, key=lambda n: objects[n]["first_seen"]):
        e = objects[name]
        lines.append(
            f"| {name} | {e['kind']} | {e['first_seen']} | {e['run_id']} | {e['facing']} |"
        )

    lines.extend(["", "## Constellations", ""])
    lines.append("| Name | First seen | Run | Facing |")
    lines.append("|---|---|---|---|")
    for name in sorted(constellations, key=lambda n: constellations[n]["first_seen"]):
        e = constellations[name]
        lines.append(f"| {name} | {e['first_seen']} | {e['run_id']} | {e['facing']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild personal sky index from sky logs")
    parser.add_argument("--sky-logs", default="data/sky-logs")
    parser.add_argument("--out", default="data/sky-index.json")
    args = parser.parse_args()
    index = rebuild_from_sky_logs(args.sky_logs, Path(args.out))
    md_path = Path(args.out).with_suffix(".md")
    md_path.write_text(render_index_markdown(index))
    print(
        f"Index: {len(index.get('objects', {}))} objects, "
        f"{len(index.get('constellations', {}))} constellations → {args.out}"
    )


if __name__ == "__main__":
    main()
