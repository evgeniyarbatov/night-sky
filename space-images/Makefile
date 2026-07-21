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
	@uv run python scripts/inspire.py $(if $(SELECT),--select,)

select: install
	@test -n "$(IMAGE)" || (echo "Usage: make select IMAGE=path/to/image.jpg" >&2; exit 2)
	@uv run python scripts/select.py "$(IMAGE)"

album: install
	@uv run python scripts/select.py --list

clean:
	rm -rf planets/* images/*
	@find album/daily album/selected -mindepth 1 ! -name '.gitkeep' -exec rm -rf {} + 2>/dev/null || true

lock:
	@uv lock

help:
	@echo "install    - create/update .venv and install dependencies"
	@echo "inspire    - daily APOD → album/daily (set SELECT=1 to also select)"
	@echo "nasa       - run nasa.py 20 times → images/"
	@echo "planets    - run planets.py → planets/"
	@echo "select     - copy IMAGE into album/selected (IMAGE=path required)"
	@echo "album      - list album/selected"
	@echo "clean      - remove generated downloads"
	@echo "lock       - refresh uv.lock"

.PHONY: install nasa planets inspire select album clean lock help
