# Architecture

## Pipeline

```text
GPX
  → viewpoint selection (heading change + elev angles)
  → Skyfield identity (stars, planets, Moon, constellations)
  → intentional FOV zoom when highlight near center
  → sky_log / profile / tonight artifacts

Optional visual path:
  → Stellarium .ssc → screenshots → map overlays → merge → video
```

**Identity** is offline-first (Skyfield + curated bright-star list). **Pictures** are optional (Stellarium). Network: map tiles, first ephemeris download, optional Open-Meteo.

## Modules (`scripts/`)

| Module | Role |
|---|---|
| `utils.py` | GPX load, viewpoint selection, `Point` |
| `sky.py` | FOV catalog, highlight, zoom, wonder line |
| `bright_stars.py` | Named bright-star table (no Hipparcos download) |
| `sky_log.py` | Per-run JSON/MD sky logs |
| `sky_index.py` | Append-only personal sky index |
| `profile.py` | Route profile, seasonal rotation, constellation cards |
| `tonight.py` | Pre-run briefing, glance card, audio script, weather |
| `gpx.py` | Copy sample or `SRC` into the GPX drop zone |
| `create_scripts.py` | Stellarium scripts |
| `make_maps.py` / `merge.py` | Map thumbnails and composite images |

Shared sky identity: everything that answers “what was / will be there” goes through `sky.py`.

## Data layout

```text
data/samples/                    # committed sample GPX
data/content/                    # constellation card YAML

$(DATA_DIR)/gpx/                 # drop zone (generated)
$(DATA_DIR)/sky-logs/<run>/      # sky_log, profile, seasonal, cards, tonight/
$(DATA_DIR)/sky-index.json       # project-wide first-seen index
$(DATA_DIR)/.skyfield/           # ephemeris cache (generated)
$(DATA_DIR)/scripts|screenshots|maps|…  # Stellarium visual path
```

`run-id` = GPX basename. `DATA_DIR` defaults to `~/data/stargazing-on-the-run/` (see Makefile). Everything under `data/` in the repo is gitignored except `samples/` and `content/`.

## Principles (from roadmap)

- Runs are the frame — every feature ties to a real route, time, and direction.
- One thing at a time — one highlight per viewpoint.
- Offline-first — Stellarium and weather are optional.
- Wonder over trivia — short wonder lines on highlights, not dense catalogs.
