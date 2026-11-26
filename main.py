#!/usr/bin/env python3
"""Entry program for the make.fun bounty "Sum up 26 November's world
news in one image" (news-image-20261126).

The repository ships exactly one PNG, entry.png, rendered from
stories.json by render.py. Running this program copies that PNG to
/output/entry.png. Standard library only, fully offline, and every
run produces bytes identical to the PNG in the repository.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = Path("/output/entry.png")


def the_one_png() -> Path:
    found = sorted(ROOT.glob("*.png"))
    if len(found) != 1:
        raise SystemExit(f"expected exactly one PNG in {ROOT}, found {len(found)}")
    return found[0]


def main() -> None:
    # The PNG is the deliverable; this program only delivers it to /output.
    source = the_one_png()
    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, DEST)
    print(f"wrote {DEST} ({DEST.stat().st_size} bytes) from {source.name}")


if __name__ == "__main__":
    main()
