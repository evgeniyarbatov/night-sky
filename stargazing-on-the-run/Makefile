# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.

GPX_DIR ?= data/gpx
SKY_LOGS_DIR ?= data/sky-logs
SRC ?=
START ?=
GPX ?=

install:
	@uv sync --dev

# Copy a GPX into data/gpx/. Default: committed sample. Override: make gpx SRC=/path/to/file.gpx
gpx: install
	@if [ -n "$(SRC)" ]; then \
		uv run python scripts/gpx.py "$(SRC)" --clear; \
	else \
		uv run python scripts/gpx.py --clear; \
	fi

# Sky identity logs (no Stellarium required)
sky-log: install
	@uv run python -m scripts.sky_log $(GPX_DIR) $(SKY_LOGS_DIR)
	@uv run python -m scripts.sky_index --sky-logs $(SKY_LOGS_DIR)

stellarium-scripts: install
	@uv run python -m scripts.create_scripts \
	$(GPX_DIR) \
	data/scripts \
	data/screenshots

screenshots:
	@for file in data/scripts/*.ssc; do \
		script_path=$$(realpath $$file); \
		/Applications/Stellarium.app/Contents/MacOS/stellarium --startup-script $$script_path; \
	done

maps: install
	@uv run python -m scripts.make_maps \
	$(GPX_DIR) \
	data/maps

merge: install
	@uv run python scripts/merge.py \
	$(GPX_DIR) \
	data/screenshots \
	data/maps \
	data/screenshots-with-maps

video:
	@for dir in data/screenshots-with-maps/*/; do \
		if [ -n "$$(ls $$dir/*.png 2>/dev/null)" ]; then \
			subdir=$$(basename $$dir); \
			echo "Creating video for $$subdir..."; \
			ffmpeg -y \
				-framerate 2 \
				-pattern_type glob -i "$$dir/*.png" \
				-c:v libx264 \
				-pix_fmt yuv420p \
				-filter:v "setpts=3.0*PTS" \
				"data/$$subdir.mp4"; \
			echo "Video created: $$subdir.mp4"; \
		fi; \
	done

# Route profile, seasonal rotation, constellation cards
profile: install
	@uv run python -m scripts.profile --gpx-dir $(GPX_DIR) --out $(SKY_LOGS_DIR) --also-sky-log
	@uv run python -m scripts.sky_index --sky-logs $(SKY_LOGS_DIR)

# Rebuild personal sky index only
index: install
	@uv run python -m scripts.sky_index --sky-logs $(SKY_LOGS_DIR)

# Pre-run briefing. Example: make tonight GPX=data/gpx/sample_night_run.gpx START=2026-07-24T21:30
tonight: install
	@if [ -z "$(GPX)" ] || [ -z "$(START)" ]; then \
		echo "Usage: make tonight GPX=data/gpx/your.gpx START=YYYY-MM-DDTHH:MM"; \
		exit 1; \
	fi
	@uv run python -m scripts.tonight --gpx "$(GPX)" --start "$(START)"

tonight-weather: install
	@if [ -z "$(GPX)" ] || [ -z "$(START)" ]; then \
		echo "Usage: make tonight-weather GPX=data/gpx/your.gpx START=YYYY-MM-DDTHH:MM"; \
		exit 1; \
	fi
	@uv run python -m scripts.tonight --gpx "$(GPX)" --start "$(START)" --weather

# Full visual pipeline (requires Stellarium on macOS for screenshots)
all: sky-log stellarium-scripts screenshots maps merge

demo: install
	@$(MAKE) gpx
	@$(MAKE) sky-log
	@$(MAKE) profile
	@echo ""
	@echo "Open data/sky-logs/sample_night_run/sky_log.md"

test: install
	@uv run python -m pytest

clean:
	@rm -rf data/gpx data/scripts data/screenshots data/maps data/screenshots-with-maps data/sky-logs data/sky-index.json data/sky-index.md data/*.mp4 data/.skyfield

lock:
	@uv lock

help:
	@echo "install              - create/update .venv and install dependencies"
	@echo "gpx                  - copy sample (or SRC=...) into data/gpx/"
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
