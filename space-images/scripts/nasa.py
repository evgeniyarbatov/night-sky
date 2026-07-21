#!/usr/bin/env python3
"""
NASA Space Image Downloader

Downloads images from:
1. Astronomy Picture of the Day (APOD) API
2. NASA Image and Video Library (random space object search)
"""

from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

from common import (
    apod_to_meta,
    download_file,
    fetch_apod,
    library_item_to_meta,
    library_search,
    nasa_api_key,
    repo_root,
    resolve_library_image_url,
    safe_filename,
    session,
    write_sidecar,
)


class SpaceImageDownloader:
    def __init__(self, download_dir: str | Path = "images") -> None:
        root = repo_root()
        path = Path(download_dir)
        self.download_dir = path if path.is_absolute() else root / path
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = nasa_api_key()
        self.sess = session()

    def download_apod(self) -> bool:
        """Download APOD from a random day within the last year."""
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)
        for _ in range(8):
            random_days = random.randint(0, 365)
            random_date = one_year_ago + timedelta(days=random_days)
            date_str = random_date.strftime("%Y-%m-%d")
            try:
                data = fetch_apod(date=date_str, api_key=self.api_key, sess=self.sess)
            except Exception as e:
                print(f"Failed to fetch APOD {date_str}: {e}")
                continue
            if data.get("media_type") != "image":
                print(f"APOD for {date_str} is a video, trying another date…")
                continue
            meta = apod_to_meta(data)
            if not meta.image_url:
                continue
            filename = f"apod_{date_str}_{safe_filename(meta.title)}.jpg"
            filepath = self.download_dir / filename
            print(f"APOD: {meta.title} ({meta.date})")
            try:
                download_file(meta.image_url, filepath, sess=self.sess)
                write_sidecar(filepath, meta)
                print(f"✓ Downloaded: {filepath}")
                return True
            except Exception as e:
                print(f"✗ Failed to download APOD image: {e}")
                return False
        print("Failed to find an APOD image after several tries")
        return False

    def download_nasa_library_random(self) -> bool:
        """Search and download a random space object from the NASA Image Library."""
        space_objects = [
            "mars",
            "jupiter",
            "saturn",
            "venus",
            "mercury",
            "uranus",
            "neptune",
            "earth",
            "moon",
            "comet",
            "galaxy",
            "andromeda",
            "milky way",
            "nebula",
            "betelgeuse",
            "sirius",
            "vega",
            "polaris",
        ]
        search_term = random.choice(space_objects)
        try:
            items, _ = library_search(search_term, sess=self.sess)
        except Exception as e:
            print(f"Failed to search NASA library for '{search_term}': {e}")
            return False
        if not items:
            print(f"No images found for '{search_term}'")
            return False

        item = random.choice(items[:20])
        try:
            image_url = resolve_library_image_url(item, sess=self.sess)
        except Exception as e:
            print(f"Failed to resolve image assets: {e}")
            return False
        if not image_url:
            print(f"No suitable image found for '{search_term}'")
            return False

        meta = library_item_to_meta(item, image_url=image_url, search_term=search_term)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nasa_library_{safe_filename(search_term)}_{timestamp}.jpg"
        filepath = self.download_dir / filename
        print(f"NASA Library: {meta.title}")
        print(f"Search term: {search_term} · destination: {meta.destination}")
        try:
            download_file(image_url, filepath, sess=self.sess)
            write_sidecar(filepath, meta)
            print(f"✓ Downloaded: {filepath}")
            return True
        except Exception as e:
            print(f"✗ Failed to download library image: {e}")
            return False

    def download_all(self) -> None:
        print("NASA Space Image Downloader")
        print("=" * 40)
        results: list[tuple[str, bool]] = []
        print("\n1. Downloading Astronomy Picture of the Day…")
        results.append(("APOD", self.download_apod()))
        print("\n2. Downloading random space object from NASA Library…")
        results.append(("NASA Library", self.download_nasa_library_random()))
        print("\n" + "=" * 40)
        print("Summary:")
        for source, success in results:
            status = "✓" if success else "✗"
            print(f"{status} {source}")
        print(f"\nImages saved to: {self.download_dir.absolute()}")
        if not any(ok for _, ok in results):
            sys.exit(1)


if __name__ == "__main__":
    SpaceImageDownloader().download_all()
