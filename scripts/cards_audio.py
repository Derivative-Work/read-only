"""M6 S50: an instrumental under the end card (the human: "make an instrumental bounce for the text afterwards (please
make sure to run it through the post filter)"). After Not Yet's scripts/cards_audio.py (its limiter and post-filter
call), with this track's span and the master's own chain.

1. Bounce: the stems from START_S (Verse 4's first downbeat, 2:34.68, "I'm the bot") minus PREROLL_S of context for
   the model, to the stems' end (3:16.16, the piano tail): 41.48 s, the end card's 42 s less half a second. Muted: both
   vocal stems (an instrumental) and "9 Other" (the record scratches, already the cue for the login screen in S48b).
   A lookahead peak limiter (LIMIT_CEILING_DB) catches the stem sum's peaks.
2. Post-filter: music-deslop M6f 10k, the release chain's defaults, as this track's master was made
   (audio/master/REPORT.md: with the fallback, the default; Read-Only had no fallback passages).
3. Trim the pre-roll; a 10 ms fade-in on the downbeat, FADE_OUT_S on the stems' end.

The edit places it from the end card's first frame (S50).

Usage: .venv/bin/python -I scripts/cards_audio.py  ->  audio/post/cards_bounce_{raw,deslop}.wav,
                                                        audio/post/cards_audio.wav, timing/cards_audio.json
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
STEMS = ROOT / "audio/stems"
MUTED = {"Lead Vocals", "Backing Vocals", "Other"}
LIMIT_CEILING_DB = -1.0
LOOKAHEAD_S = 0.005
RELEASE_S = 0.08
START_S = 154.68  # Verse 4's first downbeat (timing/beats.json)
PREROLL_S = 4.0
FADE_OUT_S = 1.0
DESLOP = Path.home() / "Code/music-deslop"
CKPT = Path.home() / "Code/music-deslop-data/release/m6f_10k.safetensors"
RAW, DESLOPPED, OUT = (ROOT / "audio/post" / f for f in ("cards_bounce_raw.wav", "cards_bounce_deslop.wav",
                                                       "cards_audio.wav"))


def stem_name(p):
    return p.stem.split(" ", 1)[1]  # "2 Drums" -> "Drums"


def bounce():
    names = sorted(p for p in STEMS.glob("*.wav") if stem_name(p) not in MUTED)
    a = START_S - PREROLL_S
    mix, sr = None, None
    for p in names:
        info = sf.info(p)
        y, sr = sf.read(p, start=int(round(a * info.samplerate)), always_2d=True)
        mix = y if mix is None else mix + y
    mix, gr = limit(mix, sr)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    sf.write(RAW, mix, sr, subtype="FLOAT")
    return [p.name for p in names], sr, gr


def limit(x, sr):
    from scipy.ndimage import minimum_filter1d
    ceil = 10 ** (LIMIT_CEILING_DB / 20)
    peak = np.abs(x).max(axis=1)
    need = np.minimum(1.0, ceil / np.maximum(peak, 1e-12))
    L = int(LOOKAHEAD_S * sr)
    g = minimum_filter1d(need, size=2 * L + 1, mode="nearest")
    k = 1 - np.exp(-1 / (RELEASE_S * sr))
    out = np.empty_like(g)
    cur = 1.0
    for i, v in enumerate(g):  # release: rise back towards 1 no faster than the time constant
        cur = v if v < cur else cur + (min(v, 1.0) - cur) * k
        out[i] = cur
    win = np.hanning(L + 1)
    out = np.convolve(out, win / win.sum(), mode="same")
    y = x * out[:, None]
    return y, {"ceiling_db": LIMIT_CEILING_DB, "lookahead_s": LOOKAHEAD_S, "release_s": RELEASE_S,
               "in_peak_dbfs": round(20 * np.log10(peak.max()), 2),
               "out_peak_dbfs": round(20 * np.log10(np.abs(y).max()), 2),
               "max_reduction_db": round(-20 * np.log10(out.min()), 2),
               "time_reducing_s": round(float((out < 0.999).sum()) / sr, 2)}


def deslop():
    cmd = ["uv", "run", "python", "-m", "postfilter.infer", "--in", str(RAW), "--out", str(DESLOPPED),
           "--ckpt", str(CKPT), "--source", "suno"]
    subprocess.run(cmd, cwd=DESLOP, check=True)
    return cmd


def finish(sr):
    y, sr2 = sf.read(DESLOPPED, always_2d=True)
    assert sr2 == sr
    out = y[int(round(PREROLL_S * sr)):].copy()
    fi, fo = int(0.01 * sr), int(FADE_OUT_S * sr)
    out[:fi] *= np.linspace(0, 1, fi)[:, None]
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    peak = np.abs(out).max()
    if peak > 10 ** (-0.1 / 20):
        out *= 10 ** (-0.1 / 20) / peak
    sf.write(OUT, out, sr, subtype="PCM_24")
    return len(out) / sr, 20 * np.log10(np.abs(out).max())


def main():
    stems, sr, gr = bounce()
    cmd = deslop()
    dur, peak = finish(sr)
    info = {"stems": stems, "muted": sorted(MUTED), "limiter": gr, "start_song_s": START_S, "preroll_s": PREROLL_S,
            "fade_out_s": FADE_OUT_S, "at": "S50 start", "duration_s": round(dur, 4), "peak_dbfs": round(peak, 2),
            "postfilter": " ".join(cmd[2:]), "postfilter_repo": str(DESLOP),
            "postfilter_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=DESLOP, capture_output=True,
                                                text=True).stdout.strip(),
            "output": str(OUT.relative_to(ROOT))}
    (ROOT / "timing/cards_audio.json").write_text(json.dumps(info, indent=1) + "\n")
    print(info)


if __name__ == "__main__":
    main()
