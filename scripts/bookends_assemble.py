"""M6 gate: the bookends as one review cut.

Opener (pre-roll, no music; brief S01a-S01e):
  S01a  the rendered push into the eatery, with the caption "San Francisco, 2018" (brief's gag column)
  S01b  POV through the phone's camera: a generic camera UI over the render (focus box, shutter button, a toy thumb
        that taps it), a white flash, then the human's real plate photo in a plain photo viewer, "Just now": the only
        real image in the video (assets/real/plate.jpg)
  S01c  the drift across the table to the badge and the schedule (rendered)
  S01d  the phone in hand: its screen is in the render (overlays/screens phone_s01d)
  S01e  the match cut to S02 on the first piano chord: the first --tail s of the approved Act 1 frames, with the music
Under the opener: the diner ambience (audio/sfx/diner_ambience.wav), out by the cut.

Closing (post-roll): S48b's last second (Act 2), S49 (the photoreal take with its overlay), S50 (the end card).

Usage: .venv/bin/python -I scripts/bookends_assemble.py OUT.mp4 --preroll renders/m6/preroll_v1 [--s49 take.mp4]
       [--s50 renders/screens/end_card] [--tail 3.0]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import animatic_assemble as aa  # noqa: E402

FPS = aa.FPS
W, H = 1280, 720
FONT = "assets/fonts/Inter-Medium-flat.ttf"
PLATE = "assets/real/plate.jpg"
ACT1 = Path("renders/m4/act1_v8/frames")
AMBIENCE = Path("audio/sfx/diner_ambience.wav")
S01B = {"focus": 0.35, "thumb_in": 1.0, "tap": 1.7, "flash": 0.12, "review": 1.85}  # seconds into S01b


def font(px):
    return ImageFont.truetype(FONT, px)


_PHOTO = None


def photo_review():
    """The plain photo viewer: the plate photo fitted to the frame's height, black around it, "Just now"."""
    global _PHOTO
    if _PHOTO is None:
        im = Image.open(PLATE).convert("RGB")
        im.thumbnail((W, H), Image.LANCZOS)
        base = Image.new("RGB", (W, H), (0, 0, 0))
        base.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
        d = ImageDraw.Draw(base)
        d.text((W / 2, 34), "Just now", font=font(24), fill=(240, 240, 240), anchor="mm")
        _PHOTO = np.asarray(base)
    return _PHOTO


def thumb(d, x, y, press):
    """A toy thumb (Act 1's figures' style): a rounded skin-tone capsule from the lower right, a pale nail."""
    skin, shade, nail = (196, 140, 104), (168, 114, 84), (232, 196, 178)
    d.rounded_rectangle([x - 40, y - 30 + press, x + 60, y + 400], 48, fill=shade)
    d.rounded_rectangle([x - 48, y - 40 + press, x + 52, y + 400], 50, fill=skin)
    d.rounded_rectangle([x - 26, y - 26 + press, x + 26, y + 26 + press], 20, fill=nail)


def camera_ui(frame, t):
    """t: seconds into S01b."""
    im = Image.fromarray(frame).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in (1, 2):  # thirds grid
        d.line([(W * k / 3, 0), (W * k / 3, H)], fill=(255, 255, 255, 60), width=1)
        d.line([(0, H * k / 3), (W, H * k / 3)], fill=(255, 255, 255, 60), width=1)
    d.rectangle([0, 0, W, 56], fill=(0, 0, 0, 120))  # top bar: flash, a dot menu
    d.polygon([(42, 12), (30, 31), (39, 31), (34, 45), (48, 24), (39, 24)], fill=(255, 255, 255, 230))  # the flash
    for k in range(3):
        d.ellipse([W - 52 + k * 10, 25, W - 46 + k * 10, 31], fill=(255, 255, 255, 230))
    d.rectangle([0, H - 150, W, H], fill=(0, 0, 0, 130))  # bottom bar: last photo, shutter, switch
    d.rounded_rectangle([90, H - 106, 150, H - 46], 10, fill=(70, 70, 72, 255), outline=(255, 255, 255, 200), width=2)
    d.text((W / 2, H - 132), "Photo", font=font(20), fill=(255, 214, 90, 255), anchor="mm")
    press = 6 if S01B["tap"] - 0.08 <= t <= S01B["tap"] + 0.1 else 0
    cx, cy, r = W / 2, H - 70, 40
    d.ellipse([cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8], outline=(255, 255, 255, 255), width=5)
    d.ellipse([cx - r + press, cy - r + press, cx + r - press, cy + r - press], fill=(255, 255, 255, 255))
    d.ellipse([W - 150, H - 100, W - 98, H - 48], outline=(255, 255, 255, 200), width=3)
    if t >= S01B["focus"]:  # the focus box settling on the plate
        k = min(1.0, (t - S01B["focus"]) / 0.3)
        s = 120 - 30 * k
        fx, fy = W * 0.52, H * 0.42
        for (ax, ay) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            x0, y0 = fx + ax * s, fy + ay * s
            d.line([(x0, y0), (x0 - ax * 26, y0)], fill=(255, 214, 90, 255), width=3)
            d.line([(x0, y0), (x0, y0 - ay * 26)], fill=(255, 214, 90, 255), width=3)
    if t >= S01B["thumb_in"]:  # the thumb: in from the lower right, onto the shutter, back out
        a = min(1.0, (t - S01B["thumb_in"]) / (S01B["tap"] - S01B["thumb_in"]))
        a = a * a * (3 - 2 * a)
        out = max(0.0, (t - S01B["tap"] - 0.12) / 0.25)
        tx = cx + (1 - a) * 420 + out * 380
        ty = cy + (1 - a) * 260 + out * 240 - 8
        thumb(d, tx, ty, press)
    im = Image.alpha_composite(im, ov).convert("RGB")
    return np.asarray(im)


def s01b(frame, t):
    if t < S01B["tap"]:
        return camera_ui(frame, t)
    if t < S01B["tap"] + S01B["flash"]:  # the shutter flash
        k = 1 - (t - S01B["tap"]) / S01B["flash"]
        return np.clip(camera_ui(frame, t).astype(np.float32) * (1 - k) + 255 * k, 0, 255).astype(np.uint8)
    if t < S01B["review"]:
        k = (t - S01B["tap"] - S01B["flash"]) / (S01B["review"] - S01B["tap"] - S01B["flash"])
        return (photo_review().astype(np.float32) * k + 255 * (1 - k) * 0.3).astype(np.uint8)
    return photo_review()


def caption(frame, t, t0, t1, text="San Francisco, 2018"):
    """A plain caption, lower left, fading in and out."""
    a = min(1.0, (t - t0) / 0.6, (t1 - t) / 0.6)
    if a <= 0:
        return frame
    im = Image.fromarray(frame).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((64, H - 80), text, font=font(34), fill=(0, 0, 0, int(160 * a)))
    ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(3)))
    ImageDraw.Draw(ov).text((62, H - 82), text, font=font(34), fill=(255, 255, 255, int(255 * a)))
    return np.asarray(Image.alpha_composite(im, ov).convert("RGB"))


def grade(img):
    """The opener's render, a touch more contrast (the human, on v4: "still a little washed out in the beginning"): the
    black point down 6%, a gentle S round the middle, saturation +8%. Not on the real photo or the camera UI."""
    x = img.astype(np.float32) / 255
    x = np.clip((x - 0.06) / 0.94, 0, 1)
    x = x + 0.2 * (x - 0.5) * (1 - np.abs(2 * x - 1))
    lum = x.mean(2, keepdims=True)
    x = lum + (x - lum) * 1.08
    return (np.clip(x, 0, 1) * 255).astype(np.uint8)


def frames_of(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v", "-f", "rawvideo",
                                   "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--preroll", required=True)
    ap.add_argument("--s49")
    ap.add_argument("--s50")
    ap.add_argument("--tail", type=float, default=3.0)
    a = ap.parse_args()
    SP = aa.spans()
    F = aa.F
    pre = Path(a.preroll)
    tmp = Path(a.out).with_suffix(".parts")
    tmp.mkdir(parents=True, exist_ok=True)
    # the opener + the cut into S02, with ambience under the opener and the master from the cut
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                            str(tmp / "opener.mp4")], stdin=subprocess.PIPE)
    f_cut = F(SP["S02"][0])
    for f in range(0, f_cut + int(a.tail * FPS)):
        if f < f_cut:
            img = grade(cv2.cvtColor(cv2.imread(str(pre / f"f_{f:05d}.png")), cv2.COLOR_BGR2RGB))
        else:
            img = cv2.cvtColor(cv2.imread(str(ACT1 / f"f_{f:05d}.png")), cv2.COLOR_BGR2RGB)
        t = f / FPS - aa.PRE
        if SP["S01a"][0] <= t < SP["S01a"][1]:
            img = caption(img, t, SP["S01a"][0] + 0.8, SP["S01a"][1] - 0.3)
        elif SP["S01b"][0] <= t < SP["S01b"][1]:
            img = s01b(img, t - SP["S01b"][0])
        enc.stdin.write(np.ascontiguousarray(img).tobytes())
    enc.stdin.close()
    enc.wait()
    cut = f_cut / FPS
    amb = (f"[1:a]atrim=0:{cut + 0.4},afade=t=in:d=1.0,afade=t=out:st={cut - 0.1}:d=0.5,volume=0.8[amb];"
           if AMBIENCE.exists() else f"anullsrc=r=48000:cl=stereo,atrim=0:{cut + 0.4}[amb];")
    inputs = ["-i", str(tmp / "opener.mp4")] + (["-i", str(AMBIENCE)] if AMBIENCE.exists() else [])
    mi = len(inputs) // 2
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-i", aa.MASTER, "-filter_complex",
                    amb + f"[{mi}:a]adelay={int(aa.PRE * 1000)}:all=1,atrim=0:{cut + a.tail}[mus];"
                    "[amb][mus]amix=inputs=2:duration=longest:normalize=0[a]",
                    "-map", "0:v", "-map", "[a]", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                    str(tmp / "opener_a.mp4")], check=True)
    parts = [tmp / "opener_a.mp4"]
    if a.s49:  # the closing: S49 (picture), then S50; silent (the song has ended)
        clo = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                                "-shortest", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac",
                                str(tmp / "closing.mp4")], stdin=subprocess.PIPE)
        for img in frames_of(a.s49):
            clo.stdin.write(np.ascontiguousarray(img).tobytes())
        if a.s50:
            d = Path(a.s50)
            for p in sorted(d.glob("f_*.png")):
                clo.stdin.write(np.ascontiguousarray(cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB)).tobytes())
        clo.stdin.close()
        clo.wait()
        parts.append(tmp / "closing.mp4")
    (tmp / "list.txt").write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-c:v",
                    "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", a.out], check=True)
    print(a.out, flush=True)


if __name__ == "__main__":
    main()
