VENV_PATH := .venv
PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

.PHONY: all art stars galaxies planets nebulae clusters exotic path timelapse test clean venv install

all: art stars galaxies planets nebulae clusters exotic path timelapse

venv:
	@uv venv $(VENV_PATH)

install: venv
	@uv pip install -q -r $(REQUIREMENTS)

art: install
	@$(PYTHON) scripts/star-art.py
stars: install
	@$(PYTHON) scripts/star-art-names.py
galaxies: install
	@$(PYTHON) scripts/star-art-galaxies.py
planets: install
	@$(PYTHON) scripts/star-art-planets.py
nebulae: install
	@$(PYTHON) scripts/star-art-nebulae.py
clusters: install
	@$(PYTHON) scripts/star-art-star-clusters.py
exotic: install
	@$(PYTHON) scripts/star-art-exotic-objects.py
path: install
	@$(PYTHON) scripts/star-art-path.py
timelapse: install
	@$(PYTHON) scripts/star-art-timelapse.py
test: install
	@$(PYTHON) -m unittest discover -s tests
clean:
	@find images -mindepth 1 ! -name '.gitignore' -exec rm -rf {} +
