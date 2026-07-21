#!/usr/bin/env python3
"""Add an image (and its sidecars) to the local album of selected images."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import copy_with_sidecars, load_meta, repo_root, write_sidecar


def ensure_sidecar(image_path: Path) -> None:
    if image_path.with_suffix(".json").is_file():
        return
    meta = load_meta(image_path)
    if meta is None:
        from common import ImageMeta, classify_destination, go_deeper_text

        title = image_path.stem
        dest = classify_destination(title)
        meta = ImageMeta(
            title=title,
            date="",
            source_url="",
            image_url="",
            destination=dest,
            go_deeper=go_deeper_text("", title),
        )
        write_sidecar(image_path, meta)


def rebuild_album_index(selected_dir: Path) -> Path:
    images = sorted(
        p for p in selected_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    lines = [
        "# Selected album",
        "",
        "Local favorites. Add with `make select IMAGE=path/to/image.jpg`.",
        "",
    ]
    if not images:
        lines.append("_No images selected yet._")
    else:
        lines.append(f"{len(images)} image(s):\n")
        for img in images:
            meta = load_meta(img)
            title = meta.title if meta else img.stem
            dest = meta.destination if meta else "other"
            story = img.with_suffix(".md").name
            lines.append(f"- **{title}** (`{dest}`) — `{img.name}` · [story]({story})")
        lines.append("")
    index = selected_dir / "INDEX.md"
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy an image into album/selected/")
    parser.add_argument(
        "image",
        type=Path,
        nargs="?",
        default=None,
        help="Path to an image file (jpg/png)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Rebuild and print album/selected/INDEX.md only",
    )
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve() if args.root else repo_root()
    selected = root / "album" / "selected"
    selected.mkdir(parents=True, exist_ok=True)

    if args.list or args.image is None:
        if args.image is None and not args.list:
            print("Usage: select.py IMAGE  or  select.py --list", file=sys.stderr)
            sys.exit(2)
        index = rebuild_album_index(selected)
        print(index.read_text(encoding="utf-8"))
        return

    image = args.image.expanduser().resolve()
    if not image.is_file():
        print(f"Not a file: {image}", file=sys.stderr)
        sys.exit(1)
    if image.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        print(f"Expected an image file, got: {image.suffix}", file=sys.stderr)
        sys.exit(1)

    ensure_sidecar(image)
    dest = copy_with_sidecars(image, selected)
    rebuild_album_index(selected)
    print(f"Selected → {dest}")


if __name__ == "__main__":
    main()
