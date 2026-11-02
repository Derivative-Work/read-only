"""M6 S49: carry an image made for one frame of a shot into another frame's camera, through the Blender depth (the
human: "the ending's wall appears to travel": each close-up anchor was painted from scratch and put the wall and
window somewhere else; reprojected from the opening anchor they stay put in the room, and FLUX only re-details them).

For each pixel of the destination frame: its depth (renders/m5/plates/<shot>/depth_z, from scenes/blender/cams.py)
and camera give a world point, which is projected into the source camera and sampled from the source image. Points the
source camera sees something nearer at (occluded there) or that fall outside it are holes: written to the mask
(white = hole) for the repaint. Sizes: the source image may be any multiple of the plate size; the output is the
source image's size.

Usage: .venv/bin/python -I scripts/reproject.py S49 SRC.png --src-frame 5236 --dst-frame 5427 --out OUT.png
       [--mask MASK.png]
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def cam(rec, scale):
    M = np.array(rec["matrix_world"], np.float64)
    return M, rec["f_px"] * scale, rec["cx"] * scale, rec["cy"] * scale


def depth(plates, f, size):
    z = np.load(plates / "depth_z" / f"{f:05d}.npy").astype(np.float32)
    return cv2.resize(z, size, interpolation=cv2.INTER_NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("src")
    ap.add_argument("--src-frame", type=int, required=True)
    ap.add_argument("--dst-frame", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mask")
    ap.add_argument("--tol", type=float, default=0.04, help="occlusion tolerance, fraction of the depth")
    a = ap.parse_args()
    plates = Path("renders/m5/plates") / a.shot
    cams = json.load(open(plates / "cams.json"))
    pw, ph = cams["size"]
    src = cv2.imread(a.src)
    h, w = src.shape[:2]
    s = w / pw
    Ms, fs, cxs, cys = cam(cams["frames"][str(a.src_frame)], s)
    Md, fd, cxd, cyd = cam(cams["frames"][str(a.dst_frame)], s)
    zd = depth(plates, a.dst_frame, (w, h))
    zs = depth(plates, a.src_frame, (w, h))
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64) + 0.5
    c = np.stack([(xs - cxd) * zd / fd, -(ys - cyd) * zd / fd, -zd, np.ones_like(zd)], -1)  # destination camera space
    P = c @ Md.T  # world
    q = P @ np.linalg.inv(Ms).T  # source camera space
    zq = -q[..., 2]
    u = cxs + fs * q[..., 0] / np.maximum(zq, 1e-6) - 0.5
    v = cys - fs * q[..., 1] / np.maximum(zq, 1e-6) - 0.5
    mx, my = u.astype(np.float32), v.astype(np.float32)
    out = cv2.remap(src, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    seen = cv2.remap(zs, mx, my, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    hole = (zq <= 0) | (mx < 0) | (my < 0) | (mx > w - 1) | (my > h - 1) | (seen < zq * (1 - a.tol))
    cv2.imwrite(a.out, out)
    if a.mask:
        cv2.imwrite(a.mask, (hole * 255).astype(np.uint8))
    print(f"{a.out}: holes {hole.mean():.1%}", flush=True)


if __name__ == "__main__":
    main()
