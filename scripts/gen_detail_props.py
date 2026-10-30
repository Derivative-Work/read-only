"""The detail pass's printed and handwritten surfaces for the gags' props (scenes/blender/sets/props.py), drawn with
PIL from a fixed seed. Handwriting is Oooh Baby (OFL, vendored from Not Yet); print is Inter and JetBrains Mono.

  calpage_NN.png   S06: a tear-off wall calendar's daily pages, JUNE 1 .. JUNE 28 in steps of 3 (the deadline is
                   June 30, 2023: the board behind them, calboard.png, shows it, ringed)
  receipt.png      S09: three strips of adding-machine tape, "0.24 +" down the columns, the total at the bottom,
                   stapled up as an eviction notice
  sticky_NN.png    S31: yellow sticky notes, "thanks, this worked" (a few in other hands and words)
  goodbot_NN.png   S39a: sticky notes, "good bot"
  payroll.png      S32: a kraft pay envelope printed PAYROLL, its amount line empty
  cassette.png     S11-S13: the cassette's label, handwritten
  envelope.png     S06: the envelope through the mail slot: a window, a printed return block, a metered postage mark

Writes assets/gen/detail/props/*.png. Usage: .venv/bin/python -I scripts/gen_detail_props.py
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path("assets/gen/detail/props")
FONTS = Path("assets/fonts")
SEED = 20261031
HAND = str(FONTS / "OoohBaby-Regular.ttf")
SANS = str(FONTS / "Inter-Medium-flat.ttf")
MONO = str(FONTS / "JetBrainsMono-SemiBold-flat.ttf")
INKS = ["#1b2a6b", "#151515", "#2a2a2a", "#3a2a6b"]


def font(path, size):
    return ImageFont.truetype(path, size)


def paper(w, h, col, rng, grain=10):
    im = Image.new("RGB", (w, h), col)
    px = im.load()
    for _ in range(w * h // 40):
        x, y = rng.randrange(w), rng.randrange(h)
        r, g, b = px[x, y]
        d = rng.randint(-grain, grain)
        px[x, y] = (max(0, r + d), max(0, g + d), max(0, b + d))
    return im.filter(ImageFilter.GaussianBlur(0.6))


def calpages(rng):
    for k in range(10):
        day = 1 + 3 * k
        im = paper(600, 800, (244, 241, 232), rng)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 600, 150), fill=(34, 60, 96))
        d.text((300, 78), "JUNE", font=font(SANS, 96), fill=(244, 241, 232), anchor="mm")
        d.text((300, 440), str(day), font=font(SANS, 380), fill=(30, 30, 30), anchor="mm")
        wd = ["THURSDAY", "SUNDAY", "WEDNESDAY", "SATURDAY", "TUESDAY", "FRIDAY", "MONDAY", "THURSDAY", "SUNDAY",
              "WEDNESDAY"][k]  # June 2023
        d.text((300, 690), wd, font=font(SANS, 52), fill=(90, 90, 90), anchor="mm")
        for y in (8, 14):  # the perforation at the top
            for x in range(10, 600, 16):
                d.ellipse((x, 150 + y - 2, x + 4, 150 + y + 2), fill=(200, 196, 186))
        im.save(OUT / f"calpage_{k:02d}.png")
    im = paper(600, 800, (244, 241, 232), rng)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 600, 150), fill=(34, 60, 96))
    d.text((300, 78), "JUNE", font=font(SANS, 96), fill=(244, 241, 232), anchor="mm")
    d.text((300, 440), "30", font=font(SANS, 380), fill=(30, 30, 30), anchor="mm")
    d.text((300, 690), "FRIDAY", font=font(SANS, 52), fill=(90, 90, 90), anchor="mm")
    for k in range(3):  # ringed by hand, three times round
        r = 225 + k * 9
        d.ellipse((300 - r - 30, 450 - r + 25, 300 + r + 20, 450 + r - 15), outline=(26, 42, 107), width=7)
    im.save(OUT / "calboard.png")


def receipt(rng):
    W, H = 1000, 1400
    im = Image.new("RGB", (W, H), (60, 52, 44))
    d = ImageDraw.Draw(im)
    f = font(MONO, 34)
    for s in range(3):
        x0 = 40 + s * 320
        strip = paper(290, H - 40, (247, 243, 228), rng, 6)
        sd = ImageDraw.Draw(strip)
        y = 30
        total = 0.0
        while y < H - 200:
            total += 0.24
            sd.text((250, y), f"0.24 +", font=f, fill=(70, 70, 80), anchor="ra")
            y += 42
        if s == 2:
            sd.line((30, y + 10, 260, y + 10), fill=(70, 70, 80), width=3)
            sd.text((268, y + 30), "20,000,000.00 *", font=font(MONO, 23), fill=(40, 40, 50), anchor="ra")
        im.paste(strip.rotate(rng.uniform(-1.2, 1.2), expand=False, fillcolor=(60, 52, 44)), (x0, 20))
        for yy in (40, H - 90):  # staples
            d.rectangle((x0 + 110, yy, x0 + 180, yy + 8), fill=(180, 182, 186))
    # the number written on it (S09, "an eviction with a number written on"): red marker across the strips, ringed
    big = next(font(HAND, s) for s in range(190, 60, -5)  # the largest that fits inside the ring (190 ran off the edges)
               if d.textlength("$20,000,000", font=font(HAND, s)) <= W - 220)
    d.text((W / 2, H * 0.47), "$20,000,000", font=big, fill=(196, 24, 24), anchor="mm", stroke_width=5,
           stroke_fill=(196, 24, 24))
    d.ellipse((40, H * 0.47 - 150, W - 40, H * 0.47 + 150), outline=(196, 24, 24), width=12)
    d.text((W / 2, H * 0.47 + 230), "due June 30", font=font(HAND, 110), fill=(196, 24, 24), anchor="mm")
    im.save(OUT / "receipt.png")


def sticky(text, rng, name, ink=None, col=None):
    col = col or rng.choice([(250, 226, 96), (252, 232, 120), (246, 218, 88)])
    im = paper(512, 512, col, rng, 8)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 512, 70), fill=tuple(max(0, c - 18) for c in col))  # the gummed strip, a shade darker
    ink = ink or rng.choice(INKS)
    words = text.split()
    lines, cur = [], ""
    f = font(HAND, rng.randint(84, 104))
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > 440 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    y = 270 - len(lines) * 55
    for ln in lines:
        d.text((256 + rng.randint(-12, 12), y), ln, font=f, fill=ink, anchor="ma")
        y += 110
    im = im.rotate(rng.uniform(-3, 3), resample=Image.BICUBIC, fillcolor=col)
    im.save(OUT / f"{name}.png")


def payroll(rng):
    im = paper(1200, 560, (196, 160, 112), rng, 12)
    d = ImageDraw.Draw(im)
    d.text((80, 70), "PAYROLL", font=font(SANS, 120), fill=(60, 40, 24))
    for k, lab in enumerate(("NAME", "PERIOD", "AMOUNT")):
        y = 250 + k * 90
        d.text((80, y), lab, font=font(SANS, 44), fill=(60, 40, 24))
        d.line((330, y + 46, 1100, y + 46), fill=(60, 40, 24), width=4)
    d.text((360, 200), "the mods", font=font(HAND, 90), fill=(21, 21, 21))
    im.save(OUT / "payroll.png")


def cassette(rng):
    """The label over the cassette's face (90 x 42 mm of it): writing lines, an orange band, side A, and a
    transparent cut-out where the modelled window and reels show through (props.cassette lines them up)."""
    W, H = 1000, 467
    im = paper(W, H, (240, 236, 222), rng, 6).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 300, W, 400), fill=(224, 120, 40))  # the band across the bottom of the label
    d.rectangle((0, 400, W, 412), fill=(40, 40, 44))
    d.text((40, 20), "A", font=font(SANS, 110), fill=(30, 30, 30))
    for k in range(2):
        d.line((140, 110 + k * 62, 960, 110 + k * 62), fill=(150, 150, 160), width=3)
    d.text((150, 6), "PHONE CALL", font=font(HAND, 120), fill=(21, 30, 90))
    d.text((520, 105), "do not tape over!", font=font(HAND, 64), fill=(170, 20, 20))
    d.text((40, 420), "C-60   NORMAL POSITION", font=font(SANS, 30), fill=(60, 60, 60))
    cut = Image.new("L", (W, H), 255)  # the window: alpha 0 inside
    ImageDraw.Draw(cut).rounded_rectangle((211, 190, 789, 368), 60, fill=0)
    im.putalpha(cut)
    ImageDraw.Draw(im).rounded_rectangle((207, 186, 793, 372), 64, outline=(30, 30, 30, 255), width=8)
    im.save(OUT / "cassette.png")


def envelope(rng):
    im = paper(1100, 520, (246, 244, 238), rng, 5)
    d = ImageDraw.Draw(im)
    for k in range(3):
        d.rectangle((60, 60 + k * 34, 360, 76 + k * 34), fill=(150, 150, 150))  # the return block, unreadable
    d.rectangle((300, 240, 820, 420), outline=(180, 180, 180), width=4)  # the window
    d.rectangle((330, 280, 640, 300), fill=(120, 120, 120))
    d.rectangle((330, 320, 700, 340), fill=(120, 120, 120))
    d.rectangle((860, 50, 1050, 160), outline=(60, 60, 140), width=5)  # a metered postage mark
    d.text((955, 105), "POSTAGE\nPAID", font=font(SANS, 30), fill=(60, 60, 140), anchor="mm", align="center")
    d.text((60, 470), "IMPORTANT: NEW PRICING", font=font(SANS, 34), fill=(30, 30, 30))
    im.save(OUT / "envelope.png")


def tape_strip(rng):
    """The adding machine's paper tape, a tile 57 mm wide x 228 mm long (props.tape_run repeats it along the run):
    "0.24 +" printed along it (not across, as a real one prints: S13 sees it from the side and it has to read),
    big, a little uneven."""
    W, H = 1024, 256  # drawn lying along the run, turned upright for the UVs below
    im = paper(W, H, (247, 243, 228), rng, 6)
    d = ImageDraw.Draw(im)
    f = font(MONO, 96)
    for k in range(3):
        ink = (50 + rng.randint(-10, 10), 50, 65)
        d.text((W * (k + 0.5) / 3, H / 2), "0.24+", font=f, fill=ink, anchor="mm")
    im = im.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)  # read from the shop side (S13)
    im.save(OUT / "tape_strip.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    calpages(rng)
    receipt(rng)
    notes = ["thanks, this worked"] * 6 + ["thanks, this worked!", "this worked, thank you", "3am. this worked. thanks",
                                           "thanks!! this worked"]
    for k, t in enumerate(notes):
        sticky(t, rng, f"sticky_{k:02d}")
    for k, t in enumerate(["good bot", "good bot.", "good bot", "Good bot", "good bot <3", "good bot",
                           "good bot.", "good bot", "Good bot.", "good bot"]):
        sticky(t, rng, f"goodbot_{k:02d}", col=rng.choice([(250, 226, 96), (246, 186, 210), (180, 220, 250),
                                                           (200, 240, 170)]))
    payroll(rng)
    cassette(rng)
    envelope(rng)
    tape_strip(random.Random(SEED + 7))
    print(len(list(OUT.glob("*.png"))), "textures ->", OUT)


if __name__ == "__main__":
    main()
