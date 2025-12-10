SHELL := /bin/bash

VENV_PATH := .venv

PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

INPUT_DIR = /Users/zhenya/Downloads/Photos-1-001-16

venv:
	@python3 -m venv $(VENV_PATH)

install: venv
	@$(PIP) install --disable-pip-version-check -q --upgrade pip
	@$(PIP) install --disable-pip-version-check -q -r $(REQUIREMENTS)

nasa:
	@for i in $(shell seq 1 20); do \
		$(PYTHON) scripts/nasa.py; \
	done

planets:
	@$(PYTHON) scripts/planets.py

clean:
	rm -rf planets/*

.PHONY: nasa planets

cleanvenv:
	@rm -rf .venv
