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


POSES = {  # joint positions (x, y, z), metres at h = 1, figure facing -Y; arms: shoulder, elbow, wrist per side
    "stand": {"knee": (0.1, -0.01, 0.46), "ankle": (0.1, 0.0, 0.1), "arm": {
        -1: ((-0.2, 0.0, 1.19), (-0.27, 0.02, 0.95), (-0.29, -0.01, 0.73)),
        1: ((0.2, 0.0, 1.19), (0.27, 0.02, 0.95), (0.29, -0.01, 0.73))}},
    "sit": {"knee": (0.1, -0.42, 0.84), "ankle": (0.1, -0.46, 0.2), "arm": {
        -1: ((-0.2, 0.0, 1.19), (-0.27, -0.08, 0.96), (-0.24, -0.3, 0.86)),
        1: ((0.2, 0.0, 1.19), (0.27, -0.08, 0.96), (0.24, -0.3, 0.86))}},
    "phone": {"knee": (0.1, -0.01, 0.46), "ankle": (0.1, 0.0, 0.1), "arm": {
        -1: ((-0.2, 0.0, 1.19), (-0.27, 0.02, 0.95), (-0.29, -0.01, 0.73)),
        1: ((0.2, 0.0, 1.19), (0.33, 0.02, 1.13), (0.22, -0.05, 1.38))}},
    "reach": {"knee": (0.1, -0.01, 0.46), "ankle": (0.1, 0.0, 0.1), "arm": {  # S11: into the handset in front of him
        -1: ((-0.2, 0.0, 1.19), (-0.27, 0.02, 0.95), (-0.29, -0.01, 0.73)),
        1: ((0.2, 0.0, 1.19), (0.2, -0.25, 1.08), (0.06, -0.44, 0.86))}},
    "hold": {"knee": (0.1, -0.01, 0.46), "ankle": (0.1, 0.0, 0.1), "arm": {  # S11-S12: the tape held up like evidence
        -1: ((-0.2, 0.0, 1.19), (-0.27, 0.02, 0.95), (-0.29, -0.01, 0.73)),
        1: ((0.2, 0.0, 1.19), (0.3, -0.1, 1.38), (0.24, -0.2, 1.6))}},
    "dribble": {"knee": (0.1, -0.01, 0.46), "ankle": (0.1, 0.0, 0.1), "arm": {  # S20: palm down over the ball
        -1: ((-0.2, 0.0, 1.19), (-0.27, 0.02, 0.95), (-0.29, -0.01, 0.73)),
        1: ((0.2, 0.0, 1.19), (0.3, -0.12, 0.98), (0.32, -0.3, 0.9))}},
    # S19: on both knees, shins flat behind, soles up; the figure's root goes KNEEL_DROP under the ground
    "kneel": {"knee": (0.1, -0.1, 0.48), "ankle": (0.1, 0.32, 0.47), "arm": {
        -1: ((-0.2, 0.0, 1.19), (-0.27, 0.02, 0.95), (-0.29, -0.01, 0.73)),
        1: ((0.2, 0.0, 1.19), (0.27, 0.02, 0.95), (0.29, -0.01, 0.73))}},
}
KNEEL_DROP = 0.4  # "kneel": the ground is this far over the root (h = 1)
HOLD = (0.226, -0.254, 1.745)
DRIBBLE = (0.326, -0.355, 0.816)  # "dribble": under the palm (x, y), and the palm's underside (z), figure space  # "hold": where the held thing's centre is, figure space (h = 1)


def skin_body(name, verts, edges, radii, m, root, h):
    """A continuous limb or trunk: a skeleton of joints with a radius each (Blender's Skin modifier, subdivided),
    baked once to a plain mesh."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(c * h for c in v) for v in verts], edges, [])
    o = gb.link(bpy.data.objects.new(name, me), root)
    o.modifiers.new("skin", "SKIN").use_smooth_shade = True
    sv = me.skin_vertices[0].data
    for i, r in enumerate(radii):
        sv[i].radius = (r[0] * h, r[1] * h) if isinstance(r, tuple) else (r * h, r * h)
    sv[0].use_root = True
    o.modifiers.new("sub", "SUBSURF").levels = 2
    bpy.context.view_layer.update()
    baked = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    o.modifiers.clear()
    o.data = baked
    baked.materials.append(m)
    for poly in baked.polygons:
        poly.use_smooth = True
    return o


def base(name, loc, rot_z, top, legs="jeans", skin="skin1", h=1.0, head_r=0.19, style="crop", hair_col="hair0",
         face=True, pose="stand"):
    """A toy-like figure: one continuous trunk-and-arms in `top`, one pair of legs in `legs` (Skin-modifier bodies,
    so shoulders, elbows and knees join), mitten hands, rounded shoes, a big head with white eyes and dark pupils,
    brows, nose, ears and hair (`style`). h scales the whole figure; face=False is a mannequin's; pose is a POSES key
    (stand, sit, phone). The mouth (`jaw`) is the lip sync's: its z scale opens it."""
    root = gb.empty(name, loc)
    root.rotation_euler.z = rot_z
    P = POSES[pose]
    kx, ky, kz = P["knee"]
    ax, ay, az = P["ankle"]
    # legs and hips: pelvis (root vertex), then hip, knee, ankle per side
    for s in (-1, 1):  # each leg its own chain from under the hem (a branched pelvis folded into flaps)
        skin_body(f"{name}.leg{s}", [(s * 0.09, 0, 0.86), (s * 0.095, 0, 0.74), (s * kx, ky, kz), (s * ax, ay, az)],
                  [(0, 1), (1, 2), (2, 3)], [0.1, 0.1, 0.075, 0.06], M(legs), root, h)
    # trunk and arms: waist (root), chest, shoulder line, neck base; shoulder, elbow, wrist per side
    # the top comes down over the hips (hem, waist, chest, shoulder line, neck base)
    tv = [(0, 0, 0.68), (0, 0, 0.86), (0, 0, 1.08), (0, 0, 1.2), (0, 0, 1.28)]
    te = [(0, 1), (1, 2), (2, 3), (3, 4)]
    tr = [(0.2, 0.135), (0.19, 0.13), (0.2, 0.135), (0.17, 0.12), 0.065]
    for s in (-1, 1):
        sh, el, wr = P["arm"][s]
        i = len(tv)
        tv += [sh, el, wr]
        te += [(3, i), (i, i + 1), (i + 1, i + 2)]
        tr += [0.068, 0.058, 0.05]
        # mitten hand and thumb, just past the wrist
        d = tuple(w - e for w, e in zip(wr, el))
        L = math.sqrt(sum(c * c for c in d)) or 1
        hc = tuple((w + 0.06 * c / L) * h for w, c in zip(wr, d))
        ellipsoid(f"{name}.hand{s}", hc, (0.042 * h, 0.05 * h, 0.06 * h), M(skin), root)
        gb.sphere(f"{name}.thumb{s}", (hc[0] - s * 0.01 * h, hc[1] - 0.04 * h, hc[2] + 0.015 * h), 0.022 * h, M(skin),
                  parent=root)
    skin_body(f"{name}.torso", tv, te, tr, M(top), root, h)
    kneel = pose == "kneel"
    g = KNEEL_DROP if kneel else 0.0  # the ground, figure space
    for s in (-1, 1):  # rounded shoes with white soles (kneeling: lying behind, soles up)
        fy = ay + 0.09 if kneel else ay - 0.04
        ellipsoid(f"{name}.shoe{s}", (s * ax * h, fy * h, (g + 0.05) * h), (0.065 * h, 0.13 * h, 0.055 * h), M("shoe"),
                  root)
        rbox(f"{name}.sole{s}", (s * ax * h, fy * h, (g + (0.088 if kneel else 0.012)) * h), (0.13 * h, 0.26 * h, 0.025 * h),
             M("sole"), root, 0.012)
    gb.cyl(f"{name}.neck", (0, 0, 1.3 * h), 0.06 * h, 0.1 * h, M(skin), parent=root)
    head = gb.sphere(f"{name}.head", (0, 0, 1.47 * h), head_r * h, M(skin), parent=root)
    head.scale = (1.0, 0.96, 1.04)
    jaw = rbox(f"{name}.jaw", (0, -0.178 * h, 1.4 * h), (0.085 * h, 0.03 * h, 0.065 * h), M("mouth"), root, 0.015)
    jaw.scale.z = 0.05
    root["jaw"] = jaw.name
    if not face:  # a mannequin: smooth and blank
        jaw.hide_render = jaw.hide_viewport = True
        return root
    for s in (-1, 1):
        ellipsoid(f"{name}.eyewhite{s}", (s * 0.068 * h, -0.158 * h, 1.51 * h), (0.036 * h, 0.022 * h, 0.042 * h),
                  M("white"), root)
        gb.sphere(f"{name}.eye{s}", (s * 0.066 * h, -0.176 * h, 1.505 * h), 0.021 * h, M("eye"), parent=root)
        gb.sphere(f"{name}.glint{s}", (s * 0.066 * h + 0.008 * h, -0.194 * h, 1.515 * h), 0.006 * h,
                  gb.mat("chr.glint", "#ffffff", emit=2.0), parent=root)
        ellipsoid(f"{name}.ear{s}", (s * head_r * 0.98 * h, 0.01 * h, 1.47 * h), (0.025 * h, 0.035 * h, 0.05 * h), M(skin),
                  root)
        rbox(f"{name}.brow{s}", (s * 0.07 * h, -0.164 * h, 1.572 * h), (0.07 * h, 0.018 * h, 0.017 * h), M(hair_col),
             root, 0.007).rotation_euler.y = s * 0.12
    ellipsoid(f"{name}.nose", (0, -0.188 * h, 1.455 * h), (0.024 * h, 0.028 * h, 0.03 * h), M(skin), root)
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


def dev(loc, rot_z=0.0, name="dev", pose="stand"):
    root = base(name, loc, rot_z, "hoodie", skin="skin1", style="curly", hair_col="hair0", pose=pose)
    for s in (-1, 1):  # the hoodie's drawstrings
        gb.cyl(f"{name}.string{s}", (s * 0.045, -0.17, 1.17), 0.008, 0.16, M("drawstring"), parent=root)
    rbox(f"{name}.hood", (0, 0.12, 1.28), (0.34, 0.16, 0.16), M("hoodie"), root, 0.06)  # hood down, on the shoulders
    # the shop apron: canvas wrapped round the body from chest to thigh, a pocket, a neck strap, a tool belt
    skin_body(f"{name}.apron", [(0, 0, 0.6), (0, 0, 0.8), (0, 0, 1.0), (0, 0, 1.12)], [(0, 1), (1, 2), (2, 3)],
              [(0.215, 0.15), (0.21, 0.148), (0.218, 0.152), (0.15, 0.11)], M("apron"), root, 1.0)
    rbox(f"{name}.apronpocket", (0, -0.2, 0.84), (0.2, 0.012, 0.1), M("belt"), root, 0.01)
    for s in (-1, 1):  # the neck strap
        rbox(f"{name}.apronstrap{s}", (s * 0.075, -0.12, 1.2), (0.028, 0.02, 0.14), M("belt"), root, 0.006)
    import mk
    belt = mk.MK()
    belt.torus((0, 0, 0), 0.215, 0.022, M("belt"), n=32, k=6)
    o = gb.link(bpy.data.objects.new(f"{name}.belt", belt.mesh(f"{name}.belt")), root)
    o.location, o.scale = (0, 0, 0.74), (1.0, 0.72, 1.0)
    for s in (-1, 1):
        rbox(f"{name}.pouch{s}", (s * 0.19, -0.12, 0.68), (0.1, 0.06, 0.12), M("belt"), root, 0.015)
    return root


def ceo(loc, rot_z=0.0, name="ceo"):
    pose = {"ceo18": "sit", "ceo10": "phone", "ceo20": "dribble"}.get(name, "stand")  # S18 on the throne; S10 on the
    # phone; S20 bouncing the ball
    root = base(name, loc, rot_z, "ceohood", skin="skin3", style="crop", hair_col="hair3", pose=pose)
    if pose == "sit":
        root.location.z = 0.0  # hips on the throne's seat
    if pose == "phone":
        rbox(f"{name}.phone", (0.2, -0.07, 1.46), (0.02, 0.075, 0.15), M("case"), root, 0.006)
    rbox(f"{name}.hood", (0, 0.11, 1.27), (0.32, 0.15, 0.15), M("ceohood"), root, 0.06)
    # the ermine cape hangs behind from the shoulders, its red lining showing at the open front edges
    cape_mk = __import__("mk").MK()
    prof = [(0.17, 1.26), (0.27, 1.12), (0.33, 0.8), (0.37, 0.4), (0.39, 0.12)]
    for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
        pass
    import bmesh
    n = 20
    a0, a1 = -0.3 * math.pi, 1.3 * math.pi  # an open shell round the back (front gap between the edges)
    bm = cape_mk.bm
    rows = []
    for r, z in prof:
        rows.append([bm.verts.new((r * math.cos(a0 + (a1 - a0) * j / n), 0.03 + 0.75 * r * math.sin(a0 + (a1 - a0) * j / n),
                                   z)) for j in range(n + 1)])
    for ra, rb in zip(rows, rows[1:]):
        for j in range(n):
            f = bm.faces.new((ra[j], ra[j + 1], rb[j + 1], rb[j]))
            f.smooth = True
    cape_mk._finish([v for r in rows for v in r], M("ermine"))
    me = cape_mk.mesh(f"{name}.cape")
    cape = gb.link(bpy.data.objects.new(f"{name}.cape", me), root)
    sol = cape.modifiers.new("thick", "SOLIDIFY")
    sol.thickness, sol.material_offset = -0.025, 1  # the lining on the inside
    me.materials.append(M("lining"))
    bpy.context.view_layer.update()
    baked = bpy.data.meshes.new_from_object(cape.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    cape.modifiers.clear()
    cape.data = baked
    collar = __import__("mk").MK()
    collar.torus((0, 0.02, 1.27), 0.17, 0.055, M("ermine"), n=28, k=10)
    for k in range(10):
        a = 2 * math.pi * k / 10
        collar.box((0.215 * math.cos(a), 0.02 + 0.215 * math.sin(a), 1.27), (0.02, 0.02, 0.045), M("spot"))
    gb.link(bpy.data.objects.new(f"{name}.collar", collar.mesh(f"{name}.collar")), root)
    for k in range(16):  # ermine spots on the back of the cape
        a = 0.15 * math.pi + 0.7 * math.pi * (k % 8) / 7
        z = 0.35 + 0.3 * (k // 8) + 0.12 * (k % 2)
        r = 0.37 + 0.02 * (0.8 - z)
        gb.box(f"{name}.spot{k}", (r * math.cos(a), 0.03 + 0.75 * r * math.sin(a) + 0.015, z), (0.03, 0.02, 0.06),
               M("spot"), parent=root).rotation_euler.z = a - math.pi / 2
    return root


def mod(loc, k, rot_z=0.0, broom=True, name=None, pose="stand"):
    """A mod in a MOD vest, with a broom. pose "kneel": loc is still the ground under them."""
    name = name or f"mod{k}"
    g = KNEEL_DROP if pose == "kneel" else 0.0
    loc = (loc[0], loc[1], loc[2] - g)
    skin = ("skin1", "skin2", "skin3")[k % 3]
    blank = name.startswith("mannequin")  # S21: identical, faceless mannequins in MOD vests
    style = HAIRS[k % 6]
    root = base(name, loc, rot_z, "mannequin" if blank else "modbody", legs="mannequin" if blank else "jeans",
                skin="mannequin" if blank else skin, style=style,
                hair_col=f"knit{k % 3}" if style == "beanie" else f"hair{k % 5}", face=not blank, pose=pose)
    # the vest, shaped to the body: a trunk a little bigger than the top, arm holes left at the shoulders
    vest = skin_body(f"{name}.vest", [(0, 0, 0.76), (0, 0, 0.9), (0, 0, 1.08), (0, 0, 1.2), (0, 0, 1.25)],
              [(0, 1), (1, 2), (2, 3), (3, 4)],
              [(0.22, 0.15), (0.225, 0.155), (0.235, 0.16), (0.2, 0.14), (0.12, 0.1)], M("vest"), root, 1.0)
    import mk
    for z, rx, ry in ((0.9, 0.212, 0.152), (1.06, 0.226, 0.159)):  # reflective tape
        t = mk.MK()
        t.torus((0, 0, 0), rx, 0.016, M("reflect", rough=0.3), n=32, k=6)
        o = gb.link(bpy.data.objects.new(f"{name}.tape{z}", t.mesh(f"{name}.tape{z}")), root)
        o.location, o.scale = (0, 0, z), (1.0, ry / rx, 0.7)
    front = min(v.co.y for v in vest.data.vertices if abs(v.co.x) < 0.05 and 1.1 < v.co.z < 1.17)
    gb.text(f"{name}.vest.t", "MOD", 0.075, gb.mat("chr.vestink", "#1a1a1a"), (0, front - 0.004, 1.135), facing="-Y",
            parent=root)
    if broom:
        import kit
        kit.place(f"{name}.broom", "wooden_broom", (0.315, -0.04, g), rot_z=math.pi / 2, scale=0.93, parent=root)
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
