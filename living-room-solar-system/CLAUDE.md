# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- `make run` — install dependencies (via `uv sync --dev`) and run `scripts/planets.py`.
- `make test` — install dependencies and run the full test suite (`pytest -q`).
- `uv run python -m pytest tests/test_planets.py::test_load_settings_success` — run a single test.
- `make lock` — refresh `uv.lock` after changing dependencies in `pyproject.toml`.
- `make clean` — remove `.venv`.
- Pre-commit hooks (ruff lint/format, mypy --strict, trailing-whitespace, etc.) are configured in `.pre-commit-config.yaml`.

## Architecture

`scripts/planets.py` is a single-file, interactive CLI script with three phases:

1. **Settings** — `load_settings()` reads `config.json` (repo root, path resolved relative to the script location so it works regardless of cwd) into a frozen `Settings` dataclass: location (`city_name`, `country`, `latitude`, `longitude`, `timezone`), `elevation_m`, and `sample_interval_minutes`. All fields are required; missing/invalid values raise `ValueError` with a message naming the offending key.
2. **Astronomy** — Skyfield (`de421.bsp` ephemeris, loaded from the repo root) computes planet altitude/azimuth at fixed intervals between tonight's sunset and tomorrow's sunrise (sunset/sunrise from Astral, using the configured location/timezone). Results per planet are reduced to a `VisibilitySummary` (visible if average altitude > 0, with average alt/az and rise/set times).
3. **Wall projection** — visible planets are grouped by azimuth (rounded to 15°) into compass directions. The script prompts interactively for a measured wall distance per direction group, then converts each planet's altitude into a projected wall height (cm) via `compute_wall_projection_height` (simple `tan(altitude) * distance`).

`main()` wires these phases together and drives the interactive prompts/output; the rest of the module is pure functions covered by `tests/test_planets.py`. `tests/conftest.py` adds `scripts/` to `sys.path` so tests can `import planets` directly.
