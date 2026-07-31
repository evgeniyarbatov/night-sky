# Living Room Solar System

This repo contains a script that calculates which planets are visible from a
location between sunset and sunrise, then helps you map those planets onto a wall
by converting sky positions into wall projection heights.

## What the script does

`scripts/planets.py`:
- Uses Skyfield + an ephemeris file (`de421.bsp`) to compute planet positions.
- Uses Astral to find sunset (today) and sunrise (tomorrow) for the configured
  location and time zone.
- Samples the night sky at a fixed interval and determines which planets are
  above the horizon.
- Prints average altitude/azimuth and visibility window per visible planet.
- Groups visible planets by direction and prompts you for wall distances in those
  directions.
- Converts each planet's average altitude into a wall height (cm) using the
  measured wall distance.

## Setup

```bash
make install
```

This creates a `.venv` and installs dependencies.

## Configure your location

Edit `config.json` in the repo root:

```json
{
  "city_name": "Ho Chi Minh",
  "country": "Vietnam",
  "latitude": 10.811487948774618,
  "longitude": 106.6741415742141,
  "timezone": "Asia/Ho_Chi_Minh",
  "sample_interval_minutes": 10,
  "elevation_m": 5
}
```

All values are required. The script loads these settings at runtime.

## Run

```bash
make run
```

The script is interactive. After it prints visible planets, it will prompt for
wall distances (in centimeters) for each direction group.

## Tests

```bash
make test
```

## Notes

- All calculations are based on average altitude/azimuth during the night window.
  If you need higher precision, reduce `sample_interval_minutes`.
