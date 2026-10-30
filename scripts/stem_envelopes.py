"""M2: per-frame loudness envelopes of the two vocal stems, the drum stem's onsets, and the beat's drop-outs.

Envelopes are RMS at the video's fps, in dB normalised to 0..1 over a 40 dB range: the lead drives the performers'
mouths in Act 1 (the brief's B+M shots; Rhubarb Lip Sync may refine them), the backing the crowd's replies. Drum onsets
(librosa onset detection on the drum stem, backtracked) are for hits. Drop-outs are where the drum stem falls below
-45 dBFS RMS for at least 0.4 s: the song's stops (Verse 2's "beat drops out" and the turns between sections).
From Share the Shares' stem_envelopes.py.
Usage: .venv/bin/python -I scripts/stem_envelopes.py -> timing/envelopes/*.npy, timing/drum_onsets.json
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from song import stem  # noqa: E402

FPS = json.loads(Path("config/render_profiles.json").read_text())["fps"]
SR = 48000
out = Path("timing/envelopes")
out.mkdir(parents=True, exist_ok=True)
for name, tag in (("Lead Vocals", "lead"), ("Backing Vocals", "backing")):
    y, _ = librosa.load(stem(name), sr=SR, mono=True)
    hop = SR // FPS
    rms = librosa.feature.rms(y=y, frame_length=hop * 2, hop_length=hop, center=True)[0]
    db = 20 * np.log10(rms / (rms.max() + 1e-12) + 1e-12)
    np.save(out / f"{tag}.npy", np.clip((db + 40) / 40, 0, 1).astype(np.float32))
    print(tag, len(rms), "frames")
y, _ = librosa.load(stem("Drums"), sr=22050, mono=True)
on = librosa.onset.onset_detect(y=y, sr=22050, hop_length=256, backtrack=True, units="time", delta=0.12)
hop = 441  # 50 per second
rms = 20 * np.log10(librosa.feature.rms(y=y, frame_length=hop * 2, hop_length=hop)[0] + 1e-9)
quiet = rms < -45
drops, i = [], 0
while i < len(quiet):
    if quiet[i]:
        j = i
        while j < len(quiet) and quiet[j]:
            j += 1
        if (j - i) / 50 >= 0.4:
            drops.append([round(i / 50, 2), round(j / 50, 2)])
        i = j
    else:
        i += 1
Path("timing/drum_onsets.json").write_text(json.dumps({
    "method": "librosa onset_detect, backtrack, delta 0.12; drop-outs: drum stem RMS < -45 dBFS for >= 0.4 s",
    "onsets": [round(float(t), 4) for t in on], "dropouts": drops}) + "\n")
print("drum onsets", len(on), "drop-outs", drops)
