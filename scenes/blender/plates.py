"""M5 plates: the Act 2 shots (B→V) rendered as guide passes for video-to-video, from the same build as the animatic
(look final). After Folks Like Us's scripts/blender/render_shot.py.

For each shot, its own frames at the V size (no handles: past its span a shot's cast is hidden; the V script pads a
clip by holding the last frame), into <out>/<shot>/:
  beauty/NNNNN.png   the Act 1 look (tonemapped), the keyframe layout and the S41 crossfade's B side
  depth/NNNNN.png    16-bit relative inverse depth: near = white, the shot's "far" and beyond = black
  exr/NNNNN.exr      all passes, scene-linear (multilayer)
  shot.json          frames, size, far

Frame numbers are timeline frames (gb.F: song second t is frame round((PRE + t) * FPS)).

Usage: blender -b --factory-startup --python scenes/blender/plates.py -- S43 [S42 ...] [--res 1280x704]
       [--samples 32] [--first] [--out renders/m5/plates]
--first renders only the first frame (the keyframe layout).
"""
import argparse
import json
import math
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
VCFG = json.loads((ROOT / "config" / "v.json").read_text())


def clip_plan(n, cmax):
    """Clip lengths (each 8k+1, at most cmax) covering n frames, chained with one frame of overlap."""
    if n <= cmax:
        return [max(9, 8 * math.ceil((n - 1) / 8) + 1)]
    plan, covered = [cmax], cmax
    while covered < n:
        rest = n - covered + 1
        plan.append(cmax if rest > cmax else max(9, 8 * math.ceil((rest - 1) / 8) + 1))
        covered += plan[-1] - 1
    return plan


def write_png(path, arr, bits):
    path.parent.mkdir(parents=True, exist_ok=True)
    a = np.ascontiguousarray(arr.astype(np.float32)[:, :, None] if arr.ndim == 2 else arr.astype(np.float32))
    spec = oiio.ImageSpec(a.shape[1], a.shape[0], a.shape[2], oiio.UINT16 if bits == 16 else oiio.UINT8)
    out = oiio.ImageOutput.create(str(path))
    out.open(str(path), spec)
    out.write_image(a)
    out.close()


def depth_png(exr, dest, far):
    """Relative inverse depth (MiDaS-style, what depth-guided video models expect): 1/Z from the shot's far limit (0)
    to the nearest 1% of pixels (1). The sky and anything past far are 0."""
    inp = oiio.ImageInput.open(str(exr))
    z = None
    sub = 0
    while inp.seek_subimage(sub, 0):
        spec = inp.spec()
        names = list(spec.channelnames)
        hit = [i for i, n in enumerate(names) if n.endswith("Depth.Z")]
        if hit:
            z = inp.read_image(sub, 0, 0, spec.nchannels, oiio.FLOAT)[:, :, hit[0]]
            break
        sub += 1
    inp.close()
    if z is None:
        raise KeyError(f"no Depth.Z in {exr}")
    inv = 1.0 / np.maximum(z, 0.05)
    lo, hi = 1.0 / far, np.percentile(inv, 99)
    write_png(dest, np.clip((inv - lo) / max(hi - lo, 1e-6), 0, 1), 16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="+")
    ap.add_argument("--res", default="x".join(map(str, VCFG["size"])))
    ap.add_argument("--samples", type=int, default=32)
    ap.add_argument("--first", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "renders/m5/plates"))
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
    w, h = (int(x) for x in a.res.split("x"))
    sc, SP = animatic.build((w, h), a.samples, "final", 2)
    sc.view_layers[0].use_pass_z = True
    for sid in a.shots:
        t0, t1 = SP[sid]
        s0, s1 = gb.F(t0), gb.F(t1)
        plan = clip_plan(s1 - s0, VCFG["clip_max"])
        frames = [s0] if a.first else list(range(s0, s1))
        far = VCFG.get("far", {}).get(sid, VCFG.get("far_default", 120))
        out = Path(a.out) / sid
        for sub in ("beauty", "exr", "depth"):
            (out / sub).mkdir(parents=True, exist_ok=True)
        for f in frames:
            if (out / "depth" / f"{f:05d}.png").exists():
                continue
            sc.frame_set(f)
            bpy.ops.render.render(write_still=False)
            img = bpy.data.images["Render Result"]
            ims = sc.render.image_settings
            ims.media_type, ims.file_format, ims.color_depth, ims.exr_codec = \
                "MULTI_LAYER_IMAGE", "OPEN_EXR_MULTILAYER", "32", "ZIP"
            exr = out / "exr" / f"{f:05d}.exr"
            img.save_render(str(exr), scene=sc)
            ims.media_type, ims.file_format, ims.color_depth = "IMAGE", "PNG", "8"
            img.save_render(str(out / "beauty" / f"{f:05d}.png"), scene=sc)
            depth_png(exr, out / "depth" / f"{f:05d}.png", far)
        json.dump({"shot": sid, "song_time": [t0, t1], "frames_shot": [s0, s1], "frames_rendered": [frames[0], frames[-1] + 1],
                   "plan": plan, "resolution": [w, h], "samples": a.samples, "far": far,
                   "blender": bpy.app.version_string}, open(out / "shot.json", "w"), indent=1)
        print(f"{sid}: frames {frames[0]}-{frames[-1]} -> {out}", flush=True)


if __name__ == "__main__":
    main()
