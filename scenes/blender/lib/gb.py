"""Grey-box kit for the M3 animatic: flat-coloured primitives, signs, cameras and keyframe helpers.

Grey-box means blocking, not look: shapes and colours only say what a thing is and where it stands, so framing and
timing can be judged (brief, M3 gate: "Approve framing and timing"). Look is set at M4.

Clock: the animatic's timeline runs pre-roll, then the song, then post-roll. Song time t (seconds of the Suno mix;
negative in the pre-roll) is timeline frame F(t) = round((PRE + t) * FPS), with PRE the pre-roll length from
config/bookends.json. Everything is procedural and deterministic: no random calls without a fixed seed.
"""
import json
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
FPS = json.loads((ROOT / "config" / "render_profiles.json").read_text())["fps"]
BOOK = json.loads((ROOT / "config" / "bookends.json").read_text())
PRE = sum(BOOK["preroll"].values())
FONTS = ROOT / "assets" / "fonts"
TM = json.loads((ROOT / "timing" / "timing_map.json").read_text())


def F(t):
    """Timeline frame for song time t."""
    return int(round((PRE + t) * FPS))


# ---------------------------------------------------------------- materials

_MATS = {}


def lin(hexstr):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    h = hexstr.lstrip("#")
    return (ch(int(h[0:2], 16)), ch(int(h[2:4], 16)), ch(int(h[4:6], 16)), 1.0)


def mat(name, hexcol, rough=0.8, emit=0.0, metal=0.0, alpha=1.0):
    """A flat principled material, cached by name. emit > 0 makes it glow in its own colour."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = lin(hexcol)
        b.inputs["Emission Strength"].default_value = emit
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    _MATS[name] = m
    return m


def glow_mat(name, hexcol, strength, owner, prop, base=None):
    """An emissive material whose strength follows owner[prop] (0..1), so a sign or light can be keyed on and off.
    base: the surface colour when unlit (default: the glow colour), e.g. dark glass for a window."""
    m = mat(name, hexcol, emit=strength)
    b = m.node_tree.nodes["Principled BSDF"]
    if base:
        b.inputs["Base Color"].default_value = lin(base)
        b.inputs["Roughness"].default_value = 0.15
    if prop not in owner:
        owner[prop] = 0.0
    d = b.inputs["Emission Strength"].driver_add("default_value").driver
    d.type = "SCRIPTED"
    v = d.variables.new()
    v.name, v.type = "x", "SINGLE_PROP"
    v.targets[0].id_type = "OBJECT"
    v.targets[0].id = owner
    v.targets[0].data_path = f'["{prop}"]'
    d.expression = f"x * {strength}"
    return m


LOOK = json.loads((ROOT / "config" / "look.json").read_text())
TEX = ROOT / "assets" / "textures"


def tex_mat(name, tex_id, rough=None):
    """A CC0 texture (style spec, "Materials"), box-projected in object space at its real-world scale (look.json:
    metres per tile), so no mesh needs UVs: diffuse (optionally tinted), roughness, OpenGL normal."""
    key = f"tex.{name}"
    if key in _MATS:
        return _MATS[key]
    scale_m, tint, rough_k = LOOK["textures"][tex_id]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / scale_m,) * 3
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])

    def img(mapname, noncolor):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(str(TEX / tex_id / f"{mapname}.jpg"), check_existing=True)
        if noncolor:
            n.image.colorspace_settings.name = "Non-Color"
        n.projection, n.projection_blend = "BOX", 0.25
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n
    d = img("diff", False)
    if tint:
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(d.outputs["Color"], mix.inputs["A"])
        mix.inputs["B"].default_value = lin(tint)
        nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    else:
        nt.links.new(d.outputs["Color"], b.inputs["Base Color"])
    r = img("rough", True)
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = rough if rough is not None else rough_k
    nt.links.new(r.outputs["Color"], mul.inputs[0])
    nt.links.new(mul.outputs[0], b.inputs["Roughness"])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(img("nor", True).outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    _MATS[key] = m
    return m


# ---------------------------------------------------------------- objects

def link(o, parent=None):
    bpy.context.scene.collection.objects.link(o)
    if parent:
        o.parent = parent
    return o


def empty(name, loc=(0, 0, 0), parent=None):
    o = link(bpy.data.objects.new(name, None), parent)
    o.location = loc
    return o


def box(name, center, size, m, parent=None, rot_z=0.0):
    """An axis-aligned box: center (x, y, z) and full size (sx, sy, sz), metres."""
    sx, sy, sz = (s / 2 for s in size)
    v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
         (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(m)
    o = link(bpy.data.objects.new(name, me), parent)
    o.location, o.rotation_euler.z = center, rot_z
    return o


def cyl(name, center, r, h, m, parent=None, n=16, axis="Z"):
    ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
    v = [(r * math.cos(a), r * math.sin(a), -h / 2) for a in ang] + [(r * math.cos(a), r * math.sin(a), h / 2) for a in ang]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(m)
    o = link(bpy.data.objects.new(name, me), parent)
    o.location = center
    if axis == "X":
        o.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        o.rotation_euler.x = math.pi / 2
    return o


def sphere(name, center, r, m, parent=None):
    me = bpy.data.meshes.new(name)
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=r)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(m)
    o = link(bpy.data.objects.new(name, me), parent)
    o.location = center
    return o


def plane(name, center, size, m, parent=None, facing="-Y"):
    """A vertical rectangle (width, height) facing the given axis direction (its front faces -Y by default, i.e. a
    sign on a south-row facade facing the street is facing '+Y')."""
    w, h = size[0] / 2, size[1] / 2
    v = {"-Y": [(-w, 0, -h), (w, 0, -h), (w, 0, h), (-w, 0, h)],
         "+Y": [(w, 0, -h), (-w, 0, -h), (-w, 0, h), (w, 0, h)],
         "+X": [(0, -w, -h), (0, w, -h), (0, w, h), (0, -w, h)],
         "-X": [(0, w, -h), (0, -w, -h), (0, -w, h), (0, w, h)],
         "+Z": [(-w, -h, 0), (w, -h, 0), (w, h, 0), (-w, h, 0)]}[facing]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], [(0, 1, 2, 3)])
    me.materials.append(m)
    o = link(bpy.data.objects.new(name, me), parent)
    o.location = center
    return o


FACING_ROT = {"-Y": (math.pi / 2, 0, 0), "+Y": (math.pi / 2, 0, math.pi), "+X": (math.pi / 2, 0, math.pi / 2),
              "-X": (math.pi / 2, 0, -math.pi / 2), "+Z": (0, 0, 0)}  # turns a -Y-facing text upright toward `facing`


def text(name, body, size, m, loc, facing="+Y", mono=False, parent=None, align="CENTER", extrude=0.0):
    """A text object whose face points along `facing` (a south-row sign facing the street is '+Y'); it reads left to
    right for a viewer in front of it."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x, cu.align_y = align, "CENTER"
    font = "JetBrainsMono-SemiBold-flat.ttf" if mono else "Inter-Medium-flat.ttf"
    cu.font = bpy.data.fonts.load(str(FONTS / font), check_existing=True)
    cu.materials.append(m)
    o = link(bpy.data.objects.new(name, cu), parent)
    o.location = loc
    # A text object lies in its XY plane, read from +Z along +X.
    o.rotation_euler = FACING_ROT[facing]
    return o


# ---------------------------------------------------------------- cameras and keys

def look_rot(loc, target):
    return (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def camera(name, lens=35.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start, cd.clip_end = 0.02, 800
    return link(bpy.data.objects.new(name, cd))


def fcurve(owner, path, index=0):
    if owner.animation_data is None:
        owner.animation_data_create()
    act = owner.animation_data.action
    if act is None:
        act = bpy.data.actions.new(f"{owner.name}.act")
        owner.animation_data.action = act
    return act.fcurve_ensure_for_datablock(owner, path, index=index)


def fcurves(owner):
    """The F-curves on owner's action (Blender 5 layered actions: layer 0, strip 0, the owner's slot)."""
    ad = owner.animation_data
    if ad is None or ad.action is None or not ad.action.layers:
        return []
    cb = ad.action.layers[0].strips[0].channelbag(ad.action_slot)
    return list(cb.fcurves) if cb else []


def keys(owner, path, pts, index=0, interp="LINEAR"):
    """Write keys [(frame, value[, interp])] to owner's data path, replacing any there; frames may be floats."""
    fc = fcurve(owner, path, index)
    fc.keyframe_points.clear()
    d = {}
    for p in sorted(pts, key=lambda p: p[0]):
        d[float(p[0])] = p
    pts = [d[k] for k in sorted(d)]
    fc.keyframe_points.add(len(pts))
    co = np.empty(2 * len(pts), np.float32)
    co[0::2] = [p[0] for p in pts]
    co[1::2] = [p[1] for p in pts]
    fc.keyframe_points.foreach_set("co", co)
    lookup = {"BEZIER", "LINEAR", "CONSTANT"}
    for kp, p in zip(fc.keyframe_points, pts):
        ip = p[2] if len(p) > 2 else interp
        assert ip in lookup
        kp.interpolation = ip
        kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
    fc.update()
    return fc


def key_vec(owner, path, pts, interp="LINEAR"):
    """pts [(frame, (x, y, z))]: keys each component."""
    for i in range(3):
        keys(owner, path, [(f, v[i]) for f, v in pts], index=i, interp=interp)


def show_between(o, t0, t1):
    """Visible (render) only for song times t0 <= t < t1; hidden otherwise."""
    pts = [(0, 1.0, "CONSTANT"), (F(t0), 0.0, "CONSTANT"), (F(t1), 1.0, "CONSTANT")]
    keys(o, "hide_render", pts, interp="CONSTANT")
    keys(o, "hide_viewport", pts, interp="CONSTANT")


def hide_between(o, t0, t1):
    """Hidden only for song times t0 <= t < t1."""
    pts = [(0, 0.0, "CONSTANT"), (F(t0), 1.0, "CONSTANT"), (F(t1), 0.0, "CONSTANT")]
    keys(o, "hide_render", pts, interp="CONSTANT")
    keys(o, "hide_viewport", pts, interp="CONSTANT")


def show_from(o, t0):
    show_between(o, t0, 1e5)


def beats_between(t0, t1):
    return [b for b in TM["beats"] if t0 <= b < t1]


def words_between(t0, t1, word=None):
    out = []
    for ln in TM["lines"]:
        for w in ln["words"]:
            if t0 <= w["start"] < t1 and (word is None or word in w["w"].lower()):
                out.append(w)
    return out


def envelope(tag):
    return np.load(ROOT / "timing" / "envelopes" / f"{tag}.npy")


def mouth(jaw, t0, t1, tag="lead", step=2, gain=0.25):
    """Grey-box lip sync: the jaw box's z-scale follows the vocal stem's envelope between song times t0 and t1
    (closed outside). Envelope frames are song frames at FPS; timeline frames are offset by the pre-roll."""
    env = envelope(tag)
    pts = [(F(t0) - 2, 0.05)]
    for k in range(max(0, int(t0 * FPS)), min(len(env), int(t1 * FPS)), step):
        pts.append((F(k / FPS), 0.05 + gain * float(env[k]) * 4))
    pts.append((F(t1) + 2, 0.05))
    keys(jaw, "scale", pts, index=2)
