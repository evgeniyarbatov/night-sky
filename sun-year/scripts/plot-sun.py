from datetime import datetime, timedelta

import ephem
import matplotlib.pyplot as plt
import numpy as np

# Location: Hanoi, Vietnam
lat = 20.994839969936898
lon = 105.86779701825405

# Create observer
observer = ephem.Observer()
observer.lat = str(lat)
observer.lon = str(lon)
observer.elevation = 0  # meters above sea level
observer.horizon = "0"  # 0 degrees for astronomical sunrise/sunset


def get_sun_azimuth_at_rise_set(observer, date):
    """
    Calculate sun's exact azimuth at sunrise and sunset using PyEphem.
    PyEphem computes exact rise/set times analytically.
    """
    observer.date = date
    sun = ephem.Sun()

    try:
        # Get exact sunrise time
        sunrise_time = observer.next_rising(sun)
        observer.date = sunrise_time
        sun.compute(observer)
        sunrise_az = np.degrees(sun.az)

        # Reset date and get exact sunset time
        observer.date = date
        sunset_time = observer.next_setting(sun)
        observer.date = sunset_time
        sun.compute(observer)
        sunset_az = np.degrees(sun.az)

        return sunrise_az, sunset_az
    except (ephem.AlwaysUpError, ephem.NeverUpError):
        # Handle polar day/night scenarios
        return None, None


# Calculate for one year from today
start_date = datetime.now()
dates = []
sunrise_azimuths = []
sunset_azimuths = []

print(
    f"Calculating exact sun rise/set positions for 1 year from {start_date.strftime('%Y-%m-%d')}..."
)
print("Using PyEphem analytical methods for exact rise/set moments")
print()

# Calculate for 365 days from today
for day_offset in range(365):
    dt = start_date + timedelta(days=day_offset)
    sr_az, ss_az = get_sun_azimuth_at_rise_set(observer, dt)

    if sr_az is not None and ss_az is not None:
        dates.append(dt)
        sunrise_azimuths.append(sr_az)
        sunset_azimuths.append(ss_az)

    if (day_offset + 1) % 30 == 0:
        print(f"  Processed {day_offset + 1}/365 days...")

print(f"\nTotal days calculated: {len(dates)}")

# Find dates when sun is exactly East (90°) and West (270°)
# These occur around equinoxes
east_dates = []
west_dates = []

for i in range(len(dates) - 1):
    # Check for crossing 90° (East) for sunrise
    if (sunrise_azimuths[i] < 90 and sunrise_azimuths[i + 1] >= 90) or (
        sunrise_azimuths[i] > 90 and sunrise_azimuths[i + 1] <= 90
    ):
        # Interpolate exact date
        fraction = (90 - sunrise_azimuths[i]) / (sunrise_azimuths[i + 1] - sunrise_azimuths[i])
        exact_date = dates[i] + (dates[i + 1] - dates[i]) * fraction
        east_dates.append(exact_date)

    # Check for crossing 270° (West) for sunset
    if (sunset_azimuths[i] < 270 and sunset_azimuths[i + 1] >= 270) or (
        sunset_azimuths[i] > 270 and sunset_azimuths[i + 1] <= 270
    ):
        # Interpolate exact date
        fraction = (270 - sunset_azimuths[i]) / (sunset_azimuths[i + 1] - sunset_azimuths[i])
        exact_date = dates[i] + (dates[i + 1] - dates[i]) * fraction
        west_dates.append(exact_date)

# Find min and max azimuth points
sunrise_min_idx = np.argmin(sunrise_azimuths)
sunrise_max_idx = np.argmax(sunrise_azimuths)
sunset_min_idx = np.argmin(sunset_azimuths)
sunset_max_idx = np.argmax(sunset_azimuths)

# Plotting - Separate plots for sunrise and sunset
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Stronger colors
sunrise_color = "#FF8C00"  # Dark orange
sunset_color = "#DC143C"  # Crimson
equinox_color = "#4A90E2"  # Blue
extrema_color = "#2ECC71"  # Green

# Sunrise plot
ax1.plot(dates, sunrise_azimuths, color=sunrise_color, alpha=0.8, linewidth=2.5)
ax1.fill_between(dates, sunrise_azimuths, 90, alpha=0.2, color=sunrise_color)

# Draw vertical lines at exact East
for ed in east_dates:
    ax1.axvline(x=ed, color=equinox_color, linestyle="-", alpha=0.5, linewidth=1.5)
    ax1.text(
        ed,
        115,
        ed.strftime("%b %d"),
        rotation=90,
        ha="right",
        va="bottom",
        fontsize=9,
        color=equinox_color,
        fontweight="bold",
    )

# Mark min azimuth (most northern, summer solstice)
ax1.plot(
    dates[sunrise_min_idx],
    sunrise_azimuths[sunrise_min_idx],
    "o",
    color=extrema_color,
    markersize=8,
    zorder=5,
)
ax1.text(
    dates[sunrise_min_idx],
    sunrise_azimuths[sunrise_min_idx] - 3,
    f"{sunrise_azimuths[sunrise_min_idx]:.1f}°\n{dates[sunrise_min_idx].strftime('%b %d')}",
    ha="center",
    va="top",
    fontsize=9,
    color=extrema_color,
    fontweight="bold",
)

# Mark max azimuth (most southern, winter solstice)
ax1.plot(
    dates[sunrise_max_idx],
    sunrise_azimuths[sunrise_max_idx],
    "o",
    color=extrema_color,
    markersize=8,
    zorder=5,
)
ax1.text(
    dates[sunrise_max_idx],
    sunrise_azimuths[sunrise_max_idx] + 3,
    f"{sunrise_azimuths[sunrise_max_idx]:.1f}°\n{dates[sunrise_max_idx].strftime('%b %d')}",
    ha="center",
    va="bottom",
    fontsize=9,
    color=extrema_color,
    fontweight="bold",
)

ax1.grid(True, alpha=0.2, color="gray", linestyle="-", linewidth=0.5)
ax1.set_ylim(60, 120)
ax1.set_yticks([60, 90, 120])
ax1.set_yticklabels(["60° NE", "90° East", "120° SE"], fontsize=11, color="#333333")
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.spines["left"].set_color("#CCCCCC")
ax1.spines["bottom"].set_color("#CCCCCC")
ax1.tick_params(colors="#999999")

# Sunset plot
ax2.plot(dates, sunset_azimuths, color=sunset_color, alpha=0.8, linewidth=2.5)
ax2.fill_between(dates, sunset_azimuths, 270, alpha=0.2, color=sunset_color)

# Draw vertical lines at exact West
for wd in west_dates:
    ax2.axvline(x=wd, color=equinox_color, linestyle="-", alpha=0.5, linewidth=1.5)
    ax2.text(
        wd,
        295,
        wd.strftime("%b %d"),
        rotation=90,
        ha="right",
        va="bottom",
        fontsize=9,
        color=equinox_color,
        fontweight="bold",
    )

# Mark max azimuth (most northern, summer solstice)
ax2.plot(
    dates[sunset_max_idx],
    sunset_azimuths[sunset_max_idx],
    "o",
    color=extrema_color,
    markersize=8,
    zorder=5,
)
ax2.text(
    dates[sunset_max_idx],
    sunset_azimuths[sunset_max_idx] + 3,
    f"{sunset_azimuths[sunset_max_idx]:.1f}°\n{dates[sunset_max_idx].strftime('%b %d')}",
    ha="center",
    va="bottom",
    fontsize=9,
    color=extrema_color,
    fontweight="bold",
)

# Mark min azimuth (most southern, winter solstice)
ax2.plot(
    dates[sunset_min_idx],
    sunset_azimuths[sunset_min_idx],
    "o",
    color=extrema_color,
    markersize=8,
    zorder=5,
)
ax2.text(
    dates[sunset_min_idx],
    sunset_azimuths[sunset_min_idx] - 3,
    f"{sunset_azimuths[sunset_min_idx]:.1f}°\n{dates[sunset_min_idx].strftime('%b %d')}",
    ha="center",
    va="top",
    fontsize=9,
    color=extrema_color,
    fontweight="bold",
)

ax2.grid(True, alpha=0.2, color="gray", linestyle="-", linewidth=0.5)
ax2.set_ylim(240, 300)
ax2.set_yticks([240, 270, 300])
ax2.set_yticklabels(["240° SW", "270° West", "300° NW"], fontsize=11, color="#333333")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_color("#CCCCCC")
ax2.spines["bottom"].set_color("#CCCCCC")
ax2.tick_params(colors="#999999")

plt.tight_layout()
plt.show()

# Summary statistics
print("\n" + "=" * 80)
print("Annual Summary Statistics:")
print("=" * 80)
print("  Sunrise Azimuth:")
print(f"    • Average: {np.mean(sunrise_azimuths):.2f}°")
print(f"    • Most northern: {min(sunrise_azimuths):.2f}° (summer - sun rises NE)")
print(f"    • Most southern: {max(sunrise_azimuths):.2f}° (winter - sun rises SE)")
print(f"    • Total variation: {max(sunrise_azimuths) - min(sunrise_azimuths):.2f}°")
print(f"    • Deviation from due East: {abs(np.mean(sunrise_azimuths) - 90):.2f}°")
print()
print("  Sunset Azimuth:")
print(f"    • Average: {np.mean(sunset_azimuths):.2f}°")
print(f"    • Most northern: {max(sunset_azimuths):.2f}° (summer - sun sets NW)")
print(f"    • Most southern: {min(sunset_azimuths):.2f}° (winter - sun sets SW)")
print(f"    • Total variation: {max(sunset_azimuths) - min(sunset_azimuths):.2f}°")
print(f"    • Deviation from due West: {abs(np.mean(sunset_azimuths) - 270):.2f}°")
print()
print("=" * 80)
print("Compass Reference:")
print("  • 0°/360° = North    • 90° = East    • 180° = South    • 270° = West")
print("=" * 80)
print(f"Calculation period: {start_date.strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
print("Method: PyEphem analytical calculation (exact to the second)")
print("=" * 80)
