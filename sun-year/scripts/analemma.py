#!/usr/bin/env python3
# analemma.py
#
# Skyfield version (only). Plots the Sun’s azimuth vs altitude at fixed LOCAL CLOCK times
# across a year (analemma curves).
#
# Install:
#   pip install skyfield numpy matplotlib
#
# Notes:
# - Skyfield will download the ephemeris file on first run unless already cached.
#   If you’re offline, pre-download de421.bsp (or another .bsp) and point EPHEMERIS_PATH to it.

from __future__ import annotations

import os
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import load, wgs84


# --- User-provided location/timezone (Hanoi) ---
LATITUDE = 20.994839969936898
LONGITUDE = 105.86779701825405
TZ_NAME = "Asia/Bangkok"

# --- Parameters ---
YEAR = 2026
CLOCK_TIMES = ["09:00", "12:00", "15:00"]   # fixed local clock times
STEP_DAYS = 1                               # daily sampling
EPHEMERIS = os.environ.get("SKYFIELD_EPHEMERIS", "de421.bsp")  # or path to local .bsp


def _build_dates(year: int, step_days: int) -> list[date]:
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    n = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(0, n, step_days)]


def _skyfield_times_for_local_clock(dates: list[date], hh: int, mm: int, tz: ZoneInfo, ts):
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
    tz = ZoneInfo(tz_name)
    dates = _build_dates(year, step_days)

    eph = load(ephemeris)          # downloads if given a name and not cached
    ts = load.timescale()
    earth = eph["earth"]
    sun = eph["sun"]

    observer = wgs84.latlon(lat_deg, lon_deg)

    out = {}
    for ct in clock_times:
        hh, mm = map(int, ct.split(":"))
        t = _skyfield_times_for_local_clock(dates, hh, mm, tz, ts)

        astrometric = (earth + observer).at(t).observe(sun).apparent()
        alt, az, _ = astrometric.altaz()

        out[ct] = {
            "date": np.array(dates, dtype=object),
            "az_deg": az.degrees,    # 0..360 (from North, eastward)
            "alt_deg": alt.degrees,
        }

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
    # Minimal, “zen” styling: no ticks, no spines, airy margins.
    fig = plt.figure(figsize=(7.2, 7.2), dpi=170)
    ax = fig.add_axes([0.08, 0.08, 0.84, 0.84])

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    # Draw curves (thin strokes)
    for ct, d in data.items():
        x = _unwrap_azimuth_compact(d["az_deg"])
        y = d["alt_deg"]
        ax.plot(x, y, linewidth=1.0, alpha=0.9)

        # small, quiet label near last point
        ax.text(x[-1], y[-1], f" {ct}", fontsize=9, va="center", ha="left")

    ax.text(0.02, 0.98, title, transform=ax.transAxes, va="top", ha="left", fontsize=9)
    ax.margins(0.18)
    plt.show()


def main():
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


if __name__ == "__main__":
    main()
