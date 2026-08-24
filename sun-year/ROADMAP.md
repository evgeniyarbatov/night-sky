# Roadmap

Started as one-off sun-position scripts (analemma, day duration) for a hardcoded city, then consolidated into a single `config.json`-driven location, a shared plot style, and six standing charts (azimuth, sun path, day duration, times, noon altitude, twilight). Recent commits were about making it runnable anywhere (config-driven location, `DATA_DIR` output) rather than adding new charts.

## Near-term

- Restore test coverage — the analemma tests were dropped along with the analemma chart, leaving the six current charts untested.
- Add a CI workflow (ruff/mypy/pytest on push) — every other repo in this cluster ([private], etc.) has one, this one doesn't.
