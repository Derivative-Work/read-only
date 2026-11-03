"""M3 animatic (brief: "Grey-box Blender set and an animatic of every shot at low resolution, cut to the track"):
the grey-box block (sets/block.py), every shot's camera, stand-ins and gags (shots.py), rendered with Eevee at low
resolution and few samples. Cameras switch on timeline markers, one per shot (brief: "one camera per shot ID").
After Not Yet's scenes/blender/animatic.py.

Timeline frame f shows song time f / FPS - PRE (pre-roll before the track; see lib/gb.py).

Modes:
  --anchors   one still per shot, a third of the way in -> <out>/anchor_<ID>.png, for the contact sheet
  default     every --step'th frame from --from to --to (song seconds) -> <out>/f_<frame>.png

Usage: blender -b --factory-startup --python scenes/blender/animatic.py -- --out DIR [--profile NAME] [--step K]
       [--from S] [--to S] [--anchors] [--only ID ...]
"""
import argparse
import json
import sys
import time
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "lib"), str(HERE / "sets"), str(HERE)]
import block  # noqa: E402
import gb  # noqa: E402
import shots  # noqa: E402

PROFILES = json.loads((HERE.parents[1] / "config" / "render_profiles.json").read_text())


def build(size, samples, look="greybox", mb_steps=1):
    t = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.resolution_percentage = 100
    sc.render.fps = gb.FPS
    sc.eevee.taa_render_samples = samples
    sc.eevee.use_shadows = True
    sc.eevee.use_raytracing = False
    sc.view_settings.view_transform = "AgX"
    sc.render.film_transparent = False
    if look == "final":  # the M4 look (style/style_spec.md, config/look.json)
        block.FINAL = True
        gb.LOOK["_final"] = True  # gb.mouth uses the viseme shapes
        block.look_colours()
        sc.view_settings.look = gb.LOOK["agx_look"]
        sc.view_settings.exposure = gb.LOOK["exposure"]
        sc.render.use_motion_blur = True
        sc.render.motion_blur_shutter = gb.LOOK["motion_blur_shutter"]
        sc.eevee.motion_blur_steps = mb_steps
        sc.eevee.use_raytracing = True
        # 2 GB: at 1 GB, S05 (the Dev's shop, looking out) overflowed it (~4500 / 4096 pages, "Shadow buffer full"),
        # dropping different shadow tiles every frame: the human saw flicker. Frames that fit are unchanged.
        sc.eevee.shadow_pool_size = "2048"
        sc.eevee.volumetric_end = 120
    S = block.build()
    shots.light(S, final=look == "final")
    SP = shots.stage(S)
    if look == "final":  # the in-world screens (overlays/screens.mjs) on their surfaces; the gags' props
        import screens
        screens.build(S, SP)
        import detail
        detail.run(detail.STAGED, S, SP)
    sc.frame_start = 0
    sc.frame_end = gb.F(max(b for _, b in SP.values()))
    print(f"built in {time.time() - t:.1f} s; {len(bpy.data.objects)} objects; {len(shots.CAMS)} cameras; "
          f"frames 0..{sc.frame_end}", flush=True)
    return sc, SP


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--profile", default="animatic", choices=[k for k in PROFILES if not k.startswith("_") and k != "fps"])
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--from", dest="t0", type=float)
    ap.add_argument("--to", dest="t1", type=float)
    ap.add_argument("--anchors", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--look", choices=["greybox", "final"], default="greybox")
    ap.add_argument("--mb-start", action="store_true", help="the shutter opens on the frame (not centred on it): for "
                    "the cut frame, so its blur doesn't sample the pre-roll's daylight a half frame earlier")
    ap.add_argument("--times", nargs="*", type=float, help="stills at these song seconds -> <out>/t_<s>.png")
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
    prof = PROFILES[args.profile]
    sc, SP = build(prof["size"], prof["samples"], args.look, prof.get("motion_blur_steps", 1))
    if args.mb_start:
        sc.render.motion_blur_position = "START"
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sc.render.image_settings.file_format = "PNG"
    t_start = time.time()
    if args.times:
        for t in args.times:
            sc.frame_set(gb.F(t))
            sc.render.filepath = str(out / f"t_{t:07.2f}.png")
            bpy.ops.render.render(write_still=True)
    elif args.anchors:
        for sid, (a, b) in SP.items():
            if args.only and sid not in args.only:
                continue
            sc.frame_set(gb.F(a + (b - a) / 3))
            sc.render.filepath = str(out / f"anchor_{sid}.png")
            bpy.ops.render.render(write_still=True)
    else:
        f0 = 0 if args.t0 is None else gb.F(args.t0)
        f1 = sc.frame_end if args.t1 is None else gb.F(args.t1)
        n = 0
        for f in range(f0, f1 + 1, args.step):
            p = out / f"f_{f:05d}.png"
            if args.resume and p.exists():
                continue
            sc.frame_set(f)
            sc.render.filepath = str(p)
            bpy.ops.render.render(write_still=True)
            n += 1
            if n % 200 == 0:
                print(f"{n} frames, {(time.time() - t_start) / n:.2f} s/frame", flush=True)
    print(f"rendered in {time.time() - t_start:.0f} s", flush=True)
