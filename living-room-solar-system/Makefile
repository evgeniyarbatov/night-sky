# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

.DEFAULT_GOAL := help

run: setup
	@uv run python scripts/planets.py

setup:
	@uv sync --all-packages

lock:
	@uv lock

test: setup
	@uv run python -m pytest -q

help:
	@echo "run      - install dependencies and run scripts/planets.py"
	@echo "setup    - install dependencies via uv sync"
	@echo "lock     - refresh uv.lock"
	@echo "test     - run pytest"
