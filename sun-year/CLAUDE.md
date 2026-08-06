# CLAUDE.md

## Project

Scripts that chart the Sun's position and daylight over a year for a fixed location from `config.json`: azimuth, sun path, day duration, clock times, noon altitude, and golden hour.

## Entry points

- `scripts/plot-sun.py` — sunrise/set azimuth (`ephem`)
- `scripts/sun-path.py` — altitude by hour × month (`pvlib`)
- `scripts/day-duration.py` — day length (`pvlib`)
- `scripts/sun-times.py` — rise/set/solar-noon clock times (`pvlib`)
- `scripts/noon-altitude.py` — noon altitude + shadow (`pvlib`)
- `scripts/twilight.py` — golden-hour length 0°–6° (`ephem`)
- `scripts/location.py` — load `config.json`
- `scripts/style.py` — shared plot style

## How to run

```bash
make run          # all plots (plot path duration times noon twilight)
```

Each writes a PNG to `$(DATA_DIR)` (default `~/data/<repo-folder>/`; override with `DATA_ROOT=` or `DATA_DIR=`).

## Conventions

- Python 3.11+, `uv` for dependency management.
- Location lives only in repo-root `config.json` (`name`, `latitude`, `longitude`, `timezone`). No city names or coords in scripts; load via `location.load_location()`.
- Plots are title-free (minimal ink); site comes from config for calculations and console summaries only.
- Shared look via `style.py` (palette, axes, save helper).
