"""M6 S49: tape hiss and crackle under the shut-down notice (the human, rejecting the generated room sound as "far too
noisy for what it was going for": "make tape hiss and crackle"). Synthesised, seeded, so it is clean and repeatable:
the tape running on after the song's last track.

- Hiss: white noise shaped like a cassette's (a gentle high shelf from ~2 kHz, rolled off above 12 kHz and below
  150 Hz), the two channels 70% correlated; breathing with the tape's wow (0.55 Hz) and flutter (6.5 Hz), +-0.6 dB.
- Hum: 60 Hz mains and its odd harmonics, 30 dB under the hiss.
- Crackle: small clicks at random (Poisson, ~5 a second), each a 0.2-1.5 ms decaying burst band-passed 1-7 kHz, sizes
  log-normal; a bigger, duller pop about every 2 s. Left and right differ a little.
- A 0.25 s fade-in (the head engaging) and loudness-normalised to LUFS (default -30, under the opener's -26 room).

Usage: .venv/bin/python -I scripts/tape_hiss.py OUT.wav [--seconds 9.5] [--seed 49] [--lufs -30]
"""
import argparse
import subprocess
import tempfile

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000


def band(x, lo=None, hi=None, order=2):
    if lo and hi:
        sos = butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    elif lo:
        sos = butter(order, lo, "highpass", fs=SR, output="sos")
    else:
        sos = butter(order, hi, "lowpass", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seconds", type=float, default=9.5)
    ap.add_argument("--seed", type=int, default=49)
    ap.add_argument("--lufs", type=float, default=-30.0)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    n = int(a.seconds * SR)
    t = np.arange(n) / SR
    # the hiss
    common, own = rng.normal(size=n), rng.normal(size=(n, 2))
    w = 0.7 * common[:, None] + np.sqrt(1 - 0.7 ** 2) * own
    lowmid = band(w, 150, 2000)
    high = band(w, 2000, 12000)
    hiss = 0.45 * lowmid + 1.0 * high
    wow = 1 + 0.07 * np.sin(2 * np.pi * 0.55 * t + rng.uniform(0, 6)) + 0.02 * np.sin(2 * np.pi * 6.5 * t)
    hiss *= wow[:, None]
    hiss /= np.sqrt((hiss ** 2).mean())
    # the hum
    hum = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) / k for k, f in ((1, 60), (3, 180), (5, 300)))
    hum = (hum / np.sqrt((hum ** 2).mean()))[:, None] * 10 ** (-30 / 20)
    # the crackle
    crack = np.zeros((n, 2))
    def burst(at, ms, amp, lo, hi, side):
        L = max(8, int(ms / 1000 * SR))
        b = rng.normal(size=L) * np.exp(-np.linspace(0, 6, L))
        b = band(b[:, None], lo, hi)[:, 0] * amp
        j = min(n, at + L)
        for c in (0, 1):
            crack[at:j, c] += b[:j - at] * (1.0 if c == side else rng.uniform(0.3, 0.8))
    k = 0
    while True:
        k += rng.exponential(SR / 5)
        if k >= n:
            break
        burst(int(k), rng.uniform(0.2, 1.5), rng.lognormal(0, 0.6) * 2.2, 1000, 7000, rng.integers(2))
    k = 0
    while True:
        k += rng.exponential(SR * 2.0)
        if k >= n:
            break
        burst(int(k), rng.uniform(3, 6), rng.lognormal(0, 0.3) * 4.5, 200, 2500, rng.integers(2))
    out = hiss + hum + crack
    fi = int(0.25 * SR)
    out[:fi] *= np.linspace(0, 1, fi)[:, None] ** 2
    with tempfile.NamedTemporaryFile(suffix=".wav") as tf:
        sf.write(tf.name, out / np.abs(out).max() * 0.5, SR, subtype="FLOAT")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tf.name, "-af", f"loudnorm=I={a.lufs}:TP=-6:LRA=11",
                        "-ar", str(SR), "-c:a", "pcm_s24le", a.out], check=True)
    print(f"{a.out}: {a.seconds} s of tape hiss and crackle (seed {a.seed}, {a.lufs} LUFS)", flush=True)


if __name__ == "__main__":
    main()
