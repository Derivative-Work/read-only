"""M5 S44: the comment box (overlays/screens.html "billboard_reply", rendered by overlays/screens.mjs) pinned onto the
rooftop billboard of the V take (brief: "The tower's rooftop billboard shows a generic comment box"; B→V+JS).

The V take's billboard is a plain glowing white face (the keyframe asks for it blank). Each frame, that face is found
in the take itself (the largest bright four-cornered region), its corners smoothed over time, and the screen's frame
warped onto it. The screen is multiplied by the take's own light there (the face's brightness, normalised to its
white), so the rain streaks and the falloff toward the frame's edges carry over the comment box.

Usage: .venv/bin/python scripts/billboard.py S44 takes/v/S44/S44_s1.mp4 [--screen renders/screens/billboard_reply]
Output: takes/fx/<shot>/<shot>_billboard.mp4 (picture only) and _audio.mp4 (with the master, for review);
        takes/fx/<shot>/corners.json (the tracked corners per frame).
"""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

FPS = 24
MASTER = json.load(open("config/l.json"))["master"]


def find_face(img):
    """The billboard face's four corners (TL, TR, BR, BL), from the brightest large region."""
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, m = cv2.threshold(g, 200, 255, cv2.THRESH_BINARY)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea)
    hull = cv2.convexHull(c).reshape(-1, 2).astype(np.float32)
    s, d = hull.sum(1), hull[:, 0] - hull[:, 1]
    return np.array([hull[s.argmin()], hull[d.argmax()], hull[s.argmax()], hull[d.argmin()]], np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("take")
    ap.add_argument("--screen", default="renders/screens/billboard_reply")
    a = ap.parse_args()
    meta = json.load(open(Path("renders/m5/plates") / a.shot / "shot.json"))
    w, h = meta["resolution"]
    n = meta["frames_shot"][1] - meta["frames_shot"][0]
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", a.take, "-map", "0:v", "-frames:v", str(n), "-f",
                                   "rawvideo", "-pix_fmt", "rgb24", "-"])
    vid = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    corners = np.array([find_face(f) for f in vid])
    k = 5  # smooth the track over 5 frames (the camera move is slow; the threshold edge flickers in the rain)
    pad = np.concatenate([corners[:1].repeat(k // 2, 0), corners, corners[-1:].repeat(k // 2, 0)])
    smooth = np.array([pad[i:i + k].mean(0) for i in range(len(corners))])
    out_dir = Path("takes/fx") / a.shot
    out_dir.mkdir(parents=True, exist_ok=True)
    json.dump({"take": a.take, "corners": smooth.round(2).tolist()}, open(out_dir / "corners.json", "w"))
    out = out_dir / f"{a.shot}_billboard.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)],
                           stdin=subprocess.PIPE)
    for i, img in enumerate(vid):
        scr = cv2.cvtColor(cv2.imread(str(Path(a.screen) / f"f_{i + 1:04d}.png")), cv2.COLOR_BGR2RGB)
        sh, sw = scr.shape[:2]
        src = np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]])
        H = cv2.getPerspectiveTransform(src, smooth[i])
        warped = cv2.warpPerspective(scr, H, (w, h), flags=cv2.INTER_AREA).astype(np.float32)
        mask = cv2.warpPerspective(np.full((sh, sw), 255, np.uint8), H, (w, h)).astype(np.float32) / 255
        mask = cv2.GaussianBlur(mask, (3, 3), 0)[..., None]
        f = img.astype(np.float32)
        lum = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
        white = np.percentile(lum[mask[..., 0] > 0.9], 60) if (mask > 0.9).any() else 240.0
        light = np.clip(lum / max(white, 1), 0.6, 1.15)[..., None]
        comp = np.clip(warped * light, 0, 255)
        enc.stdin.write((f * (1 - mask) + comp * mask).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    t0 = meta["song_time"][0]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-ss", f"{t0:.3f}", "-t", f"{n / FPS:.3f}", "-i",
                    MASTER, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest",
                    str(out_dir / f"{a.shot}_billboard_audio.mp4")], check=True)
    print(f"{a.shot}: {n} frames -> {out}", flush=True)


if __name__ == "__main__":
    main()
