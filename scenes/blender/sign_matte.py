"""M5 sign mattes: a shop sign's lettering alone, from the shot's camera, for putting the Act 1 signs back on the
photoreal takes (the human's note on S41: "put the text back for continuity"). Every other object is a holdout, so
whatever stands in front of the sign (the pole in S41) still hides it. Same build as plates.py.

Out: renders/m5/plates/<shot>/sign/NNNNN.png (RGBA: the ink's colour, alpha = coverage).

Usage: blender -b --factory-startup --python scenes/blender/sign_matte.py -- S41 [--objects shop0.sign]
"""
import argparse
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", nargs="+")
    ap.add_argument("--objects", nargs="+", default=["shop0.sign"])
    ap.add_argument("--out", default=str(ROOT / "renders/m5/plates"))
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
    sc, SP = animatic.build(tuple(VCFG["size"]), 16, "final", 1)
    sc.render.film_transparent = True
    sc.render.use_motion_blur = False
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0
    if sc.world and sc.world.node_tree:  # no fog: it would put haze in the alpha
        for l in [l for l in sc.world.node_tree.links if l.to_socket.name == "Volume"]:
            sc.world.node_tree.links.remove(l)
    keep = set(a.objects)
    for o in bpy.data.objects:
        if o.name not in keep:
            o.is_holdout = True
            if any(ms.material and ms.material.node_tree and any(n.type.startswith("PRINCIPLED_VOLUME") or n.type == "VOLUME_SCATTER"
                   for n in ms.material.node_tree.nodes) for ms in o.material_slots):
                o.hide_render = True
    for o in keep:  # flat ink: emission only, so the matte is the lettering's coverage, not its lighting
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
        out = Path(a.out) / sid / "sign"
        out.mkdir(parents=True, exist_ok=True)
        for f in range(gb.F(t0), gb.F(t1)):
            sc.frame_set(f)
            sc.render.filepath = str(out / f"{f:05d}.png")
            bpy.ops.render.render(write_still=True)
        print(f"{sid}: sign matte -> {out}", flush=True)


if __name__ == "__main__":
    main()
