# Stargazing on the Run

## The Story

The idea for this project came during one of my early morning or late night runs. I spend a lot of time under the open sky, and if I'm lucky enough to see a cloudless sky, it's a perfect opportunity for stargazing. Even just getting to know the major stars and constellations I have a chance of observing is already an achievement.

## What This Does

I made this work with GPX files since this is the most common format for running watches. I parse GPX files, extract latitude/longitude/azimuth from several distinct points, and create a Stellarium script based on them. The Stellarium script takes care of capturing screenshots, which can optionally be turned into videos.

## How to use

Run the commands

```sh
# Get random GPX traces
make gpx
# Create Stellarium scripts
make stellarium-scripts
# Create Stellarium screenshots
make screenshots
# Create maps to show location and direction
make maps
# Merge Stellarium screenshots and maps into a single image
make merge
# Create videos
make video
```
