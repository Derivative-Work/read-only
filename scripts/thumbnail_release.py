"""Release: the main video's thumbnail G (the human, 2026-11-04: the upload underperformed with D, the lineup; "Let's go
with G and #4", with the title "Reddit sold your posts to AI, so AI wrote a diss track back").

In Not Yet's approved thumbnail style (~/Projects/not-yet/scripts/thumbnail.py: a treated frame, one subject, an Inter
Black headline and an Oooh Baby line under it, white with a soft drop shadow), not the captions' VT323 boxes of A-F.

The frame is S48a at song 191.0 s, the same frame as option A (scripts/thumbnail.py): the photoreal open grave under
"Logged-out Reddit · 2005 –", taken clean (before the captions) from act2_assemble.Act2. Reddit said on Oct 29, 2026
that it will move to a primarily logged-in experience (docs/sources.md); the headline is the login prompt the video
cuts to after the grave. A vignette centred on the stone; the text sits low on the left, over the dark grave.

Usage: .venv/bin/python -I scripts/thumbnail_release.py [--act1 renders/final/act1_frames] OUT.jpg
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import act2_assemble as a2  # noqa: E402
import animatic_assemble as aa  # noqa: E402

FONTS = Path("assets/fonts")
W, H = 1280, 720
T = 191.0                    # song seconds: S48a, the grave
CENTRE = (0.72, 0.4)         # the vignette's centre (fractions of the frame): the stone
CREAM, SCRIPT = (255, 250, 240), (255, 245, 225)
TEXT = [  # font, size, weight (None: static), text, top left
    ("Inter[opsz,wght].ttf", 96, 900, "LOG IN", (44, 420)),
    ("Inter[opsz,wght].ttf", 96, 900, "TO CONTINUE", (44, 521)),
    ("OoohBaby-Regular.ttf", 72, None, "a diss track for Reddit", (48, 630)),
]


def plate(act1):
    a = a2.Act2(act1).frame(aa.F(T)).astype(np.float32) / 255
    assert a.shape[:2] == (H, W), a.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - CENTRE[0] * W) / W) ** 2 + ((yy - CENTRE[1] * H) / H) ** 2)
    v = np.clip(1.05 - 1.5 * r, 0.4, 1.0)
    return Image.fromarray((np.clip(a * v[..., None] * 0.92, 0, 1) * 255).astype(np.uint8))


def font(name, size, wght):
    f = ImageFont.truetype(str(FONTS / name), size)
    if wght:
        f.set_variation_by_axes([32, wght])  # Inter: opsz, wght
    return f


def shadowed(img, xy, txt, f, fill):
    sh = Image.new("L", img.size, 0)
    ImageDraw.Draw(sh).text((xy[0], xy[1] + 4), txt, font=f, fill=235)
    img.paste((0, 0, 0), mask=sh.filter(ImageFilter.GaussianBlur(11)))
    ImageDraw.Draw(img).text(xy, txt, font=f, fill=fill)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--act1", default="renders/final/act1_frames")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"{out} exists: archive it first (never overwrite an asset)")
    img = plate(a.act1)
    for name, size, wght, txt, xy in TEXT:
        shadowed(img, xy, txt, font(name, size, wght), SCRIPT if wght is None else CREAM)
    img.save(out, quality=92)
    print(out, f"({img.width}x{img.height})")


if __name__ == "__main__":
    main()
