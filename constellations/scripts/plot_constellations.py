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

# Load constellation names
try:
    names_df = pd.read_csv(NAMES_FILE)
    const_names = dict(zip(names_df['abbreviation'], names_df['name']))
except:
    print(f"Error: Could not load {NAMES_FILE}")
    exit(1)

# Observer setup
observer_location = EarthLocation(lat=LAT*u.deg, lon=LON*u.deg, height=ELEV*u.m)
observer = Observer(location=observer_location)

# Astronomical sunset/sunrise
location_info = LocationInfo(latitude=LAT, longitude=LON)
s = sun(location_info.observer, date=DATE, tzinfo=HANOI_TZ)
sunset = s['sunset']
sunrise = s['sunrise'] + timedelta(days=1)

print(f"Night: {sunset.strftime('%H:%M')} - {sunrise.strftime('%H:%M')} (Hanoi TZ)")

# Time grid (night only)
times = [sunset + timedelta(minutes=i) for i in range(0, int((sunrise - sunset).total_seconds()/60), DELTA_MINUTES)]
times_astropy = Time([t.astimezone(pytz.UTC) for t in times])

# Ensure sunset and sunrise are in Hanoi TZ
sunset = sunset.astimezone(HANOI_TZ)
sunrise = sunrise.astimezone(HANOI_TZ)

constellation_data = {}

# ===== Process constellation files =====
for file_name in os.listdir(DATA_FOLDER):
    if file_name.endswith(".txt"):
        file_path = os.path.join(DATA_FOLDER, file_name)
        df = pd.read_csv(file_path, sep="|", names=["RA_hms", "Dec_deg", "Constellation"], engine='python')
        df['Dec_deg'] = df['Dec_deg'].astype(float)

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

            visible = np.any(altitudes > 0, axis=1)
            visible_times = np.array(times)[visible]

            if len(visible_times) > 0:
                visible_mask = visible
                median_alt = np.median(altitudes[visible_mask][altitudes[visible_mask] > 0])
                median_az = np.median(azimuths[visible_mask][altitudes[visible_mask] > 0])
                
                # Ensure times are in Hanoi TZ
                start_time = visible_times[0]
                end_time = visible_times[-1]
                if not hasattr(start_time, 'tzinfo') or start_time.tzinfo is None:
                    start_time = HANOI_TZ.localize(start_time)
                else:
                    start_time = start_time.astimezone(HANOI_TZ)
                if not hasattr(end_time, 'tzinfo') or end_time.tzinfo is None:
                    end_time = HANOI_TZ.localize(end_time)
                else:
                    end_time = end_time.astimezone(HANOI_TZ)
                
                constellation_data[const_abbr] = {
                    'start': start_time,
                    'end': end_time,
                    'median_alt': median_alt,
                    'median_az': median_az
                }

# ===== Create individual plots =====
for const_abbr, data in constellation_data.items():
    full_name = const_names.get(const_abbr, const_abbr)
    
    # Check if GIF exists
    gif_path = os.path.join(GIF_FOLDER, f"{const_abbr}.gif")
    has_gif = os.path.exists(gif_path)
    
    if has_gif:
        fig = plt.figure(figsize=(16, 4))
        gs = fig.add_gridspec(1, 3, width_ratios=[1.2, 1, 1.8], wspace=0.3)
        gif_col = 0
        sky_col = 1
        time_col = 2
    else:
        fig = plt.figure(figsize=(12, 4))
        gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.8], wspace=0.25)
        sky_col = 0
        time_col = 1
    
    # GIF (if available)
    if has_gif:
        from PIL import Image
        ax_gif = fig.add_subplot(gs[gif_col])
        img = Image.open(gif_path)
        # Show first frame
        ax_gif.imshow(img)
        ax_gif.axis('off')
    
    # Sky position
    ax_sky = fig.add_subplot(gs[sky_col], projection='polar')
    ax_sky.set_theta_zero_location('N')
    ax_sky.set_theta_direction(-1)
    
    az_rad = np.radians(data['median_az'])
    r = 90 - data['median_alt']
    
    ax_sky.plot(az_rad, r, 'o', markersize=18, color='gold', markeredgecolor='darkorange', markeredgewidth=2)
    ax_sky.set_ylim(0, 90)
    ax_sky.set_yticks([0, 30, 60, 90])
    ax_sky.set_yticklabels(['90°', '60°', '30°', '0°'])
    ax_sky.grid(True, alpha=0.3)
    
    direction = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][int((data['median_az'] + 22.5) / 45) % 8]
    
    # Timeline (night only)
    ax_time = fig.add_subplot(gs[time_col])
    
    start_num = mdates.date2num(data['start'])
    end_num = mdates.date2num(data['end'])
    duration_hours = (data['end'] - data['start']).total_seconds()/3600
    
    ax_time.barh(0, end_num - start_num, left=start_num, height=0.5, 
                 color='steelblue', edgecolor='navy', linewidth=1.5)
    
    start_str = data['start'].strftime('%H:%M')
    end_str = data['end'].strftime('%H:%M')
    
    ax_time.text(start_num, 0.35, start_str, ha='center', fontsize=9, fontweight='bold')
    ax_time.text(end_num, 0.35, end_str, ha='center', fontsize=9, fontweight='bold')
    ax_time.text((start_num + end_num)/2, 0, f'{duration_hours:.1f}h', 
                ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    
    ax_time.set_ylim(-0.4, 0.6)
    ax_time.set_yticks([])
    ax_time.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=HANOI_TZ))
    ax_time.xaxis.set_major_locator(mdates.HourLocator(interval=2, tz=HANOI_TZ))
    ax_time.set_xlim(mdates.date2num(sunset), mdates.date2num(sunrise))
    ax_time.grid(True, axis='x', alpha=0.3)
    ax_time.set_xlabel('Time (Hanoi)', fontsize=10)
    
    for spine in ['top', 'right', 'left']:
        ax_time.spines[spine].set_visible(False)
    
    fig.suptitle(full_name, fontsize=13, fontweight='bold')
    
    # Save with constellation name
    safe_name = full_name.replace(' ', '_').replace('/', '_')
    plt.savefig(os.path.join(OUTPUT_FOLDER, f"{safe_name}.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ {full_name}")

print(f"\nGenerated {len(constellation_data)} plots")