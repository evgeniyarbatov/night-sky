"""Solar altitude at solar noon, plus noon shadow length ratio."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import pvlib

from location import load_location
from style import (
    COLORS,
    chart_title,
    mark_extrema,
    month_axis,
    new_figure,
    plot_line,
    ref_hline,
    save_figure,
    style_axes,
)

OUTPUT_DIR = Path(os.environ.get("DATA_DIR", "data"))


def main() -> None:
    loc = load_location()
    tz = loc["timezone"]
    lat = loc["latitude"]
    lon = loc["longitude"]

    start = pd.Timestamp.now(tz=tz).normalize()
    days = pd.date_range(start=start, periods=365, freq="D", tz=tz)
    srs = pvlib.solarposition.sun_rise_set_transit_ephem(days, lat, lon)
    solpos = pvlib.solarposition.get_solarposition(srs["transit"], lat, lon)
    altitude = solpos["apparent_elevation"].to_numpy(dtype=float)
    shadow = np.where(altitude > 0.5, 1.0 / np.tan(np.deg2rad(altitude)), np.nan)

    i_max = int(np.nanargmax(altitude))
    i_min = int(np.nanargmin(altitude))

    fig, (ax1, ax2) = new_figure(nrows=2, ncols=1, sharex=True)
    style_axes(ax1)
    style_axes(ax2)

    plot_line(ax1, days, altitude, color=COLORS["noon"])
    ref_hline(ax1, 90.0 - abs(lat), "overhead max at lat")
    mark_extrema(ax1, days[i_max], float(altitude[i_max]), f"{altitude[i_max]:.0f}°")
    mark_extrema(ax1, days[i_min], float(altitude[i_min]), f"{altitude[i_min]:.0f}°")
    chart_title(ax1, "Altitude at solar noon")
    ax1.set_ylabel("Altitude (°)")

    plot_line(ax2, days, shadow, color=COLORS["day"])
    chart_title(ax2, "Noon shadow length")
    ax2.set_ylabel("× object height")
    month_axis(ax2)

    out = OUTPUT_DIR / "noon-altitude.png"
    save_figure(fig, out)
    print(f"Saved plot to {out}")

    print("\nNoon altitude summary:")
    print(f"  Max: {altitude[i_max]:.2f}° on {days[i_max].strftime('%Y-%m-%d')}")
    print(f"  Min: {altitude[i_min]:.2f}° on {days[i_min].strftime('%Y-%m-%d')}")
    print(f"  Range: {altitude[i_max] - altitude[i_min]:.2f}°")
    print(
        f"  Noon shadow (unit height): "
        f"{float(np.nanmin(shadow)):.2f}–{float(np.nanmax(shadow)):.2f}×"
    )


if __name__ == "__main__":
    main()
