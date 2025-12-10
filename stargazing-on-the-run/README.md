# Stargazing on the Run

Stellarium scripts to render stars and planets based on GPX file location and direction.

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
