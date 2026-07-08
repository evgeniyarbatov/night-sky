VENV_PATH := .venv
PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip

venv:
	@uv venv $(VENV_PATH)

install: venv
	@uv pip install -q -r requirements.txt

gpx: install
	@$(PYTHON) scripts/gpx.py
stellarium-scripts: install
	@$(PYTHON) scripts/create-scripts.py \
	data/gpx \
	data/scripts \
	data/screenshots
screenshots:
	@for file in data/scripts/*.ssc; do \
		script_path=$$(realpath $$file); \
		/Applications/Stellarium.app/Contents/MacOS/stellarium --startup-script $$script_path; \
	done

maps: install
	@$(PYTHON) scripts/make-maps.py \
	data/gpx \
	data/maps
merge: install
	@$(PYTHON) scripts/merge.py \
	data/gpx \
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

test: install
	@$(PYTHON) -m pytest
clean:
	@rm -rf data/*