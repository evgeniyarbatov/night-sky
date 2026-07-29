# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

DATA_ROOT ?= $(HOME)/data
REPO_NAME := $(notdir $(CURDIR))
DATA_DIR  ?= $(DATA_ROOT)/$(REPO_NAME)

install:
	@uv sync

test: install
	@uv run python -m unittest discover -s tests -p 'test_*.py' -v

lock:
	@uv lock

plot: install
	@uv run python scripts/plot-sun.py

path: install
	@uv run python scripts/sun-path.py

duration: install
	@uv run python scripts/day-duration.py

analemma: install
	@uv run python scripts/analemma.py

help:
	@echo "install    - uv sync (create/update .venv with all deps)"
	@echo "test       - run unit tests"
	@echo "lock       - uv lock (refresh uv.lock)"
	@echo "plot       - run scripts/plot-sun.py"
	@echo "path       - run scripts/sun-path.py"
	@echo "duration   - run scripts/day-duration.py"
	@echo "analemma   - run scripts/analemma.py"
