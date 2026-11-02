"""M7: the thumbnail (brief, deliverables: "Thumbnail"), three options for the human to choose from (R1), after Not
Yet's scripts/thumbnail.py (a treated frame with type set over it). The type is the captions' (scripts/captions.py):
VT323 stretched to the 608 cell, white on black boxes, so the thumbnail looks like the video's closed captions.

  a  S48a: the photoreal open grave under "Logged-out Reddit · 2005 –" (the lockdown the song ends on);
     "READ-ONLY" over it.
  b  S42: the Dev's face glitching into a waveform; "WHO'S RAPPIN' THIS?" (Verse 4's turn).
  c  S41: the toy Dev of Act 1 and the photoreal Dev of Act 2 split on a diagonal (the reveal); "I'M THE BOT".
Each with a vignette; c is zoomed 1.7x on the Dev (small in the wide
frame), about a point either side of him, so the toy is whole left of the split and the photoreal Dev right of it.

Usage: .venv/bin/python -I scripts/thumbnail.py OUT_DIR [--act1 renders/m7/act1/frames]  ->  OUT_DIR/thumb_{a,b,c}.jpg
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import act2_assemble as a2  # noqa: E402
import animatic_assemble as aa  # noqa: E402
import captions  # noqa: E402

W, H = 1280, 720
OPTIONS = {  # song seconds of the frame(s), headline rows, row height (px), where
    "a": {"t": [191.0], "rows": ["READ-ONLY"], "row": 120, "pos": (0.06, 0.08)},
    "b": {"t": [161.9], "rows": ["WHO'S RAPPIN'", "THIS?"], "row": 96, "pos": (0.04, 0.62)},
    "c": {"t": [157.2, 159.3], "rows": ["I'M THE BOT"], "row": 110, "pos": (0.05, 0.74), "zoom": [(1.7, 0.6, 0.45), (1.7, 0.38, 0.45)]},
}


def vignette(img, k=0.45):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2)) / np.sqrt(2)
    g = 1 - k * np.clip(r, 0, 1) ** 1.6
    return (img.astype(np.float32) * g[..., None]).astype(np.uint8)


def type_layer(rows, row, pos):
    """The headline as caption boxes: RGBA (H, W, 4) uint8."""
    st = captions.STRETCH
    w1 = int(np.ceil(W / st))
    im = Image.new("RGBA", (w1, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(str(captions.FONT), row)
    cw = row * 0.4
    x0, y0 = pos[0] * W / st, pos[1] * H
    for i, text in enumerate(rows):
        y = y0 + i * row
        d.rectangle([x0, y, x0 + (len(text) + 2) * cw - 1, y + row - 1], fill=(0, 0, 0, 240))
        for j, ch in enumerate(text):
            d.text((x0 + (j + 1) * cw, y), ch, font=font, fill=(255, 255, 255, 255))
    return np.asarray(im.resize((W, H), Image.BILINEAR))


def over(img, layer):
    a = layer[..., 3:].astype(np.float32) / 255
    return (layer[..., :3] * a + img * (1 - a)).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--act1", default="renders/m4/act1_v8/frames")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    act2 = a2.Act2(a.act1)
    F = lambda t: aa.F(t)  # noqa: E731
    for k, o in OPTIONS.items():
        imgs = [act2.frame(F(t)) for t in o["t"]]
        if "zoom" in o:  # scale about a point (fractions of the frame), keeping the frame's size
            Ms = [np.float32([[z, 0, W * cx * (1 - z)], [0, z, H * cy * (1 - z)]]) for z, cx, cy in o["zoom"]]
            imgs = [cv2.warpAffine(i, M, (W, H), flags=cv2.INTER_LANCZOS4) for i, M in zip(imgs, Ms)]
        if len(imgs) == 2:  # the diagonal split: toy on the left, photoreal on the right
            y, x = np.mgrid[0:H, 0:W]
            m = (x - W * 0.5 - (y - H / 2) * 0.35 < 0)[..., None]
            img = np.where(m, imgs[0], imgs[1])
            cv2.line(img, (round(W * 0.5 - H / 2 * 0.35), 0), (round(W * 0.5 + H / 2 * 0.35), H), (255, 255, 255), 4)
        else:
            img = imgs[0]
        img = vignette(img)
        img = over(img, type_layer(o["rows"], o["row"], o["pos"]))
        p = out / f"thumb_{k}.jpg"
        if p.exists():
            raise SystemExit(f"{p} exists: archive it first")
        cv2.imwrite(str(p), cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(p)


if __name__ == "__main__":
    main()
