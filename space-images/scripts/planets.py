#!/usr/bin/env python3
"""
NASA Planet Image Downloader

Downloads up to 20 planet images for each planet from the NASA Image and Video Library.
"""

from __future__ import annotations

import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from common import (
    download_file,
    library_item_to_meta,
    library_search,
    repo_root,
    resolve_library_image_url,
    safe_filename,
    session,
    write_sidecar,
)


class PlanetImageDownloader:
    def __init__(self, download_dir: str | Path = "images") -> None:
        root = repo_root()
        path = Path(download_dir)
        self.download_dir = path if path.is_absolute() else root / path
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.sess = session()

    def is_valid_planet_image(self, item: dict[str, Any], planet_name: str) -> bool:
        try:
            data_block = item.get("data", [{}])[0]
            title = str(data_block.get("title", "")).lower()
            desc = str(data_block.get("description", "")).lower()
            keywords = data_block.get("keywords", [])
            keywords_text = " ".join(str(k) for k in keywords).lower() if keywords else ""
            combined = f"{title} {desc} {keywords_text}"
            if planet_name not in combined:
                return False
            exclude_terms = [
                "rover on",
                "landing site",
                "lander",
                "from rover",
                "spacecraft diagram",
                "mission patch",
                "crew",
                "astronaut",
                "launch",
                "rocket",
                "artist concept",
                "artist's concept",
                "illustration",
                "diagram",
                "schematic",
            ]
            if any(term in combined for term in exclude_terms):
                return False
            positive_indicators = [
                planet_name,
                "surface",
                "atmosphere",
                "view",
                "photo",
                "image",
                "picture",
                "observation",
                "captured",
            ]
            return any(term in combined for term in positive_indicators)
        except Exception:
            return False

    def download_planet_images(self, planet_name: str, max_images: int = 20) -> bool:
        print(f"\nDownloading images for: {planet_name.capitalize()}")
        all_valid_items: list[dict[str, Any]] = []
        pages_to_check = min(5, max(1, max_images // 2))

        for page in range(1, pages_to_check + 1):
            try:
                items, total_hits = library_search(planet_name, page=page, sess=self.sess)
            except Exception as e:
                print(f"   Failed to fetch page {page}: {e}")
                break
            if page == 1:
                print(f"   Total hits in NASA library: {total_hits}")
            if not items:
                break
            for item in items:
                if self.is_valid_planet_image(item, planet_name):
                    all_valid_items.append(item)
            time.sleep(0.5)

        if not all_valid_items:
            print(f"   No valid images found for '{planet_name}'")
            return False

        print(f"   Found {len(all_valid_items)} valid images")
        random.shuffle(all_valid_items)
        items_to_download = all_valid_items[:max_images]
        planet_dir = self.download_dir / planet_name
        planet_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for item in items_to_download:
            try:
                image_url = resolve_library_image_url(item, sess=self.sess)
                if not image_url:
                    continue
                meta = library_item_to_meta(
                    item,
                    image_url=image_url,
                    search_term=planet_name,
                    body=planet_name,
                )
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                nasa_id = safe_filename(meta.nasa_id or "unknown", max_len=30)
                filename = f"{planet_name}_{nasa_id}_{timestamp}.jpg"
                filepath = planet_dir / filename
                download_file(image_url, filepath, sess=self.sess)
                write_sidecar(filepath, meta)
                print(f"   ✓ {filepath.name}")
                count += 1
                if count >= max_images:
                    break
                time.sleep(0.5)
            except Exception as e:
                print(f"   Error processing image: {e}")
                continue

        print(f"   Successfully downloaded {count}/{max_images} images for {planet_name}")
        return count > 0

    def download_all(self) -> None:
        print("NASA Planet Image Downloader")
        print("=" * 60)
        planets = [
            "mercury",
            "venus",
            "earth",
            "mars",
            "jupiter",
            "saturn",
            "uranus",
            "neptune",
        ]
        results: list[tuple[str, bool]] = []
        start_time = time.time()
        for planet in planets:
            success = self.download_planet_images(planet, max_images=20)
            results.append((planet, success))
            time.sleep(1)
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("Summary:")
        for planet, success in results:
            status = "✓" if success else "✗"
            print(f"   {status} {planet.capitalize()}")
        print(f"\nTotal time: {elapsed:.1f} seconds")
        print(f"All images saved to: {self.download_dir.absolute()}/<planet>/")
        if not any(ok for _, ok in results):
            sys.exit(1)


if __name__ == "__main__":
    PlanetImageDownloader(download_dir="images").download_all()
