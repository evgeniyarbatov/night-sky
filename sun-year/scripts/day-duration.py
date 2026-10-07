"""Daylight duration over a year (daily curve + monthly means)."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pvlib

from location import load_location
from style import (
    COLORS,
    MARKER_SIZE,
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


def main() -> None:
    loc = load_location()
    tz = loc["timezone"]

    start = pd.Timestamp.now(tz=tz).normalize()
    times = pd.date_range(start=start, periods=365, freq="D", tz=tz)
    srs = pvlib.solarposition.sun_rise_set_transit_ephem(
        times, loc["latitude"], loc["longitude"]
    )
    day_length = (srs["sunset"] - srs["sunrise"]).dt.total_seconds() / 3600

    df = pd.DataFrame({"date": times, "month": times.month, "day_length": day_length})
    monthly_avg = df.groupby("month")["day_length"].mean().reset_index()

    fig, ax = new_figure()
    style_axes(ax)

    plot_line(ax, df["date"], df["day_length"], color=COLORS["day"], label="Daily")
    month_dates = [times[times.month == m][0] for m in monthly_avg["month"]]
    ax.scatter(
        month_dates,
        monthly_avg["day_length"],
        s=MARKER_SIZE + 8,
        color=COLORS["noon"],
        zorder=5,
        edgecolors="none",
        label="Monthly mean",
    )

    i_min = int(df["day_length"].values.argmin())
    i_max = int(df["day_length"].values.argmax())
    min_h = float(df["day_length"].iloc[i_min])
    max_h = float(df["day_length"].iloc[i_max])
    mark_extrema(ax, df["date"].iloc[i_min], min_h, f"{min_h:.1f} h")
    mark_extrema(ax, df["date"].iloc[i_max], max_h, f"{max_h:.1f} h")

    chart_title(ax, "Day length")
    ax.set_ylabel("Hours")
    month_axis(ax)
    place_legend(ax, side="right")

    out = OUTPUT_DIR / "day-duration.png"
    save_figure(fig, out)
    print(f"Saved plot to {out}")

    shortest = df.iloc[i_min]
    longest = df.iloc[i_max]
    print("\nDaylight summary (daily rise–set):")
    print(
        f"  Shortest: {shortest['day_length']:.2f} h on "
        f"{shortest['date'].strftime('%Y-%m-%d')}"
    )
    print(
        f"  Longest:  {longest['day_length']:.2f} h on "
        f"{longest['date'].strftime('%Y-%m-%d')}"
    )
    print(f"  Range:    {longest['day_length'] - shortest['day_length']:.2f} h")
    print(
        f"  Monthly means: {monthly_avg['day_length'].min():.2f}–"
        f"{monthly_avg['day_length'].max():.2f} h"
    )


if __name__ == "__main__":
    main()
