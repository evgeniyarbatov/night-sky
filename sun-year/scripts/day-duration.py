import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pvlib

OUTPUT_DIR = Path(os.environ.get("DATA_DIR", "data"))
REPO_ROOT = Path(__file__).resolve().parent.parent

with open(REPO_ROOT / "config.json") as f:
    _cfg = json.load(f)
location_name = _cfg["name"]
latitude = _cfg["latitude"]
longitude = _cfg["longitude"]
tz = _cfg["timezone"]

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

plt.title(
    f"Daylight duration • {location_name} ({latitude:.4f}°, {longitude:.4f}°)",
    fontsize=12,
    fontweight="bold",
)
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

plt.gcf().patch.set_facecolor("#f9f9f6")
plt.gca().set_facecolor("#f9f9f6")

for spine in plt.gca().spines.values():
    spine.set_visible(False)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_path = OUTPUT_DIR / "day-duration.png"
plt.savefig(out_path, dpi=150)
print(f"Saved plot to {out_path}")

daily_min_idx = df["day_length"].idxmin()
daily_max_idx = df["day_length"].idxmax()
shortest = df.loc[daily_min_idx]
longest = df.loc[daily_max_idx]
print("\nDaylight summary (daily rise–set):")
print(
    f"  Shortest: {shortest['day_length']:.2f} h on {shortest['date'].strftime('%Y-%m-%d')}"
)
print(f"  Longest:  {longest['day_length']:.2f} h on {longest['date'].strftime('%Y-%m-%d')}")
print(f"  Range:    {longest['day_length'] - shortest['day_length']:.2f} h")
print(
    f"  Monthly means: {monthly_avg['day_length'].min():.2f}–"
    f"{monthly_avg['day_length'].max():.2f} h"
)
