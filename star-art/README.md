# Star Art

This project generates minimalist star-field artworks from real star positions.

## Code

- Loads locations from `stargazing-locations.json`.
- For each location and each registered style, computes astronomical dusk for the current UTC date and observes stars from that place and time.
- Uses the Hipparcos catalog (via Skyfield) and filters stars by a magnitude threshold.
- Projects the visible stars into a 2D stereographic view centered at azimuth 0 deg and altitude 90 deg with a 180 deg field of view (the horizon style instead plots a narrow altitude band in panoramic azimuth/altitude coordinates).
- Renders each view with Matplotlib and saves a PNG to `<images dir>/<style>/...` (see below).

## How to run

```
make install    # sync dependencies with uv
make            # or `make all` — generates every style below
```

Individual styles:

```
make art        # generates the base star art
make stars      # generates named star renders
make galaxies   # generates galaxy renders
make planets    # generates planet renders
make nebulae    # generates nebula renders
make clusters   # generates star cluster renders
make exotic     # generates exotic object renders
make path       # generates the path renders
make timelapse  # generates timelapse frames for a single location
make horizon    # generates dusk-to-sunrise frames of a low-altitude band (12-20 deg), one sequence per magnitude limit
```

Other targets:

```
make test       # runs the unittest suite
make clean      # removes generated images
make help       # lists all targets
```

Generated images are written outside the repo, to `~/Documents/data/star-art/images` by
default. Override the location with `make <target> DATA_ROOT=/path` (changes
the root under which every repo's data lives) or `make <target> DATA_DIR=/path`
(changes this repo's data dir directly).

## Single render

`scripts/render.py` renders one style for one place and date, so pipelines can drive star-art reproducibly:

```
uv run python scripts/render.py --seed 1 --params params.json --out out/ --inputs sky.json [--size preview|full]
uv run python scripts/render.py --list-styles
```

- `sky.json`: `{"name", "lat", "lon", "date": "YYYY-MM-DD"}`.
- `params.json`: `{"style", "magnitude", "fov", "azimuth", "altitude", "minutes_after_dusk", "footer"}`; all but `style` optional.
- Writes `<out>/render.png` (`preview` ≈1024 px, `full` 300 dpi). Exit code 3 means nothing was visible.
- Skyfield files are cached in `STAR_ART_CACHE` (default `~/.cache/star-art`).
- Installed as a package, the same CLI is `star-art-render` or `python -m star_art.render`.
