"""M4: mouth shapes for the singing figures from Rhubarb Lip Sync itself (the brief: "Rhubarb, e.g."), replacing
scripts/visemes.py's in-house mapping (archived output: archive/timing/visemes_mms_superseded.json).

Each sung line is cut from its stem (padded), resampled to 16 kHz mono, and run through Rhubarb 1.14.0 with the
line's text as the dialog file (PocketSphinx recognizer, extended shapes G, H, X). Cue times come back relative to
the cut and are shifted to song seconds. Same file format as before, so gb.mouth() is unchanged.

Rhubarb lives in tools/Rhubarb-Lip-Sync-1.14.0-Linux/ (git-ignored; fetched from the project's GitHub release,
the zip's SHA-256 is in the production log).

Usage: .venv/bin/python -I scripts/rhubarb_visemes.py  ->  timing/visemes.json
"""
import json
import subprocess
import sys
from pathlib import Path

import librosa
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from song import stem  # noqa: E402

RHUBARB = Path("tools/Rhubarb-Lip-Sync-1.14.0-Linux/rhubarb")
CACHE = Path("cache/rhubarb")
SR = 16000
PAD = 0.25


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    lines = json.loads(Path("timing/words.json").read_text())["lines"]
    stems, out = {}, []
    for ln in lines:
        st = ln["stem"]
        if st not in stems:
            stems[st] = librosa.load(stem(st), sr=SR, mono=True)[0]
        a, b = max(0.0, ln["start"] - PAD), ln["end"] + PAD
        wav, txt, js = (CACHE / f"{ln['id']}.{e}" for e in ("wav", "txt", "json"))
        sf.write(wav, stems[st][int(a * SR):int(b * SR)], SR, subtype="PCM_16")
        txt.write_text(ln["text"] + "\n")
        subprocess.run([str(RHUBARB), "-q", "-r", "pocketSphinx", "-f", "json", "--extendedShapes", "GHX",
                        "-d", str(txt), "-o", str(js), str(wav)], check=True)
        cues = [[round(a + c["start"], 3), c["value"]] for c in json.loads(js.read_text())["mouthCues"]]
        out.append({"id": ln["id"], "stem": st, "start": ln["start"], "end": ln["end"], "cues": cues})
        print(f"{ln['id']} {ln['start']:7.2f} {len(cues):4d} cues  {''.join(s for _, s in cues)[:60]}")
    Path("timing/visemes.json").write_text(json.dumps({
        "method": "Rhubarb Lip Sync 1.14.0 (PocketSphinx, dialog text, extended shapes GHX) per line on its stem "
                  "(scripts/rhubarb_visemes.py)",
        "shapes": "A closed (MBP), B teeth (consonants, EE), C open (EH), D wide (AA), E round (AO), F pucker (OO, W), "
                  "G F/V, H L, X rest", "lines": out}, indent=1) + "\n")


if __name__ == "__main__":
    main()
