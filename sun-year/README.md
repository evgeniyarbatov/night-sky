# sun-year

Where does the Sun rise and set throughout the year — and how does daylight shift in ways that are hard to notice day to day?

Year-round solar charts for **any location** (set once in `config.json`). Makes the year’s light readable at a glance: photography light, morning and evening runs, when the day starts to feel short.

The Sun is also the easiest astronomical object to watch — a door into the sky beyond.

## Location

**Site is only in `config.json`.** Charts never hardcode a city — change this file and re-run `make run`.

```json
{
  "name": "Saigon",
  "latitude": 10.811326766789612,
  "longitude": 106.67426954305321,
  "timezone": "Asia/Ho_Chi_Minh"
}
```

| Field | Meaning |
| --- | --- |
| `name` | Site label in console summaries |
| `latitude` | Degrees, −90…90 (south negative) |
| `longitude` | Degrees, −180…180 (west negative) |
| `timezone` | IANA name for local clock times (e.g. `Europe/Paris`, `America/New_York`) |

Example — switch to New York:

```json
{
  "name": "New York",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timezone": "America/New_York"
}
```

Then `make run`. Calculations and console summaries pick up the new site automatically.

At low latitudes day length barely moves; higher latitudes swing hard. Near the tropics the sun can be nearly overhead when declination ≈ latitude — not only at June solstice.

## Charts

| Chart | File | Question |
| --- | --- | --- |
| Sunrise / set azimuth | `sun-azimuth.png` | Where on the horizon does the Sun rise and set? (NE–SE / NW–SW; due E/W near equinoxes) |
| Sun path | `sun-path.png` | How high is the Sun by hour of day, by month? |
| Day duration | `day-duration.png` | How much does daylight length change across the year? |
| Rise / set / noon times | `sun-times.png` | When does the day start and end? (earliest sunset ≠ shortest day) |
| Noon altitude | `noon-altitude.png` | How high is the Sun at solar noon — and how long is a noon shadow? |
| Golden hour | `twilight.png` | How long is soft light (0°–6° altitude) morning and evening? |

## How to run

```bash
make run
```

Builds **all** plots (the six charts above) as PNGs under `~/data/<repo-folder>/` by default — no GUI window. Override output with `DATA_ROOT=` or `DATA_DIR=`.

```bash
make run DATA_DIR=/tmp/sun-year
```

Python 3.11+, managed with `uv` (`make install` if you only want the venv).

Single chart (optional):

```bash
make plot         # sun-azimuth.png
make path         # sun-path.png
make duration     # day-duration.png
make times        # sun-times.png
make noon         # noon-altitude.png
make twilight     # twilight.png
make help
```
