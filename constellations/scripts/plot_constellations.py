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
DATA_FOLDER = "data/boundaries"  # folder with .txt files
OUTPUT_FOLDER = "data/plots"
DATE = datetime.now().date()
DELTA_MINUTES = 10  # time step in minutes
HANOI_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Observer setup
observer_location = EarthLocation(lat=LAT*u.deg, lon=LON*u.deg, height=ELEV*u.m)
observer = Observer(location=observer_location)

# Astronomical sunset/sunrise
location_info = LocationInfo(latitude=LAT, longitude=LON)
s = sun(location_info.observer, date=DATE)
sunset = s['sunset']
sunrise = s['sunrise'] + timedelta(days=1)  # next day

print(f"Sunset: {sunset}, Sunrise: {sunrise}")

# Time grid
times = [sunset + timedelta(minutes=i) for i in range(0, int((sunrise - sunset).total_seconds()/60), DELTA_MINUTES)]
times_astropy = Time([t.astimezone(pytz.UTC) for t in times])  # convert to UTC for astropy

# Store visibility info for timeline
visibility_dict = {}

# ===== Iterate over constellation files =====
for file_name in os.listdir(DATA_FOLDER):
    if file_name.endswith(".txt"):
        file_path = os.path.join(DATA_FOLDER, file_name)

        # Read the file
        df = pd.read_csv(file_path, sep="|", names=["RA_hms", "Dec_deg", "Constellation"], engine='python')
        df['Dec_deg'] = df['Dec_deg'].astype(float)

        # Convert RA HH MM SS.SSSS -> degrees
        ra_deg = []
        for ra_hms in df['RA_hms']:
            h, m, s = [float(x) for x in ra_hms.strip().split()]
            ra_deg.append((h + m/60 + s/3600) * 15)
        df['RA_deg'] = ra_deg

        # Group by constellation
        for const_abbr, group in df.groupby('Constellation'):
            const_abbr = const_abbr.strip()
            
            stars = SkyCoord(ra=group['RA_deg'].values*u.degree,
                             dec=group['Dec_deg'].values*u.degree,
                             frame='icrs')

            # Compute altitudes for each star at each time
            altitudes = []
            azimuths = []
            for t in times_astropy:
                altaz_frame = AltAz(obstime=t, location=observer_location)
                star_altaz = stars.transform_to(altaz_frame)
                altitudes.append(star_altaz.alt.deg)
                azimuths.append(star_altaz.az.deg)

            altitudes = np.array(altitudes)  # shape: (num_times, num_stars)
            azimuths = np.array(azimuths)

            # Determine visibility: any star above horizon
            visible = np.any(altitudes > 0, axis=1)
            visible_times = np.array(times)[visible]  # already in Hanoi timezone

            if len(visible_times) > 0:
                visibility_dict[const_abbr] = (visible_times[0], visible_times[-1])
            else:
                visibility_dict[const_abbr] = None

            # ===== Sky position plot for this constellation =====
            plt.figure(figsize=(8,6))
            num_stars = stars.shape[0]
            for i in range(num_stars):
                # Only plot points above horizon
                alt_i = altitudes[:, i]
                az_i = azimuths[:, i]
                mask = alt_i > 0
                plt.plot(az_i[mask], alt_i[mask], 'o')

            plt.xlabel("Azimuth (deg)")
            plt.ylabel("Altitude (deg)")
            plt.title(f"{const_abbr} positions tonight (Hanoi TZ)")
            plt.xlim(0,360)
            plt.ylim(0,90)
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(OUTPUT_FOLDER, f"{const_abbr}_positions.png"))
            plt.close()

# ===== Timeline plot in Hanoi timezone =====
plt.figure(figsize=(12, len(visibility_dict)*0.5 + 2))
constellations = list(visibility_dict.keys())
y_pos = np.arange(len(constellations))

for i, const_abbr in enumerate(constellations):
    times_range = visibility_dict[const_abbr]
    if times_range is not None:
        plt.hlines(y=i, xmin=times_range[0], xmax=times_range[1], color='blue', linewidth=4)
    else:
        plt.hlines(y=i, xmin=sunset, xmax=sunrise, color='lightgray', linewidth=2, linestyles='dashed')

plt.yticks(y_pos, constellations)
plt.xlabel("Time (Hanoi TZ)")
plt.title(f"Constellation Visibility Timeline for {DATE} (Hanoi TZ)")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.grid(axis='x', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "constellations_timeline_hanoi.png"))
plt.show()