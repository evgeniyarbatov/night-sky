"""Golden-hour / low-sun duration (0°–6° altitude) morning and evening."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

import ephem
import numpy as np

from location import load_location, today_local
from style import (
    COLORS,
    month_axis,
    new_figure,
    plot_line,
    save_figure,
    style_axes,
)

OUTPUT_DIR = Path(os.environ.get("DATA_DIR", "data"))


def _crossing(observer: ephem.Observer, start: datetime, horizon_deg: float, rising: bool):
    observer.date = start
    observer.horizon = str(horizon_deg)
    sun = ephem.Sun()
    try:
        t = observer.next_rising(sun) if rising else observer.next_setting(sun)
        return ephem.Date(t).datetime()
    except (ephem.AlwaysUpError, ephem.NeverUpError):
        return None


def golden_minutes(observer: ephem.Observer, day: datetime) -> tuple[float | None, float | None]:
    base = day.replace(hour=0, minute=0, second=0, microsecond=0)
    r0 = _crossing(observer, base, 0.0, rising=True)
    r6 = _crossing(observer, base, 6.0, rising=True)
    s6 = _crossing(observer, base, 6.0, rising=False)
    s0 = _crossing(observer, base, 0.0, rising=False)
    morning = (r6 - r0).total_seconds() / 60 if r0 and r6 and r6 > r0 else None
    evening = (s0 - s6).total_seconds() / 60 if s0 and s6 and s0 > s6 else None
    return morning, evening


def main() -> None:
    loc = load_location()
    lat = loc["latitude"]
    lon = loc["longitude"]

    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.elevation = 0
    observer.pressure = 0

    start = today_local(loc)
    dates: list[datetime] = []
    morning: list[float] = []
    evening: list[float] = []

    for i in range(365):
        day = start + timedelta(days=i)
        m, e = golden_minutes(observer, day)
        if m is None or e is None:
            continue
        dates.append(day)
        morning.append(m)
        evening.append(e)

    m_arr = np.array(morning)
    e_arr = np.array(evening)

    # Shared y-scale so morning vs evening are comparable
    y_min = float(min(m_arr.min(), e_arr.min())) - 0.5
    y_max = float(max(m_arr.max(), e_arr.max())) + 0.5

    fig, (ax1, ax2) = new_figure(nrows=2, ncols=1, sharex=True)
    style_axes(ax1)
    style_axes(ax2)

    plot_line(ax1, dates, m_arr, color=COLORS["sunrise"])
    ax1.set_ylabel("Morning (min)")
    ax1.set_ylim(y_min, y_max)

    plot_line(ax2, dates, e_arr, color=COLORS["sunset"])
    ax2.set_ylabel("Evening (min)")
    ax2.set_ylim(y_min, y_max)
    month_axis(ax2)

    out = OUTPUT_DIR / "twilight.png"
    save_figure(fig, out)
    print(f"Saved plot to {out}")

    print("\nGolden-hour duration (minutes):")
    print(f"  Morning: {m_arr.min():.0f}–{m_arr.max():.0f} min (mean {m_arr.mean():.0f})")
    print(f"  Evening: {e_arr.min():.0f}–{e_arr.max():.0f} min (mean {e_arr.mean():.0f})")


if __name__ == "__main__":
    main()
