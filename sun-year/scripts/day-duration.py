import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pvlib

# === CONFIGURATION ===
latitude = 20.994839969936898
longitude = 105.86779701825405
tz = "Asia/Bangkok"  # Hanoi timezone

# === DEFINE DATE RANGE: 12 MONTHS FROM TODAY ===
start_date = pd.Timestamp.now(tz=tz).normalize()
end_date = start_date + pd.DateOffset(months=12)

times = pd.date_range(
    start=start_date,
    end=end_date,
    freq="D",
    tz=tz,  # daily steps are sufficient
)

# === CALCULATE SUNRISE, SUNSET, AND DAY DURATION ===
srs = pvlib.solarposition.sun_rise_set_transit_ephem(times, latitude, longitude)

# Compute daylight duration in hours
day_duration = (srs["sunset"] - srs["sunrise"]).dt.total_seconds() / 3600

# === BUILD DATAFRAME ===
df = pd.DataFrame({"date": times, "month": times.month, "day_length": day_duration})

# === AVERAGE DAY LENGTH PER MONTH ===
monthly_avg = df.groupby("month")["day_length"].mean().reset_index()

# === PLOT ===
plt.figure(figsize=(10, 6))

# Cheerful & distinct palette
colors = plt.cm.tab10(np.linspace(0, 1, 12))

plt.plot(
    monthly_avg["month"],
    monthly_avg["day_length"],
    color="#3D8E8E",
    linewidth=3,
    alpha=0.9,
)
plt.scatter(monthly_avg["month"], monthly_avg["day_length"], s=70, color=colors, alpha=0.9)

# === Minimal, Zen-like styling ===
plt.xlabel("Month", fontsize=12)
plt.ylabel("Daylight Duration (hours)", fontsize=12)
plt.xticks(
    monthly_avg["month"],
    [pd.Timestamp(2000, m, 1).strftime("%b") for m in monthly_avg["month"]],
    fontsize=10,
)
plt.yticks(fontsize=10)
plt.grid(alpha=0.15, linestyle="--")
plt.box(False)
plt.tight_layout()

# Gentle background tones
plt.gcf().patch.set_facecolor("#f9f9f6")
plt.gca().set_facecolor("#f9f9f6")

# Remove spines for calm aesthetic
for spine in plt.gca().spines.values():
    spine.set_visible(False)

plt.show()
