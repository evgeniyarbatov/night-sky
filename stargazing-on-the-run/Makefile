# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

DATA_ROOT ?= $(HOME)/Documents/data
REPO_NAME := $(notdir $(CURDIR))
DATA_DIR  ?= $(DATA_ROOT)/$(REPO_NAME)
export DATA_DIR

GPX_DIR ?= $(DATA_DIR)/gpx
SKY_LOGS_DIR ?= $(DATA_DIR)/sky-logs
SCRIPTS_DIR ?= $(DATA_DIR)/scripts
SCREENSHOTS_DIR ?= $(DATA_DIR)/screenshots
MAPS_DIR ?= $(DATA_DIR)/maps
MERGED_DIR ?= $(DATA_DIR)/screenshots-with-maps
SKY_INDEX_JSON ?= $(DATA_DIR)/sky-index.json
SRC ?=
START ?=
GPX ?=

install:
	@uv sync --dev

# Copy a GPX into $(GPX_DIR). Default: committed sample (data/samples/). Override: make gpx SRC=/path/to/file.gpx
gpx: install
	@if [ -n "$(SRC)" ]; then \
		uv run python scripts/gpx.py "$(SRC)" --clear --dest $(GPX_DIR); \
	else \
		uv run python scripts/gpx.py --clear --dest $(GPX_DIR); \
	fi

# Sky identity logs (no Stellarium required)
sky-log: install
	@uv run python -m scripts.sky_log $(GPX_DIR) $(SKY_LOGS_DIR)
	@uv run python -m scripts.sky_index --sky-logs $(SKY_LOGS_DIR) --out $(SKY_INDEX_JSON)

stellarium-scripts: install
	@uv run python -m scripts.create_scripts \
	$(GPX_DIR) \
	$(SCRIPTS_DIR) \
	$(SCREENSHOTS_DIR)

screenshots:
	@for file in $(SCRIPTS_DIR)/*.ssc; do \
		script_path=$$(realpath $$file); \
		/Applications/Stellarium.app/Contents/MacOS/stellarium --startup-script $$script_path; \
	done

maps: install
	@uv run python -m scripts.make_maps \
	$(GPX_DIR) \
	$(MAPS_DIR)

merge: install
	@uv run python scripts/merge.py \
	$(GPX_DIR) \
	$(SCREENSHOTS_DIR) \
	$(MAPS_DIR) \
	$(MERGED_DIR)

video:
	@for dir in $(MERGED_DIR)/*/; do \
		if [ -n "$$(ls $$dir/*.png 2>/dev/null)" ]; then \
			subdir=$$(basename $$dir); \
			echo "Creating video for $$subdir..."; \
			ffmpeg -y \
				-framerate 2 \
				-pattern_type glob -i "$$dir/*.png" \
				-c:v libx264 \
				-pix_fmt yuv420p \
				-filter:v "setpts=3.0*PTS" \
				"$(DATA_DIR)/$$subdir.mp4"; \
			echo "Video created: $$subdir.mp4"; \
		fi; \
	done

# Route profile, seasonal rotation, constellation cards
profile: install
	@uv run python -m scripts.profile --gpx-dir $(GPX_DIR) --out $(SKY_LOGS_DIR) --also-sky-log
	@uv run python -m scripts.sky_index --sky-logs $(SKY_LOGS_DIR) --out $(SKY_INDEX_JSON)

# Rebuild personal sky index only
index: install
	@uv run python -m scripts.sky_index --sky-logs $(SKY_LOGS_DIR) --out $(SKY_INDEX_JSON)

# Pre-run briefing. Example: make tonight GPX=$(DATA_DIR)/gpx/sample_night_run.gpx START=2026-07-24T21:30
tonight: install
	@if [ -z "$(GPX)" ] || [ -z "$(START)" ]; then \
		echo "Usage: make tonight GPX=$(GPX_DIR)/your.gpx START=YYYY-MM-DDTHH:MM"; \
		exit 1; \
	fi
	@uv run python -m scripts.tonight --gpx "$(GPX)" --start "$(START)" --sky-logs-dir $(SKY_LOGS_DIR)

tonight-weather: install
	@if [ -z "$(GPX)" ] || [ -z "$(START)" ]; then \
		echo "Usage: make tonight-weather GPX=$(GPX_DIR)/your.gpx START=YYYY-MM-DDTHH:MM"; \
		exit 1; \
	fi
	@uv run python -m scripts.tonight --gpx "$(GPX)" --start "$(START)" --weather --sky-logs-dir $(SKY_LOGS_DIR)

# Full visual pipeline (requires Stellarium on macOS for screenshots)
all: sky-log stellarium-scripts screenshots maps merge

demo: install
	@$(MAKE) gpx
	@$(MAKE) sky-log
	@$(MAKE) profile
	@echo ""
	@echo "Open $(SKY_LOGS_DIR)/sample_night_run/sky_log.md"

test: install
	@uv run python -m pytest

clean:
	@rm -rf $(DATA_DIR)

lock:
	@uv lock

help:
	@echo "Generated data goes under DATA_DIR (default: $(DATA_DIR))"
	@echo "Override with DATA_ROOT=... or DATA_DIR=..."
	@echo ""
	@echo "install              - create/update .venv and install dependencies"
	@echo "gpx                  - copy sample (or SRC=...) into \$$(GPX_DIR)/"
	@echo "sky-log              - Skyfield sky logs + personal index (no Stellarium)"
	@echo "profile              - route profile, seasonal rotation, constellation cards"
	@echo "index                - rebuild personal sky index from sky-logs"
	@echo "tonight              - pre-run briefing (GPX=... START=...)"
	@echo "tonight-weather      - tonight + Open-Meteo cloud cover"
	@echo "stellarium-scripts   - create Stellarium scripts"
	@echo "screenshots          - run Stellarium startup scripts"
	@echo "maps                 - map thumbnails"
	@echo "merge                - merge screenshots and maps"
	@echo "video                - build videos from screenshots-with-maps"
	@echo "all                  - sky-log + stellarium visual pipeline"
	@echo "demo                 - sample GPX → sky-log → profile"
	@echo "test                 - run pytest"
	@echo "clean                - remove generated data (keeps samples/content)"
	@echo "lock                 - refresh uv.lock"

# Entry point: full capture pipeline (already chains sky-log, stellarium-scripts, screenshots, maps, merge).
run: all
