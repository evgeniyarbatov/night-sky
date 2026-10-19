import argparse
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray
from skyfield.api import Star, load
from star_art_utils import StarArtUtils

IMAGES_DIR = os.environ.get("STAR_ART_IMAGES_DIR", "images")

MAGNITUDE_LIMIT = 6.0
# Fixed so ink tones match across runs instead of depending on each strip's brightest star.
BRIGHTEST_MAG = -1.5
HALF_WIDTH_DEG = 4.0
PAPER = "#fdfdf9"
INK = "#1a1a1a"

GPX_NS = {"g": "http://www.topografix.com/GPX/1/1"}


def read_run(gpx_path: str) -> tuple[datetime, datetime, int, int]:
    points = ET.parse(gpx_path).getroot().findall(".//g:trkpt", GPX_NS)  # noqa: S314 — own exports
    times = [p.findtext("g:time", namespaces=GPX_NS) for p in points]
    stamps = [datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times if t]
    if not stamps:
        raise ValueError(f"{gpx_path}: no timestamped track points")
    return (
        min(stamps),
        max(stamps),
        round(float(points[0].attrib["lat"])),
        round(float(points[0].attrib["lon"])),
    )


def select_band(
    ra_hours: NDArray[np.float64],
    dec_deg: NDArray[np.float64],
    mags: NDArray[np.float64],
    lst_hours: NDArray[np.float64],
    lat: float,
) -> dict[str, Any]:
    """Stars that crossed the meridian within HALF_WIDTH_DEG of the zenith, keyed by minute."""
    lst = np.unwrap(lst_hours, period=24)
    ra = lst[0] + (ra_hours - lst[0]) % 24
    offset = dec_deg - lat
    keep = (ra <= lst[-1]) & (np.abs(offset) <= HALF_WIDTH_DEG) & (mags < MAGNITUDE_LIMIT)
    minutes = np.interp(ra[keep], lst, np.arange(len(lst), dtype=float))
    return {"minute": minutes, "offset": offset[keep], "mag": mags[keep], "count": int(keep.sum())}


def overhead_stars(start: datetime, end: datetime, lat: int, lon: int) -> dict[str, Any]:
    ts = load.timescale()
    minutes = int((end - start).total_seconds() // 60)
    t = ts.from_datetimes([start + timedelta(minutes=m) for m in range(minutes + 1)])
    lst_hours = (np.asarray(t.gast) + lon / 15) % 24

    df = StarArtUtils._load_hipparcos(source="remote")
    df = df[df["magnitude"] < MAGNITUDE_LIMIT]
    mid = ts.from_datetime(start + (end - start) / 2)
    ra, dec, _ = (
        load("de421.bsp")["earth"].at(mid).observe(Star.from_dataframe(df)).radec(epoch=mid)
    )
    return select_band(
        np.asarray(ra.hours),
        np.asarray(dec.degrees),
        np.asarray(df["magnitude"].values),
        lst_hours,
        lat,
    )


def run_strip_style(stars: dict[str, Any], run_minutes: int) -> Figure:
    fig, ax = plt.subplots(figsize=(3, 12), facecolor=PAPER, dpi=300)
    ax.set_facecolor(PAPER)

    sizes = 40 * np.exp(-stars["mag"] / 2.2)
    alphas = np.clip(0.9 - (stars["mag"] - BRIGHTEST_MAG) / 12, 0.3, 0.9)
    ax.scatter(stars["offset"], stars["minute"], s=sizes, c=INK, alpha=alphas, linewidths=0)

    ax.set_xlim(-HALF_WIDTH_DEG, HALF_WIDTH_DEG)
    ax.set_ylim(run_minutes, 0)
    ax.axis("off")
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description="Stars that passed overhead during one run.")
    parser.add_argument("gpx")
    args = parser.parse_args()

    start, end, lat, lon = read_run(args.gpx)
    run_minutes = int((end - start).total_seconds() // 60)
    stars = overhead_stars(start, end, lat, lon)

    tz = StarArtUtils.get_timezone(lat, lon)
    local_date = (start.astimezone(tz) if tz else start).strftime("%Y-%m-%d")

    fig = run_strip_style(stars, run_minutes)
    fig.text(
        0.5,
        -0.02,
        f"{local_date}  ·  {run_minutes} min",
        ha="center",
        fontsize=9,
        family="monospace",
        color=INK,
    )

    out_dir = f"{IMAGES_DIR}/run-strip"
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{out_dir}/{local_date}.png"
    fig.tight_layout(pad=0.5)
    plt.savefig(filename, dpi=300, facecolor=PAPER, edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {stars['count']} stars over {run_minutes} min → {filename}")


if __name__ == "__main__":
    main()
