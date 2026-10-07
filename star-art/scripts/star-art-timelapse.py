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
MAGNITUDE = 12.4
FOV = 180
AZIMUTH = 0
ALTITUDE = 90

os.makedirs(IMAGES_DIR, exist_ok=True)


def generate_timelapse(location: dict[str, Any]) -> None:
    start_time = time.time()

    planets = load("de421.bsp")
    earth = planets["earth"]

    lat = float(location["lat"])
    lon = float(location["lon"])
    name = location.get("name", f"{lat},{lon}")

    observer = earth + wgs84.latlon(lat, lon)

    dusk, sunrise = StarArtUtils.get_night_window(lat, lon)

    total_minutes = max(0, int((sunrise - dusk).total_seconds() / 60))
    total_frames = total_minutes // FRAME_MINUTES + 1
    safe_name = name.replace(" ", "_").replace(",", "_")
    out_dir = f"{IMAGES_DIR}/timelapse/{safe_name}"
    os.makedirs(out_dir, exist_ok=True)

    print(
        f"\nGenerating timelapse for {name} starting at astronomical dusk (UTC): {dusk.strftime('%Y-%m-%d %H:%M UTC')}"
    )

    for idx in range(total_frames):
        obs_time = dusk + timedelta(minutes=FRAME_MINUTES * idx)
        stars = StarArtUtils.get_visible_stars(
            observer, obs_time, MAGNITUDE, ALTITUDE, AZIMUTH, FOV
        )

        if stars is None or stars.get("count", 0) == 0:
            print(f"Frame {idx + 1}/{total_frames}: no stars visible, skipping...")
            continue

        fig, bg_color = StarArtUtils.sumi_star_style(stars, FOV)
        if fig is None:
            print(f"Frame {idx + 1}/{total_frames}: failed to render, skipping...")
            continue

        details = f"Mag ≤{MAGNITUDE}  |  FOV {FOV}°  |  Az {AZIMUTH}°  Alt {ALTITUDE}°"
        StarArtUtils.add_info_text(fig, location, obs_time, details, bg_color)

        filename = f"{out_dir}/frame_{idx + 1:04d}.png"
        fig.tight_layout(pad=0.5)
        plt.savefig(filename, dpi=300, facecolor=bg_color, edgecolor="none", bbox_inches="tight")
        plt.close(fig)
        print(f"✓ Saved frame {idx + 1}/{total_frames}: {filename}")

    duration = time.time() - start_time
    print(f"\n✓ Timelapse frames saved to {out_dir} ({duration:.2f}s)")


def main(locations_file: str = LOCATIONS_FILE) -> None:
    with open(locations_file) as f:
        locations = json.load(f)

    for location in locations:
        generate_timelapse(location)


if __name__ == "__main__":
    main()
