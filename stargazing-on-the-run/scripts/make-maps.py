import glob
import os
import shutil
import sys

import pandas as pd

import contextily as ctx
import matplotlib.pyplot as plt
from dataclasses import asdict

from utils import load_points


def plot_run(
    points,
    maps_dir,
):
    points_df = pd.DataFrame.from_records([asdict(p) for p in points])

    for _, point in points_df.iterrows():
        fig = plt.figure(
            figsize=(10, 6),
            dpi=600,
        )
        ax1 = fig.add_subplot(1, 1, 1)
        ax1.set_aspect("equal", adjustable="box")
        ax1.scatter(
            point["lon"], point["lat"], zorder=3, alpha=1, c="r", s=60, marker="o"
        )
        buffer = 0.001
        ax1.set_xlim(point["lon"] - buffer, point["lon"] + buffer)
        ax1.set_ylim(point["lat"] - buffer, point["lat"] + buffer)
        ctx.add_basemap(
            ax1,
            crs="EPSG:4326",
            source=ctx.providers.CartoDB.Positron,
            zoom=19,
            attribution=False,
        )
        ax1.set_xticks([], [])
        ax1.set_yticks([], [])
        ax1.tick_params(
            axis="both", which="both", bottom=False, top=False, left=False, right=False
        )

        fig.tight_layout()
        fig.savefig(
            f"{maps_dir}/{point['timestamp']}.png",
            dpi=360,
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
