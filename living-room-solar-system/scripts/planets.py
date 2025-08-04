from skyfield.api import load, Topos
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, timedelta
from math import radians, tan
import numpy as np
from zoneinfo import ZoneInfo

# ========== USER SETTINGS ==========
city_name = "Hanoi"
latitude = 20.994852335385882
longitude = 105.8676630997609
timezone_str = "Asia/Ho_Chi_Minh"
sample_interval_minutes = 10
elevation_m = 15.4
# ===================================

def get_wall_distance_for_azimuth(azimuth_deg, wall_distances):
    """
    Get wall distance for a given azimuth based on the closest direction.
    """
    min_diff = 360
    closest_direction = None
    
    for direction, distance in wall_distances.items():
        # Calculate angular difference (accounting for circular nature of degrees)
        diff = abs(azimuth_deg - direction)
        if diff > 180:
            diff = 360 - diff
        
        if diff < min_diff:
            min_diff = diff
            closest_direction = direction
    
    return wall_distances[closest_direction], closest_direction

def prompt_for_wall_distances():
    """
    Prompt user for wall distances in specific directions (degrees).
    """
    print("Enter wall distances for different directions (in degrees from North):")
    print("Examples: 0° = North, 90° = East, 180° = South, 270° = West")
    print("Enter 'done' when finished.")
    
    wall_distances = {}
    
    while True:
        direction_input = input("Direction in degrees (or 'done'): ").strip()
        
        if direction_input.lower() == 'done':
            if not wall_distances:
                print("You must enter at least one wall distance!")
                continue
            break
        
        try:
            direction = float(direction_input)
            if direction < 0 or direction >= 360:
                print("Direction must be between 0 and 359 degrees.")
                continue
            
            distance_input = input(f"Wall distance at {direction}° (in cm): ").strip()
            distance = float(distance_input)
            
            if distance <= 0:
                print("Distance must be positive.")
                continue
            
            wall_distances[direction] = distance
            print(f"Added: {direction}° = {distance} cm\n")
            
        except ValueError:
            print("Please enter valid numbers.\n")
    
    return wall_distances

# Load ephemeris and timescale
eph = load('de421.bsp')
ts = load.timescale()

# Define observer and location
observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude, elevation_m=elevation_m)
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
        rise_time = visibility_times[0]
        set_time = visibility_times[-1]
    else:
        avg_alt = avg_az = None
        rise_time = set_time = None
    
    results.append({
        'planet': name_map[key],
        'visible': bool(visible_altitudes),
        'avg_alt': avg_alt,
        'avg_az': avg_az,
        'rise_time': rise_time,
        'set_time': set_time
    })

# ========== OUTPUT ==========
print(f"Sunset: {sunset.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Sunrise: {sunrise.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print("\n--- Visible Planets Between Sunset and Sunrise ---\n")

visible_planets = [r for r in results if r['visible']]

if not visible_planets:
    print("No planets are visible between sunset and sunrise.")
else:
    # Show visible planets first
    for r in visible_planets:
        print(f"{r['planet']:>8}: Alt={r['avg_alt']:.1f}°, Az={r['avg_az']:.1f}°, "
              f"Visible from {r['rise_time'].strftime('%H:%M')} to {r['set_time'].strftime('%H:%M')}")
    
    # Now ask for wall distances for visible planet directions
    print(f"\n--- Wall Distance Input ---")
    print("Enter wall distances for the directions where planets are visible:")
    
    # Get unique azimuth ranges (group similar azimuths)
    azimuth_groups = {}
    for r in visible_planets:
        az = r['avg_az']
        # Round to nearest 10 degrees for grouping
        rounded_az = round(az / 10) * 10
        if rounded_az not in azimuth_groups:
            azimuth_groups[rounded_az] = []
        azimuth_groups[rounded_az].append(r)
    
    wall_distances = {}
    
    for grouped_az in sorted(azimuth_groups.keys()):
        planets_in_group = azimuth_groups[grouped_az]
        planet_names_str = ", ".join([p['planet'] for p in planets_in_group])
        
        print(f"\nPlanets near {grouped_az}° ({planet_names_str}):")
        while True:
            try:
                distance_input = input(f"Wall distance at ~{grouped_az}° (in cm): ").strip()
                distance = float(distance_input)
                if distance <= 0:
                    print("Distance must be positive.")
                    continue
                wall_distances[grouped_az] = distance
                break
            except ValueError:
                print("Please enter a valid number.")
    
    # Calculate wall heights for visible planets
    print(f"\n--- Planet Wall Projections ---\n")
    
    for r in visible_planets:
        # Find closest wall distance
        wall_distance_cm, closest_direction = get_wall_distance_for_azimuth(r['avg_az'], wall_distances)
        vertical_offset_cm = tan(radians(r['avg_alt'])) * wall_distance_cm
        
        print(f"{r['planet']:>8}: Alt={r['avg_alt']:.1f}°, Az={r['avg_az']:.1f}° "
              f"(using {wall_distance_cm:.0f}cm wall at ~{closest_direction:.0f}°)")
        print(f"{'':>10} Wall Height={vertical_offset_cm:.1f} cm, "
              f"Visible from {r['rise_time'].strftime('%H:%M')} to {r['set_time'].strftime('%H:%M')}")
        print()

# Show non-visible planets
non_visible_planets = [r for r in results if not r['visible']]
if non_visible_planets:
    print("--- Non-Visible Planets ---")
    for r in non_visible_planets:
        print(f"{r['planet']:>8}: Not visible between sunset and sunrise.")