# CLAUDE.md

## Project

Four independent scripts that chart the Sun's position/daylight over a year for a fixed location (from `config.json`): azimuth/altitude plot, sun path, day-duration, and analemma.

## Entry points

- `scripts/plot-sun.py` — sun azimuth chart (`ephem`)
- `scripts/sun-path.py` — sun path chart (`pvlib`)
- `scripts/day-duration.py` — day length over the year (`pvlib`)
- `scripts/analemma.py` — analemma curve (`skyfield`, downloads ephemeris on first run)

## How to run

```bash
make run          # generate all four charts
make plot         # or run one target individually
make path
make duration
make analemma
```

Each writes a PNG to `$(DATA_DIR)` (default `~/data/sunset-sunrise-azimuth/`; override with `DATA_ROOT=` or `DATA_DIR=`).

## Conventions

- Python 3.11+, `uv` for dependency management.
- Location lives only in repo-root `config.json` (`name`, `latitude`, `longitude`, `timezone`); scripts read it at startup. No CLI args for lat/lon.
- `analemma.py` needs network on first run to fetch `de440s.bsp` unless pre-cached.
