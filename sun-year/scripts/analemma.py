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

# Use de421.bsp by default - it's smaller (17MB) and downloads faster than de440s (32MB)
# Both are accurate enough for analemma visualization
EPHEMERIS = os.environ.get("SKYFIELD_EPHEMERIS", "de421.bsp")

# Alternative download sources (mirrors)
EPHEMERIS_MIRRORS = {
    "de421.bsp": [
        "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de421.bsp",
        "https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de421.bsp",
    ],
    "de440s.bsp": [
        "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp",
        "https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp",
    ],
}


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

    # Check for common ephemeris files (prefer smaller, faster ones)
    for fname in ["de421.bsp", "de440s.bsp", "de440.bsp"]:
        fpath = cache_dir / fname
        if fpath.exists() and verify_ephemeris_file(str(fpath)):
            return str(fpath)

    return None


def download_ephemeris_with_progress(url: str, dest_path: Path):
    """Download ephemeris file with progress bar."""
    import urllib.request

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if HAS_TQDM:
        class DownloadProgressBar(tqdm):
            def update_to(self, b=1, bsize=1, tsize=None):
                if tsize is not None:
                    self.total = tsize
                self.update(b * bsize - self.n)

        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=dest_path.name) as t:
            urllib.request.urlretrieve(url, dest_path, reporthook=t.update_to)
    else:
        print_progress(f"Downloading {dest_path.name}...")
        urllib.request.urlretrieve(url, dest_path)
        print(" ✓", file=sys.stderr)


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

    # Load ephemeris with fallback strategy
    print_progress(f"Loading ephemeris: {ephemeris}...")
    eph = None

    try:
        # First try: use Skyfield's default loader (may download)
        eph = load(ephemeris)
        print_progress("✓ Ephemeris loaded")

    except Exception as e:
        print(f" ✗\nError loading ephemeris: {e}", file=sys.stderr)

        # Second try: check cache for alternatives
        print_progress("Checking cache for alternative ephemeris files...")
        cached = check_ephemeris_cache()
        if cached:
            print_progress(f"Found cached ephemeris: {cached}")
            try:
                eph = load(cached)
                print_progress("✓ Using cached ephemeris")
            except Exception as e2:
                print_progress(f"✗ Cached file also failed: {e2}")

        # Third try: manual download with progress
        if eph is None and ephemeris in EPHEMERIS_MIRRORS:
            cache_dir = Path.home() / ".skyfield"
            dest_path = cache_dir / ephemeris

            print_progress(f"Attempting manual download of {ephemeris}...")
            print_progress(f"Size: ~{'17MB' if 'de421' in ephemeris else '32MB'}")

            for i, mirror_url in enumerate(EPHEMERIS_MIRRORS[ephemeris], 1):
                try:
                    print_progress(f"Trying mirror {i}/{len(EPHEMERIS_MIRRORS[ephemeris])}...")
                    download_ephemeris_with_progress(mirror_url, dest_path)
                    eph = load(str(dest_path))
                    print_progress("✓ Download successful")
                    break
                except Exception as e3:
                    print_progress(f"✗ Mirror {i} failed: {e3}")
                    if i < len(EPHEMERIS_MIRRORS[ephemeris]):
                        continue
                    else:
                        raise RuntimeError(f"All download attempts failed") from e3

        if eph is None:
            raise RuntimeError("Could not load any ephemeris file")

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
            print_progress("Will attempt to download a fresh copy...")

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
        print("2. Use smaller/faster de421.bsp instead of de440s.bsp", file=sys.stderr)
        print("3. Or manually download from NASA:", file=sys.stderr)
        print("   de421.bsp (17MB): https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de421.bsp", file=sys.stderr)
        print("4. Place in ~/.skyfield/ directory", file=sys.stderr)
        print("5. Try alternative mirror: https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()