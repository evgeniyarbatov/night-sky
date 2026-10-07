# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.
VENV_PATH := .venv

default: run

run: install
	@uv run python scripts/planets.py

install:
	@uv sync --dev

lock:
	@uv lock

test: install
	@uv run python -m pytest -q

clean:
	@rm -rf $(VENV_PATH)

help:
	@echo "run      - install dependencies and run scripts/planets.py"
	@echo "install  - install dependencies via uv sync"
	@echo "lock     - refresh uv.lock"
	@echo "test     - run pytest"
	@echo "clean    - remove .venv"
