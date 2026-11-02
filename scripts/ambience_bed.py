"""M6: the opener's diner ambience as a bed that doesn't audibly cycle (the human: "I am hearing the foley repeat --
also use seed 3 and mix them together").

The sources are the full LTX-2.3 model's room-sound clips the human picked (takes/sfx/amb_dev_s2.wav, then s3), 4 s
each. Each of two layers is a chain of pieces 1.5-2.6 s long, each taken from a random place in a random one of the
clips (never the same clip and place twice running), joined with 0.5 s equal-power crossfades; the second layer starts
offset by half a piece. The layers are summed (each at -3 dB), so no stretch repeats at a fixed period and the two
clips play over each other throughout. Then loudness-normalised to -26 LUFS (the old bed's level).

Usage: .venv/bin/python -I scripts/ambience_bed.py OUT.wav [--seconds 19.5] [--seed 7]
"""
import argparse
import subprocess
import tempfile

import numpy as np
import soundfile as sf

SOURCES = ["takes/sfx/amb_dev_s2.wav", "takes/sfx/amb_dev_s3.wav"]
XF = 0.5


def layer(clips, sr, n, rng, lead=0.0):
    out = np.zeros((n, 2))
    x = int(-lead * sr)
    last = None
    xf = int(XF * sr)
    ramp = np.linspace(0, np.pi / 2, xf)
    fin, fout = np.sin(ramp)[:, None], np.cos(ramp)[:, None]
    while x < n:
        length = int(rng.uniform(1.5, 2.6) * sr)
        while True:
            k = int(rng.integers(len(clips)))
            src = clips[k]
            start = int(rng.integers(0, len(src) - length))
            if last is None or k != last[0] or abs(start - last[1]) > sr:
                break
        last = (k, start)
        piece = src[start:start + length].copy()
        piece[:xf] *= fin
        piece[-xf:] *= fout
        a, b = max(x, 0), min(x + length, n)
        if b > a:
            out[a:b] += piece[a - x:b - x]
        x += length - xf
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seconds", type=float, default=19.5)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    clips, sr = [], None
    for p in SOURCES:
        x, r = sf.read(p, always_2d=True)
        sr = sr or r
        assert r == sr
        x = x / (np.sqrt((x ** 2).mean()) + 1e-9)  # level-matched, so neither clip dominates
        clips.append(x)
    n = int(a.seconds * sr)
    rng = np.random.default_rng(a.seed)
    bed = (layer(clips, sr, n, rng) + layer(clips, sr, n, rng, lead=1.0)) * 10 ** (-3 / 20)
    with tempfile.NamedTemporaryFile(suffix=".wav") as t:
        sf.write(t.name, bed / np.abs(bed).max() * 0.5, sr, subtype="FLOAT")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", t.name, "-af", "loudnorm=I=-26:TP=-3:LRA=11",
                        "-ar", str(sr), "-c:a", "pcm_s24le", a.out], check=True)
    print(f"{a.out}: {a.seconds} s from {', '.join(SOURCES)}", flush=True)


if __name__ == "__main__":
    main()
