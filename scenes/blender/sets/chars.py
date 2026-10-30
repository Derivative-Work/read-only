"""Act 1's stylized figures (style/style_spec.md, "Characters"): toy-like, readable by silhouette and colour, no
likenesses. Same calls as block.py's grey-box stand-ins (person, dev, ceo, mod, vip, hypeman), so shots.py stages
either set unchanged. Each figure faces -Y before rot_z, and its root carries "jaw": the mouth object, whose z-scale
the lip sync drives (closed 0.05, open ~1).

Built from ellipsoids and bevelled boxes: a big head, two dot eyes, a dark mouth, rounded limbs.
"""
import math

import bpy

import gb

P = gb.LOOK["palette"]
COL = {
    "skin1": "#c99a76", "skin2": "#8d5f43", "skin3": "#e1b896", "eye": "#0e0e10", "mouth": "#3a1416",
    "jeans": "#2c3a52", "shoe": "#1a1a1c", "hoodie": "#2f8a84", "apron": "#b98a56", "belt": "#3a2a1c",
    "ceohood": "#5d6066", "ermine": "#f4f1ea", "spot": "#101010", "lining": "#9e1b2c", "modbody": "#55606e",
    "vest": P["vest"], "broom": "#b08a57", "bristle": "#8a6a3a", "suit": "#3d434c", "gold": P["gold"],
    "eyeslit": P["screen"], "case": "#1c1c1e", "goodbot": "#e9e1cf", "goodbot2": "#9fc3d6", "screw": "#8a8a8a",
    "lantern": P["community"], "black": "#030303", "cap": "#202020", "plain": "#7d8590",
}


def M(key, **kw):
    return gb.mat(f"chr.{key}", COL[key], **kw)


def ellipsoid(name, center, radii, m, parent):
    o = gb.sphere(name, center, 1.0, m, parent=parent)
    o.scale = radii
    return o


def rbox(name, center, size, m, parent, r=0.04):
    o = gb.box(name, center, size, m, parent=parent)
    bv = o.modifiers.new("round", "BEVEL")
    bv.width, bv.segments, bv.limit_method = r, 3, "NONE"
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def base(name, loc, rot_z, top, legs="jeans", skin="skin1", h=1.0, head_r=0.19):
    """Legs, shoes, torso (colour `top`), arms, hands, head, eyes, mouth. h scales the whole figure."""
    root = gb.empty(name, loc)
    root.rotation_euler.z = rot_z
    for s in (-1, 1):
        ellipsoid(f"{name}.leg{s}", (s * 0.1 * h, 0, 0.36 * h), (0.09 * h, 0.09 * h, 0.36 * h), M(legs), root)
        rbox(f"{name}.shoe{s}", (s * 0.1 * h, -0.05 * h, 0.04 * h), (0.13 * h, 0.24 * h, 0.08 * h), M("shoe"), root, 0.03)
    ellipsoid(f"{name}.torso", (0, 0, 0.95 * h), (0.24 * h, 0.17 * h, 0.3 * h), M(top), root)
    for s in (-1, 1):
        ellipsoid(f"{name}.arm{s}", (s * 0.29 * h, 0, 0.93 * h), (0.075 * h, 0.075 * h, 0.27 * h), M(top), root)
        gb.sphere(f"{name}.hand{s}", (s * 0.3 * h, -0.02 * h, 0.64 * h), 0.06 * h, M(skin), parent=root)
    gb.sphere(f"{name}.head", (0, 0, 1.47 * h), head_r * h, M(skin), parent=root)
    for s in (-1, 1):
        gb.sphere(f"{name}.eye{s}", (s * 0.065 * h, -0.17 * h, 1.52 * h), 0.026 * h, M("eye"), parent=root)
    jaw = rbox(f"{name}.jaw", (0, -0.175 * h, 1.4 * h), (0.09 * h, 0.03 * h, 0.07 * h), M("mouth"), root, 0.012)
    jaw.scale.z = 0.05
    root["jaw"] = jaw.name
    return root


def person(name, loc, body, extra=None, h=1.75, rot_z=0.0, head=None):
    """A plain extra (the eatery's customers, the bouncer)."""
    top = {"stucco2": "plain", "ink": "black"}.get(body, "plain")
    return base(name, loc, rot_z, top, skin="skin2" if hash(name) % 2 else "skin3")


def dev(loc, rot_z=0.0, name="dev"):
    root = base(name, loc, rot_z, "hoodie", skin="skin1")
    rbox(f"{name}.hood", (0, 0.12, 1.28), (0.34, 0.16, 0.16), M("hoodie"), root, 0.06)  # hood down, on the shoulders
    rbox(f"{name}.apron", (0, -0.165, 0.86), (0.36, 0.03, 0.5), M("apron"), root, 0.02)
    rbox(f"{name}.belt", (0, 0, 0.74), (0.5, 0.36, 0.07), M("belt"), root, 0.02)
    for s in (-1, 1):
        rbox(f"{name}.pouch{s}", (s * 0.2, -0.15, 0.68), (0.1, 0.06, 0.12), M("belt"), root, 0.015)
    return root


def ceo(loc, rot_z=0.0, name="ceo"):
    root = base(name, loc, rot_z, "ceohood", skin="skin3")
    rbox(f"{name}.hood", (0, 0.12, 1.28), (0.34, 0.16, 0.16), M("ceohood"), root, 0.06)
    cape = ellipsoid(f"{name}.cape", (0, 0.1, 0.8), (0.36, 0.22, 0.62), M("ermine"), root)
    ellipsoid(f"{name}.lining", (0, 0.06, 0.8), (0.33, 0.2, 0.6), M("lining"), root)
    gb.sphere(f"{name}.collar", (0, 0.02, 1.27), 0.2, M("ermine"), parent=root).scale = (1.25, 1.0, 0.35)
    for k in range(14):  # ermine spots on the back of the cape
        a = -1.1 + 2.2 * (k % 7) / 6
        z = 0.45 + 0.35 * (k // 7) + 0.1 * (k % 2)
        gb.box(f"{name}.spot{k}", (0.36 * math.sin(a), 0.1 + 0.22 * math.cos(a), z), (0.03, 0.03, 0.06),
               M("spot"), parent=root)
    return root


def mod(loc, k, rot_z=0.0, broom=True, name=None):
    name = name or f"mod{k}"
    skin = ("skin1", "skin2", "skin3")[k % 3]
    root = base(name, loc, rot_z, "modbody", skin=skin)
    rbox(f"{name}.vest", (0, 0, 0.98), (0.5, 0.36, 0.46), M("vest"), root, 0.08)
    gb.text(f"{name}.vest.t", "MOD", 0.09, gb.mat("chr.vestink", "#1a1a1a"), (0, -0.185, 1.02), facing="-Y", parent=root)
    if broom:
        gb.cyl(f"{name}.broom", (0.36, -0.08, 0.72), 0.018, 1.36, M("broom"), parent=root)
        rbox(f"{name}.bristle", (0.36, -0.08, 0.07), (0.3, 0.07, 0.12), M("bristle"), root, 0.02)
    return root


def vip(loc, k, rot_z=0.0, name=None):
    name = name or f"vip{k}"
    root = gb.empty(name, loc)
    root.rotation_euler.z = rot_z
    for s in (-1, 1):
        rbox(f"{name}.leg{s}", (s * 0.12, 0, 0.42), (0.14, 0.16, 0.84), M("suit"), root, 0.03)
        rbox(f"{name}.shoe{s}", (s * 0.12, -0.04, 0.04), (0.15, 0.26, 0.08), M("case"), root, 0.02)
    rbox(f"{name}.body", (0, 0, 1.18), (0.62, 0.32, 0.72), M("suit", metal=0.5, rough=0.35), root, 0.06)
    rbox(f"{name}.tie", (0, -0.165, 1.2), (0.06, 0.02, 0.4), M("gold", metal=0.8, rough=0.3), root, 0.01)
    for s in (-1, 1):
        rbox(f"{name}.arm{s}", (s * 0.37, 0, 1.12), (0.11, 0.14, 0.62), M("suit"), root, 0.03)
    rbox(f"{name}.head", (0, 0, 1.75), (0.34, 0.3, 0.32), M("suit", metal=0.5, rough=0.35), root, 0.05)
    gb.box(f"{name}.eye", (0, -0.155, 1.78), (0.24, 0.02, 0.045), gb.mat("chr.eyeslit", COL["eyeslit"], emit=6.0),
           parent=root)
    rbox(f"{name}.badge", (0.15, -0.17, 1.36), (0.13, 0.015, 0.09), M("gold", metal=0.8, rough=0.3), root, 0.01)
    gb.text(f"{name}.badge.t", "VIP", 0.045, gb.mat("chr.badgeink", "#1a1408"), (0.15, -0.18, 1.36), facing="-Y",
            parent=root)
    rbox(f"{name}.case", (0.43, -0.04, 0.6), (0.09, 0.42, 0.3), M("case"), root, 0.02)
    root["jaw"] = f"{name}.eye"  # bots have no mouth; the lip sync never targets them
    return root


def goodbot(name, loc, parent=None):
    """A small homemade robot (S34-S37): round body, screws, mismatched arm, antenna."""
    root = gb.empty(name, loc, parent=parent)
    ellipsoid(f"{name}.body", (0, 0, 0.22), (0.15, 0.12, 0.17), M("goodbot"), root)
    rbox(f"{name}.head", (0, 0, 0.45), (0.2, 0.16, 0.14), M("goodbot2"), root, 0.03)
    for s in (-1, 1):
        gb.sphere(f"{name}.eye{s}", (s * 0.05, -0.08, 0.46), 0.018, M("eye"), parent=root)
        gb.cyl(f"{name}.screw{s}", (s * 0.08, -0.115, 0.26), 0.012, 0.01, M("screw"), parent=root, axis="Y")
    gb.cyl(f"{name}.antenna", (0.04, 0, 0.58), 0.006, 0.12, M("screw"), parent=root)
    gb.cyl(f"{name}.arm", (0.17, -0.02, 0.24), 0.02, 0.18, M("screw"), parent=root)
    return root


def hypeman(loc):
    root = gb.empty("hypeman", loc)
    for s in (-1, 1):
        ellipsoid(f"hypeman.leg{s}", (s * 0.11, 0, 0.4), (0.1, 0.1, 0.4), M("black"), root)
    ellipsoid("hypeman.torso", (0, 0, 1.05), (0.28, 0.19, 0.33), M("black"), root)
    for s in (-1, 1):
        ellipsoid(f"hypeman.arm{s}", (s * 0.33, 0, 1.0), (0.08, 0.08, 0.3), M("black"), root)
    gb.sphere("hypeman.head", (0, 0, 1.55), 0.19, M("black"), parent=root)
    rbox("hypeman.cap", (0, -0.06, 1.68), (0.4, 0.42, 0.08), M("black"), root, 0.03)
    return root
