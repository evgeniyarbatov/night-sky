# space-images

Toolkit for pulling real NASA space imagery onto a laptop: APIs, sidecars with captions and credit, and a practical map from Earth to the stars.

See [ROADMAP.md](ROADMAP.md) for the path outward and what you can build with a network connection today.

## What this repo does

| Piece | Role |
| --- | --- |
| `make inspire` | Today's [APOD](https://apod.nasa.gov) + caption + social draft → `album/daily/` (local only) |
| `scripts/nasa.py` | Random APOD (last year) + NASA Image Library sample → `images/` |
| `scripts/planets.py` | Up to 20 images per planet (Mercury–Neptune) → `planets/` |
| `make select` / `album` | Local favorites album in `album/selected/` |
| `ROADMAP.md` | Ladder outward + project plan |

Every download gets **sidecar** `.json` + `.md`: title, date, mission, body, license, source URL, destination tag, and full caption from the source.

Images stay local (gitignored). Credit NASA and other sources when you share.

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
scripts/         downloaders + inspire / select
images/          APOD + library downloads (local)
planets/         per-planet downloads (local)
album/daily/     daily pull (local, gitignored)
album/selected/  favorites (local, gitignored)
ROADMAP.md       path outward + project plan
```

## Image & news sources

**Images:** [NASA Images](https://images.nasa.gov) · [ESA photolibrary](https://photolibrary.esa.int/home-page) · [Hubble](https://hubblesite.org/images) · [JPL Photojournal](https://photojournal.jpl.nasa.gov) · [APOD archive](https://apod.nasa.gov/apod/archivepix.html) · [ESO](https://www.eso.org/public/images) · [Chandra](https://chandra.harvard.edu/photo)

**Mars:** [Perseverance raw images](https://mars.nasa.gov/mars2020/multimedia/raw-images/)

**News:** [Space.com](https://www.space.com) · [SpaceWeather](https://spaceweather.com) · [Sky & Telescope](https://skyandtelescope.org)

## License

MIT — see [LICENSE.md](LICENSE.md). Downloaded NASA media remains under its own terms; check each source before redistribution. APOD entries may carry third-party copyright — see each day's credit line.
