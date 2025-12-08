VENV_PATH := .venv

PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

venv:
	@python3 -m venv $(VENV_PATH)

install: venv
	@$(PIP) install --disable-pip-version-check -q --upgrade pip
	@$(PIP) install --disable-pip-version-check -q -r $(REQUIREMENTS)

NAME = solar-system

all: planets

	pip install --disable-pip-version-check -q -r requirements.txt

planets:	
	source $(VENV_PATH)/bin/activate && \
	python3 scripts/planets.py
