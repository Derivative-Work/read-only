"""Detail pass: the gags' props, modelled (see detail.py). Called after shots.stage(): every grey-box object a shot made
or animates keeps its object (name, transform, keys, visibility) and takes a modelled mesh in place of its box
(mk.MK, or a CC0 model through kit.swap). A few new objects carry their shot's visibility (inherit_visibility).

  verse 1   the adding machine; the tear-off calendar (JUNE 1 .. 28, the board ringed 30); the envelope; the receipt
            tape stapled up (S09); the cassette; the boombox (CC0); the magnifying glass (CC0)
  verse 2   the locksmith van; the down arrows; the VIP bots' vacuum hoses; the brick wall laid course by course
            (S24); the briefcase; a cold light on the balcony (S22, S23, S30 were near black)
  verse 3   box trucks and the archive van, lettered on both sides; slatted crates; the bell and its yoke; the
            lectern; the banner's rod; sticky notes ("thanks, this worked"); the funnel; the brooms (CC0) standing in
            a crate; the payroll envelope; the rubber band; the chalk square round YOUR LAND
  eulogy    the shoebox coffin on two crates with its tiny robot; "good bot" notes; the doghouse; the lanterns; the
            shovel (CC0)
"""
import math
import random

import bpy

import block as B
import gb
import kit
import mk
import shots

GEN = gb.ROOT / "assets" / "gen" / "detail" / "props"
EMPTY = None


def mat(key, hexcol, **kw):
    return gb.mat(f"prop.{key}", hexcol, **kw)


def img(key, rough=0.8):
    return mk.img_mat(f"prop.img.{key}", GEN / f"{key}.png", rough=rough)


def obj(name):
    return bpy.data.objects.get(name)


def blank(o):
    """o keeps its keys but draws nothing (its model is part of a sibling's mesh)."""
    global EMPTY
    if EMPTY is None:
        EMPTY = mk.empty_mesh("prop.empty")
    if o:
        o.data = EMPTY


def reset_rot(o):
    o.rotation_euler = (0, 0, 0)


# ---------------------------------------------------------------- verse 1

def adding_machine():
    """S07: a '90s desk adding machine, keys toward the Dev (-Y), the paper roll at the back (+Y)."""
    o = obj("dev.adder")
    m = mk.MK()
    body, dark, key, keyd = mat("adder", "#7f8f86", rough=0.45), mat("adder.dark", "#2a2c2e", rough=0.5), \
        mat("adder.key", "#e9e3d2", rough=0.4), mat("adder.keyd", "#3a3a3a", rough=0.4)
    m.box((0, 0.02, -0.035), (0.34, 0.30, 0.07), body, bevel=0.012)
    m.box((0, -0.05, 0.005), (0.32, 0.18, 0.05), body, rot=(-0.28, 0, 0), bevel=0.01)  # the sloped key deck
    for r in range(4):
        for c in range(5):
            x, y = -0.1 + c * 0.04, -0.115 + r * 0.035
            m.box((x, y, 0.02 + r * 0.01), (0.03, 0.026, 0.014), keyd if c == 4 else key, bevel=0.003, seg=1)
    m.box((0.135, -0.07, 0.035), (0.03, 0.09, 0.016), key, bevel=0.004, seg=1)  # the total bar
    m.box((0, 0.1, 0.04), (0.3, 0.08, 0.07), dark, bevel=0.01)  # the print head housing
    m.cyl((0, 0.13, 0.11), 0.042, 0.1, mat("adder.paper", "#f5f1e2"), axis="X")  # the roll
    for s in (-1, 1):
        m.box((s * 0.06, 0.13, 0.085), (0.008, 0.02, 0.06), dark)
    m.cyl((0.185, 0.03, 0.0), 0.012, 0.06, dark, axis="X")  # the crank
    m.box((0.215, 0.03, 0.04), (0.012, 0.012, 0.09), dark)
    m.cyl((0.215, 0.0, 0.085), 0.012, 0.05, key, axis="Y")
    kit.mesh_swap(o, m.mesh("prop.adder"))


def calendar():
    """S06: the daily tear-off pages (page 0 on top, first to go); the board under them, the 30th ringed."""
    board = obj("dev.cal.board")
    m = mk.MK()
    m.quad((0.004, 0, 0), (0.6, 0.8), img("calboard"), facing="-X")
    m.box((0.012, 0, 0.0), (0.01, 0.66, 0.86), mat("cal.back", "#3a3026"))
    m.cyl((-0.002, 0, 0.44), 0.012, 0.02, mat("cal.nail", "#9a9a9a", metal=0.8, rough=0.3), axis="X")
    kit.mesh_swap(board, m.mesh("prop.calboard"))
    for k in range(10):
        pg = obj(f"calpage{k}")
        m = mk.MK()
        m.quad((-0.003 * (10 - k), 0, 0), (0.6, 0.8), img(f"calpage_{k:02d}"), facing="-X")
        kit.mesh_swap(pg, m.mesh(f"prop.calpage{k}"))


def envelope():
    o = obj("envelope")
    m = mk.MK()
    paper = mat("env", "#f2f0ea")
    m.box((0, 0, 0), (0.22, 0.006, 0.11), paper)
    for face in ("+Y", "-Y"):
        m.quad((0, 0.0035 if face == "+Y" else -0.0035, 0), (0.22, 0.11), img("envelope"), facing=face)
    kit.mesh_swap(o, m.mesh("prop.envelope"))


def notice():
    """S09: the tape, torn into strips and stapled up on his door, the total in red marker."""
    o = obj("notice")
    m = mk.MK()
    m.quad((0, 0.001, 0), (0.5, 0.7), img("receipt"), facing="+Y")
    for x in (-0.16, 0.0, 0.16):  # a staple at the top of each strip
        m.box((x, 0.003, 0.3), (0.04, 0.002, 0.004), mat("staple", "#b4b6ba", metal=0.9, rough=0.3))
    kit.mesh_swap(o, m.mesh("prop.notice"))
    from mathutils import Vector  # flat on the door's street face (it floated 10 cm off it)
    sc = bpy.context.scene
    hit, loc, *_ = sc.ray_cast(bpy.context.evaluated_depsgraph_get(), Vector((-18.94, -8.0, 1.4)), Vector((0, -1, 0)),
                               distance=3.0)
    o.location = (-18.94, (loc.y + 0.004) if hit else -9.9, 1.4)


# the tape's run (S07-S13), waypoints (x, y, zmax): each stretch drapes onto the highest upward-facing surface
# below zmax (the counter, the floor, the threshold, the sidewalk, the street); zmax None = the point's own z (in
# the air, leaving the roll)
TAPE_W, TAPE_TILE = 0.085, 0.34  # 1.5x a real 57 mm tape (the props' scale), the strip texture's tile length


def _bend(cy, cz, r, a0, a1, n=8, x=-20.4):
    """Placed points round an arc in the y-z plane (angles from +y, counter-clockwise toward +z)."""
    return [(x, cy + r * math.cos(a0 + (a1 - a0) * k / n), None, cz + r * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


# off the roll's top (its centre y -13.27, z 1.18, r 0.042), down onto the counter (top 1.0, front edge y -13.1),
# round the edge (an arc about it, 1.3 mm clear of the corner: a straight cut went into the counter), plumb down its
# face, and round onto the floor (0.168)
TAPE_PATH = ([(-20.4, -13.27, None, 1.226), (-20.4, -13.23, None, 1.222), (-20.4, -13.2, None, 1.17),
              (-20.4, -13.18, None, 1.06), (-20.4, -13.165, None, 1.008), (-20.4, -13.14, None, 1.005)]
             + _bend(-13.109, 0.991, 0.014, math.pi / 2, 0.0)
             + _bend(-12.975, 0.293, 0.12, math.pi, 1.5 * math.pi, n=12)
             + [(-20.38, -12.9, 0.3, 0), (-20.2, -12.4, 0.3, 0), (-19.6, -11.4, 0.3, 0), (-19.0, -10.4, 0.3, 0),
             (-18.94, -9.4, 0.3, 0), (-19.3, -8.2, 0.3, 0), (-20.4, -7.65, 0.3, 0), (-26.4, -7.6, 0.3, 0),
             (-27.2, -7.2, 0.3, 0), (-27.5, -5.6, 0.3, 0), (-27.7, -0.7, 0.3, 0), (-27.9, 4.0, 0.3, 0)])
# (the sidewalk stretch at y -7.6: at -7.0 it lay beside the curb's painted line and read as another one)


def tape_points(SP):
    """The run sampled every centimetre and laid like paper (the set as the tape finds it, at S08's middle), 3 mm up.
    Returns [(x, y, z, s)], s the arc length from the roll.

    The surface under it is the highest surface under the tape's whole width: one ray down the middle every 2 cm
    missed narrow things (the sidewalk's joint lines, the rails, litter) and the tape ran under them. Then a 1-D
    relaxation stands in for a cloth simulation: the paper can't bend sharper than a slope (it rides over a joint
    line or a rail in a short ramp, not a step) and is smoothed only upward, so it never goes into what it lies on.
    The stretches in the air (off the roll, over the counter's edge and down its face) keep their placed heights."""
    import numpy as np
    from mathutils import Vector
    sc = bpy.context.scene
    sc.frame_set(gb.F(sum(SP["S08"]) / 2))
    dg = bpy.context.evaluated_depsgraph_get()
    skip = ("tape", "notice", "cassette", "magnifier", "haze", "weeds", "cam.", "door", "recorder", "handset")
    STEP, LIFT, SLOPE, REACH = 0.01, 0.003, 0.5, 30  # m; m; rise per run; samples the slope reaches

    def ground(x, y, zmax):
        org, d = Vector((x, y, zmax)), Vector((0, 0, -1))
        for _ in range(20):
            hit, loc, n, _, ob, _ = sc.ray_cast(dg, org, d, distance=org.z + 1.0)
            if not hit:
                return 0.0
            o = ob.original
            if abs(n.z) > 0.7 and not o.hide_render and not o.name.startswith(skip) and ".door" not in o.name:
                # (some floors' faces point down; a door's underside is not a floor)
                return max(loc.z, 0.0)  # the haze's floor is the road's (z 0): stepping past it skips the road too,
                # and the ray found the far ground 1 cm under it
            org = loc + d * 1e-4
        return 0.0
    raw = []  # (x, y, placed z or None, the ray's start)
    for (x0, y0, zm0, z0), (x1, y1, zm1, z1) in zip(TAPE_PATH, TAPE_PATH[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if zm0 is None:  # placed: toward the next point's placed height, or its surface's if it's laid
            z1 = z1 if zm1 is None else ground(x1, y1, zm1) + LIFT
        n = max(1, int((L if zm0 is not None else math.hypot(L, z1 - z0)) / STEP))
        for i in range(n):
            u = i / n
            raw.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, None if zm0 is not None else z0 + (z1 - z0) * u,
                        zm0 if zm0 is not None else z0 + (z1 - z0) * u + 0.002))
    x, y, zm = TAPE_PATH[-1][:3]
    raw.append((x, y, None, zm))
    N = len(raw)
    xy = np.array([(r[0], r[1]) for r in raw])
    lo = np.zeros(N)
    for i, (x, y, zp, zmax) in enumerate(raw):
        a, b = xy[max(i - 2, 0)], xy[min(i + 2, N - 1)]
        dx, dy = b - a
        L = math.hypot(dx, dy)
        if L > 0.005:
            px, py = -dy / L * TAPE_W / 2, dx / L * TAPE_W / 2
        lo[i] = max(ground(x + px * k, y + py * k, zmax) for k in (-1, -0.5, 0, 0.5, 1)) + LIFT
    laid = np.array([r[2] is None for r in raw])
    d = np.where(laid, lo, -1.0)  # the paper's stiffness, from the laid samples only (not from the counter top)
    for k in range(1, REACH + 1):
        drop = SLOPE * k * STEP
        d[k:] = np.maximum(d[k:], np.where(laid[:-k], lo[:-k], -1.0) - drop)
        d[:-k] = np.maximum(d[:-k], np.where(laid[k:], lo[k:], -1.0) - drop)
    g = np.exp(-0.5 * (np.arange(-6, 7) / 2.0) ** 2)
    sm = np.convolve(np.pad(d, 6, mode="edge"), g / g.sum(), mode="valid")
    z = np.where(laid, np.maximum(lo, np.maximum(d, sm)), [max(r[2], l) if r[2] is not None else 0 for r, l in zip(raw, lo)])
    pts, s = [], 0.0
    for (x, y), zz in zip(xy, z):
        if pts:
            s += math.dist(pts[-1][:3], (x, y, zz))
        pts.append((float(x), float(y), float(zz), s))
    return pts


def tape_run(S, SP):
    """The adding machine's tape as one continuous printed ribbon, revealed by arc length (an empty's ["reveal"],
    metres, keyed by shots.py): S07 spews it off the roll and over the counter; S08 runs it out the door, down the
    sidewalk and across the tracks; it lies there through S13. Replaces the grey-box's stretched box."""
    pts = tape_points(SP)
    me = bpy.data.meshes.new("prop.tape.run")
    V, Fc, UV, ARC = [], [], [], []
    px, py = TAPE_W / 2, 0.0
    for i, (x, y, z, s) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L > 0.002:  # hanging straight down (over the counter's edge) it keeps the last heading's width
            px, py = -dy / L * TAPE_W / 2, dx / L * TAPE_W / 2
        V += [(x - px, y - py, z), (x + px, y + py, z)]
        UV += [(0.0, s / TAPE_TILE), (1.0, s / TAPE_TILE)]
        ARC += [(s, 0.0), (s, 0.0)]
        if i:
            Fc.append((2 * i - 2, 2 * i - 1, 2 * i + 1, 2 * i))
    me.from_pydata(V, [], Fc)
    for name, data in (("UVMap", UV), ("arc", ARC)):
        uvl = me.uv_layers.new(name=name)
        for poly in me.polygons:
            for li in poly.loop_indices:
                uvl.data[li].uv = data[me.loops[li].vertex_index]
    for p in me.polygons:
        p.use_smooth = True
    ctl = gb.empty("tape.ctl", (0, 0, 0))
    ctl["reveal"] = 0.0
    m = bpy.data.materials.new("prop.tape.run")
    m.use_nodes = True
    m.surface_render_method = "DITHERED"
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(GEN / "tape_strip.png"), check_existing=True)
    t.extension = "REPEAT"
    nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.7
    arc = nt.nodes.new("ShaderNodeUVMap")
    arc.uv_map = "arc"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(arc.outputs["UV"], sep.inputs[0])
    val = nt.nodes.new("ShaderNodeValue")
    d = val.outputs[0].driver_add("default_value").driver
    d.type = "SCRIPTED"
    v = d.variables.new()
    v.name, v.type = "r", "SINGLE_PROP"
    v.targets[0].id_type, v.targets[0].id, v.targets[0].data_path = "OBJECT", ctl, '["reveal"]'
    d.expression = "r"
    lt = nt.nodes.new("ShaderNodeMath")
    lt.operation = "LESS_THAN"
    nt.links.new(sep.outputs["X"], lt.inputs[0])
    nt.links.new(val.outputs[0], lt.inputs[1])
    nt.links.new(lt.outputs[0], bsdf.inputs["Alpha"])
    me.materials.append(m)
    o = obj("tape.run")
    o.data = me
    o.location, o.rotation_euler, o.scale = (0, 0, 0), (0, 0, 0), (1, 1, 1)
    o.animation_data_clear()  # the grey-box's stretching keys; its visibility is re-keyed below
    shots.during(o, SP["S07"][0], SP["S13"][1])
    blank(obj("tape.sidewalk"))
    blank(obj("dev.tape"))  # the grey-box's stub of tape at the roll (it showed as a stray scrap)
    S["tape_ctl"], S["tape_len"], S["tape_pts"] = ctl, pts[-1][3], pts
    return ctl


def payphone():
    """The corner payphone (S02, S03, S11, S47), modelled into the grey-box's objects (they keep their places, so the
    cassette's rest on the post's street face and the handset's swing stay as they were): a square steel post on a
    bolted base plate; the armoured housing with its instruction card, coin slot, keypad, coin return and the empty
    hook; a canopy with side panels; the handset (earpiece, grip, mouthpiece) on a coiled cord. Worn: grime on the
    steel, the paint chipped down to the metal round the keypad."""
    steel = mat("pay.steel", "#7d8288", metal=0.75, rough=0.45)
    if not steel.get("grimed"):
        gb.grime(steel, amt=0.55, streak=0.8, damp=0.6)
        steel["grimed"] = 1
    paint = mat("pay.paint", "#2f5d8a", metal=0.2, rough=0.5)  # the housing's blue enamel
    if not paint.get("grimed"):
        gb.grime(paint, amt=0.45, streak=0.7)
        paint["grimed"] = 1
    dark, black = mat("pay.dark", "#16181b", rough=0.6), mat("pay.black", "#0b0b0c", rough=0.35)
    chrome = mat("pay.chrome", "#c6c9cc", metal=0.95, rough=0.2)
    card = mat("pay.card", "#e9e6da", rough=0.8)
    key = mat("pay.key", "#b9bcbf", metal=0.6, rough=0.35)
    # the post (origin at its centre, z 0.9; the street face at +Y 0.075, where the cassette is taped)
    m = mk.MK()
    m.box((0, 0, 0), (0.15, 0.15, 1.8), steel, bevel=0.008, seg=2)
    m.box((0, 0, -0.89), (0.32, 0.32, 0.02), steel, bevel=0.004, seg=1)  # the base plate
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.cyl((sx * 0.12, sy * 0.12, -0.875), 0.012, 0.012, chrome, n=6)  # its bolts
    m.box((0, 0, 0.905), (0.17, 0.17, 0.012), steel, bevel=0.003, seg=1)  # the cap under the housing
    kit.mesh_swap(obj("payphone.post"), m.mesh("prop.pay.post"))
    # the housing (origin at its centre: local (0, 0.05, 1.5) on the post; its face at +Y 0.125)
    m = mk.MK()
    m.box((0, 0, 0), (0.42, 0.25, 0.7), paint, bevel=0.025, seg=3)
    f = 0.125
    m.box((0, f + 0.004, 0.23), (0.34, 0.01, 0.16), steel, bevel=0.004, seg=1)  # the top plate
    m.quad((0, f + 0.0095, 0.23), (0.3, 0.12), card, facing="+Y")  # the instruction card behind it, worn blank
    m.box((0.09, f + 0.012, 0.11), (0.07, 0.018, 0.025), chrome, bevel=0.004, seg=1)  # the coin slot's bezel
    m.box((0.09, f + 0.021, 0.11), (0.04, 0.002, 0.006), black)
    m.box((-0.03, f + 0.006, -0.04), (0.17, 0.014, 0.22), steel, bevel=0.006, seg=1)  # the keypad plate
    for r in range(4):
        for c in range(3):
            m.box((-0.08 + c * 0.05, f + 0.016, 0.04 - r * 0.052), (0.036, 0.012, 0.034), key, bevel=0.004, seg=1)
    m.box((0.12, f + 0.02, -0.25), (0.09, 0.05, 0.08), chrome, bevel=0.01, seg=2)  # the coin return
    m.box((0.12, f + 0.046, -0.255), (0.06, 0.004, 0.05), black)
    # the hook, empty: a chrome lever up the housing's left side, the cradle the handset should be in
    m.box((-0.235, 0.0, 0.08), (0.05, 0.16, 0.36), paint, bevel=0.012, seg=2)
    m.box((-0.265, 0.04, 0.2), (0.02, 0.05, 0.04), chrome, bevel=0.006, seg=1)
    m.tube([(-0.2, f + 0.01, -0.32), (-0.2, f + 0.04, -0.35), (-0.2, f + 0.06, -0.37)], 0.012, steel, k=10)  # cord boot
    kit.mesh_swap(obj("payphone.box"), m.mesh("prop.pay.box"))
    # the canopy (origin at its centre: local (0, 0.1, 1.95)); side panels down past the housing
    m = mk.MK()
    m.box((0, 0, 0), (0.62, 0.46, 0.05), steel, bevel=0.01, seg=2)
    for sx in (-1, 1):
        m.box((sx * 0.3, -0.02, -0.42), (0.018, 0.4, 0.8), paint, bevel=0.006, seg=1)
    kit.mesh_swap(obj("payphone.hood"), m.mesh("prop.pay.hood"))
    # the handset (origin at its centre, hanging; +Y the side that faces the street, where the REC light is)
    m = mk.MK()
    m.box((0, 0, 0), (0.045, 0.035, 0.15), black, bevel=0.012, seg=3)
    for sz in (1, -1):  # earpiece above, mouthpiece below, both cups facing the street
        m.box((0, 0.012, sz * 0.085), (0.06, 0.045, 0.05), black, bevel=0.016, seg=3)
        m.cyl((0, 0.036, sz * 0.085), 0.02, 0.004, dark, axis="Y", n=20)
        for k in range(5):
            m.cyl((-0.008 + k * 0.004, 0.0385, sz * 0.085), 0.0012, 0.002, black, axis="Y", n=6)
    kit.mesh_swap(obj("handset.body"), m.mesh("prop.pay.handset"))
    # the coiled cord, from the housing's boot down to the handset's top (origin at its centre, 0.135 under the boot)
    m = mk.MK()
    for k in range(22):  # the coils, each tipped a little like a helix's turn (mk.tube resamples too coarsely for one)
        m.torus((0, 0, -0.13 + k * 0.0124), 0.012, 0.0035, black, rot=(0.18, 0, 0), n=14, k=6)
    kit.mesh_swap(obj("handset.cord"), m.mesh("prop.pay.cord"))
    recorder(black, dark, chrome)


def recorder(black, dark, chrome):
    """S02-S03, S11: a portable cassette recorder (generic, no maker's name) taped to the post beside the handset, the
    tape behind its window, the REC light on; a thin lead from its mic jack to a suction-cup pickup on the handset's
    back, the way calls were taped. 1.5x a real one, like the tape (origin at its centre; +Y the street)."""
    body = mat("rec.body", "#2a2c2f", rough=0.55)
    gb.grime(body, amt=0.35, space="object") if not body.get("grimed") else None
    body["grimed"] = 1
    tape = mat("rec.tape", "#7d7b76", rough=0.6, metal=0.15)  # grey duct tape
    m = mk.MK()
    W, D, H = 0.19, 0.055, 0.27
    wx, wz0, wz1 = 0.08, -0.0175, 0.0875  # the cassette well's opening (half width; bottom and top)
    m.box((0, -D / 2 + 0.0125, 0), (W, 0.025, H), body, bevel=0.01, seg=2)  # the back half
    fy, fd = -D / 2 + 0.025 + 0.015, 0.03  # the front frame round the well
    m.box((-(wx + (W / 2 - wx) / 2), fy, 0), (W / 2 - wx, fd, H), body, bevel=0.006, seg=1)
    m.box(((wx + (W / 2 - wx) / 2), fy, 0), (W / 2 - wx, fd, H), body, bevel=0.006, seg=1)
    m.box((0, fy, (wz1 + H / 2) / 2), (2 * wx + 0.002, fd, H / 2 - wz1), body, bevel=0.004, seg=1)
    m.box((0, fy, (wz0 - H / 2) / 2), (2 * wx + 0.002, fd, wz0 + H / 2), body, bevel=0.004, seg=1)
    m.box((0, -D / 2 + 0.0255, (wz0 + wz1) / 2), (2 * wx, 0.002, wz1 - wz0), dark)  # the well's floor
    for r in range(4):  # the speaker grille, below the well
        for c in range(9):
            m.box((-0.064 + c * 0.016, D / 2 + 0.0005, -0.065 - r * 0.014), (0.009, 0.002, 0.005), black)
    keys = ["#3a3d41"] * 6
    keys[0] = "#b3261e"  # REC
    for k, col in enumerate(keys):  # the piano keys along the top
        m.box((-0.07 + k * 0.028, 0.004, H / 2 + 0.006), (0.024, 0.034, 0.014), mat(f"rec.key{k}", col, rough=0.5),
              bevel=0.003, seg=1)
    m.cyl((-0.075, 0.0, H / 2 + 0.004), 0.005, 0.008, chrome, n=12)  # the mic jack
    m.box((0.06, D / 2 + 0.001, 0.098), (0.03, 0.002, 0.016), black)  # the REC light's bezel, clear of the tape
    for z, ang in ((0.124, 0.05), (-0.112, -0.05)):  # two bands of tape round it and the post, a little askew
        m.box((0, D / 2 + 0.0015, z), (W + 0.006, 0.003, 0.028), tape, rot=(0, ang, 0))
        m.box((0, -D / 2 - 0.15 - 0.0015, z), (W + 0.006, 0.003, 0.028), tape, rot=(0, ang, 0))
        for s in (-1, 1):
            m.box((s * (W / 2 + 0.0015), -0.075 - 0.0015, z - s * ang * W / 2), (0.003, D + 0.15 + 0.006, 0.028), tape)
    kit.mesh_swap(obj("recorder.body"), m.mesh("prop.recorder"))
    # the well's door: a smoked window in a thin frame, hinged at its bottom edge (S11 opens it)
    m = mk.MK()
    smoke = mat("rec.window", "#2b2a30", rough=0.1)
    smoke.surface_render_method = "DITHERED"
    smoke.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.22
    m.box((0, 0.0, 0.0525), (0.156, 0.002, 0.101), smoke)
    for c, sz in (((0, 0.002, 0.004), (0.162, 0.004, 0.008)), ((0, 0.002, 0.101), (0.162, 0.004, 0.008)),
                  ((-0.077, 0.002, 0.0525), (0.008, 0.004, 0.105)), ((0.077, 0.002, 0.0525), (0.008, 0.004, 0.105))):
        m.box(c, sz, body)
    kit.mesh_swap(obj("recorder.door.glass"), m.mesh("prop.recorder.door"))
    obj("recorder.door.glass").location = (0, 0, 0)
    # the lead, from the jack over to a suction cup on the handset's back, in the handset's (swinging) frame
    hp, rc = B.HANDSET_PIVOT, B.RECORDER
    jack = (rc[0] - 0.075 - hp[0], rc[1] - hp[1], rc[2] + H / 2 + 0.008 - hp[2])
    cup = (0.0, -0.0215, -B.HANDSET_DROP + 0.06)
    mid1 = (jack[0] - 0.01, jack[1] + 0.02, jack[2] + 0.03)
    mid2 = ((jack[0] + cup[0]) / 2, (jack[1] + cup[1]) / 2 - 0.01, (jack[2] + cup[2]) / 2 - 0.05)
    m = mk.MK()
    m.tube([jack, mid1, mid2, (cup[0] + 0.005, cup[1] - 0.012, cup[2] + 0.004), (cup[0], cup[1] - 0.004, cup[2])],
           0.0018, black, k=6)
    m.cyl(cup, 0.012, 0.006, mat("rec.cup", "#3b3e42", rough=0.4), axis="Y", n=16)
    lead = gb.link(bpy.data.objects.new("handset.lead", m.mesh("prop.recorder.lead")), obj("handset"))


CASS_S = 1.5  # the cassette at 1.5x a real one (100 x 64 x 12 mm): it's the evidence, it has to read at 720p


def cassette():
    """A compact cassette, both faces: the shell, five screws, the label (its window cut out) over a smoked window
    with the two tape packs (one full, one nearly empty) and toothed hubs, the trapezoid at the bottom with the head
    openings."""
    o = obj("cassette")
    m = mk.MK()
    shell = mat("cass.shell", "#2b2d33", rough=0.35)
    smoke, tape = mat("cass.smoke", "#141517", rough=0.15), mat("cass.tape", "#4a2e1c", rough=0.5)
    white, dark = mat("cass.hub", "#e8e8e8", rough=0.4), mat("cass.hole", "#0b0b0c", rough=0.6)
    steel = mat("cass.screw", "#a9abb0", metal=0.9, rough=0.3)
    m.box((0, 0, 0), (0.1004, 0.012, 0.0638), shell, bevel=0.0015, seg=1)
    label = mk.img_mat("prop.img.cassette", GEN / "cassette.png", rough=0.7, alpha=True)
    hz = 0.003  # the hubs' and window's height on the face
    for sg, face in ((1, "+Y"), (-1, "-Y")):
        y = sg * 0.006
        m.quad((0, y + sg * 0.0002, hz), (0.054, 0.017), smoke, facing=face)
        for x, r in ((-0.0213, 0.0215), (0.0213, 0.0115)):  # the tape packs: side A played most of the way
            m.cyl((x, y + sg * 0.0004, hz), r, 0.0002, tape, axis="Y", n=40)
            m.cyl((x, y + sg * 0.0007, hz), 0.0065, 0.0004, white, axis="Y", n=24)
            m.cyl((x, y + sg * 0.0010, hz), 0.0042, 0.0003, dark, axis="Y", n=20)
            for k in range(6):  # the hub's teeth
                a = k * math.pi / 3
                m.box((x + 0.0034 * math.cos(a), y + sg * 0.0012, hz + 0.0034 * math.sin(a)), (0.0014, 0.0003, 0.0014),
                      white, rot=(0, -a, 0))
        m.quad((0, y + sg * 0.0016, 0.006), (0.09, 0.042), label, facing=face)
        # the trapezoid below the label, with the head opening and the capstan holes
        m.prism([(-0.0365, -0.0319), (0.0365, -0.0319), (0.03, -0.0165), (-0.03, -0.0165)], 0.0009, shell,
                c=(0, y + sg * 0.00045, 0))
        m.quad((0, y + sg * 0.001, -0.027), (0.012, 0.004), dark, facing=face)
        for s in (-1, 1):
            m.cyl((s * 0.0175, y + sg * 0.001, -0.026), 0.0018, 0.0002, dark, axis="Y", n=12)
        for sx, sz in ((-0.046, 0.0275), (0.046, 0.0275), (-0.046, -0.0275), (0.046, -0.0275), (0, -0.021)):
            m.cyl((sx, y + sg * (0.0013 if sz > -0.021 else 0.0013), sz), 0.0014, 0.0004, steel, axis="Y", n=10)
    me = m.mesh("prop.cassette")
    me.transform(__import__("mathutils").Matrix.Scale(CASS_S, 4))
    kit.mesh_swap(o, me)


def boombox():
    o = obj("boombox")
    kit.swap(o, "boombox", scale=0.85, offset=(0, 0, -0.15), rot=(0, 0, math.pi))


def magnifier():
    o = obj("magnifier")
    reset_rot(o)
    s = 1.8
    zc = (kit.dims("magnifying_glass_01").z - 0.066) * s
    kit.swap(o, "magnifying_glass_01", scale=s, offset=(0, zc, 0), rot=(math.pi / 2, 0, 0))
    for m in o.data.materials:  # the lens: clear glass, seen through (as transmission, Eevee rendered it black)
        if m and "lense" in m.name:
            m.surface_render_method = "BLENDED"
            b = m.node_tree.nodes.get("Principled BSDF")
            if b:
                for l in list(b.inputs["Alpha"].links):
                    m.node_tree.links.remove(l)
                b.inputs["Transmission Weight"].default_value = 0.0
                b.inputs["Roughness"].default_value = 0.03
                b.inputs["Alpha"].default_value = 0.12


# ---------------------------------------------------------------- vehicles

def vehicle(name, L, W, H, colour, kind="van", front=-1, open_side=False, roof_hatch=False):
    """A van or box truck in the grey-box box's frame (centred, L x W x H, ground at -H/2), nose toward x*front."""
    m = mk.MK()
    paint = mat(f"veh.{name}", colour, rough=0.45, metal=0.2)
    gb.grime(paint, amt=0.35, damp=0.6) if not paint.get("grimed") else None
    paint["grimed"] = 1
    glass, tyre, rim = mat("veh.glass", "#0d1218", rough=0.08), mat("veh.tyre", "#141414", rough=0.85), \
        mat("veh.rim", "#9a9ea4", metal=0.8, rough=0.35)
    trim, lamp, tail = mat("veh.trim", "#1c1d1f", rough=0.6), mat("veh.lamp", "#fff1cc", emit=1.5), \
        mat("veh.tail", "#5a2a10", emit=0.4)
    g = -H / 2
    wr = 0.38 if kind == "truck" else 0.34
    clear = wr + 0.1
    f = front
    if kind == "van":
        # side profile, seen from -Y, nose at -L/2 (mirrored for front=+1)
        prof = [(-L / 2, g + clear), (L / 2, g + clear), (L / 2, H / 2 - 0.1), (-L / 2 + 1.0, H / 2 - 0.1),
                (-L / 2 + 0.25, g + clear + 0.95), (-L / 2, g + clear + 0.85)]
        if f > 0:
            prof = [(-x, z) for x, z in reversed(prof)]
        m.prism(prof, W, paint, bevel=0.05)
        # windscreen and cab windows
        ax, az = -L / 2 + 0.25, g + clear + 0.98
        bx, bz = -L / 2 + 0.98, H / 2 - 0.16
        ang = math.atan2(bz - az, bx - ax)
        mx, mz = (ax + bx) / 2 * -f * -1, (az + bz) / 2
        mx = (ax + bx) / 2 if f < 0 else -(ax + bx) / 2
        m.box((mx - 0.012 * f, 0, mz), (math.hypot(bx - ax, bz - az) * 0.92, W - 0.2, 0.02), glass,
              rot=(0, ang if f < 0 else -ang, 0))
        for s in (-1, 1):
            cx = (-L / 2 + 1.25) * -f
            m.box((cx, s * (W / 2 + 0.002), H / 2 - 0.45), (0.75, 0.01, 0.5), glass)
            m.box(((-L / 2 + 0.5) * -f, s * (W / 2 + 0.12), g + clear + 0.95), (0.06, 0.2, 0.14), trim)  # mirrors
        nose_x = (-L / 2) * -f
        top_light = g + clear + 0.55
    else:
        cab_l = 1.9
        bx0, bx1 = (-L / 2, L / 2 - cab_l - 0.1) if f > 0 else (-L / 2 + cab_l + 0.1, L / 2)
        z0b, z1b = g + clear + 0.1, H / 2  # the box body's floor and roof
        if not open_side:
            m.box(((bx0 + bx1) / 2, 0, (z0b + z1b) / 2), (bx1 - bx0, W, z1b - z0b), paint, bevel=0.03)
        else:  # a hollow box with a real door opening on -Y, so the lot stays in sight (in shadow) once it's loaded
            t = 0.05
            dx0, dx1 = bx0 + 1.6 - 0.9, bx0 + 1.6 + 0.9
            dz0, dz1 = z0b + t, (z0b + z1b) / 2 - 0.1 + 0.95  # the opening down to the hold's floor
            xm, ln = (bx0 + bx1) / 2, bx1 - bx0
            for c, sz in ((((xm, 0, z0b + t / 2)), (ln, W, t)), ((xm, 0, z1b - t / 2), (ln, W, t)),  # floor, roof
                          ((bx0 + t / 2, 0, (z0b + z1b) / 2), (t, W, z1b - z0b)),  # the two ends
                          ((bx1 - t / 2, 0, (z0b + z1b) / 2), (t, W, z1b - z0b)),
                          ((xm, W / 2 - t / 2, (z0b + z1b) / 2), (ln, t, z1b - z0b)),  # the far side
                          (((bx0 + dx0) / 2, -W / 2 + t / 2, (z0b + z1b) / 2), (dx0 - bx0, t, z1b - z0b)),  # round the door
                          (((dx1 + bx1) / 2, -W / 2 + t / 2, (z0b + z1b) / 2), (bx1 - dx1, t, z1b - z0b)),
                          (((dx0 + dx1) / 2, -W / 2 + t / 2, (dz1 + z1b) / 2), (dx1 - dx0, t, z1b - dz1))):
                m.box(c, sz, paint)
            inner = mat("veh.inner", "#8a8478", rough=0.85)  # the hold's lining: scuffed grey, darker than the paint
            m.box((xm, 0, z0b + t + 0.005), (ln - 2 * t, W - 2 * t, 0.01), mat("veh.holdfloor", "#4a4038", rough=0.9))
            m.box((xm, W / 2 - t - 0.005, (z0b + z1b) / 2), (ln - 2 * t, 0.01, z1b - z0b - 2 * t), inner)
            for x in (bx0 + t + 0.005, bx1 - t - 0.005):
                m.box((x, 0, (z0b + z1b) / 2), (0.01, W - 2 * t - 0.02, z1b - z0b - 2 * t), inner)
            m.box(((dx0 + dx1) / 2, -W / 2 - 0.004, dz1 + 0.06), (dx1 - dx0 + 0.08, 0.02, 0.12), mat("veh.trim2", "#8d9196", metal=0.6, rough=0.4))  # the rolled-up door's drum
        cx0 = bx1 + 0.1 if f > 0 else -L / 2
        cx1 = L / 2 if f > 0 else bx0 - 0.1
        ch = 2.3
        prof = [(0, g + clear), (cab_l, g + clear), (cab_l, g + clear + 1.0), (cab_l - 0.35, g + ch),
                (0, g + ch)]
        if f < 0:
            prof = [(-x + cab_l, z) for x, z in reversed(prof)]
        m.prism([(cx0 + x, z) for x, z in prof], W - 0.1, mat("veh.cab", "#e9e9e6", rough=0.45), bevel=0.04)
        wx = cx1 - 0.2 if f > 0 else cx0 + 0.2
        m.box((wx, 0, g + clear + 1.45), (0.05, W - 0.3, 0.6), glass, rot=(0, -0.3 * f, 0))
        for s in (-1, 1):
            m.box(((cx0 + cx1) / 2 + 0.15 * f, s * (W / 2 - 0.04), g + clear + 1.45), (0.8, 0.01, 0.5), glass)
            m.box((cx1 - 0.3 if f > 0 else cx0 + 0.3, s * (W / 2 + 0.1), g + clear + 1.4), (0.06, 0.15, 0.25), trim)
        m.box(((bx0 + bx1) / 2, 0, g + clear + 0.05), (bx1 - bx0, W - 0.2, 0.12), trim)  # the chassis rail
        if roof_hatch:
            m.box(((bx0 + bx1) / 2, 0, H / 2 + 0.005), (1.2, 1.2, 0.01), mat("veh.hold", "#060606", rough=0.9))
        rear_x = bx0 if f > 0 else bx1
        for k in range(5):  # the roll-up door's ribs at the back
            m.box((rear_x - 0.01 * f, 0, g + clear + 0.3 + k * 0.42), (0.02, W - 0.2, 0.03), trim)
        nose_x = cx1 if f > 0 else cx0
        top_light = g + clear + 0.55
    # wheels, bumpers, lights
    wx = [L / 2 - 0.85, -L / 2 + 0.85] if kind == "van" else [L / 2 - 0.9, -L / 2 + 1.0, -L / 2 + 2.0]
    for x in wx:
        for s in (-1, 1):
            m.cyl((x, s * (W / 2 - 0.12), g + wr), wr, 0.26, tyre, axis="Y", n=20)
            m.cyl((x, s * (W / 2 - 0.0), g + wr), wr * 0.55, 0.02, rim, axis="Y", n=16)
            m.box((x, s * (W / 2 + 0.01), g + wr + 0.08), (wr * 2.4, 0.04, wr * 1.3), trim)  # the wheel arch
    for x in (nose_x, -nose_x):
        m.box((x, 0, g + clear + 0.05), (0.12, W + 0.04, 0.22), trim, bevel=0.03)
    for s in (-1, 1):
        m.box((nose_x + 0.01 * (-1 if nose_x < 0 else 1), s * (W / 2 - 0.25), top_light), (0.04, 0.26, 0.14), lamp)
        m.box((-nose_x - 0.01 * (-1 if nose_x < 0 else 1), s * (W / 2 - 0.15), top_light), (0.04, 0.14, 0.22), tail)
    return m.mesh(f"prop.{name}")


def label_both_sides(o):
    """The grey-box lettered one side (+Y); the cameras see some vehicles from -Y: letter that side too."""
    for t in [c for c in o.children if c.type == "FONT"]:
        t2 = t.copy()
        t2.data = t.data.copy()
        bpy.context.scene.collection.objects.link(t2)
        t2.parent = o
        t2.name = t.name + ".far"
        t2.location = (t.location.x, -t.location.y, t.location.z)
        t2.rotation_euler = (t.rotation_euler.x, t.rotation_euler.y, t.rotation_euler.z + math.pi)


def vehicles():
    v = obj("van")
    kit.mesh_swap(v, vehicle("van", 5.0, 2.1, 2.2, "#d9d9d4", "van", front=-1))
    av = obj("archivevan")
    kit.mesh_swap(av, vehicle("archivevan", 4.0, 2.0, 2.0, "#c8cdd2", "van", front=1))
    label_both_sides(av)
    for nm, open_side, hatch in (("truck28", True, False), ("truck.SEARCH", False, False), ("truck.CHAT", False, False),
                                 ("truck31", False, True)):
        o = obj(nm)
        sx, sy, sz = (o.dimensions.x, o.dimensions.y, o.dimensions.z)
        kit.mesh_swap(o, vehicle(nm.replace(".", "_"), sx, sy, sz, "#ecebe6", "truck", front=1, open_side=open_side,
                                 roof_hatch=hatch))
        label_both_sides(o)


def crates():
    wood = gb.tex_mat("crate_wood", "plywood")
    for k in range(6):
        o = obj(f"crate{k}")
        m = mk.MK()
        w, d, h = 0.8, 0.8, 0.6
        for z in (-0.22, 0.0, 0.22):  # slats on four sides with gaps
            for s in (-1, 1):
                m.box((0, s * (d / 2 - 0.01), z), (w, 0.02, 0.15), wood)
                m.box((s * (w / 2 - 0.01), 0, z), (0.02, d - 0.04, 0.15), wood)
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.box((sx * (w / 2 - 0.03), sy * (d / 2 - 0.03), 0), (0.06, 0.06, h), wood)
        m.box((0, 0, -h / 2 + 0.01), (w, d, 0.02), wood)
        m.box((0, 0, h / 2 - 0.05), (w - 0.06, d - 0.06, 0.06), mat("crate.fill", "#2a2622", rough=0.9))  # the contents
        kit.mesh_swap(o, m.mesh(f"prop.crate{k}"))


# ---------------------------------------------------------------- verse 2

def arrows():
    """S22: generic down arrows in a downvote's blue-purple (the human's note at M4; the shape is generic, not the
    site's), lit a little from within so the colour holds at night."""
    out = [(-0.3, 0.8), (-0.3, 0.0), (-0.6, 0.0), (0.0, -0.8), (0.6, 0.0), (0.3, 0.0), (0.3, 0.8)]
    m = mk.MK()
    m.prism(out, 0.3, mat("arrow", "#8f8fff", rough=0.35, emit=0.6), bevel=0.04)
    me = m.mesh("prop.arrow")
    for o in bpy.data.objects:
        if o.name.startswith("arrow") and o.type == "MESH":
            kit.mesh_swap(o, me)


def hoses():
    """S23: ribbed vacuum hoses from each VIP bot's back, sagging into the shop's mail slot."""
    hose, nozzle = mat("hose", "#222428", rough=0.55), mat("hose.noz", "#8a8f96", metal=0.7, rough=0.35)
    for k in range(4):
        o = obj(f"hose{k}")
        if not o:
            continue
        reset_rot(o)
        m = mk.MK()
        m.tube([(0, 0.2, 0.25), (0, 0.05, -0.1), (0, -0.22, -0.12), (0, -0.38, -0.01)], 0.05, hose, rib=0.006, rib_n=28)
        m.cyl((0, -0.4, 0.0), 0.055, 0.06, nozzle, axis="Y", r2=0.035)
        m.cyl((0, 0.22, 0.27), 0.07, 0.06, nozzle, axis="Y")
        kit.mesh_swap(o, m.mesh(f"prop.hose{k}"))


def brickwall(SP):
    """S24: the wall goes up course by course (bands of four courses), in place of the grey-box's stretched box."""
    w = obj("brickwall")
    blank(w)
    brick = gb.tex_mat("brick_laid", "brick_4")
    x0, y0, _ = B.LOBBY_DOOR_X, B.TOWER_Y[0] - 0.3, 0
    a, b = SP["S24"]
    n = 10
    for k in range(n):
        m = mk.MK()
        m.box((x0, y0, (k + 0.5) * 0.3), (3.6, 0.35, 0.3), brick)
        o = gb.link(bpy.data.objects.new(f"brickwall.band{k}", m.mesh(f"prop.brickband{k}")))
        gb.show_from(o, a + (k + 1) * (b - a) / (n + 1))
    m = mk.MK()  # the mortar line along the top of each band and the fresh mortar smears
    mortar = mat("mortar", "#b9b2a6", rough=0.95)
    m.box((x0, y0 - 0.18, 3.0), (3.6, 0.02, 0.02), mortar)
    o = gb.link(bpy.data.objects.new("brickwall.cap", m.mesh("prop.brickcap")))
    gb.show_from(o, b - 0.01)


def briefcase():
    o = obj("case25")
    m = mk.MK()
    leather, gold = mat("case", "#151517", rough=0.4), mat("case.gold", gb.LOOK["palette"]["gold"], metal=0.9, rough=0.3)
    m.box((0, 0, 0), (0.42, 0.1, 0.3), leather, bevel=0.015)
    for s in (-1, 1):
        m.box((s * 0.12, -0.052, 0.12), (0.04, 0.01, 0.025), gold)
        m.box((s * 0.07, 0, 0.165), (0.015, 0.02, 0.04), gold)
    m.torus((0, 0, 0.17), 0.06, 0.011, leather, rot=(math.pi / 2, 0, 0), arc=math.pi, n=12)
    kit.mesh_swap(o, m.mesh("prop.case"))


def keys25():
    """S25: the keys the CEO hands back, oversized (it's a cartoon deal; at 720p, side-on, real ones are a few pixels):
    a ring, three keys of different cuts hanging from it, and a brass tag."""
    o = obj("keys25")
    if not o:
        return
    brass = mat("keys.brass", gb.LOOK["palette"]["gold"], metal=0.9, rough=0.25)
    steel = mat("keys.steel", "#b8bcc2", metal=0.9, rough=0.3)
    m = mk.MK()
    m.torus((0, 0, 0.06), 0.045, 0.006, steel, rot=(math.pi / 2, 0, 0), n=24, k=8)  # the ring, face to the side
    for k, (dx, ang, mt) in enumerate(((-0.03, 0.35, brass), (0.0, 0.0, steel), (0.03, -0.35, brass))):
        c = (dx, 0, -0.02)
        rot = (0, ang, 0)
        m.torus((dx + 0.02 * math.sin(ang), 0, 0.02), 0.022, 0.006, mt, rot=(math.pi / 2, ang, 0), n=16, k=6)  # bow
        m.box((dx - 0.06 * math.sin(ang), 0, -0.05), (0.014, 0.008, 0.12), mt, rot=rot)  # shaft
        for j in range(3):  # the cut
            m.box((dx - (0.09 + j * 0.02) * math.sin(ang) + 0.012 * math.cos(ang), 0,
                   -0.085 - j * 0.02 * math.cos(ang)), (0.014, 0.008, 0.01 + 0.006 * ((j + k) % 2)), mt, rot=rot)
    m.box((0.06, 0, 0.0), (0.05, 0.006, 0.08), brass, rot=(0, -0.5, 0), bevel=0.004, seg=1)  # the tag
    me = m.mesh("prop.keys25")
    me.transform(__import__("mathutils").Matrix.Scale(2.8, 4))
    kit.mesh_swap(o, me)


def balcony_rail():
    """The balcony's rail was an opaque box hiding the CEO from below (S22): clear glass between steel posts."""
    o = obj("balcony.rail")
    m = mk.MK()
    steel = mat("rail.steel", "#c9ced4", metal=0.9, rough=0.25)
    m.box((0, 0, 0), (12, 0.02, 0.85), gb.mat("glass_rail", "#cfe6ff", rough=0.03, alpha=0.08))
    m.box((0, 0, 0.47), (12.1, 0.07, 0.05), steel, bevel=0.01)
    for k in range(7):
        m.box((-6 + k * 2, 0, 0), (0.05, 0.05, 0.95), steel)
    kit.mesh_swap(o, m.mesh("prop.rail"))


def balcony_light():
    """The balcony (S22, S23, S30) was near black: the tower's own cold light from above it, all night."""
    ld = bpy.data.lights.new("balcony.light", "SPOT")
    ld.energy, ld.spot_size, ld.spot_blend = 2600, math.radians(70), 0.5
    ld.color = gb.lin(gb.LOOK["palette"]["corporate"])[:3]
    lo = gb.link(bpy.data.objects.new("balcony.light", ld))
    lo.location = (B.LOBBY_DOOR_X + 1.5, B.TOWER_Y[0] - 5.0, 13.5)
    lo.rotation_euler = gb.look_rot(lo.location, (B.LOBBY_DOOR_X + 1.5, B.TOWER_Y[0] - 1.2, 8.3))
    gb.keys(ld, "energy", [(0, 0.0, "CONSTANT"), (gb.F(0.14), 2600.0, "CONSTANT")], interp="CONSTANT")


# ---------------------------------------------------------------- verse 3

def bell():
    body = obj("bell.body")
    m = mk.MK()
    gold, iron = mat("bell", gb.LOOK["palette"]["gold"], metal=0.95, rough=0.28), mat("bell.iron", "#2a2826", metal=0.6)
    prof = [(0.0, 0.27), (0.1, 0.27), (0.17, 0.24), (0.2, 0.15), (0.22, 0.0), (0.27, -0.13), (0.36, -0.22),
            (0.38, -0.25), (0.33, -0.25)]
    m.lathe(prof, gold, n=36)
    m.lathe([(0.32, -0.25), (0.19, 0.12), (0.0, 0.2)], gold, n=36)  # the inside
    m.cyl((0, 0, 0.3), 0.04, 0.08, iron)
    m.cyl((0, 0, -0.08), 0.012, 0.3, iron)
    m.sphere((0, 0, -0.23), 0.04, iron)
    kit.mesh_swap(body, m.mesh("prop.bell"))
    fr = obj("bell.frame")
    m = mk.MK()
    for s in (-1, 1):
        m.box((s * 0.55, 0, -0.05), (0.08, 0.08, 2.2), iron, bevel=0.01)
    m.box((0, 0, 1.0), (1.26, 0.1, 0.1), iron, bevel=0.01)
    m.box((0, 0, -1.12), (1.4, 0.4, 0.06), iron)
    kit.mesh_swap(fr, m.mesh("prop.bellframe"))


def podium():
    o = obj("podium")
    m = mk.MK()
    white, strip = mat("podium", "#eef1f4", rough=0.25), mat("podium.strip", "#e6f2ff", emit=5.0)
    m.box((0, 0, -0.5), (0.7, 0.5, 0.06), white, bevel=0.01)
    m.prism([(-0.25, -0.47), (0.25, -0.47), (0.33, 0.45), (-0.33, 0.45)], 0.42, white, rot=(0, 0, 0), bevel=0.01)
    m.box((0, -0.03, 0.52), (0.8, 0.5, 0.05), white, rot=(0.25, 0, 0), bevel=0.01)
    m.box((0, -0.22, 0.1), (0.5, 0.01, 0.02), strip)
    m.tube([(0, 0.05, 0.55), (0, -0.02, 0.75), (0, -0.12, 0.82)], 0.006, mat("mic", "#222222", metal=0.6))
    m.cyl((0, -0.13, 0.83), 0.018, 0.05, mat("mic", "#222222", metal=0.6), axis="Y")
    kit.mesh_swap(o, m.mesh("prop.podium"))


def banner():
    o = obj("banner")
    m = mk.MK()
    m.box((0, 0, -2.5), (5.0, 0.02, 5.0), mat("banner", "#f2efe6", rough=0.9))
    m.cyl((0, 0, 0.03), 0.04, 5.3, mat("banner.rod", gb.LOOK["palette"]["gold"], metal=0.9, rough=0.3), axis="X")
    m.cyl((0, 0, -5.0), 0.03, 5.1, mat("banner.rod", gb.LOOK["palette"]["gold"], metal=0.9, rough=0.3), axis="X")
    kit.mesh_swap(o, m.mesh("prop.banner"))


def stickies():
    r = random.Random(31)
    for k in range(10):
        o = obj(f"sticky{k}")
        if not o:
            continue
        m = mk.MK()
        m.quad((0, 0.002, 0), (0.3, 0.3), img(f"sticky_{k:02d}", 0.7), facing="+Y", rot=(0, r.uniform(-0.12, 0.12), 0))
        kit.mesh_swap(o, m.mesh(f"prop.sticky{k}"))


def funnel():
    o = obj("funnel")
    m = mk.MK()
    steel = mat("funnel", "#9aa1a8", metal=0.8, rough=0.35)
    m.lathe([(0.75, 0.6), (0.72, 0.55), (0.14, -0.25), (0.12, -0.6)], steel, n=32)
    m.lathe([(0.11, -0.6), (0.13, -0.25), (0.7, 0.55)], mat("funnel.in", "#3a3d40", metal=0.6), n=32)
    m.torus((0, 0, 0.6), 0.75, 0.025, steel, n=32)
    kit.mesh_swap(o, m.mesh("prop.funnel"))


def brooms(SP):
    r = random.Random(32)
    for k in range(5):
        o = obj(f"broomstack{k}")
        kit.swap(o, "wooden_broom", scale=0.95, offset=(0, 0, -0.68), rot=(r.uniform(-0.06, 0.06), r.uniform(-0.05, 0.05),
                                                                              r.uniform(0, math.pi)))
    cr = kit.place("broomstack.crate", "plastic_crate_02", (-7.8, -6.3, 0.15), rot_z=0.1)
    shots.only(cr, "S32")


def payroll():
    o = obj("payroll")
    m = mk.MK()
    m.box((0, 0, 0), (0.24, 0.12, 0.004), mat("payroll", "#c4a070"))
    m.quad((0, 0, 0.0025), (0.24, 0.12), img("payroll"), facing="+Z")
    kit.mesh_swap(o, m.mesh("prop.payroll"))


def rubberband():
    o = obj("rubberband")
    reset_rot(o)
    m = mk.MK()
    m.torus((0, 0, 0), 0.04, 0.003, mat("band", "#c79a5c", rough=0.6), n=24, k=6)
    kit.mesh_swap(o, m.mesh("prop.band"))


def chalk(S, SP):
    cx, cy = S["chalk_sq"]
    m = mk.MK()
    ch = mat("chalk", "#ecebe4", rough=1.0)
    h = 0.72
    for (x, y, sx, sy) in ((cx, cy - h, 2 * h, 0.03), (cx, cy + h, 2 * h, 0.03), (cx - h, cy, 0.03, 2 * h),
                           (cx + h, cy, 0.03, 2 * h)):
        m.box((x, y, 0.1515), (sx, sy, 0.002), ch)
    o = gb.link(bpy.data.objects.new("yourland.square", m.mesh("prop.chalk")))
    gb.show_between(o, *SP["S33"])
    t = obj("yourland")
    if t:
        t.data.materials.clear()
        t.data.materials.append(ch)


# ---------------------------------------------------------------- the eulogy

def coffin():
    cardboard, tissue = mat("shoebox", "#c9a46e", rough=0.85), mat("tissue", "#f3efe8", rough=0.95)
    o = obj("coffin")
    m = mk.MK()
    w, d, h, t = 0.7, 0.35, 0.16, 0.008
    m.box((0, 0, -h / 2 + t / 2), (w, d, t), cardboard)
    for s in (-1, 1):
        m.box((0, s * (d / 2 - t / 2), 0), (w, t, h), cardboard)
        m.box((s * (w / 2 - t / 2), 0, 0), (t, d, h), cardboard)
    r = random.Random(33)
    for k in range(14):  # crumpled tissue paper
        m.sphere((r.uniform(-0.3, 0.3), r.uniform(-0.13, 0.13), -0.03), r.uniform(0.04, 0.07), tissue,
                 s=(1.4, 1.0, 0.45), u=8, v=5)
    # the lid, leaning on the crates' front
    m.box((0.0, -0.32, -0.32), (0.74, 0.012, 0.4), cardboard, rot=(0.25, 0, 0))
    m.box((0.0, -0.3, -0.13), (0.74, 0.05, 0.012), cardboard, rot=(0.25, 0, 0))
    kit.mesh_swap(o, m.mesh("prop.coffin"))
    bot = obj("coffin.bot")
    m = mk.MK()
    cream, blue, dark = mat("tiny.body", "#e9e1cf", rough=0.5), mat("tiny.head", "#9fc3d6", rough=0.5), \
        mat("tiny.eye", "#101012")
    m.sphere((0.03, 0, 0), 0.06, cream, s=(1.6, 1.0, 0.7))
    m.box((-0.12, 0, 0.005), (0.07, 0.08, 0.06), blue, bevel=0.01)
    for s in (-1, 1):
        m.box((-0.12, s * 0.02, 0.037), (0.012, 0.012, 0.004), dark)  # eyes closed: two short dashes
        m.cyl((0.04, s * 0.06, 0.0), 0.01, 0.1, mat("tiny.arm", "#8a8a8a", metal=0.7), axis="X")
    m.cyl((-0.17, 0, 0.005), 0.003, 0.05, mat("tiny.arm", "#8a8a8a", metal=0.7), axis="X")
    kit.mesh_swap(bot, m.mesh("prop.tinybot"))
    st = obj("coffin.stand")
    m = mk.MK()
    wood = gb.tex_mat("crate_wood", "plywood")
    for s in (-1, 1):  # two crates
        cx = s * 0.23
        for z in (-0.2, 0.0, 0.2):
            m.box((cx, -0.24, z), (0.43, 0.02, 0.13), wood)
            m.box((cx, 0.24, z), (0.43, 0.02, 0.13), wood)
            m.box((cx + s * 0.2, 0, z), (0.02, 0.46, 0.13), wood)
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.box((cx + sx * 0.19, sy * 0.21, 0), (0.05, 0.05, 0.6), wood)
        m.box((cx, 0, 0.29), (0.43, 0.48, 0.02), wood)
    kit.mesh_swap(st, m.mesh("prop.coffinstand"))
    for k in range(10):  # the "good bot" notes on the coffin's front
        n = obj(f"note{k}")
        if not n:
            continue
        m = mk.MK()
        m.quad((0, -0.004, 0), (0.1, 0.1), img(f"goodbot_{k:02d}", 0.7), facing="-Y",
               rot=(0, random.Random(k).uniform(-0.15, 0.15), 0))
        kit.mesh_swap(n, m.mesh(f"prop.note{k}"))


def ball():
    """S20: a basketball, orange with its black seams (two great circles and the curved pair)."""
    o = obj("ball")
    m = mk.MK()
    R = 0.12
    m.sphere((0, 0, 0), R, mat("ball.rubber", "#c9622a", rough=0.75), u=32, v=20)
    seam = mat("ball.seam", "#151515", rough=0.6)
    m.torus((0, 0, 0), R * 1.004, 0.0035, seam, n=48, k=6)
    m.torus((0, 0, 0), R * 1.004, 0.0035, seam, rot=(math.pi / 2, 0, 0), n=48, k=6)
    for s in (-1, 1):  # the curved seams: small circles round each pole of the third axis
        m.torus((s * R * 0.62, 0, 0), R * 0.79, 0.0035, seam, rot=(0, math.pi / 2, 0), n=40, k=6)
    kit.mesh_swap(o, m.mesh("prop.ball"))


def forklift():
    """S28: a small warehouse forklift, facing +Y: the body and counterweight, the overhead guard, seat and wheel,
    four wheels, the mast's two rails at the front; the carriage (its own object, keyed up and down) gets the backrest
    and the two forks."""
    body = obj("forklift28.body")
    m = mk.MK()
    paint, dark = mat("fl.paint", "#e0a21a", rough=0.5), mat("fl.dark", "#1d1e20", rough=0.6)
    tyre, steel = mat("veh.tyre", "#141414", rough=0.85), mat("fl.steel", "#6f7378", metal=0.8, rough=0.35)
    seat = mat("fl.seat", "#121212", rough=0.7)
    gb.grime(paint, amt=0.4, damp=0.6) if not paint.get("grimed") else None
    paint["grimed"] = 1
    m.box((0, -0.15, -0.25), (1.05, 1.5, 0.55), paint, bevel=0.04)  # the body (origin at its box's centre, z 0.6)
    m.box((0, -0.82, -0.05), (1.05, 0.38, 0.75), dark, bevel=0.06)  # the counterweight at the back
    m.box((0, 0.35, -0.02), (0.9, 0.5, 0.12), dark)  # the floor plate
    m.box((0, -0.25, 0.15), (0.5, 0.45, 0.12), seat, bevel=0.03)
    m.box((0, -0.45, 0.42), (0.5, 0.1, 0.45), seat, bevel=0.03)  # the seat back
    m.cyl((0, 0.32, 0.62), 0.16, 0.03, dark, rot=(0.9, 0, 0), n=20)  # the steering wheel
    m.cyl((0, 0.27, 0.45), 0.02, 0.4, dark, rot=(0.9, 0, 0), n=8)
    for x in (-0.48, 0.48):  # the overhead guard
        for y in (-0.6, 0.55):
            m.box((x, y, 0.85), (0.06, 0.06, 1.3), dark)
    m.box((0, -0.02, 1.5), (1.02, 1.2, 0.05), dark)
    for k in range(5):
        m.box((0, -0.5 + k * 0.24, 1.53), (0.98, 0.03, 0.02), dark)
    for x in (-0.42, 0.42):  # the mast's rails, up the front
        m.box((x, 1.0, 0.55), (0.08, 0.1, 2.3), steel)
    m.box((0, 1.0, 1.66), (0.92, 0.1, 0.08), steel)
    for y, r in ((0.7, 0.3), (-0.7, 0.24)):
        for x in (-0.52, 0.52):
            m.cyl((x, y, -0.6 + r), r, 0.22, tyre, axis="X", n=20)
            m.cyl((x * 1.03, y, -0.6 + r), r * 0.5, 0.02, steel, axis="X", n=14)
    kit.mesh_swap(body, m.mesh("prop.forklift"))
    forks = obj("forklift28.forks")  # in the carriage's frame (forks' box centre at y 0.5, z 0.03)
    m = mk.MK()
    for x in (-0.3, 0.3):
        m.box((x, 0.0, 0.0), (0.12, 1.0, 0.05), steel)
        m.box((x, -0.5, 0.35), (0.12, 0.05, 0.7), steel)  # the fork's heel, up the carriage
    m.box((0, -0.5, 0.75), (1.0, 0.04, 0.6), dark)  # the load backrest
    for k in range(4):
        m.box((0, -0.49, 0.5 + k * 0.17), (0.98, 0.05, 0.03), steel)
    kit.mesh_swap(forks, m.mesh("prop.forks"))


def auction_sign():
    """S28: the A-frame board, its two legs splayed behind."""
    o = obj("auction28.board")
    m = mk.MK()
    wood, board = mat("aframe.wood", "#5a4630", rough=0.8), mat("aframe.board", "#efe6cf", rough=0.85)
    m.box((0, 0, 0), (0.75, 0.03, 1.1), board, bevel=0.01)
    for s in (-1, 1):
        m.box((s * 0.36, 0.0, 0.0), (0.04, 0.05, 1.14), wood)
    m.box((0, -0.25, -0.02), (0.75, 0.03, 1.1), wood, rot=(-0.45, 0, 0))  # the back leaf (the lettering's on +Y)
    kit.mesh_swap(o, m.mesh("prop.aframe"))


def doghouse():
    o = obj("doghouse")
    m = mk.MK()
    wood = mat("dog.wood", "#a07048", rough=0.85)
    gb.grime(wood, amt=0.5) if not wood.get("grimed") else None
    wood["grimed"] = 1
    roof, dark, board = mat("dog.roof", "#2f2b28", rough=0.9), mat("dog.hole", "#050505", rough=1.0), \
        mat("dog.board", "#d8cfb8", rough=0.9)
    w, d, hw = 1.0, 1.1, 0.75  # walls to 0.75 above the ground; the box's centre is 0.5 up
    z0 = -0.5
    m.box((0, 0, z0 + hw / 2), (w, d, hw), wood)
    m.prism([(-w / 2, z0 + hw), (w / 2, z0 + hw), (0, z0 + hw + 0.45)], d, wood)  # the gable
    for k in range(6):  # plank lines
        m.box((0, -d / 2 - 0.004, z0 + 0.1 + k * 0.12), (w, 0.006, 0.012), roof)
    ang, sl = math.atan2(0.45, w / 2), math.hypot(0.45, w / 2)
    for s in (-1, 1):  # the roof's two slopes: each the slope's full length plus an eave, meeting at the ridge
        ux, uz = s * (w / 2) / sl, -0.45 / sl  # down the slope, from the ridge
        nx, nz = s * 0.45 / sl, (w / 2) / sl  # out of it
        ln = sl + 0.14
        cx, cz = ux * (ln / 2 - 0.02) + nx * 0.02, z0 + hw + 0.45 + uz * (ln / 2 - 0.02) + nz * 0.02
        m.box((cx, 0, cz), (ln, d + 0.2, 0.04), roof, rot=(0, s * ang, 0))
    m.cyl((0, 0, z0 + hw + 0.45 + 0.035), 0.035, d + 0.2, roof, axis="Y", n=12)  # the ridge cap
    r = 0.2  # the doorway: straight sides and a round arch
    arch = [(r * math.cos(a), 0.33 + r * math.sin(a)) for a in [math.pi * k / 24 for k in range(25)]]
    m.prism([(-r, 0.0), (r, 0.0)] + arch, 0.02, dark, c=(0, -d / 2 - 0.006, z0 + 0.02))
    m.box((0, -d / 2 - 0.015, 0.35), (0.72, 0.02, 0.16), board)  # the sign board behind BOT DEFENSE
    m.lathe([(0.0, z0 + 0.0), (0.12, z0 + 0.0), (0.13, z0 + 0.06), (0.1, z0 + 0.06), (0.1, z0 + 0.02), (0.0, z0 + 0.02)],
            mat("dog.bowl", "#8a9096", metal=0.8, rough=0.35), c=(0.35, -0.85, 0), n=24)  # an empty bowl
    kit.mesh_swap(o, m.mesh("prop.doghouse"))
    blank(obj("doghouse.roof"))
    blank(obj("doghouse.door"))
    sign = obj("doghouse.sign")
    if sign:
        # on the board's face (-d/2 - 0.025 from the house's centre): 4.5 cm off it, the letters cast a ghost below
        sign.location.y = o.location.y - d / 2 - 0.025 - 0.003
        sign.data.materials.clear()
        sign.data.materials.append(mat("dog.ink", "#1b1b1b"))


def lanterns():
    iron = mat("lantern.iron", "#2c2a27", metal=0.6, rough=0.5)
    for k in range(8):
        o = obj(f"goodbot{k}.lantern")
        if not o:
            continue
        glow = o.data.materials[0]
        m = mk.MK()
        m.sphere((0, 0, 0), 0.035, glow)
        m._mi(glow)
        m.cyl((0, 0, -0.06), 0.05, 0.02, iron)
        m.cyl((0, 0, 0.065), 0.05, 0.03, iron, r2=0.015)
        for j in range(4):
            a = j * math.pi / 2 + math.pi / 4
            m.box((0.042 * math.cos(a), 0.042 * math.sin(a), 0.0), (0.008, 0.008, 0.12), iron)
        m.torus((0, 0, 0.09), 0.035, 0.004, iron, rot=(math.pi / 2, 0, 0), arc=math.pi, n=10)
        kit.mesh_swap(o, m.mesh(f"prop.lantern{k}"))


def shovel():
    obj("shovel").location.z = 0.3  # stuck in the south end of the spoil heap (parkdress)
    h = obj("shovel.handle")
    kit.swap(h, "rusted_spade_01", scale=1.15, offset=(0, 0, -0.7))
    blank(obj("shovel.blade"))


# ---------------------------------------------------------------- the bookends (M6)

PROPS6 = gb.ROOT / "assets" / "gen" / "props"


def food(key, c1, c2, scale=60.0, bump=0.4, rough=0.6, detail=6.0):
    """A food surface: two colours mixed by noise, with a matching bump (rice grains, crisp fish skin, egg white)."""
    name = f"prop.food.{key}"
    if name in gb._MATS:
        return gb._MATS[name]
    m = gb.mat(name, c1, rough=rough)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs[6].default_value = gb.lin(c1)
    mix.inputs[7].default_value = gb.lin(c2)
    nt.links.new(n.outputs["Fac"], mix.inputs["Factor"])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.002
    nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def breakfast(S, SP):
    """S01a-S01d, S49: the breakfast as in the human's plate photo (assets/real/plate.jpg, which the phone shows in
    S01b): bangsilog on a paper plate (garlic rice, two fried eggs with runny yolks, a butterflied fried milkfish),
    a white plastic fork and spoon, on a black textured tray with a paper napkin and a paper cup; the visitor badge
    beside it and the folded schedule (assets/gen/props/, scripts/gen_bookend_props.py) under the saucer. S49: the
    badge has expired."""
    tx, ty, tz = S["table"]
    cx, cy, top = tx + 0.1, ty - 0.1, tz + 0.0175  # the plate's centre on the tray
    paper = mat("paperplate", "#f1efe8", rough=0.85)
    m = mk.MK()  # the paper plate: a shallow dish with a rolled rim
    m.lathe([(0, 0.002), (0.095, 0.002), (0.112, 0.008), (0.127, 0.016), (0.131, 0.017), (0.132, 0.015),
             (0.113, 0.006), (0.096, 0.0005), (0, 0.0005)], paper, c=(0, 0, 0), n=48)
    o = obj("eat.plate")
    o.location = (cx, cy, top)
    mk_ = m.mesh("prop.paperplate")
    kit.mesh_swap(o, mk_)
    rice = food("rice", "#efe6d2", "#c9b48c", scale=180, bump=0.9, rough=0.7)
    egg = food("eggwhite", "#fbfaf4", "#e9e2c8", scale=25, bump=0.25, rough=0.35)
    yolk = mat("yolk", "#f2b51c", rough=0.15)
    fish = food("milkfish", "#b8793c", "#5a3a1f", scale=22, bump=1.0, rough=0.45, detail=8)
    skin = mat("milkfish.skin", "#3d3a36", rough=0.4)
    m = mk.MK()
    rng = random.Random(27)
    m.sphere((0.035, -0.025, 0.004), 0.085, rice, s=(1.0, 0.85, 0.3))  # the garlic rice, mounded on the right
    grain = mat("ricegrain", "#f3ecdc", rough=0.5)
    toast = mat("garlic", "#b98a45", rough=0.6)
    for k in range(700):  # its grains, over the mound (and a few toasted garlic bits)
        a, r = rng.uniform(0, 2 * math.pi), 0.088 * math.sqrt(rng.random())
        x, y = 0.035 + r * math.cos(a), -0.025 + 0.85 * r * math.sin(a)
        z = 0.004 + 0.3 * 0.085 * math.sqrt(max(0.0, 1 - (r / 0.088) ** 2)) + 0.001
        m.sphere((x, y, z), 0.0036, toast if k % 23 == 0 else grain, s=(1.0, 0.42, 0.38),
                 rot=(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(0, math.pi)), u=6, v=4)
    for (ex, ey, ez, sx, sy, rz) in ((-0.03, -0.04, 0.02, 0.055, 0.043, 0.4), (0.025, -0.012, 0.028, 0.05, 0.04, -0.3)):
        m.sphere((ex, ey, ez), 1.0, egg, s=(sx, sy, 0.006), rot=(0, 0, rz), u=20, v=8)  # the whites, frilled flat
        m.sphere((ex + 0.006, ey + 0.004, ez + 0.006), 0.015, yolk, s=(1.2, 1.0, 0.45), u=16, v=8)  # the yolks, broken
        m.sphere((ex - 0.01, ey - 0.012, ez + 0.003), 0.011, yolk, s=(1.6, 0.8, 0.2), u=12, v=6)  # the runny spill
    kit.mesh_swap(obj("eat.fish"), m.mesh("prop.bangsilog"))
    obj("eat.fish").location = (cx, cy, top)
    # the milkfish, butterflied and fried: two rounded fillets side by side, joined at the dark backbone, tapering to
    # the tail, across the back of the plate: mottled golden-brown crisp flesh, dark skin showing at the edges
    flesh = food("milkfish.v2", "#c98f4c", "#7a4a22", scale=45, bump=1.6, rough=0.35, detail=10)
    skin = mat("milkfish.skin", "#2e2a26", rough=0.35)
    m = mk.MK()
    for side in (1, -1):
        m.sphere((0.0, side * 0.03, 0.0), 1.0, skin, s=(0.11, 0.036, 0.005), rot=(side * 0.08, 0, side * 0.04), u=36, v=10)
        m.sphere((-0.004, side * 0.029, 0.0025), 1.0, flesh, s=(0.104, 0.032, 0.005), rot=(side * 0.08, 0, side * 0.04),
                 u=36, v=10)
    m.box((0.0, 0.0, 0.006), (0.17, 0.007, 0.003), skin, bevel=0.0015)  # the backbone
    m.prism([(0.1, 0.0), (0.135, 0.03), (0.126, 0.0), (0.135, -0.03)], 0.003, skin, c=(0, 0, 0.001),
            rot=(math.pi / 2, 0, 0))  # the tail
    fi = gb.link(bpy.data.objects.new("eat.milkfish", m.mesh("prop.milkfish")))
    fi.location = (cx - 0.01, cy + 0.058, top + 0.01)
    fi.rotation_euler = (0.05, 0, 0.12)
    plast = mat("plasticware", "#f6f5f0", rough=0.3)
    m = mk.MK()  # the fork (across the front left, handle off the rim) and the spoon (on the rice, back right)
    m.box((-0.09, -0.06, 0.03), (0.1, 0.009, 0.0025), plast, rot=(0, 0.08, -0.12), bevel=0.001)
    m.box((-0.03, -0.068, 0.034), (0.025, 0.016, 0.002), plast, rot=(0, 0.0, -0.12), bevel=0.0006)
    for k in range(4):
        m.box((-0.008, -0.074 + k * 0.0045, 0.035), (0.026, 0.002, 0.0016), plast, rot=(0, 0, -0.12))
    m.box((0.12, 0.03, 0.04), (0.09, 0.009, 0.0025), plast, rot=(0, -0.12, 0.3), bevel=0.001)
    m.sphere((0.07, 0.015, 0.045), 0.02, plast, s=(1.0, 0.7, 0.22), rot=(0, 0, 0.3), u=14, v=6)
    ware = gb.link(bpy.data.objects.new("eat.plasticware", m.mesh("prop.plasticware")))
    ware.location = (cx, cy, top)
    tray_o = obj("eat.mytray")
    tray = food("tray", "#1d1e20", "#2a2b2e", scale=140, bump=0.6, rough=0.55, detail=2)
    m = mk.MK()
    m.box((0, 0, 0), (0.5, 0.36, 0.008), tray, bevel=0.004)
    for s in (-1, 1):  # the raised rim
        m.box((0, s * 0.177, 0.007), (0.5, 0.008, 0.012), tray, bevel=0.003)
        m.box((s * 0.247, 0, 0.007), (0.008, 0.36, 0.012), tray, bevel=0.003)
    kit.mesh_swap(tray_o, m.mesh("prop.tray"))
    m = mk.MK()  # the paper cup (tapered) and the napkin folded on the tray's back right
    cup = mat("papercup", "#f4f2ec", rough=0.75)
    m.lathe([(0, 0), (0.028, 0), (0.037, 0.095), (0.039, 0.097), (0.036, 0.097), (0.026, 0.004), (0, 0.004)], cup, n=32)
    co = obj("eat.cup")
    co.location = (tx + 0.3, ty + 0.05, tz + 0.012)
    kit.mesh_swap(co, m.mesh("prop.papercup"))
    m = mk.MK()
    m.box((0, 0, 0), (0.15, 0.1, 0.003), mat("napkin", "#f7f6f2", rough=0.9), rot=(0, 0, 0.35), bevel=0.001)
    m.box((0.01, 0.0, 0.003), (0.13, 0.08, 0.002), mat("napkin", "#f7f6f2", rough=0.9), rot=(0.05, 0, 0.3), bevel=0.001)
    nap = gb.link(bpy.data.objects.new("eat.napkin", m.mesh("prop.napkin")))
    nap.location = (tx + 0.22, ty + 0.03, tz + 0.02)
    # the badge and the schedule, printed
    for name, key, during_ in (("eat.badge", "badge_visitor", (-1e5, SP["S49"][0])),
                               ("eat.badge.exp", "badge_expired", (SP["S49"][0], 1e5))):
        m = mk.MK()
        m.box((0, 0, -0.0006), (0.0889, 0.0572, 0.0008), mat("badge.back", "#f4f4f2", rough=0.6))
        m.quad((0, 0, 0.0002), (0.0889, 0.0572), mk.img_mat(f"prop.img.{key}", PROPS6 / f"{key}.png", rough=0.5),
               facing="+Z")
        if name == "eat.badge":
            bo = obj("eat.badge")
            bo.scale = (1, 1, 1)
            kit.mesh_swap(bo, m.mesh(f"prop.{key}"))
        else:
            bo = gb.link(bpy.data.objects.new(name, m.mesh(f"prop.{key}")))
            bo.location = obj("eat.badge").location
        bo.location = (tx - 0.2, ty - 0.08, tz + 0.006)  # beside the tray, where S01c's drift passes
        bo.rotation_euler = (0, 0, 0.18)
        gb.show_between(bo, *during_)
    for t in ("eat.badge.t", "eat.badge.expired"):  # the grey-box lettering (text curves): the print replaces it
        o = obj(t)
        if o:
            o.animation_data_clear()
            o.hide_render = o.hide_viewport = True
    m = mk.MK()  # the schedule folded in thirds, one panel lifted where it pokes out from under the saucer
    sched = mk.img_mat("prop.img.schedule", PROPS6 / "schedule.png", rough=0.85)
    m.quad((0, 0, 0), (0.2159, 0.2794), sched, facing="+Z")
    so = obj("eat.schedule")
    so.scale = (1, 1, 1)
    kit.mesh_swap(so, m.mesh("prop.schedule"))
    so.rotation_euler = (0.0, 0.0, -0.22)
    so.location.z = tz + 0.0015


def build(S, SP):
    breakfast(S, SP)
    for f in (payphone, adding_machine, calendar, envelope, notice, cassette, boombox, magnifier, vehicles, crates, arrows,
              hoses, ball, forklift, auction_sign, briefcase, keys25, balcony_rail, balcony_light, bell, podium, banner, stickies, funnel, payroll, rubberband, coffin,
              doghouse, lanterns, shovel):
        f()
    brickwall(SP)
    brooms(SP)
    chalk(S, SP)
    import os
    only = os.environ.get("DETAIL_ONLY")
    if not only or "interiors" in only.split(","):  # the lobby's display by the glass replaces shots.stage()'s boxes
        import interiors
        interiors.staged(S, SP)
    shots.tape_staging(S, SP, tape_run(S, SP))  # last: it drapes onto the interiors' floors too
    shots.inherit_visibility()
