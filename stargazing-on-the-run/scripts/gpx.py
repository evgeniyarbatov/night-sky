"""Copy a GPX file into the local drop zone."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

GPX_DEST_DIR = Path("data/gpx")
SAMPLE_GPX = Path("data/samples/sample_night_run.gpx")


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy a GPX into the drop zone")
    parser.add_argument(
        "src",
        nargs="?",
        default=None,
        help="Path to a .gpx file (default: committed sample)",
    )
    parser.add_argument(
        "--dest",
        default=str(GPX_DEST_DIR),
        help="Drop zone directory (default: data/gpx)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Remove existing files in the drop zone before copying",
    )
    args = parser.parse_args()

    src = Path(args.src) if args.src else SAMPLE_GPX
    if not src.is_file():
        raise SystemExit(f"GPX not found: {src}")

    dest_dir = Path(args.dest)
    if args.clear and dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    shutil.copy(src, dest)
    print(f"Copied {src} → {dest}")


if __name__ == "__main__":
    main()
