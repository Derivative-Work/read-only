"""M7: the burned-in captions and the SRT (brief, deliverables: "burned-in captions and a separate SRT"; done when
"captions sit within two frames of the timing map"). The human: "for the captions I think a VHS/old-school closed
caption font would work best".

The look is broadcast closed captioning as a late-'90s VCR recorded it off air (CEA-608, "line 21"):
- Roll-up, two rows (608's RU2), on a fixed grid of COLS columns, left-aligned: each word paints on at its first frame
  in the timing map (timing/timing_map.json, words' start_frame), so every word is on screen on the frame it is sung;
  each sung line starts a new row, and long lines wrap on the grid. A new row rolls the others up over ROLL s; the top
  row drops off. A run of lines is erased HOLD s after its last word, or when the next run starts.
- 608's conventions: ">>" at a change of speaker, a music note at the start of each sung line, "♪♪" over music with
  no words, and a few sound tags in brackets (TAGS), in capitals like the period's captions.
- The type: VT323 (SIL OFL 1.1; assets/fonts), a bitmap terminal face, stretched STRETCH times wide to the decoder's
  character cell (608: 32 columns of about 0.6 of a row's height); white on solid black boxes, one cell of box before
  and after the text, the rows stacked without gaps. VT323 has no music note: it is drawn here as a bitmap on the
  font's own pixel grid (608 has it as a special character).
- The tape: the layer is softened a little across (analog luma bandwidth) and its red and blue pulled a pixel apart.

Lines are the timing map's sung text, so the captions match what is heard (including Suno's sung stage directions).

Usage (also imported by scripts/assemble.py):
  .venv/bin/python -I scripts/captions.py srt OUT.srt [--from SONG_S --to SONG_S] [--offset VIDEO_S_OF_SONG_0]
  .venv/bin/python -I scripts/captions.py sheet OUT_DIR FRAMES_DIR T1 T2 ...   (stills over rendered frames)
"""
import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TM = json.loads((ROOT / "timing/timing_map.json").read_text())
FPS = TM["fps"]
FONT = ROOT / "assets/fonts/VT323-Regular.ttf"
PX_EM = 0.08          # VT323's pixel, in em (measured: 8 px at 100 px)
STRETCH = 1.5         # VT323's 0.4 em advance -> 0.6 em, the 608 cell
ROLL = 0.125          # s: the roll-up
HOLD = 2.0            # s after a run's last word, then erased
GAP = 2.5             # s of no words that ends a run
NOTE = ["..#..",      # the eighth note, on VT323's pixel grid (a row above the cap height, which is 7 px)
        "..##.",
        "..#.#",
        "..#.#",
        "..#..",
        ".##..",
        "###..",
        ".#..."]
# Sound tags: (song seconds on, off, text, where). "right" sets the row against the grid's right edge, clear of the
# opener's location caption at the lower left and of the eatery's sign above (608 places captions anywhere on its
# grid to keep them off on-screen text); "top" rows sit high.
TAGS = [
    (-17.7, -14.6, "[INDISTINCT CHATTER]", "right"),  # S01a: the eatery in the morning
    (0.14, 3.0, "♪♪", "right"),                       # the first piano chord (lower right, clear of the timecard)
    (187.9, 190.9, "[TAPE HISSES]", "bottom"),         # S48a's silence after "So was everything else."
    (194.65, 196.1, "[RECORD SCRATCH]", "bottom"),     # the scratches into the login prompt
]
# M8 (log/audits/m8_resolution.md, approved by the human): the conflict-of-interest disclosure after "allegedly" (Verse 4
# ends 168.96 s), at the top of the frame in the captions' own boxes, held until the second "This call was recorded":
# (on, off, text), song seconds. Burned in, not in the SRT (it isn't sound).
NOTICES = [
    (169.1, 176.4, "CLAUDE (ANTHROPIC) WROTE THESE LYRICS. REDDIT IS SUING ANTHROPIC, ALLEGING IT SCRAPED REDDIT "
                   "WITHOUT A LICENSE. ANTHROPIC DISPUTES IT. NO RULING YET."),
]
STYLES = {  # per output: columns, row height (fraction of frame height), the bottom row's bottom, the top row's top
    "main": {"cols": 32, "row": 50 / 1080, "bottom": 0.92, "top": 0.08},
    "vertical": {"cols": 22, "row": 60 / 1920, "bottom": 0.76, "top": 0.12},
}


def speaker(line):
    return line["singer"].split(",")[0]


def clean(w):
    return w.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').upper()


def wrap(texts, cols):
    """The fewest rows of at most cols that hold the words, broken so the longest row is as short as it can be
    (balanced, not greedy: no word left alone on a row). Returns lists of word indices."""
    n = len(texts)
    width = lambda a, b: sum(len(t) for t in texts[a:b]) + (b - a - 1)
    k = 1
    while True:
        best = None

        def go(a, rows_left, acc, worst):
            nonlocal best
            if rows_left == 1:
                w = width(a, n)
                if w <= cols and (best is None or max(worst, w) < best[0]):
                    best = (max(worst, w), acc + [list(range(a, n))])
                return
            for b in range(a + 1, n - rows_left + 2):
                w = width(a, b)
                if w > cols:
                    break
                go(b, rows_left - 1, acc + [list(range(a, b))], max(worst, w))

        go(0, k, [], 0)
        if best:
            return best[1]
        k += 1


def build_rows(cols):
    """The caption rows: [{"t": first frame's time, "pieces": [(frame, text)], "run": k, "where": ...}], and each run's
    erase time."""
    rows, runs, prev_spk, last_end, run = [], [], None, -1e9, -1
    events = [("line", ln["words"][0]["start_frame"] / FPS, ln) for ln in TM["lines"]]
    events += [("tag", on, t) for t in TAGS for on in [t[0]]]
    events.sort(key=lambda e: e[1])
    for kind, t0, ev in events:
        if kind == "tag":
            on, off, text, where = ev
            f = round(on * FPS)
            rows.append({"t": f / FPS, "pieces": [(f, text)], "run": len(runs), "where": where})
            runs.append(off)
            run, last_end = -1, -1e9  # a tag stands alone: the next line starts a new run
            continue
        if t0 - last_end > GAP or run < 0:
            runs.append(None)
            run = len(runs) - 1
        spk = speaker(ev)
        prefix = (">> " if prev_spk is not None and spk != prev_spk else "") + "♪ "
        prev_spk = spk
        texts = [(prefix if i == 0 else "") + clean(w["w"]) for i, w in enumerate(ev["words"])]
        for grp in wrap(texts, cols):
            ws = [(ev["words"][i]["start_frame"], texts[i]) for i in grp]
            rows.append({"t": ws[0][0] / FPS, "where": "bottom", "run": run,
                         "pieces": [(f, (" " if j else "") + x) for j, (f, x) in enumerate(ws)]})
        last_end = ev["words"][-1]["end_frame"] / FPS
        runs[run] = last_end + HOLD
    # a run is also erased when the next one starts
    starts = {}
    for r in rows:
        starts.setdefault(r["run"], r["t"])
    order = sorted(starts, key=starts.get)
    for a, b in zip(order, order[1:]):
        runs[a] = min(runs[a], starts[b] - ROLL)
    return rows, runs


class Captions:
    def __init__(self, size, style="main"):
        self.W, self.H = size
        st = STYLES[style]
        self.cols = st["cols"]
        self.row = round(st["row"] * self.H)               # row height = the font's em (ascent + descent)
        self.cell = self.row * 0.4 * STRETCH                # the 608 cell's width
        self.x0 = round((self.W - (self.cols + 2) * self.cell) / 2)  # the grid's left edge (with the box's lead cell)
        self.bottom = round(st["bottom"] * self.H)
        self.top = round(st["top"] * self.H)
        self.font = ImageFont.truetype(str(FONT), self.row)
        self.rows, self.runs = build_rows(self.cols)

    def notice(self, t):
        """The NOTICES rows on screen at song time t, as state entries at the top (slot k: the k-th row down)."""
        for on, off, text in NOTICES:
            if on <= t < off:
                words = text.split()
                return tuple((" ".join(words[i] for i in grp), "top", float(k))
                             for k, grp in enumerate(wrap(words, self.cols)))
        return ()

    def state(self, t):
        """The rows on screen at song time t: [(text, where, slot offset)]: slot 0 is the base row, 1 above it."""
        return self.lyric_state(t) + self.notice(t)

    def lyric_state(self, t):
        f = round(t * FPS)
        live = [r for r in self.rows if r["t"] - ROLL <= t < self.runs[r["run"]]]
        if not live:
            return ()
        run = live[-1]["run"]
        live = [r for r in live if r["run"] == run]
        out = []
        newest = live[-1]
        k = min(1.0, max(0.0, (t - (newest["t"] - ROLL)) / ROLL))  # 0 -> 1 over the roll before the newest row
        for i, r in enumerate(reversed(live[-3:])):
            if i == 0:
                if r["t"] > t:  # rolling: the newest row's first word isn't sung yet, its slot is empty
                    continue
                slot = 0.0
            else:
                slot = i - (1 - k)  # the older rows slide up a slot over the roll; past slot 1 they're gone
                if slot > 1.0 + 1e-6:
                    continue
            text = "".join(p for fr, p in r["pieces"] if fr <= f)
            if text:
                out.append((text, r["where"], round(slot * 8) / 8))
        return tuple(out)

    @lru_cache(maxsize=64)
    def layer(self, state):
        """The caption layer for a state: RGBA float32 (H, W, 4), premultiplied; None when empty."""
        if not state:
            return None
        w1 = int(np.ceil(self.W / STRETCH))
        im = Image.new("RGBA", (w1, self.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cw = self.row * 0.4  # the unstretched cell
        x0 = self.x0 / STRETCH
        px = self.row * PX_EM
        asc = self.row * 0.8
        for text, where, slot in state:
            y_top = (self.top + self.row * slot) if where == "top" else (self.bottom - self.row * (1 + slot))
            n = len(text)
            xb = x0 + (self.cols - n) * cw if where == "right" else x0
            d.rectangle([xb, y_top, xb + (n + 2) * cw - 1, y_top + self.row - 1], fill=(0, 0, 0, 235))
            x = xb + cw
            for ch in text:
                if ch == "♪":
                    base = y_top + asc
                    for j, line in enumerate(NOTE):
                        for i, c in enumerate(line):
                            if c == "#":
                                xx, yy = x + i * px, base - (len(NOTE) - j) * px
                                d.rectangle([xx, yy, xx + px - 1, yy + px - 1], fill=(255, 255, 255, 255))
                else:
                    d.text((x, y_top), ch, font=self.font, fill=(255, 255, 255, 255))
                x += cw
        im = im.resize((self.W, self.H), Image.BILINEAR)
        # the tape: a little softness across, red and blue a pixel apart
        a = np.asarray(im).astype(np.float32) / 255
        out = np.concatenate([a[..., :3] * a[..., 3:], a[..., 3:]], 2)  # premultiplied
        out = (out + 0.6 * np.roll(out, 1, 1) + 0.6 * np.roll(out, -1, 1)) / 2.2  # softened across
        k = max(1, round(self.H / 720))
        out[..., 0] = 0.5 * out[..., 0] + 0.5 * np.roll(out[..., 0], k, 1)   # red a pixel right
        out[..., 2] = 0.5 * out[..., 2] + 0.5 * np.roll(out[..., 2], -k, 1)  # blue a pixel left
        return out

    def over(self, frame, t):
        """frame: uint8 RGB (H, W, 3); t: song seconds. Returns the frame with the captions on it."""
        L = self.layer(self.state(t))
        if L is None:
            return frame
        x = frame.astype(np.float32) / 255
        x = L[..., :3] + x * (1 - L[..., 3:])
        return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)


def stamp(t):
    ms = int(round(max(t, 0.0) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt(t0=-1e9, t1=1e9, offset=0.0):
    """One cue per sung line (the timing map's text, its first word's frame to the next line or 1 s after its last
    word), and the sound tags; times from song t0's video time (offset = the video time of song 0)."""
    cues = []
    lines = TM["lines"]
    for i, ln in enumerate(lines):
        on = ln["words"][0]["start_frame"] / FPS
        off = ln["words"][-1]["end_frame"] / FPS + 1.0
        if i + 1 < len(lines):
            off = min(off, lines[i + 1]["words"][0]["start_frame"] / FPS)
        cues.append((on, off, "♪ " + ln["text"]))
    cues += [(on, off, text) for on, off, text, _ in TAGS]
    cues.sort()
    out = []
    for on, off, text in cues:
        a, b = max(on, t0), min(off, t1)
        if b - a < 0.3:
            continue
        base = offset if t0 < -1e8 else -t0
        out.append(f"{len(out) + 1}\n{stamp(a + base)} --> {stamp(b + base)}\n{text}\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["srt", "sheet"])
    ap.add_argument("out")
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--from", dest="t0", type=float, default=-1e9)
    ap.add_argument("--to", dest="t1", type=float, default=1e9)
    ap.add_argument("--offset", type=float, default=0.0)
    ap.add_argument("--style", default="main")
    a = ap.parse_args()
    if a.what == "srt":
        Path(a.out).write_text(srt(a.t0, a.t1, a.offset), encoding="utf-8")
        print(a.out)
        return
    import cv2
    frames, times = Path(a.rest[0]), [float(x) for x in a.rest[1:]]
    pre = 18.0
    Path(a.out).mkdir(parents=True, exist_ok=True)
    cap = None
    for t in times:
        f = round((pre + t) * FPS)
        img = cv2.cvtColor(cv2.imread(str(frames / f"f_{f:05d}.png")), cv2.COLOR_BGR2RGB)
        if cap is None:
            cap = Captions((img.shape[1], img.shape[0]), a.style)
        out = cap.over(img, t)
        cv2.imwrite(str(Path(a.out) / f"cc_{t:07.2f}.png"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
        print(t, cap.state(t))


if __name__ == "__main__":
    sys.exit(main())
