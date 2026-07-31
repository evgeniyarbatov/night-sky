# constellations

Plots of which constellations are visible overnight from a fixed observer location. Boundary data and reference GIFs come from the [IAU constellation pages](https://iauarchive.eso.org/public/themes/constellations/); visibility uses astropy/astroplan for tonight’s astronomical dusk → dawn.

## Run

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11+.

```sh
make run
```

Installs deps, refreshes IAU assets, and writes tonight's plots under `~/data/constellations/plots/`.

## Other commands

```sh
make install    # .venv + deps
make download   # refresh IAU GIFs + boundary .txt under DATA_DIR
make plot       # visibility plots for tonight
make test       # offline unit tests
make help
```

## Configuration

Observer lat/lon/elevation, timezone, and time step live in `config.json` at the repo root (currently Saigon).

Override where plots land with `DATA_ROOT=` (parent dir) or `DATA_DIR=` (full path) on any `make` target:

```sh
make plot DATA_DIR=/tmp/constellations
```
