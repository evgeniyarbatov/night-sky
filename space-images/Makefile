# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.
SHELL := /bin/bash

install:
	@uv sync --dev

nasa: install
	@for i in $(shell seq 1 20); do \
		uv run python scripts/nasa.py; \
	done

planets: install
	@uv run python scripts/planets.py

inspire: install
	@uv run python scripts/inspire.py

clean:
	rm -rf planets/* images/*
	@find album/daily -mindepth 1 ! -name '.gitkeep' -exec rm -rf {} + 2>/dev/null || true

lock:
	@uv lock

help:
	@echo "install    - create/update .venv and install dependencies"
	@echo "inspire    - APOD → album/daily (adds a new photo each run)"
	@echo "nasa       - run nasa.py 20 times → images/"
	@echo "planets    - run planets.py → planets/"
	@echo "clean      - remove generated downloads"
	@echo "lock       - refresh uv.lock"

.PHONY: install nasa planets inspire clean lock help
