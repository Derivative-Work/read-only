"""M2: the beat grid and the bars (downbeats) for a 4/4 boom-bap track. From Share the Shares (itself from Not Yet's 3/4 meter.py v2).

Beats: dynamic-programming beat tracking (Ellis 2007, librosa.beat.beat_track) on beat_this's frame-wise beat
probability (50 fps; the mix and the drum stem averaged), with a tempo prior from beat_this's own median beat and
high tightness, so the tracker keeps a steady pulse through the beat's drop-outs (Verse 2's "beat drops out", the turns before each section).

Bars: dynamic programming over those beats. Each beat scores beat_this's downbeat probability (mix and drums, max
within 40 ms) plus WORD_WEIGHT if a line starts within 80 ms of it. Bars of 4 beats cost nothing; 2, 3 or 6 cost
PENALTY. Irregular bars are listed for the ear check.

Usage: .venv/bin/python -I scripts/meter.py  ->  config/meter.json, timing/beats.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch
from beat_this.inference import Audio2Frames

sys.path.insert(0, str(Path(__file__).resolve().parent))
from song import TRACK, stem  # noqa: E402

BT_FPS = 50
SOURCES = [TRACK, stem("Drums")]
WORD_WEIGHT = 0.6
PENALTY = {4: 0.0, 2: 1.2, 3: 1.2, 6: 1.6}
TIGHTNESS = 400


def activations():
    a2f = Audio2Frames(checkpoint_path="final0", device="cuda")
    bs, ds = [], []
    for p in SOURCES:
        y, sr = sf.read(p, dtype="float32")
        b, d = a2f(y, sr)
        bs.append(torch.sigmoid(b).cpu().numpy())
        ds.append(torch.sigmoid(d).cpu().numpy())
    n = min(len(x) for x in bs)
    return np.mean([x[:n] for x in bs], 0), np.max([x[:n] for x in ds], 0)


def prior_tempo():
    """bpm prior: beat_this's median inter-beat interval on the mix (timing/beat_this.json)."""
    b = np.array(json.loads(Path("timing/beat_this.json").read_text())["mix"]["beats"])
    return 60.0 / float(np.median(np.diff(b))), len(b)


def track_beats(act, bpm):
    # librosa's beat tracker on the activation as an onset envelope: sr / hop = 50 fps.
    tempo, frames = librosa.beat.beat_track(onset_envelope=act, sr=BT_FPS * 441, hop_length=441, bpm=bpm,
                                            tightness=TIGHTNESS, trim=False, units="frames")
    return frames / BT_FPS


def best_bars(s):
    n = len(s)
    best, prev = np.full(n, -np.inf), np.full(n, -1)
    for k in range(min(6, n)):
        best[k] = s[k]
    for k in range(n):
        for L, pen in PENALTY.items():
            j = k - L
            if j >= 0 and best[j] > -np.inf and best[j] + s[k] - pen > best[k]:
                best[k], prev[k] = best[j] + s[k] - pen, j
    k = int(np.argmax(best[-6:])) + n - 6
    path = []
    while k >= 0:
        path.append(k)
        k = prev[k]
    return path[::-1]


def main():
    lines = json.loads(Path("timing/words.json").read_text())["lines"]
    bact, dact = activations()
    bpm, ngaps = prior_tempo()
    beats = track_beats(bact, bpm)
    dur = sf.info(TRACK).duration
    beats = beats[(beats >= 0) & (beats < dur)]
    f = np.clip(np.round(beats * BT_FPS).astype(int), 0, len(dact) - 1)
    s = np.array([dact[max(0, k - 2):k + 3].max() for k in f])
    starts = np.array([ln["start"] for ln in lines])
    s += WORD_WEIGHT * np.array([np.any(np.abs(starts - b) < 0.08) for b in beats])
    down = best_bars(s)
    lens = np.diff(down)
    bp = np.array([bact[max(0, k - 2):k + 3].max() for k in f])
    odd = [{"bar": i + 1, "beat": int(down[i]), "t": round(float(beats[down[i]]), 3), "beats": int(L)}
           for i, L in enumerate(lens) if L != 4]
    ibi = np.diff(beats)
    Path("timing/beats.json").write_text(json.dumps({
        "source": "librosa DP beat tracking on beat_this beat activations (scripts/meter.py)",
        "beats": [round(float(b), 4) for b in beats], "downbeat_beats": [int(d) for d in down]}) + "\n")
    Path("config/meter.json").write_text(json.dumps({
        "_doc": "Beats and 4/4 bars (scripts/meter.py): beat_this activations, a tempo prior from beat_this's median "
                "beat, DP beat tracking, DP bar choice. Bars that are not 4 beats are listed for the ear check.",
        "tempo_prior_bpm": round(bpm, 2), "from_beat_this_beats": ngaps, "tightness": TIGHTNESS,
        "beats": len(beats), "beat_bpm_median": round(60 / float(np.median(ibi)), 2),
        "beat_bpm_p5_p95": [round(60 / float(np.percentile(ibi, 95)), 1), round(60 / float(np.percentile(ibi, 5)), 1)],
        "beats_on_activation": round(float(np.mean(bp > 0.3)), 3),
        "bars": len(down), "bar_lengths": dict(Counter(int(x) for x in lens)), "irregular_bars": odd}, indent=1) + "\n")
    print(f"tempo prior {bpm:.1f} bpm ({ngaps} beat_this beats); {len(beats)} beats, median {60 / np.median(ibi):.1f} bpm "
          f"(p5-p95 {60 / np.percentile(ibi, 95):.1f}-{60 / np.percentile(ibi, 5):.1f}); beats on activation "
          f"{np.mean(bp > 0.3):.2f}; {len(down)} bars {dict(Counter(int(x) for x in lens))}")
    for o in odd:
        print("  irregular", o)
    # Where each line starts within its bar (for the ear check).
    dt = beats[down]
    pos = []
    for st in starts:
        k = int(np.searchsorted(dt, st + 0.08)) - 1
        bi = int(np.argmin(np.abs(beats - st)))
        pos.append(bi - down[k] + 1 if k >= 0 else None)
    print("line start beat-in-bar:", Counter(pos))


if __name__ == "__main__":
    main()
