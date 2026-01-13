#!/usr/bin/env python3
# analemma.py
#
# Skyfield version (only). Plots the Sun's azimuth vs altitude at fixed LOCAL CLOCK times
# across a year (analemma curves).
#
# Install:
#   pip install skyfield numpy matplotlib tqdm
#
# Notes:
# - Skyfield will download the ephemeris file on first run unless already cached.
#   If you're offline, pre-download de440s.bsp and point EPHEMERIS_PATH to it.

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import load, wgs84

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Note: Install 'tqdm' for progress bars: pip install tqdm", file=sys.stderr)


# --- User-provided location/timezone (Hanoi) ---
LATITUDE = 20.994839969936898
LONGITUDE = 105.86779701825405
TZ_NAME = "Asia/Bangkok"

# --- Parameters ---
YEAR = 2026
CLOCK_TIMES = ["09:00", "12:00", "15:00"]   # fixed local clock times
STEP_DAYS = 1                               # daily sampling
EPHEMERIS = os.environ.get("SKYFIELD_EPHEMERIS", "de440s.bsp")  # modern, smaller ephemeris


def print_progress(message: str, end: str = "\n"):
    """Simple progress printer."""
    print(f"→ {message}", file=sys.stderr, end=end, flush=True)


def verify_ephemeris_file(ephemeris_path: str) -> bool:
    """Check if ephemeris file exists and has reasonable size."""
    if not os.path.exists(ephemeris_path):
        return False

    size = os.path.getsize(ephemeris_path)
    # de440s.bsp should be ~32MB, de421.bsp ~17MB
    if size < 1_000_000:  # Less than 1MB is definitely corrupted
        print_progress(f"Warning: {ephemeris_path} is only {size:,} bytes (likely corrupted)")
        return False

    return True


def check_ephemeris_cache() -> str | None:
    """Find Skyfield's cache directory and check for ephemeris files."""
    cache_dir = Path.home() / ".skyfield"
    if not cache_dir.exists():
        return None

    # Check for common ephemeris files
    for fname in ["de440s.bsp", "de421.bsp", "de440.bsp"]:
        fpath = cache_dir / fname
        if fpath.exists() and verify_ephemeris_file(str(fpath)):
            return str(fpath)

    return None


def _build_dates(year: int, step_days: int) -> list[date]:
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    n = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(0, n, step_days)]


def _skyfield_times_for_local_clock(dates: list[date], hh: int, mm: int, tz: ZoneInfo, ts):
    """Convert local clock times to Skyfield Time array."""
    # local datetimes -> UTC datetimes
    dts_local = [datetime(d.year, d.month, d.day, hh, mm, 0, tzinfo=tz) for d in dates]
    dts_utc = [dt.astimezone(ZoneInfo("UTC")) for dt in dts_local]

    # Build a Skyfield Time array
    t = ts.utc(
        [dt.year for dt in dts_utc],
        [dt.month for dt in dts_utc],
        [dt.day for dt in dts_utc],
        [dt.hour for dt in dts_utc],
        [dt.minute for dt in dts_utc],
        [dt.second + dt.microsecond * 1e-6 for dt in dts_utc],
    )
    return t


def analemma_series_skyfield(
    year: int = YEAR,
    clock_times: list[str] = CLOCK_TIMES,
    step_days: int = STEP_DAYS,
    lat_deg: float = LATITUDE,
    lon_deg: float = LONGITUDE,
    tz_name: str = TZ_NAME,
    ephemeris: str = EPHEMERIS,
):
    """
    Returns dict: { "HH:MM": {"date": np.array[date], "az_deg": np.array[float], "alt_deg": np.array[float]} }
    """
    print_progress(f"Computing analemma for {year}")
    print_progress(f"Location: {lat_deg:.4f}°N, {lon_deg:.4f}°E")
    print_progress(f"Timezone: {tz_name}")
    print_progress(f"Clock times: {', '.join(clock_times)}")
    print_progress(f"Sampling: every {step_days} day(s)")

    tz = ZoneInfo(tz_name)
    dates = _build_dates(year, step_days)
    print_progress(f"Computing {len(dates)} positions per time...")

    # Load ephemeris
    print_progress(f"Loading ephemeris: {ephemeris}...", end="")
    try:
        eph = load(ephemeris)
        print(" ✓", file=sys.stderr)
    except Exception as e:
        print(f" ✗\nError loading ephemeris: {e}", file=sys.stderr)

        # Check cache for alternatives
        cached = check_ephemeris_cache()
        if cached:
            print_progress(f"Found cached ephemeris: {cached}")
            print_progress("Trying cached file...", end="")
            eph = load(cached)
            print(" ✓", file=sys.stderr)
        else:
            raise

    ts = load.timescale()
    earth = eph["earth"]
    sun = eph["sun"]

    observer = wgs84.latlon(lat_deg, lon_deg)

    out = {}
    iterator = tqdm(clock_times, desc="Computing curves", unit="time") if HAS_TQDM else clock_times

    for ct in iterator:
        if not HAS_TQDM:
            print_progress(f"Computing curve for {ct}...", end="")

        hh, mm = map(int, ct.split(":"))
        t = _skyfield_times_for_local_clock(dates, hh, mm, tz, ts)

        astrometric = (earth + observer).at(t).observe(sun).apparent()
        alt, az, _ = astrometric.altaz()

        out[ct] = {
            "date": np.array(dates, dtype=object),
            "az_deg": az.degrees,    # 0..360 (from North, eastward)
            "alt_deg": alt.degrees,
        }

        if not HAS_TQDM:
            print(" ✓", file=sys.stderr)

    print_progress(f"Computation complete! ({len(out)} curves)")
    return out


def _unwrap_azimuth_compact(az_deg: np.ndarray) -> np.ndarray:
    """
    Make azimuth a smooth x-coordinate for plotting by unwrapping around its circular mean,
    then centering. This avoids a big jump at 0/360.
    """
    rad = np.deg2rad(az_deg)
    mean_angle = np.angle(np.mean(np.exp(1j * rad)))
    centered = np.angle(np.exp(1j * (rad - mean_angle)))   # (-pi, pi]
    unwrapped = np.unwrap(centered)
    x = np.rad2deg(unwrapped)
    return x - np.median(x)


def plot_analemma(data: dict, title: str):
    """Plot analemma curves with minimal, zen styling."""
    print_progress("Generating plot...")

    # Minimal, "zen" styling: no ticks, no spines, airy margins.
    fig = plt.figure(figsize=(7.2, 7.2), dpi=170)
    ax = fig.add_axes([0.08, 0.08, 0.84, 0.84])

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    # Color palette for multiple curves
    colors = plt.cm.tab10(np.linspace(0, 1, len(data)))

    # Draw curves (thin strokes)
    for (ct, d), color in zip(data.items(), colors):
        x = _unwrap_azimuth_compact(d["az_deg"])
        y = d["alt_deg"]
        ax.plot(x, y, linewidth=1.2, alpha=0.9, color=color, label=ct)

        # small, quiet label near last point
        ax.text(x[-1], y[-1], f" {ct}", fontsize=9, va="center", ha="left", color=color)

    ax.text(0.02, 0.98, title, transform=ax.transAxes, va="top", ha="left", fontsize=9)
    ax.margins(0.18)

    print_progress("Displaying plot...")
    plt.show()


def main():
    print_progress("=== Analemma Generator ===")

    # Check ephemeris situation
    if EPHEMERIS.endswith('.bsp') and os.path.exists(EPHEMERIS):
        if not verify_ephemeris_file(EPHEMERIS):
            print_progress(f"Warning: Ephemeris file may be corrupted: {EPHEMERIS}")
            print_progress("Skyfield will attempt to download a fresh copy...")

    try:
        data = analemma_series_skyfield(
            year=YEAR,
            clock_times=CLOCK_TIMES,
            step_days=STEP_DAYS,
            lat_deg=LATITUDE,
            lon_deg=LONGITUDE,
            tz_name=TZ_NAME,
            ephemeris=EPHEMERIS,
        )

        title = (
            "Sun analemma • azimuth vs altitude\n"
            f"Hanoi • {LATITUDE:.4f}°, {LONGITUDE:.4f}° • {TZ_NAME} • {YEAR}"
        )
        plot_analemma(data, title)

        print_progress("Done! ✓")

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        print("\nTroubleshooting:", file=sys.stderr)
        print("1. Delete corrupted ephemeris: rm ~/.skyfield/*.bsp", file=sys.stderr)
        print("2. Or manually download: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp", file=sys.stderr)
        print("3. Place in ~/.skyfield/ directory", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()