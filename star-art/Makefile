# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.
.PHONY: all art stars galaxies planets nebulae clusters exotic path timelapse test clean install lock help

all: art stars galaxies planets nebulae clusters exotic path timelapse

install:
	@uv sync

art: install
	@uv run python scripts/star-art.py

stars: install
	@uv run python scripts/star-art-names.py

galaxies: install
	@uv run python scripts/star-art-galaxies.py

planets: install
	@uv run python scripts/star-art-planets.py

nebulae: install
	@uv run python scripts/star-art-nebulae.py

clusters: install
	@uv run python scripts/star-art-star-clusters.py

exotic: install
	@uv run python scripts/star-art-exotic-objects.py

path: install
	@uv run python scripts/star-art-path.py

timelapse: install
	@uv run python scripts/star-art-timelapse.py

test: install
	@uv run python -m unittest discover -s tests

clean:
	@find images -mindepth 1 ! -name '.gitignore' -exec rm -rf {} +

lock:
	@uv lock

help:
	@echo "install    - create/update .venv and install dependencies"
	@echo "all        - run all generation targets"
	@echo "art        - run star-art.py"
	@echo "stars      - run star-art-names.py"
	@echo "galaxies   - run star-art-galaxies.py"
	@echo "planets    - run star-art-planets.py"
	@echo "nebulae    - run star-art-nebulae.py"
	@echo "clusters   - run star-art-star-clusters.py"
	@echo "exotic     - run star-art-exotic-objects.py"
	@echo "path       - run star-art-path.py"
	@echo "timelapse  - run star-art-timelapse.py"
	@echo "test       - run unittest suite"
	@echo "clean      - remove generated images"
	@echo "lock       - refresh uv.lock"
