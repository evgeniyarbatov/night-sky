#!/usr/bin/env python3
"""Daily (or on-demand) inspiration: fetch → caption → album/daily."""

from __future__ import annotations

import argparse
import random
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
    load_meta,
    repo_root,
    safe_filename,
    session,
    write_sidecar,
)


def existing_apod_dates(day_dir: Path) -> set[str]:
    """APOD calendar dates already present under day_dir (from sidecars)."""
    found: set[str] = set()
    if not day_dir.is_dir():
        return found
    for path in day_dir.glob("*.json"):
        meta = load_meta(path)
        if meta and meta.date:
            found.add(meta.date)
    return found


def try_apod_image(
    date_str: str,
    *,
    sess: requests.Session,
    exclude_dates: set[str],
) -> dict[str, Any] | None:
    if date_str in exclude_dates:
        return None
    data = fetch_apod(date=date_str, sess=sess)
    if data.get("media_type") == "image" and (data.get("hdurl") or data.get("url")):
        return data
    return None


def resolve_apod_image(
    *,
    exclude_dates: set[str],
    max_back_days: int = 7,
    random_attempts: int = 24,
) -> tuple[dict[str, Any], requests.Session]:
    """Pick an APOD image not already saved (prefer recent days, then random)."""
    sess = session()
    today = datetime.now().date()
    last_error: Exception | None = None

    for offset in range(max_back_days + 1):
        day = today - timedelta(days=offset)
        date_str = day.strftime("%Y-%m-%d")
        try:
            data = try_apod_image(date_str, sess=sess, exclude_dates=exclude_dates)
        except Exception as e:
            last_error = e
            continue
        if data is not None:
            return data, sess
        if date_str not in exclude_dates:
            print(f"APOD {date_str} is not an image; trying previous day…")

    one_year_ago = today - timedelta(days=365)
    tried: set[str] = set(exclude_dates)
    for _ in range(random_attempts):
        random_date = one_year_ago + timedelta(days=random.randint(0, 365))
        date_str = random_date.strftime("%Y-%m-%d")
        if date_str in tried:
            continue
        tried.add(date_str)
        try:
            data = try_apod_image(date_str, sess=sess, exclude_dates=exclude_dates)
        except Exception as e:
            last_error = e
            continue
        if data is not None:
            return data, sess

    raise RuntimeError(
        "No new APOD image found (recent days and random sample exhausted"
        + (f": {last_error}" if last_error else "")
        + ")"
    )


def run_inspire(*, root: Path) -> Path:
    run_date = datetime.now().strftime("%Y-%m-%d")
    day_dir = root / "album" / "daily" / run_date
    day_dir.mkdir(parents=True, exist_ok=True)

    exclude = existing_apod_dates(day_dir)
    data, sess = resolve_apod_image(exclude_dates=exclude)
    meta = apod_to_meta(data)
    apod_date = meta.date or run_date

    stem = f"apod_{apod_date}_{safe_filename(meta.title)}"
    image_path = day_dir / f"{stem}.jpg"
    if image_path.exists():
        # Same calendar day / title collision — treat as already present.
        raise RuntimeError(f"Image already exists: {image_path.name}")

    print(f"APOD: {meta.title} ({apod_date})")
    download_file(meta.image_url, image_path, sess=sess)
    write_sidecar(image_path, meta)

    latest = root / "album" / "daily" / "LATEST.md"
    rel_img = f"{run_date}/{image_path.name}"
    latest.write_text(
        f"# Daily inspiration — {run_date}\n\n"
        f"**{meta.title}**\n\n"
        f"![APOD]({rel_img})\n\n"
        f"{meta.go_deeper}\n\n"
        f"Credit: {meta.credit}  \n"
        f"Source: {meta.source_url}\n",
        encoding="utf-8",
    )

    images_dir = root / "images"
    images_dir.mkdir(exist_ok=True)
    copy_with_sidecars(image_path, images_dir)

    n = sum(1 for p in day_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    print(f"Saved to {day_dir} ({n} image(s) today)")
    print(f"Story: {image_path.with_suffix('.md')}")
    return image_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch an APOD into album/daily (adds a new photo each run)."
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
        run_inspire(root=root)
    except Exception as e:
        print(f"inspire failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
