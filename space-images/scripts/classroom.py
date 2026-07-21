#!/usr/bin/env python3
"""Build a classroom pack: 5 images + 5 questions as markdown."""

from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime
from pathlib import Path

from common import iter_sidecars, load_meta, repo_root

QUESTION_TEMPLATES = [
    "Look at **{title}**. What do you notice first? Color, shape, or light?",
    "This picture is tagged **{destination}**. What might it feel like to stand near that place (or look at it from a spaceship)?",
    "Read the “Explain like I'm 10” note. Can you retell it in one sentence of your own?",
    "Scientists and engineers made this image possible. Name one job (other than astronaut) that helped.",
    "What question would you ask a mission scientist about **{title}**?",
    "Compare this image with another in the pack. How are they the same? How are they different?",
    "If you could send a robot or telescope to learn more, what would you measure next?",
]


def _identity(img: Path) -> str:
    meta = load_meta(img)
    if meta and meta.nasa_id:
        return meta.nasa_id
    if meta and meta.title:
        return meta.title.lower()
    return img.stem.lower()


def candidate_images(root: Path) -> list[Path]:
    roots = [
        root / "album" / "selected",
        root / "album" / "daily",
        root / "images",
        root / "planets",
    ]
    images: list[Path] = []
    for json_path in iter_sidecars(roots):
        for ext in (".jpg", ".jpeg", ".png"):
            img = json_path.with_suffix(ext)
            if img.is_file():
                images.append(img)
                break

    def rank(p: Path) -> tuple[int, str]:
        s = str(p)
        if "album/selected" in s or "album\\selected" in s:
            return (0, s)
        if "album/daily" in s or "album\\daily" in s:
            return (1, s)
        if "/images/" in s or "\\images\\" in s:
            return (2, s)
        return (3, s)

    best: dict[str, Path] = {}
    for img in sorted(images, key=rank):
        key = _identity(img)
        if key not in best:
            best[key] = img
    return sorted(best.values(), key=rank)


def pick_five(images: list[Path], n: int = 5) -> list[Path]:
    if len(images) <= n:
        return images
    # Prefer diversity of destination when possible
    by_dest: dict[str, list[Path]] = {}
    for img in images:
        meta = load_meta(img)
        dest = meta.destination if meta else "other"
        by_dest.setdefault(dest, []).append(img)
    picked: list[Path] = []
    dests = list(by_dest.keys())
    random.shuffle(dests)
    for dest in dests:
        if len(picked) >= n:
            break
        choice = random.choice(by_dest[dest])
        if choice not in picked:
            picked.append(choice)
    remaining = [i for i in images if i not in picked]
    random.shuffle(remaining)
    while len(picked) < n and remaining:
        picked.append(remaining.pop())
    return picked[:n]


def build_pack(root: Path, count: int = 5) -> Path:
    images = candidate_images(root)
    if not images:
        raise RuntimeError(
            "No images with sidecars found. Run `make inspire` or `make nasa` first."
        )
    chosen = pick_five(images, n=count)
    stamp = datetime.now().strftime("%Y%m%d")
    pack_dir = root / "classroom" / f"pack-{stamp}"
    pack_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Classroom pack — {stamp}",
        "",
        f"{len(chosen)} real space image(s). Use with any age: look first, then talk, then read the story.",
        "",
        "## Images",
        "",
    ]

    pack_questions: list[str] = []
    templates = QUESTION_TEMPLATES.copy()
    random.shuffle(templates)

    for i, img in enumerate(chosen, start=1):
        meta = load_meta(img)
        title = meta.title if meta else img.stem
        dest = meta.destination if meta else "other"
        el10 = meta.explain_like_10 if meta else ""
        deeper = meta.go_deeper if meta else ""
        credit = meta.credit if meta else "NASA"
        source = meta.source_url if meta else ""
        try:
            rel = img.resolve().relative_to(root.resolve())
        except ValueError:
            rel = img

        lines.extend(
            [
                f"### {i}. {title}",
                "",
                f"- Destination: **{dest}**",
                f"- File: `{rel}`",
                f"- Credit: {credit}",
            ]
        )
        if source:
            lines.append(f"- Source: {source}")
        lines.append("")
        if el10:
            lines.append(f"**Explain like I'm 10:** {el10}")
            lines.append("")
        if deeper:
            short = deeper if len(deeper) <= 600 else deeper[:597].rsplit(" ", 1)[0] + "…"
            lines.append(f"**Go deeper:** {short}")
            lines.append("")

        tmpl = templates[(i - 1) % len(templates)]
        pack_questions.append(tmpl.format(title=title, destination=dest.replace("-", " ")))

    while len(pack_questions) < 5:
        tmpl = templates[len(pack_questions) % len(templates)]
        title = chosen[-1].stem if chosen else "this image"
        pack_questions.append(tmpl.format(title=title, destination="space"))

    lines.append("## Five questions")
    lines.append("")
    for i, q in enumerate(pack_questions[:5], start=1):
        lines.append(f"{i}. {q}")
    lines.append("")
    lines.append(
        "_Tip for educators: let students answer before reading “Go deeper.” "
        "Wonder first, jargon second._"
    )
    lines.append("")

    readme = pack_dir / "README.md"
    readme.write_text("\n".join(lines), encoding="utf-8")

    latest = root / "classroom" / "LATEST.md"
    latest.write_text(
        f"# Latest classroom pack\n\nSee [{pack_dir.name}/README.md]({pack_dir.name}/README.md).\n",
        encoding="utf-8",
    )
    return readme


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a 5-image classroom pack")
    parser.add_argument("--count", type=int, default=5, help="Number of images (default 5)")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    root = args.root.resolve() if args.root else repo_root()
    try:
        path = build_pack(root, count=max(1, args.count))
    except Exception as e:
        print(f"classroom failed: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Wrote {path}")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
