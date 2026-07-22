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

test: install
	@PYTHONPATH=scripts uv run python -m unittest discover -s tests -p 'test_*.py' -v

clean:
	rm -rf images/* planets/*

lock:
	@uv lock

help:
	@echo "install    - create/update .venv and install dependencies"
	@echo "inspire    - APOD → album/daily (adds a new photo each run)"
	@echo "nasa       - run nasa.py 20 times → images/"
	@echo "planets    - run planets.py → images/<planet>/"
	@echo "test       - run unit tests"
	@echo "clean      - remove generated downloads"
	@echo "lock       - refresh uv.lock"

.PHONY: install nasa planets inspire test clean lock help
