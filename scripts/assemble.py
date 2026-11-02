"""M7: the full edit (brief, deliverables: "Main video, 16:9, 1080p, 24 fps, with the locked track"; "burned-in
captions"), from the opener to the end card in one pass, every frame from its source, so nothing is encoded twice.
After Not Yet's scripts/assemble.py.

Picture, by video frame (song time t is at video time PRE + t; timing/timing_map.json, config/bookends.json):
- S01a-S01d: the opener render (--preroll), graded, with S01a's location caption and S01b's camera
  (bookends_assemble.opener_frame).
- S02-S39e (the match cut on the first piano chord to S40): Act 1's frames (--act1), each with its code-drawn
  overlay (renders/overlays/act1, 1080p RGBA, scaled), as the M4 cut.
- S40-S48b: Act 2 (act2_assemble.Act2: the rewind from the same Act 1 frames, the takes, the login prompt).
- S49: the photoreal take with its sign and screen (takes/fx/S49/S49_overlay.mp4), scaled to cover the frame like
  Act 2's takes (the M6 cut stretched its 1280x704 to 720 high; this crops 8 px top and bottom instead).
- S50: the end card (renders/screens/end_card).
- Captions over all of it (scripts/captions.py: closed captions as a VCR taped them), but not over the end card.

Sound, laid on one timeline: the diner ambience under the opener (in over 1 s, out by the cut), the master from the
cut (the first piano chord is song 0.14 s), the tape bed from S47 (scripts/tape_hiss.py: it eases up to full at S49,
out over the end card's first second), the end card's instrumental (scripts/cards_audio.py) from S50 at -4 dB.

--vertical: the vertical cut (brief: "9:16, S34-S45"), 1080x1920: config/reframe.json's window on each shot (or the
whole frame over a blurred fill, "fit"), the captions re-set for the narrow frame (captions.py "vertical": 22 columns,
higher, clear of a phone app's bottom controls), the master over the span; in from black over 0.4 s, picture and
music out together over the last fade_out_s.

Encoded for review with x264 (CRF 16) and AAC 256k; the release encode is the final render's (M7 gate).

Usage: .venv/bin/python -I scripts/assemble.py OUT.mp4 --preroll renders/m6/preroll_v6 --act1 renders/m7/act1/frames
       [--from VIDEO_S --to VIDEO_S] [--no-captions] [--srt OUT.srt]
       .venv/bin/python -I scripts/assemble.py OUT.mp4 --vertical --act1 renders/m7/act1/frames [--srt OUT.srt]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import act2_assemble as a2  # noqa: E402
import animatic_assemble as aa  # noqa: E402
import bookends_assemble as ba  # noqa: E402
import captions  # noqa: E402

FPS = aa.FPS
W, H = ba.W, ba.H
OVERLAY = Path("renders/overlays/act1")
S49 = Path("takes/fx/S49/S49_overlay.mp4")
END_CARD = Path("renders/screens/end_card")
AMBIENCE, TAPE, CARDS = ba.AMBIENCE, ba.S49_FOLEY, ba.CARDS


def read(p):
    return cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB)


def with_overlay(img, f):
    o = OVERLAY / f"f_{f:05d}.png"
    if not o.exists():
        return img
    top = cv2.imread(str(o), cv2.IMREAD_UNCHANGED)
    if top.shape[:2] != img.shape[:2]:
        top = cv2.resize(top, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
    a = top[..., 3:].astype(np.float32) / 255
    rgb = cv2.cvtColor(top[..., :3], cv2.COLOR_BGR2RGB).astype(np.float32)
    return (rgb * a + img.astype(np.float32) * (1 - a) + 0.5).astype(np.uint8)


def interp(keys, t):
    ts, vs = zip(*keys)
    return float(np.interp(t, ts, vs))


def vertical(a):
    """The vertical cut (module docstring)."""
    RF = json.loads(Path("config/reframe.json").read_text())
    SP, F = aa.spans(), aa.F
    VW, VH = 1080, 1920
    t0, t1 = SP[RF["from"]][0], SP[RF["to"]][1]
    f0, f1 = F(t0), F(t1)
    dur = (f1 - f0) / FPS
    fade = RF["fade_out_s"]
    act2 = a2.Act2(a.act1)
    act1 = Path(a.act1)
    cap = None if a.no_captions else captions.Captions((VW, VH), "vertical")
    order = list(SP)
    shots = order[order.index(RF["from"]):order.index(RF["to"]) + 1]
    g = (f"[1:a]atrim={t0}:{t1},asetpts=PTS-STARTPTS,afade=t=in:d=0.4,afade=t=out:st={dur - fade}:d={fade}[a]")
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
                            "-r", str(FPS), "-i", "-", "-i", aa.MASTER, "-filter_complex", g, "-map", "0:v",
                            "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt",
                            "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", a.out],
                           stdin=subprocess.PIPE)
    for f in range(f0, f1):
        t = f / FPS - aa.PRE
        img = act2.frame(f) if f >= act2.fa else with_overlay(read(act1 / f"f_{f:05d}.png"), f)
        h, w = img.shape[:2]
        sid = next(x for x in shots if SP[x][0] <= t < SP[x][1] + 1e-6)
        rf = RF["shots"][sid]
        if rf.get("mode") == "fit":
            bg = cv2.resize(img, (round(w * VH / h), VH), interpolation=cv2.INTER_AREA)
            x = (bg.shape[1] - VW) // 2
            bg = cv2.GaussianBlur(bg[:, x:x + VW], (0, 0), 40) * 0.45
            fg = cv2.resize(img, (VW, round(h * VW / w)), interpolation=cv2.INTER_LANCZOS4)
            y = (VH - fg.shape[0]) // 2
            bg[y:y + fg.shape[0]] = fg
            out = bg.astype(np.uint8)
        else:
            cw = round(h * VW / VH)
            x = round(min(max(interp(rf["cx"], t) * w - cw / 2, 0), w - cw))
            out = cv2.resize(img[:, x:x + cw], (VW, VH), interpolation=cv2.INTER_LANCZOS4)
        if cap is not None:
            out = cap.over(np.ascontiguousarray(out), t)
        k = min(1.0, (f - f0) / (0.4 * FPS), (f1 - 1 - f) / (fade * FPS))
        if k < 1:
            out = (out.astype(np.float32) * max(k, 0)).astype(np.uint8)
        enc.stdin.write(np.ascontiguousarray(out).tobytes())
    enc.stdin.close()
    if enc.wait():
        raise SystemExit("ffmpeg failed")
    if a.srt:
        Path(a.srt).write_text(captions.srt(t0, t1), encoding="utf-8")
    print(f"{a.out}: {dur:.2f} s (vertical, {RF['from']}-{RF['to']})", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--preroll")
    ap.add_argument("--act1", required=True)
    ap.add_argument("--vertical", action="store_true")
    ap.add_argument("--from", dest="v0", type=float, default=0.0, help="video seconds (a section, for checking)")
    ap.add_argument("--to", dest="v1", type=float, default=None)
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--srt", help="also write the captions as SRT (video times)")
    a = ap.parse_args()
    if Path(a.out).exists():
        raise SystemExit(f"{a.out} exists: archive it first (never overwrite an asset)")
    if a.vertical:
        return vertical(a)
    SP, F = aa.spans(), aa.F
    act1 = Path(a.act1)
    f_cut, f40, f49, f50 = F(SP["S02"][0]), F(SP["S40"][0]), F(SP["S49"][0]), F(SP["S50"][0])
    s49 = a2.frames(S49)
    card = sorted(END_CARD.glob("f_*.png"))
    f_end = f50 + len(card)
    act2 = a2.Act2(act1)
    cap = None if a.no_captions else captions.Captions((W, H))
    v0 = round(a.v0 * FPS)
    v1 = f_end if a.v1 is None else min(f_end, round(a.v1 * FPS))
    dur = (v1 - v0) / FPS

    # the sound, on the video's timeline
    ms = lambda s: int(round(s * 1000))  # noqa: E731
    cut = f_cut / FPS
    bed_len = SP["S49"][1] - SP[ba.TAPE_FROM][0]  # the bed from S47 to the end of S49, then out over 1.2 s
    ins = ["-i", str(AMBIENCE), "-i", aa.MASTER, "-i", str(TAPE), "-i", str(CARDS)]
    g = (f"[1:a]atrim=0:{cut + 0.4},afade=t=in:d=1.0,afade=t=out:st={cut - 0.1}:d=0.5,volume=0.8[amb];"
         f"[2:a]adelay={ms(aa.PRE)}:all=1[mus];"
         f"[3:a]atrim=0:{bed_len + 1.0},afade=t=out:st={bed_len - 0.2}:d=1.2,"
         f"adelay={ms(aa.PRE + SP[ba.TAPE_FROM][0])}:all=1[bed];"
         f"[4:a]volume={ba.CARDS_GAIN_DB}dB,adelay={ms(f50 / FPS)}:all=1[crd];"
         f"[amb][mus][bed][crd]amix=inputs=4:duration=longest:normalize=0,"
         f"atrim={v0 / FPS}:{v1 / FPS},asetpts=PTS-STARTPTS,apad,atrim=0:{dur}[a]")
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", *ins, "-filter_complex", g, "-map", "0:v", "-map", "[a]",
                            "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", a.out],
                           stdin=subprocess.PIPE)
    for f in range(v0, v1):
        if f < f_cut:
            img = ba.opener_frame(a.preroll, f, SP)
        elif f < f40:
            img = with_overlay(read(act1 / f"f_{f:05d}.png"), f)
        elif f < f49:
            img = act2.frame(f)
        elif f < f50:
            img = a2.cover(s49[min(f - f49, len(s49) - 1)])
        else:
            img = read(card[f - f50])
        if cap is not None and f < f50:
            img = cap.over(np.ascontiguousarray(img), f / FPS - aa.PRE)
        enc.stdin.write(np.ascontiguousarray(img).tobytes())
        if (f - v0) % 480 == 0:
            print(f"frame {f} / {v1}", flush=True)
    enc.stdin.close()
    if enc.wait():
        raise SystemExit("ffmpeg failed")
    if a.srt:
        Path(a.srt).write_text(captions.srt(offset=aa.PRE), encoding="utf-8")
    print(f"{a.out}: {dur:.2f} s, frames {v0}..{v1 - 1}", flush=True)


if __name__ == "__main__":
    main()
