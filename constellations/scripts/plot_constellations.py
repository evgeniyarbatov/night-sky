import os
import pandas as pd
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import astropy.units as u
from astroplan import Observer
from astral import LocationInfo
from astral.sun import sun
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import pytz
from PIL import Image

# ===== User settings =====
LAT = 20.99484044876172
LON = 105.86796107324045
ELEV = 10  # meters
DATA_FOLDER = "data/boundaries"
OUTPUT_FOLDER = "data/plots"
GIF_FOLDER = "data/gifs"
DATE = datetime.now().date()
DELTA_MINUTES = 10
HANOI_TZ = pytz.timezone("Asia/Ho_Chi_Minh")
NAMES_FILE = "data/constellation_names.csv"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ===== Load constellation names =====
try:
    names_df = pd.read_csv(NAMES_FILE)
    const_names = dict(zip(names_df['abbreviation'], names_df['name']))
except Exception as e:
    print(f"Error: Could not load {NAMES_FILE} — {e}")
    exit(1)

# ===== Observer setup =====
observer_location = EarthLocation(lat=LAT*u.deg, lon=LON*u.deg, height=ELEV*u.m)
observer = Observer(location=observer_location)

# ===== Compute sunset/sunrise =====
location_info = LocationInfo(latitude=LAT, longitude=LON)
s = sun(location_info.observer, date=DATE, tzinfo=HANOI_TZ)
sunset = s['sunset']
sunrise = s['sunrise'] + timedelta(days=1)

# ===== Time grid for visibility calculation =====
times = [sunset + timedelta(minutes=i) for i in range(0, int((sunrise - sunset).total_seconds()/60), DELTA_MINUTES)]
times_astropy = Time([t.astimezone(pytz.UTC) for t in times])

# ===== Observation time for direction info =====
obs_time_local = HANOI_TZ.localize(datetime.combine(DATE, datetime.strptime("23:00", "%H:%M").time()))
obs_time_utc = obs_time_local.astimezone(pytz.UTC)
obs_time_astropy = Time(obs_time_utc)

constellation_data = {}

# ===== Process constellation files =====
for file_name in os.listdir(DATA_FOLDER):
    if not file_name.endswith(".txt"):
        continue

    file_path = os.path.join(DATA_FOLDER, file_name)
    df = pd.read_csv(file_path, sep="|", names=["RA_hms", "Dec_deg", "Constellation"], engine='python')
    df['Dec_deg'] = df['Dec_deg'].astype(float)

    # Convert RA hms to degrees
    ra_deg = []
    for ra_hms in df['RA_hms']:
        h, m, s = [float(x) for x in ra_hms.strip().split()]
        ra_deg.append((h + m/60 + s/3600) * 15)
    df['RA_deg'] = ra_deg

    for const_abbr, group in df.groupby('Constellation'):
        const_abbr = const_abbr.strip()
        stars = SkyCoord(ra=group['RA_deg'].values*u.degree,
                         dec=group['Dec_deg'].values*u.degree,
                         frame='icrs')

        altitudes = []
        azimuths = []

        for t in times_astropy:
            altaz_frame = AltAz(obstime=t, location=observer_location)
            star_altaz = stars.transform_to(altaz_frame)
            altitudes.append(star_altaz.alt.deg)
            azimuths.append(star_altaz.az.deg)

        altitudes = np.array(altitudes)
        azimuths = np.array(azimuths)

        # Determine if any part of constellation is above horizon at each time
        visible = np.any(altitudes > 0, axis=1)
        if not np.any(visible):
            continue  # skip never-visible constellations

        # Visible times in local timezone
        visible_times = np.array(times)[visible]
        start_time = visible_times[0].astimezone(HANOI_TZ)
        end_time = visible_times[-1].astimezone(HANOI_TZ)

        # 23:00 reference data (for position/direction)
        altaz_23 = stars.transform_to(AltAz(obstime=obs_time_astropy, location=observer_location))
        visible_at_23 = altaz_23.alt.deg > 0
        if np.any(visible_at_23):
            avg_alt = np.mean(altaz_23.alt.deg[visible_at_23])
            avg_az = np.mean(altaz_23.az.deg[visible_at_23])
            direction = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][int((avg_az + 22.5) / 45) % 8]
        else:
            avg_alt, avg_az, direction = np.nan, np.nan, "below horizon"

        constellation_data[const_abbr] = {
            'start': start_time,
            'end': end_time,
            'alt_23': avg_alt,
            'az_23': avg_az,
            'direction': direction
        }

# ===== Create plots =====
for const_abbr, data in constellation_data.items():
    full_name = const_names.get(const_abbr, const_abbr)

    gif_path = os.path.join(GIF_FOLDER, f"{const_abbr}.gif")
    has_gif = os.path.exists(gif_path)

    if has_gif:
        fig = plt.figure(figsize=(16, 4))
        gs = fig.add_gridspec(1, 3, width_ratios=[1.2, 1, 1.8], wspace=0.3)
        gif_col, sky_col, time_col = 0, 1, 2
    else:
        fig = plt.figure(figsize=(12, 4))
        gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.8], wspace=0.25)
        sky_col, time_col = 0, 1

    # ===== GIF (if available) =====
    if has_gif:
        ax_gif = fig.add_subplot(gs[gif_col])
        img = Image.open(gif_path)
        ax_gif.imshow(img)
        ax_gif.axis('off')

    # ===== Sky position at 23:00 (polar) =====
    ax_sky = fig.add_subplot(gs[sky_col], projection='polar')
    ax_sky.set_theta_zero_location('N')
    ax_sky.set_theta_direction(-1)
    ax_sky.set_thetagrids(np.arange(0, 360, 45),
                          labels=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

    if not np.isnan(data['alt_23']):
        az_rad = np.radians(data['az_23'])
        r = 90 - data['alt_23']
        ax_sky.plot(az_rad, r, 'o', markersize=18, color='gold',
                    markeredgecolor='darkorange', markeredgewidth=2)
        ax_sky.set_title(f"{data['direction']} @ 23:00", fontsize=11, pad=10)
    else:
        ax_sky.text(0.5, 0.5, "Below horizon at 23:00", ha='center', va='center', transform=ax_sky.transAxes)

    ax_sky.set_ylim(0, 90)
    ax_sky.set_yticks([0, 30, 60, 90])
    ax_sky.set_yticklabels(['90°', '60°', '30°', '0°'])
    ax_sky.grid(True, alpha=0.3)

    # ===== Timeline: visibility period =====
    ax_time = fig.add_subplot(gs[time_col])

    start_num = mdates.date2num(data['start'])
    end_num = mdates.date2num(data['end'])
    obs_num = mdates.date2num(obs_time_local)

    # Full night background
    ax_time.barh(0, mdates.date2num(sunrise) - mdates.date2num(sunset),
                 left=mdates.date2num(sunset), height=0.5,
                 color='lightgray', alpha=0.4)

    # Visibility window
    ax_time.barh(0, end_num - start_num, left=start_num, height=0.5,
                 color='steelblue', edgecolor='navy', linewidth=1.5)

    # Mark 23:00
    ax_time.plot([obs_num, obs_num], [-0.25, 0.25],
                 color='gold', linewidth=2, solid_capstyle='round')
    ax_time.text(obs_num, 0.35, "23:00", ha='center', fontsize=9,
                 fontweight='bold', color='gold')

    ax_time.set_ylim(-0.4, 0.6)
    ax_time.set_yticks([])
    ax_time.set_xlim(mdates.date2num(sunset), mdates.date2num(sunrise))
    ax_time.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=HANOI_TZ))
    ax_time.xaxis.set_major_locator(mdates.HourLocator(interval=2, tz=HANOI_TZ))
    ax_time.grid(True, axis='x', alpha=0.3)
    ax_time.set_xlabel('Time (Hanoi)', fontsize=10)
    for spine in ['top', 'right', 'left']:
        ax_time.spines[spine].set_visible(False)

    fig.suptitle(f"{full_name} — visible {data['start'].strftime('%H:%M')}–{data['end'].strftime('%H:%M')} "
                 f"({data['direction']} {data['alt_23']:.1f}° @ 23:00)",
                 fontsize=13, fontweight='bold')

    safe_name = full_name.replace(' ', '_').replace('/', '_')
    plt.savefig(os.path.join(OUTPUT_FOLDER, f"{safe_name}.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ {full_name}: visible {data['start'].strftime('%H:%M')}–{data['end'].strftime('%H:%M')}")

print(f"\nGenerated {len(constellation_data)} plots showing visibility periods.")
