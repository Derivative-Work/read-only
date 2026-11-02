"""A shot's camera per frame, for reprojecting images between its frames (scripts/reproject.py): the world matrix, the
focal length and sensor in pixels, and the shift, from the same build as the plates, into
renders/m5/plates/<shot>/cams.json. Also each frame's depth (the EXR's Depth.Z, planar, metres) as depth_z/NNNNN.npy,
float16.

Usage: blender -b --factory-startup --python scenes/blender/cams.py -- S49 [--frames 5236,5332,5427]
"""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
import OpenImageIO as oiio

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "lib"), str(HERE / "sets"), str(HERE)]
import animatic  # noqa: E402
import gb  # noqa: E402

ROOT = HERE.parents[1]


def depth_z(exr):
    inp = oiio.ImageInput.open(str(exr))
    sub = 0
    while inp.seek_subimage(sub, 0):
        spec = inp.spec()
        hit = [i for i, n in enumerate(spec.channelnames) if n.endswith("Depth.Z")]
        if hit:
            z = inp.read_image(sub, 0, 0, spec.nchannels, oiio.FLOAT)[:, :, hit[0]]
            inp.close()
            return z
        sub += 1
    raise KeyError(exr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("--frames", default="")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
    out = ROOT / "renders/m5/plates" / a.shot
    meta = json.load(open(out / "shot.json"))
    w, h = meta["resolution"]
    sc, SP = animatic.build((w, h), 1, "final", 1)
    s0, s1 = meta["frames_shot"]
    rec = {}
    for f in range(s0, s1):
        sc.frame_set(f)
        # the camera bound by the timeline marker at or before f (one camera per shot)
        cam = max((m for m in sc.timeline_markers if m.frame <= f and m.camera), key=lambda m: m.frame).camera
        d = cam.data
        sensor = d.sensor_width if d.sensor_fit in ("AUTO", "HORIZONTAL") else d.sensor_height * w / h
        fpx = d.lens / sensor * w
        rec[f] = {"matrix_world": [list(r) for r in cam.matrix_world], "f_px": fpx,
                  "cx": w / 2 - d.shift_x * w, "cy": h / 2 + d.shift_y * w}
    json.dump({"size": [w, h], "frames": rec}, open(out / "cams.json", "w"))
    (out / "depth_z").mkdir(exist_ok=True)
    for f in ([int(x) for x in a.frames.split(",")] if a.frames else range(s0, s1)):
        np.save(out / "depth_z" / f"{f:05d}.npy", depth_z(out / "exr" / f"{f:05d}.exr").astype(np.float16))
    print("cams ->", out / "cams.json", flush=True)


if __name__ == "__main__":
    main()
