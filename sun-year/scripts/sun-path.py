import pandas as pd
import matplotlib.pyplot as plt
import pvlib
import numpy as np
from datetime import datetime

# === CONFIGURATION ===
latitude = 20.994839969936898
longitude = 105.86779701825405
tz = "Asia/Bangkok"  # Hanoi timezone

# === DEFINE DATE RANGE: 12 MONTHS FROM TODAY ===
start_date = pd.Timestamp.now(tz=tz).normalize()
end_date = start_date + pd.DateOffset(months=12)

times = pd.date_range(start=start_date, end=end_date, freq="30min", tz=tz)

# === SOLAR POSITION CALCULATION ===
solpos = pvlib.solarposition.get_solarposition(times, latitude, longitude)

# === PREPARE DATA ===
data = pd.DataFrame(
    {"month": times.month, "hour": times.hour, "altitude": solpos["apparent_elevation"]}
)

# Keep only above-horizon data
data = data[data["altitude"] > 0]
months = sorted(data["month"].unique())

# === AVERAGE BY MONTH & HOUR ===
monthly_avg = data.groupby(["month", "hour"]).mean().reset_index()

# === CHEERFUL, DISTINCT COLORS ===
# Using 'tab10' for vibrant, clear, non-harsh tones
cmap = plt.cm.tab10
if len(months) > 10:
    cmap = plt.cm.tab20  # fallback if more than 10 months
colors = cmap(np.linspace(0, 1, len(months)))

# === PLOT ===
plt.figure(figsize=(10, 6))

for i, month in enumerate(months):
    subset = monthly_avg[monthly_avg["month"] == month]
    plt.plot(
        subset["hour"],
        subset["altitude"],
        color=colors[i],
        linewidth=2.5,
        alpha=0.9,
        label=pd.Timestamp(2000, month, 1).strftime("%b"),
    )

# === ZEN + VIBRANT AESTHETIC ===
plt.xlabel("Hour of Day", fontsize=12)
plt.ylabel("Solar Altitude (°)", fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.grid(alpha=0.15, linestyle="--")
plt.legend(
    title="Month",
    frameon=False,
    fontsize=10,
    title_fontsize=11,
    loc="upper right",
    ncol=3,
)
plt.box(False)
plt.tight_layout()

# Gentle background
plt.gcf().patch.set_facecolor("#f9f9f6")
plt.gca().set_facecolor("#f9f9f6")

# Remove spines for minimalist look
for spine in plt.gca().spines.values():
    spine.set_visible(False)

plt.show()
