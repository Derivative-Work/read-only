"""M5 sign mattes: a shop sign's lettering alone, from the shot's camera, for putting the Act 1 signs back on the
photoreal takes (the human's note on S41: "put the text back for continuity"). Every other object is a holdout, so
whatever stands in front of the sign (the pole in S41) still hides it. Same build as plates.py.

--materials instead keeps every face with a material whose name starts with one of the prefixes (a poster that is a
quad inside an interior's merged mesh, S45's STITCH NIGHT notice), showing its own texture; glass is clear and every
other material renders as a holdout.

Out: renders/m5/plates/<shot>/sign/NNNNN.png (RGBA: --objects, black ink; --materials, the texture's colours;
alpha = coverage).

--own keeps the kept objects' own materials and the look's view transform (an overlay pass: S48's signs, neon,
keypad screens and REC lights in their Act 1 colours, to lay over the take). --objects takes glob patterns.
--subdir names the output folder (default sign). --frames renders only those frames; --scale multiplies the
resolution (S49's hold: the last frame at 3x, so the notice stays sharp under the hold's zoom).

Usage: blender -b --factory-startup --python scenes/blender/sign_matte.py -- S41 [--objects shop0.sign]
       blender -b --factory-startup --python scenes/blender/sign_matte.py -- S45 --materials int.atlas.shops
"""
import argparse
import fnmatch
import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "lib"), str(HERE / "sets"), str(HERE)]
import animatic  # noqa: E402
import gb  # noqa: E402

ROOT = HERE.parents[1]
VCFG = json.loads((ROOT / "config" / "v.json").read_text())


def materials_matte(prefixes):
    """Kept materials emit their image texture (alpha from the texture); every other material is a holdout. Objects
    without a material are holdouts."""
    for m in list(bpy.data.materials):
        if not m.use_nodes:
            m.use_nodes = True
        nt = m.node_tree
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None) or nt.nodes.new("ShaderNodeOutputMaterial")
        for l in list(out.inputs["Surface"].links) + list(out.inputs["Volume"].links):
            nt.links.remove(l)
        if any(m.name.startswith(p) for p in prefixes):
            tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
            em = nt.nodes.new("ShaderNodeEmission")
            nt.links.new(tex.outputs["Color"], em.inputs["Color"])
            nt.links.new(em.outputs[0], out.inputs["Surface"])
        elif m.name.startswith("glass"):  # windows: see through them to the poster behind
            nt.links.new(nt.nodes.new("ShaderNodeBsdfTransparent").outputs[0], out.inputs["Surface"])
        else:
            nt.links.new(nt.nodes.new("ShaderNodeHoldout").outputs[0], out.inputs["Surface"])
    for o in bpy.data.objects:
        if o.type in ("MESH", "CURVE", "FONT") and not any(ms.material for ms in o.material_slots):
            o.is_holdout = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="+")
    ap.add_argument("--objects", nargs="+", default=["shop0.sign"])
    ap.add_argument("--materials", nargs="+")
    ap.add_argument("--own", action="store_true")
    ap.add_argument("--subdir", default="sign")
    ap.add_argument("--out", default=str(ROOT / "renders/m5/plates"))
    ap.add_argument("--frames", nargs="+", type=int)
    ap.add_argument("--scale", type=int, default=1)
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
    sc, SP = animatic.build(tuple(v * a.scale for v in VCFG["size"]), 16, "final", 1)
    sc.render.film_transparent = True
    sc.render.use_motion_blur = False
    if not a.own:
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.view_settings.exposure = 0
    if sc.world and sc.world.node_tree:  # no fog: it would put haze in the alpha
        for l in [l for l in sc.world.node_tree.links if l.to_socket.name == "Volume"]:
            sc.world.node_tree.links.remove(l)
    if a.materials:
        materials_matte(a.materials)
        a.objects = []
    keep = {o.name for o in bpy.data.objects if any(fnmatch.fnmatchcase(o.name, p) for p in a.objects)}
    for o in [] if a.materials else bpy.data.objects:
        if o.name not in keep:
            o.is_holdout = True
            if any(ms.material and ms.material.node_tree and any(n.type.startswith("PRINCIPLED_VOLUME") or n.type == "VOLUME_SCATTER"
                   for n in ms.material.node_tree.nodes) for ms in o.material_slots):
                o.hide_render = True
    for o in [] if a.own else keep:  # flat ink: emission only, so the matte is the lettering's coverage, not its lighting
        ob = bpy.data.objects[o]
        m = bpy.data.materials.new(f"{o}.matte")
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (0, 0, 0, 1)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(em.outputs[0], out.inputs[0])
        ob.data.materials.clear()
        ob.data.materials.append(m)
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    for sid in a.shots:
        t0, t1 = SP[sid]
        out = Path(a.out) / sid / a.subdir
        out.mkdir(parents=True, exist_ok=True)
        for f in (a.frames or range(gb.F(t0), gb.F(t1))):
            sc.frame_set(f)
            sc.render.filepath = str(out / f"{f:05d}.png")
            bpy.ops.render.render(write_still=True)
        print(f"{sid}: sign matte -> {out}", flush=True)


if __name__ == "__main__":
    main()
