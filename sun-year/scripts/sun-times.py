"""Clock times of sunrise, sunset, and solar noon over a year."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pvlib
from matplotlib.ticker import FuncFormatter

from location import load_location
from style import (
    COLORS,
    chart_title,
    mark_extrema,
    month_axis,
    new_figure,
    place_legend,
    plot_line,
    save_figure,
    style_axes,
)

OUTPUT_DIR = Path(os.environ.get("DATA_DIR", "data"))


def _fmt_hour(h: float, _pos: float | None = None) -> str:
    hour = int(h)
    minute = int(round((h - hour) * 60))
    if minute == 60:
        hour += 1
        minute = 0
    return f"{hour:02d}:{minute:02d}"


def main() -> None:
    loc = load_location()
    tz = loc["timezone"]

    start = pd.Timestamp.now(tz=tz).normalize()
    days = pd.date_range(start=start, periods=365, freq="D", tz=tz)
    srs = pvlib.solarposition.sun_rise_set_transit_ephem(
        days, loc["latitude"], loc["longitude"]
    )

    def to_hours(series: pd.Series) -> pd.Series:
        local = series.dt.tz_convert(tz)
        return local.dt.hour + local.dt.minute / 60 + local.dt.second / 3600

    sunrise_h = to_hours(srs["sunrise"])
    sunset_h = to_hours(srs["sunset"])
    noon_h = to_hours(srs["transit"])
    day_length = sunset_h - sunrise_h

    fig, ax = new_figure()
    style_axes(ax)

    plot_line(ax, days, sunrise_h, color=COLORS["sunrise"], label="Sunrise")
    plot_line(ax, days, sunset_h, color=COLORS["sunset"], label="Sunset")
    plot_line(ax, days, noon_h, color=COLORS["noon"], label="Noon")

    i_early_set = int(sunset_h.values.argmin())
    i_late_rise = int(sunrise_h.values.argmax())
    i_short = int(day_length.values.argmin())
    i_long = int(day_length.values.argmax())

    mark_extrema(ax, days[i_early_set], float(sunset_h.iloc[i_early_set]))
    mark_extrema(ax, days[i_late_rise], float(sunrise_h.iloc[i_late_rise]))
    mark_extrema(ax, days[i_short], float(sunset_h.iloc[i_short]))
    mark_extrema(ax, days[i_long], float(sunrise_h.iloc[i_long]))

    chart_title(ax, "Rise / set / solar noon")
    ax.set_ylabel("Local time")
    month_axis(ax)
    ax.set_ylim(max(0.0, float(sunrise_h.min()) - 0.4), min(24.0, float(sunset_h.max()) + 0.4))
    ax.yaxis.set_major_formatter(FuncFormatter(_fmt_hour))
    place_legend(ax, side="right")

    out = OUTPUT_DIR / "sun-times.png"
    save_figure(fig, out)
    print(f"Saved plot to {out}")

    print("\nClock-time extrema:")
    print(
        f"  Earliest sunset: {days[i_early_set].strftime('%Y-%m-%d')} "
        f"{_fmt_hour(float(sunset_h.iloc[i_early_set]))}"
    )
    print(
        f"  Latest sunrise:  {days[i_late_rise].strftime('%Y-%m-%d')} "
        f"{_fmt_hour(float(sunrise_h.iloc[i_late_rise]))}"
    )
    print(
        f"  Shortest day:    {days[i_short].strftime('%Y-%m-%d')} "
        f"({float(day_length.iloc[i_short]):.2f} h)"
    )
    print(
        f"  Longest day:     {days[i_long].strftime('%Y-%m-%d')} "
        f"({float(day_length.iloc[i_long]):.2f} h)"
    )
    print(
        f"  Solar noon range: {_fmt_hour(float(noon_h.min()))}–"
        f"{_fmt_hour(float(noon_h.max()))}"
    )


if __name__ == "__main__":
    main()
