# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

DATA_ROOT ?= $(HOME)/Documents/data
REPO_NAME := $(notdir $(CURDIR))
DATA_DIR  ?= $(DATA_ROOT)/$(REPO_NAME)

.DEFAULT_GOAL := help

setup:
	@uv sync --all-packages

test: setup
	@uv run python -m unittest discover -s tests -p 'test_*.py' -v

download: setup
	@DATA_DIR=$(DATA_DIR) uv run python scripts/download.py

plot: setup
	@rm -rf $(DATA_DIR)/plots/*
	@DATA_DIR=$(DATA_DIR) uv run python scripts/plot_constellations.py

run: download plot

lock:
	@uv lock

help:
	@echo "setup      - create/update .venv and install dependencies"
	@echo "test       - run offline unit tests (tests/test_*.py)"
	@echo "download   - run scripts/download.py"
	@echo "plot       - clear plots and run scripts/plot_constellations.py"
	@echo "run        - full pipeline: install → download → plot"
	@echo "lock       - refresh uv.lock"
