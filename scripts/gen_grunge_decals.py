"""The grunge pass's decals (style spec, "Grime"): made-up graffiti tags and torn wheatpaste posters, drawn here with
PIL from a fixed seed, so they're regenerable and copy nobody's work.

- Tags: looping marker and spray strokes with an outline and the odd drip. Shapes only, no letters or words (style
  spec, "Graffiti": no real tags). Never the REC red or Reddit's orange-red.
- Posters: gig-flyer layouts of colour blocks, circles and grey bars where text would be (no text), with torn,
  ragged edges, fading and creases; a few are torn half away, with an older poster's scrap showing beneath.

Writes assets/gen/grunge/{tag,poster}_NN.png (RGBA). Usage: .venv/bin/python -I scripts/gen_grunge_decals.py
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

OUT = Path("assets/gen/grunge")
SEED = 20261030
TAG_COLS = ["#f2f2ee", "#111111", "#c9ccd1", "#e85aa8", "#3f8fe0", "#f4d23c", "#8fe04a", "#7a4fd8", "#2ec4b6"]
POSTER_COLS = ["#f4d23c", "#e85aa8", "#3f8fe0", "#f2efe6", "#2ec4b6", "#8fe04a", "#1b1b1b", "#f0a35e", "#7a4fd8"]


def bez(p0, p1, p2, p3, n=40):
    for k in range(n + 1):
        t = k / n
        u = 1 - t
        yield (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
               u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def tag(rng, W=1024, H=512):
    """A looping, illegible tag: one continuous stroke of joined Bezier loops, outlined, with a few drips."""
    fill, line = rng.sample(TAG_COLS, 2)
    pts, x = [], rng.uniform(80, 140)
    y = H * rng.uniform(0.45, 0.6)
    while x < W - 140:
        nx = x + rng.uniform(40, 110)
        ny = H * rng.uniform(0.3, 0.65)
        c1 = (x + rng.uniform(-90, 60), y - rng.uniform(110, 190) * rng.choice((-1, 1)))
        c2 = (nx + rng.uniform(-60, 90), ny + rng.uniform(110, 190) * rng.choice((-1, 1)))
        pts += list(bez((x, y), c1, c2, (nx, ny)))
        x, y = nx, ny
    w = rng.randint(30, 52)
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.line(pts, fill=line, width=w + 14, joint="curve")
    d.line(pts, fill=fill, width=w, joint="curve")
    for _ in range(rng.randint(2, 6)):  # drips from the stroke's low points
        px, py = rng.choice(pts)
        d.line([(px, py), (px, py + rng.uniform(40, 160))], fill=fill, width=rng.randint(4, 8))
    if rng.random() < 0.6:  # an underline swoosh with an arrowhead
        y0 = H * 0.85
        d.line([(120, y0), (W - 200, y0 - 30)], fill=line, width=w // 2 + 6)
        d.polygon([(W - 200, y0 - 60), (W - 120, y0 - 34), (W - 200, y0 + 4)], fill=line)
    return wear(rng, img, 0.75)


def throwup(rng, W=1024, H=512):
    """A bubble throw-up: a row of fat overlapping rounded blobs, outlined and shadowed. It reads as bubble
    lettering at a glance, but the blobs are only shapes."""
    fill, line = rng.sample(TAG_COLS, 2)
    n = rng.randint(3, 5)
    blobs, x = [], 90
    for _ in range(n):
        w, h = rng.uniform(150, 230), rng.uniform(230, 360)
        y = H / 2 + rng.uniform(-40, 40)
        blobs.append([x, y - h / 2, x + w, y + h / 2])
        x += w * rng.uniform(0.6, 0.8)
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for b in blobs:  # drop shadow, outline, fill
        d.rounded_rectangle([b[0] + 22, b[1] + 22, b[2] + 22, b[3] + 22], 70, fill="#111111")
    for b in blobs:
        d.rounded_rectangle([b[0] - 14, b[1] - 14, b[2] + 14, b[3] + 14], 80, fill=line)
    for b in blobs:
        d.rounded_rectangle(b, 70, fill=fill)
        d.ellipse([b[0] + 30, b[1] + 30, b[0] + 70, b[1] + 90], fill="#ffffff")  # the shine
        if rng.random() < 0.5:
            cx = (b[0] + b[2]) / 2
            d.rounded_rectangle([cx - 22, b[1] + 70, cx + 22, b[3] - 70], 20, fill=line)  # a counter
    img = img.resize((W, H)).transform((W, H), Image.AFFINE, (1, rng.uniform(-0.25, 0.25), 0, 0, 1, 0))
    return wear(rng, img, 0.7)


def wear(rng, img, keep):
    """Fade and flake: multiply alpha by thresholded noise, so the paint is patchy as on a real wall."""
    W, H = img.size
    n = Image.effect_noise((W // 8, H // 8), 64).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
    fine = Image.effect_noise((W, H), 90)
    m = ImageChops.add(n, fine, scale=2.0).point(lambda v: 255 if v > 128 * (1 - keep) + 30 else 90)
    a = ImageChops.multiply(img.getchannel("A"), m)
    img.putalpha(a)
    return img


def torn_mask(rng, W, H, bite=0.0):
    """A ragged-edged sheet; bite > 0 tears a diagonal chunk off one corner."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    edge = []
    for side in range(4):
        for k in range(24):
            t = k / 24
            j = rng.uniform(4, 22)
            edge.append([(t * W, j), (W - j, t * H), (W - t * W, H - j), (j, H - t * H)][side])
    d.polygon(edge, fill=255)
    if bite:
        x0 = rng.uniform(0.3, 0.7) * W
        d.polygon([(x0, H), (W, H * (1 - bite)), (W, H)], fill=0)
        d.polygon([(x0 + rng.uniform(-30, 30), H), (W * 0.9, H), (W, H * (1 - bite) - 40)], fill=0)
    return m


def poster(rng, W=600, H=800):
    bg, a, b = rng.sample(POSTER_COLS, 3)
    img = Image.new("RGBA", (W, H), bg)
    d = ImageDraw.Draw(img)
    layout = rng.randrange(3)
    if layout == 0:  # a big circle and a band
        r = rng.uniform(0.25, 0.4) * W
        cx, cy = W / 2 + rng.uniform(-60, 60), H * 0.38
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=a)
        d.rectangle([0, H * 0.66, W, H * 0.74], fill=b)
    elif layout == 1:  # stripes on the diagonal
        for k in range(-6, 12):
            x = k * 70
            d.polygon([(x, 0), (x + 35, 0), (x + 35 - H * 0.5, H * 0.6), (x - H * 0.5, H * 0.6)], fill=a if k % 2 else b)
    else:  # stacked blocks
        y = 40
        while y < H * 0.62:
            h = rng.uniform(50, 140)
            d.rectangle([40, y, W - 40 - rng.uniform(0, 200), y + h], fill=rng.choice((a, b)))
            y += h + 20
    ink = "#1b1b1b" if bg not in ("#1b1b1b", "#7a4fd8", "#3f8fe0") else "#f2efe6"
    y = H * 0.78
    while y < H - 40:  # bars where the copy would be; deliberately unreadable
        d.rectangle([40, y, 40 + rng.uniform(0.3, 0.85) * (W - 80), y + 16], fill=ink)
        y += 30
    for _ in range(rng.randint(1, 3)):  # creases
        x = rng.uniform(0, W)
        d.line([(x, 0), (x + rng.uniform(-80, 80), H)], fill=(255, 255, 255, 60), width=3)
    sun = Image.new("RGBA", (W, H), (236, 226, 200, int(rng.uniform(90, 150))))  # sun-faded
    img = Image.alpha_composite(img, sun)
    dirt = Image.effect_noise((12, 16), 70).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    dirt = dirt.point(lambda v: min(150, max(0, v - 110) * 3))  # soft water stains, heavier in patches
    run = Image.linear_gradient("L").resize((W, H)).point(lambda v: max(0, v - 150))  # grime gathers at the bottom
    img = Image.composite(Image.new("RGBA", (W, H), (60, 50, 38, 255)), img, ImageChops.add(dirt, run))
    img.putalpha(torn_mask(rng, W, H, bite=rng.choice((0, 0, 0.35, 0.55))))
    return wear(rng, img, 0.9)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    for k in range(12):
        (throwup if k % 3 == 2 else tag)(rng).save(OUT / f"tag_{k:02d}.png")
    for k in range(10):
        poster(rng).save(OUT / f"poster_{k:02d}.png")
    print(f"{OUT}: 12 tags, 10 posters")


if __name__ == "__main__":
    main()
