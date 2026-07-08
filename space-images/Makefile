SHELL := /bin/bash

VENV_PATH := .venv

PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

INPUT_DIR = $(HOME)/Downloads/Photos-1-001-16

venv:
	@uv venv $(VENV_PATH)

install: venv
	@uv pip install -q -r $(REQUIREMENTS)

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
	@rm -rf $(VENV_PATH)
