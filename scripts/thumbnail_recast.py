"""M8: thumbnail options for the recast (the human: "Suggest new thumbnails with the edit in mind"), after
scripts/thumbnail.py (the approved B was S42's waveform face on the approved rapper alone). Same type (the captions'
VT323 boxes) and vignette. The seven identities' takes are aligned frame for frame (scripts/recast.py), so their
faces can be cut together.

  d  the lineup: the seven men in S42's medium shot side by side, head to apron, each tile a tape still (scan lines,
     a little chroma), "I'M THE BOT" across them.
  e  the splice: one S43 close-up made of three men in bands (hair and brow, eyes, nose and mouth) joined by VHS
     tracking bars, "WHICH ONE'S SINGING NOW?".
  f  the index: a 4x2 grid of the seven S43 close-ups and the waveform face (S43's opening flash), "WHO'S RAPPIN'
     THIS?" across the middle.

Usage: .venv/bin/python -I scripts/thumbnail_recast.py OUT_DIR [--only def]  ->  OUT_DIR/thumb_{d,e,f}.jpg
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from thumbnail import H, W, over, type_layer, vignette  # noqa: E402

RC = json.load(open("config/recast.json"))
IDS = list(RC["identities"])  # a..g
LINEUP = ["e", "b", "a", "d", "f", "c", "g"]  # no one's place reads as the lead: a sits third
S43_FRAME = 6  # every man mid-word, mouth open, no glitch (S43 frame sheet)
S42_FRAME = 20


def take(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, 704, 1280, 3)


def clean(shot, i):
    """The lip-synced take, before the glitch pass (a clean face)."""
    return take(f"takes/l/{shot}/{shot}_s2.mp4" if i == "a" else f"takes/l/{shot}_{i}/{shot}_{i}_s2.mp4")


def tape(img, rng, k=0.35):
    """A tape still: chroma pulled apart, every third line darker, a little noise."""
    img = img.astype(np.float32)
    sh = max(1, int(round(3 * k * img.shape[0] / 720 + 1)))
    img[..., 0] = np.roll(img[..., 0], sh, axis=1)
    img[..., 2] = np.roll(img[..., 2], -sh, axis=1)
    img[::3] *= 1 - 0.22 * k
    img += rng.normal(0, 6 * k, img.shape[:2])[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)


def bar(img, y, rng, half=10):
    """A VHS tracking bar across the frame at row y: snow, the lines either side torn sideways."""
    h, w = img.shape[:2]
    out = img.copy()
    for r in range(max(0, y - 3 * half), min(h, y + 3 * half)):
        out[r] = np.roll(out[r], int(rng.normal(0, 1) * 18 * np.exp(-((r - y) / (2.0 * half)) ** 2)), axis=0)
    y0, y1 = max(0, y - half), min(h, y + half)
    out[y0:y1] = (out[y0:y1] * 0.2 + rng.random((y1 - y0, w, 1)) * 255 * 0.8).astype(np.uint8)
    return out


def cover(img, w, h):
    s = max(w / img.shape[1], h / img.shape[0])
    r = cv2.resize(img, (round(img.shape[1] * s), round(img.shape[0] * s)), interpolation=cv2.INTER_AREA)
    y, x = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2
    return r[y:y + h, x:x + w]


def lineup(rng):
    tw = W // 7
    img = np.zeros((H, W, 3), np.uint8)
    cx = round(965 * 1280 / 1920)  # the man's centre in S42 (config/recast.json's head ellipse)
    for k, i in enumerate(LINEUP):
        fr = clean("S42", i)[S42_FRAME]
        cw = round(tw * 704 / H * 1.0)
        crop = fr[:, cx - cw // 2:cx + cw // 2]
        t = tape(cv2.resize(crop, (tw, H), interpolation=cv2.INTER_AREA), rng)
        img[:, k * tw:(k + 1) * tw] = t
        if k:
            img[:, k * tw - 1:k * tw + 1] = 12
    return vignette(img, 0.3), (["I'M THE BOT"], 104, (0.24, 0.80))


def splice(rng):
    takes = {i: clean("S43", i)[S43_FRAME] for i in ("d", "f", "a")}  # v1 used b: his eyes blink at this frame
    # rows at the take's 704 lines: hair and brow / eyes / nose and mouth
    cuts = [0, 205, 300, 704]
    img = np.zeros_like(takes["a"])
    for (y0, y1), i in zip(zip(cuts, cuts[1:]), ("d", "f", "a")):
        img[y0:y1] = takes[i][y0:y1]
    for y in cuts[1:-1]:
        img = bar(img, y, rng)
    img = tape(cover(img, W, H), rng, 0.5)
    return vignette(img), (["WHICH ONE'S", "SINGING NOW?"], 88, (0.03, 0.66))


def index(rng):
    tw, th = W // 4, H // 2
    order = ["b", "e", "a", "d", "c", "g", "f"]
    tiles = [clean("S43", i)[S43_FRAME] for i in order]
    wave = take("takes/fx/S43_a/S43_a_glitch.mp4")[1]  # the opening flash (frame 1; frame 0 only tears): the face is the vocal's waveform
    tiles.insert(5, wave)  # the waveform sits among them, bottom row second
    img = np.zeros((H, W, 3), np.uint8)
    for k, t in enumerate(tiles):
        x, y = (k % 4) * tw, (k // 4) * th
        c = t[0:620, 290:990]  # head and shoulders
        img[y:y + th, x:x + tw] = tape(cover(c, tw, th), rng)
    img[th - 1:th + 1] = 12
    for x in (tw, 2 * tw, 3 * tw):
        img[:, x - 1:x + 1] = 12
    return vignette(img, 0.3), (["WHO'S RAPPIN' THIS?"], 84, (0.17, 0.02))  # v1 at 0.44 hid the top row's mouths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--only", default="def", help="which options to render, e.g. ef")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for k, fn in (("d", lineup), ("e", splice), ("f", index)):
        if k not in a.only:
            continue
        img, (rows, row, pos) = fn(np.random.default_rng(ord(k)))
        img = over(img, type_layer(rows, row, pos))
        p = out / f"thumb_{k}.jpg"
        if p.exists():
            raise SystemExit(f"{p} exists: archive it first")
        cv2.imwrite(str(p), cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(p)


if __name__ == "__main__":
    main()
