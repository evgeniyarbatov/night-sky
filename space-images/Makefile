# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.
DATA_ROOT ?= $(HOME)/data
REPO_NAME := $(notdir $(CURDIR))
DATA_DIR  ?= $(DATA_ROOT)/$(REPO_NAME)

SHELL := /bin/bash

install:
	@uv sync --dev

nasa: install
	@mkdir -p $(DATA_DIR)/images
	@for i in $(shell seq 1 20); do \
		uv run python scripts/nasa.py --output-dir $(DATA_DIR)/images; \
	done

planets: install
	@mkdir -p $(DATA_DIR)/images
	@uv run python scripts/planets.py --output-dir $(DATA_DIR)/images

inspire: install
	@mkdir -p $(DATA_DIR)
	@uv run python scripts/inspire.py --root $(DATA_DIR)

test: install
	@PYTHONPATH=scripts uv run python -m unittest discover -s tests -p 'test_*.py' -v

clean:
	rm -rf $(DATA_DIR)/images $(DATA_DIR)/planets $(DATA_DIR)/album

lock:
	@uv lock

help:
	@echo "install    - create/update .venv and install dependencies"
	@echo "inspire    - APOD → $(DATA_DIR)/album/daily (adds a new photo each run)"
	@echo "nasa       - run nasa.py 20 times → $(DATA_DIR)/images"
	@echo "planets    - run planets.py → $(DATA_DIR)/images/<planet>"
	@echo "test       - run unit tests"
	@echo "clean      - remove generated downloads"
	@echo "lock       - refresh uv.lock"
	@echo ""
	@echo "DATA_DIR=$(DATA_DIR) (override with DATA_ROOT=... or DATA_DIR=...)"

.PHONY: install nasa planets inspire test clean lock help

# Entry point: fetch all image sets.
run: nasa planets inspire
