# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.
DATA_ROOT ?= $(HOME)/Documents/data
REPO_NAME := $(notdir $(CURDIR))
DATA_DIR  ?= $(DATA_ROOT)/$(REPO_NAME)
IMAGES_DIR := $(DATA_DIR)/images

.PHONY: all art stars galaxies planets nebulae clusters exotic path timelapse horizon test clean install lock help

# Entry point (default goal): generate every style of star art
all: art stars galaxies planets nebulae clusters exotic path timelapse horizon

install:
	@uv sync

art: install
	@STAR_ART_IMAGES_DIR=$(IMAGES_DIR) uv run python scripts/star-art.py

stars: install
	@STAR_ART_IMAGES_DIR=$(IMAGES_DIR) uv run python scripts/star-art-names.py

galaxies: install
	@STAR_ART_IMAGES_DIR=$(IMAGES_DIR) uv run python scripts/star-art-galaxies.py

planets: install
	@STAR_ART_IMAGES_DIR=$(IMAGES_DIR) uv run python scripts/star-art-planets.py

nebulae: install
	@STAR_ART_IMAGES_DIR=$(IMAGES_DIR) uv run python scripts/star-art-nebulae.py

clusters: install
	@STAR_ART_IMAGES_DIR=$(IMAGES_DIR) uv run python scripts/star-art-star-clusters.py

exotic: install
	@STAR_ART_IMAGES_DIR=$(IMAGES_DIR) uv run python scripts/star-art-exotic-objects.py

path: install
	@STAR_ART_IMAGES_DIR=$(IMAGES_DIR) uv run python scripts/star-art-path.py

timelapse: install
	@STAR_ART_IMAGES_DIR=$(IMAGES_DIR) uv run python scripts/star-art-timelapse.py

horizon: install
	@STAR_ART_IMAGES_DIR=$(IMAGES_DIR) uv run python scripts/star-art-horizon-slice.py

test: install
	@uv run python -m unittest discover -s tests

clean:
	@rm -rf $(IMAGES_DIR)

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
	@echo "horizon    - run star-art-horizon-slice.py (dusk-to-sunrise frames per magnitude)"
	@echo "test       - run unittest suite"
	@echo "clean      - remove generated images"
	@echo "lock       - refresh uv.lock"
	@echo ""
	@echo "Images are written to \$$(DATA_DIR)/images, default: ~/Documents/data/star-art/images"
	@echo "Override with: make <target> DATA_ROOT=/path or DATA_DIR=/path"

# Entry point: full art generation pipeline.
run: all
