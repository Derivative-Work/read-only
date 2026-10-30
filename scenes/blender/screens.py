"""The in-world screens on the set (the final look): the image sequences overlays/screens.mjs draws are mapped onto
their surfaces, in place of the grey-box's static text.
  lobby_blackmail  the lobby screen, S10 (BLACKMAIL flashing on the eighth notes)
  lobby_traffic    the lobby screen, S20 (the traffic chart dipping and bouncing back)
  pawn_led         the pawn shop's LED sign (48:00:00 counting down in S16, holding its last value after)
  ticker           the LED band's street face, looping from S30 on (it lights with the band's own control)

Each sequence's range.json gives the timeline frame of its first image; frames before it show the first image and
frames after it the last (or loop).
"""
import json

import bpy

import gb

SCREENS = gb.ROOT / "renders" / "screens"


def seq_mat(name, strength, owner=None, prop=None):
    d = SCREENS / name
    r = json.loads((d / "range.json").read_text())
    m = bpy.data.materials.new(f"screen.{name}")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.load(str(d / "f_0001.png"), check_existing=True)
    img.source = "SEQUENCE"
    t.image = img
    iu = t.image_user
    iu.frame_duration, iu.frame_start, iu.frame_offset = r["count"], r["first_frame"], 0
    iu.use_auto_refresh, iu.use_cyclic = True, r["loop"]
    b.inputs["Base Color"].default_value = (0, 0, 0, 1)
    b.inputs["Roughness"].default_value = 0.25
    nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength
    if owner is not None:
        dr = b.inputs["Emission Strength"].driver_add("default_value").driver
        dr.type = "SCRIPTED"
        v = dr.variables.new()
        v.name, v.type = "x", "SINGLE_PROP"
        v.targets[0].id_type, v.targets[0].id, v.targets[0].data_path = "OBJECT", owner, f'["{prop}"]'
        dr.expression = f"x * {strength}"
    return m


def surface(name, center, size, m, facing):
    o = gb.plane(f"screen.{name}.face", center, size, m, facing=facing)
    uv = o.data.uv_layers.new()
    for loop, c in zip(o.data.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[loop.index].uv = c
    return o


def build(S, SP):
    import block as B
    x0, x1 = B.TOWER_X
    y0, y1 = B.TOWER_Y
    for name, sid in (("lobby_blackmail", "S10"), ("lobby_traffic", "S20")):
        o = surface(name, (B.LOBBY_DOOR_X, y1 - 6.27, 3.6), (7.8, 3.3), seq_mat(name, 3.0), "-Y")
        gb.show_between(o, *SP[sid])
        txt = bpy.data.objects.get(f"screen.{sid}")  # the grey-box's static text, replaced
        if txt:
            bpy.data.objects.remove(txt)
    surface("pawn_led", (-3.0, B.FRONT + 0.37, 4.6), (2.5, 0.55), seq_mat("pawn_led", 6.0), "+Y")
    bpy.data.objects.remove(bpy.data.objects["pawn.led.txt"])
    surface("ticker", ((x0 + x1) / 2, y0 - 0.21, 13.6), (x1 - x0 + 0.4, 1.2),
            seq_mat("ticker", 8.0, S["ticker"], "on"), "-Y")
