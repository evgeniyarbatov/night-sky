"""Copy a GPX file into the local drop zone (data/gpx/)."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

GPX_DEST_DIR = Path("data/gpx")
SAMPLE_GPX = Path("data/samples/sample_night_run.gpx")


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy a GPX into data/gpx/")
    parser.add_argument(
        "src",
        nargs="?",
        default=None,
        help="Path to a .gpx file (default: committed sample)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Remove existing files in data/gpx/ before copying",
    )
    args = parser.parse_args()

    src = Path(args.src) if args.src else SAMPLE_GPX
    if not src.is_file():
        raise SystemExit(f"GPX not found: {src}")

    if args.clear and GPX_DEST_DIR.exists():
        shutil.rmtree(GPX_DEST_DIR)
    GPX_DEST_DIR.mkdir(parents=True, exist_ok=True)
    dest = GPX_DEST_DIR / src.name
    shutil.copy(src, dest)
    print(f"Copied {src} → {dest}")


if __name__ == "__main__":
    main()
