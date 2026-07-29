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
	@mkdir -p $(DATA_DIR)
	@DATA_DIR=$(DATA_DIR) uv run python scripts/plot-sun.py

path: install
	@mkdir -p $(DATA_DIR)
	@DATA_DIR=$(DATA_DIR) uv run python scripts/sun-path.py

duration: install
	@mkdir -p $(DATA_DIR)
	@DATA_DIR=$(DATA_DIR) uv run python scripts/day-duration.py

analemma: install
	@mkdir -p $(DATA_DIR)
	@DATA_DIR=$(DATA_DIR) uv run python scripts/analemma.py

help:
	@echo "install    - uv sync (create/update .venv with all deps)"
	@echo "test       - run unit tests"
	@echo "lock       - uv lock (refresh uv.lock)"
	@echo "plot       - save scripts/plot-sun.py output to \$$(DATA_DIR)/sun-azimuth.png"
	@echo "path       - save scripts/sun-path.py output to \$$(DATA_DIR)/sun-path.png"
	@echo "duration   - save scripts/day-duration.py output to \$$(DATA_DIR)/day-duration.png"
	@echo "analemma   - save scripts/analemma.py output to \$$(DATA_DIR)/analemma.png"
	@echo "Default DATA_DIR: ~/data/sunset-sunrise-azimuth. Override: make plot DATA_DIR=/tmp/run"
