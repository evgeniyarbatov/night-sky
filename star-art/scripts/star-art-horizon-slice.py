import json
import os
import time
from datetime import datetime
from typing import Any

import matplotlib.pyplot as plt
import pytz
from skyfield.api import load, wgs84
from star_art_utils import StarArtUtils

IMAGES_DIR = os.environ.get("STAR_ART_IMAGES_DIR", "images")

os.makedirs(IMAGES_DIR, exist_ok=True)


def create_artwork(
    location: dict[str, Any],
    magnitude: float,
    fov: float,
    azimuth: float,
    alt_min: float,
    alt_max: float,
) -> None:
    start_time = time.time()

    planets = load("de421.bsp")
    earth = planets["earth"]

    lat = float(location["lat"])
    lon = float(location["lon"])
    name = location.get("name", f"{lat},{lon}")

    observer = earth + wgs84.latlon(lat, lon)

    today = datetime.now(pytz.UTC).date()
    obs_time = StarArtUtils.get_astronomical_dusk(lat, lon, today)

    print(
        f"\nGenerating 'horizon-slice' for {name} at astronomical dusk (UTC): "
        f"{obs_time.strftime('%Y-%m-%d %H:%M UTC')}"
    )

    stars = StarArtUtils.get_horizon_band_stars(
        observer, obs_time, magnitude, alt_min, alt_max, azimuth, fov
    )
    if stars is None or stars.get("count", 0) == 0:
        print("No stars visible in this band, skipping...")
        return

    print(f"Stars in band: {stars['count']}")

    fig, bg_color = StarArtUtils.horizon_slice_style(stars, alt_min, alt_max, fov)
    if fig is None:
        print("Failed to generate artwork, skipping...")
        return

    details = f"Mag ≤{magnitude}  |  FOV {fov}°  |  Az {azimuth}°  |  Alt {alt_min}-{alt_max}°"
    StarArtUtils.add_info_text(fig, location, obs_time, details, bg_color)

    date_stamp = obs_time.strftime("%Y%m%d")
    safe_name = name.replace(" ", "_").replace(",", "_")
    out_dir = f"{IMAGES_DIR}/horizon-slice"
    os.makedirs(out_dir, exist_ok=True)
    filename = (
        f"{out_dir}/{safe_name}_horizon_mag{magnitude}_fov{fov}_az{azimuth}_"
        f"alt{alt_min}-{alt_max}_{date_stamp}.png"
    )

    try:
        fig.tight_layout(pad=0.5)
        plt.savefig(filename, dpi=300, facecolor=bg_color, edgecolor="none", bbox_inches="tight")
        duration = time.time() - start_time
        print(f"✓ Saved: {filename} ({duration:.2f}s)")
    except Exception as e:
        print(f"Error saving figure: {e}")
    finally:
        plt.close(fig)


def main(locations_file: str = "stargazing-locations.json") -> None:
    try:
        with open(locations_file) as f:
            locations = json.load(f)
    except Exception as e:
        print(f"Could not load locations file '{locations_file}': {e}")
        return

    print(f"\nGenerating horizon-slice artworks for {len(locations)} locations...")

    magnitudes = [3.5]
    fovs = [180]
    azimuths = [0]
    alt_min, alt_max = 12, 20

    total = len(locations) * len(magnitudes) * len(fovs) * len(azimuths)
    current = 0

    for location in locations:
        for magnitude in magnitudes:
            for fov in fovs:
                for azimuth in azimuths:
                    current += 1
                    print(f"\n[{current}/{total}]", end=" ")
                    try:
                        create_artwork(location, magnitude, fov, azimuth, alt_min, alt_max)
                    except Exception as e:
                        print(f"Error: {e}")

    print(f"\n✓ All artworks (attempted) saved to {IMAGES_DIR}/")


if __name__ == "__main__":
    main()
