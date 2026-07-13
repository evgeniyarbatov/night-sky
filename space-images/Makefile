# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.
SHELL := /bin/bash

INPUT_DIR = $(HOME)/Downloads/Photos-1-001-16

install:
	@uv sync --dev

nasa: install
	@for i in $(shell seq 1 20); do \
		uv run python scripts/nasa.py; \
	done

planets: install
	@uv run python scripts/planets.py

clean:
	rm -rf planets/*

lock:
	@uv lock

help:
	@echo "install    - create/update .venv and install dependencies"
	@echo "nasa       - run nasa.py 20 times"
	@echo "planets    - run planets.py"
	@echo "clean      - remove generated planet images"
	@echo "lock       - refresh uv.lock"

.PHONY: nasa planets
