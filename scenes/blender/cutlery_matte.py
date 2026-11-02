"""M7: the breakfast's cutlery as mattes from S49's camera, old and new, for pasting the new cutlery into the approved
S49 anchors and nothing else (the human, on the M7 cut: S49's cutlery "is also visibly wrong -- regenerate it").

The new fork and spoon (sets/props.py utensil/rest: eat.fork, eat.spoon) are in the build; the old plasticware (flat
slabs, the spoon's bowl a separate disc; props.py before M7) is rebuilt here from its old parameters at the plate, for
its matte only. Every other object is a holdout, so the fish, eggs and plate still hide what they cover.

Out: <out>/{new,old}_NNNNN.png (alpha = coverage), for each --frames.

Usage: blender -b --factory-startup --python scenes/blender/cutlery_matte.py -- --out renders/m7/s49_v8/matte
       [--frames 5236 5332]
"""
import argparse
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / "lib"), str(HERE / "sets"), str(HERE)]
import animatic  # noqa: E402
import gb  # noqa: E402
import mk  # noqa: E402

import json  # noqa: E402

ROOT = HERE.parents[1]
VCFG = json.loads((ROOT / "config" / "v.json").read_text())


def old_ware(m):
    """props.breakfast's plasticware before M7, verbatim, at the plate (its location is the plate's centre on the tray)."""
    k = mk.MK()
    k.box((-0.09, -0.06, 0.03), (0.1, 0.009, 0.0025), m, rot=(0, 0.08, -0.12), bevel=0.001)
    k.box((-0.03, -0.068, 0.034), (0.025, 0.016, 0.002), m, rot=(0, 0.0, -0.12), bevel=0.0006)
    for i in range(4):
        k.box((-0.008, -0.074 + i * 0.0045, 0.035), (0.026, 0.002, 0.0016), m, rot=(0, 0, -0.12))
    k.box((0.125, -0.07, 0.04), (0.09, 0.009, 0.0025), m, rot=(0, -0.12, -0.3), bevel=0.001)
    k.sphere((0.075, -0.055, 0.045), 0.02, m, s=(1.0, 0.7, 0.22), rot=(0, 0, -0.3), u=14, v=6)
    o = gb.link(bpy.data.objects.new("eat.plasticware.old", k.mesh("prop.plasticware.old")))
    o.location = bpy.data.objects["eat.plate"].location
    return o


def flat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0, 0, 0, 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", nargs="+", type=int, default=[5236, 5332])
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
    sc, SP = animatic.build(tuple(VCFG["size"]), 16, "final", 1)
    sc.render.film_transparent = True
    sc.render.use_motion_blur = False
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0
    if sc.world and sc.world.node_tree:
        for l in [l for l in sc.world.node_tree.links if l.to_socket.name == "Volume"]:
            sc.world.node_tree.links.remove(l)
    ink = flat("cutlery.matte")
    old = old_ware(ink)
    new = [bpy.data.objects["eat.fork"], bpy.data.objects["eat.spoon"]]
    for o in new:
        o.data.materials.clear()
        o.data.materials.append(ink)
    for o in bpy.data.objects:
        if o not in new and o is not old:
            o.is_holdout = True
            if any(ms.material and ms.material.node_tree and any(n.type.startswith("PRINCIPLED_VOLUME")
                   for n in ms.material.node_tree.nodes) for ms in o.material_slots):
                o.hide_render = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for tag, show in (("new", new), ("old", [old])):
        for o in new + [old]:
            o.hide_render = o not in show
        for f in a.frames:
            sc.frame_set(f)
            sc.render.filepath = str(out / f"{tag}_{f:05d}.png")
            bpy.ops.render.render(write_still=True)
    print(f"cutlery mattes -> {out}", flush=True)


if __name__ == "__main__":
    main()
