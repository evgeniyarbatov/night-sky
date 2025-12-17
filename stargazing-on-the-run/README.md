# Stargazing on the Run

[![Format Python Code](https://github.com/evgeniyarbatov/stargazing-on-the-run/actions/workflows/format.yml/badge.svg)](https://github.com/evgeniyarbatov/stargazing-on-the-run/actions/workflows/format.yml)
[![Lint Python Code](https://github.com/evgeniyarbatov/stargazing-on-the-run/actions/workflows/lint.yaml/badge.svg)](https://github.com/evgeniyarbatov/stargazing-on-the-run/actions/workflows/lint.yaml)

The idea for this project came during one of my early morning or late night runs. I spend a lot of time under the open sky, and if I'm lucky enough to see a cloudless sky, it's a perfect opportunity for stargazing. Even just getting to know the major stars and constellations I have a chance of observing is already an achievement.

I made this work with GPX files since this is the most common format for running watches. I parse GPX files, extract latitude/longitude/azimuth from several distinct points, and create a Stellarium script based on them. The Stellarium script takes care of capturing screenshots, which can optionally be turned into videos.

I hope you get to learn something new about the night sky after your next run!

## How to use

Get GPX traces:

```
make gpx
```

Create Stellarium scripts:

```
make scripts
```

Update Stellarium config.ini:

```
# ~/Library/Application\ Support/Stellarium/config.ini
[scripts]
flag_allow_screenshots_dir             = true
```

Create Stellarium screenshots:

```
make screenshots
```

Create maps to show location adn direction:

```
make maps
```

Merge Stellarium screenshots and maps into a single image:

```
make merge
```

Create videos:

```
ffmpeg \
-framerate 1 \
-pattern_type glob -i '*.png' \
-c:v libx264 \
-pix_fmt yuv420p \
-filter:v "setpts=3.0*PTS" \
video.mp4
```
