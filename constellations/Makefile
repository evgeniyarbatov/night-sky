# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

install:
	@uv sync --dev

download: install
	@uv run python scripts/download.py

plot: install clean
	@uv run python scripts/plot_constellations.py

clean:
	@rm -rf data/plots/*
	@rm -rf .venv

cleanvenv:
	@rm -rf .venv

lock:
	@uv lock

help:
	@echo "install    - create/update .venv and install dependencies"
	@echo "download   - run scripts/download.py"
	@echo "plot       - clean and run scripts/plot_constellations.py"
	@echo "clean      - remove generated plots and .venv"
	@echo "cleanvenv  - remove .venv"
	@echo "lock       - refresh uv.lock"
