# Stargazing on the Run

![1737127230-compressed](https://github.com/user-attachments/assets/5209ebf3-4b8f-4c3a-b490-00d58c3bd279)

## The Story

The idea for this project came during one of my early morning or late night runs. I spend a lot of time under the open sky, and if I'm lucky enough to see a cloudless sky, it's a perfect opportunity for stargazing. The goal would be to know the night sky as well as I do the streets I run every day.

## What This Does

I made this work with GPX files since this is the most common format for running watches. I parse GPX files, extract latitude/longitude/azimuth from several distinct points, and create a Stellarium script based on them. The Stellarium script takes care of capturing screenshots, which can optionally be turned into videos.

## How to use

```sh
make gpx # Get random GPX traces
make stellarium-scripts # Create Stellarium scripts
make screenshots # Create Stellarium screenshots
make maps # Create maps to show location and direction
make merge # Merge Stellarium screenshots and maps
make video # Create videos
```
