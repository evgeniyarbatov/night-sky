# sunset-sunrise-azimuth

Where does the Sun rise and set throughout the year — and how does daylight shift in ways that are hard to notice day to day?

Charts for a fixed site (see `config.json`; currently Saigon) that make the year’s light readable at a glance: photography light, morning and evening runs, when the day starts to feel short.

The Sun is also the easiest astronomical object to watch — a door into the sky beyond.

## Location

Edit `config.json` at the repo root:

```json
{
  "name": "Saigon",
  "latitude": 10.811326766789612,
  "longitude": 106.67426954305321,
  "timezone": "Asia/Ho_Chi_Minh"
}
```

Near 11°N, day length barely moves compared with higher latitudes; azimuth swing and solar altitude still mark the seasons clearly.

## Charts

| Chart | File | Question |
| --- | --- | --- |
| Sunrise / set azimuth | `sun-azimuth.png` | Where on the horizon does the Sun rise and set across the year? (NE–SE / NW–SW; due E/W near equinoxes) |
| Sun path | `sun-path.png` | How high is the Sun by hour of day, by month? |
| Day duration | `day-duration.png` | How much does daylight length change month to month? |
| Analemma | `analemma.png` | At a fixed clock time, where is the Sun on the sky over a year? (figure‑8 from axial tilt + orbital eccentricity) |

## How to run

```bash
make run          # all four charts
make plot         # sun-azimuth
make path         # sun-path
make duration     # day-duration
make analemma     # analemma
make help
```

Python 3.11+, managed with `uv`. PNGs go to `~/data/sunset-sunrise-azimuth/` by default (no GUI). Override with `DATA_ROOT=` or `DATA_DIR=`.

`analemma` needs network on first run to fetch a JPL ephemeris (or use a pre-cached `.bsp`).
