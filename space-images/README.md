# space-images

Inspiration and toolkit for looking outward: download real NASA space imagery, keep captions with the files, and follow a practical path from Earth to the stars.

It takes all of us — kids, teachers, builders, artists — to get there. See [ROADMAP.md](ROADMAP.md) for the human ladder and project plan.

## What this repo does

| Piece | Role |
| --- | --- |
| `make inspire` | **Daily wow path** — today's [APOD](https://apod.nasa.gov), kid + deep captions, social draft → `album/daily/` |
| `scripts/nasa.py` | Random APOD (last year) + NASA Image Library sample → `images/` |
| `scripts/planets.py` | Up to 20 images per planet (Mercury–Neptune) → `planets/` |
| `make select` / `album` | Build a local favorites album in `album/selected/` |
| `make browse` | Index local images by destination (Moon, Mars, gas giants, …) |
| `make classroom` | 5 images + 5 questions for teachers and families |
| `ROADMAP.md` | Vision and phased project plan |

Every download gets **sidecar** `.json` + `.md` stories: title, date, mission, body, license, source URL, destination tag, “explain like I'm 10”, and “go deeper”.

Images are local (gitignored). Credit NASA and other sources when you share.

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv).

```bash
make install
export NASA_API_KEY=your_key   # free at https://api.nasa.gov — optional; DEMO_KEY works with limits
make inspire                   # one picture + story + post draft
```

Open `album/daily/LATEST.md`. Optional:

```bash
make inspire SELECT=1          # also save to album/selected/
make select IMAGE=images/some.jpg
make browse                    # browse/INDEX.md by destination
make classroom                 # classroom/pack-YYYYMMDD/
```

Bulk pulls:

```bash
make nasa      # 20× APOD + library samples → images/
make planets   # per-planet sets → planets/
```

Or run scripts once:

```bash
uv run python scripts/inspire.py
uv run python scripts/nasa.py
uv run python scripts/planets.py
```

### Daily schedule

```bash
# crontab example — 08:00 every day
0 8 * * * cd /path/to/space-images && make inspire
```

Social sharing is **draft-only**: each daily folder includes `post.txt` (credit + source URL). Paste into X or elsewhere yourself.

## Layout

```
scripts/       downloaders + inspire / select / browse / classroom
images/        APOD + library downloads (local)
planets/       per-planet downloads (local)
album/daily/   daily inspiration (local)
album/selected/ favorites (local)
browse/        destination indexes (regenerate with make browse)
classroom/     classroom packs (local packs; README committed)
ROADMAP.md     inspiration + project roadmap
```

## Image & news sources

**Images:** [NASA Images](https://images.nasa.gov) · [ESA photolibrary](https://photolibrary.esa.int/home-page) · [Hubble](https://hubblesite.org/images) · [JPL Photojournal](https://photojournal.jpl.nasa.gov) · [APOD archive](https://apod.nasa.gov/apod/archivepix.html) · [ESO](https://www.eso.org/public/images) · [Chandra](https://chandra.harvard.edu/photo)

**Mars:** [Perseverance raw images](https://mars.nasa.gov/mars2020/multimedia/raw-images/)

**News:** [Space.com](https://www.space.com) · [SpaceWeather](https://spaceweather.com) · [Sky & Telescope](https://skyandtelescope.org)

## License

MIT — see [LICENSE.md](LICENSE.md). Downloaded NASA media remains under its own terms; check each source before redistribution. APOD entries may carry third-party copyright — see each day's credit line.
