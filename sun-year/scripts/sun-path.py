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

plt.title(
    f"Solar altitude by hour • {location_name} ({latitude:.4f}°, {longitude:.4f}°)",
    fontsize=12,
    fontweight="bold",
)
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

plt.gcf().patch.set_facecolor("#f9f9f6")
plt.gca().set_facecolor("#f9f9f6")

for spine in plt.gca().spines.values():
    spine.set_visible(False)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_path = OUTPUT_DIR / "sun-path.png"
plt.savefig(out_path, dpi=150)
print(f"Saved plot to {out_path}")

peak_by_month = monthly_avg.loc[monthly_avg.groupby("month")["altitude"].idxmax()]
print("\nPeak solar altitude by month (monthly mean of half-hour samples):")
for _, row in peak_by_month.iterrows():
    label = pd.Timestamp(2000, int(row["month"]), 1).strftime("%b")
    print(f"  {label}: {row['altitude']:.1f}° around {int(row['hour']):02d}:00")
print(
    f"  Range: {peak_by_month['altitude'].max() - peak_by_month['altitude'].min():.1f}° "
    f"({peak_by_month['altitude'].min():.1f}°–{peak_by_month['altitude'].max():.1f}°)"
)
