# constellations

Project rules for agents. Global preferences still apply; this file wins on conflicts.

## What this is

Fixed-location night-sky plots: for each IAU constellation, when (if ever) it is above the horizon between astronomical dusk and dawn. Pipeline: download IAU assets → compute visibility on a time grid → write plots (with optional GIF overlay).

## Commands

```sh
make run               # full pipeline: install → download → plot
make install
make test
make download          # scripts/download.py → $DATA_DIR/{gifs,boundaries}
make plot              # clear $DATA_DIR/plots, then scripts/plot_constellations.py
make clean             # wipe $DATA_DIR/plots and .venv
make lock
```

Default `DATA_DIR` is `~/data/constellations` (see Makefile). Scripts fall back to `data/` if `DATA_DIR` is unset. Run ad-hoc Python with `uv run`.

## Architecture (do not bypass)

| Path | Role |
|---|---|
| `scripts/download.py` | Scrape IAU page; pull `.gif` + boundary `.txt` |
| `scripts/plot_constellations.py` | Observer, dusk/dawn, altitude grid, plots |
| `scripts/ra_utils.py` | RA HMS → degrees (shared, tested) |
| `data/boundaries/`, `data/gifs/`, `data/constellation_names.csv` | Checked-in IAU assets + name map used as plot inputs |
| `tests/` | Offline unittest; no network |

Plot script hardcodes observer `LAT`/`LON`/`ELEV` and `Asia/Ho_Chi_Minh`. Boundary/name inputs read from repo `data/`; plot outputs and Makefile-driven downloads go under `DATA_DIR`.

## Style / quality

- Python 3.11+, **uv**, ruff + mypy strict (`pyproject.toml`). Pre-commit runs ruff + mypy.
- Conventional Commits. Do not commit unless asked.
- Unit tests must stay offline (no live IAU fetch in tests).
- No drive-by refactors; no new deps without a clear need.
- Comments only when the *why* is non-obvious.

## Out of scope unless asked

Interactive sky atlas, multi-location UI, real-time AR, packaging as a library, committing generated plots.
