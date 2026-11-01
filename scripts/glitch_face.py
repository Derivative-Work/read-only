"""M5 face glitch (brief: S42 "the rapper's face glitches into a waveform", S43 "face still flickering"): an effect
pass over a lip-synced take, inside the face box from takes/l/<shot>/faces.json.

Events in config/glitch.json are [start, end, strength] in song seconds. While one is on:
  - the face's rows tear sideways, each band shifted by the vocal's samples at that frame (scanline glitch);
  - the colour channels split apart;
  - at strength above 0.5 the face fades to black and the vocal's waveform is drawn across it, a teal trace with a
    white core, so for that moment the face *is* the voice.
Outside the face ellipse every pixel is the lip-synced take. The effect is driven by the lead vocal stem, so it
moves with the words.

Usage: .venv/bin/python scripts/glitch_face.py S42 [S43 ...]   (after l_batch.py)
Output: takes/fx/<shot>/<shot>_glitch.mp4 (picture only) and _audio.mp4 (with the master, for review).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

CFG = json.load(open("config/glitch.json"))
LCFG = json.load(open("config/l.json"))
FPS = 24
TEAL = np.array([40, 230, 210], np.float32)


def frames(path):
    w, h = (int(x) for x in subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
         str(path)]).decode().split(","))
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def strength(t, events):
    s = 0.0
    for a, b, k in events:
        if a <= t < b:
            ramp = min(1.0, (t - a) / 0.04, (b - t) / 0.04)  # two-frame edges at most
            s = max(s, k * ramp)
    return s


def ellipse_mask(h, w, box, grow=1.25, feather=8):
    x, y, bw, bh = box
    cx, cy = x + bw / 2, y + bh / 2
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse([cx - bw * grow / 2, cy - bh * grow / 2, cx + bw * grow / 2, cy + bh * grow / 2], 255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(feather)), np.float32)[..., None] / 255


def glitch(img, box, s, wav, rng):
    h, w, _ = img.shape
    out = img.astype(np.float32)
    x, y, bw, bh = (int(v) for v in box)
    y0, y1 = max(0, y - bh // 8), min(h, y + bh + bh // 8)
    # tear: bands of rows shifted by the audio
    band = max(2, bh // 24)
    for r in range(y0, y1, band):
        k = wav[int((r - y0) / max(1, y1 - y0) * (len(wav) - 1))]
        dx = int(k * s * bw * 0.6 + rng.normal(0, 3) * s)
        out[r:r + band] = np.roll(out[r:r + band], dx, axis=1)
    # channel split
    d = int(4 + 10 * s)
    out[..., 0] = np.roll(out[..., 0], d, axis=1)
    out[..., 2] = np.roll(out[..., 2], -d, axis=1)
    if s > 0.5:  # the face becomes the waveform
        k = (s - 0.5) / 0.5
        out *= 1 - 0.85 * k
        tr = Image.new("L", (w, h), 0)
        dr = ImageDraw.Draw(tr)
        cy, amp = y + bh * 0.5, bh * 0.42
        xs = np.linspace(x - bw * 0.2, x + bw * 1.2, len(wav))
        pts = [(float(px), float(cy - amp * v)) for px, v in zip(xs, wav)]
        dr.line(pts, fill=255, width=5, joint="curve")
        core = np.asarray(tr, np.float32)[..., None] / 255
        glow = np.asarray(tr.filter(ImageFilter.GaussianBlur(6)), np.float32)[..., None] / 255
        out += k * (glow * 2.5 * TEAL + core * 255 * 0.9)
        # scanlines
        out[::3] *= 1 - 0.3 * k
    return np.clip(out, 0, 255)


def run(shot):
    spec = CFG["shots"][shot]
    t0 = LCFG["takes"][shot]["song_time"][0]
    src = Path(spec["take"])
    faces = json.load(open(Path("takes/l") / shot / "faces.json"))["faces"]
    vid = frames(src)
    vocal, sr = sf.read(LCFG["vocal"], always_2d=True)
    vocal = vocal.mean(1)
    peak = np.percentile(np.abs(vocal[int(t0 * sr):int((t0 + len(vid) / FPS) * sr)]), 99.5) or 1.0
    rng = np.random.default_rng(spec.get("seed", 1))
    out_dir = Path("takes/fx") / shot
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{shot}_glitch.mp4"
    h, w = vid.shape[1:3]
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)],
                           stdin=subprocess.PIPE)
    for i, img in enumerate(vid):
        t = t0 + i / FPS
        s = strength(t, spec["events"])
        if s <= 0:
            enc.stdin.write(img.tobytes())
            continue
        a = int(t * sr)
        win = vocal[a:a + int(sr * 0.012)]  # 12 ms of the voice: two or three cycles
        wav = np.clip(np.interp(np.linspace(0, len(win) - 1, 90), np.arange(len(win)), win) / peak, -1, 1)
        box = faces[min(i, len(faces) - 1)][:4]
        m = ellipse_mask(h, w, box)
        g = glitch(img, box, s, wav, rng)
        enc.stdin.write((img * (1 - m) + g * m).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    a0 = t0
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-ss", f"{a0:.3f}", "-t", f"{len(vid) / FPS:.3f}",
                    "-i", LCFG["master"], "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                    "-shortest", str(out_dir / f"{shot}_glitch_audio.mp4")], check=True)
    print(f"{shot}: {len(vid)} frames -> {out}", flush=True)


if __name__ == "__main__":
    for s in sys.argv[1:]:
        run(s)
