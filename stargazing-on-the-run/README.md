# Stargazing on the Run

> Know the night sky as well as you know the streets you run.

Night runs put you under an open sky. This project turns a GPX trace into a **sky log** of what you faced — bright stars, planets, Moon, constellations — so the sky above your routes becomes as familiar as the streets.

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11+.

```sh
make demo
# → ~/data/stargazing-on-the-run/sky-logs/sample_night_run/sky_log.md
```

```sh
make gpx SRC=/path/to/your-run.gpx
make sky-log
```

Generated data (sky logs, screenshots, maps, videos) is written under `~/data/stargazing-on-the-run/` by default. Override with `DATA_ROOT=` (changes the parent) or `DATA_DIR=` (changes the full path) on any `make` invocation.

| Docs | |
|---|---|
| [Usage](docs/usage.md) | Make targets, own runs, tonight briefing, route profile |
| [Architecture](docs/architecture.md) | Pipeline hops, modules, data layout |
| [Roadmap](ROADMAP.md) | Phases and north star |
