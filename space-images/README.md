# space-images

Inspiration and toolkit for looking outward: download real NASA space imagery, keep captions with the files, and follow a practical path from Earth to the stars.

It takes all of us — kids, teachers, builders, artists — to get there. See [ROADMAP.md](ROADMAP.md) for the human ladder and project plan.

## What this repo does

| Piece | Role |
| --- | --- |
| `scripts/nasa.py` | Pulls a random [APOD](https://apod.nasa.gov) image (last year) plus a random hit from the [NASA Image and Video Library](https://images.nasa.gov). Writes image + `.md` description into `images/`. |
| `scripts/planets.py` | Downloads up to 20 filtered images per planet (Mercury–Neptune) from the NASA library into `planets/`, each with metadata. |
| `Makefile` | `make nasa` (20 runs), `make planets`, `make install`, `make clean`. Uses [uv](https://docs.astral.sh/uv). |
| `ROADMAP.md` | Vision for a broad audience and phased work for this project. |

Images and descriptions are local artifacts (gitignored under `images/` and `planets/`). Source data is public NASA material — credit missions and agencies when you share.

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv).

```bash
make install   # uv sync --dev
make nasa      # APOD + library samples → images/
make planets   # per-planet sets → planets/
```

Or run once without the loop:

```bash
uv run python scripts/nasa.py
uv run python scripts/planets.py
```

NASA APOD needs an API key ([api.nasa.gov](https://api.nasa.gov)); set it in the downloader (prefer env over hardcoding). Rate limits apply.

## Layout

```
scripts/     downloaders
images/      APOD + library downloads (local)
planets/     per-planet downloads (local)
ROADMAP.md   inspiration + project roadmap
```

## Image & news sources

**Images:** [NASA Images](https://images.nasa.gov) · [ESA photolibrary](https://photolibrary.esa.int/home-page) · [Hubble](https://hubblesite.org/images) · [JPL Photojournal](https://photojournal.jpl.nasa.gov) · [APOD archive](https://apod.nasa.gov/apod/archivepix.html) · [ESO](https://www.eso.org/public/images) · [Chandra](https://chandra.harvard.edu/photo)

**Mars:** [Perseverance raw images](https://mars.nasa.gov/mars2020/multimedia/raw-images/)

**News:** [Space.com](https://www.space.com) · [SpaceWeather](https://spaceweather.com) · [Sky & Telescope](https://skyandtelescope.org)

## License

MIT — see [LICENSE.md](LICENSE.md). Downloaded NASA media remains under its own terms; check each source before redistribution.
