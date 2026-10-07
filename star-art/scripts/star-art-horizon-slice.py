import json
import os
import time
from datetime import timedelta
from typing import Any

import matplotlib.pyplot as plt
from skyfield.api import load, wgs84
from star_art_utils import StarArtUtils

IMAGES_DIR = os.environ.get("STAR_ART_IMAGES_DIR", "images")
LOCATIONS_FILE = "stargazing-locations.json"

FRAME_MINUTES = 10
# City sky, suburban, rural, dark-site naked-eye limit, binoculars, small telescope.
MAGNITUDES = [2.0, 3.5, 5.0, 6.5, 9.0, 12.0]
FOV = 180
AZIMUTH = 0
ALT_MIN, ALT_MAX = 12, 20

os.makedirs(IMAGES_DIR, exist_ok=True)


def filter_by_magnitude(stars: dict[str, Any] | None, magnitude: float) -> dict[str, Any] | None:
    if stars is None:
        return None
    mask = stars["mag"] <= magnitude
    return {
        "x": stars["x"][mask],
        "y": stars["y"][mask],
        "mag": stars["mag"][mask],
        "count": int(mask.sum()),
    }


def generate_timelapse(location: dict[str, Any]) -> None:
    start_time = time.time()

    earth = load("de421.bsp")["earth"]

    lat = float(location["lat"])
    lon = float(location["lon"])
    name = location.get("name", f"{lat},{lon}")
    observer = earth + wgs84.latlon(lat, lon)

    dusk, sunrise = StarArtUtils.get_night_window(lat, lon)
    total_minutes = max(0, int((sunrise - dusk).total_seconds() / 60))
    total_frames = total_minutes // FRAME_MINUTES + 1

    safe_name = name.replace(" ", "_").replace(",", "_")
    out_dirs = {
        magnitude: f"{IMAGES_DIR}/horizon-slice/{safe_name}/mag{magnitude}" for magnitude in MAGNITUDES
    }
    for out_dir in out_dirs.values():
        os.makedirs(out_dir, exist_ok=True)

    print(
        f"\nGenerating horizon-slice timelapse for {name}: {total_frames} frames x "
        f"{len(MAGNITUDES)} magnitudes, starting at astronomical dusk "
        f"{dusk.strftime('%Y-%m-%d %H:%M %Z')}"
    )

    for idx in range(total_frames):
        obs_time = dusk + timedelta(minutes=FRAME_MINUTES * idx)
        all_stars = StarArtUtils.get_horizon_band_stars(
            observer, obs_time, max(MAGNITUDES), ALT_MIN, ALT_MAX, AZIMUTH, FOV
        )

        for magnitude in MAGNITUDES:
            stars = filter_by_magnitude(all_stars, magnitude)
            fig, bg_color = StarArtUtils.horizon_slice_style(stars, ALT_MIN, ALT_MAX, FOV)

            details = f"Mag ≤{magnitude}  |  FOV {FOV}°  |  Az {AZIMUTH}°  |  Alt {ALT_MIN}-{ALT_MAX}°"
            StarArtUtils.add_info_text(fig, location, obs_time, details, bg_color)

            filename = f"{out_dirs[magnitude]}/frame_{idx + 1:04d}.png"
            fig.tight_layout(pad=0.5)
            plt.savefig(filename, dpi=300, facecolor=bg_color, edgecolor="none", bbox_inches="tight")
            plt.close(fig)

        print(f"✓ Frame {idx + 1}/{total_frames} ({obs_time.strftime('%H:%M %Z')})")

    duration = time.time() - start_time
    print(f"\n✓ Horizon-slice frames saved to {IMAGES_DIR}/horizon-slice/{safe_name} ({duration:.2f}s)")


def main(locations_file: str = LOCATIONS_FILE) -> None:
    with open(locations_file) as f:
        locations = json.load(f)

    for location in locations:
        generate_timelapse(location)


if __name__ == "__main__":
    main()
