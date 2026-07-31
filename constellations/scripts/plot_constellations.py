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
from PIL import Image
from ra_utils import ra_hms_to_deg

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
HANOI_TZ = pytz.timezone(config["timezone"])
NAMES_FILE = "data/constellation_names.csv"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


class ConstellationVisibility(TypedDict):
    start: datetime | None
    end: datetime | None
    below_horizon: bool


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

# ===== Observation time for direction info =====
obs_time_local = HANOI_TZ.localize(
    datetime.combine(DATE, datetime.strptime("23:00", "%H:%M").time())
)
obs_time_utc = obs_time_local.astimezone(pytz.UTC)
obs_time_astropy = Time(obs_time_utc)

constellation_data: dict[str, ConstellationVisibility] = {}

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
            altitude_samples.append(star_altaz.alt.deg)
            azimuth_samples.append(star_altaz.az.deg)

        altitudes = np.array(altitude_samples)
        azimuths = np.array(azimuth_samples)

        # Determine if constellation is above horizon
        mean_altitudes = np.mean(altitudes, axis=1)
        visible = mean_altitudes > 0

        if not np.any(visible):
            # Entirely below horizon
            constellation_data[const_abbr] = {
                "start": None,
                "end": None,
                "below_horizon": True,
            }
            continue

        # Visible times in local timezone
        visible_times = np.array(times)[visible]
        start_time = visible_times[0].astimezone(HANOI_TZ)
        end_time = visible_times[-1].astimezone(HANOI_TZ)

        constellation_data[const_abbr] = {
            "start": start_time,
            "end": end_time,
            "below_horizon": False,
        }

# ===== Create plots =====
for const_abbr, data in constellation_data.items():
    full_name = const_names.get(const_abbr, const_abbr)

    gif_path = os.path.join(GIF_FOLDER, f"{const_abbr}.gif")
    has_gif = os.path.exists(gif_path)

    # Skip constellations that somehow failed earlier
    if const_abbr not in constellation_data:
        continue

    # Retrieve altitude and azimuth data again for plotting
    file_path = os.path.join(DATA_FOLDER, f"{const_abbr}.txt")
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

    stars = SkyCoord(
        ra=df["RA_deg"].values * u.degree,
        dec=df["Dec_deg"].values * u.degree,
        frame="icrs",
    )

    altitude_samples = []
    azimuth_samples = []
    for t in times_astropy:
        altaz_frame = AltAz(obstime=t, location=observer_location)
        star_altaz = stars.transform_to(altaz_frame)
        altitude_samples.append(np.mean(star_altaz.alt.deg))
        azimuth_samples.append(np.mean(star_altaz.az.deg))

    altitudes = np.array(altitude_samples)
    azimuths = np.array(azimuth_samples)

    # Create figure layout
    if has_gif:
        fig = plt.figure(figsize=(16, 4))
        gs = fig.add_gridspec(1, 3, width_ratios=[1.2, 1, 1], wspace=0.3)
        gif_col, az_col, alt_col = 0, 1, 2
    else:
        fig = plt.figure(figsize=(12, 4))
        gs = fig.add_gridspec(1, 2, width_ratios=[1, 1], wspace=0.3)
        az_col, alt_col = 0, 1

    # ===== GIF (if available) =====
    if has_gif:
        ax_gif = fig.add_subplot(gs[gif_col])
        img = Image.open(gif_path)
        ax_gif.imshow(img)
        ax_gif.axis("off")

    # ===== Azimuth over time =====
    ax_az = fig.add_subplot(gs[az_col])
    ax_az.plot(times, azimuths, color="darkorange", lw=2)
    ax_az.set_ylabel("Azimuth ° (Direction)")
    ax_az.set_xlabel("Time (Hanoi)")
    # matplotlib.dates.DateFormatter/HourLocator have no type annotations upstream
    ax_az.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=HANOI_TZ))  # type: ignore[no-untyped-call]
    ax_az.xaxis.set_major_locator(mdates.HourLocator(interval=2, tz=HANOI_TZ))  # type: ignore[no-untyped-call]
    ax_az.grid(True, alpha=0.3)

    # Set azimuth ticks and add cardinal directions
    ax_az.set_ylim(0, 360)
    az_ticks = np.arange(0, 361, 45)
    az_labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    ax_az.set_yticks(az_ticks)
    ax_az.set_yticklabels(
        [f"{deg}° ({label})" for deg, label in zip(az_ticks, az_labels, strict=False)]
    )

    # ===== Altitude over time =====
    ax_alt = fig.add_subplot(gs[alt_col])
    ax_alt.plot(times, altitudes, color="steelblue", lw=2)
    ax_alt.set_ylabel("Altitude (°)")
    ax_alt.set_xlabel("Time (Hanoi)")
    ax_alt.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=HANOI_TZ))  # type: ignore[no-untyped-call]
    ax_alt.xaxis.set_major_locator(mdates.HourLocator(interval=2, tz=HANOI_TZ))  # type: ignore[no-untyped-call]
    ax_alt.grid(True, alpha=0.3)
    ax_alt.axhline(0, color="gray", linestyle="--", lw=1)

    # ===== Title & Save =====
    if data.get("below_horizon", False) or data["start"] is None or data["end"] is None:
        title_text = f"{full_name} - below horizon"
    else:
        start_str = data["start"].strftime("%H:%M")
        end_str = data["end"].strftime("%H:%M")
        title_text = f"{full_name} - visible {start_str}-{end_str}"

    fig.suptitle(title_text, fontsize=13, fontweight="bold")

    safe_name = full_name.replace(" ", "_").replace("/", "_")
    plt.savefig(os.path.join(OUTPUT_FOLDER, f"{safe_name}.png"), dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ {full_name}")

print(f"\nGenerated {len(constellation_data)} plots.")
