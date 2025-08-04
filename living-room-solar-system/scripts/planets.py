from skyfield.api import load, Topos
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, timedelta
from math import radians, tan
import numpy as np
from zoneinfo import ZoneInfo

# ========== USER SETTINGS ==========
city_name = "Hanoi"
latitude = 21.0285
longitude = 105.8544
timezone_str = "Asia/Ho_Chi_Minh"

wall_distance_cm = 300     # Distance from eyes to wall
sample_interval_minutes = 10
# ===================================

# Load ephemeris and timescale
eph = load('de421.bsp')
ts = load.timescale()

# Define observer and location
observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
earth = eph['earth']
location = earth + observer

# Astral: get sunset today and sunrise tomorrow
today = datetime.now(ZoneInfo(timezone_str)).date()
tomorrow = today + timedelta(days=1)
city = LocationInfo(city_name, "Vietnam", timezone_str, latitude, longitude)
tz = ZoneInfo(timezone_str)

sun_today = sun(city.observer, date=today, tzinfo=tz)
sun_tomorrow = sun(city.observer, date=tomorrow, tzinfo=tz)

sunset = sun_today['sunset']
sunrise = sun_tomorrow['sunrise']

# Generate sample times (Skyfield) and corresponding native datetimes
dt_list = []
sample_times = []
current_dt = sunset
while current_dt <= sunrise:
    dt_list.append(current_dt)
    sample_times.append(ts.from_datetime(current_dt))
    current_dt += timedelta(minutes=sample_interval_minutes)

# Planets to track
planet_names = [
    'Mercury', 'Venus', 'Mars',
    'Jupiter barycenter', 'Saturn barycenter',
    'Uranus barycenter', 'Neptune barycenter'
]

# Map simplified names
name_map = {
    'Mercury': 'Mercury',
    'Venus': 'Venus',
    'Mars': 'Mars',
    'Jupiter barycenter': 'Jupiter',
    'Saturn barycenter': 'Saturn',
    'Uranus barycenter': 'Uranus',
    'Neptune barycenter': 'Neptune'
}

# Store results
results = []

# Loop through each planet
for key in planet_names:
    planet = eph[key]
    altitudes = []
    azimuths = []
    visibility_times = []

    for dt, t in zip(dt_list, sample_times):
        astrometric = location.at(t).observe(planet).apparent()
        alt, az, _ = astrometric.altaz()
        alt_deg = alt.degrees
        altitudes.append(alt_deg)
        azimuths.append(az.degrees)

        if alt_deg > 0:
            visibility_times.append(dt)

    # Filter out when planet is above the horizon
    visible_altitudes = [a for a in altitudes if a > 0]
    visible_azimuths = [azimuths[i] for i, a in enumerate(altitudes) if a > 0]

    if visible_altitudes:
        avg_alt = np.mean(visible_altitudes)
        avg_az = np.mean(visible_azimuths)
        vertical_offset_cm = tan(radians(avg_alt)) * wall_distance_cm
        rise_time = visibility_times[0]
        set_time = visibility_times[-1]
    else:
        avg_alt = avg_az = vertical_offset_cm = None
        rise_time = set_time = None

    results.append({
        'planet': name_map[key],
        'visible': bool(visible_altitudes),
        'avg_alt': avg_alt,
        'avg_az': avg_az,
        'vertical_offset_cm': vertical_offset_cm,
        'rise_time': rise_time,
        'set_time': set_time
    })

# ========== OUTPUT ==========
print(f"Sunset: {sunset.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Sunrise: {sunrise.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print("\n--- Planet Positions Between Sunset and Sunrise ---\n")

for r in results:
    if r['visible']:
        print(f"{r['planet']:>8}: Alt={r['avg_alt']:.1f}°, Az={r['avg_az']:.1f}°, "
              f"Wall Height={r['vertical_offset_cm']:.1f} cm, "
              f"Visible from {r['rise_time'].strftime('%H:%M')} to {r['set_time'].strftime('%H:%M')}")
    else:
        print(f"{r['planet']:>8}: Not visible between sunset and sunrise.")
