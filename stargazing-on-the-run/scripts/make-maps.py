import glob
import os
import shutil
import sys

import pandas as pd

import contextily as ctx
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from dataclasses import asdict

from numpy import pi

from utils import load_points


def get_compass_data(degrees):
    values = [0, 0, 0, 0, 0, 0, 0, 0]
    values[int(degrees / 45)] = 1

    compass_data = pd.DataFrame(
        {
            "value": values,
            "bearing": range(0, 360, 45),
            "compass": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
        }
    )
    compass_data.index = compass_data["bearing"] * 2 * pi / 360

    return compass_data


def plot_run(
    points,
    maps_dir,
):
    points_df = pd.DataFrame.from_records([asdict(p) for p in points])

    for _, point in points_df.iterrows():
        compass_data = get_compass_data(point["az"])

        fig = plt.figure(
            figsize=(8, 4),
            dpi=300,
        )
        gs = GridSpec(nrows=1, ncols=2, width_ratios=[1, 1])

        ax1 = fig.add_subplot(gs[0, 0])
        ax1.set_aspect("equal", "datalim")
        ax1.plot(points_df["lon"], points_df["lat"], linewidth=3, zorder=2)
        ax1.scatter(
            point["lon"], point["lat"], zorder=3, alpha=1, c="r", s=60, marker="o"
        )
        ctx.add_basemap(ax1, crs="EPSG:4326", source=ctx.providers.OpenStreetMap.Mapnik)
        ax1.set_xticks([], [])
        ax1.set_yticks([], [])
        ax1.tick_params(
            axis="both", which="both", bottom=False, top=False, left=False, right=False
        )

        ax2 = fig.add_subplot(gs[0, 1], projection="polar")
        ax2.set_theta_zero_location("N")
        ax2.set_theta_direction(-1)
        ax2.bar(x=compass_data.index, height=compass_data["value"], width=pi / 4)
        ax2.set_xticklabels(compass_data.compass)
        ax2.set_rgrids([])

        fig.tight_layout()
        fig.savefig(
            f"{maps_dir}/{point['timestamp']}.png",
        )
        plt.close(fig)


def main(
    gpx_dir,
    maps_dir,
):
    shutil.rmtree(maps_dir, ignore_errors=True)
    os.makedirs(maps_dir, exist_ok=True)

    gpx_files = glob.glob(
        os.path.join(gpx_dir, "*.gpx"),
    )
    for gpx_file in gpx_files:
        filename = os.path.splitext(os.path.basename(gpx_file))[0]

        map_path = f"{maps_dir}/{filename}"
        os.makedirs(map_path)

        plot_run(load_points(gpx_file), map_path)


if __name__ == "__main__":
    main(*sys.argv[1:])
