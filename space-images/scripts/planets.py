#!/usr/bin/env python3
"""
NASA Planet Image Downloader

Downloads up to 20 planet images for each planet from the NASA Image and Video Library.
Re-runs skip NASA IDs already on disk (accumulate new only).
Keeps body/surface imagery (globe, orbit, rover terrain); drops PR, people, and hardware.
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
    load_meta,
    repo_root,
    resolve_library_image_url,
    safe_filename,
    session,
    write_sidecar,
)

# Multiple queries per body so surface/globe hits are not buried under mission PR.
PLANET_SEARCH_QUERIES: dict[str, tuple[str, ...]] = {
    "mercury": ("mercury planet", "mercury surface", "mercury messenger"),
    "venus": ("venus planet", "venus surface", "venus atmosphere"),
    "earth": ("earth from space", "blue marble", "earth globe"),
    "mars": (
        "mars surface",
        "mars globe",
        "mars from orbit",
        "mars crater terrain",
        "planet mars hubble",
        "mars planet",
    ),
    "jupiter": ("jupiter atmosphere", "jupiter from juno", "jupiter planet"),
    "saturn": ("saturn rings", "saturn from cassini", "saturn planet"),
    "uranus": ("uranus voyager", "uranus atmosphere", "uranus planet"),
    "neptune": ("neptune voyager", "neptune atmosphere", "neptune planet"),
}

# Hardware, people, graphics, PR — not photos of the body or its terrain.
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
    "museum exhibit",
    "museum",
    "employees",
    "clean room",
    "cleanroom",
    "cutaway",
    "spacecraft diagram",
    "briefing",
    "science overview",
    "engineering overview",
    "technology overview",
    "landing update",
    "post-landing",
    "mission support",
    "mission control",
    "control room",
    "marketsite",
    "nasdaq",
    "empire state",
    "illuminated for",
    "times square",
    "entry vehicle",
    "payload canister",
    "payload fairing",
    "assembly facility",
    "processing facility",
    "overhead crane",
    "team members",
    "from left",
    "pictured here",
    "administrator",
    "media day",
    "ribbon cutting",
    "unveiling",
    "signed by",
    "autograph",
    "animation",
    "frame from an animation",
    "space simulator",
    "vacuum chamber",
    "flight model",
    "engineering unit",
    "test model",
    "team inspect",
    "technicians",
    "technician",
    "hair net",
    "hairnet",
    "bunny suit",
    "clean-room",
    "clean suit",
    "ground test",
    "lab test",
    "boresight",
    "downtrack",
    "crosstrack",
    "radiation dosage",
    "dose equivalent",
    "cosmic ray",
    "rem/yr",
    "stereo imager on mars",
    "face-on",
    "landing area narrowed",
    "candidate landing",
    "landing site candidates",
)

# Allowed non-planet words in short portrait titles ("Crescent Mercury", "Blue Marble Earth").
PORTRAIT_TITLE_WORDS: frozenset[str] = frozenset(
    {
        "the",
        "planet",
        "crescent",
        "bold",
        "pale",
        "full",
        "blue",
        "red",
        "marble",
        "globe",
        "disk",
        "disc",
        "view",
        "of",
        "from",
        "space",
        "orbit",
        "mosaic",
        "true",
        "color",
        "false",
        "enhanced",
        "global",
        "map",
        "image",
        "photo",
        "portrait",
    }
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
    "mars": (
        "mars celebration",
        "mars day",
        "mars 2020 engineering",
        "mars 2020 science overview",
        "mars 2020 technology",
        "perseverance on nasdaq",
        "illuminated for mars",
    ),
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

# Evidence the frame is the body (globe/disk) or its terrain (orbit or rover).
BODY_TERMS: tuple[str, ...] = (
    "surface",
    "surfaces",
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
    "in orbit",
    "orbital",
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
    "the planet",
    "planet mars",
    "planet mercury",
    "planet venus",
    "planet jupiter",
    "planet saturn",
    "planet uranus",
    "planet neptune",
    "full disk",
    "full-disc",
    "full-disk",
    "whole planet",
    "whole-planet",
    "rock",
    "rocks",
    "outcrop",
    "dune",
    "dunes",
    "regolith",
    "soil",
    "panorama",
    "layered",
    "sediment",
    "ridge",
    "cliff",
    "valley",
    "canyon",
    "channel",
    "boulder",
    "sand",
    "dust devil",
    "ice cap",
    "polar cap",
    "volcan",
    "plains",
    "basin",
    "impact",
    "ejecta",
    "bedrock",
    "hillside",
    "slope",
    "gully",
    "delta",
    "lava",
    "frost",
)

# Short ambiguous body terms need word boundaries (avoid "rock" in "rocket").
_BODY_WORD_BOUNDARY: frozenset[str] = frozenset(
    {
        "rock",
        "rocks",
        "ring",
        "soil",
        "sand",
        "slope",
        "delta",
        "lava",
        "frost",
        "cloud",
        "storm",
        "polar",
        "basin",
        "plains",
        "global",
        "orbital",
        "surface",
        "surfaces",
        "terrain",
        "horizon",
        "crater",
        "globe",
        "disk",
        "disc",
    }
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
        "ingenuity",
        "hirise",
        "ctx",
        "mastcam",
        "navcam",
        "hazcam",
    ),
    "jupiter": ("juno", "galileo", "voyager", "cassini", "hubble", "new horizons", "pioneer"),
    "saturn": ("cassini", "voyager", "pioneer", "hubble"),
    "uranus": ("voyager", "hubble"),
    "neptune": ("voyager", "hubble"),
}


def _has_term(text: str, term: str) -> bool:
    if term in _BODY_WORD_BOUNDARY or " " not in term and len(term) <= 5:
        return bool(re.search(rf"\b{re.escape(term)}\b", text))
    return term in text


def _item_nasa_id(item: dict[str, Any]) -> str:
    data_block = item.get("data", [{}])[0]
    return str(data_block.get("nasa_id") or "").strip()


class PlanetImageDownloader:
    def __init__(self, download_dir: str | Path = "images") -> None:
        root = repo_root()
        path = Path(download_dir)
        self.download_dir = path if path.is_absolute() else root / path
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.sess = session()

    def existing_nasa_ids(self, planet_dir: Path) -> set[str]:
        found: set[str] = set()
        if not planet_dir.is_dir():
            return found
        for path in planet_dir.glob("*.json"):
            meta = load_meta(path)
            if meta and meta.nasa_id:
                found.add(meta.nasa_id)
        return found

    def is_valid_planet_image(self, item: dict[str, Any], planet_name: str) -> bool:
        data_block = item.get("data", [{}])[0]
        title = str(data_block.get("title", "")).lower()
        desc = str(data_block.get("description", "")).lower()
        keywords = data_block.get("keywords") or []
        keywords_text = " ".join(str(k).lower() for k in keywords)
        combined = f"{title} {desc} {keywords_text}"

        planet_in_title = bool(re.search(rf"\b{re.escape(planet_name)}\b", title))
        planet_in_kw = any(planet_name in str(k).lower() for k in keywords)
        planet_in_desc = bool(re.search(rf"\b{re.escape(planet_name)}\b", desc))
        mission_hit = any(m in combined for m in PLANET_MISSIONS.get(planet_name, ()))

        # Title must name the planet, or a known mission with planet in keywords/desc.
        if not planet_in_title and not (mission_hit and (planet_in_kw or planet_in_desc)):
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

        body_hit = any(_has_term(title, term) or _has_term(desc, term) for term in BODY_TERMS)
        if body_hit:
            return True

        # Short portrait titles only ("Crescent Mercury") — not "Inspecting Mars Helicopter".
        if not planet_in_title:
            return False
        title_words = re.findall(r"[a-z0-9]+", title)
        if not (1 <= len(title_words) <= 6):
            return False
        extras = [w for w in title_words if w != planet_name]
        return all(w in PORTRAIT_TITLE_WORDS for w in extras)

    def download_planet_images(self, planet_name: str, max_images: int = 20) -> bool:
        print(f"\nDownloading images for: {planet_name.capitalize()}")
        planet_dir = self.download_dir / planet_name
        planet_dir.mkdir(parents=True, exist_ok=True)
        existing = self.existing_nasa_ids(planet_dir)
        if existing:
            print(f"   Already on disk: {len(existing)} NASA IDs (will skip)")

        all_valid_items: list[dict[str, Any]] = []
        seen_ids: set[str] = set(existing)
        queries = PLANET_SEARCH_QUERIES.get(planet_name, (f"{planet_name} planet",))
        pool_target = max(max_images * 3, max_images)
        max_pages_per_query = 3

        def collect_page(query: str, page: int) -> bool:
            """Fetch one search page into all_valid_items. Returns False on empty/error."""
            try:
                items, total_hits = library_search(query, page=page, sess=self.sess)
            except Exception as e:
                print(f"   Failed to fetch {query!r} page {page}: {e}")
                return False
            if page == 1:
                print(f"   Search: {query!r} — {total_hits} hits")
            if not items:
                return False
            for item in items:
                nasa_id = _item_nasa_id(item)
                if not nasa_id or nasa_id in seen_ids:
                    continue
                if self.is_valid_planet_image(item, planet_name):
                    all_valid_items.append(item)
                    seen_ids.add(nasa_id)
            time.sleep(0.5)
            return True

        # Page 1 of every query first so surface/globe are not starved by "planet" PR noise.
        for query in queries:
            collect_page(query, 1)

        # Deeper pages until the candidate pool is large enough.
        for query in queries:
            if len(all_valid_items) >= pool_target:
                break
            for page in range(2, max_pages_per_query + 1):
                if len(all_valid_items) >= pool_target:
                    break
                if not collect_page(query, page):
                    break

        if not all_valid_items:
            print(f"   No new valid images found for '{planet_name}'")
            return False

        print(f"   Found {len(all_valid_items)} new valid candidates")
        random.shuffle(all_valid_items)
        items_to_download = all_valid_items[:max_images]
        count = 0

        for item in items_to_download:
            try:
                nasa_id_raw = _item_nasa_id(item)
                if nasa_id_raw and nasa_id_raw in existing:
                    continue
                image_url = resolve_library_image_url(item, sess=self.sess)
                if not image_url:
                    continue
                meta = library_item_to_meta(
                    item,
                    image_url=image_url,
                    search_term=planet_name,
                    body=planet_name,
                )
                if meta.nasa_id and meta.nasa_id in existing:
                    continue
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                nasa_id = safe_filename(meta.nasa_id or "unknown", max_len=30)
                filename = f"{planet_name}_{nasa_id}_{timestamp}.jpg"
                filepath = planet_dir / filename
                download_file(image_url, filepath, sess=self.sess)
                write_sidecar(filepath, meta)
                if meta.nasa_id:
                    existing.add(meta.nasa_id)
                print(f"   ✓ {filepath.name}")
                count += 1
                if count >= max_images:
                    break
                time.sleep(0.5)
            except Exception as e:
                print(f"   Error processing image: {e}")
                continue

        print(f"   Successfully downloaded {count}/{max_images} new images for {planet_name}")
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
