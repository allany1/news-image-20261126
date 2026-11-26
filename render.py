#!/usr/bin/env python3
"""Render entry.png: 'Sum up 26 November 2026 world news in one image'.

Newspaper-style one-pager, 1024x1024, built from stories.json with Pillow.
Deterministic: same input -> same output bytes.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
MARGIN = 36
CW = W - 2 * MARGIN  # content width

PAPER = (250, 247, 239)
INK = (17, 17, 17)
RED = (163, 0, 22)
GREY = (70, 70, 70)
RULE = (17, 17, 17)
FAINT = (196, 190, 172)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")

DATE_LINE = "THURSDAY 26 NOVEMBER 2026"
FOOTER_LINE = "All 35 stories above are from Thursday 26 November 2026 (UTC)."


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, width):
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if text_w(draw, trial, f) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(draw, s, f, width):
    if text_w(draw, s, f) <= width:
        return s
    while s and text_w(draw, s + "…", f) > width:
        s = s.rsplit(" ", 1)[0] if " " in s else s[:-1]
    return s + "…"


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    stories = data["stories"]
    leads = [s for s in stories if s.get("lead")]
    briefs = [s for s in stories if not s.get("lead")]
    assert len(leads) == 6, f"expected 6 leads, got {len(leads)}"

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- Masthead ----------
    y = 16
    f_title = font(SERIF_B, 50)
    title = "THE WORLD IN ONE DAY"
    tw = text_w(d, title, f_title)
    d.text(((W - tw) / 2, y), title, font=f_title, fill=INK)
    y += 62
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=4)
    y += 3
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)
    y += 9
    band_h = 54
    d.rectangle([MARGIN, y, W - MARGIN, y + band_h], fill=INK)
    f_date = font(SANS_B, 34)
    dw = text_w(d, DATE_LINE, f_date)
    d.text(((W - dw) / 2, y + 8), DATE_LINE, font=f_date, fill=(255, 255, 255))
    y += band_h + 10
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=2)
    y += 10
    print("masthead ends at", y)

    # ---------- Lead stories ----------
    f_tag = font(SANS_B, 13)
    f_head = font(SERIF_B, 24)
    f_deck = font(SANS, 15)
    HEAD_LH = 29
    for k, s in enumerate(leads):
        d.text((MARGIN, y), s["region"].upper(), font=f_tag, fill=RED)
        y += 17
        for line in wrap(d, s["headline"], f_head, CW)[:2]:
            d.text((MARGIN, y), line, font=f_head, fill=INK)
            y += HEAD_LH
        deck = fit_one_line(d, s["deck"], f_deck, CW)
        d.text((MARGIN, y), deck, font=f_deck, fill=GREY)
        y += 23
        if k < len(leads) - 1:
            d.line([(MARGIN, y), (W - MARGIN, y)], fill=FAINT, width=1)
            y += 7
    print("leads end at", y)

    # ---------- Also today (briefs) ----------
    y += 5
    d.rectangle([MARGIN, y, W - MARGIN, y + 32], fill=RED)
    f_also = font(SANS_B, 19)
    also = "ALSO TODAY — AROUND THE WORLD"
    aw = text_w(d, also, f_also)
    d.text(((W - aw) / 2, y + 5), also, font=f_also, fill=(255, 255, 255))
    y += 44
    print("briefs start at", y)

    FOOTER_TOP = H - 42
    rows = (len(briefs) + 1) // 2
    avail = FOOTER_TOP - y
    lh = avail // rows
    assert lh >= 17, f"briefs line height too small: {lh}"
    f_brief = font(SANS, 14)
    f_brief_tag = font(SANS_B, 13)
    col_w = (CW - 28) // 2
    col_x = [MARGIN, MARGIN + col_w + 28]
    tag_short = {
        "Middle East": "MEAST",
        "Europe": "EUROPE",
        "Asia-Pacific": "ASIA-PAC",
        "Americas": "AMERICAS",
        "Africa": "AFRICA",
        "Global": "GLOBAL",
        "Sport": "SPORT",
    }
    for i, s in enumerate(briefs):
        col = i // rows
        row = i % rows
        x = col_x[col]
        by = y + row * lh
        tag = tag_short.get(s["region"], s["region"].upper())
        d.text((x, by), tag, font=f_brief_tag, fill=RED)
        tag_w = text_w(d, tag, f_brief_tag) + 8
        head = fit_one_line(d, s["headline"], f_brief, col_w - tag_w)
        d.text((x + tag_w, by), head, font=f_brief, fill=INK)

    # ---------- Footer ----------
    d.line([(MARGIN, FOOTER_TOP), (W - MARGIN, FOOTER_TOP)], fill=RULE, width=2)
    f_foot = font(SANS_B, 14)
    fw = text_w(d, FOOTER_LINE, f_foot)
    d.text(((W - fw) / 2, FOOTER_TOP + 10), FOOTER_LINE, font=f_foot, fill=INK)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes; briefs lh =", lh)


if __name__ == "__main__":
    main()
