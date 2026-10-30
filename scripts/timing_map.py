"""M2: the timing map, the clock every later step reads.

Joins the beats and bars (scripts/meter.py), the aligned words (scripts/align_words.py), the drum onsets and drop-outs
(scripts/stem_envelopes.py) and the brief's shot list (docs/brief.md) into timing/timing_map.json and a readable
timing/timing_map.md. Times are seconds of the Suno mix; frames are at the render fps (config/render_profiles.json).
From Share the Shares' timing_map.py, re-cut for this brief's six-column shot tables and its cue wording.

Shot cues (brief: "cues are lyric lines"): resolved in reading order, searching forward from the previous shot.
- A quoted cue is matched to the first line at or after that point holding most of its words; the shot starts at the
  first cue word sung there (a cue may open with an ad-lib, as "(He got the tape!) I got the tape…").
- An ordinal cue (The first "good bot" replies) is the n'th time the phrase is sung after the previous shot.
- "Before the music" is pre-roll; "Whole hook" is the start of the next hook; "Silence after …" is the end of the
  outro's last word; the bookends' S49-S50 and "After the last word" (S48b) come after the audio.
- "Replies continue" / "The last replies" (S39b-S39e): the replies, from S39a to S40's "Hold up", split into equal
  runs of whole beats, one per shot (a proposal for M3's animatic).
- A retired ID gets no time. A cue that can't be found is listed for the ear check. config/shot_holds.json (if
  present) moves a shot's start off its cue (the human's notes).

Usage: .venv/bin/python -I scripts/timing_map.py  ->  timing/timing_map.json, timing/timing_map.md, config/shot_anchors.json
"""
import json
import re
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from song import TRACK  # noqa: E402

FPS = json.loads(Path("config/render_profiles.json").read_text())["fps"]
HOLDS_PATH = Path("config/shot_holds.json")
HOLDS = ({k: v for k, v in json.loads(HOLDS_PATH.read_text()).items() if not k.startswith("_")}
         if HOLDS_PATH.exists() else {})
ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4}
ORDINAL = re.compile(r"the (first|second|third|fourth) \"")
SPLIT_REPLIES = ("replies continue", "the last replies")


def fr(t):
    return None if t is None else int(round(t * FPS))


def norm(s):
    return re.sub(r"[^a-z0-9' ]", " ", s.lower().replace("’", "'").replace("…", " ").replace("-", " ")).split()


def shot_rows():
    rows = []
    for line in Path("docs/brief.md").read_text().splitlines():
        # ID | Section | Cue | Start | Shot | Gag / overlay | Pipeline (Start: this map's times, written back at M2)
        m = re.match(r"\| (S\d\d[a-z]?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$", line)
        if m:
            rows.append({"id": m.group(1), "section": m.group(2), "cue": m.group(3), "brief_start": m.group(4),
                         "picture": m.group(5), "overlay": m.group(6), "pipeline": m.group(7)})
            continue
        m = re.match(r"\| (S\d\d[a-z]?) \| (.*?) \| (.*?) \| (.*?) \|$", line)  # bookends: no cue column
        if m and m.group(2) in ("Closing bookend", "End card"):  # not the headstone table's rows
            rows.append({"id": m.group(1), "section": m.group(2), "cue": "", "picture": m.group(3), "overlay": "",
                         "pipeline": m.group(4)})
    return rows


def first_note():
    """The first onset in the mix (the piano and synth intro, before any word)."""
    y, sr = librosa.load(TRACK, sr=22050, mono=True, duration=5)
    return round(float(librosa.onset.onset_detect(y=y, sr=sr, units="time", backtrack=True)[0]), 3)


def find_quoted(lines, cue, cursor):
    want = norm(cue)
    for ln in lines:
        if ln["end"] < cursor - 0.01:
            continue
        toks = [norm(w["w"]) for w in ln["words"]]
        flat = [x for tk in toks for x in tk]
        if sum(1 for w in want if w in flat) / len(want) < 0.75:
            continue
        wi = next((i for i, tk in enumerate(toks) if set(tk) & set(want) and ln["words"][i]["start"] >= cursor - 0.01),
                  None)
        if wi is not None:
            return ln, ln["words"][wi]["start"]
    return None, None


def main():
    B = json.loads(Path("timing/beats.json").read_text())
    beats, down = np.array(B["beats"]), B["downbeat_beats"]
    lines = json.loads(Path("timing/words.json").read_text())["lines"]
    drums = json.loads(Path("timing/drum_onsets.json").read_text())
    dur = sf.info(TRACK).duration
    bars = []
    for i, k in enumerate(down):
        end_b = down[i + 1] if i + 1 < len(down) else len(beats)
        nb = end_b - k
        span = (beats[end_b] if end_b < len(beats) else beats[-1] + np.median(np.diff(beats))) - beats[k]
        bars.append({"n": i + 1, "beat": int(k), "start": round(float(beats[k]), 4), "beats": int(nb),
                     "bpm": round(60 * nb / span, 1), "frame": fr(beats[k])})
    dts = np.array([b["start"] for b in bars])
    sections = []
    for ln in lines:
        if not sections or ln["section"] != sections[-1]["name"]:
            sections.append({"name": ln["section"], "singer": ln["singer"], "stem": ln["stem"], "start": ln["start"]})
        sections[-1]["end"] = ln["end"]
    for s in sections:
        s["frame"] = fr(s["start"])
    for ln in lines:
        ln["start_frame"], ln["end_frame"] = fr(ln["start"]), fr(ln["end"])
        for w in ln["words"]:
            w["start_frame"], w["end_frame"] = fr(w["start"]), fr(w["end"])
    last_word = lines[-1]["end"]
    rows = shot_rows()
    shots, cursor, unresolved = [], 0.0, []
    for r in rows:
        cue, t, line_id, how = r["cue"], None, None, None
        low = cue.lower()
        quoted = re.findall(r'"([^"]+)"', cue)
        if r["cue"].startswith("Retired"):
            how = "retired"  # IDs never change: removals retire theirs
        elif low == "before the music":
            how = "pre-roll"
        elif not cue or low == "after the last word":
            how = "after the audio"
        elif low.startswith("silence after"):
            t, how = last_word, "end of the outro's last word"
        elif low == "whole hook":
            nxt = next(s for s in sections if s["name"].startswith("Hook") and s["start"] > cursor)
            t, how = nxt["start"], f"start of {nxt['name']}"
        elif low in SPLIT_REPLIES:
            how = "split"  # filled in below, once S40 is known
        elif quoted and ORDINAL.match(low):
            n = ORDINALS[ORDINAL.match(low).group(1)]
            want = norm(quoted[0])
            flat = [(w, ln) for ln in lines for w in ln["words"] if w["start"] >= cursor - 0.01]
            toks = [norm(w["w"]) for w, _ in flat]
            hits = [i for i in range(len(flat) - len(want) + 1)
                    if [tk[0] if tk else "" for tk in toks[i:i + len(want)]] == want]
            if len(hits) >= n:
                w, ln = flat[hits[n - 1]]
                t, line_id, how = w["start"], ln["id"], f"lyric (occurrence {n} after the previous shot)"
        elif quoted:
            ln, t = find_quoted(lines, quoted[0], cursor)
            if ln:
                line_id, how = ln["id"], "lyric"
            else:  # a cue that spans two lines: its first phrase ("You went dark for forty-eight", "Hold up.")
                head = re.split(r"…|(?<=[.?!]) ", quoted[0])[0]
                ln, t = find_quoted(lines, head, cursor)
                if ln:
                    line_id, how = ln["id"], f"lyric (the cue's first phrase, \"{head}\")"
        if how is None:
            unresolved.append(r["id"])
            how = "NOT FOUND in the as-sung lyrics"
        if r["id"] in HOLDS and t is not None:
            how += f" (held: starts {HOLDS[r['id']]['t'] - t:+.2f} s off its cue, config/shot_holds.json)"
            t = HOLDS[r["id"]]["t"]
        if t is not None:
            cursor = t
        shots.append({**r, "t": t, "line": line_id, "how": how})
    # S39b-S39e: split the replies between S39a and the next timed shot into runs of whole beats, in the
    # proportions of config/replies_split.json (equal runs without it)
    idx = [i for i, s in enumerate(shots) if s["how"] == "split"]
    if idx:
        a = shots[idx[0] - 1]["t"]
        b = next(s["t"] for s in shots[idx[-1] + 1:] if s["t"] is not None)
        ka, kb = int(np.searchsorted(beats, a - 0.05)), int(np.searchsorted(beats, b - 0.05))
        ids = [shots[idx[0] - 1]["id"]] + [shots[i]["id"] for i in idx]
        wp = Path("config/replies_split.json")
        wts = json.loads(wp.read_text())["weights"] if wp.exists() else {}
        w = np.array([wts.get(i, 1.0) for i in ids], float)
        edges = ka + np.round(np.cumsum(w)[:-1] / w.sum() * (kb - ka)).astype(int)
        for i, k in zip(idx, edges):
            shots[i]["t"] = float(beats[k])
            shots[i]["how"] = f"replies split by beats in proportion {wts.get(shots[i]['id'], 1.0)} (config/replies_split.json)"
    for s in shots:
        s["t"] = None if s["t"] is None else round(float(s["t"]), 3)
        s["frame"] = fr(s["t"])
        s["downbeat"] = None if s["t"] is None else round(float(dts[np.argmin(np.abs(dts - s["t"]))]), 4)
    timed = [s for s in shots if s["t"] is not None]
    for s, nxt in zip(timed, timed[1:] + [None]):
        s["end"] = round(nxt["t"] if nxt else dur, 3)
        s["dur"] = round(s["end"] - s["t"], 3)
    Path("config/shot_anchors.json").write_text(json.dumps({
        "_doc": "Shot anchors (scripts/timing_map.py): each brief cue resolved to the Suno mix's clock.",
        "shots": {s["id"]: {"t": s["t"], "frame": s["frame"], "line": s["line"]} for s in shots},
        "unresolved": unresolved}, indent=1) + "\n")
    tm = {"fps": FPS, "duration_s": round(dur, 3), "duration_frames": fr(dur), "audio": TRACK, "meter": "4/4",
          "beats": B["beats"], "downbeat_beats": down, "bars": bars, "sections": sections, "lines": lines,
          "shots": shots, "drum_onsets": drums["onsets"], "drum_dropouts": drums["dropouts"],
          "last_word_end": last_word, "first_note": first_note()}
    Path("timing/timing_map.json").write_text(json.dumps(tm) + "\n")

    def clock(t):
        return "" if t is None else f"{int(t // 60)}:{t % 60:05.2f}"

    L = ["# Timing map", "", f"M2. Generated by `scripts/timing_map.py`. {FPS} fps; {dur:.2f} s ({fr(dur)} frames) of "
         f"the Suno mix; the first note at {clock(tm['first_note'])}; 4/4, {len(bars)} bars at a median {np.median([b['bpm'] for b in bars]):.1f} bpm. The last "
         f"word ends at {clock(last_word)}; the piano tail runs to {clock(dur)}.", "",
         "## Sections", "", "| Section | Singer | Stem | Start | End |", "| --- | --- | --- | --- | --- |"]
    L += [f"| {s['name']} | {s['singer']} | {s['stem']} | {clock(s['start'])} | {clock(s['end'])} |" for s in sections]
    L += ["", "## Shots", "", "| ID | Cue | Start | Length (s) | Frame | Line | How |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for s in shots:
        L.append(f"| {s['id']} | {s['cue']} | {clock(s['t'])} | {s.get('dur', '')} | "
                 f"{'' if s['frame'] is None else s['frame']} | {s['line'] or ''} | {s['how']} |")
    irregular = [b for b in bars[:-1] if b["beats"] != 4]
    L += ["", "## Bars that are not 4 beats (for the ear check)", "", "| Bar | Start | Beats |", "| --- | --- | --- |"]
    L += [f"| {b['n']} | {clock(b['start'])} | {b['beats']} |" for b in irregular]
    L += ["", "## Drum drop-outs (the beat stops)", "", ", ".join(f"{clock(a)}–{clock(b)}" for a, b in drums["dropouts"])]
    L += ["", "## Words with low alignment confidence (score < 0.3)", ""]
    L += [", ".join(f"{ln['id']} {w['w']} ({w['score']})" for ln in lines for w in ln["words"] if w["score"] < 0.3)]
    Path("timing/timing_map.md").write_text("\n".join(L) + "\n")
    print(f"{len(bars)} bars, {len(lines)} lines, {len(shots)} shots; unresolved {unresolved}")
    for s in shots:
        print(f"{s['id']:5s} {clock(s['t']):>8s} {str(s.get('dur', '')):>7s} {s['how'][:60]:60s} {s['cue'][:50]}")


if __name__ == "__main__":
    main()
