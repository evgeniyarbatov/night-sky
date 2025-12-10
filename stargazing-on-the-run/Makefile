VENV_PATH := .venv

PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

venv:
	@python3 -m venv $(VENV_PATH)

install: venv
	@$(PIP) install --disable-pip-version-check -q --upgrade pip
	@$(PIP) install --disable-pip-version-check -q -r $(REQUIREMENTS)

include ../[private]/gpxdata.env
export $(shell sed 's/=.*//' ../[private]/gpxdata.env)

GPX_DIR = gpx
STELLARIUM_SCRIPTS_DIR = stellarium-scripts

SCREENSHOT_DIR = ~/Downloads/stellarium
MAPS_DIR = ~/Downloads/stellarium-maps

MERGED_DIR = ~/Downloads/stellarium-with-maps

TIMEZONE = Asia/Ho_Chi_Minh

STELLARIUM_SCRIPTS := $(wildcard $(STELLARIUM_SCRIPTS_DIR)/*.ssc)

all: venv install jupyter

	pip install --disable-pip-version-check -q -r requirements.txt

jupyter: install
	@source $(VENV_PATH)/bin/activate && \
	python3 -m ipykernel install \
	--user \
	--name "$(PROJECT_NAME)" \
	--display-name "$(PROJECT_NAME)" \
	> /dev/null 2>&1

gpx:
	@mkdir -p $(GPX_DIR)

	@echo "*" > $(GPX_DIR)/.gitignore
	@echo "!.gitignore" >> $(GPX_DIR)/.gitignore

	@gdown --folder https://drive.google.com/drive/folders/$(GPX_FOLDER_ID) -O $(GPX_DIR)

scripts:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/create-scripts.py \
	$(GPX_DIR) \
	$(TIMEZONE) \
	$(STELLARIUM_SCRIPTS_DIR) \
	$(SCREENSHOT_DIR)

screenshots:
	@for file in $(STELLARIUM_SCRIPTS); do \
		script_path=$$(realpath $$file); \
		/Applications/Stellarium.app/Contents/MacOS/stellarium --startup-script $$script_path; \
	done

maps:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/make-maps.py \
	$(GPX_DIR) \
	$(TIMEZONE) \
	$(MAPS_DIR)

merge:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/merge.py \
	$(GPX_DIR) \
	$(SCREENSHOT_DIR) \
	$(MAPS_DIR) \
	$(MERGED_DIR)
	
.PHONY: venv install jupyter gpx scripts screenshots maps merge

cleanvenv:
	@rm -rf $(VENV_PATH)
