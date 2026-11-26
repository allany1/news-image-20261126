#!/usr/bin/env python3
"""Draw the front page for today's make.fun news-image entry.

Reads stories.json (35 stories dated today, UTC), lays them out as a
1024x1024 newspaper front page and writes the result to entry.png.
Only Pillow and the standard library are used, and the output is
deterministic: the same stories.json always yields the same PNG.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "stories.json").read_text(encoding="utf-8"))

PAGE = 1024
MARGIN = 36
COL_GAP = 28
COL_W = (PAGE - 2 * MARGIN - COL_GAP) // 2
PAPER = (247, 243, 234)
INK = (17, 17, 17)
ACCENT = (158, 27, 27)
GREY = (96, 96, 96)
DATE_LINE = "THURSDAY 26 NOVEMBER 2026"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def load(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap measured with the real font metrics."""
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def block(draw, x, y, text, fnt, width, leading, fill=INK, max_lines=None):
    """Draw wrapped text at (x, y); return the y just below it."""
    lines = wrap(draw, text, fnt, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        tail = lines[-1]
        while tail and draw.textlength(tail + "…", font=fnt) > width:
            tail = tail[:-1]
        lines[-1] = tail + "…"
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centered(draw, y, text, fnt, fill=INK):
    w = draw.textlength(text, font=fnt)
    draw.text(((PAGE - w) / 2, y), text, font=fnt, fill=fill)


def masthead(draw):
    centered(draw, 26, "THE WORLD IN ONE DAY", load(SERIF_B, 57))
    draw.line([(MARGIN, 104), (PAGE - MARGIN, 104)], fill=INK, width=3)
    draw.line([(MARGIN, 110), (PAGE - MARGIN, 110)], fill=INK, width=1)
    draw.rectangle([MARGIN, 122, PAGE - MARGIN, 162], fill=INK)
    band = load(SANS_B, 23)
    w = draw.textlength(DATE_LINE, font=band)
    draw.text(((PAGE - w) / 2, 130), DATE_LINE, font=band, fill=(255, 255, 255))


def lead_story(draw, story, x, y):
    """Draw one lead story; return the y just below its deck."""
    tag = load(SANS_B, 14)
    draw.text((x, y), story["region"].upper(), font=tag, fill=ACCENT)
    y = block(draw, x, y + 22, story["headline"], load(SERIF_B, 23), COL_W, 27, max_lines=2)
    return block(draw, x, y + 3, story["deck"], load(SANS, 15), COL_W, 20, max_lines=2)


def leads(draw, stories):
    # Each column stacks its three stories by measured height, so a
    # two-line headline can never collide with the story below it.
    top = 178
    col_y = [top, top]
    for i, story in enumerate(stories):
        col = i % 2
        x = MARGIN + col * (COL_W + COL_GAP)
        col_y[col] = lead_story(draw, story, x, col_y[col]) + 18
    bottom = max(col_y)
    draw.line([(MARGIN, bottom - 6), (PAGE - MARGIN, bottom - 6)], fill=INK, width=1)
    return bottom + 6


def briefs(draw, stories, top):
    draw.rectangle([MARGIN, top, PAGE - MARGIN, top + 34], fill=ACCENT)
    head = load(SANS_B, 19)
    label = "ALSO TODAY — AROUND THE WORLD"
    w = draw.textlength(label, font=head)
    draw.text(((PAGE - w) / 2, top + 7), label, font=head, fill=(255, 255, 255))
    fnt = load(SANS, 13)
    bottom_limit = PAGE - 52
    col_x = [MARGIN, MARGIN + COL_W + COL_GAP]
    col, y = 0, top + 48
    for story in stories:
        text = f"{story['region'].upper()} — {story['headline']}"
        lines = wrap(draw, text, fnt, COL_W)
        height = len(lines) * 16 + 7
        if y + height > bottom_limit and col == 0:
            col, y = 1, top + 48
        for line in lines:
            draw.text((col_x[col], y), line, font=fnt, fill=INK)
            y += 16
        y += 7
    return bottom_limit


def footer(draw):
    note = ("All 35 stories are dated Thursday 26 November 2026 (UTC) and were "
            "compiled from public news wires · make.fun news-image-20261126")
    centered(draw, PAGE - 34, note, load(SANS, 12), fill=GREY)


def main():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(img)
    stories = DATA["stories"]
    masthead(draw)
    # Six leads in two columns first, then the briefs flow underneath.
    bottom = leads(draw, [s for s in stories if s.get("lead")])
    briefs(draw, [s for s in stories if not s.get("lead")], bottom)
    footer(draw)
    out = HERE / "entry.png"
    img.save(out)
    print(f"saved {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
