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
| `gpx.py` | Copy sample or `SRC` into `data/gpx/` |
| `create_scripts.py` | Stellarium scripts |
| `make_maps.py` / `merge.py` | Map thumbnails and composite images |

Shared sky identity: everything that answers “what was / will be there” goes through `sky.py`.

## Data layout

```text
data/gpx/              # drop zone (generated; not committed)
data/samples/          # committed sample GPX
data/content/          # constellation card YAML
data/sky-logs/<run>/   # sky_log, profile, seasonal, cards, tonight/
data/sky-index.json    # project-wide first-seen index
data/.skyfield/        # ephemeris cache (generated)
data/scripts|screenshots|maps|…  # Stellarium visual path
```

`run-id` = GPX basename. `data/*` is gitignored except `samples/` and `content/`.

## Principles (from roadmap)

- Runs are the frame — every feature ties to a real route, time, and direction.
- One thing at a time — one highlight per viewpoint.
- Offline-first — Stellarium and weather are optional.
- Wonder over trivia — short wonder lines on highlights, not dense catalogs.
