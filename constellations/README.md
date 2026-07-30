# constellations

Plots of which constellations are visible overnight from a fixed observer location. Boundary data and reference GIFs come from the [IAU constellation pages](https://iauarchive.eso.org/public/themes/constellations/); visibility uses astropy/astroplan for tonight’s astronomical dusk → dawn.

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11+.

```sh
make run        # install → download → plot
make install    # .venv + deps
make download   # refresh IAU GIFs + boundary .txt under DATA_DIR
make plot       # visibility plots for tonight
make test       # offline unit tests
```

Observer lat/lon live in `scripts/plot_constellations.py` (currently Saigon). Plots land under `~/data/constellations/plots/` by default. Override with `DATA_ROOT=` (parent) or `DATA_DIR=` (full path) on any `make` target.

```sh
make plot DATA_DIR=/tmp/constellations
make help
```
