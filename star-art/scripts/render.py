"""Render one sky in one style for a given place and date, reproducibly.

render --seed INT --params PARAMS.json --out DIR --inputs SKY.json [--size preview|full]
render --list-styles

SKY.json: {"name": str, "lat": float, "lon": float, "date": "YYYY-MM-DD"}
"""

import argparse
import importlib.util
import json
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from types import ModuleType
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent
PREVIEW_LONG_SIDE_PX = 1024
FULL_DPI = 300
CACHE_DIR = Path(os.environ.get("STAR_ART_CACHE", Path.home() / ".cache" / "star-art"))
HIPPARCOS_FILE = "hip_main.dat"

STYLES = {
    "sumi": "Every catalog star brighter than the magnitude limit, magnitude as size and ink",
    "sumi-stars": "Named bright stars with labels",
    "wabi-sabi-stars": "Named stars joined by one wandering shortest path",
    "sumi-planets": "Planets overhead with labels",
    "sumi-galaxies": "Galaxies overhead with labels",
    "sumi-nebulae": "Nebulae overhead with labels",
    "sumi-star-clusters": "Star clusters overhead with labels",
    "sumi-exotic-objects": "Black holes, pulsars and quasars overhead with labels",
}


def _load(filename: str, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS_DIR / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _star_names_csv() -> Path:
    for candidate in (SCRIPTS_DIR / "data", SCRIPTS_DIR.parent / "data"):
        if (candidate / "star_names.csv").exists():
            return candidate / "star_names.csv"
    raise FileNotFoundError("data/star_names.csv not found")


def list_styles() -> list[dict[str, str]]:
    return [{"name": n, "input": "sky", "description": d} for n, d in STYLES.items()]


def render(seed: int, params: dict[str, Any], sky_file: Path, out_dir: Path, size: str) -> Path:
    style = params["style"]
    if style not in STYLES:
        raise ValueError(f"unknown style {style!r}")
    sky = json.loads(sky_file.read_text())
    random.seed(seed)
    np.random.seed(seed)

    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    names_csv = _star_names_csv()
    # The scripts create IMAGES_DIR on import and resolve skyfield files against the cwd.
    os.environ["STAR_ART_IMAGES_DIR"] = str(out_dir)
    os.chdir(CACHE_DIR)
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))

    from skyfield.api import load, wgs84
    from star_art_utils import StarArtUtils

    magnitude = float(params.get("magnitude", 12.4))
    fov = float(params.get("fov", 180))
    azimuth = float(params.get("azimuth", 0))
    altitude = float(params.get("altitude", 90))

    planets = load("de421.bsp")
    lat, lon = float(sky["lat"]), float(sky["lon"])
    observer = planets["earth"] + wgs84.latlon(lat, lon)
    obs_time = StarArtUtils.get_astronomical_dusk(lat, lon, date.fromisoformat(sky["date"]))
    obs_time += timedelta(minutes=float(params.get("minutes_after_dusk", 0)))

    if style == "sumi":
        objects = StarArtUtils.get_visible_stars(
            observer, obs_time, magnitude, altitude, azimuth, fov
        )
        fig, bg = StarArtUtils.sumi_star_style(objects, fov)
    elif style in ("sumi-stars", "wabi-sabi-stars"):
        StarArtUtils._load_hipparcos(source="remote")
        named = StarArtUtils.load_named_stars(str(names_csv))
        objects = StarArtUtils.get_named_stars(
            observer, obs_time, named, altitude, azimuth, fov, HIPPARCOS_FILE
        )
        if style == "sumi-stars":
            fig, bg = StarArtUtils.sumi_object_style(objects)
        else:
            if objects is not None:
                keep = objects["mag"] <= magnitude
                objects = {k: v[keep] for k, v in objects.items() if k != "count"}
                objects["count"] = int(np.sum(keep))
            path_mod = _load("star-art-path.py", "star_art_path")
            fig, bg = path_mod.wabi_sabi_minimal_style(objects)
    elif style == "sumi-planets":
        planets_mod = _load("star-art-planets.py", "star_art_planets")
        objects = planets_mod.get_bodies(observer, planets, obs_time, altitude, azimuth, fov)
        fig, bg = StarArtUtils.sumi_object_style(objects)
    else:
        kind = style.removeprefix("sumi-")
        catalog_mod = _load(f"star-art-{kind}.py", f"star_art_{kind.replace('-', '_')}")
        catalog = getattr(catalog_mod, kind.replace("-", "_").upper())
        objects = StarArtUtils.get_objects_by_ra_dec(
            observer, obs_time, catalog, altitude, azimuth, fov
        )
        fig, bg = StarArtUtils.sumi_object_style(objects)

    if fig is None:
        raise LookupError(f"nothing visible for {style} with these params")

    if params.get("footer", False):
        details = f"Mag ≤{magnitude}  |  FOV {fov}°  |  Az {azimuth}°  Alt {altitude}°"
        StarArtUtils.add_info_text(fig, sky, obs_time, details, bg)

    dpi = FULL_DPI if size == "full" else PREVIEW_LONG_SIDE_PX / max(fig.get_size_inches())
    fig.tight_layout(pad=0.5)
    out = out_dir / "render.png"
    fig.savefig(
        out,
        dpi=dpi,
        facecolor=bg,
        edgecolor="none",
        bbox_inches="tight",
        metadata={"Software": None},
    )
    plt.close("all")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(prog="render")
    parser.add_argument("--list-styles", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--params", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--inputs", type=Path, nargs="+")
    parser.add_argument("--size", choices=["preview", "full"], default="preview")
    args = parser.parse_args()

    if args.list_styles:
        print(json.dumps(list_styles()))
        return
    if args.seed is None or args.params is None or args.out is None or not args.inputs:
        parser.error("--seed, --params, --out and --inputs are required")
    params = json.loads(args.params.read_text())
    try:
        out = render(args.seed, params, args.inputs[0].resolve(), args.out, args.size)
    except LookupError as e:
        print(e, file=sys.stderr)
        sys.exit(3)
    print(out)


if __name__ == "__main__":
    main()
