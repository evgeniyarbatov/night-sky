#!/usr/bin/env python3
"""Daily (or on-demand) inspiration: fetch → caption → album/daily."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from common import (
    apod_to_meta,
    copy_with_sidecars,
    download_file,
    fetch_apod,
    repo_root,
    safe_filename,
    session,
    social_post_text,
    write_sidecar,
)


def resolve_apod_image(max_back_days: int = 7) -> tuple[dict[str, Any], requests.Session]:
    """Fetch today's APOD, walking back if media is not an image."""
    sess = session()
    today = datetime.now().date()
    last_error: Exception | None = None
    for offset in range(max_back_days + 1):
        day = today - timedelta(days=offset)
        date_str = day.strftime("%Y-%m-%d")
        try:
            data = fetch_apod(date=date_str, sess=sess)
        except Exception as e:
            last_error = e
            continue
        if data.get("media_type") == "image" and (data.get("hdurl") or data.get("url")):
            return data, sess
        print(f"APOD {date_str} is not an image; trying previous day…")
    raise RuntimeError(f"No APOD image found in the last {max_back_days + 1} days: {last_error}")


def run_inspire(*, select: bool, root: Path) -> Path:
    data, sess = resolve_apod_image()
    meta = apod_to_meta(data)
    date = meta.date or datetime.now().strftime("%Y-%m-%d")
    day_dir = root / "album" / "daily" / date
    day_dir.mkdir(parents=True, exist_ok=True)

    stem = f"apod_{date}_{safe_filename(meta.title)}"
    image_path = day_dir / f"{stem}.jpg"
    print(f"APOD: {meta.title} ({date})")
    download_file(meta.image_url, image_path, sess=sess)
    write_sidecar(image_path, meta)

    post_path = day_dir / "post.txt"
    post_path.write_text(social_post_text(meta), encoding="utf-8")

    latest = root / "album" / "daily" / "LATEST.md"
    rel_img = f"{date}/{image_path.name}"
    latest.write_text(
        f"# Daily inspiration — {date}\n\n"
        f"**{meta.title}**\n\n"
        f"![APOD]({rel_img})\n\n"
        f"## Explain like I'm 10\n\n{meta.explain_like_10}\n\n"
        f"## Go deeper\n\n{meta.go_deeper}\n\n"
        f"Credit: {meta.credit}  \n"
        f"Source: {meta.source_url}\n\n"
        f"Social draft: `{date}/post.txt`\n",
        encoding="utf-8",
    )

    images_dir = root / "images"
    images_dir.mkdir(exist_ok=True)
    copy_with_sidecars(image_path, images_dir)

    if select:
        selected = root / "album" / "selected"
        copy_with_sidecars(image_path, selected)
        print("Also copied into album/selected/")

    print(f"Saved daily inspiration to {day_dir}")
    print(f"Story: {image_path.with_suffix('.md')}")
    print(f"Post draft: {post_path}")
    return image_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch today's APOD into album/daily with captions and a social draft."
    )
    parser.add_argument(
        "--select",
        action="store_true",
        help="Also copy today's image into album/selected/",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: parent of scripts/)",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root else repo_root()
    try:
        run_inspire(select=args.select, root=root)
    except Exception as e:
        print(f"inspire failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
