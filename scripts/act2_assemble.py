"""M5 gate: Act 2 as one cut with the master, from the end of Act 1 through S48b (brief M5: "Lip-sync test on S43,
then Act 2 shots (S41–S48)"; S40 and S48b are the edit's, built here).

- Lead-in: the last --lead seconds of S39e from the approved Act 1 frames (renders/m4/act1_v8/frames).
- S40 (F, "Hard freeze; the whole video rewinds at high speed through earlier shots" + "Rewind scan lines"): the M3
  assembler's rewind (scripts/animatic_assemble.py: REWIND_HOLD s of S39e's last frame, then every Act 1 frame back to
  S02 in reverse, sampled evenly), with a VHS rewind look over the rewind: fine scan lines, a tracking band of noise
  rolling up the frame, the colour channels pulled apart, a little horizontal jitter, the picture crushed and
  desaturated. The freeze itself stays clean.
- S41–S48a: the approved M5 takes (TAKES below).
- S48b: the human: "use the record scratches at the end to fade directly to the login screen (skip the fade to black
  first)". On the scratches at the end of the track (overlays/cues.json login_prompt "scratch", 194.65-195.75 s, in
  S48a's last seconds) the grave fades straight into the login prompt (renders/screens/login_prompt), its opacity
  following the scratch stem's accumulated energy, so it moves with each stroke; the prompt then holds, its cursor
  blinking, to the cut.
Act 2 takes are 1280×704; they are scaled to cover 1280×720 (centre crop). The master plays from the lead-in's start
to its end (196.16 s); S48b is silent.

Usage: .venv/bin/python scripts/act2_assemble.py OUT.mp4 [--lead 2.0]
"""
import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import json
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import animatic_assemble as aa  # noqa: E402

FPS = aa.FPS
W, H = 1280, 720
ACT1 = Path("renders/m4/act1_v8/frames")
TAKES = {"S41": "takes/fx/S41/S41_reveal.mp4", "S42": "takes/fx/S42/S42_glitch.mp4",
         "S43": "takes/fx/S43/S43_glitch.mp4", "S44": "takes/fx/S44/S44_billboard.mp4",
         "S45": "takes/fx/S45/S45_sign.mp4", "S47": "takes/fx/S47/S47_rec.mp4",
         "S48": "takes/fx/S48/S48_overlay.mp4", "S48a": "takes/v/S48a/S48a_joined.mp4"}
LOGIN = Path("renders/screens/login_prompt")
SCRATCH_STEM = "audio/stems/9 Other.wav"


def scratch_curve(t0, t1):
    """0..1 through the scratches: the Other stem's energy accumulated over [t0, t1], per frame time."""
    x, sr = sf.read(SCRATCH_STEM, always_2d=True)
    e = x.mean(1)[int(t0 * sr):int(t1 * sr)] ** 2
    c = np.cumsum(e) / e.sum()
    return lambda t: float(np.interp((t - t0) * sr, np.arange(len(c)), c))


def frames(path):
    w, h = (int(x) for x in subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
         str(path)]).decode().split(","))
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v", "-f", "rawvideo",
                                   "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def cover(img):
    h, w = img.shape[:2]
    s = max(W / w, H / h)
    r = cv2.resize(img, (round(w * s), round(h * s)), interpolation=cv2.INTER_LANCZOS4)
    y, x = (r.shape[0] - H) // 2, (r.shape[1] - W) // 2
    return r[y:y + H, x:x + W]


def act1(f):
    have = ACT1 / f"f_{f:05d}.png"
    return cv2.cvtColor(cv2.imread(str(have)), cv2.COLOR_BGR2RGB)


def rewind_look(img, k, rng):
    """VHS rewind: k is the frame's index into the rewind."""
    out = img.astype(np.float32)
    lum = out.mean(2, keepdims=True)
    out = lum + (out - lum) * 0.6  # desaturated
    out = np.clip((out - 20) * 1.15, 0, 255)  # crushed
    out[..., 0] = np.roll(out[..., 0], 4, axis=1)  # the channels pulled apart
    out[..., 2] = np.roll(out[..., 2], -4, axis=1)
    for y in range(0, H, 24):  # a little line jitter
        out[y:y + 24] = np.roll(out[y:y + 24], int(rng.normal(0, 2.5)), axis=1)
    band_y = int(H - (k * 37) % (H + 160)) - 80  # the tracking band rolling up
    y0, y1 = max(0, band_y), min(H, band_y + 70)
    if y1 > y0:
        noise = rng.random((y1 - y0, W, 1)) * 255
        out[y0:y1] = out[y0:y1] * 0.35 + noise * 0.65
        out[y0:y1] = np.roll(out[y0:y1], 30, axis=1)
    out[::3] *= 0.72  # scan lines
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--lead", type=float, default=2.0)
    a = ap.parse_args()
    SP = aa.spans()
    F = aa.F
    t0 = SP["S40"][0] - a.lead
    f0, f_end = F(t0), F(SP["S48b"][1])
    fa, fb = F(SP["S40"][0]), F(SP["S40"][1])
    hold = fa + int(round(aa.REWIND_HOLD * FPS))
    back = list(range(fa - 1, F(SP["S02"][0]) - 1, -1))
    rng = np.random.default_rng(40)
    takes = {sid: frames(p) for sid, p in TAKES.items()}
    cue = json.load(open("overlays/cues.json"))["screens"]["login_prompt"]
    first = json.load(open(LOGIN / "range.json"))["first_frame"]
    curve = scratch_curve(*cue["scratch"])
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-ss", f"{t0:.4f}", "-t", f"{SP['S48a'][1] - t0:.4f}", "-i",
                            aa.MASTER, "-filter_complex", "[1:a]apad[a]", "-map", "0:v", "-map", "[a]", "-shortest",
                            "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
                            a.out], stdin=subprocess.PIPE)
    for f in range(f0, f_end):
        if f < fa:
            img = act1(f)
        elif f < fb:
            if f < hold:
                img = act1(fa - 1)
            else:
                k = f - hold
                img = rewind_look(act1(back[int(k * len(back) / (fb - hold))]), k, rng)
        elif f >= F(cue["from"]):
            i = f - first
            scr = cv2.cvtColor(cv2.imread(str(LOGIN / f"f_{i + 1:04d}.png")), cv2.COLOR_BGR2RGB).astype(np.float32)
            k = curve(f / FPS - aa.PRE)
            if k < 1 and f < F(SP["S48a"][1]):
                grave = cover(takes["S48a"][min(f - F(SP["S48a"][0]), len(takes["S48a"]) - 1)]).astype(np.float32)
                scr = grave * (1 - k) + scr * k
            img = np.clip(scr, 0, 255).astype(np.uint8)
        else:
            sid = next(s for s in TAKES if F(SP[s][0]) <= f < F(SP[s][1]))
            tk = takes[sid]
            img = cover(tk[min(f - F(SP[sid][0]), len(tk) - 1)])
        enc.stdin.write(np.ascontiguousarray(img).tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"{a.out}: {(f_end - f0) / FPS:.2f} s, frames {f0}..{f_end - 1}", flush=True)


if __name__ == "__main__":
    main()
