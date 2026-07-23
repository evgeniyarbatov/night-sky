# Stargazing on the Run

Project rules for agents. Global preferences still apply; this file adds repo-specific facts.

## What this is

GPX → sky identity (Skyfield) → per-run logs / route learning / tonight briefings. Optional Stellarium path for screenshots and video. Goal: know the night sky as well as the streets you run. See [ROADMAP.md](ROADMAP.md).

## Commands

```sh
make install          # uv sync --dev
make demo             # sample → sky-log → profile
make sky-log          # identity logs + index (no Stellarium)
make profile          # route profile, seasons, cards
make tonight GPX=… START=YYYY-MM-DDTHH:MM
make test
make clean            # generated data only; keeps samples/content
```

Use `uv run` for ad-hoc Python. Do not invent personal GPX paths; drop files in `data/gpx/` or `make gpx SRC=…`.

## Architecture (do not bypass)

- **Identity** = `scripts/sky.py` (stars, planets, Moon, FOV, highlight, zoom). Shared by sky-log, profile, tonight.
- **Viewpoints** = `scripts/utils.py` (`load_points`, heading filter, elev angles).
- **FOV zoom** is intentional (highlight near center), not random.
- **Stellarium** is pictures only; sky logs must work without it.
- **Ephemeris** caches under `data/.skyfield/`. First planet/Moon run needs network once.

Hops and data layout: [docs/architecture.md](docs/architecture.md). User-facing usage: [docs/usage.md](docs/usage.md).

## When changing sky behavior

- Edit `sky.py` / `bright_stars.py` once; all consumers follow.
- Keep `Point.time` as civil local at lat/lon; `local_to_skyfield_time` converts for astronomy.
- Unit tests must not hit Open-Meteo live; inject weather fetcher or omit `--weather`.
- Prefer fixtures under `data/samples/`; do not commit personal GPX.

## Style / quality

- Python 3.11+, `uv`, ruff + mypy strict (see `pyproject.toml`).
- Conventional commits. No hardcoded home-directory paths.
- Docs: current-state only; user docs in `docs/`, agent rules here, not mixed into README.
- Content pack for constellation cards: `data/content/constellations.yaml` (hand-written, not scraped fluff).

## Out of scope unless asked

Real-time AR, full Skyfield renderer replacing Stellarium, web app, multi-culture sky lore beyond the content pack, light-pollution map tiles.
