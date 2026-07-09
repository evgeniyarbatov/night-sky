# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.
VENV_PATH := .venv

default: planets

install:
	@uv sync --dev

lock:
	@uv lock

planets: install
	@uv run python planets.py

test: install
	@uv run python -m pytest -q

clean:
	@rm -rf $(VENV_PATH)

help:
	@echo "install  - install dependencies via uv sync"
	@echo "lock     - refresh uv.lock"
	@echo "planets  - run planets.py"
	@echo "test     - run pytest"
	@echo "clean    - remove .venv"
