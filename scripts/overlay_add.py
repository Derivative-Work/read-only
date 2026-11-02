"""M5 S48: the Act 1 set's lettering and lights over the photoreal take, for continuity and for the gag (brief: "every
shutter has a keypad reading 'Log in to continue,' and every window shows a red REC light"): the shop signs, the
READ-ONLY neon, the keypad screens, the window REC lights, the doormen's eye slits and the pawn shop's clock,
rendered alone from the shot's camera in their own colours (scenes/blender/sign_matte.py --own --subdir overlay),
laid over the take, which follows the same camera through the Blender depth. The bright parts also glow (a blur of
the overlay's highlights, added), so the lights sit in the rain.

--clean R: the take's own copy of the lettering (keyframes made from the layout keep it, a little off) is blurred out
under the overlay's ink, dilated by R px, before the overlay goes on, so the letters don't double.

Usage: .venv/bin/python scripts/overlay_add.py S48 takes/v/S48/S48_v4_s1.mp4 [--glow 6] [--clean 5] [--bloom 0.8]
Output: takes/fx/<shot>/<shot>_overlay.mp4 (picture only) and _audio.mp4 (with the master, for review).
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
    ap.add_argument("--glow", type=float, default=6)
    ap.add_argument("--clean", type=int, default=0)
    ap.add_argument("--bloom", type=float, default=0.8, help="how much of the lights' glow is added (0: none, S49's phone)")
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
    out = out_dir / f"{a.shot}_overlay.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)],
                           stdin=subprocess.PIPE)
    for i in range(n):
        img = vid[min(i, len(vid) - 1)].astype(np.float32)
        ov = cv2.cvtColor(cv2.imread(str(plate / "overlay" / f"{s0 + i:05d}.png"), cv2.IMREAD_UNCHANGED),
                          cv2.COLOR_BGRA2RGBA).astype(np.float32)
        ov = cv2.GaussianBlur(ov, (0, 0), 0.6)  # the take's softness
        alpha = ov[..., 3:] / 255
        rgb = ov[..., :3]
        if a.clean:  # under the ink (dark lettering, not the lights), the take's own letters blurred away
            ink = ((ov[..., 3] > 30) & (rgb.max(2) < 150)).astype(np.uint8)
            zone = cv2.GaussianBlur(cv2.dilate(ink, np.ones((2 * a.clean + 1,) * 2, np.uint8)).astype(np.float32),
                                    (0, 0), 2)[..., None]
            img = img * (1 - zone) + cv2.GaussianBlur(img, (0, 0), 3 * a.clean) * zone
        comp = img * (1 - alpha) + rgb * alpha
        hi = rgb * alpha * (rgb.max(2, keepdims=True) > 150)  # the lights, not the ink
        glow = cv2.GaussianBlur(hi, (0, 0), a.glow)
        comp = np.clip(comp + a.bloom * glow, 0, 255)
        enc.stdin.write(comp.astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    t0 = meta["song_time"][0]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-ss", f"{t0:.3f}", "-t", f"{n / FPS:.3f}", "-i",
                    MASTER, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest",
                    str(out_dir / f"{a.shot}_overlay_audio.mp4")], check=True)
    print(f"{a.shot}: {n} frames -> {out}", flush=True)


if __name__ == "__main__":
    main()
