# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

DATA_ROOT ?= $(HOME)/data
REPO_NAME := $(notdir $(CURDIR))
DATA_DIR  ?= $(DATA_ROOT)/$(REPO_NAME)

.DEFAULT_GOAL := help

setup:
	@uv sync --all-packages

test: setup
	@uv run python -m unittest discover -s tests -p 'test_*.py' -v

lock:
	@uv lock

plot: setup
	@mkdir -p $(DATA_DIR)
	@DATA_DIR=$(DATA_DIR) uv run python scripts/plot-sun.py

path: setup
	@mkdir -p $(DATA_DIR)
	@DATA_DIR=$(DATA_DIR) uv run python scripts/sun-path.py

duration: setup
	@mkdir -p $(DATA_DIR)
	@DATA_DIR=$(DATA_DIR) uv run python scripts/day-duration.py

times: setup
	@mkdir -p $(DATA_DIR)
	@DATA_DIR=$(DATA_DIR) uv run python scripts/sun-times.py

noon: setup
	@mkdir -p $(DATA_DIR)
	@DATA_DIR=$(DATA_DIR) uv run python scripts/noon-altitude.py

twilight: setup
	@mkdir -p $(DATA_DIR)
	@DATA_DIR=$(DATA_DIR) uv run python scripts/twilight.py

# Entry point: generate every plot into DATA_DIR
.PHONY: setup test lock plot path duration times noon twilight run help
run: plot path duration times noon twilight

help:
	@echo "run        - generate ALL plots into \$$(DATA_DIR)"
	@echo "plot       - sunrise/set azimuth → \$$(DATA_DIR)/sun-azimuth.png"
	@echo "path       - solar altitude by hour → \$$(DATA_DIR)/sun-path.png"
	@echo "duration   - day length → \$$(DATA_DIR)/day-duration.png"
	@echo "times      - rise/set/noon clock times → \$$(DATA_DIR)/sun-times.png"
	@echo "noon       - noon altitude + shadow → \$$(DATA_DIR)/noon-altitude.png"
	@echo "twilight   - golden hour length → \$$(DATA_DIR)/twilight.png"
	@echo "setup      - uv sync (create/update .venv with all deps)"
	@echo "test       - run unit tests"
	@echo "lock       - uv lock (refresh uv.lock)"
	@echo "Default DATA_DIR: ~/data/\$$(REPO_NAME). Override: make run DATA_DIR=/tmp/run"
