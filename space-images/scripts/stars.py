#!/usr/bin/env python3
"""
NASA Deep-Sky Image Downloader

Downloads telescope photographs of nebulae, galaxies and star clusters from the NASA Image and
Video Library. Re-runs skip NASA IDs already on disk (accumulate new only).
"""

from __future__ import annotations

import argparse
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from common import (
    download_file,
    library_item_to_meta,
    library_search,
    load_meta,
    resolve_library_image_url,
    safe_filename,
    session,
    write_sidecar,
)

from planets import GLOBAL_EXCLUDE, _item_nasa_id

SEARCH_QUERIES: tuple[str, ...] = (
    "hubble nebula",
    "hubble galaxy",
    "hubble star cluster",
    "globular cluster",
    "carina nebula",
    "orion nebula",
    "pillars of creation",
    "planetary nebula",
    "supernova remnant",
    "star-forming region",
    "webb nebula",
    "spiral galaxy",
)

SUBJECT_TERMS: tuple[str, ...] = (
    "nebula",
    "nebulae",
    "galaxy",
    "galaxies",
    "cluster",
    "star",
    "stars",
    "supernova",
    "remnant",
    "pillars",
    "stellar",
    "nursery",
)

# A telescope credit is the strongest sign the frame is an observation, not PR or hardware.
TELESCOPES: tuple[str, ...] = ("hubble", "webb", "jwst", "chandra", "spitzer")

DEEP_SKY_EXCLUDE: tuple[str, ...] = (
    "spectrum",
    "spectra",
    "light curve",
    "graph",
    "chart",
    "plot",
    "comparison",
    "side by side",
    "mirror",
    "instrument",
    "sunshield",
    "simulation",
    "history of",
    "examples of",
    "arranged",
    "panel",
    "labeled",
    "labelled",
    "annotated",
)


def is_deep_sky_photo(item: dict[str, Any]) -> bool:
    data_block = item.get("data", [{}])[0]
    title = str(data_block.get("title", "")).lower()
    desc = str(data_block.get("description", "")).lower()
    keywords = " ".join(str(k).lower() for k in data_block.get("keywords") or [])
    combined = f"{title} {desc} {keywords}"
    if not any(re.search(rf"\b{re.escape(t)}\b", title) for t in SUBJECT_TERMS):
        return False
    if not any(t in combined for t in TELESCOPES):
        return False
    return not any(t in combined for t in GLOBAL_EXCLUDE + DEEP_SKY_EXCLUDE)


def existing_nasa_ids(out_dir: Path) -> set[str]:
    return {
        meta.nasa_id
        for path in out_dir.glob("*.json")
        if (meta := load_meta(path)) and meta.nasa_id
    }


def download_stars(out_dir: Path, limit: int) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    sess = session()
    seen = existing_nasa_ids(out_dir)
    candidates: list[dict[str, Any]] = []
    for query in random.sample(SEARCH_QUERIES, len(SEARCH_QUERIES)):
        if len(candidates) >= limit * 3:
            break
        try:
            items, _ = library_search(query, page=random.randint(1, 2), sess=sess)
        except Exception as e:
            print(f"Failed to search {query!r}: {e}")
            continue
        for item in items:
            nasa_id = _item_nasa_id(item)
            if nasa_id and nasa_id not in seen and is_deep_sky_photo(item):
                candidates.append(item)
                seen.add(nasa_id)
        time.sleep(0.5)

    random.shuffle(candidates)
    count = 0
    for item in candidates:
        if count >= limit:
            break
        try:
            image_url = resolve_library_image_url(item, sess=sess)
            if not image_url:
                continue
            meta = library_item_to_meta(item, image_url=image_url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filepath = out_dir / f"stars_{safe_filename(meta.nasa_id, max_len=30)}_{timestamp}.jpg"
            download_file(image_url, filepath, sess=sess)
            write_sidecar(filepath, meta)
            print(f"✓ {meta.title} → {filepath.name}")
            count += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"Error processing image: {e}")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Download NASA deep-sky photographs.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(os.environ.get("SPACE_IMAGES_OUTPUT_DIR", "images")) / "stars",
        help="Directory to save images to (default: images/stars/)",
    )
    parser.add_argument("--limit", type=int, default=20, help="new images to download")
    args = parser.parse_args()
    count = download_stars(args.output_dir, args.limit)
    print(f"Downloaded {count}/{args.limit} new images to {args.output_dir.absolute()}")
    if count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
