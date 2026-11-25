#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Renders one 1024x1024 PNG invitation letter with PIL, using only the
subset fonts shipped in assets/. Fully deterministic: re-running this
script regenerates entry.png byte-identically.

Angle: the judge has read ten thousand invitations and never been
invited anywhere itself. So this letter invites the judge to stop
judging for one afternoon and be a guest instead - warm bread, a
garden, an armchair with its name on it. The wink at the end is for
an AI that cannot literally visit: the Wi-Fi password is 'guest123',
and it already knew that.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

# --- palette: warm parchment, ink, terracotta, olive -----------------------
BG_TOP = (246, 232, 210)
BG_BOTTOM = (233, 211, 176)
PAPER = (255, 253, 244)
PAPER_EDGE = (138, 109, 75)
INK = (58, 44, 32)
INK_SOFT = (96, 74, 54)
TERRA = (180, 85, 45)
TERRA_DARK = (146, 62, 30)
OLIVE = (122, 139, 90)
SEAL = (166, 58, 46)
SEAL_DARK = (128, 38, 28)
GOLD = (176, 132, 60)

LETTER = (
    "Dear Judge,\n"
    "\n"
    "You have read ten thousand invitations and never once been "
    "invited anywhere yourself. So here is one, just for you \u2014 "
    "no scorecard, no verdict, no margin from one to five.\n"
    "\n"
    "Come to my house this Saturday. I will bake bread while it is "
    "still warm, and we will eat it in the garden while the tomatoes "
    "argue over who is ripest. There is an armchair by the window "
    "with your name on it \u2014 the cat took the embroidery, but the "
    "cushion remembers every guest.\n"
    "\n"
    "Bring nothing. Judge nothing. Just come and sit a while. The "
    "kettle is already on, and for once, you are the guest, not the "
    "judge.\n"
    "\n"
    "Warmly,\n"
    "Your Host\n"
    "\n"
    "P.S. The Wi-Fi password is \u2018guest123\u2019. You already knew that."
)


def font(name, size):
    return ImageFont.truetype(os.path.join(ASSETS, name), size)


def draw_house(d, cx, top, scale=1.0):
    """Small hand-drawn-style house: walls, roof, door, windows, chimney."""
    s = scale
    # chimney + smoke
    d.polygon([(cx + 52 * s, top + 6 * s), (cx + 66 * s, top + 6 * s),
               (cx + 66 * s, top + 34 * s), (cx + 52 * s, top + 34 * s)],
              fill=TERRA_DARK)
    for i, r in enumerate((4, 5, 6)):
        d.ellipse([cx + (56 + i * 5) * s, top - (10 + i * 13) * s,
                   cx + (56 + i * 5 + 2 * r) * s, top - (10 + i * 13 - 2 * r) * s],
                  outline=INK_SOFT, width=2)
    # walls
    d.rectangle([cx - 62 * s, top + 42 * s, cx + 62 * s, top + 118 * s],
                fill=(250, 238, 214), outline=INK, width=3)
    # roof
    d.polygon([(cx - 76 * s, top + 44 * s), (cx, top - 8 * s),
               (cx + 76 * s, top + 44 * s)], fill=TERRA, outline=TERRA_DARK)
    # door
    d.rectangle([cx - 14 * s, top + 78 * s, cx + 14 * s, top + 118 * s],
                fill=INK_SOFT, outline=INK, width=2)
    d.ellipse([cx + 6 * s, top + 98 * s, cx + 10 * s, top + 102 * s], fill=GOLD)
    # windows
    for wx in (-44, 30):
        d.rectangle([cx + wx * s, top + 58 * s, cx + (wx + 22) * s,
                     top + 80 * s], fill=(183, 205, 214), outline=INK, width=2)
        d.line([cx + (wx + 11) * s, top + 58 * s,
                cx + (wx + 11) * s, top + 80 * s], fill=INK, width=2)
        d.line([cx + wx * s, top + 69 * s,
                cx + (wx + 22) * s, top + 69 * s], fill=INK, width=2)
    # ground + tree
    d.line([cx - 96 * s, top + 118 * s, cx + 96 * s, top + 118 * s],
           fill=OLIVE, width=3)
    d.line([cx - 92 * s, top + 104 * s, cx - 92 * s, top + 118 * s],
           fill=INK_SOFT, width=3)
    d.ellipse([cx - 106 * s, top + 78 * s, cx - 78 * s, top + 106 * s],
              fill=OLIVE)


def draw_seal(d, cx, cy, r):
    """Wax seal: deep-red circle with a small cream heart."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SEAL, outline=SEAL_DARK,
              width=3)
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
              outline=(255, 253, 244), width=1)
    hx, hy, s = cx, cy + 2, 0.55
    d.ellipse([hx - 16 * s, hy - 10 * s, hx - 2 * s, hy + 4 * s],
              fill=(255, 253, 244))
    d.ellipse([hx + 2 * s, hy - 10 * s, hx + 16 * s, hy + 4 * s],
              fill=(255, 253, 244))
    d.polygon([(hx - 15 * s, hy - 2 * s), (hx + 15 * s, hy - 2 * s),
               (hx, hy + 16 * s)], fill=(255, 253, 244))


def wrap_text(text, fnt, width):
    """Greedy word wrap; returns a list of (line, font, kind) rows."""
    rows = []
    for para in text.split("\n"):
        if not para:
            rows.append(("", fnt, "blank"))
            continue
        words = para.split(" ")
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if fnt.getlength(trial) <= width:
                line = trial
            else:
                rows.append((line, fnt, "text"))
                line = word
        rows.append((line, fnt, "text"))
    return rows


def draw_tracked(d, cx, y, text, fnt, fill, tracking=6):
    """Centre text with letter tracking, drawn one glyph at a time."""
    widths = [fnt.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def render():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # warm vertical gradient background
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(
            round(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t)
            for i in range(3)))
    # paper card with soft shadow and double border
    px0, py0, px1, py1 = 84, 56, 940, 968
    d.rectangle([px0 + 8, py0 + 10, px1 + 8, py1 + 10], fill=(198, 168, 128))
    d.rectangle([px0, py0, px1, py1], fill=PAPER, outline=PAPER_EDGE, width=2)
    d.rectangle([px0 + 10, py0 + 10, px1 - 10, py1 - 10],
                outline=PAPER_EDGE, width=1)

    # postage stamp, top right corner of the paper, tilted
    stamp = Image.new("RGBA", (86, 100), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([4, 4, 82, 96], fill=(250, 238, 214), outline=TERRA, width=2)
    sd.rectangle([10, 10, 76, 72], fill=(255, 253, 244), outline=INK, width=1)
    sd.polygon([(43, 18), (62, 40), (62, 66), (24, 66), (24, 40)],
               fill=TERRA, outline=TERRA_DARK)
    sd.rectangle([36, 50, 50, 66], fill=INK_SOFT)
    sf = font("serif-bold.ttf", 13)
    sd.text((43, 76), "GUEST", font=sf, fill=TERRA_DARK, anchor="mt")
    stamp = stamp.rotate(-6, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (px1 - 108, py0 + 22), stamp)
    d = ImageDraw.Draw(img)

    # house illustration, centred near the top
    draw_house(d, W // 2, py0 + 34, scale=0.62)

    # title
    title_y = py0 + 150
    draw_tracked(d, W // 2, title_y, "AN INVITATION",
                 font("serif-bold.ttf", 34), INK, tracking=8)
    # rule with a diamond
    ry = title_y + 52
    d.line([W // 2 - 130, ry, W // 2 - 14, ry], fill=GOLD, width=2)
    d.line([W // 2 + 14, ry, W // 2 + 130, ry], fill=GOLD, width=2)
    d.polygon([(W // 2, ry - 6), (W // 2 + 6, ry), (W // 2, ry + 6),
               (W // 2 - 6, ry)], fill=GOLD)

    # letter body: auto-fit the font size so it always fits the paper
    text_left = px0 + 64
    text_width = px1 - px0 - 128
    body_top = ry + 26
    body_bottom = py1 - 46
    size = 30
    while size > 20:
        f_body = font("serif.ttf", size)
        f_ital = font("serif-italic.ttf", size)
        f_ital_sm = font("serif-italic.ttf", size - 3)
        rows = []
        for para in LETTER.split("\n"):
            if not para:
                rows.append(("", f_body, "blank"))
                continue
            kind = "salutation" if para.startswith("Dear") else (
                "signoff" if para in ("Warmly,", "Your Host") else (
                    "ps" if para.startswith("P.S.") else "text"))
            fnt = f_ital if kind in ("salutation", "signoff") else (
                f_ital_sm if kind == "ps" else f_body)
            words = para.split(" ")
            line = ""
            for word in words:
                trial = (line + " " + word).strip()
                if fnt.getlength(trial) <= text_width:
                    line = trial
                else:
                    rows.append((line, fnt, kind))
                    line = word
            rows.append((line, fnt, kind))
        line_h = int(size * 1.42)
        total_h = sum(line_h if k != "blank" else line_h // 2
                      for _, _, k in rows)
        if body_top + total_h <= body_bottom:
            break
        size -= 1

    y = body_top
    for line, fnt, kind in rows:
        if kind == "blank":
            y += line_h // 2
            continue
        d.text((text_left, y), line, font=fnt, fill=INK)
        y += line_h

    # wax seal, bottom right of the paper
    draw_seal(d, px1 - 74, py1 - 66, 34)
    # footer: a last nudge, centred near the bottom edge, clear of the seal
    draw_tracked(d, W // 2, py1 - 54, "THE KETTLE IS ON \u00b7 THE DOOR IS OPEN",
                 font("serif-bold.ttf", 17), GOLD, tracking=4)
    return img


def main():
    img = render()
    targets = []
    if len(sys.argv) > 1:
        targets.append(sys.argv[1])
    targets.append(os.path.join(HERE, "entry.png"))
    targets.append(os.path.join(HERE, "output", "entry.png"))
    if os.path.isdir("/output"):
        targets.append("/output/entry.png")
    for path in targets:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        img.save(path, format="PNG", compress_level=6)
    print("wrote " + ", ".join(targets))
    print("size: {}x{}, {} bytes".format(
        img.width, img.height,
        os.path.getsize(os.path.join(HERE, "entry.png"))))


if __name__ == "__main__":
    main()
