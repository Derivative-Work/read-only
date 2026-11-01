"""M5 S41 reveal (brief: "the Blender street gains real texture, frame by frame"; "crossfade from S41's B render to
its B→V version"): a dissolve from the plates' beauty pass (the Act 1 look) to the V take, in patches rather than all
at once. Each pixel turns real at its own moment: a soft noise field plus the depth pass, so the far street goes
first and the corner nearest the camera last. Both sides share the Blender camera (V follows its depth), so they
line up through the dissolve.

Usage: .venv/bin/python scripts/reveal.py S41 takes/v/S41/S41_depth_s2.mp4 [--start 0.25 --end 2.0] [--seed 1]
       --start/--end: seconds into the shot where the reveal begins and ends.
Output: takes/fx/<shot>/<shot>_reveal.mp4 (picture only) and _audio.mp4 (with the master, for review).
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

FPS = 24
MASTER = json.load(open("config/l.json"))["master"]


def frames(path, n):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-frames:v", str(n), "-f", "rawvideo",
                                   "-pix_fmt", "rgb24", "-"])
    return raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("take")
    ap.add_argument("--start", type=float, default=0.25)
    ap.add_argument("--end", type=float, default=2.0)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    plate = Path("renders/m5/plates") / a.shot
    meta = json.load(open(plate / "shot.json"))
    s0, s1 = meta["frames_shot"]
    w, h = meta["resolution"]
    n = s1 - s0
    raw = frames(a.take, n)
    v = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    rng = np.random.default_rng(a.seed)
    noise = Image.fromarray((rng.random((h // 8, w // 8)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    noise = np.asarray(noise.filter(ImageFilter.GaussianBlur(10)), np.float32) / 255
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    out_dir = Path("takes/fx") / a.shot
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{a.shot}_reveal.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)],
                           stdin=subprocess.PIPE)
    for i in range(n):
        f = s0 + i
        b = np.asarray(Image.open(plate / "beauty" / f"{f:05d}.png").convert("RGB"), np.float32)
        d = np.asarray(Image.open(plate / "depth" / f"{f:05d}.png"), np.float32)
        d = d / (65535.0 if d.max() > 255 else 255.0)
        thr = 0.55 * noise + 0.45 * d  # near (white) turns last
        p = np.clip((i / FPS - a.start) / (a.end - a.start), 0, 1)
        p = p * p * (3 - 2 * p)
        alpha = np.clip((p * 1.25 - thr) / 0.25 + 0.0, 0, 1)[..., None] if 0 < p < 1 else np.full((h, w, 1), p)
        vi = v[min(i, len(v) - 1)].astype(np.float32)
        enc.stdin.write((b * (1 - alpha) + vi * alpha).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    t0 = meta["song_time"][0]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-ss", f"{t0:.3f}", "-t", f"{n / FPS:.3f}", "-i",
                    MASTER, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest",
                    str(out_dir / f"{a.shot}_reveal_audio.mp4")], check=True)
    print(f"{a.shot}: {n} frames -> {out}", flush=True)


if __name__ == "__main__":
    main()
