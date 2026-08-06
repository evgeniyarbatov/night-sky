"""Monthly-average solar altitude by hour of day."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pvlib

from location import load_location
from style import (
    month_colors,
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
    end = start + pd.DateOffset(months=12)
    times = pd.date_range(start=start, end=end, freq="30min", tz=tz)

    solpos = pvlib.solarposition.get_solarposition(
        times, loc["latitude"], loc["longitude"]
    )
    data = pd.DataFrame(
        {
            "month": times.month,
            "hour": times.hour + times.minute / 60,
            "altitude": solpos["apparent_elevation"],
        }
    )
    data = data[data["altitude"] > 0]
    months = sorted(data["month"].unique())
    monthly_avg = data.groupby(["month", "hour"]).mean().reset_index()

    fig, ax = new_figure()
    style_axes(ax)

    colors = month_colors(len(months))
    for i, month in enumerate(months):
        subset = monthly_avg[monthly_avg["month"] == month]
        plot_line(
            ax,
            subset["hour"],
            subset["altitude"],
            color=colors[i],
            label=pd.Timestamp(2000, int(month), 1).strftime("%b"),
        )

    ax.set_xlabel("Hour")
    ax.set_ylabel("Altitude (°)")
    place_legend(ax, side="top", ncol=6)

    out = OUTPUT_DIR / "sun-path.png"
    save_figure(fig, out)
    print(f"Saved plot to {out}")

    peak_by_month = monthly_avg.loc[monthly_avg.groupby("month")["altitude"].idxmax()]
    print("\nPeak solar altitude by month (monthly mean of half-hour samples):")
    for _, row in peak_by_month.iterrows():
        label = pd.Timestamp(2000, int(row["month"]), 1).strftime("%b")
        hour = int(row["hour"])
        minute = int(round((row["hour"] - hour) * 60))
        print(f"  {label}: {row['altitude']:.1f}° around {hour:02d}:{minute:02d}")
    print(
        f"  Range: {peak_by_month['altitude'].max() - peak_by_month['altitude'].min():.1f}° "
        f"({peak_by_month['altitude'].min():.1f}°–{peak_by_month['altitude'].max():.1f}°)"
    )


if __name__ == "__main__":
    main()
