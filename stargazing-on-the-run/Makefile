VENV_PATH := .venv

PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
REQUIREMENTS := requirements.txt

GPX_SOURCE_DIR = /Users/zhenya/gitRepo/[private]/data/year/2023
NUMBER_OF_GPX = 1

DATA_DIR = data
GPX_DIR = $(DATA_DIR)/gpx
STELLARIUM_SCRIPTS_DIR = $(DATA_DIR)/scripts

SCREENSHOTS_DIR = $(DATA_DIR)/screenshots
MAPS_DIR = $(DATA_DIR)/maps
SCREENSHOTS_WITH_MAPS_DIR = $(DATA_DIR)/screenshots-with-maps

STELLARIUM_SCRIPTS := $(wildcard $(STELLARIUM_SCRIPTS_DIR)/*.ssc)
PYTHON_FILES := $(shell find scripts/ -name "*.py")

venv:
	@python3 -m venv $(VENV_PATH)

install: venv
	@$(PIP) install --disable-pip-version-check -q --upgrade pip
	@$(PIP) install --disable-pip-version-check -q -r $(REQUIREMENTS)

gpx:
	@rm -rf $(GPX_DIR)/*
	@mkdir -p $(GPX_DIR)

	@find $(GPX_SOURCE_DIR) -name "*.gpx" -type f | shuf -n $(NUMBER_OF_GPX) | xargs -I {} cp {} $(GPX_DIR)/

stellarium-scripts:
	@rm -rf $(STELLARIUM_SCRIPTS_DIR)/*
	@mkdir -p $(STELLARIUM_SCRIPTS_DIR)

	@$(PYTHON) scripts/create-scripts.py \
	$(GPX_DIR) \
	$(STELLARIUM_SCRIPTS_DIR) \
	$(SCREENSHOTS_DIR)

screenshots:
	@for file in $(STELLARIUM_SCRIPTS); do \
		script_path=$$(realpath $$file); \
		/Applications/Stellarium.app/Contents/MacOS/stellarium --startup-script $$script_path; \
	done

maps:
	@rm -rf $(MAPS_DIR)/*
	@mkdir -p $(MAPS_DIR)

	@$(PYTHON) scripts/make-maps.py \
	$(GPX_DIR) \
	$(MAPS_DIR)

merge:
	@rm -rf $(SCREENSHOTS_WITH_MAPS_DIR)/*
	@mkdir -p $(SCREENSHOTS_WITH_MAPS_DIR)

	@$(PYTHON) scripts/merge.py \
	$(GPX_DIR) \
	$(SCREENSHOTS_DIR) \
	$(MAPS_DIR) \
	$(SCREENSHOTS_WITH_MAPS_DIR)

video:
	@for dir in $(SCREENSHOTS_WITH_MAPS_DIR)/*/; do \
		if [ -n "$$(ls $$dir/*.png 2>/dev/null)" ]; then \
			subdir=$$(basename $$dir); \
			echo "Creating video for $$subdir..."; \
			ffmpeg -y \
				-framerate 1 \
				-pattern_type glob -i "$$dir/*.png" \
				-c:v libx264 \
				-pix_fmt yuv420p \
				-filter:v "setpts=3.0*PTS" \
				"$(DATA_DIR)/$$subdir.mp4"; \
			echo "Video created: $$subdir.mp4"; \
		fi; \
	done

gif:
	@for dir in $(SCREENSHOTS_WITH_MAPS_DIR)/*/; do \
		if [ -n "$$(ls $$dir/*.png 2>/dev/null)" ]; then \
			subdir=$$(basename $$dir); \
			echo "Creating GIF for $$subdir..."; \
			ffmpeg -y \
				-framerate 2 \
				-pattern_type glob -i "$$dir/*.png" \
				-filter_complex "[0:v] setpts=3.0*PTS,split [a][b];[a] palettegen [p];[b][p] paletteuse" \
				"$(DATA_DIR)/$$subdir.gif"; \
			echo "GIF created: $$subdir.gif"; \
		fi; \
	done

clean:
	@rm -rf $(DATA_DIR)/*

cleanvenv:
	@rm -rf $(VENV_PATH)