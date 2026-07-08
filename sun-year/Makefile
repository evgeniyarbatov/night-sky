VENV_PATH := .venv

PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

venv:
	@uv venv $(VENV_PATH)

install: venv
	@uv pip install -q -r $(REQUIREMENTS)

plot:
	@$(PYTHON) scripts/plot-sun.py

path:
	@$(PYTHON) scripts/sun-path.py

duration:
	@$(PYTHON) scripts/day-duration.py

analemma:
	@$(PYTHON) scripts/analemma.py

cleanvenv:
	@rm -rf $(VENV_PATH)
