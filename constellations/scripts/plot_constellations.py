import json
import os
from datetime import datetime, timedelta
from io import BytesIO
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
from matplotlib.figure import Figure
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
DATE = (
    datetime.fromisoformat(os.environ["CONSTELLATIONS_DATE"]).date()
    if os.environ.get("CONSTELLATIONS_DATE")
    else datetime.now().date()
)
DELTA_MINUTES = config["delta_minutes"]
# Single-sample grazes plot as a point; skip windows shorter than this.
MIN_VISIBILITY_MINUTES = 30
# Fixed canvas so every PNG is identical pixels (video-friendly).
FIGSIZE = (7.2, 5.4)
DPI = 200
OUT_SIZE = (int(FIGSIZE[0] * DPI), int(FIGSIZE[1] * DPI))
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


def new_figure() -> Figure:
    return plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor="white")


def save_fixed_canvas(fig: Figure, path: str) -> None:
    """Tight-crop the figure, then center it on a fixed white canvas."""
    buf = BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=DPI,
        bbox_inches="tight",
        pad_inches=0.1,
        facecolor="white",
        edgecolor="none",
    )
    plt.close(fig)
    buf.seek(0)
    content = Image.open(buf).convert("RGB")

    out_w, out_h = OUT_SIZE
    canvas = Image.new("RGB", (out_w, out_h), (255, 255, 255))
    iw, ih = content.size
    # Leave a thin margin so content never clips the frame edge.
    max_w = int(out_w * 0.98)
    max_h = int(out_h * 0.98)
    scale = min(max_w / iw, max_h / ih)
    nw = max(1, int(round(iw * scale)))
    nh = max(1, int(round(ih * scale)))
    if (nw, nh) != (iw, ih):
        content = content.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (out_w - nw) // 2
    y = (out_h - nh) // 2
    canvas.paste(content, (x, y))
    canvas.save(path)


def plot_chart(gif_path: str, title: str) -> Figure:
    fig = new_figure()
    ax = fig.add_subplot(1, 1, 1)
    img = Image.open(gif_path)
    ax.imshow(img)
    ax.axis("off")
    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_azimuth(
    plot_times: list[datetime],
    plot_azimuths: list[float],
    x0: datetime,
    x1: datetime,
    title: str,
) -> Figure:
    fig = new_figure()
    ax = fig.add_subplot(1, 1, 1)
    az_series = unwrap_degrees(plot_azimuths)
    ax.plot(plot_times, az_series, color="darkorange", lw=2)  # type: ignore[arg-type]
    ax.set_xlim(x0, x1)  # type: ignore[arg-type]
    az_min = min(az_series)
    az_max = max(az_series)
    pad = max(5.0, 0.05 * (az_max - az_min + 1e-9))
    y0 = az_min - pad
    y1 = az_max + pad
    ax.set_ylim(y0, y1)
    tick_start = int(np.floor(y0 / 45.0)) * 45
    tick_stop = int(np.ceil(y1 / 45.0)) * 45
    az_ticks = np.arange(tick_start, tick_stop + 1, 45)
    cardinals = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}
    ax.set_yticks(az_ticks)
    az_labels: list[str] = []
    for t in az_ticks:
        deg = int(round(t % 360)) % 360
        card = cardinals.get(deg)
        az_labels.append(f"{deg}° ({card})" if card else f"{deg}°")
    ax.set_yticklabels(az_labels)
    ax.set_ylabel("Azimuth ° (Direction)")
    ax.set_xlabel(f"Time ({TZ_LABEL})")
    apply_time_axis(ax, x0, x1)
    ax.grid(True, alpha=0.3)
    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_altitude(
    plot_times: list[datetime],
    plot_altitudes: list[float],
    x0: datetime,
    x1: datetime,
    title: str,
) -> Figure:
    fig = new_figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(plot_times, plot_altitudes, color="steelblue", lw=2)  # type: ignore[arg-type]
    ax.set_xlim(x0, x1)  # type: ignore[arg-type]
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Altitude (°)")
    ax.set_xlabel(f"Time ({TZ_LABEL})")
    apply_time_axis(ax, x0, x1)
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="gray", linestyle="--", lw=1)
    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout()
    return fig


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
written = 0
for const_abbr, data in constellation_data.items():
    full_name = const_names.get(const_abbr, const_abbr)

    gif_path = os.path.join(GIF_FOLDER, f"{const_abbr.upper()}.gif")
    plot_times = data["times"]
    plot_altitudes = data["altitudes"]
    plot_azimuths = data["azimuths"]
    x0, x1 = pad_time_window(plot_times[0], plot_times[-1])
    start_str = data["start"].strftime("%H:%M")
    end_str = data["end"].strftime("%H:%M")
    visible = f"visible {start_str}-{end_str}"
    safe_name = full_name.replace(" ", "_").replace("/", "_")
    out_base = os.path.join(OUTPUT_FOLDER, safe_name)

    if os.path.exists(gif_path):
        save_fixed_canvas(
            plot_chart(gif_path, f"{full_name} · {visible}"),
            f"{out_base}.png",
        )
        written += 1

    save_fixed_canvas(
        plot_azimuth(
            plot_times, plot_azimuths, x0, x1, f"{full_name} · azimuth · {visible}"
        ),
        f"{out_base}-az.png",
    )
    save_fixed_canvas(
        plot_altitude(
            plot_times, plot_altitudes, x0, x1, f"{full_name} · altitude · {visible}"
        ),
        f"{out_base}-alt.png",
    )
    written += 2
    print(f"✓ {full_name}")

print(
    f"\nGenerated {written} plots for {len(constellation_data)} constellations"
    f" (skipped {skipped_below_horizon} below horizon,"
    f" {skipped_too_brief} too brief)."
)
