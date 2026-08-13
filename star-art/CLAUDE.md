# CLAUDE.md

## Project

Generates minimalist star-field artwork (PNG) from real astronomical data — star positions, named stars, galaxies, planets, nebulae, clusters, exotic objects, and time-lapses — for each location in `stargazing-locations.json`, at that location's astronomical dusk on the current UTC date.

## Entry points

- `scripts/star-art.py` — base star-field render (default `make all` step)
- `scripts/star-art-{names,galaxies,planets,nebulae,star-clusters,exotic-objects,path,timelapse}.py` — one render style each
- `scripts/star_art_utils.py` — shared projection/rendering helpers, imported by all the above

## How to run

```bash
make install
make            # or `make all` — runs every style
make art        # or any single style target (stars, galaxies, planets, ...)
```

Images are written to `$(DATA_DIR)/images` (default `~/Documents/data/star-art/images`); override with `DATA_ROOT=` or `DATA_DIR=`.

## Conventions

- Python 3.11+, `uv` for dependency management.
- Uses the Hipparcos catalog via Skyfield; filters stars by a magnitude threshold.
- Stereographic projection centered at azimuth 0deg / altitude 90deg, 180deg field of view.
- `data/star_names.csv` maps catalog entries to display names; `stargazing-locations.json` is the list of locations rendered.
