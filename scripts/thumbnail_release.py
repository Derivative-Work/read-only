"""Release: the main video's thumbnails after the upload underperformed with D, the lineup (scripts/thumbnail_recast.py).

  g  (the human, 2026-11-04: "Let's go with G and #4", with the title "Reddit sold your posts to AI, so AI wrote a
     diss track back"). In Not Yet's approved style (~/Projects/not-yet/scripts/thumbnail.py: a treated frame, an Inter
     Black headline and an Oooh Baby line under it, white with a soft drop shadow). S48a at song 191.0 s, the frame of
     option A (scripts/thumbnail.py): the photoreal open grave under "Logged-out Reddit · 2005 –", taken clean (before
     the captions) from act2_assemble.Act2; Reddit said on Oct 29, 2026 that it will move to a primarily logged-in
     experience (docs/sources.md), and the headline is the login prompt the video cuts to after the grave.
  m  (the human: "give me some more thumbnails that ideally read quickly on mobile", then "let's go with M"). One
     subject filling the frame and two huge words, nothing bottom right (YouTube's duration badge), no handwritten
     line (illegible at the up-next list's 168x94). The good bot in its box at S39a's opening (video frame 3814),
     rendered sharp at 3x by scenes/blender/stills3x.py, cropped to the bot; "GOOD BOT" with BOT in yellow.

Usage: .venv/bin/python -I scripts/thumbnail_release.py {g,m} OUT.jpg [--act1 renders/final/act1_frames]
       (m needs: blender -b --factory-startup --python scenes/blender/stills3x.py -- renders/m8/thumbs_release/stills3x 3814)
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import act2_assemble as a2  # noqa: E402
import animatic_assemble as aa  # noqa: E402

FONTS = Path("assets/fonts")
W, H = 1280, 720
CREAM, SCRIPT, YELLOW = (255, 250, 240), (255, 245, 225), (255, 214, 64)

# g: the grave
G_T = 191.0                  # song seconds: S48a
G_CENTRE = (0.72, 0.4)       # the vignette's centre (fractions of the frame): the stone
G_TEXT = [  # font, size, weight (None: static), text, top left
    ("Inter[opsz,wght].ttf", 96, 900, "LOG IN", (44, 420)),
    ("Inter[opsz,wght].ttf", 96, 900, "TO CONTINUE", (44, 521)),
    ("OoohBaby-Regular.ttf", 72, None, "a diss track for Reddit", (48, 630)),
]

# m: the good bot
M_STILL = Path("renders/m8/thumbs_release/stills3x/s_03814.png")  # 5760x3240
M_CROP = (1750, 880, 1950)   # x, y, width at 3x; height is width * 9/16
M_CENTRE, M_K, M_DARK = (0.55, 0.62), 1.2, 0.9
M_SIZE, M_XY = 176, (44, 30)
M_WORDS = [("GOOD ", CREAM), ("BOT", YELLOW)]


def vignette(a, centre, k, dark):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - centre[0] * W) / W) ** 2 + ((yy - centre[1] * H) / H) ** 2)
    v = np.clip(1.05 - k * r, {1.5: 0.4}.get(k, 0.35), 1.0)
    return Image.fromarray((np.clip(a * v[..., None] * dark, 0, 1) * 255).astype(np.uint8))


def font(name, size, wght):
    f = ImageFont.truetype(str(FONTS / name), size)
    if wght:
        f.set_variation_by_axes([32, wght])  # Inter: opsz, wght
    return f


def shadowed(img, xy, txt, f, fill):
    """g's type: a 4 px drop, 11 px blur."""
    sh = Image.new("L", img.size, 0)
    ImageDraw.Draw(sh).text((xy[0], xy[1] + 4), txt, font=f, fill=235)
    img.paste((0, 0, 0), mask=sh.filter(ImageFilter.GaussianBlur(11)))
    ImageDraw.Draw(img).text(xy, txt, font=f, fill=fill)


def heavy(img, xy, words, size):
    """m's type: one line of coloured words over a heavier shadow (a 6 px stroke, blurred 12% of the size)."""
    f = font("Inter[opsz,wght].ttf", size, 900)
    x, y = xy
    sh = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(sh)
    xx = x
    for t, _ in words:
        d.text((xx, y + size * 0.05), t, font=f, fill=255, stroke_width=6)
        xx += f.getlength(t)
    img.paste((0, 0, 0), mask=sh.filter(ImageFilter.GaussianBlur(size * 0.12)))
    d = ImageDraw.Draw(img)
    xx = x
    for t, c in words:
        d.text((xx, y), t, font=f, fill=c, stroke_width=0, stroke_fill=(0, 0, 0))
        xx += f.getlength(t)


def thumb_g(act1):
    a = a2.Act2(act1).frame(aa.F(G_T)).astype(np.float32) / 255
    assert a.shape[:2] == (H, W), a.shape
    img = vignette(a, G_CENTRE, 1.5, 0.92)
    for name, size, wght, txt, xy in G_TEXT:
        shadowed(img, xy, txt, font(name, size, wght), SCRIPT if wght is None else CREAM)
    return img


def thumb_m(_act1):
    a = cv2.imread(str(M_STILL))
    assert a is not None and a.shape[:2] == (3240, 5760), M_STILL
    x, y, w = M_CROP
    a = a[y:y + round(w * 9 / 16), x:x + w, ::-1].astype(np.float32) / 255
    a = cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA)
    img = vignette(a, M_CENTRE, M_K, M_DARK)
    heavy(img, M_XY, M_WORDS, M_SIZE)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("option", choices=["g", "m"])
    ap.add_argument("out")
    ap.add_argument("--act1", default="renders/final/act1_frames")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"{out} exists: archive it first (never overwrite an asset)")
    img = {"g": thumb_g, "m": thumb_m}[a.option](a.act1)
    img.save(out, quality=92)
    print(out, f"({img.width}x{img.height})")


if __name__ == "__main__":
    main()
