# Usage

## Setup

```sh
make install   # uv sync --dev
```

First planet/Moon computation downloads the Skyfield ephemeris into `$(DATA_DIR)/.skyfield/` (one-time, then offline).

## Generated data location

All generated artifacts (GPX drop zone, sky logs, screenshots, maps, videos, sky index)
are written under `DATA_DIR`, which defaults to `~/data/stargazing-on-the-run/`.

```sh
make <target> DATA_ROOT=/path/to/shared   # changes the parent dir
make <target> DATA_DIR=/tmp/run-42        # changes the full path
```

The committed sample GPX (`data/samples/sample_night_run.gpx`) and constellation
content (`data/content/`) stay in the repo and are unaffected by `DATA_DIR`.

## Sky log (no Stellarium)

```sh
make gpx                              # sample → $(DATA_DIR)/gpx/
make gpx SRC=/path/to/run.gpx         # or your file

make sky-log
```

Open `$(DATA_DIR)/sky-logs/<run-id>/sky_log.md`.

| Artifact | Contents |
|---|---|
| `sky_log.md` / `.json` | Viewpoints: facing, minute, highlight, objects |
| `$(DATA_DIR)/sky-index.md` | Objects/constellations first seen across runs |

## Route learning

```sh
make profile    # needs GPX in $(DATA_DIR)/gpx/
make index      # rebuild index from all sky logs
```

Per run under `$(DATA_DIR)/sky-logs/<run-id>/`:

| File | Contents |
|---|---|
| `route_profile.md` | Highlights by direction of travel |
| `seasonal.md` | Same spot/direction, month by month |
| `cards/` | Constellation cards (`data/content/constellations.yaml`) |

## Tonight (pre-run)

```sh
make tonight GPX=$(DATA_DIR)/gpx/your.gpx START=2026-01-15T21:30
make tonight-weather GPX=$(DATA_DIR)/gpx/your.gpx START=2026-01-15T21:30
```

Outputs under `$(DATA_DIR)/sky-logs/<run-id>/tonight/`:

| File | Contents |
|---|---|
| `glance_card.md` | Phone/print: moon, planets, 1–3 look-fors by km |
| `tonight_script.md` | Speakable ~5 minute briefing |
| `tonight.json` | Machine-readable |

## Visual pipeline (optional)

Needs Stellarium (macOS path in Makefile) and ffmpeg for video.

```sh
make all     # sky-log + scripts + screenshots + maps + merge
make video
```

Steps: `stellarium-scripts` → `screenshots` → `maps` → `merge` → `video`.

## Make targets

| Target | What it does |
|---|---|
| `make demo` | Sample GPX → sky-log → profile |
| `make sky-log` | Sky logs + personal index |
| `make profile` | Route profile, seasons, cards |
| `make index` | Rebuild personal sky index |
| `make tonight GPX=… START=…` | Pre-run briefing |
| `make tonight-weather …` | Briefing + Open-Meteo cloud cover |
| `make all` | Sky log + Stellarium visual chain |
| `make test` | Pytest |
| `make clean` | Generated outputs (keeps samples/content) |
