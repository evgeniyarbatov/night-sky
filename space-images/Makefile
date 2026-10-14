# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.
DATA_ROOT ?= $(HOME)/Documents/data
REPO_NAME := $(notdir $(CURDIR))
DATA_DIR  ?= $(DATA_ROOT)/$(REPO_NAME)

SHELL := /bin/bash

.DEFAULT_GOAL := help

setup:
	@uv sync --all-packages

nasa: setup
	@mkdir -p $(DATA_DIR)/images
	@for i in $(shell seq 1 20); do \
		uv run python scripts/nasa.py --output-dir $(DATA_DIR)/images; \
	done

planets: setup
	@mkdir -p $(DATA_DIR)/images
	@uv run python scripts/planets.py --output-dir $(DATA_DIR)/images

stars: setup
	@uv run python scripts/stars.py --output-dir $(DATA_DIR)/images/stars

inspire: setup
	@mkdir -p $(DATA_DIR)
	@uv run python scripts/inspire.py --root $(DATA_DIR)

test: setup
	@PYTHONPATH=scripts uv run python -m unittest discover -s tests -p 'test_*.py' -v

lock:
	@uv lock

help:
	@echo "run        - fetch all image sets"
	@echo "setup      - create/update .venv and install dependencies"
	@echo "inspire    - APOD → $(DATA_DIR)/album/daily (adds a new photo each run)"
	@echo "nasa       - run nasa.py 20 times → $(DATA_DIR)/images"
	@echo "planets    - run planets.py → $(DATA_DIR)/images/<planet>"
	@echo "stars      - run stars.py → $(DATA_DIR)/images/stars (nebulae, galaxies, clusters)"
	@echo "test       - run unit tests"
	@echo "lock       - refresh uv.lock"
	@echo ""
	@echo "DATA_DIR=$(DATA_DIR) (override with DATA_ROOT=... or DATA_DIR=...)"

.PHONY: setup nasa planets inspire test lock help

# Entry point: fetch all image sets.
run: nasa planets inspire
