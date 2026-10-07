"""Sunrise and sunset azimuth over a year."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

import ephem
import numpy as np

from location import format_site, load_location, today_local
from style import (
    COLORS,
    chart_title,
    mark_extrema,
    month_axis,
    new_figure,
    plot_line,
    ref_hline,
    ref_vline,
    save_figure,
    style_axes,
)

OUTPUT_DIR = Path(os.environ.get("DATA_DIR", "data"))


def get_sun_azimuth_at_rise_set(
    observer: ephem.Observer, date: datetime
) -> tuple[float, float] | tuple[None, None]:
    observer.date = date
    sun = ephem.Sun()
    try:
        sunrise_time = observer.next_rising(sun)
        observer.date = sunrise_time
        sun.compute(observer)
        sunrise_az = float(np.degrees(sun.az))

        observer.date = date
        sunset_time = observer.next_setting(sun)
        observer.date = sunset_time
        sun.compute(observer)
        sunset_az = float(np.degrees(sun.az))
        return sunrise_az, sunset_az
    except (ephem.AlwaysUpError, ephem.NeverUpError):
        return None, None


def _crossings(values: list[float], dates: list[datetime], target: float) -> list[datetime]:
    out: list[datetime] = []
    for i in range(len(dates) - 1):
        a, b = values[i], values[i + 1]
        if (a < target <= b) or (a > target >= b):
            if b == a:
                continue
            fraction = (target - a) / (b - a)
            out.append(dates[i] + (dates[i + 1] - dates[i]) * fraction)
    return out


def main() -> None:
    loc = load_location()
    lat = loc["latitude"]
    lon = loc["longitude"]

    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.elevation = 0
    observer.horizon = "0"

    start_date = today_local(loc)
    dates: list[datetime] = []
    sunrise_azimuths: list[float] = []
    sunset_azimuths: list[float] = []

    print(
        f"Calculating rise/set azimuth for 1 year from {start_date.strftime('%Y-%m-%d')} "
        f"({format_site(loc)}, {loc['timezone']})..."
    )
    for day_offset in range(365):
        dt = start_date + timedelta(days=day_offset)
        sr_az, ss_az = get_sun_azimuth_at_rise_set(observer, dt)
        if sr_az is not None and ss_az is not None:
            dates.append(dt)
            sunrise_azimuths.append(sr_az)
            sunset_azimuths.append(ss_az)
        if (day_offset + 1) % 30 == 0:
            print(f"  Processed {day_offset + 1}/365 days...")

    east_dates = _crossings(sunrise_azimuths, dates, 90.0)
    west_dates = _crossings(sunset_azimuths, dates, 270.0)

    sunrise_min_idx = int(np.argmin(sunrise_azimuths))
    sunrise_max_idx = int(np.argmax(sunrise_azimuths))
    sunset_min_idx = int(np.argmin(sunset_azimuths))
    sunset_max_idx = int(np.argmax(sunset_azimuths))

    fig, (ax1, ax2) = new_figure(nrows=2, ncols=1, sharex=True)
    style_axes(ax1)
    style_axes(ax2)

    plot_line(ax1, dates, sunrise_azimuths, color=COLORS["sunrise"])
    ref_hline(ax1, 90.0, "due E")
    for ed in east_dates:
        ref_vline(ax1, ed)
    mark_extrema(
        ax1,
        dates[sunrise_min_idx],
        sunrise_azimuths[sunrise_min_idx],
        f"{sunrise_azimuths[sunrise_min_idx]:.0f}°",
    )
    mark_extrema(
        ax1,
        dates[sunrise_max_idx],
        sunrise_azimuths[sunrise_max_idx],
        f"{sunrise_azimuths[sunrise_max_idx]:.0f}°",
    )
    chart_title(ax1, "Sunrise azimuth")
    ax1.set_ylabel("Azimuth")
    ax1.set_ylim(60, 120)
    ax1.set_yticks([60, 90, 120])
    ax1.set_yticklabels(["60° NE", "90° E", "120° SE"])

    plot_line(ax2, dates, sunset_azimuths, color=COLORS["sunset"])
    ref_hline(ax2, 270.0, "due W")
    for wd in west_dates:
        ref_vline(ax2, wd)
    mark_extrema(
        ax2,
        dates[sunset_max_idx],
        sunset_azimuths[sunset_max_idx],
        f"{sunset_azimuths[sunset_max_idx]:.0f}°",
    )
    mark_extrema(
        ax2,
        dates[sunset_min_idx],
        sunset_azimuths[sunset_min_idx],
        f"{sunset_azimuths[sunset_min_idx]:.0f}°",
    )
    chart_title(ax2, "Sunset azimuth")
    ax2.set_ylabel("Azimuth")
    ax2.set_ylim(240, 300)
    ax2.set_yticks([240, 270, 300])
    ax2.set_yticklabels(["240° SW", "270° W", "300° NW"])
    month_axis(ax2)

    out_path = OUTPUT_DIR / "sun-azimuth.png"
    save_figure(fig, out_path)
    print(f"Saved plot to {out_path}")

    print(f"\nAnnual summary — {format_site(loc)} · {loc['timezone']}")
    print("  Sunrise azimuth:")
    print(f"    Most northern: {min(sunrise_azimuths):.2f}°")
    print(f"    Most southern: {max(sunrise_azimuths):.2f}°")
    print(f"    Variation: {max(sunrise_azimuths) - min(sunrise_azimuths):.2f}°")
    print("  Sunset azimuth:")
    print(f"    Most northern: {max(sunset_azimuths):.2f}°")
    print(f"    Most southern: {min(sunset_azimuths):.2f}°")
    print(f"    Variation: {max(sunset_azimuths) - min(sunset_azimuths):.2f}°")
    print(f"  Period: {start_date.strftime('%Y-%m-%d')} → {dates[-1].strftime('%Y-%m-%d')}")


if __name__ == "__main__":
    main()
