# Stargazing on the Run

![1737127230-compressed](https://github.com/user-attachments/assets/5209ebf3-4b8f-4c3a-b490-00d58c3bd279)

> Know the night sky as well as you know the streets you run.

Night runs put you under an open sky. This project turns a GPX trace into a **sky log** of what you faced — bright stars, planets, Moon, constellations — so the sky above your routes becomes as familiar as the streets.

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11+.

```sh
make demo
# → data/sky-logs/sample_night_run/sky_log.md
```

```sh
cp /path/to/your-run.gpx data/gpx/
make sky-log
```

| Docs | |
|---|---|
| [Usage](docs/usage.md) | Make targets, own runs, tonight briefing, route profile |
| [Architecture](docs/architecture.md) | Pipeline hops, modules, data layout |
| [Roadmap](ROADMAP.md) | Phases and north star |
