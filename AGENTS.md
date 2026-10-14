# AGENTS.md

Each top-level folder is an independent project. Work inside one folder; `cd <folder> && make help` lists its targets. Each folder has its own `CLAUDE.md`; read it first.

## Hub setup

- Python folders share one uv workspace: `uv sync --all-packages` at the root (or `make setup` in the folder).
- Observer location is set per folder in `config.json`.
- Generated images and data go outside the repo by default (`DATA_DIR` / `*_DIR` env vars, usually under `~/Documents/data`).

## Needs

| Tag | Meaning |
|---|---|
| `stellarium` | Stellarium rendered headlessly in Docker (`make stellarium-image` builds it) |
| `nasa` | `NASA_API_KEY` in the environment (falls back to the rate-limited demo key) |
| `gpx` | A run GPX; a committed sample is used when none is given |

## Folders

| Folder | What it does | Run | Needs |
|---|---|---|---|
| `stargazing-on-the-run` | Sky log and Stellarium renders of what I faced on night runs | `make gpx SRC=<file.gpx> sky-log`; `make run` for the full pipeline | `gpx`; render targets need `stellarium` |
| `constellations` | Nightly plots of the IAU constellations visible from one location | `make run` | network (IAU pages) |
| `sun-year` | Year-round solar charts: rise/set azimuth and times, day length, golden hour | `make run`, or `make plot` | — |
| `star-art` | Generative artworks of stars, galaxies, planets, nebulae and clusters | `make art`, or `make run` | — |
| `space-images` | Downloads NASA imagery with captions and credit | `make nasa planets` | `nasa` |
| `living-room-solar-system` | Where the planets are, projected onto the living-room walls | `make run` | — |

## Cautions

- `constellations`: `make plot` clears `$(DATA_DIR)/plots/` first.
- `sun-year` is the solar-geometry source other hubs copy (route-lab, ultra-prep, vietnam-city-lab, edge-llm); changing its maths changes their expected numbers.
