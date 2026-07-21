#!/usr/bin/env python3
"""Shared helpers for NASA downloads, sidecars, destinations, and captions."""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

NASA_IMAGES_API = "https://images-api.nasa.gov"
APOD_API = "https://api.nasa.gov/planetary/apod"
DEFAULT_LICENSE = "NASA media (check source; U.S. government works are typically public domain)"
USER_AGENT = "space-images/0.1 (+https://github.com/evgeniyarbatov/space-images)"

DESTINATIONS: dict[str, tuple[str, ...]] = {
    "moon": ("moon", "lunar", "apollo", "artemis", "selen"),
    "mars": ("mars", "martian", "perseverance", "curiosity", "ingenuity", "olympus mons"),
    "gas-giants": (
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "jovian",
        "rings of",
        "europa",
        "ganymede",
        "io ",
        "titan",
        "enceladus",
    ),
    "nebulae": (
        "nebula",
        "nebulae",
        "galaxy",
        "galaxies",
        "andromeda",
        "milky way",
        "cluster",
        "supernova",
        "quasar",
        "black hole",
    ),
    "earth-from-space": (
        "earth",
        "blue marble",
        "from iss",
        "international space station",
        "earthrise",
        "our planet",
    ),
    "sun": ("sun", "solar", "heliosphere", "coronal", "sdo"),
    "comets-asteroids": ("comet", "asteroid", "meteor", "osiris", "bennu", "ryugu"),
    "stars": ("star", "stellar", "proxima", "centauri", "betelgeuse", "sirius", "vega", "polaris"),
}


@dataclass
class ImageMeta:
    title: str
    date: str
    source_url: str
    image_url: str
    license: str = DEFAULT_LICENSE
    mission: str = ""
    body: str = ""
    destination: str = "other"
    nasa_id: str = ""
    credit: str = "NASA"
    keywords: list[str] = field(default_factory=list)
    explain_like_10: str = ""
    go_deeper: str = ""
    search_term: str = ""
    center: str = ""
    local_image: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def nasa_api_key() -> str:
    key = os.environ.get("NASA_API_KEY", "").strip()
    if key:
        return key
    return "DEMO_KEY"


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def safe_filename(text: str, max_len: int = 80) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', "", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().replace(" ", "_")
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned[:max_len] or "untitled"


def first_sentence(text: str) -> str:
    text = " ".join(text.split())
    if not text:
        return ""
    match = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)
    return match[0].strip()


def classify_destination(
    title: str = "",
    description: str = "",
    keywords: list[str] | None = None,
    body_hint: str = "",
) -> str:
    if body_hint:
        hint = body_hint.lower().strip()
        for dest, terms in DESTINATIONS.items():
            if hint in terms or any(hint == t.strip() for t in terms):
                return dest
        if hint in {"mercury", "venus"}:
            return "other"
        if hint in {"jupiter", "saturn", "uranus", "neptune"}:
            return "gas-giants"
        if hint == "mars":
            return "mars"
        if hint in {"earth", "moon"}:
            return hint if hint == "moon" else "earth-from-space"

    title_l = title.lower()
    blob = " ".join(
        [
            title_l,
            description.lower(),
            " ".join(keywords or []).lower(),
            body_hint.lower(),
        ]
    )
    scores: dict[str, int] = dict.fromkeys(DESTINATIONS, 0)
    for dest, terms in DESTINATIONS.items():
        for term in terms:
            if term not in blob:
                continue
            # Prefer distinctive / longer terms; title hits count more than body text.
            scores[dest] += 2 + len(term)
            if term in title_l:
                scores[dest] += 8
    best = max(scores, key=lambda d: scores[d])
    return best if scores[best] > 0 else "other"


def explain_like_10(title: str, destination: str, description: str, body: str = "") -> str:
    where = ""
    if body:
        where = f" It is about {body}."
    elif destination and destination != "other":
        label = destination.replace("-", " ")
        where = f" It belongs with our {label} pictures."
    lead = first_sentence(description)
    if len(lead) > 220:
        lead = lead[:217].rsplit(" ", 1)[0] + "…"
    if lead:
        return (
            f'Today\'s sky picture is called "{title}".{where} '
            f"{lead} Real spacecraft and telescopes took it so everyone can explore space."
        )
    return (
        f'Today\'s sky picture is called "{title}".{where} '
        "Real spacecraft and telescopes took it so everyone can explore space."
    )


def go_deeper_text(description: str, title: str) -> str:
    text = description.strip()
    if text:
        return text
    return f"No longer description was provided for “{title}”. Follow the source URL for mission pages and archives."


def write_sidecar(image_path: Path, meta: ImageMeta) -> tuple[Path, Path]:
    """Write image_path.with_suffix('.json') and '.md' next to the image."""
    meta.local_image = image_path.name
    if not meta.explain_like_10:
        meta.explain_like_10 = explain_like_10(
            meta.title, meta.destination, meta.go_deeper, meta.body
        )
    if not meta.go_deeper:
        meta.go_deeper = go_deeper_text("", meta.title)

    json_path = image_path.with_suffix(".json")
    md_path = image_path.with_suffix(".md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meta.to_dict(), f, indent=2, ensure_ascii=False)
        f.write("\n")

    kw = ", ".join(meta.keywords) if meta.keywords else "—"
    md = (
        f"# {meta.title}\n\n"
        f"| Field | Value |\n"
        f"| --- | --- |\n"
        f"| Date | {meta.date or '—'} |\n"
        f"| Mission | {meta.mission or '—'} |\n"
        f"| Body | {meta.body or '—'} |\n"
        f"| Destination | {meta.destination} |\n"
        f"| License | {meta.license} |\n"
        f"| Credit | {meta.credit} |\n"
        f"| NASA ID | {meta.nasa_id or '—'} |\n"
        f"| Source | {meta.source_url or '—'} |\n"
        f"| Image URL | {meta.image_url or '—'} |\n"
        f"| Keywords | {kw} |\n\n"
        f"## Explain like I'm 10\n\n"
        f"{meta.explain_like_10}\n\n"
        f"## Go deeper\n\n"
        f"{meta.go_deeper}\n"
    )
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    return json_path, md_path


def load_meta(path: Path) -> ImageMeta | None:
    """Load ImageMeta from a .json sidecar or from an image path."""
    json_path = path if path.suffix == ".json" else path.with_suffix(".json")
    if not json_path.is_file():
        return None
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    known = {f.name for f in fields(ImageMeta)}
    filtered = {k: v for k, v in data.items() if k in known}
    return ImageMeta(**filtered)


def download_file(
    url: str,
    filepath: Path,
    *,
    sess: requests.Session | None = None,
    retries: int = 3,
) -> None:
    """Download url to filepath. Raises on failure after retries."""
    s = sess or session()
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = s.get(url, stream=True, timeout=30)
            response.raise_for_status()
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(2)
    raise RuntimeError(f"Failed to download {url}: {last_error}")


def pick_image_asset(assets: list[str]) -> str | None:
    for asset in assets:
        if ("orig" in asset or "large" in asset) and asset.endswith((".jpg", ".jpeg", ".png")):
            return asset
    for asset in assets:
        if asset.endswith((".jpg", ".jpeg", ".png")):
            return asset
    return None


def fetch_apod(
    *,
    date: str | None = None,
    api_key: str | None = None,
    sess: requests.Session | None = None,
) -> dict[str, Any]:
    s = sess or session()
    key = api_key or nasa_api_key()
    params: dict[str, str] = {"api_key": key}
    if date:
        params["date"] = date
    response = s.get(APOD_API, params=params, timeout=20)
    response.raise_for_status()
    data: dict[str, Any] = response.json()
    return data


def apod_to_meta(data: dict[str, Any]) -> ImageMeta:
    title = str(data.get("title") or "Astronomy Picture of the Day")
    explanation = str(data.get("explanation") or "")
    image_url = str(data.get("hdurl") or data.get("url") or "")
    date = str(data.get("date") or "")
    copyright = data.get("copyright")
    credit = f"APOD / {copyright}" if copyright else "APOD / NASA"
    license_note = (
        f"Copyright may apply ({copyright}). See APOD page for terms."
        if copyright
        else DEFAULT_LICENSE
    )
    source_url = (
        f"https://apod.nasa.gov/apod/ap{date.replace('-', '')[2:]}.html"
        if date
        else ("https://apod.nasa.gov/apod/")
    )
    # APOD URL pattern uses YYMMDD — fix properly
    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            source_url = f"https://apod.nasa.gov/apod/ap{d.strftime('%y%m%d')}.html"
        except ValueError:
            source_url = "https://apod.nasa.gov/apod/"

    dest = classify_destination(title, explanation)
    meta = ImageMeta(
        title=title,
        date=date,
        source_url=source_url,
        image_url=image_url,
        license=license_note,
        mission="APOD",
        body="",
        destination=dest,
        nasa_id=f"apod-{date}" if date else "apod",
        credit=credit,
        keywords=["APOD", "astronomy"],
        go_deeper=go_deeper_text(explanation, title),
    )
    meta.explain_like_10 = explain_like_10(title, dest, explanation)
    return meta


def library_search(
    query: str,
    *,
    page: int = 1,
    sess: requests.Session | None = None,
) -> tuple[list[dict[str, Any]], int]:
    s = sess or session()
    url = f"{NASA_IMAGES_API}/search"
    response = s.get(
        url,
        params={"q": query, "media_type": "image", "page": str(page)},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    items = data.get("collection", {}).get("items", [])
    total = data.get("collection", {}).get("metadata", {}).get("total_hits", 0)
    return items, int(total or 0)


def library_item_to_meta(
    item: dict[str, Any],
    *,
    image_url: str,
    search_term: str = "",
    body: str = "",
) -> ImageMeta:
    data_block = item.get("data", [{}])[0]
    title = str(data_block.get("title") or "NASA image")
    description = str(data_block.get("description") or "")
    keywords = list(data_block.get("keywords") or [])
    nasa_id = str(data_block.get("nasa_id") or "")
    date = str(data_block.get("date_created") or "")[:10]
    center = str(data_block.get("center") or "")
    dest = classify_destination(title, description, keywords, body_hint=body or search_term)
    source_url = (
        f"https://images.nasa.gov/details/{quote(nasa_id)}"
        if nasa_id
        else "https://images.nasa.gov"
    )
    credit = f"NASA/{center}" if center else "NASA"
    meta = ImageMeta(
        title=title,
        date=date,
        source_url=source_url,
        image_url=image_url,
        license=DEFAULT_LICENSE,
        mission=center or "NASA Image Library",
        body=body or search_term,
        destination=dest,
        nasa_id=nasa_id,
        credit=credit,
        keywords=[str(k) for k in keywords],
        search_term=search_term,
        center=center,
        go_deeper=go_deeper_text(description, title),
    )
    meta.explain_like_10 = explain_like_10(title, dest, description, meta.body)
    return meta


def resolve_library_image_url(
    item: dict[str, Any], *, sess: requests.Session | None = None
) -> str | None:
    s = sess or session()
    href = item.get("href")
    if not href:
        return None
    response = s.get(href, timeout=20)
    response.raise_for_status()
    assets = response.json()
    if not isinstance(assets, list):
        return None
    return pick_image_asset([str(a) for a in assets])


def social_post_text(meta: ImageMeta) -> str:
    lines = [
        meta.title,
        "",
        meta.explain_like_10,
        "",
        f"Credit: {meta.credit}",
        f"Source: {meta.source_url}",
        "",
        "#space #astronomy #nasa",
    ]
    return "\n".join(lines)


def copy_with_sidecars(image_path: Path, dest_dir: Path) -> Path:
    """Copy image + .json/.md sidecars into dest_dir. Returns new image path."""
    import shutil

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_image = dest_dir / image_path.name
    shutil.copy2(image_path, dest_image)
    for suffix in (".json", ".md"):
        src = image_path.with_suffix(suffix)
        if src.is_file():
            shutil.copy2(src, dest_dir / src.name)
    return dest_image


def iter_sidecars(roots: list[Path]) -> list[Path]:
    found: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        found.extend(sorted(root.rglob("*.json")))
    return found


def destination_label(dest: str) -> str:
    return dest.replace("-", " ").title()
