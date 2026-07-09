# Uses uv (https://docs.astral.sh/uv) for dependency management — uv sync creates/updates .venv; run commands via uv run, no manual activation.
install:
	@uv sync --dev

gpx: install
	@uv run python scripts/gpx.py

stellarium-scripts: install
	@uv run python scripts/create-scripts.py \
	data/gpx \
	data/scripts \
	data/screenshots

screenshots:
	@for file in data/scripts/*.ssc; do \
		script_path=$$(realpath $$file); \
		/Applications/Stellarium.app/Contents/MacOS/stellarium --startup-script $$script_path; \
	done

maps: install
	@uv run python scripts/make-maps.py \
	data/gpx \
	data/maps

merge: install
	@uv run python scripts/merge.py \
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
	@uv run python -m pytest

clean:
	@rm -rf data/*

lock:
	@uv lock

help:
	@echo "install              - create/update .venv and install dependencies"
	@echo "gpx                  - run gpx.py"
	@echo "stellarium-scripts   - run create-scripts.py"
	@echo "screenshots          - run stellarium startup scripts"
	@echo "maps                 - run make-maps.py"
	@echo "merge                - run merge.py"
	@echo "video                - build videos from screenshots-with-maps"
	@echo "test                 - run pytest"
	@echo "clean                - remove data/*"
	@echo "lock                 - refresh uv.lock"
