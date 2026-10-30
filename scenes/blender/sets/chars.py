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
    "jeans": "#2c3a52", "shoe": "#1a1a1c", "hoodie": "#2f8a84", "apron": "#8f6b45", "belt": "#3a2a1c",
    "ceohood": "#5d6066", "ermine": "#f4f1ea", "spot": "#101010", "lining": "#9e1b2c", "modbody": "#55606e",
    "vest": P["vest"], "broom": "#b08a57", "bristle": "#8a6a3a", "suit": "#3d434c", "gold": P["gold"],
    "eyeslit": P["screen"], "case": "#1c1c1e", "goodbot": "#e9e1cf", "goodbot2": "#9fc3d6", "screw": "#8a8a8a",
    "lantern": P["community"], "black": "#030303", "cap": "#202020", "plain": "#7d8590",
    "sole": "#e8e6e0", "white": "#f4f4f2", "mannequin": "#e7e2d8", "reflect": "#d9dde2", "lens": "#0a0a0c",
    "hair0": "#1e1611", "hair1": "#3b2a1e", "hair2": "#6b4a2e", "hair3": "#9a7a52", "hair4": "#2b2b2e",
    "knit0": "#3a4a6b", "knit1": "#6b3a3a", "knit2": "#2f5d4e", "seam": "#23272d", "drawstring": "#e9e6df",
}
HAIRS = ("crop", "bun", "beanie", "curly", "cap", "bald")


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


def hair(name, root, style, col, h=1.0, r=0.19):
    """A hairstyle (or hat) over the head: kept above the eyes so the face reads."""
    hc = M(col)
    z = 1.47 * h
    if style == "bald":
        return
    if style in ("crop", "bun", "cap", "beanie"):
        cap = hc if style != "beanie" else M(col)
        ellipsoid(f"{name}.hair", (0, 0.03 * h, z + 0.11 * h), (r * 1.04 * h, r * 1.03 * h, r * 0.8 * h), cap, root)
    if style == "bun":
        gb.sphere(f"{name}.bun", (0, 0.15 * h, z + 0.17 * h), 0.07 * h, hc, parent=root)
    if style == "beanie":
        rbox(f"{name}.beanie.band", (0, 0.02 * h, z + 0.09 * h), (0.4 * h, 0.4 * h, 0.06 * h), hc, root, 0.025)
    if style == "cap":
        rbox(f"{name}.cap.brim", (0, -0.2 * h, z + 0.1 * h), (0.24 * h, 0.14 * h, 0.018 * h), hc, root, 0.008)
    if style == "curly":
        for k in range(16):
            a = 2 * math.pi * k / 11
            ring = k // 11
            rr = (0.15 if ring == 0 else 0.07) * h
            gb.sphere(f"{name}.curl{k}", (rr * math.cos(a), 0.04 * h + rr * math.sin(a) * 0.9,
                                          z + (0.13 if ring == 0 else 0.19) * h), 0.075 * h, hc, parent=root)


def base(name, loc, rot_z, top, legs="jeans", skin="skin1", h=1.0, head_r=0.19, style="crop", hair_col="hair0",
         face=True):
    """Legs, shoes, torso (colour `top`), arms, hands, head, eyes, mouth. h scales the whole figure. The detail pass
    adds a neck, ears, a nose, brows, catchlights, hair (`style`), and white soles; face=False is a mannequin's."""
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
    gb.cyl(f"{name}.neck", (0, 0, 1.26 * h), 0.07 * h, 0.1 * h, M(skin), parent=root)
    for s in (-1, 1):
        rbox(f"{name}.sole{s}", (s * 0.1 * h, -0.05 * h, 0.012 * h), (0.14 * h, 0.25 * h, 0.025 * h), M("sole"), root, 0.01)
    if not face:  # a mannequin: smooth and blank
        for part in ("eye-1", "eye1", "jaw"):
            o = bpy.data.objects[f"{name}.{part}"]
            o.hide_render = o.hide_viewport = True
        return root
    for s in (-1, 1):
        ellipsoid(f"{name}.ear{s}", (s * head_r * 0.98 * h, 0.01 * h, 1.47 * h), (0.025 * h, 0.035 * h, 0.05 * h), M(skin),
                  root)
        rbox(f"{name}.brow{s}", (s * 0.068 * h, -0.168 * h, 1.575 * h), (0.065 * h, 0.016 * h, 0.016 * h), M(hair_col),
             root, 0.006).rotation_euler.y = s * 0.12
        gb.sphere(f"{name}.glint{s}", (s * 0.065 * h + 0.008 * h, -0.192 * h, 1.53 * h), 0.007 * h,
                  gb.mat("chr.glint", "#ffffff", emit=2.0), parent=root)
    ellipsoid(f"{name}.nose", (0, -0.19 * h, 1.465 * h), (0.025 * h, 0.03 * h, 0.03 * h), M(skin), root)
    hair(name, root, style, hair_col, h, head_r)
    return root


def person(name, loc, body, extra=None, h=1.75, rot_z=0.0, head=None):
    """A plain extra (the eatery's customers, the bouncer)."""
    top = {"stucco2": "plain", "ink": "black"}.get(body, "plain")
    k = sum(map(ord, name))  # seeded by name (Python's hash() of a str changes run to run)
    if name == "bouncer":  # black clothes, shaved head, dark glasses
        root = base(name, loc, rot_z, "black", legs="black", skin="skin2", style="bald")
        rbox(f"{name}.shades", (0, -0.185, 1.53), (0.2, 0.02, 0.05), M("lens"), root, 0.01)
        return root
    return base(name, loc, rot_z, top, skin=("skin1", "skin2", "skin3")[k % 3], style=HAIRS[k % 5],
                hair_col=f"hair{k % 5}" if HAIRS[k % 5] != "beanie" else f"knit{k % 3}")


def dev(loc, rot_z=0.0, name="dev"):
    root = base(name, loc, rot_z, "hoodie", skin="skin1", style="curly", hair_col="hair0")
    for s in (-1, 1):  # the hoodie's drawstrings
        gb.cyl(f"{name}.string{s}", (s * 0.045, -0.17, 1.17), 0.008, 0.16, M("drawstring"), parent=root)
    rbox(f"{name}.hood", (0, 0.12, 1.28), (0.34, 0.16, 0.16), M("hoodie"), root, 0.06)  # hood down, on the shoulders
    ellipsoid(f"{name}.apron", (0, -0.03, 0.88), (0.235, 0.15, 0.3), M("apron"), root)  # canvas, wrapped round
    rbox(f"{name}.apronpocket", (0, -0.178, 0.8), (0.22, 0.012, 0.11), M("belt"), root, 0.01)
    for s in (-1, 1):  # the neck strap
        rbox(f"{name}.apronstrap{s}", (s * 0.08, -0.13, 1.17), (0.03, 0.02, 0.16), M("belt"), root, 0.006)
    rbox(f"{name}.belt", (0, 0, 0.74), (0.5, 0.36, 0.07), M("belt"), root, 0.02)
    for s in (-1, 1):
        rbox(f"{name}.pouch{s}", (s * 0.2, -0.15, 0.68), (0.1, 0.06, 0.12), M("belt"), root, 0.015)
    return root


def ceo(loc, rot_z=0.0, name="ceo"):
    root = base(name, loc, rot_z, "ceohood", skin="skin3", style="crop", hair_col="hair3")
    if name == "ceo10":  # on the phone (S10): right hand up at the ear, holding it
        hand, arm = bpy.data.objects[f"{name}.hand1"], bpy.data.objects[f"{name}.arm1"]
        hand.location = (0.22, -0.04, 1.42)
        arm.location, arm.rotation_euler, arm.scale = (0.3, -0.02, 1.2), (0, -0.35, 0), (0.075, 0.075, 0.2)
        rbox(f"{name}.phone", (0.2, -0.06, 1.47), (0.02, 0.075, 0.15), M("case"), root, 0.006)
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
    blank = name.startswith("mannequin")  # S21: identical, faceless mannequins in MOD vests
    style = HAIRS[k % 6]
    root = base(name, loc, rot_z, "mannequin" if blank else "modbody", legs="mannequin" if blank else "jeans",
                skin="mannequin" if blank else skin, style=style,
                hair_col=f"knit{k % 3}" if style == "beanie" else f"hair{k % 5}", face=not blank)
    rbox(f"{name}.vest", (0, 0, 0.98), (0.5, 0.36, 0.46), M("vest"), root, 0.08)
    for z in (0.86, 1.06):  # reflective tape
        rbox(f"{name}.tape{z}", (0, 0, z), (0.51, 0.37, 0.035), M("reflect", rough=0.3), root, 0.015)
    gb.text(f"{name}.vest.t", "MOD", 0.09, gb.mat("chr.vestink", "#1a1a1a"), (0, -0.185, 1.155), facing="-Y", parent=root)
    if broom:
        import kit
        kit.place(f"{name}.broom", "wooden_broom", (0.36, -0.08, 0.0), rot_z=math.pi / 2, scale=0.93, parent=root)
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
    for s in (-1, 1):
        rbox(f"{name}.pad{s}", (s * 0.3, 0, 1.53), (0.2, 0.34, 0.06), M("suit", metal=0.5, rough=0.35), root, 0.025)
        gb.cyl(f"{name}.bolt{s}", (s * 0.175, 0, 1.76), 0.035, 0.03, M("gold", metal=0.8, rough=0.3), parent=root, axis="X")
        rbox(f"{name}.lapel{s}", (s * 0.11, -0.165, 1.33), (0.08, 0.012, 0.3), M("seam"), root, 0.004).rotation_euler.y = \
            s * 0.25
        rbox(f"{name}.latch{s}", (0.48, -0.04 + s * 0.12, 0.72), (0.012, 0.04, 0.025), M("gold", metal=0.8, rough=0.3), root,
             0.003)
    for j in range(3):  # a mouth grille
        gb.box(f"{name}.grille{j}", (0, -0.152, 1.66 - j * 0.022), (0.14, 0.01, 0.008), M("seam"), parent=root)
    gb.box(f"{name}.seam", (0, -0.162, 0.96), (0.58, 0.008, 0.012), M("seam"), parent=root)
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
    k = sum(map(ord, name))  # homemade, so no two alike
    if k % 2:  # a mismatched claw arm
        gb.cyl(f"{name}.arm2", (-0.17, -0.02, 0.26), 0.028, 0.14, M("goodbot2"), parent=root)
        rbox(f"{name}.claw", (-0.17, -0.04, 0.17), (0.05, 0.03, 0.04), M("screw", metal=0.7), root, 0.008)
    else:
        gb.cyl(f"{name}.arm2", (-0.17, -0.02, 0.24), 0.016, 0.18, M("screw"), parent=root)
    rbox(f"{name}.patch", (0.05 * (1 if k % 3 else -1), -0.12, 0.2), (0.07, 0.01, 0.06), M("goodbot2"), root, 0.006)
    for s in (-1, 1):
        gb.cyl(f"{name}.wheel{s}", (s * 0.08, 0, 0.035), 0.035, 0.03, M("eye"), parent=root, axis="X")
    gb.sphere(f"{name}.tip", (0.04, 0, 0.645), 0.014, M("lantern" if k % 3 else "goodbot2"), parent=root)
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
