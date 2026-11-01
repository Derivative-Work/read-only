"""M5: an Act 1 sign or poster back on a photoreal take, for continuity (the human's note on S41: "put the text back
for continuity"). The sign is rendered alone from the shot's camera (scenes/blender/sign_matte.py --materials,
renders/m5/plates/<shot>/sign/), so it lines up with a take made over the Blender depth, and whatever comes in front
of it (a shutter) still covers it.

The take's own version of the sign (often garbled letters) is replaced: the rendered sign is lit by the take's light
there, its luminance blurred (sigma --blur px) so the take's letters don't show through, normalised to the paper's
white. --shutter X0 X1 (a locked-off camera): the take's own shutter coming down from the top (its timing needn't
match the Blender one's) is found row by row between columns X0 and X1, as the rows that changed from the first frame
contiguously from the top; above its bottom edge the paste gives way to the take.
(S41's sign, black ink on the take's own band, is printed by scripts/reveal.py instead.)

Usage: .venv/bin/python scripts/sign_paste.py S45 takes/v/S45/S45_s1.mp4 [--blur 14] [--shutter 650 1250]
Output: takes/fx/<shot>/<shot>_sign.mp4 (picture only) and _audio.mp4 (with the master, for review).
"""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

FPS = 24
MASTER = json.load(open("config/l.json"))["master"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("take")
    ap.add_argument("--blur", type=float, default=14)
    ap.add_argument("--shutter", nargs=2, type=int)
    a = ap.parse_args()
    plate = Path("renders/m5/plates") / a.shot
    meta = json.load(open(plate / "shot.json"))
    s0, s1 = meta["frames_shot"]
    w, h = meta["resolution"]
    n = s1 - s0
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", a.take, "-map", "0:v", "-frames:v", str(n), "-f",
                                   "rawvideo", "-pix_fmt", "rgb24", "-"])
    vid = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    out_dir = Path("takes/fx") / a.shot
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{a.shot}_sign.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)],
                           stdin=subprocess.PIPE)
    for i in range(n):
        img = vid[min(i, len(vid) - 1)].astype(np.float32)
        sg = cv2.cvtColor(cv2.imread(str(plate / "sign" / f"{s0 + i:05d}.png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
        alpha = cv2.GaussianBlur(sg[..., 3].astype(np.float32) / 255, (0, 0), 0.7)[..., None]
        if alpha.max() < 0.05:
            enc.stdin.write(img.astype(np.uint8).tobytes())
            continue
        if a.shutter:
            x0, x1 = a.shutter
            d = cv2.GaussianBlur(np.abs(img - vid[0].astype(np.float32)).mean(2), (0, 0), 2)[:, x0:x1]
            rows = (d > 20).mean(1) > 0.5
            edge = int(np.argmin(rows)) if not rows.all() else h  # the first row from the top that didn't change
            if edge > 2:
                cover = np.clip((edge + 6 - np.arange(h)) / 8, 0, 1)[:, None, None]
                alpha = alpha * (1 - cover)
        rgb = sg[..., :3].astype(np.float32)
        lum = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
        # the take's light on the sign: its luminance under the sign, spread so its own lettering averages out
        wgt = cv2.GaussianBlur(alpha[..., 0], (0, 0), a.blur) + 1e-4
        light = cv2.GaussianBlur(lum * alpha[..., 0], (0, 0), a.blur) / wgt
        paper = np.percentile(cv2.cvtColor(sg[..., :3], cv2.COLOR_RGB2GRAY)[sg[..., 3] > 200], 90)
        comp = np.clip(rgb * (light / max(paper, 1))[..., None], 0, 255)
        enc.stdin.write((img * (1 - alpha) + comp * alpha).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    t0 = meta["song_time"][0]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-ss", f"{t0:.3f}", "-t", f"{n / FPS:.3f}", "-i",
                    MASTER, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest",
                    str(out_dir / f"{a.shot}_sign_audio.mp4")], check=True)
    print(f"{a.shot}: {n} frames -> {out}", flush=True)


if __name__ == "__main__":
    main()
