"""M5 S48: join a shot made in two parts (A forward, B generated backwards from the shot's end) across an overlap,
without a visible seam (the human's note: "blending or color-matching together the shots from the sidewalk to the
graveyard"). Over the overlap, B is graded to A (per-channel mean and spread in Lab, measured over the overlap's
frames of both) and crossfaded in with a smoothstep; after the overlap the grade eases off over --settle frames, so
B ends as generated.

Frames are the shot's own indices: A covers 0 .. len(A)-1; B (already in forward order) starts at --b-start.

Usage: .venv/bin/python scripts/join_blend.py A.mp4 B.mp4 --b-start 160 --length 231 --out OUT.mp4 [--settle 24]
"""
import argparse
import subprocess

import cv2
import numpy as np


def read(path, w, h):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-map", "0:v", "-f", "rawvideo", "-pix_fmt",
                                   "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def lab(x):
    return cv2.cvtColor(x, cv2.COLOR_RGB2LAB).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--b-start", type=int, required=True)
    ap.add_argument("--length", type=int, required=True)
    ap.add_argument("--settle", type=int, default=24)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", default="1280x704")
    a = ap.parse_args()
    w, h = (int(v) for v in a.size.split("x"))
    A, B = read(a.a, w, h), read(a.b, w, h)
    b0, a1 = a.b_start, len(A) - 1  # the overlap: b0 .. a1
    ov = range(b0, a1 + 1)
    la = np.stack([lab(A[i]) for i in ov]).reshape(-1, 3)
    lb = np.stack([lab(B[i - b0]) for i in ov]).reshape(-1, 3)
    mu_a, sd_a, mu_b, sd_b = la.mean(0), la.std(0) + 1e-3, lb.mean(0), lb.std(0) + 1e-3
    print("A", mu_a.round(1), sd_a.round(1), "B", mu_b.round(1), sd_b.round(1), flush=True)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", "24", "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", a.out],
                           stdin=subprocess.PIPE)
    ss = lambda x: x * x * (3 - 2 * x)  # noqa: E731
    for i in range(a.length):
        if i < b0:
            enc.stdin.write(A[i].tobytes())
            continue
        g = 1.0 if i <= a1 else 1 - ss(min(1.0, (i - a1) / a.settle))  # the grade, easing off after the overlap
        lb_i = lab(B[i - b0])
        graded = (lb_i - mu_b) / sd_b * sd_a + mu_a
        lb_i = lb_i * (1 - g) + graded * g
        bi = cv2.cvtColor(np.clip(lb_i, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)
        if i <= a1:
            k = ss((i - b0) / max(1, a1 - b0))
            bi = A[i].astype(np.float32) * (1 - k) + bi * k
        enc.stdin.write(bi.astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"{a.length} frames -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
