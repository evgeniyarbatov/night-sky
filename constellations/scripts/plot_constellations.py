import json
import os
from datetime import datetime, timedelta
from typing import TypedDict

import astropy.units as u
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
from astroplan import Observer
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time
from matplotlib.axes import Axes
from matplotlib.ticker import NullLocator
from PIL import Image
from ra_utils import circular_mean_deg, ra_hms_to_deg, unwrap_degrees

# ===== User settings =====
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"
)
with open(CONFIG_PATH) as f:
    config = json.load(f)

LAT = config["lat"]
LON = config["lon"]
ELEV = config["elev_m"]
DATA_DIR = os.environ.get("DATA_DIR", "data")
DATA_FOLDER = "data/boundaries"
OUTPUT_FOLDER = os.path.join(DATA_DIR, "plots")
GIF_FOLDER = os.path.join(DATA_DIR, "gifs")
DATE = datetime.now().date()
DELTA_MINUTES = config["delta_minutes"]
# Single-sample grazes plot as a point; skip windows shorter than this.
MIN_VISIBILITY_MINUTES = 30
# Fixed canvas so every PNG is identical pixels (video-friendly).
FIGSIZE = (16.0, 4.0)
DPI = 300
HANOI_TZ = pytz.timezone(config["timezone"])
TZ_LABEL = config["tz_label"]
NAMES_FILE = "data/constellation_names.csv"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


class ConstellationVisibility(TypedDict):
    start: datetime
    end: datetime
    times: list[datetime]
    altitudes: list[float]
    azimuths: list[float]


def pad_time_window(
    t0: datetime, t1: datetime, min_span_minutes: float = 30.0
) -> tuple[datetime, datetime]:
    """Widen a zero/near-zero span so matplotlib date axes stay non-singular.

    Identical xlims make the date transform expand to multi-year limits, and
    MinuteLocator then tries tens of thousands of ticks.
    """
    span_s = (t1 - t0).total_seconds()
    min_s = min_span_minutes * 60.0
    if span_s >= min_s:
        return t0, t1
    pad = timedelta(seconds=(min_s - span_s) / 2.0)
    return t0 - pad, t1 + pad


def apply_time_axis(ax: Axes, t0: datetime, t1: datetime) -> None:
    """Sparse hour/minute ticks sized to the visibility window."""
    # matplotlib.dates locators/formatters lack upstream type annotations
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=HANOI_TZ))  # type: ignore[no-untyped-call]
    duration_h = max((t1 - t0).total_seconds() / 3600.0, 0.1)
    if duration_h <= 2:
        locator: mdates.DateLocator = mdates.MinuteLocator(byminute=[0, 30], tz=HANOI_TZ)  # type: ignore[no-untyped-call]
    elif duration_h <= 6:
        locator = mdates.HourLocator(interval=1, tz=HANOI_TZ)  # type: ignore[no-untyped-call]
    else:
        locator = mdates.HourLocator(interval=2, tz=HANOI_TZ)  # type: ignore[no-untyped-call]
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_minor_locator(NullLocator())


# ===== Load constellation names =====
try:
    names_df = pd.read_csv(NAMES_FILE)
    const_names = dict(zip(names_df["abbreviation"], names_df["name"], strict=False))
except Exception as e:
    print(f"Error: Could not load {NAMES_FILE} — {e}")
    exit(1)

# ===== Observer setup =====
observer_location = EarthLocation(lat=LAT * u.deg, lon=LON * u.deg, height=ELEV * u.m)
observer = Observer(location=observer_location)

# ===== Compute sunset/sunrise =====
midnight = HANOI_TZ.localize(datetime.combine(DATE, datetime.min.time()))
midnight_astropy = Time(midnight)

# Astronomical dusk (sun 18° below horizon in the evening)
astronomical_dusk = observer.twilight_evening_astronomical(midnight_astropy, which="nearest")
# Astronomical dawn (sun 18° below horizon in the morning)
astronomical_dawn = observer.twilight_morning_astronomical(midnight_astropy, which="next")

# Convert to local timezone
astronomical_dusk_local = astronomical_dusk.to_datetime(timezone=HANOI_TZ)
astronomical_dawn_local = astronomical_dawn.to_datetime(timezone=HANOI_TZ)

print(f"Astronomical dusk: {astronomical_dusk_local.strftime('%H:%M')}")
print(f"Astronomical dawn: {astronomical_dawn_local.strftime('%H:%M')}")

# ===== Time grid for visibility calculation =====
times = [
    astronomical_dusk_local + timedelta(minutes=i)
    for i in range(
        0,
        int((astronomical_dawn_local - astronomical_dusk_local).total_seconds() / 60),
        DELTA_MINUTES,
    )
]
times_astropy = Time([t.astimezone(pytz.UTC) for t in times])

constellation_data: dict[str, ConstellationVisibility] = {}
skipped_below_horizon = 0
skipped_too_brief = 0

# ===== Process constellation files =====
for file_name in os.listdir(DATA_FOLDER):
    if not file_name.endswith(".txt"):
        continue

    file_path = os.path.join(DATA_FOLDER, file_name)
    df = pd.read_csv(
        file_path,
        sep="|",
        names=["RA_hms", "Dec_deg", "Constellation"],
        engine="python",
    )
    df["Dec_deg"] = df["Dec_deg"].astype(float)

    # Convert RA hms to degrees
    ra_deg = [ra_hms_to_deg(ra_hms) for ra_hms in df["RA_hms"]]
    df["RA_deg"] = ra_deg

    for const_abbr_raw, group in df.groupby("Constellation"):
        const_abbr = str(const_abbr_raw).strip()
        full_name = const_names.get(const_abbr, const_abbr)
        stars = SkyCoord(
            ra=group["RA_deg"].values * u.degree,
            dec=group["Dec_deg"].values * u.degree,
            frame="icrs",
        )

        altitude_samples = []
        azimuth_samples = []

        for t in times_astropy:
            altaz_frame = AltAz(obstime=t, location=observer_location)
            star_altaz = stars.transform_to(altaz_frame)
            altitude_samples.append(float(np.mean(star_altaz.alt.deg)))
            # Arithmetic mean of degrees is wrong when points straddle north
            azimuth_samples.append(circular_mean_deg(star_altaz.az.deg))

        altitudes = np.array(altitude_samples)
        azimuths = np.array(azimuth_samples)
        visible = altitudes > 0

        if not np.any(visible):
            skipped_below_horizon += 1
            print(f"– {full_name} (below horizon)")
            continue

        # Plot only while the constellation is above the horizon
        vis_idx = np.flatnonzero(visible)
        visible_times = [times[i] for i in vis_idx]
        start_time = visible_times[0].astimezone(HANOI_TZ)
        end_time = visible_times[-1].astimezone(HANOI_TZ)
        duration_min = (end_time - start_time).total_seconds() / 60.0
        if duration_min < MIN_VISIBILITY_MINUTES:
            skipped_too_brief += 1
            print(f"– {full_name} (too brief, {duration_min:.0f} min)")
            continue

        constellation_data[const_abbr] = {
            "start": start_time,
            "end": end_time,
            "times": visible_times,
            "altitudes": altitudes[vis_idx].tolist(),
            "azimuths": azimuths[vis_idx].tolist(),
        }

# ===== Create plots =====
for const_abbr, data in constellation_data.items():
    full_name = const_names.get(const_abbr, const_abbr)

    gif_path = os.path.join(GIF_FOLDER, f"{const_abbr}.gif")
    has_gif = os.path.exists(gif_path)

    plot_times = data["times"]
    plot_altitudes = data["altitudes"]
    plot_azimuths = data["azimuths"]
    x0, x1 = pad_time_window(plot_times[0], plot_times[-1])

    # Always the same canvas + 3-col grid (GIF slot empty if missing).
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.2, 1, 1], wspace=0.35)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.86, bottom=0.18)

    ax_gif = fig.add_subplot(gs[0])
    if has_gif:
        img = Image.open(gif_path)
        ax_gif.imshow(img)
    ax_gif.axis("off")

    # ===== Azimuth over time =====
    ax_az = fig.add_subplot(gs[1])
    # Unwrap so north crossings stay continuous (e.g. 5° → 0° → -7° not 353°)
    az_series = unwrap_degrees(plot_azimuths)
    ax_az.plot(plot_times, az_series, color="darkorange", lw=2)  # type: ignore[arg-type]
    ax_az.set_xlim(x0, x1)  # type: ignore[arg-type]
    az_min = min(az_series)
    az_max = max(az_series)
    pad = max(5.0, 0.05 * (az_max - az_min + 1e-9))
    y0 = az_min - pad
    y1 = az_max + pad
    ax_az.set_ylim(y0, y1)
    tick_start = int(np.floor(y0 / 45.0)) * 45
    tick_stop = int(np.ceil(y1 / 45.0)) * 45
    az_ticks = np.arange(tick_start, tick_stop + 1, 45)
    cardinals = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}
    ax_az.set_yticks(az_ticks)
    az_labels: list[str] = []
    for t in az_ticks:
        deg = int(round(t % 360)) % 360
        card = cardinals.get(deg)
        az_labels.append(f"{deg}° ({card})" if card else f"{deg}°")
    ax_az.set_yticklabels(az_labels)
    ax_az.set_ylabel("Azimuth ° (Direction)")
    ax_az.set_xlabel(f"Time ({TZ_LABEL})")
    apply_time_axis(ax_az, x0, x1)
    ax_az.grid(True, alpha=0.3)

    # ===== Altitude over time =====
    ax_alt = fig.add_subplot(gs[2])
    ax_alt.plot(plot_times, plot_altitudes, color="steelblue", lw=2)  # type: ignore[arg-type]
    ax_alt.set_xlim(x0, x1)  # type: ignore[arg-type]
    ax_alt.set_ylim(bottom=0)
    ax_alt.set_ylabel("Altitude (°)")
    ax_alt.set_xlabel(f"Time ({TZ_LABEL})")
    apply_time_axis(ax_alt, x0, x1)
    ax_alt.grid(True, alpha=0.3)
    ax_alt.axhline(0, color="gray", linestyle="--", lw=1)

    # ===== Title & Save =====
    start_str = data["start"].strftime("%H:%M")
    end_str = data["end"].strftime("%H:%M")
    title_text = f"{full_name} - visible {start_str}-{end_str}"

    fig.suptitle(title_text, fontsize=13, fontweight="bold")

    safe_name = full_name.replace(" ", "_").replace("/", "_")
    # No bbox_inches="tight" — that crops per-content and makes frame sizes jump.
    fig.savefig(os.path.join(OUTPUT_FOLDER, f"{safe_name}.png"), dpi=DPI)
    plt.close()
    print(f"✓ {full_name}")

print(
    f"\nGenerated {len(constellation_data)} plots"
    f" (skipped {skipped_below_horizon} below horizon,"
    f" {skipped_too_brief} too brief)."
)
