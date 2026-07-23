# Usage

## Setup

```sh
make install   # uv sync --dev
```

First planet/Moon computation downloads the Skyfield ephemeris into `data/.skyfield/` (one-time, then offline).

## Sky log (no Stellarium)

```sh
make gpx                              # sample → data/gpx/
make gpx SRC=/path/to/run.gpx         # or your file
# or: cp run.gpx data/gpx/

make sky-log
```

Open `data/sky-logs/<run-id>/sky_log.md`.

| Artifact | Contents |
|---|---|
| `sky_log.md` / `.json` | Viewpoints: facing, minute, highlight, objects |
| `data/sky-index.md` | Objects/constellations first seen across runs |

## Route learning

```sh
make profile    # needs GPX in data/gpx/
make index      # rebuild index from all sky logs
```

Per run under `data/sky-logs/<run-id>/`:

| File | Contents |
|---|---|
| `route_profile.md` | Highlights by direction of travel |
| `seasonal.md` | Same spot/direction, month by month |
| `cards/` | Constellation cards (`data/content/constellations.yaml`) |

## Tonight (pre-run)

```sh
make tonight GPX=data/gpx/your.gpx START=2026-01-15T21:30
make tonight-weather GPX=data/gpx/your.gpx START=2026-01-15T21:30
```

Outputs under `data/sky-logs/<run-id>/tonight/`:

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
