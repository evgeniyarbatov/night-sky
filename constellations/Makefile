# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

install:
	@uv sync --dev

test: install
	@uv run python -m unittest discover -s tests -p 'test_*.py' -v

download: install
	@uv run python scripts/download.py

plot: install clean
	@uv run python scripts/plot_constellations.py

clean:
	@rm -rf data/plots/*
	@rm -rf .venv

lock:
	@uv lock

help:
	@echo "install    - create/update .venv and install dependencies"
	@echo "test       - run offline unit tests (tests/test_*.py)"
	@echo "download   - run scripts/download.py"
	@echo "plot       - clean and run scripts/plot_constellations.py"
	@echo "clean      - remove generated plots and .venv"
	@echo "lock       - refresh uv.lock"
