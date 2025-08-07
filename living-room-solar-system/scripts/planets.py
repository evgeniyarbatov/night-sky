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

def get_cardinal_direction(azimuth):
    """Convert azimuth to cardinal direction description."""
    directions = [
        (0, "North"), (22.5, "NNE"), (45, "NE"), (67.5, "ENE"),
        (90, "East"), (112.5, "ESE"), (135, "SE"), (157.5, "SSE"),
        (180, "South"), (202.5, "SSW"), (225, "SW"), (247.5, "WSW"),
        (270, "West"), (292.5, "WNW"), (315, "NW"), (337.5, "NNW"), (360, "North")
    ]
    
    for i in range(len(directions) - 1):
        if directions[i][0] <= azimuth < directions[i + 1][0]:
            return directions[i][1]
    return "North"

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

# Map simplified names with unique symbols
name_map = {
    'Mercury': 'Mercury',
    'Venus': 'Venus',
    'Mars': 'Mars',
    'Jupiter barycenter': 'Jupiter',
    'Saturn barycenter': 'Saturn',
    'Uranus barycenter': 'Uranus',
    'Neptune barycenter': 'Neptune'
}

# Unique planet symbols/logos
planet_symbols = {
    'Mercury': '☿️',  # Mercury symbol
    'Venus': '♀️',    # Venus symbol
    'Mars': '♂️',     # Mars symbol
    'Jupiter': '♃',   # Jupiter symbol
    'Saturn': '♄',    # Saturn symbol
    'Uranus': '♅',    # Uranus symbol
    'Neptune': '♆'    # Neptune symbol
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
print("="*60)
print(f"PLANET VISIBILITY REPORT FOR {city_name.upper()}")
print("="*60)
print(f"Sunset:  {sunset.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Sunrise: {sunrise.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Duration: {(sunrise - sunset).total_seconds() / 3600:.1f} hours")
print()

visible_planets = [r for r in results if r['visible']]
non_visible_planets = [r for r in results if not r['visible']]

print("--- VISIBLE PLANETS AND THEIR DIRECTIONS ---")
print()

if not visible_planets:
    print("❌ No planets are visible between sunset and sunrise.")
    print()
else:
    print("✅ The following planets will be visible:")
    print()
    
    for r in visible_planets:
        cardinal = get_cardinal_direction(r['avg_az'])
        symbol = planet_symbols[r['planet']]
        print(f"{symbol} {r['planet']:>8}: {r['avg_alt']:5.1f}° altitude, {r['avg_az']:5.1f}° azimuth ({cardinal})")
        print(f"{'':>12} Visible from {r['rise_time'].strftime('%H:%M')} to {r['set_time'].strftime('%H:%M')}")
        print()
    
    # Show azimuth reference
    print("📍 DIRECTION REFERENCE:")
    print("   0° = North, 90° = East, 180° = South, 270° = West")
    print()
    
    # Group planets by similar directions for wall distance input
    azimuth_groups = {}
    for r in visible_planets:
        az = r['avg_az']
        # Round to nearest 15 degrees for grouping
        rounded_az = round(az / 15) * 15
        if rounded_az >= 360:
            rounded_az = 0
        if rounded_az not in azimuth_groups:
            azimuth_groups[rounded_az] = []
        azimuth_groups[rounded_az].append(r)
    
    print("--- WALL DISTANCE INPUT NEEDED ---")
    print()
    print("You need to measure wall distances in these directions:")
    
    for grouped_az in sorted(azimuth_groups.keys()):
        planets_in_group = azimuth_groups[grouped_az]
        planet_names_with_symbols = ", ".join([f"{planet_symbols[p['planet']]} {p['planet']}" for p in planets_in_group])
        cardinal = get_cardinal_direction(grouped_az)
        print(f"📏 ~{grouped_az:3.0f}° ({cardinal:>3}) for: {planet_names_with_symbols}")
    
    print()
    print("Now measuring wall distances...")
    print("-" * 40)
    
    # Get wall distances
    wall_distances = {}
    
    for grouped_az in sorted(azimuth_groups.keys()):
        planets_in_group = azimuth_groups[grouped_az]
        planet_names_with_symbols = ", ".join([f"{planet_symbols[p['planet']]} {p['planet']}" for p in planets_in_group])
        cardinal = get_cardinal_direction(grouped_az)
        
        print(f"\n🎯 Direction: {grouped_az}° ({cardinal}) - for {planet_names_with_symbols}")
        while True:
            try:
                distance_input = input(f"   Wall distance (in cm): ").strip()
                distance = float(distance_input)
                if distance <= 0:
                    print("   ❌ Distance must be positive. Please try again.")
                    continue
                wall_distances[grouped_az] = distance
                print(f"   ✅ Recorded: {distance} cm")
                break
            except ValueError:
                print("   ❌ Please enter a valid number.")
    
    # Calculate wall heights for visible planets
    print()
    print("=" * 60)
    print("PLANET WALL PROJECTION RESULTS")
    print("=" * 60)
    
    for r in visible_planets:
        # Find closest wall distance
        wall_distance_cm, closest_direction = get_wall_distance_for_azimuth(r['avg_az'], wall_distances)
        vertical_offset_cm = tan(radians(r['avg_alt'])) * wall_distance_cm
        cardinal = get_cardinal_direction(r['avg_az'])
        symbol = planet_symbols[r['planet']]
        
        print(f"\n{symbol} {r['planet']:>8}:")
        print(f"   Position: {r['avg_alt']:5.1f}° altitude, {r['avg_az']:5.1f}° azimuth ({cardinal})")
        print(f"   Using wall: {wall_distance_cm:.0f} cm at ~{closest_direction:.0f}°")
        print(f"   📐 Wall projection height: {vertical_offset_cm:.1f} cm")
        print(f"   ⏰ Visible: {r['rise_time'].strftime('%H:%M')} to {r['set_time'].strftime('%H:%M')}")

if non_visible_planets:
    print()
    print("--- NON-VISIBLE PLANETS ---")
    for r in non_visible_planets:
        symbol = planet_symbols[r['planet']]
        print(f"⭕ {symbol} {r['planet']:>8}: Not visible between sunset and sunrise")

print()
print("=" * 60)