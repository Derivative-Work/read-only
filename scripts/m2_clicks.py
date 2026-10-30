"""M2 ear check, by sound only: the Suno mix with a click on every beat (an accent on each downbeat) and a tone at
each sync point the edit hangs on. From Share the Shares' c3_clicks.py (the human found its lane preview hard to
read; a click track was approved there).
Clicks: 3 ms decaying sine bursts, 1.2 kHz on beats, 2 kHz and louder on downbeats. Markers: a 0.25 s 660 Hz
tone pair (660 then 880 Hz), so they can't be mistaken for clicks. The mix is lowered 6 dB under them.
Usage: .venv/bin/python -I scripts/m2_clicks.py  ->  renders/m2/m2_clicks.wav, .mp3, renders/m2/m2_clicks.md
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

TM = json.loads(Path("timing/timing_map.json").read_text())
OUT = Path("renders/m2")
SHOT = {s["id"]: s for s in TM["shots"]}


def burst(sr, f, dur, amp):
    t = np.arange(int(sr * dur)) / sr
    return amp * np.sin(2 * np.pi * f * t) * np.exp(-t / (dur / 4))


def tone_pair(sr):
    a = np.concatenate([burst(sr, 660, 0.12, 0.5), burst(sr, 880, 0.13, 0.5)])
    t = np.arange(len(a)) / sr
    return a * np.minimum(1, t / 0.005)


def main():
    y, sr = sf.read(TM["audio"], dtype="float32")
    if y.ndim == 1:
        y = y[:, None].repeat(2, 1)
    mix = y * 10 ** (-6 / 20)
    click = np.zeros(len(mix), np.float32)
    beats = np.array(TM["beats"])
    down = set(TM["downbeat_beats"])
    for i, b in enumerate(beats):
        c = burst(sr, 2000, 0.03, 0.55) if i in down else burst(sr, 1200, 0.025, 0.3)
        k = int(round(b * sr))
        click[k:k + len(c)] += c[:max(0, len(click) - k)]
    marks = [("the first piano chord: the music starts here, 2.9 s before \"Yeah, hello?\" (proposed S01e cut)",
              TM["first_note"]),
             ("\"Yeah, hello?\" (the brief's S01e cue)", SHOT["S01e"]["t"]),
             ("the full beat comes in, after a drum fill from 0:07.1", [b for a, b in TM["drum_dropouts"] if b < 12][-1]),
             ("the beat drops out before \"…so I sold 'em the whole lot\" (S25)",
              next(a for a, b in TM["drum_dropouts"] if 85 < a < 90)),
             ("the first \"good bot\" reply (S39a, the headstones begin)", SHOT["S39a"]["t"]),
             ("\"Hold up\": the freeze and the rewind (S40)", SHOT["S40"]["t"]),
             ("end of \"So was everything else\": the silent hold on the open grave (S48a)", SHOT["S48a"]["t"])]
    tp = tone_pair(sr)
    for _, t in marks:
        k = int(round(t * sr))
        click[k:k + len(tp)] += tp[:max(0, len(click) - k)]
    out = np.clip(mix + click[:, None], -1, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    sf.write(OUT / "c3_clicks.wav", out, sr, subtype="PCM_16")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT / "c3_clicks.wav"), "-b:a", "256k",
                    str(OUT / "c3_clicks.mp3")], check=True)
    L = ["# M2 ear check", "", "`m2_clicks.mp3`: the song 6 dB down, a click on every beat (higher and louder on "
         "beat 1 of each bar), and a two-note tone (low, high) at each of these:", "",
         "| Tone at | What should happen there |", "| --- | --- |"]
    L += [f"| {int(t // 60)}:{t % 60:05.2f} | {name} |" for name, t in marks]
    odd = [b for b in TM["bars"][:-1] if b["beats"] != 4]  # the last bar runs into the end of the audio
    L += ["", "Listen for: the clicks sitting on the pulse throughout, the loud click on each bar's first beat, and "
          "each tone at its moment. Two bars are 2 beats long (both at a \"(beat)\" pause in the lyrics), so the loud click "
          "comes early there: "
          + ", ".join(f"{int(b['start'] // 60)}:{b['start'] % 60:05.2f}" for b in odd) + "."]
    (OUT / "c3_clicks.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
