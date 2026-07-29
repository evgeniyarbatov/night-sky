# space-images

Toolkit for pulling real NASA space imagery onto a laptop: APIs, sidecars with captions and credit, and a practical map from Earth to the stars.

See [ROADMAP.md](ROADMAP.md) for the path outward and what you can build with a network connection today.

## What this repo does

| Piece | Role |
| --- | --- |
| `make inspire` | APOD + caption → `$(DATA_DIR)/album/daily/YYYY-MM-DD/` (adds a new photo each run; local only) |
| `scripts/nasa.py` | Random APOD (last year) + NASA Image Library sample → `$(DATA_DIR)/images/` |
| `scripts/planets.py` | Up to 20 images per planet (Mercury–Neptune) → `$(DATA_DIR)/images/<planet>/` |
| `ROADMAP.md` | Ladder outward + project plan |

Every download gets **sidecar** `.json` + `.md`: title, date, mission, body, license, source URL, destination tag, and full caption from the source.

Generated images never live in the repo working tree. By default they go to `~/data/space-images/`; override with `make <target> DATA_ROOT=/path/to/shared` (keeps the `space-images` subfolder) or `make <target> DATA_DIR=/tmp/run-42` (exact path). Credit NASA and other sources when you share.

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv).

```bash
make install
export NASA_API_KEY=your_key   # free at https://api.nasa.gov — optional; DEMO_KEY works with limits
make inspire                   # one picture + story (repeat to add more the same day)
```

Open `~/data/space-images/album/daily/LATEST.md`.

Bulk pulls:

```bash
make nasa      # 20× APOD + library samples → $(DATA_DIR)/images/
make planets   # per-planet sets → $(DATA_DIR)/images/<planet>/
```

Or run scripts once (pass `--root` / `--output-dir` to control where files land; otherwise they default to `images/` and `album/` inside the repo):

```bash
uv run python scripts/inspire.py --root ~/data/space-images
uv run python scripts/nasa.py --output-dir ~/data/space-images/images
uv run python scripts/planets.py --output-dir ~/data/space-images/images
```

### Daily schedule

```bash
# crontab example — 08:00 every day
0 8 * * * cd /path/to/space-images && make inspire
```

## Layout

```
scripts/                            downloaders + inspire
$(DATA_DIR)/images/                 APOD + library + per-planet downloads
$(DATA_DIR)/images/<planet>/        make planets output (mercury … neptune)
$(DATA_DIR)/album/daily/            daily pulls
ROADMAP.md                          path outward + project plan
```

`$(DATA_DIR)` defaults to `~/data/space-images` (see Quick start).

## Image & news sources

**Images:** [NASA Images](https://images.nasa.gov) · [ESA photolibrary](https://photolibrary.esa.int/home-page) · [Hubble](https://hubblesite.org/images) · [JPL Photojournal](https://photojournal.jpl.nasa.gov) · [APOD archive](https://apod.nasa.gov/apod/archivepix.html) · [ESO](https://www.eso.org/public/images) · [Chandra](https://chandra.harvard.edu/photo)

**Mars:** [Perseverance raw images](https://mars.nasa.gov/mars2020/multimedia/raw-images/)

**News:** [Space.com](https://www.space.com) · [SpaceWeather](https://spaceweather.com) · [Sky & Telescope](https://skyandtelescope.org)

## License

MIT — see [LICENSE.md](LICENSE.md). Downloaded NASA media remains under its own terms; check each source before redistribution. APOD entries may carry third-party copyright — see each day's credit line.
