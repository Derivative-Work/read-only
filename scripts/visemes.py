"""M4: mouth shapes for Act 1's singing figures, in Rhubarb Lip Sync's set (A-H, X; the brief names Rhubarb "e.g.").

Rhubarb's binary was not run: downloading and running it was blocked by this session's permissions. So this follows
its idea with what M2 already uses. torchaudio's MMS forced aligner (as in scripts/align_words.py) aligns each sung
line again, now keeping every letter's span. Letters, and a few digraphs, map onto Rhubarb's mouth shapes. Where the
stem is quiet (below -30 dB of its peak) the mouth rests (X).

Rhubarb's shapes (its README): A closed (M B P); B slightly open, teeth (most consonants, EE); C open (EH, AE);
D wide open (AA); E rounded (AO, ER); F puckered (UW, OW, W); G teeth on lip (F V); H tongue up (L); X rest.

Usage: .venv/bin/python -I scripts/visemes.py  ->  timing/visemes.json
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import torch
import torchaudio

sys.path.insert(0, str(Path(__file__).resolve().parent))
from align_words import SR, spoken  # noqa: E402
from song import stem  # noqa: E402

DIGRAPHS = {"oo": "F", "ou": "F", "ow": "F", "ee": "B", "ea": "B", "th": "B", "ch": "B", "sh": "B", "ph": "G",
            "ai": "C", "ay": "C", "oi": "E", "er": "E", "ar": "D", "or": "E"}
LETTERS = {**{c: "A" for c in "mbp"}, **{c: "G" for c in "fv"}, "l": "H", "w": "F", "u": "F", "o": "E", "a": "D",
           "e": "C", "i": "C", "y": "B"}
PAD = 0.15


def shapes(word):
    """(letter index, shape) for each letter, a digraph taking both of its letters."""
    out, k = [], 0
    while k < len(word):
        dg = word[k:k + 2]
        if dg in DIGRAPHS:
            out += [(k, DIGRAPHS[dg]), (k + 1, DIGRAPHS[dg])]
            k += 2
        else:
            out.append((k, LETTERS.get(word[k], "B")))
            k += 1
    return out


def main():
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=False)
    tokenizer, aligner = bundle.get_tokenizer(), bundle.get_aligner()
    lines = json.loads(Path("timing/words.json").read_text())["lines"]
    stems, out = {}, []
    for ln in lines:
        st = ln["stem"]
        if st not in stems:
            stems[st] = librosa.load(stem(st), sr=SR, mono=True)[0]
        voc = stems[st]
        a, b = max(0.0, ln["start"] - PAD), ln["end"] + PAD
        i0, i1 = int(a * SR), min(len(voc), int(b * SR))
        y = voc[i0:i1] / (np.abs(voc[i0:i1]).max() + 1e-9)
        words = [p for w in ln["words"] for p in spoken(w["w"])]
        with torch.inference_mode():
            emission, _ = model(torch.from_numpy(y).float().unsqueeze(0))
            spans = aligner(emission[0], tokenizer(words))
        ratio = (i1 - i0) / emission.shape[1] / SR
        # loudness gate, 10 ms hops
        rms = librosa.feature.rms(y=y, frame_length=640, hop_length=160)[0]
        db = 20 * np.log10(rms / (np.abs(voc).max() + 1e-12) + 1e-12)
        cues = []
        for w, sp in zip(words, spans):
            for k, shape in shapes(w):
                if k >= len(sp):
                    continue
                t0, t1 = sp[k].start * ratio + a, sp[k].end * ratio + a
                f = min(len(db) - 1, int(((t0 + t1) / 2 - a) * SR / 160))
                cues.append([round(t0, 3), shape if db[f] > -30 else "X"])
            cues.append([round(sp[-1].end * ratio + a, 3), "X"])
        # merge repeats; a rest shorter than 60 ms between letters is dropped (the mouth doesn't close mid-phrase)
        merged = []
        for k, (t, s) in enumerate(cues):
            nxt = cues[k + 1][0] if k + 1 < len(cues) else t + 1
            if s == "X" and nxt - t < 0.06:
                continue
            if merged and merged[-1][1] == s:
                continue
            merged.append([t, s])
        out.append({"id": ln["id"], "stem": st, "start": ln["start"], "end": ln["end"], "cues": merged})
        print(f"{ln['id']} {ln['start']:7.2f} {len(merged):4d} cues  {''.join(s for _, s in merged)[:60]}")
    Path("timing/visemes.json").write_text(json.dumps({
        "method": "torchaudio MMS_FA letter spans mapped to Rhubarb Lip Sync's mouth shapes (scripts/visemes.py)",
        "shapes": "A closed (MBP), B teeth (consonants, EE), C open (EH), D wide (AA), E round (AO), F pucker (OO, W), "
                  "G F/V, H L, X rest", "lines": out}, indent=1) + "\n")


if __name__ == "__main__":
    main()
