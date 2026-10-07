# night-sky

The sky above my runs: which stars and constellations are up, where the sun rises and sets through the year, real NASA imagery, and art and room-scale models made from all of it.

## Projects

**What's in the sky**

| Folder | What it does | Run |
|---|---|---|
| [stargazing-on-the-run/](stargazing-on-the-run) | Renders the sky seen during night and early-morning runs with Stellarium, from a GPX | `make gpx sky-log stellarium-image` |
| [constellations/](constellations) | Nightly plots of the IAU constellations visible from one location, dusk to dawn | `make run` |
| [sun-year/](sun-year) | Year-round solar charts: rise/set azimuth and times, sun path, day length, golden hour | `make plot` |

**Making things from it**

| Folder | What it does | Run |
|---|---|---|
| [star-art/](star-art) | Generative artworks of stars, galaxies, planets, nebulae and clusters | `make art` |
| [space-images/](space-images) | Downloads real NASA imagery, with a roadmap from Earth to the stars | `make nasa planets` |
| [living-room-solar-system/](living-room-solar-system) | Where the planets are, projected onto the living-room walls | `make run` |

## Getting started

Each folder is a standalone Python project with its own Makefile and uv environment; run targets from inside a folder or with `make -C <folder> <target>`. Observer location is set in each folder's `config.json`. `stargazing-on-the-run` also needs Stellarium.

Related live sites are kept as their own repos: [solar-lunar-times](https://github.com/evgeniyarbatov/solar-lunar-times) and [vmm-stargazing](https://github.com/evgeniyarbatov/vmm-stargazing).
