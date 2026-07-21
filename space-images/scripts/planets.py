#!/usr/bin/env python3
"""
NASA Planet Image Downloader

Downloads up to 20 planet images for each planet from the NASA Image and Video Library.
"""

from __future__ import annotations

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
    repo_root,
    resolve_library_image_url,
    safe_filename,
    session,
    write_sidecar,
)

# Bare planet queries rank event photos and program homonyms first; bias toward the body.
PLANET_SEARCH_QUERY: dict[str, str] = {
    "mercury": "mercury planet",
    "venus": "venus planet",
    "earth": "earth from space",
    "mars": "mars planet",
    "jupiter": "jupiter planet",
    "saturn": "saturn planet",
    "uranus": "uranus planet",
    "neptune": "neptune planet",
}

# Hardware, people, graphics — not photos of the body itself.
GLOBAL_EXCLUDE: tuple[str, ...] = (
    "artist concept",
    "artist's concept",
    "artists concept",
    "concept art",
    "illustration",
    "diagram",
    "schematic",
    "infographic",
    "mission patch",
    "logo",
    "poster",
    "artwork",
    "wind tunnel",
    "spin tunnel",
    "scale model",
    "engineering model",
    "mockup",
    "mock-up",
    "mock up",
    "model of",
    "astronaut",
    "cosmonaut",
    "crew portrait",
    "launch pad",
    "liftoff",
    "lift-off",
    "celebration",
    "ceremony",
    "conference",
    "headquarters",
    "press conference",
    "speech",
    "award",
    "handshake",
    "students",
    "classroom",
    "visitor center",
    "exhibit",
    "museum",
    "employees",
    "clean room",
    "cleanroom",
    "cutaway",
    "spacecraft diagram",
)

# Homonyms and named programs that share a planet word.
PLANET_EXCLUDE: dict[str, tuple[str, ...]] = {
    "mercury": (
        "project mercury",
        "mercury project",
        "mercury program",
        "mercury capsule",
        "mercury-redstone",
        "mercury redstone",
        "mercury-atlas",
        "mercury atlas",
        "friendship 7",
        "space capsule",
    ),
    "venus": ("venus transit event",),
    "earth": ("earth day",),
    "mars": ("mars celebration", "mars day"),
    "saturn": (
        "saturn v",
        "saturn 5",
        "saturn i",
        "saturn 1",
        "saturn apollo",
        "apollo program",
        "saturn rocket",
    ),
}

# Moons in the title usually mean the subject is not the planet.
PLANET_MOON_TITLE: dict[str, tuple[str, ...]] = {
    "earth": (),  # Earth–Moon pairs are classic planet imagery
    "mars": ("phobos", "deimos"),
    "jupiter": ("europa", "ganymede", "callisto", "io"),
    "saturn": (
        "titan",
        "enceladus",
        "mimas",
        "iapetus",
        "rhea",
        "dione",
        "tethys",
    ),
    "uranus": ("miranda", "titania", "oberon", "ariel", "umbriel"),
    "neptune": ("triton",),
}

# Non-Earth planets as a point of light from crewed missions are not planet portraits.
CREWED_CONTEXT: tuple[str, ...] = (
    "expedition",
    "sts-",
    "international space station",
    "from iss",
    "space shuttle",
)

# Strong evidence the item is imagery of the body (not just a name-drop).
BODY_TERMS: tuple[str, ...] = (
    "surface",
    "atmosphere",
    "cloud",
    "ring",
    "crater",
    "terrain",
    "mosaic",
    "globe",
    "disk",
    "disc",
    "horizon",
    "flyby",
    "from orbit",
    "global",
    "crescent",
    "storm",
    "polar",
    "topograph",
    "albedo",
    "false color",
    "true color",
    "enhanced color",
    "hemisphere",
    "from space",
    "blue marble",
)

PLANET_MISSIONS: dict[str, tuple[str, ...]] = {
    "mercury": ("messenger", "mariner 10", "mariner10", "bepicolombo"),
    "venus": ("magellan", "akatsuki", "venera", "parker solar", "galileo"),
    "earth": (
        "galileo",
        "apollo",
        "dscovr",
        "suomi",
        "terra",
        "aqua",
        "goes",
        "landsat",
        "himawari",
        "epix",
    ),
    "mars": (
        "mro",
        "mgs",
        "viking",
        "curiosity",
        "perseverance",
        "opportunity",
        "spirit",
        "maven",
        "mars express",
        "mars global",
        "mars reconnaissance",
        "mars odyssey",
        "pathfinder",
        "hubble",
    ),
    "jupiter": ("juno", "galileo", "voyager", "cassini", "hubble", "new horizons", "pioneer"),
    "saturn": ("cassini", "voyager", "pioneer", "hubble"),
    "uranus": ("voyager", "hubble"),
    "neptune": ("voyager", "hubble"),
}


class PlanetImageDownloader:
    def __init__(self, download_dir: str | Path = "images") -> None:
        root = repo_root()
        path = Path(download_dir)
        self.download_dir = path if path.is_absolute() else root / path
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.sess = session()

    def is_valid_planet_image(self, item: dict[str, Any], planet_name: str) -> bool:
        data_block = item.get("data", [{}])[0]
        title = str(data_block.get("title", "")).lower()
        desc = str(data_block.get("description", "")).lower()
        keywords = data_block.get("keywords") or []
        keywords_text = " ".join(str(k).lower() for k in keywords)
        combined = f"{title} {desc} {keywords_text}"

        if not re.search(rf"\b{re.escape(planet_name)}\b", title):
            return False

        if any(term in combined for term in GLOBAL_EXCLUDE):
            return False
        if any(term in combined for term in PLANET_EXCLUDE.get(planet_name, ())):
            return False

        for moon in PLANET_MOON_TITLE.get(planet_name, ()):
            if re.search(rf"\b{re.escape(moon)}\b", title):
                return False

        if planet_name != "earth" and any(term in combined for term in CREWED_CONTEXT):
            return False

        kw_hit = any(planet_name in str(k).lower() for k in keywords)
        body_hit = any(term in title or term in desc for term in BODY_TERMS)
        mission_hit = any(m in combined for m in PLANET_MISSIONS.get(planet_name, ()))
        if kw_hit or body_hit or mission_hit:
            return True

        # Short planet-forward titles ("Crescent Mercury", "Bold Saturn").
        title_words = re.findall(r"[a-z0-9]+", title)
        return planet_name in title_words and len(title_words) <= 6

    def download_planet_images(self, planet_name: str, max_images: int = 20) -> bool:
        print(f"\nDownloading images for: {planet_name.capitalize()}")
        all_valid_items: list[dict[str, Any]] = []
        pages_to_check = min(5, max(1, max_images // 2))
        query = PLANET_SEARCH_QUERY.get(planet_name, f"{planet_name} planet")

        for page in range(1, pages_to_check + 1):
            try:
                items, total_hits = library_search(query, page=page, sess=self.sess)
            except Exception as e:
                print(f"   Failed to fetch page {page}: {e}")
                break
            if page == 1:
                print(f"   Search: {query!r} — {total_hits} hits")
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
