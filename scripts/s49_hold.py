"""S49, the closing bookend, retimed so the phone's notice can be read on a phone (the human, on the v8 cut: "the
bookends need to zoom in and hold on the phone and schedule more so that they are legible on mobile -- it's okay if
the camera moves to get there faster so that there is more time to read").

The take (takes/fx/S49/S49_overlay.mp4, 192 frames, 8 s) is a photoreal video-to-video push from the table to the
phone; re-shooting its camera would mean a new take. Instead, in the same 8 s:
- 0-4 s: the take's push at twice the speed (every other frame of the approved overlay comp);
- 4-4.75 s: from its last frame, a zoom (eased) to 1.9x on the phone's notice;
- 4.75-8 s: held there.
The held picture is the last frame recomposited at 3x: the take's frame (S49_sign.mp4, without the overlay) scaled up,
and the overlay pass (the phone's screen and the EXPIRED badge) rendered at 3x for that frame
(scenes/blender/sign_matte.py -- S49 --own --subdir overlay_hold3x --objects 'screen.phone_s49.face' 'eat.badge.exp'
--frames 5427 --scale 3), laid on with overlay_add.py's S49 settings scaled 3x (bezel 27 px, halo 90 px, no bloom),
so the notice stays sharp under the zoom. The output is at the cut's size (1920x1080; the take's frame scaled to cover,
as act2_assemble.cover does).

Usage: .venv/bin/python -I scripts/s49_hold.py   ->   takes/fx/S49/S49_hold.mp4
"""
import subprocess
from pathlib import Path

import cv2
import numpy as np

FPS, W, H = 24, 1920, 1080
FX = Path("takes/fx/S49")
OV3 = Path("renders/m5/plates/S49/overlay_hold3x/05427.png")
N, FAST, RAMP = 192, 96, 18  # frames: all of S49; the push at 2x; the zoom
ZOOM, AIM = 1.9, (1790, 1420)  # on the 3x frame (3840x2112): the notice's box on the phone
BEZEL, HALO, SOFT = 27, 90, 0.9


def frames(path):
    w, h = (int(x) for x in subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
         str(path)]).decode().split(","))
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v", "-f", "rawvideo",
                                   "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def window(img, cx, cy, wh):
    """The 16:9 window wh high centred at (cx, cy) (kept inside the frame), scaled to W x H."""
    h, w = img.shape[:2]
    ww = wh * W / H
    cx = min(max(cx, ww / 2), w - ww / 2)
    cy = min(max(cy, wh / 2), h - wh / 2)
    M = np.float32([[W / ww, 0, -(cx - ww / 2) * W / ww], [0, H / wh, -(cy - wh / 2) * H / wh]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_AREA if ww > W else cv2.INTER_LANCZOS4,
                          borderMode=cv2.BORDER_REFLECT)


def held_frame(last):
    """The take's last frame at 3x with the 3x overlay, as overlay_add.py lays S49's (bezel, halo, no bloom)."""
    ov = cv2.cvtColor(cv2.imread(str(OV3), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA).astype(np.float32)
    h, w = ov.shape[:2]
    img = cv2.resize(last, (w, h), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    ov = cv2.GaussianBlur(ov, (0, 0), SOFT)
    alpha, rgb = ov[..., 3:] / 255, ov[..., :3]
    solid = (ov[..., 3] > 127).astype(np.uint8)
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2)  # noqa: E731
    ring = cv2.GaussianBlur(cv2.dilate(solid, k(BEZEL)).astype(np.float32), (0, 0), 3.6)[..., None]
    img = img * (1 - ring) + np.array([10, 10, 12], np.float32) * ring
    inner = cv2.dilate(solid, k(BEZEL)).astype(np.float32)
    outer = cv2.dilate(solid, k(HALO)).astype(np.float32)
    keep = 1 - outer
    sig = HALO * 1.5
    bg = cv2.GaussianBlur(img * keep[..., None], (0, 0), sig) / \
        np.maximum(cv2.GaussianBlur(keep, (0, 0), sig), 1e-3)[..., None]
    dist = cv2.distanceTransform((1 - inner).astype(np.uint8), cv2.DIST_L2, 5)
    wgt = np.clip(1 - dist / max(HALO - BEZEL, 1), 0, 1)
    wgt = (wgt * wgt * (3 - 2 * wgt) * (1 - inner))[..., None]
    img = img * (1 - wgt) + np.minimum(img, bg * 1.1) * wgt
    return np.clip(img * (1 - alpha) + rgb * alpha, 0, 255).astype(np.uint8)


def main():
    comp = frames(FX / "S49_overlay.mp4")
    sign = frames(FX / "S49_sign.mp4")
    assert len(comp) >= N and len(sign) >= N, (len(comp), len(sign))
    hi = held_frame(sign[N - 1])
    h3, w3 = hi.shape[:2]
    out = FX / "S49_hold.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(out)],
                           stdin=subprocess.PIPE)
    th, tw = comp.shape[1:3]
    for i in range(N):
        if i < FAST:  # the push at 2x, scaled to cover the frame
            src = comp[min(round(i * (N - 1) / (FAST - 1)), N - 1)]
            img = window(src, tw / 2, th / 2, min(th, tw * H / W))
        else:
            u = min(1.0, (i - FAST) / RAMP)
            e = u * u * (3 - 2 * u)
            z = 1 + (ZOOM - 1) * e
            wh = min(h3, w3 * H / W) / z
            img = window(hi, w3 / 2 + (AIM[0] - w3 / 2) * e, h3 / 2 + (AIM[1] - h3 / 2) * e, wh)
        enc.stdin.write(np.ascontiguousarray(img).tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"S49: {N} frames -> {out}", flush=True)


if __name__ == "__main__":
    main()
