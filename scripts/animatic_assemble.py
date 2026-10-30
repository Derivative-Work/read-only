"""Assemble the M3 animatic: rendered frames + the post-filtered master + burned-in review captions.

After Not Yet's animatic_assemble.py. The edit runs pre-roll (S01a-S01d, no music: the brief's cold open), the song
(the master starts at the pre-roll's end, so song time t is at video time PRE + t), then post-roll (S48b-S50).

- S40 (F, "hard freeze; the whole video rewinds at high speed through earlier shots"): built here from the rendered
  frames. The first REWIND_HOLD s hold S39e's last frame; the rest plays every frame from S40's start back to the
  S01e cut in reverse, sampled evenly, so the rewind reaches the payphone at S40's end.
- Captions (ASS via libass): each lyric line with its words lighting as sung; the shot ID and pipeline code top right;
  the brief's gag/overlay note for shots with a JS overlay or F effect, bottom left in brackets, since those are drawn
  at M4; placeholder cards for the code-drawn shots (S48b's login prompt, S50's end card) and for S01b's real photo.

Usage: .venv/bin/python -I scripts/animatic_assemble.py <frames dir> <out.mp4>
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TM = json.loads(Path("timing/timing_map.json").read_text())
BOOK = json.loads(Path("config/bookends.json").read_text())
FPS = TM["fps"]
PRE = sum(BOOK["preroll"].values())
MASTER = "audio/master/Read-Only (postfilter m6f).wav"
REWIND_HOLD = 0.4


def F(t):
    return int(round((PRE + t) * FPS))


def ts(v):
    h, r = divmod(max(v, 0.0), 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def spans():
    out, t = {}, -PRE
    for sid, d in BOOK["preroll"].items():
        out[sid] = (t, t + d)
        t += d
    for s in TM["shots"]:
        if s["t"] is not None and s["id"] != "S01e":
            out[s["id"]] = (s["t"], s["end"])
    out["S01d"] = (out["S01d"][0], out["S02"][0])
    t = TM["duration_s"]
    for sid, d in BOOK["postroll"].items():
        out[sid] = (t, t + d)
        t += d
    return dict(sorted(out.items(), key=lambda kv: kv[1][0]))


def brief_rows():
    rows = {}
    for s in TM["shots"]:
        rows[s["id"]] = s
    return rows


def ass(w, h, SP):
    L = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "",
         "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
         "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
         "MarginR, MarginV, Encoding",
         "Style: Cap,Inter,20,&H00B0E3FF,&H80B0B0B0,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,1.2,0,2,20,20,14,1",
         "Style: Id,JetBrains Mono,13,&H009AE35F,&H009AE35F,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,1,0,9,10,10,8,1",
         "Style: Note,Inter,12,&H00D8E8F0,&H00D8E8F0,&H00000000,&H64000000,0,1,0,0,100,100,0,0,1,1,0,7,10,10,8,1",
         "Style: Card,Inter,22,&H00F1F4EE,&H00F1F4EE,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,30,30,30,1",
         "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for ln in TM["lines"]:
        a, b = ln["start"] - 0.4, ln["end"] + 0.6
        parts, t = [], a
        for wd in ln["words"]:
            parts.append(f"{{\\k{max(0, int(round((wd['start'] - t) * 100)))}}}")
            parts.append(wd["w"] + " ")
            t = wd["start"]
        L.append(f"Dialogue: 0,{ts(PRE + a)},{ts(PRE + b)},Cap,,0,0,0,,{''.join(parts)}")
    rows = brief_rows()
    for sid, (a, b) in SP.items():
        r = rows.get(sid, {})
        pipe = r.get("pipeline", {"S49": "B→V+JS", "S50": "JS+F"}.get(sid, "B"))
        L.append(f"Dialogue: 1,{ts(PRE + a)},{ts(PRE + b)},Id,,0,0,0,,{sid}  {pipe}")
        note = r.get("overlay", "")
        if note and note != "None" and ("JS" in pipe or "F" in pipe or "Real" in pipe or "LS" in pipe):
            L.append(f"Dialogue: 1,{ts(PRE + a)},{ts(PRE + b)},Note,,0,0,0,,[{pipe}: {note}]")
        if "B→V" in pipe:
            L.append(f"Dialogue: 1,{ts(PRE + a)},{ts(PRE + b)},Note,,0,0,30,,[Act 2: made photoreal at M5]")
    cards = {"S01b": "the real plate photo appears on the phone (M6)",
             "S48b": "S48b: fade to black, then a generic login prompt, cursor blinking (JS, M4)",
             "S49": "S49: photoreal at M5; the app's shut-down notice on the phone (JS)",
             "S50": "S50: end card: AI-generated satire, credits, fact card, disclosures (JS, M6)"}
    for sid, txt in cards.items():
        a, b = SP[sid]
        L.append(f"Dialogue: 2,{ts(PRE + a + 0.2)},{ts(PRE + b)},Card,,0,0,0,,{{\\an5\\fad(300,300)}}{txt}")
    return "\n".join(L) + "\n"


def main():
    frames, out = Path(sys.argv[1]), sys.argv[2]
    SP = spans()
    have = sorted(int(p.stem[2:]) for p in frames.glob("f_*.png"))
    seq = list(range(0, F(max(b for _, b in SP.values()))))  # the whole edit, rendered or not
    a, b = SP["S40"]
    fa, fb = F(a), F(b)
    hold = fa + int(round(REWIND_HOLD * FPS))
    back = list(range(fa - 1, F(SP["S02"][0]) - 1, -1))
    n = fb - hold
    for k, f in enumerate(range(fa, fb)):
        if f < hold:
            seq[f] = fa - 1
        else:
            seq[f] = back[int((f - hold) * len(back) / n)]
    from PIL import Image
    w, h = Image.open(frames / f"f_{have[0]:05d}.png").size
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for i, f in enumerate(seq):
            src = frames / f"f_{f:05d}.png"
            if not src.exists():  # a frame not rendered (a gap): repeat the previous one
                src = frames / f"f_{max([x for x in have if x <= f] or have[:1]):05d}.png"
            os.symlink(src.resolve(), td / f"{i:05d}.png")
        (td / "caps.ass").write_text(ass(w, h, SP))
        cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(td / "%05d.png"),
               "-i", MASTER, "-filter_complex",
               f"[0:v]subtitles={td / 'caps.ass'}:fontsdir=assets/fonts,format=yuv420p[v];"
               f"[1:a]adelay={int(PRE * 1000)}:all=1,apad[a]",
               "-map", "[v]", "-map", "[a]", "-shortest", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
               "-c:a", "aac", "-b:a", "192k", out]
        subprocess.run(cmd, check=True)
    print(out, f"{len(seq) / FPS:.2f} s", f"pre-roll {PRE:.1f} s")


if __name__ == "__main__":
    main()
