"""M5 S47: the recorder's REC light blinking on the photoreal take (brief: "The payphone again, now real; the REC light
blinks"), on the Blender timing: on for 0.25 s every 0.5 s from the shot's start (shots.py, as in S03).

Video models don't blink a small light on time, so the take's own LED (it has a lit red dot where the Blender LED is)
is found each frame near the LED's position from the Blender camera (renders/m5/plates/<shot>/sign/, from
scenes/blender/sign_matte.py --objects recorder.rec) as the reddest blob within --search px, and then dimmed to
an unlit red (off) or brightened with a soft glow (on).

Usage: .venv/bin/python scripts/rec_blink.py S47 takes/v/S47/S47_s1.mp4 [--search 40]
Output: takes/fx/<shot>/<shot>_rec.mp4 (picture only) and _audio.mp4 (with the master, for review).
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
    ap.add_argument("--search", type=int, default=40)
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
    out = out_dir / f"{a.shot}_rec.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)],
                           stdin=subprocess.PIPE)
    track = []
    for i in range(n):
        img = vid[i].astype(np.float32)
        m = cv2.imread(str(plate / "sign" / f"{s0 + i:05d}.png"), cv2.IMREAD_UNCHANGED)[..., 3]
        ys, xs = np.nonzero(m > 20)
        cx, cy = int(xs.mean()), int(ys.mean())
        r0 = max(4, int(np.sqrt(len(xs) / np.pi)))
        x0, y0 = max(0, cx - a.search), max(0, cy - a.search)
        win = img[y0:cy + a.search, x0:cx + a.search]
        red = win[..., 0] - 0.5 * (win[..., 1] + win[..., 2])
        blob = (red > 60) & (win[..., 0] > 140)
        k, lab, stats, cent = cv2.connectedComponentsWithStats(blob.astype(np.uint8))
        if k > 1:  # the biggest red blob in the window
            j = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
            bx, by = cent[j][0] + x0, cent[j][1] + y0
            br = max(r0, np.sqrt(stats[j, cv2.CC_STAT_AREA] / np.pi))
        else:  # not found: the Blender position
            bx, by, br = cx, cy, r0
        track.append((bx, by, br))
    track = np.array(track)
    for c in range(3):  # smooth the track a little
        track[:, c] = np.convolve(np.pad(track[:, c], 2, mode="edge"), np.ones(5) / 5, mode="valid")
    yy, xx = np.mgrid[0:h, 0:w]
    for i in range(n):
        img = vid[i].astype(np.float32)
        bx, by, br = track[i]
        d = np.hypot(xx - bx, yy - by)
        core = np.clip((br * 1.6 - d) / (br * 0.6), 0, 1)[..., None]
        on = ((i / FPS) % 0.5) < 0.25
        if on:
            glow = np.exp(-(d / (br * 3.5)) ** 2)[..., None]
            lit = img * (1 - core) + np.array([255, 120, 105], np.float32) * core
            img = np.clip(lit + glow * np.array([140, 20, 15], np.float32), 0, 255)
        else:  # an unlit red lens: dark red, keeping the take's highlight shape
            dark = img * np.array([0.45, 0.18, 0.18], np.float32)
            img = img * (1 - core) + dark * core
        enc.stdin.write(img.astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    t0 = meta["song_time"][0]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-ss", f"{t0:.3f}", "-t", f"{n / FPS:.3f}", "-i",
                    MASTER, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest",
                    str(out_dir / f"{a.shot}_rec_audio.mp4")], check=True)
    print(f"{a.shot}: {n} frames -> {out}", flush=True)


if __name__ == "__main__":
    main()
