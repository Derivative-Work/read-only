"""M5 gate: Act 2 as one cut with the master, from the end of Act 1 through S48b (brief M5: "Lip-sync test on S43,
then Act 2 shots (S41–S48)"; S40 and S48b are the edit's, built here).

- Lead-in: the last --lead seconds of S39e from the approved Act 1 frames (renders/m4/act1_v8/frames).
- S40 (F, "Hard freeze; the whole video rewinds at high speed through earlier shots" + "Rewind scan lines"): the M3
  assembler's rewind (scripts/animatic_assemble.py: REWIND_HOLD s of S39e's last frame, then every Act 1 frame back to
  S02 in reverse, sampled evenly), with a VHS rewind look over the rewind: fine scan lines, a tracking band of noise
  rolling up the frame, the colour channels pulled apart, a little horizontal jitter, the picture crushed and
  desaturated. The freeze itself stays clean.
- S41–S48a: the approved M5 takes (TAKES below).
- S48b: the human: "use the record scratches at the end to fade directly to the login screen (skip the fade to black
  first)". On the scratches at the end of the track (overlays/cues.json login_prompt "scratch", 194.65-195.75 s, in
  S48a's last seconds) the grave goes straight to the login prompt (renders/screens/login_prompt). M6 faded it, its
  opacity following the scratch stem's accumulated energy; M7 (the human: "instead of fading from the gravestone, do a
  VHS tracking effect between it and the login screen, still synced to the record scratches") rolls a tracking bar up
  the frame instead, its height the same accumulated energy, the login prompt below it, each stroke tearing and
  rolling the picture (tracking()); the prompt then holds, its cursor blinking, to the cut.
Under S47-S48b, the tape bed (audio/sfx/tape_bed_s47_s49.wav, scripts/tape_hiss.py): hiss easing in as the recorder
is seen, rising under the song's end and the silence; full only from S49 (the bookends).
Act 2 takes are 1280×704; they are scaled to cover 1280×720 (centre crop). The master plays from the lead-in's start
to its end (196.16 s); S48b is silent.

Usage: .venv/bin/python scripts/act2_assemble.py OUT.mp4 [--lead 2.0] [--act1 FRAMES_DIR]
(class Act2: the per-frame picture, for scripts/assemble.py)
"""
import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import json
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import animatic_assemble as aa  # noqa: E402

FPS = aa.FPS
W, H = 1280, 720  # the review cuts' size; scripts/assemble.py sets the final's (set_size); the effects' pixel
                  # measures are at 720 lines, scaled by U
U = 1.0
ACT1 = Path("renders/m4/act1_v8/frames")
TAKES = {"S41": "takes/fx/S41/S41_reveal.mp4", "S42": "takes/fx/S42/S42_glitch.mp4",
         "S43": "takes/fx/S43/S43_glitch.mp4", "S44": "takes/fx/S44/S44_billboard.mp4",
         "S45": "takes/fx/S45/S45_sign.mp4", "S47": "takes/fx/S47/S47_rec.mp4",
         "S48": "takes/fx/S48/S48_overlay.mp4", "S48a": "takes/v/S48a/S48a_joined.mp4"}
LOGIN = Path("renders/screens/login_prompt")
SCRATCH_STEM = "audio/stems/9 Other.wav"
RECAST = Path("config/recast.json")  # M8: the Verse 4 recast's cut list and takes (scripts/recast.py)
TAPE = Path("audio/sfx/tape_bed_s47_s49.wav")  # tape hiss and crackle from S47 (the recorder), easing up to S49 (M6)


def set_size(w, h):
    """M8: the frame size (the final is 1920x1080)."""
    global W, H, U
    W, H, U = w, h, h / 720


def scan_rows():
    """Every third line at 720 lines, at the current height (a 720-line tape's scan lines)."""
    return np.nonzero(np.floor(np.arange(H) / U) % 3 == 0)[0]


def scratch_curve(t0, t1):
    """0..1 through the scratches: the Other stem's energy accumulated over [t0, t1], per frame time."""
    x, sr = sf.read(SCRATCH_STEM, always_2d=True)
    e = x.mean(1)[int(t0 * sr):int(t1 * sr)] ** 2
    c = np.cumsum(e) / e.sum()
    return lambda t: float(np.interp((t - t0) * sr, np.arange(len(c)), c))


def scratch_energy(t0, t1):
    """0..1 per video frame time: the Other stem's energy in the frame around t (over [t0, t1]), over its loudest
    frame's: each scratch stroke's jolt."""
    x, sr = sf.read(SCRATCH_STEM, always_2d=True)
    e = x.mean(1) ** 2
    hop = sr // FPS
    ts = np.arange(t0 - 0.2, t1 + 0.4, 1 / FPS)
    v = np.array([e[int(t * sr) - hop // 2:int(t * sr) + hop // 2].mean() for t in ts])
    v = np.sqrt(v / v.max())
    return lambda t: float(np.interp(t, ts, v, left=0.0, right=0.0))


def tracking(old, new, k, jolt, seed):
    """VHS tracking between two pictures (the human, on the M7 cut: "instead of fading from the gravestone, do a VHS
    tracking effect between it and the login screen, still synced to the record scratches"). k (0..1, the scratches'
    accumulated energy) moves the tracking bar up the frame from below: above it the old recording, below it the new
    one, as when a tape cuts between two recordings; jolt (0..1, the stroke under this frame) tears the lines sideways,
    rolls the picture a few lines, pulls the colour apart and lifts the snow. Both float32 RGB (H, W, 3)."""
    rng = np.random.default_rng(seed)
    amt = max(np.sin(np.pi * min(max(k, 0.0), 1.0)) * 0.6, jolt)  # the disturbance: the stroke, at least the crossing's
    yb = int(round(H * (1.12 - 1.3 * k)))  # the bar's centre: below the frame at k 0, above it at 1
    rows = np.arange(H)[:, None, None]
    img = np.where(rows < yb, old, new)
    # the picture rolls a few lines on each stroke
    img = np.roll(img, int(round(rng.normal(0, 6) * jolt * U)), axis=0)
    # the lines tear sideways: slow wobble in blocks, and a hard skew near the bar (the head switching)
    bl = max(1, round(4 * U))
    blocks = np.repeat(rng.normal(0, 1, H // bl + 1), bl)[:H]
    near = np.exp(-((np.arange(H) - yb) / (55.0 * U)) ** 2)
    off = (blocks * 14 * amt + near * (60 + 50 * jolt) * (1 if seed % 2 else -1) * min(1.0, amt * 2)) * U
    for y in np.nonzero(np.abs(off) >= 1)[0]:
        img[y] = np.roll(img[y], int(off[y]), axis=0)
    # the colour pulls apart and drains
    sh = int(round((2 + 8 * amt) * U))
    img[..., 0] = np.roll(img[..., 0], sh, axis=1)
    img[..., 2] = np.roll(img[..., 2], -sh, axis=1)
    lum = img.mean(2, keepdims=True)
    img = lum + (img - lum) * (1 - 0.5 * amt)
    # the bar: a band of snow with white streaks, and snow through the rest in proportion
    y0, y1 = max(0, yb - round(38 * U)), min(H, yb + round(38 * U))
    if y1 > y0:
        snow = rng.random((y1 - y0, W, 1)) * 255
        img[y0:y1] = img[y0:y1] * 0.25 + snow * 0.75
    streaks = (rng.random((H, 1, 1)) < 0.015 * amt) * (rng.random((H, W, 1)) < 0.35) * 255.0
    img = np.maximum(img, streaks)
    img = img * (1 - 0.18 * amt) + rng.random((H, W, 1)) * 255 * 0.18 * amt
    img[scan_rows()] *= 1 - 0.25 * amt  # the scan lines show
    return img


SWITCH_STYLES = ("tracking", "snow", "roll", "fields")


def change_mask(old, new, gate):
    """Where two identities' frames differ (the face, hair, neck, hands), inside the recast's gate: soft 0..1."""
    d = np.abs(old.astype(np.int16) - new.astype(np.int16)).mean(2).astype(np.float32)
    d = cv2.GaussianBlur(d, (0, 0), 2)
    m = (d > 16).astype(np.uint8)
    h = old.shape[0]
    r = max(3, int(h * 0.02))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), r * 0.7)
    return (np.clip(m * 1.4, 0, 1) * gate)[..., None]


def face_switch(old, new, k, style, gate, seed):
    """M8 (the human: "add VHS and similar era appropriate glitch transitions between the faces (masked to just the
    parts that change)"): one identity becoming the next, as a late-'90s tape would fumble it, only where the two
    frames differ. k runs 0..1 over the transition (the cut at 0.5). Styles, rotated cut by cut:
      tracking  a band of snow sweeps down through the face, the old one above it, the new below, the lines torn
      snow      the face dissolves through tape snow and white dropout streaks
      roll      the face's lines roll and skew sideways (a head switch), the picture swapping mid-roll
      fields    the two faces interlaced line by line (a paused tape's jittering fields), colour pulled apart
    old/new uint8 RGB at the take's size; returns uint8."""
    rng = np.random.default_rng(seed)
    h, w = old.shape[:2]
    o, n = old.astype(np.float32), new.astype(np.float32)
    amt = np.sin(np.pi * k)  # strongest at the cut
    rows = np.arange(h)[:, None, None]
    u = h / 720
    if style == "tracking":
        yb = int(h * (-0.1 + 1.2 * k))
        img = np.where(rows < yb, n, o)
        y0, y1 = max(0, yb - int(30 * u)), min(h, yb + int(30 * u))
        if y1 > y0:
            img[y0:y1] = img[y0:y1] * 0.2 + rng.random((y1 - y0, w, 1)) * 255 * 0.8
        near = np.exp(-((np.arange(h) - yb) / (50.0 * u)) ** 2)
        off = (rng.normal(0, 1, h) * 8 * amt + near * 40 * amt) * u
        for y in np.nonzero(np.abs(off) >= 1)[0]:
            img[y] = np.roll(img[y], int(off[y]), axis=0)
    elif style == "snow":
        mix = np.clip((k - 0.25) / 0.5, 0, 1)
        img = o * (1 - mix) + n * mix
        img = img * (1 - 0.7 * amt) + rng.random((h, w, 1)) * 255 * 0.7 * amt
        streak = (rng.random((h, 1, 1)) < 0.04 * amt) * (rng.random((h, w, 1)) < 0.5) * 255.0
        img = np.maximum(img, streak)
    elif style == "roll":
        img = (o if k < 0.5 else n).copy()
        img = np.roll(img, int(amt * h * 0.12 * (1 if seed % 2 else -1)), axis=0)
        bl = max(2, int(6 * u))
        blocks = np.repeat(rng.normal(0, 1, h // bl + 1), bl)[:h]
        skew = (np.linspace(-1, 1, h) * 30 + blocks * 12) * amt * u
        for y in np.nonzero(np.abs(skew) >= 1)[0]:
            img[y] = np.roll(img[y], int(skew[y]), axis=0)
    else:  # fields
        odd = (np.arange(h) // max(1, int(round(u)))) % 2 == 1
        img = np.where(odd[:, None, None], n, o) if 0.15 < k < 0.85 else (o if k <= 0.15 else n).copy()
        img = np.roll(img, int(rng.integers(-3, 4) * amt * u), axis=0)  # the paused frame jitters
    sh = int(round((2 + 9 * amt) * u))  # chroma pulls apart and bleeds, as on tape
    img[..., 0] = np.roll(img[..., 0], sh, axis=1)
    img[..., 2] = np.roll(img[..., 2], -sh, axis=1)
    lum = img.mean(2, keepdims=True)
    img = lum + (img - lum) * (1 - 0.45 * amt)
    m = change_mask(old, new, gate)
    base = n if k >= 0.5 else o
    return np.clip(base * (1 - m) + img * m, 0, 255).astype(np.uint8)


def frames(path):
    w, h = (int(x) for x in subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
         str(path)]).decode().split(","))
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v", "-f", "rawvideo",
                                   "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def cover(img):
    h, w = img.shape[:2]
    if (h, w) == (H, W):
        return img
    s = max(W / w, H / h)
    r = cv2.resize(img, (round(w * s), round(h * s)), interpolation=cv2.INTER_LANCZOS4)
    y, x = (r.shape[0] - H) // 2, (r.shape[1] - W) // 2
    return r[y:y + H, x:x + W]


def act1(f):
    have = ACT1 / f"f_{f:05d}.png"
    img = cv2.cvtColor(cv2.imread(str(have)), cv2.COLOR_BGR2RGB)
    return img if img.shape[:2] == (H, W) else cover(img)


def rewind_look(img, k, rng):
    """VHS rewind: k is the frame's index into the rewind."""
    out = img.astype(np.float32)
    lum = out.mean(2, keepdims=True)
    out = lum + (out - lum) * 0.6  # desaturated
    out = np.clip((out - 20) * 1.15, 0, 255)  # crushed
    out[..., 0] = np.roll(out[..., 0], round(4 * U), axis=1)  # the channels pulled apart
    out[..., 2] = np.roll(out[..., 2], -round(4 * U), axis=1)
    sl = round(24 * U)
    for y in range(0, H, sl):  # a little line jitter
        out[y:y + sl] = np.roll(out[y:y + sl], int(rng.normal(0, 2.5) * U), axis=1)
    band_y = int(H - (k * 37 * U) % (H + 160 * U) - 80 * U)  # the tracking band rolling up
    y0, y1 = max(0, band_y), min(H, band_y + round(70 * U))
    if y1 > y0:
        noise = rng.random((y1 - y0, W, 1)) * 255
        out[y0:y1] = out[y0:y1] * 0.35 + noise * 0.65
        out[y0:y1] = np.roll(out[y0:y1], round(30 * U), axis=1)
    out[scan_rows()] *= 0.72  # scan lines
    return np.clip(out, 0, 255).astype(np.uint8)


class Act2:
    """Act 2's picture, frame by frame (video frames F(S40 start) .. F(S48b end), and the lead-in before them from
    Act 1): also used by scripts/assemble.py (M7's full edit)."""

    def __init__(self, act1_dir=None):
        global ACT1
        if act1_dir:
            ACT1 = Path(act1_dir)
        SP = self.SP = aa.spans()
        F = aa.F
        self.fa, self.fb = F(SP["S40"][0]), F(SP["S40"][1])
        self.hold = self.fa + int(round(aa.REWIND_HOLD * FPS))
        self.back = list(range(self.fa - 1, F(SP["S02"][0]) - 1, -1))
        self.rng = np.random.default_rng(40)
        self.takes = {sid: frames(p) for sid, p in TAKES.items()}
        # M8 recast (config/recast.json): S41-S43 cut on the beat between seven rappers' takes
        rc = json.load(open(RECAST))
        self.cuts = {sid: [(F(t), i) for t, i in cl] for sid, cl in rc["cuts"].items()}
        self.recast = {(sid, i): frames(rc["takes_a"][sid] if i == "a" else rc["takes"][sid].format(id=i))
                       for sid, cl in rc["cuts"].items() for _, i in cl}
        # the transitions' gate: the recast's repaint ellipses (keyframe pixels) at the take's size, grown so the
        # head can move inside it; the change mask does the rest
        self.switch = rc.get("switch", {"before": 2, "after": 2, "grow": 1.5})
        self.gates = {}
        for sid in rc["cuts"]:
            th, tw = self.recast[(sid, rc["cuts"][sid][0][1])].shape[1:3]
            s = tw / rc["size"][0]
            g = np.zeros((th, tw), np.float32)
            for cx, cy, rx, ry in rc["shots"][sid]["ellipses"]:
                gr = self.switch["grow"]
                cv2.ellipse(g, (int(cx * s), int(cy * s)), (int(rx * s * gr), int(ry * s * gr)), 0, 0, 360, 1.0, -1)
            self.gates[sid] = cv2.GaussianBlur(g, (0, 0), th * 0.02)
        self.cue = json.load(open("overlays/cues.json"))["screens"]["login_prompt"]
        self.first = json.load(open(LOGIN / "range.json"))["first_frame"]
        self.curve = scratch_curve(*self.cue["scratch"])
        self.jolt = scratch_energy(*self.cue["scratch"])

    def frame(self, f):
        SP, F = self.SP, aa.F
        fa, fb, hold, back = self.fa, self.fb, self.hold, self.back
        if f < fa:
            return act1(f)
        if f < fb:
            if f < hold:
                return act1(fa - 1)
            k = f - hold
            return rewind_look(act1(back[int(k * len(back) / (fb - hold))]), k, self.rng)
        if f >= F(self.cue["from"]):
            i = f - self.first
            scr = cover(cv2.cvtColor(cv2.imread(str(LOGIN / f"f_{i + 1:04d}.png")), cv2.COLOR_BGR2RGB)).astype(np.float32)
            k = self.curve(f / FPS - aa.PRE)
            j = self.jolt(f / FPS - aa.PRE)
            if (k < 1 or j > 0.02) and f < F(SP["S48a"][1]):
                tk = self.takes["S48a"]
                grave = cover(tk[min(f - F(SP["S48a"][0]), len(tk) - 1)]).astype(np.float32)
                scr = tracking(grave, scr, k, j, f)
            elif j > 0.02:
                scr = tracking(scr, scr, 1.0, j, f)
            return np.clip(scr, 0, 255).astype(np.uint8)
        sid = next(s for s in TAKES if F(SP[s][0]) <= f < F(SP[s][1]))
        tk = self.takes[sid]
        j = min(f - F(SP[sid][0]), len(tk) - 1)
        if sid in self.cuts:
            cl = self.cuts[sid]
            tk = self.recast[(sid, ([i for fc, i in cl if fc <= f] or [cl[0][1]])[-1])]
            j = min(f - F(SP[sid][0]), len(tk) - 1)
            b, a = self.switch["before"], self.switch["after"]
            for n_cut in range(1, len(cl)):  # a shot's first entry is a camera cut: no transition
                fc = cl[n_cut][0]
                if fc - b <= f < fc + a:
                    old, new = self.recast[(sid, cl[n_cut - 1][1])], self.recast[(sid, cl[n_cut][1])]
                    k = (f - (fc - b) + 0.5) / (a + b)
                    style = SWITCH_STYLES[(sum(len(self.cuts[s]) - 1 for s in list(self.cuts)[:list(self.cuts).index(sid)])
                                           + n_cut - 1) % len(SWITCH_STYLES)]
                    jo, jn = min(j, len(old) - 1), min(j, len(new) - 1)
                    return cover(face_switch(old[jo], new[jn], k, style, self.gates[sid], f))
        return cover(tk[j])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--lead", type=float, default=2.0)
    ap.add_argument("--act1", help="Act 1's frames (default: the approved M4 frames)")
    a = ap.parse_args()
    act2 = Act2(a.act1)
    SP = act2.SP
    F = aa.F
    t0 = SP["S40"][0] - a.lead
    f0, f_end = F(t0), F(SP["S48b"][1])
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-ss", f"{t0:.4f}", "-t", f"{SP['S48a'][1] - t0:.4f}", "-i",
                            aa.MASTER, *(["-i", str(TAPE)] if TAPE.exists() else []), "-filter_complex",
                            "[1:a]apad[a]" if not TAPE.exists() else
                            f"[1:a]apad[m];[2:a]adelay={int(round((SP['S47'][0] - t0) * 1000))}:all=1[h];"
                            "[m][h]amix=inputs=2:duration=first:normalize=0[a]",
                            "-map", "0:v", "-map", "[a]", "-shortest",
                            "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
                            a.out], stdin=subprocess.PIPE)
    for f in range(f0, f_end):
        enc.stdin.write(np.ascontiguousarray(act2.frame(f)).tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"{a.out}: {(f_end - f0) / FPS:.2f} s, frames {f0}..{f_end - 1}", flush=True)


if __name__ == "__main__":
    main()
