"""The detail pass's interior textures (scenes/blender/sets/interiors.py): made-up box art, hand-lettered signs and
menus, drawn here with PIL from a fixed seed, so they're regenerable and copy nobody's work.

- The Dev's stock: repair-kit and parts boxes, and his third-party apps in boxes (invented names: no real app, brand
  or logo); the tower's "worse copies" of those apps: the same boxes, white and blank, "OFFICIAL".
- The Dev's signs: WE FIX APPS, SCREEN REPAIR, a price list, the framed first dollar (a made-up note, not a real bill).
- The eatery: a chalk menu (a made-up turo-turo list, prices plausible for the area), numbered dish cards, a drinks
  sign, taped notes, a calendar (pictures and numbers only), a framed landscape, a TV picture.
- The other shops: window signs in marker on card; board-game box art; an old map.
No red (style spec: red is reserved for the REC lights and the READ-ONLY neon) and no Reddit orange-red.

Each atlas is assets/gen/detail/interiors/<name>.png with <name>.json: {item: [u0, v0, u1, v1, aspect]} (Blender UVs,
origin bottom left). Usage: .venv/bin/python -I scripts/gen_detail_interiors.py
"""
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "gen" / "detail" / "interiors"
FONTS = ROOT / "assets" / "fonts"
SEED = 20261030
INTER = str(FONTS / "Inter-Medium-flat.ttf")
HAND = str(FONTS / "OoohBaby-Regular.ttf")
MONO = str(FONTS / "JetBrainsMono-SemiBold-flat.ttf")
INK = "#1d1d1f"


def font(path, size):
    return ImageFont.truetype(path, size)


def hand_text(d, rng, xy, text, size, fill, path=INTER, stroke=0, jitter=1.0, anchor="l"):
    """Lettering drawn a glyph at a time with a little wobble in size, baseline and spacing: marker on card."""
    x, y = xy
    widths = []
    for ch in text:
        f = font(path, int(size * rng.uniform(1 - 0.06 * jitter, 1 + 0.06 * jitter)))
        widths.append((ch, f, f.getlength(ch)))
    total = sum(w for _, _, w in widths) * 1.02
    if anchor == "m":
        x -= total / 2
    elif anchor == "r":
        x -= total
    for ch, f, w in widths:
        d.text((x, y + rng.uniform(-0.05, 0.05) * size * jitter), ch, font=f, fill=fill, anchor="ls",
               stroke_width=stroke, stroke_fill=fill)
        x += w * rng.uniform(0.98, 1.06)
    return total


def card(w, h, col, rng, grain=10):
    """A sheet of card or paper with a little unevenness and a dog-eared look."""
    im = Image.new("RGB", (w, h), col)
    px = im.load()
    base = Image.new("L", (w // 8 + 1, h // 8 + 1))
    bp = base.load()
    for yy in range(base.size[1]):
        for xx in range(base.size[0]):
            bp[xx, yy] = 128 + int(rng.uniform(-grain, grain))
    base = base.resize((w, h), Image.BILINEAR)
    b = base.load()
    for yy in range(h):
        for xx in range(w):
            r, g, bb = px[xx, yy]
            k = b[xx, yy] - 128
            px[xx, yy] = (max(0, min(255, r + k)), max(0, min(255, g + k)), max(0, min(255, bb + k)))
    return im


def tape(im, rng):
    """Masking tape at two or four corners."""
    d = ImageDraw.Draw(im, "RGBA")
    w, h = im.size
    s = max(18, w // 9)
    for cx, cy in ((0, 0), (w, 0), (0, h), (w, h))[: rng.choice((2, 4))]:
        a = rng.uniform(-0.6, 0.6) + (0.785 if (cx == 0) == (cy == 0) else -0.785)
        pts = [(cx + math.cos(a + t) * s * r, cy + math.sin(a + t) * s * r)
               for t, r in ((0.35, 1), (math.pi - 0.35, 1), (math.pi + 0.35, 1), (-0.35, 1))]
        d.polygon(pts, fill=(236, 226, 190, 200))
    return im


# ---------------------------------------------------------------- the Dev's shop

APPS = [  # the Dev's third-party apps, boxed (invented names), and their tower copies
    ("Porchlight", "reader for the rest of us", "#2f7f7a", "circle"),
    ("Threadbare", "fast, no ads", "#2a4d8f", "lines"),
    ("Corkboard", "mod tools that work", "#d9b43c", "square"),
    ("Lantern", "read in the dark", "#3d6b3a", "tri"),
    ("Tinker", "for power users", "#6a4c93", "gear"),
    ("Inkwell", "a reader for blind users", "#1f6f9f", "drop"),
]
KITS = [  # repair parts and accessories (generic names)
    ("SCREEN KIT", "glass + tools", "#1f6f9f"), ("BATTERY", "3000 mAh", "#3d6b3a"), ("FIX-IT KIT", "No. 7", "#d9b43c"),
    ("USB CABLE", "1 m", "#f0ece0"), ("CHARGER", "2A wall", "#2b2f36"), ("CLEAR CASE", "fits most", "#9fc8d8"),
    ("EARBUDS", "wired", "#f0ece0"), ("PORT BRUSH", "x10", "#6a4c93"), ("TOOL SET", "24 pc", "#2b2f36"),
    ("ADHESIVE", "strips", "#e9e2cf"), ("PRIVACY FILM", "2 pack", "#2a4d8f"), ("SD CARD", "32 GB", "#2f7f7a"),
    ("BACK GLASS", "OEM-style", "#4b4f3a"), ("SIM TRAY", "assorted", "#c9ccd1"), ("CAR MOUNT", "vent clip", "#2b2f36"),
    ("POWER BANK", "10000", "#2f7f7a"),
]


def icon(d, kind, cx, cy, r, col):
    if kind == "circle":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=max(3, r // 4))
        d.ellipse((cx - r / 3, cy - r / 3, cx + r / 3, cy + r / 3), fill=col)
    elif kind == "lines":
        for k in range(3):
            d.rounded_rectangle((cx - r, cy - r + k * r * 0.75, cx + r - k * r * 0.4, cy - r + k * r * 0.75 + r * 0.4),
                                r * 0.15, fill=col)
    elif kind == "square":
        d.rounded_rectangle((cx - r, cy - r, cx + r, cy + r), r * 0.3, outline=col, width=max(3, r // 4))
        d.ellipse((cx - r * 0.25, cy - r * 0.6, cx + r * 0.25, cy - r * 0.1), fill=col)
    elif kind == "tri":
        d.polygon([(cx, cy - r), (cx + r, cy + r * 0.8), (cx - r, cy + r * 0.8)], fill=col)
    elif kind == "gear":
        for k in range(8):
            a = k * math.pi / 4
            d.line((cx, cy, cx + math.cos(a) * r, cy + math.sin(a) * r), fill=col, width=max(4, r // 3))
        d.ellipse((cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7), fill=col)
    elif kind == "drop":
        d.ellipse((cx - r * 0.75, cy - r * 0.3, cx + r * 0.75, cy + r * 1.0), fill=col)
        d.polygon([(cx, cy - r), (cx + r * 0.72, cy + r * 0.25), (cx - r * 0.72, cy + r * 0.25)], fill=col)


def app_box(rng, name, sub, col, kind, copy=False):
    W, H = 240, 320
    if copy:  # the tower's version: the same box, white, the name gone, everything a shade of grey
        im = Image.new("RGB", (W, H), "#f4f6f8")
        d = ImageDraw.Draw(im)
        icon(d, kind, W // 2, 120, 50, "#c9d0d8")
        d.text((W // 2, 228), "OFFICIAL", font=font(INTER, 30), fill="#9aa3ad", anchor="ms")
        d.text((W // 2, 262), "App", font=font(INTER, 22), fill="#b8c0c8", anchor="ms")
        d.line((40, 290, W - 40, 290), fill="#cfe6ff", width=3)
        return im
    im = card(W, H, "#f2ede0", rng, 6)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 190), fill=col)
    light = col in ("#d9b43c",)
    icon(d, kind, W // 2, 92, 52, INK if light else "#f2ede0")
    d.text((W // 2, 238), name, font=font(INTER, 36 if len(name) < 10 else 31), fill=INK, anchor="ms")
    d.text((W // 2, 270), sub, font=font(INTER, 17), fill="#4a4a4a", anchor="ms")
    d.text((W // 2, 302), "v2.6  ·  works offline", font=font(MONO, 13), fill="#6a6a6a", anchor="ms")
    return im


def kit_box(rng, name, sub, col):
    W, H = 256, 192
    im = card(W, H, col, rng, 5)
    d = ImageDraw.Draw(im)
    dark = col in ("#f0ece0", "#e9e2cf", "#c9ccd1", "#9fc8d8", "#d9b43c")
    fg = INK if dark else "#f2ede0"
    d.rectangle((0, H - 46, W, H), fill="#f2ede0" if not dark else "#2b2f36")
    d.text((16, 60), name, font=font(INTER, 28 if len(name) < 10 else 22), fill=fg, anchor="ls")
    d.text((16, 96), sub, font=font(INTER, 22), fill=fg, anchor="ls")
    d.rounded_rectangle((W - 70, 100, W - 18, 140), 8, outline=fg, width=4)  # the product, drawn as a line icon
    d.line((W - 60, 108, W - 28, 132), fill=fg, width=3)
    for k in range(12):  # a barcode
        x = 20 + k * 6 + rng.choice((0, 1, 2))
        d.line((x, H - 38, x, H - 10), fill=INK if not dark else "#f2ede0", width=rng.choice((1, 2, 3)))
    return im


def sign_we_fix(rng):
    im = card(900, 600, "#f4d23c", rng, 8)
    d = ImageDraw.Draw(im)
    hand_text(d, rng, (450, 230), "WE FIX", 190, INK, stroke=6, anchor="m")
    hand_text(d, rng, (450, 430), "APPS", 210, "#1f4f8f", stroke=7, anchor="m")
    hand_text(d, rng, (450, 545), "(the ones they broke)", 54, INK, path=HAND, stroke=1, anchor="m")
    return tape(im, rng)


def sign_screen(rng):
    im = card(700, 900, "#f2efe6", rng, 8)
    d = ImageDraw.Draw(im)
    hand_text(d, rng, (350, 190), "SCREEN", 150, "#1f4f8f", stroke=5, anchor="m")
    hand_text(d, rng, (350, 350), "REPAIR", 150, "#1f4f8f", stroke=5, anchor="m")
    d.line((80, 400, 620, 410), fill=INK, width=6)
    hand_text(d, rng, (350, 560), "while you", 100, INK, path=HAND, stroke=2, anchor="m")
    hand_text(d, rng, (350, 690), "wait", 120, INK, path=HAND, stroke=2, anchor="m")
    hand_text(d, rng, (350, 840), "most phones · 1 hr", 52, "#3d6b3a", stroke=1, anchor="m")
    return tape(im, rng)


def price_list(rng):
    im = card(620, 880, "#f7f4ea", rng, 6)
    d = ImageDraw.Draw(im)
    for y in range(160, 880, 58):  # ruled paper
        d.line((0, y, 620, y), fill="#b9cfe0", width=2)
    d.line((70, 0, 70, 880), fill="#a8b8c8", width=2)
    hand_text(d, rng, (310, 110), "PRICES", 96, INK, stroke=3, anchor="m")
    rows = [("cracked screen", "$49"), ("battery swap", "$35"), ("charging port", "$30"), ("water damage", "ask"),
            ("data rescue", "$40"), ("app won't open", "$5"), ("app shut down", "we'll try"),
            ("old phone setup", "$15"), ("cases", "$8+"), ("diagnosis", "free")]
    for k, (a, b) in enumerate(rows):
        y = 210 + k * 58
        hand_text(d, rng, (86, y), a, 44, INK, path=HAND, stroke=1)
        hand_text(d, rng, (590, y), b, 44, "#1f4f8f", path=HAND, stroke=1, anchor="r")
    return tape(im, rng)


def first_dollar(rng):
    """A framed note: a plain made-up green bill (a '1' and a seal, no real currency design), and the date in pen."""
    im = Image.new("RGB", (640, 480), "#3a2a1c")
    d = ImageDraw.Draw(im)
    d.rectangle((26, 26, 614, 454), fill="#efe8d6")
    d.rectangle((120, 110, 520, 290), fill="#c9d3b4", outline="#4b5e3f", width=6)
    d.rectangle((140, 128, 500, 272), outline="#6b7e5a", width=2)
    d.ellipse((280, 150, 360, 230), outline="#4b5e3f", width=5)
    for x, y in ((165, 165), (475, 165), (165, 245), (475, 245)):
        d.text((x, y), "1", font=font(INTER, 40), fill="#3c5032", anchor="mm")
    hand_text(d, rng, (320, 370), "first dollar", 66, INK, path=HAND, stroke=1, anchor="m")
    hand_text(d, rng, (320, 425), "June 2008", 48, INK, path=HAND, stroke=1, anchor="m")
    return im


def sign_open(rng):
    im = card(600, 300, "#f2efe6", rng, 8)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 14, 586, 286), 20, outline="#2a4d8f", width=10)
    hand_text(d, rng, (300, 170), "OPEN", 150, "#2a4d8f", stroke=5, anchor="m")
    hand_text(d, rng, (300, 250), "knock if I'm in back", 40, INK, path=HAND, stroke=1, anchor="m")
    return im


def sign_small(rng, lines, col="#f2efe6", ink=INK, w=500, h=320, size=60):
    im = card(w, h, col, rng, 8)
    d = ImageDraw.Draw(im)
    n = len(lines)
    for k, (t, kind) in enumerate(lines):
        y = h * (k + 0.75) / (n + 0.25)
        hand_text(d, rng, (w / 2, y), t, size if kind == "big" else int(size * 0.62),
                  ink if kind == "big" else "#3a3a3a", path=INTER if kind == "big" else HAND,
                  stroke=3 if kind == "big" else 1, anchor="m")
    return tape(im, rng)


def pegboard(rng):
    im = Image.new("RGB", (1024, 512), "#9a7a52")
    d = ImageDraw.Draw(im)
    for y in range(10, 512, 24):
        for x in range(10, 1024, 24):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill="#3a2a1a")
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    d = ImageDraw.Draw(im, "RGBA")  # tool outlines drawn in marker where tools hang (the Dev's habit)
    for x, y, w, h in ((80, 80, 30, 200), (160, 80, 30, 200), (240, 70, 60, 150), (700, 300, 160, 40), (880, 90, 40, 220)):
        d.rounded_rectangle((x, y, x + w, y + h), 10, outline=(20, 20, 20, 200), width=4)
    return im


def phone_screens(rng):
    """Phone and tablet faces, dark (the shop's display phones are off): glass, a notch, a reflection."""
    im = Image.new("RGB", (256, 256), "#101317")
    d = ImageDraw.Draw(im)
    d.polygon([(0, 0), (120, 0), (40, 256), (0, 256)], fill="#1a1f26")
    return im


# ---------------------------------------------------------------- the eatery

def chalk_menu(rng):
    W, H = 2048, 600
    im = Image.new("RGB", (W, H), "#20302a")
    px = ImageDraw.Draw(im, "RGBA")
    for _ in range(260):  # old chalk, wiped
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        px.ellipse((x - 60, y - 20, x + 60, y + 20), fill=(220, 230, 220, rng.randint(3, 9)))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, H - 1), outline="#6b4a2c", width=22)
    wh, ye, gr, bl = "#eceee6", "#f2dc7a", "#a8d8a0", "#a8cce8"
    hand_text(d, rng, (W / 2, 96), "TURO-TURO  ·  point & pick", 70, ye, path=HAND, stroke=2, anchor="m")
    cols = [
        ("WITH RICE", wh, [("1 ulam + rice", "10.50"), ("2 ulam + rice", "13.50"), ("3 ulam + rice", "16.00"),
                           ("ulam only, small", "7.00"), ("extra rice", "2.50")]),
        ("SILOG  all day", gr, [("tapsilog", "13.00"), ("longsilog", "12.50"), ("bangsilog", "14.00"),
                                ("tocilog", "12.50"), ("extra egg", "1.50")]),
        ("MERIENDA", bl, [("lumpia (6)", "6.00"), ("turon", "3.00"), ("puto (3)", "3.50"),
                          ("halo-halo  wknd", "7.00"), ("champorado", "4.50")]),
    ]
    for c, (head, hc, rows) in enumerate(cols):
        x0 = 60 + c * 660
        hand_text(d, rng, (x0, 200), head, 64, hc, path=INTER, stroke=2)
        d.line((x0, 220, x0 + 560, 224), fill=hc, width=4)
        for k, (a, b) in enumerate(rows):
            y = 290 + k * 66
            hand_text(d, rng, (x0, y), a, 60, wh, path=HAND, stroke=1)
            hand_text(d, rng, (x0 + 580, y), b, 56, ye, path=HAND, stroke=1, anchor="r")
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    return im


DISHES = [  # (card label, plate colours): the six pans, in order along the steam table
    ("1  ADOBO", ["#4a2f1c", "#6a4428", "#2e1d12"]),
    ("2  PANCIT", ["#d9b778", "#c79b55", "#6b8f3a", "#e0913a"]),
    ("3  PINAKBET", ["#5d7a32", "#d48a2c", "#7a5a2a", "#8a9a40"]),
    ("4  FRIED BANGUS", ["#b8783a", "#d89a50", "#8a5428"]),
    ("5  LUMPIA", ["#c88a3a", "#e0a858", "#a8702c"]),
    ("6  MENUDO", ["#a85a2a", "#d08a3a", "#e6c46a"]),
]


def dish_card(rng, label, cols):
    W, H = 480, 360
    im = card(W, H, "#f4f0e4", rng, 6)
    d = ImageDraw.Draw(im)
    d.rectangle((20, 20, W - 20, 280), fill="#3a3430")  # the photo
    d.ellipse((90, 40, 390, 270), fill="#f4f1ea", outline="#d8d2c4", width=5)
    for _ in range(26):
        x, y = rng.uniform(150, 330), rng.uniform(80, 230)
        r = rng.uniform(14, 36)
        d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=rng.choice(cols))
    d.ellipse((300, 60, 370, 110), fill="#f6f6f2")  # the rice
    im.paste(im.crop((20, 20, W - 20, 280)).filter(ImageFilter.GaussianBlur(2)), (20, 20))
    d = ImageDraw.Draw(im)
    hand_text(d, rng, (W / 2, 335), label, 44, INK, stroke=1, anchor="m", jitter=0.5)
    return tape(im, rng)


def drinks(rng):
    return sign_small(rng, [("DRINKS", "big"), ("calamansi  3.00", "s"), ("sago't gulaman  3.50", "s"),
                            ("buko juice  4.00", "s"), ("canned soda  2.00", "s"), ("water  1.50", "s")],
                      col="#f4e9b8", w=520, h=640, size=84)


def bus_note(rng):
    return sign_small(rng, [("PLEASE BUS", "big"), ("your tray. salamat po!", "s")], col="#f7f4ea", w=600,
                      h=260, size=72)


def cash_note(rng):
    return sign_small(rng, [("CARD MIN $10", "big"), ("cash is ok too :)", "s")], col="#fff6c8", w=520, h=260, size=62)


def calendar(rng):
    W, H = 400, 600
    im = card(W, H, "#f6f3ea", rng, 4)
    d = ImageDraw.Draw(im)
    # the picture: a beach at noon
    d.rectangle((16, 16, W - 16, 300), fill="#6fb3d9")
    d.rectangle((16, 200, W - 16, 300), fill="#2e8fb0")
    d.polygon([(16, 260), (W - 16, 230), (W - 16, 300), (16, 300)], fill="#e8d9a8")
    for k in range(3):
        x = 60 + k * 30
        d.line((x, 280, x + 20, 120 + k * 10), fill="#6a4a2a", width=6)
        for a in range(6):
            ang = a * math.pi / 3
            d.line((x + 20, 120 + k * 10, x + 20 + math.cos(ang) * 50, 120 + k * 10 + math.sin(ang) * 25),
                   fill="#2f6b2a", width=8)
    d.rectangle((16, 320, W - 16, 360), fill="#2a4d8f")
    for r in range(5):
        for c in range(7):
            n = r * 7 + c - 2
            if 1 <= n <= 31:
                d.text((40 + c * 52, 395 + r * 44), str(n), font=font(INTER, 22), fill=INK if c else "#2a4d8f",
                       anchor="mm")
    return im


def landscape(rng):
    """A framed print: rice terraces in the morning."""
    W, H = 600, 420
    im = Image.new("RGB", (W, H), "#4a3020")
    d = ImageDraw.Draw(im)
    d.rectangle((24, 24, W - 24, H - 24), fill="#cfe2ea")
    d.polygon([(24, 200), (200, 110), (380, 170), (576, 90), (576, 396), (24, 396)], fill="#6a8a6a")
    for k in range(9):
        y = 180 + k * 26
        col = ["#7fa64a", "#6d9a3e", "#8fb85a"][k % 3]
        d.polygon([(24, y + 20), (200, y - 10 + k * 3), (380, y + 8), (576, y - 20), (576, y + 6), (380, y + 34),
                   (200, y + 16 + k * 3), (24, y + 46)], fill=col)
        d.line([(24, y + 20), (200, y - 10 + k * 3), (380, y + 8), (576, y - 20)], fill="#4e7330", width=3)
    return im.filter(ImageFilter.GaussianBlur(0.8))


def tv_picture(rng):
    """A made-up variety show: a stage, two blobs of hosts, a lower-third band (no words)."""
    W, H = 400, 300
    im = Image.new("RGB", (W, H), "#2a3a6a")
    d = ImageDraw.Draw(im)
    for k in range(9):
        d.polygon([(200, 120), (k * 50 - 20, 0), (k * 50 + 10, 0)], fill="#3c5aa0")
    d.ellipse((60, 240, 340, 320), fill="#e0b84a")
    d.ellipse((120, 110, 170, 160), fill="#c69c7d")
    d.rounded_rectangle((105, 160, 185, 260), 20, fill="#f2efe6")
    d.ellipse((230, 105, 280, 155), fill="#8a6a50")
    d.rounded_rectangle((215, 155, 295, 260), 20, fill="#2f7f7a")
    d.rectangle((0, 240, W, 280), fill="#f4d23c")
    d.rectangle((10, 250, 200, 270), fill="#2a4d8f")
    return im.filter(ImageFilter.GaussianBlur(1.2))


# ---------------------------------------------------------------- the other shops

SHOP_SIGNS = {  # shop index: [(lines...), card colour] in their windows
    2: [([("KNIVES", "big"), ("sharpened Saturdays", "s")], "#f2efe6"), ([("CAST IRON", "big"), ("restored", "s")], "#f4e9b8")],
    3: [([("FRESH LOAVES", "big"), ("daily from 7", "s")], "#f4e9b8"), ([("FREE STARTER", "big"), ("bring a jar", "s")], "#f2efe6")],
    4: [([("WE BUY GOLD", "big"), ("fair prices", "s")], "#f4d23c"), ([("LOANS", "big"), ("guitars · tools · TVs", "s")], "#f2efe6"),
        ([("NO ITEM", "big"), ("held over 90 days", "s")], "#f2efe6")],
    5: [([("RUN CLUB", "big"), ("Thursdays 6:30", "s")], "#cfe8d0"), ([("SHOE FITTING", "big"), ("free gait check", "s")], "#f2efe6")],
    6: [([("YARN SALE", "big"), ("2nd skein half off", "s")], "#e6d4ec"), ([("STITCH NIGHT", "big"), ("Tuesdays, all welcome", "s")], "#f2efe6")],
    7: [([("SEEDS & STARTS", "big"), ("tomatoes are in", "s")], "#d8ecc8"), ([("SOIL $8", "big"), ("compost $10", "s")], "#f2efe6")],
    8: [([("CLASSES", "big"), ("Saturday mornings", "s")], "#f4e9b8"), ([("CUSTOM SHELVES", "big"), ("ask inside", "s")], "#f2efe6")],
    10: [([("ASK US", "big"), ("we'll cite sources", "s")], "#f2efe6"), ([("MAPS · BOOKS", "big"), ("prints & letters", "s")], "#e9dcc0")],
    11: [([("POUR OVER $4", "big"), ("drip $2.50", "s")], "#f2efe6"), ([("BEANS", "big"), ("roasted here Mondays", "s")], "#e9dcc0")],
    12: [([("PLANT CLINIC", "big"), ("Sundays, bring it in", "s")], "#d8ecc8"), ([("CUTTINGS $3", "big"), ("pothos · monstera", "s")], "#f2efe6")],
    13: [([("GAME NIGHT", "big"), ("Fridays 7pm", "s")], "#cfe0f0"), ([("OPEN TABLES", "big"), ("play before you buy", "s")], "#f2efe6")],
    14: [([("CROCHET CIRCLE", "big"), ("Wednesdays", "s")], "#ecd8e4"), ([("COMMISSIONS", "big"), ("open, ask inside", "s")], "#f2efe6")],
}
GAME_COLS = ["#2a4d8f", "#3d6b3a", "#d9b43c", "#6a4c93", "#2f7f7a", "#e0913a", "#1f6f9f", "#4b4f3a", "#c9ccd1",
             "#8a6d5a", "#f2efe6", "#2b2f36"]
GAME_NAMES = ["Harbor Lights", "Moss & Stone", "Tide Market", "Hollow Pines", "Lighthouse", "Copper Road", "Night Train",
              "Orchard", "Ten Bridges", "Kiln", "Seven Winds", "Lantern Fair"]


def game_box(rng, k):
    W, H = 320, 240
    col = GAME_COLS[k % len(GAME_COLS)]
    im = card(W, H, col, rng, 6)
    d = ImageDraw.Draw(im)
    for _ in range(5):
        x, y, r = rng.uniform(0, W), rng.uniform(60, H), rng.uniform(20, 70)
        d.ellipse((x - r, y - r, x + r, y + r), fill=rng.choice(GAME_COLS))
    d.rectangle((0, 0, W, 64), fill="#f2efe6")
    d.text((W / 2, 46), GAME_NAMES[k], font=font(INTER, 34 if len(GAME_NAMES[k]) < 12 else 28), fill=INK, anchor="ms")
    d.text((W - 12, H - 12), "2-4  ·  45 min", font=font(INTER, 16), fill="#f2efe6", anchor="rs", stroke_width=2,
           stroke_fill=INK)
    return im


def old_map(rng):
    W, H = 800, 560
    im = card(W, H, "#e3d3a8", rng, 14)
    d = ImageDraw.Draw(im)
    pts = [(rng.uniform(100, 700), rng.uniform(80, 480)) for _ in range(5)]
    for x, y in pts:
        r = [rng.uniform(60, 150) for _ in range(12)]
        poly = [(x + r[k] * math.cos(k * math.pi / 6), y + r[k] * 0.7 * math.sin(k * math.pi / 6)) for k in range(12)]
        d.polygon(poly, fill="#cdb98a", outline="#6a5030")
    for k in range(1, 8):
        d.line((k * 100, 0, k * 100, H), fill="#b8a07a", width=1)
    for k in range(1, 6):
        d.line((0, k * 100, W, k * 100), fill="#b8a07a", width=1)
    d.ellipse((620, 380, 760, 520), outline="#6a5030", width=3)
    d.line((690, 380, 690, 520), fill="#6a5030", width=2)
    d.line((620, 450, 760, 450), fill="#6a5030", width=2)
    d.rectangle((0, 0, W - 1, H - 1), outline="#4a3020", width=16)
    return im.filter(ImageFilter.GaussianBlur(0.6))


def lobby_tag(rng):
    """The tower's display placard: thin, grey, blank-faced."""
    im = Image.new("RGB", (800, 200), "#f4f6f8")
    d = ImageDraw.Draw(im)
    d.text((400, 92), "NEW  ·  OFFICIAL", font=font(INTER, 64), fill="#8a939c", anchor="ms")
    d.text((400, 160), "Now with fewer features.", font=font(INTER, 34), fill="#b0b8c0", anchor="ms")
    return im


# ---------------------------------------------------------------- packing

def pack(name, items, W=2048):
    """Shelf-pack images into one atlas; writes <name>.png and <name>.json (UV rects, Blender's origin bottom left)."""
    order = sorted(items.items(), key=lambda kv: -kv[1].size[1])
    x = y = row_h = 0
    pos = {}
    for k, im in order:
        w, h = im.size
        if x + w + 4 > W:
            x, y, row_h = 0, y + row_h + 4, 0
        pos[k] = (x, y)
        x += w + 4
        row_h = max(row_h, h)
    H = 1
    while H < y + row_h:
        H *= 2
    atlas = Image.new("RGB", (W, H), "#808080")
    rects = {}
    for k, im in order:
        px, py = pos[k]
        atlas.paste(im, (px, py))
        w, h = im.size
        rects[k] = [(px + 0.5) / W, 1 - (py + h - 0.5) / H, (px + w - 0.5) / W, 1 - (py + 0.5) / H, w / h]
    OUT.mkdir(parents=True, exist_ok=True)
    atlas.save(OUT / f"{name}.png")
    (OUT / f"{name}.json").write_text(json.dumps(rects, indent=0))
    print(name, atlas.size, len(rects))


def main():
    rng = random.Random(SEED)
    dev = {f"app{k}": app_box(rng, *a) for k, a in enumerate(APPS)}
    dev.update({f"kit{k}": kit_box(rng, *a) for k, a in enumerate(KITS)})
    dev.update({"we_fix": sign_we_fix(rng), "screen": sign_screen(rng), "prices": price_list(rng),
                "dollar": first_dollar(rng), "open": sign_open(rng), "pegboard": pegboard(rng),
                "phone": phone_screens(rng),
                "nosoft": sign_small(rng, [("NO REFUNDS", "big"), ("on software (it's free)", "s")]),
                "since": sign_small(rng, [("SINCE 2008", "big"), ("same guy, same counter", "s")], col="#cfe8d0"),
                "backsoon": sign_small(rng, [("BACK IN 5", "big"), ("(really)", "s")], col="#fff6c8", w=400, h=260)})
    pack("dev", dev)
    eat = {"menu": chalk_menu(rng), "drinks": drinks(rng), "bus": bus_note(rng), "cash": cash_note(rng),
           "calendar": calendar(rng), "landscape": landscape(rng), "tv": tv_picture(rng)}
    eat.update({f"dish{k}": dish_card(rng, *dd) for k, dd in enumerate(DISHES)})
    pack("eatery", eat)
    shops = {}
    for i, signs in SHOP_SIGNS.items():
        for k, (lines, col) in enumerate(signs):
            shops[f"s{i}_{k}"] = sign_small(rng, lines, col=col, w=560, h=340, size=70)
    shops.update({f"game{k}": game_box(rng, k) for k in range(len(GAME_NAMES))})
    shops["map"] = old_map(rng)
    pack("shops", shops)
    lob = {f"copy{k}": app_box(rng, *a, copy=True) for k, a in enumerate(APPS)}
    lob["tag"] = lobby_tag(rng)
    pack("lobby", lob, W=1024)


if __name__ == "__main__":
    main()
