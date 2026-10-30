"""Detail pass: the street (see detail.py). The final look only.

Street furniture and life on the block and the streets round it:
  cars       parked cars, modelled here: sedans, hatchbacks and minivans with bevelled bodies, glass cabins with
             pillars, tyres and rims, wheel arches, lamps, bumpers and blank plates; muted colours (Object Info colour
             on one shared body material); no brands, no badges; lights off, the tail lamps dark amber. On the block
             only where no gag needs the lane: the south side east of x = 9, the north side east of x = 26 and west
             of x = -27; more along the cross street and the far streets
  furniture  hydrants (the kit's pair split, the aged one, repainted SF white: red is reserved), bins, parking
             meters, newspaper boxes (no names), utility boxes, manholes and storm drains, a bike rack, a ONE WAY sign
             and a speed-limit sign (no stop signs, no signals: red), street trees in grates (two, one mesh, thinned)
  paint      worn continental crosswalks and stop lines at both corners, parking-lane edge lines and dashed lane
             lines down the street
  the tower  its plaza kept spotless (pale granite pavers over the sidewalk), a row of steel bollards with cold
             light rings along its glass, and security cameras on its front watching the street, each with a small
             REC light (the recording theme; red is the REC lights')

Kept clear of the action (shots.py): the Dev's door and the tape's run to the tracks (S08), the boombox and the
sidewalk tape (S12, S13), the payphone and the meter lamp, the mods' walk (S17) and kneel (S19), the locksmith van's
lane (S21), the chalked square (S33), the trucks' lanes and the crates (S28-S31), the VIP bots' walk (S39), every
shop door. Seeded, so every render matches.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

import city
import gb
import kit

SEED = 20261103
Batch = city.Batch


def mat(key, hexcol, grime=0.5, **kw):
    return city.mat(f"st.{key}", hexcol, grime=grime, **kw)


# ---------------------------------------------------------------- kit helpers

_HALF = {}


def half(aid, keep):
    """One of a kit model that comes as a pair side by side in x (keep = -1 or 1), re-centred, bottom at z 0."""
    key = (aid, keep)
    if key in _HALF:
        return _HALF[key]
    me = kit.load(aid).copy()
    me.name = f"kit.{aid}.{'L' if keep < 0 else 'R'}"
    bm = bmesh.new()
    bm.from_mesh(me)
    drop = [f for f in bm.faces if (f.calc_center_median().x > 0) != (keep > 0)]
    bmesh.ops.delete(bm, geom=drop, context="FACES")
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    for v in bm.verts:
        v.co -= off
    bm.to_mesh(me)
    bm.free()
    _HALF[key] = me
    return me


def repaint(me, tint, sat=0.1, name=None):
    """me's materials, copied with their colour desaturated and tinted (the hydrant's red to an aged white)."""
    for i, m in enumerate(me.materials):
        if m is None:
            continue
        c = m.copy()
        c.name = f"{m.name}.{name or 'repaint'}"
        nt = c.node_tree
        b = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
        inp = b.inputs["Base Color"]
        if inp.is_linked:
            src = inp.links[0].from_socket
            hs = nt.nodes.new("ShaderNodeHueSaturation")
            hs.inputs["Saturation"].default_value = sat
            hs.inputs["Value"].default_value = 1.6
            nt.links.new(src, hs.inputs["Color"])
            mx = nt.nodes.new("ShaderNodeMix")
            mx.data_type, mx.blend_type = "RGBA", "MULTIPLY"
            mx.inputs[0].default_value = 1.0
            nt.links.new(hs.outputs[0], mx.inputs[6])
            mx.inputs[7].default_value = gb.lin(tint)
            nt.links.new(mx.outputs[2], inp)
        else:
            inp.default_value = gb.lin(tint)
        me.materials[i] = c
    return me


def thin(me, mi, keep, seed):
    """A copy of me with only a fraction `keep` of material mi's faces (seeded): a sparser crown of leaf cards, at a
    fraction of the cost. numpy throughout (the tree has two million faces)."""
    nv, nl, npoly = len(me.vertices), len(me.loops), len(me.polygons)
    co = np.empty(nv * 3, np.float32)
    me.vertices.foreach_get("co", co)
    ls = np.empty(npoly, np.int32)
    lt = np.empty(npoly, np.int32)
    pm = np.empty(npoly, np.int32)
    me.polygons.foreach_get("loop_start", ls)
    me.polygons.foreach_get("loop_total", lt)
    me.polygons.foreach_get("material_index", pm)
    lv = np.empty(nl, np.int32)
    me.loops.foreach_get("vertex_index", lv)
    uvs = []
    for layer in me.uv_layers:
        a = np.empty(nl * 2, np.float32)
        layer.data.foreach_get("uv", a)
        uvs.append((layer.name, a.reshape(-1, 2)))
    rng = np.random.default_rng(seed)
    keep_p = (pm != mi) | (rng.random(npoly) < keep)
    ls2, lt2, pm2 = ls[keep_p], lt[keep_p], pm[keep_p]
    idx = np.concatenate([np.arange(s, s + t) for s, t in zip(ls2, lt2)]) if len(ls2) < 50000 else \
        np.repeat(ls2, lt2) + (np.arange(lt2.sum()) - np.repeat(np.cumsum(lt2) - lt2, lt2))
    out = bpy.data.meshes.new(me.name + ".thin")
    out.vertices.add(nv)
    out.vertices.foreach_set("co", co)
    out.loops.add(len(idx))
    out.loops.foreach_set("vertex_index", lv[idx])
    out.polygons.add(len(ls2))
    out.polygons.foreach_set("loop_start", (np.cumsum(lt2) - lt2).astype(np.int32))
    out.polygons.foreach_set("material_index", pm2)
    for name, a in uvs:
        layer = out.uv_layers.new(name=name)
        layer.data.foreach_set("uv", a[idx].ravel())
    out.update(calc_edges=True)
    out.polygons.foreach_set("use_smooth", [True] * len(out.polygons))
    for m in me.materials:
        out.materials.append(m)
    return out


def decimate(me, ratio):
    """A collapse-decimated copy of me (the kit's hydrant is 43k faces; at street distance a tenth reads the same)."""
    tmp = bpy.data.objects.new("tmp.decimate", me)
    bpy.context.scene.collection.objects.link(tmp)
    mod = tmp.modifiers.new("d", "DECIMATE")
    mod.ratio = ratio
    dg = bpy.context.evaluated_depsgraph_get()
    out = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    out.name = me.name + ".lo"
    bpy.data.objects.remove(tmp)
    return out


def place(name, me, loc, rot_z=0.0, scale=1.0, rot=None):
    o = gb.link(bpy.data.objects.new(name, me))
    o.location = loc
    o.rotation_euler = rot if rot else (0, 0, rot_z)
    o.scale = (scale,) * 3
    return o


# ---------------------------------------------------------------- cars

CAR_COLOURS = ["#5b6670", "#3e4a42", "#8a8578", "#c9c6bc", "#2a3140", "#1d1e20", "#9aa2a6", "#5c4f42", "#6f7f8a",
               "#4a5a63", "#b8b0a0", "#3b3b3e", "#71736c", "#2f3a33"]
CAR_TYPES = {  # length, width, roof height, hood length, trunk length, windshield run, rear glass run
    "sedan": (4.6, 1.8, 1.44, 1.25, 0.95, 0.75, 0.62),
    "hatch": (4.05, 1.76, 1.5, 0.95, 0.22, 0.7, 0.38),
    "van": (4.9, 1.92, 1.82, 0.85, 0.12, 0.85, 0.18),
}
_CARS = {}


def car_mats():
    body = bpy.data.materials.get("st.car.body")
    if body is None:
        body = bpy.data.materials.new("st.car.body")
        body.use_nodes = True
        nt = body.node_tree
        b = nt.nodes["Principled BSDF"]
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        nt.links.new(oi.outputs["Color"], b.inputs["Base Color"])
        b.inputs["Metallic"].default_value = 0.35
        b.inputs["Roughness"].default_value = 0.38
        b.inputs["Coat Weight"].default_value = 0.4
        gb.grime(body, amt=0.4, space="object", damp=0.5)
    return [body,
            gb.mat("st.car.glass", "#10161c", rough=0.06, metal=0.2),
            gb.mat("st.car.tyre", "#141414", rough=0.9),
            gb.mat("st.car.rim", "#8e9296", rough=0.35, metal=0.8),
            mat("car.trim", "#1e1f21", grime=0.3, rough=0.6),
            gb.mat("st.car.head", "#d9dde0", rough=0.1, metal=0.3),
            gb.mat("st.car.tail", "#4a2a12", rough=0.15),
            gb.mat("st.car.plate", "#d8d6cc", rough=0.5)]


def prism(bm, pts, y0, y1):
    """A side profile (x, z) extruded across y0..y1; returns the new faces."""
    a = [bm.verts.new((x, y0, z)) for x, z in pts]
    b = [bm.verts.new((x, y1, z)) for x, z in pts]
    n = len(pts)
    faces = [bm.faces.new(a[::-1]), bm.faces.new(b)]
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    return faces


def car_mesh(kind):
    if kind in _CARS:
        return _CARS[kind]
    L, W, H, hood, trunk, ws, rg = CAR_TYPES[kind]
    hl, hw = L / 2, W / 2
    belt = 0.98 if kind != "van" else 1.05
    bm = bmesh.new()
    # the lower body
    body = prism(bm, [(-hl, 0.3), (hl, 0.3), (hl, 0.62), (hl - 0.12, belt - 0.16), (hl - hood, belt),
                      (-hl + max(trunk, 0.1), belt + 0.02), (-hl + 0.05, belt - 0.08), (-hl, 0.66)], -hw, hw)
    edges = list(dict.fromkeys(e for f in body for e in f.edges))  # ordered, so every build matches
    bmesh.ops.bevel(bm, geom=edges, offset=0.07, segments=2, affect="EDGES",
                    profile=0.6)
    for f in bm.faces:
        f.material_index = 0
    # the cabin: a tapered prism; its sides split by the B pillar and inset to leave frames in body colour
    cb = bmesh.new()
    x0, x1 = -hl + trunk, hl - hood
    cab = prism(cb, [(x0, belt), (x1, belt), (x1 - ws, H), (x0 + rg, H)], -hw + 0.1, hw - 0.1)
    for v in cb.verts:
        if v.co.z > belt + 0.01:
            v.co.y *= 0.86
    sides = [f for f in cab if abs(f.normal.y) > 0.5]
    for f in sides:  # the B pillar: split each side at the middle
        top = [e for e in f.edges if all(v.co.z > belt + 0.01 for v in e.verts)]
        bot = [e for e in f.edges if all(v.co.z < belt + 0.01 for v in e.verts)]
        res = bmesh.ops.subdivide_edges(cb, edges=top + bot, cuts=1, use_grid_fill=False)
        nv = [g for g in res["geom_inner"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.connect_verts(cb, verts=nv)
    cb.faces.ensure_lookup_table()
    for f in list(cb.faces):
        f.material_index = 0
    for f in cb.faces:
        f.normal_update()
    sides = [f for f in cb.faces if -0.7 < f.normal.z < 0.7]
    bmesh.ops.inset_individual(cb, faces=sides, thickness=0.06, depth=-0.012)
    for f in sides:
        f.material_index = 1
    me_c = bpy.data.meshes.new("tmp")
    cb.to_mesh(me_c)
    cb.free()
    bm.from_mesh(me_c)
    bpy.data.meshes.remove(me_c)
    me = bpy.data.meshes.new(f"car.{kind}")
    bm.to_mesh(me)
    bm.free()
    # wheels, arches, bumpers, lamps, plates, mirrors
    B = Batch("tmp", [])
    for sx in (-1, 1):
        wx = sx * (hl - (0.78 if sx > 0 else 0.72))
        for sy in (-1, 1):
            y = sy * (hw - 0.07)  # the tyre's outer face just proud of the body side
            B.cyl((wx, y, 0.33), 0.33, 0.22, mi=2, n=18, rot=Euler((math.pi / 2, 0, 0)))
            B.cyl((wx, y + sy * 0.112, 0.33), 0.2, 0.01, mi=3, n=14, rot=Euler((math.pi / 2, 0, 0)))
            B.cyl((wx, y + sy * 0.118, 0.33), 0.06, 0.01, mi=4, n=8, rot=Euler((math.pi / 2, 0, 0)))
            # the arch: a dark half-disc on the body side, over the tyre
            pts = [(wx + 0.43 * math.cos(a), sy * (hw + 0.004), 0.31 + 0.43 * math.sin(a))
                   for a in np.linspace(0, math.pi, 10)]
            base = len(B.v)
            B.v += pts
            B.f.append(tuple(range(base, base + 10)) if sy > 0 else tuple(range(base + 9, base - 1, -1)))
            B.mi.append(4)
        B.box((sx * (hl + 0.02), 0, 0.42), (0.16, W - 0.08, 0.2), mi=4)  # bumper
        B.box((sx * (hl + 0.105), 0, 0.46), (0.02, 0.5, 0.12), mi=7)  # blank plate
        for sy in (-1, 1):
            if sx > 0:
                B.box((hl - 0.03, sy * (hw - 0.3), belt - 0.27), (0.08, 0.36, 0.12), mi=5)
            else:
                B.box((-hl + 0.02, sy * (hw - 0.22), belt - 0.18), (0.08, 0.3, 0.14), mi=6)
    B.box((hl + 0.005, 0, 0.62), (0.04, W * 0.42, 0.14), mi=4)  # grille
    for sy in (-1, 1):  # mirrors
        B.box((hl - hood - 0.15, sy * (hw + 0.06), belt + 0.12), (0.14, 0.14, 0.11), mi=4)
    bm = bmesh.new()
    bm.from_mesh(me)
    tmp = bpy.data.meshes.new("tmp")
    tmp.from_pydata(B.v, [], B.f)
    tmp.polygons.foreach_set("material_index", B.mi)
    bm.from_mesh(tmp)
    bpy.data.meshes.remove(tmp)
    bm.to_mesh(me)
    bm.free()
    for m in car_mats():
        me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = p.material_index in (0, 2)
    _CARS[kind] = me
    return me


def car(name, x, y, heading, rng, kind=None):
    kind = kind or rng.choice(("sedan", "sedan", "hatch", "hatch", "van"))
    o = place(name, car_mesh(kind), (x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.08, 0.08), 0.0),
              rot_z=heading + rng.uniform(-0.03, 0.03))
    o.color = (*gb.lin(rng.choice(CAR_COLOURS))[:3], 1.0)
    return o


def cars(rng):
    """Parked along the curbs where the shots leave the lanes free (see the docstring)."""
    rows = [  # x0, x1, curb y, heading
        (11.0, 43.5, -5.05, 0.0),  # south side, east of the van's lane and the crates
        (27.5, 44.0, 5.05, math.pi),  # north side, east of the tower and the trucks
        (-110, -50, -5.05, 0.0), (-110, -50, 5.05, math.pi),  # the street west of the cross street
        (62, 115, -5.05, 0.0), (62, 115, 5.05, math.pi),  # and east of the next one
    ]
    skip = [(9.6, -1), (42.6, 1), (-120, 0), (130, 0)]  # hydrants (x, side) and the far crossings
    n = 0
    for x0, x1, y, hd in rows:
        x = x0 + rng.uniform(0, 1.5)
        while x < x1 - 2.4:
            side = 1 if y > 0 else -1
            if any(abs(x + 2.3 - hx) < 3.6 and (s == side or s == 0) for hx, s in skip) or rng.random() < 0.1:
                x += rng.uniform(2.0, 4.0)
                continue
            car(f"car{n}", x + 2.3, y, hd, rng)
            n += 1
            x += rng.uniform(5.3, 6.4)
    cols = [  # the one-way cross streets (southbound): parked both sides
        (-42.0, (-110, -12)), (-37.0, (-110, -14)), (-42.0, (13, 110)), (-37.0, (15, 110)),
        (49.0, (-100, -12)), (54.0, (-100, -12)), (49.0, (12, 100)), (54.0, (12, 100))]
    for xc, (y0, y1) in cols:
        y = y0 + rng.uniform(0, 3)
        while y < y1 - 2.4:
            if any(abs(y - yy) < 9 for yy in (-54, 54, -146, 144)) or (xc < -40 and -27 < y < -12) or rng.random() < 0.2:
                y += rng.uniform(3, 6)
                continue
            car(f"car{n}", xc, y + 2.3, -math.pi / 2, rng)
            n += 1
            y += rng.uniform(5.2, 6.8)


# ---------------------------------------------------------------- furniture

def furniture(rng):
    hyd = repaint(decimate(half("fire_hydrant", 1), 0.12), "#e9e4d6", sat=0.08, name="sfwhite")
    for k, (x, y) in enumerate(((9.6, -6.55), (42.6, 6.55), (-35.5, -15.8), (-43.5, 12.8), (45.5, -13.0),
                                (-43.6, -33.0), (47.6, 20.0))):
        place(f"hydrant{k}", hyd, (x, y, 0.15), rot_z=rng.uniform(0, 6.28), scale=0.95)
    can = half("metal_trash_can", -1)  # the rusty one
    for k, (x, y) in enumerate(((-11.7, -6.6), (19.6, -6.6), (37.8, -6.6), (36.4, 6.6), (-35.4, 14.2),
                                (-43.6, -27.0), (45.6, -21.0), (-34.2, -30.0), (-70, -6.6), (75, 6.6))):
        place(f"bin{k}", can, (x, y, 0.15), rot_z=rng.uniform(0, 6.28), scale=1.0)
    bx1, bx2 = kit.load("utility_box_01"), kit.load("utility_box_02")
    place("ubox0", bx2, (43.7, -9.55, 0.15), rot_z=math.pi)
    place("ubox1", bx1, (-30.5, -12.4, 0.15), rot_z=-math.pi / 2)
    place("ubox2", bx2, (-45.55, -29.0, 0.15), rot_z=math.pi / 2)
    place("ubox3", bx1, (45.5, 26.0, 0.15), rot_z=-math.pi / 2)
    mh = kit.load("water_manhole_cover")
    for k, (x, y) in enumerate(((-12.0, -2.6), (17.5, 2.9), (31.0, -2.8), (-39.5, -18.0), (-39.0, 20.0),
                                (51.5, -14.0), (-62.0, -2.5), (70.0, 2.6))):
        place(f"manhole{k}", mh, (x, y, -0.045), rot_z=rng.uniform(0, 6.28))
    # parking meters, newspaper boxes, storm drains, a bike rack: merged
    grey = mat("meter", "#6d7175", grime=0.6, metal=0.5, rough=0.5)
    dark = mat("meterdark", "#1b1c1e", grime=0.3)
    glass = gb.mat("st.meterglass", "#3a4650", rough=0.1)
    news = [mat(f"news{k}", c, grime=0.7) for k, c in enumerate(("#2f5a7a", "#3f6b4a", "#c9b46a", "#d9d6cc"))]
    F = Batch("street.furniture", [grey, dark, glass] + news + [mat("drain", "#151515", grime=0.2, metal=0.4),
                                       mat("newsprint", "#b9b5a8", grime=0.3)])
    for x, y, s in [(x, -6.42, -1) for x in (10.6, 16.6, 22.2, 27.8, 33.0, 39.2)] + \
                   [(x, 6.42, 1) for x in (28.4, 34.2, 40.2)]:
        F.cyl((x, y, 0.75), 0.03, 1.2, mi=0, n=8)
        F.box((x, y, 1.45), (0.2, 0.14, 0.32), mi=0)
        F.cyl((x, y, 1.62), 0.1, 0.08, mi=0, n=10, r2=0.06)
        F.box((x, y + s * 0.072, 1.5), (0.12, 0.01, 0.1), mi=2)
        F.box((x, y + s * 0.072, 1.36), (0.1, 0.01, 0.05), mi=1)
    for k, (x, y, rz) in enumerate(((24.5, -6.85, 0.0), (25.08, -6.85, 0.0), (25.66, -6.9, 0.05), (-34.2, -8.35, -1.5708),
                                    (-34.25, -8.95, -1.62))):
        r = Matrix.Rotation(rz, 4, "Z")
        mi = 3 + (k % 4)

        def at(dx, dy, dz):
            return tuple(Vector((x, y, 0.15)) + r @ Vector((dx, dy, dz)))
        for lx in (-0.18, 0.18):  # the pedestal's legs
            F.box(at(lx, 0, 0.2), (0.04, 0.3, 0.4), mi=1, rot_z=rz)
        F.box(at(0, 0, 0.75), (0.46, 0.42, 0.7), mi=mi, rot_z=rz)
        F.box(at(0, 0, 1.13), (0.48, 0.44, 0.06), mi=mi, rot_z=rz)
        F.box(at(0, 0.215, 0.82), (0.34, 0.01, 0.34), mi=2, rot_z=rz)  # the window
        F.box(at(0, 0.222, 0.79), (0.27, 0.004, 0.24), mi=8, rot_z=rz)  # a paper in it (no names, no print)
        F.box(at(0, 0.215, 0.55), (0.2, 0.01, 0.05), mi=1, rot_z=rz)  # the coin slot plate
    for x, y in ((-14.5, -5.86), (3.5, -5.86), (24.5, -5.86), (41.0, -5.86), (-29.5, 5.86), (30.5, 5.86), (42.0, 5.86)):
        F.box((x, y, 0.003), (0.9, 0.36, 0.006), mi=7)
        for k in range(6):
            F.box((x - 0.375 + k * 0.15, y, 0.007), (0.05, 0.3, 0.004), mi=1)
    for k in range(3):  # a bike rack: inverted U's (no bikes)
        x = 29.4 + k * 0.9
        for dy in (-0.3, 0.3):
            F.cyl((x, -7.6 + dy, 0.55), 0.025, 0.8, mi=0, n=8)
        F.cyl((x, -7.6, 0.95), 0.025, 0.6, mi=0, n=8, rot=Euler((math.pi / 2, 0, 0)))
    F.done()
    # the sign on the corner's utility pole (the cross street is one-way, southbound): black and white, no red
    signs()
    trees(rng)


def signs():
    blk = gb.mat("st.sign.black", "#141414", rough=0.4)
    wht = gb.mat("st.sign.white", "#e8e6df", rough=0.35)
    pole = mat("signpost", "#5d6064", grime=0.6, metal=0.6, rough=0.5)
    # ONE WAY on the utility pole at the corner, facing the block; its arrow points south (left, from the block)
    x, y, z = -34.32, -6.4, 3.4
    gb.box("sign.oneway", (x, y, z), (0.03, 0.92, 0.32), blk)
    gb.box("sign.oneway.bar", (x + 0.018, y + 0.06, z), (0.005, 0.62, 0.15), wht)
    head = Batch("sign.oneway.head", [wht])
    head.quad([(x + 0.021, y - 0.25, z - 0.12), (x + 0.021, y - 0.25, z + 0.12), (x + 0.021, y - 0.42, z),
               (x + 0.021, y - 0.42, z)])
    head.done()
    gb.text("sign.oneway.t", "ONE WAY", 0.085, blk, (x + 0.024, y + 0.07, z - 0.002), facing="+X")
    gb.box("sign.oneway.strap", (x - 0.06, y, z), (0.1, 0.05, 0.36), pole)
    # SPEED LIMIT 25 on its own post, far east on the south side, facing the eastbound traffic
    x, y = 44.2, -6.55
    gb.cyl("sign.speed.post", (x, y, 1.4), 0.03, 2.8, pole)
    gb.box("sign.speed", (x - 0.04, y, 2.35), (0.03, 0.6, 0.75), wht)
    gb.text("sign.speed.t", "SPEED\nLIMIT", 0.11, blk, (x - 0.06, y, 2.5), facing="-X")
    gb.text("sign.speed.n", "25", 0.26, blk, (x - 0.06, y, 2.15), facing="-X")


def trees(rng):
    """Two street trees in grates, one shared mesh (the kit's tree with its leaf cards thinned to an eighth: a scraggly
    city tree, and the leaves are most of a tree's render cost)."""
    base = kit.load("tree_small_02")
    leaves = next(i for i, m in enumerate(base.materials) if "leaves" in m.name)
    me = thin(base, leaves, 0.13, SEED)
    lm = me.materials[leaves].copy()  # dithered, not blended: cheaper, and it shadows (the park's trees keep theirs)
    lm.name = "st.tree.leaves"
    lm.surface_render_method = "DITHERED"
    me.materials[leaves] = lm
    grate = mat("grate", "#1d1c1b", grime=0.3, metal=0.5, rough=0.6)
    soil = mat("soil", "#2a2119", grime=0.2)
    for k, (x, y, rz) in enumerate(((41.0, -7.45, 0.3), (37.6, 7.45, 2.4))):
        place(f"streettree{k}", me, (x, y, 0.13), rot_z=rz, scale=rng.uniform(0.95, 1.1))
        gb.box(f"streettree{k}.soil", (x, y, 0.145), (1.2, 1.2, 0.01), soil)
        gb.box(f"streettree{k}.grate", (x, y, 0.152), (1.25, 1.25, 0.008), grate)


# ---------------------------------------------------------------- paint

def paint_mat():
    """Worn street paint: off-white, patchy (alpha from noise), so the asphalt shows through."""
    m = bpy.data.materials.get("st.paint")
    if m:
        return m
    m = bpy.data.materials.new("st.paint")
    m.use_nodes = True
    m.surface_render_method = "DITHERED"
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = gb.lin("#b4b0a6")
    b.inputs["Roughness"].default_value = 0.6
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value, n1.inputs["Detail"].default_value = 2.5, 6.0
    nt.links.new(geo.outputs["Position"], n1.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.3, 0.42
    nt.links.new(n1.outputs["Fac"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], b.inputs["Alpha"])
    gb.grime(m, amt=0.3, streak=0.0, damp=0.0)
    return m


def paint():
    P = Batch("street.paint", [paint_mat()])

    def bar(cx, cy, sx, sy):
        P.box((cx, cy, 0.005), (sx, sy, 0.01), bottom=False)  # its top 1 cm up: at 5 mm it flickered in the distance
    # continental crosswalks over the main street, both sides of each cross street
    for cx in (-34.5, -44.5, 46.5, 56.5):
        for y in np.arange(-5.4, 5.5, 1.2):
            bar(cx, y, 2.6, 0.55)
    # over the cross streets, on the line of the main street's sidewalks
    for (a, b) in ((-43.0, -36.0), (48.0, 55.0)):
        for cy in (-8.0, 8.0):
            for x in np.arange(a + 0.5, b - 0.3, 1.2):
                bar(x, cy, 0.55, 2.6)
    # stop lines on the approaches
    bar(-32.4, 3.4, 0.4, 5.0)
    bar(-46.6, -3.4, 0.4, 5.0)
    bar(44.6, -3.4, 0.4, 5.0)
    bar(58.4, 3.4, 0.4, 5.0)
    bar(-39.5, 10.6, 6.8, 0.4)
    bar(51.5, 10.6, 6.8, 0.4)
    # the parking lanes' edge lines and dashed lane lines, between the intersections
    spans = [(-200, -128), (-120, -46.8), (-32.2, 44.4), (58.6, 130), (138, 200)]
    for x0, x1 in spans:
        for y in (-4.0, 4.0):
            bar((x0 + x1) / 2, y, x1 - x0, 0.1)
        for y in (-2.0, 2.0):
            x = x0 + 1.0
            while x + 3.0 < x1:
                bar(x + 1.5, y, 3.0, 0.1)
                x += 12.0
    # the cross streets' lane line (one-way: dashed)
    for xc in (-39.5, 51.5):
        for y0, y1 in ((-142, -58), (-50, -11), (11, 50), (58, 140)):
            y = y0 + 1
            while y + 3 < y1:
                bar(xc, y + 1.5, 0.1, 3.0)
                y += 12.0
    P.done()


# ---------------------------------------------------------------- the tower's frontage

def tower_front(rng):
    """Spotless granite pavers, steel bollards with cold light rings, security cameras with REC lights."""
    m = bpy.data.materials.new("st.plaza")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    br = nt.nodes.new("ShaderNodeTexBrick")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nt.links.new(geo.outputs["Position"], br.inputs["Vector"])
    br.inputs["Color1"].default_value = gb.lin("#b9b8b3")
    br.inputs["Color2"].default_value = gb.lin("#a8a8a4")
    br.inputs["Mortar"].default_value = gb.lin("#7f7f7c")
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.006
    br.inputs["Brick Width"].default_value = 1.2
    br.inputs["Row Height"].default_value = 0.6
    br.offset = 0.5
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.3
    gb.box("plaza", (9.0, 8.32, 0.155), (30.0, 4.36, 0.01), m)  # 1 cm over the sidewalk (6 mm flickered)
    # bollards along the glass, clear of the doors and the brick wall's span (x 6.5..12.5)
    steel = gb.mat("st.bollard", "#c4c9cd", rough=0.25, metal=0.9)
    on = city.night_ctl()
    ring = gb.glow_mat("st.bollard.ring", gb.LOOK["palette"]["corporate"], 6.0, on, "on", base="#c4c9cd")
    Bd = Batch("tower.bollards", [steel, ring])
    for x in (-4.9, -2.5, -0.1, 2.3, 4.7, 13.3, 15.7, 18.1, 20.5, 22.9):
        Bd.cyl((x, 9.95, 0.15 + 0.45), 0.11, 0.9, n=16)
        Bd.cyl((x, 9.95, 1.07), 0.11, 0.04, n=16, r2=0.06)
        Bd.cyl((x, 9.95, 0.92), 0.112, 0.04, mi=1, n=16)
    Bd.done(smooth=True)
    # security cameras: the kit's lens looks along -Y; mounted on arms, tilted down at the street
    cam_me = kit.load("security_camera_01")
    arm = gb.mat("st.camarm", "#d8dce0", rough=0.3, metal=0.6)
    rec = gb.mat("st.camrec", gb.LOOK["palette"]["rec"], emit=10.0)
    for k, (x, y, z, yaw) in enumerate(((-5.6, 10.1, 5.5, -0.5), (23.6, 10.1, 5.5, 0.5), (3.6, 8.35, 7.55, -0.3),
                                        (14.4, 8.35, 7.55, 0.3), (1.0, 10.15, 12.3, -0.15), (17.0, 10.15, 12.3, 0.15))):
        o = place(f"towercam{k}", cam_me, (x, y - 0.25, z - 0.3), rot=(math.radians(22), 0, yaw), scale=1.4)
        if z < 7:
            gb.box(f"towercam{k}.arm", (x, y - 0.12, z - 0.12), (0.06, 0.34, 0.06), arm)
        else:
            gb.box(f"towercam{k}.arm", (x, y - 0.25, z + 0.05), (0.05, 0.05, 0.5) if y < 9 else (0.06, 0.34, 0.06), arm)
        bpy.context.view_layer.update()
        led = o.matrix_world @ Vector((0.05, -0.18, 0.24))
        gb.sphere(f"towercam{k}.rec", tuple(led), 0.012, rec)


# ---------------------------------------------------------------- build

def build(S):
    rng = random.Random(SEED)
    cars(rng)
    furniture(rng)
    paint()
    tower_front(rng)
    city.shadows_near_only()
