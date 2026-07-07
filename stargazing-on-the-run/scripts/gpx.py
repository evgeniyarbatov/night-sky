import os
import random
import shutil

GPX_SOURCE_DIR = os.path.expanduser("~/gitRepo/[private]/data/year/2025")
GPX_DEST_DIR = "data/gpx"
NUMBER_OF_GPX = 1


def _gpx_files_in(path):
    matches = []
    for root, _, files in os.walk(path):
        for filename in files:
            if filename.endswith(".gpx"):
                matches.append(os.path.join(root, filename))
    return matches


def main():
    shutil.rmtree(GPX_DEST_DIR, ignore_errors=True)
    os.makedirs(GPX_DEST_DIR, exist_ok=True)

    gpx_files = _gpx_files_in(GPX_SOURCE_DIR)
    for gpx_file in random.sample(gpx_files, NUMBER_OF_GPX):
        shutil.copy(gpx_file, GPX_DEST_DIR)


if __name__ == "__main__":
    main()
