#!/usr/bin/env python3
"""Entry program for the make.fun bounty "Sum up 26 November's world news
in one image" (news-image-20261126).

The repository ships the finished entry image as a PNG at its root
(a 1024x1024 newspaper-style one-pager of Thursday 26 November 2026,
rendered by render.py from stories.json). This program copies that
image to /output/entry.png, where the grader reads it.

Python 3 standard library only; fully offline and deterministic:
every run writes exactly the bytes of the shipped PNG.
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEST = Path("/output/entry.png")


def find_image():
    """The repository ships exactly one PNG: the entry image.

    Prefer the canonical name entry.png; otherwise take the single
    PNG at the repository root (its name may carry a prefix from the
    upload tool that was used to add it).
    """
    canonical = HERE / "entry.png"
    if canonical.is_file():
        return canonical
    pngs = sorted(p for p in HERE.glob("*.png") if p.is_file())
    if len(pngs) != 1:
        raise SystemExit(f"expected exactly one PNG in {HERE}, found {len(pngs)}")
    return pngs[0]


def main():
    source = find_image()
    os.makedirs(DEST.parent, exist_ok=True)
    shutil.copyfile(source, DEST)
    print(f"wrote {DEST} ({DEST.stat().st_size} bytes) from {source.name}")


if __name__ == "__main__":
    main()
