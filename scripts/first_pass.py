"""M2 scratch pass: what is sung where. faster-whisper (large-v3, float16, CUDA) on the two vocal stems, no prompt,
word timestamps, so the as-sung lyrics and the section windows for the forced alignment come from the audio, not the
submitted text. From Share the Shares' first_pass.py (medium.en on CPU there; this box has the RTX 5090, and rap
needs the larger model). Usage: .venv/bin/python -I scripts/first_pass.py -> timing/first_pass_{lead,backing}.json
"""
import ctypes
import json
import sys
from pathlib import Path

import nvidia.cublas.lib
import nvidia.cudnn.lib

# CTranslate2 dlopens cuBLAS 12 and cuDNN 9 by soname; the pip wheels put them under site-packages, off the loader's
# path, so preload them (RTLD_GLOBAL) before faster_whisper imports CTranslate2.
for mod, libs in ((nvidia.cublas.lib, ["libcublasLt.so.12", "libcublas.so.12"]),
                  (nvidia.cudnn.lib, ["libcudnn.so.9"])):
    for lib in libs:
        ctypes.CDLL(str(Path(mod.__path__[0]) / lib), mode=ctypes.RTLD_GLOBAL)

import librosa  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from song import stem  # noqa: E402

MODEL = "large-v3"
model = WhisperModel(MODEL, device="cuda", compute_type="float16")
for name, tag in (("Lead Vocals", "lead"), ("Backing Vocals", "backing")):
    # decoded here, not by faster-whisper: its PyAV call breaks on the installed PyAV (metadata_errors)
    audio = librosa.load(stem(name), sr=16000, mono=True)[0]
    segs, info = model.transcribe(audio, language="en", beam_size=5, temperature=0, word_timestamps=True,
                                  vad_filter=False, condition_on_previous_text=False)
    out = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
            "words": [{"w": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2), "p": round(w.probability, 2)}
                      for w in s.words]} for s in segs]
    Path(f"timing/first_pass_{tag}.json").write_text(json.dumps({"model": f"faster-whisper {MODEL} float16", "stem": name,
                                                                  "segments": out}, indent=1) + "\n")
    for s in out:
        print(f"{tag} {s['start']:7.2f}-{s['end']:7.2f} {s['text']}")
