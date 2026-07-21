#!/usr/bin/env python3
"""Build browse indexes by destination from sidecar JSON files."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from common import (
    DESTINATIONS,
    ImageMeta,
    destination_label,
    iter_sidecars,
    load_meta,
    repo_root,
)

BROWSE_ORDER = [
    "moon",
    "mars",
    "gas-giants",
    "nebulae",
    "earth-from-space",
    "sun",
    "comets-asteroids",
    "stars",
    "other",
]


def default_scan_roots(root: Path) -> list[Path]:
    return [
        root / "images",
        root / "planets",
        root / "album" / "daily",
        root / "album" / "selected",
    ]


def relative_to(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def image_for_sidecar(json_path: Path) -> Path | None:
    for ext in (".jpg", ".jpeg", ".png"):
        candidate = json_path.with_suffix(ext)
        if candidate.is_file():
            return candidate
    return None


def build_browse(root: Path, scan_roots: list[Path] | None = None) -> Path:
    browse_dir = root / "browse"
    browse_dir.mkdir(parents=True, exist_ok=True)

    by_dest: dict[str, list[tuple[Path, ImageMeta]]] = defaultdict(list)
    roots = scan_roots or default_scan_roots(root)
    seen: set[str] = set()

    def rank_path(p: Path) -> int:
        s = str(p)
        if "album/selected" in s or "album\\selected" in s:
            return 0
        if "album/daily" in s or "album\\daily" in s:
            return 1
        if "/images/" in s or "\\images\\" in s:
            return 2
        return 3

    entries: list[tuple[Path, ImageMeta]] = []
    for json_path in iter_sidecars(roots):
        meta = load_meta(json_path)
        if meta is None:
            continue
        image = image_for_sidecar(json_path)
        if image is None:
            continue
        entries.append((image, meta))

    entries.sort(key=lambda t: (rank_path(t[0]), t[1].title))
    for image, meta in entries:
        key = meta.nasa_id or meta.title or image.stem
        if key in seen:
            continue
        seen.add(key)
        dest = meta.destination if meta.destination in DESTINATIONS else "other"
        by_dest[dest].append((image, meta))

    for dest in by_dest:
        by_dest[dest].sort(key=lambda t: (t[1].date or "", t[1].title))

    all_dests = [d for d in BROWSE_ORDER if d in by_dest] + sorted(
        d for d in by_dest if d not in BROWSE_ORDER
    )

    index_lines = [
        "# Browse by destination",
        "",
        "Generated from local sidecars. Run `make browse` after downloading.",
        "",
    ]
    total = sum(len(v) for v in by_dest.values())
    index_lines.append(f"**{total}** image(s) across **{len(by_dest)}** destination(s).\n")

    for dest in all_dests:
        entries = by_dest[dest]
        label = destination_label(dest)
        dest_dir = browse_dir / dest
        dest_dir.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {label}",
            "",
            f"{len(entries)} image(s).",
            "",
        ]
        for image, meta in entries:
            rel_img = relative_to(image, root)
            rel_md = relative_to(image.with_suffix(".md"), root)
            lines.append(f"## {meta.title}")
            lines.append("")
            lines.append(f"- Date: {meta.date or '—'}")
            lines.append(f"- File: `{rel_img}`")
            if image.with_suffix(".md").is_file():
                lines.append(f"- Story: [`{Path(rel_md).name}`](../../{rel_md})")
            lines.append("")
            if meta.explain_like_10:
                lines.append(f"**Explain like I'm 10:** {meta.explain_like_10}")
                lines.append("")
        (dest_dir / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        index_lines.append(f"- [{label}]({dest}/INDEX.md) — {len(entries)}")

    index_path = browse_dir / "INDEX.md"
    index_path.write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    return index_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build browse/ indexes by destination")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve() if args.root else repo_root()
    try:
        index = build_browse(root)
    except Exception as e:
        print(f"browse failed: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Wrote {index}")
    print(index.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
