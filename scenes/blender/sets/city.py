"""Detail pass: the city around the block (see detail.py). The final look only.

The block was an island in a black void. Around it now:
  sky        the night sky's city glow: San Francisco's low cloud lit brownish-orange from below, strongest at the
             horizon, fading to the night blue overhead; off by day (the pre-roll is a sunny morning)
  streets    the street grid: the cross street west of the corner (road x -43..-36, sidewalks to -46 and -33), another
             east of the block (x 48..55), an alley behind the south row (y -26..-22), streets north and south
             (y 50..58, -58..-50) and further out; sidewalks with curbs; a far ground plane past the block's 200 m
  buildings  every city block around the hero blocks lined with buildings: one procedural facade shader (a window grid
             from world coordinates and per-face attributes: bays, floors, a seeded fraction lit warm `community`, a
             few cool, blinds part way down; frames and sills; brick or painted walls; parapet, cornice and coping;
             storefronts on the street faces, shuttered, dark or lit, with sign bands); far buildings fade into the
             night haze
  corner     the two plain boxes across the cross street (corner.far, corner.far.n: hidden, not deleted) replaced by
             buildings on the same footprints with modelled storefronts, an SRO hotel's blade sign, awnings and fire
             escapes; grunge.py's throw-up and posters stay on the wall at x = -46
  skyline    taller towers further off, mostly north-east (where downtown is from the Tenderloin), masonry and glass
  lamps      street lamps on the far streets: emissive heads and a soft pool on the ground; two real lights at the
             cross street
  rooftops   parapets, cornices, water tanks, HVAC units, vents, stair bulkheads, chimneys, skylights and antennas on
             the block's own roofs (the south row, the north shops: S15, S23, S26) and on the near city's roofs.
             Nothing on the tower: it is the one clean thing.

All of it is seeded (random.Random(SEED)), so every render matches. Windows, lamp heads and storefront lights are
keyed off by day (song t < 0.14, as shots.light()'s sky).
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import gb

SEED = 20261102
NIGHT_T = 0.14  # shots.light(): day before this song time, night after
# Eevee's world volume (shots.light()'s haze) is infinite, so it absorbs the sun and the moon entirely: by night the
# city's walls and roofs get no moonlight at all. FAKE_MOON stands in for it in the facade shader (a faint cool
# self-light, roofs more than walls); set it to 0 if the haze moves to a volume object and the moon comes back.
FAKE_MOON = 0.0

# the street grid: roads curb to curb (sidewalks are the blocks' edges)
XR = [(-128.0, -120.0), (-43.0, -36.0), (48.0, 55.0), (130.0, 138.0)]  # north-south roads
YR = [(-150.0, -142.0), (-58.0, -50.0), (-6.0, 6.0), (50.0, 58.0), (140.0, 148.0)]  # east-west roads
BOUND = (-230.0, 240.0, -240.0, 240.0)
HERO_S = (-36.0, 48.0, -50.0, -6.0)
HERO_N = (-36.0, 48.0, 6.0, 50.0)

PAL = {  # wall colours (sRGB): brick, painted stucco (SF's tired pastels), concrete
    "brick": ["#6e4335", "#7a4a3a", "#5e3a2f", "#84553f", "#6b4a3e"],
    "paint": ["#8a8272", "#7c8a86", "#8f8064", "#6f7a84", "#9a9284", "#7b6f62", "#8c8f80", "#a09a8a", "#6d6f73",
              "#86766a", "#7e8b78", "#8a7c86"],
    "concrete": ["#77746e", "#8a8780", "#6a6966", "#7f7b72"],
}


def lin3(h):
    return gb.lin(h)[:3]


# ---------------------------------------------------------------- small helpers

class Batch:
    """Boxes and cylinders merged into one mesh, several materials (by index)."""

    def __init__(self, name, mats, uv=False):
        self.name, self.mats, self.uv = name, mats, uv
        self.v, self.f, self.mi = [], [], []

    def _add(self, verts, faces, mtx, mi):
        base = len(self.v)
        self.v += [tuple(mtx @ Vector(p)) for p in verts]
        self.f += [tuple(base + i for i in fc) for fc in faces]
        self.mi += [mi] * len(faces)

    def box(self, c, s, mi=0, rot_z=0.0, rot=None, bottom=True):
        sx, sy, sz = (q / 2 for q in s)
        v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
             (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
        f = [(4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)] + ([(0, 3, 2, 1)] if bottom else [])
        r = Matrix.Rotation(rot_z, 4, "Z") if rot is None else rot.to_matrix().to_4x4()
        self._add(v, f, Matrix.Translation(c) @ r, mi)

    def cyl(self, c, r, h, mi=0, n=12, r2=None, rot=None, caps=True):
        r2 = r if r2 is None else r2
        v = [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), -h / 2) for k in range(n)] + \
            [(r2 * math.cos(2 * math.pi * k / n), r2 * math.sin(2 * math.pi * k / n), h / 2) for k in range(n)]
        f = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
        if caps:
            f += [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        m = Matrix.Translation(c) @ (rot.to_matrix().to_4x4() if rot is not None else Matrix())
        self._add(v, f, m, mi)

    def quad(self, pts, mi=0):
        self._add(pts, [(0, 1, 2, 3)], Matrix(), mi)

    def done(self, smooth=False):
        if not self.f:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.v, [], self.f)
        me.polygons.foreach_set("material_index", self.mi)
        for m in self.mats:
            me.materials.append(m)
        if smooth:
            me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        if self.uv:  # each quad 0..1
            uv = me.uv_layers.new()
            co = []
            for p in me.polygons:
                co += [0, 0, 1, 0, 1, 1, 0, 1][:2 * p.loop_total] + [0, 0] * max(0, p.loop_total - 4)
            uv.data.foreach_set("uv", co)
        me.update()
        return gb.link(bpy.data.objects.new(self.name, me))


def mat(key, hexcol, grime=0.5, **kw):
    m = gb.mat(f"city.{key}", hexcol, **kw)
    if grime and not m.get("grimed"):
        gb.grime(m, amt=grime)
        m["grimed"] = 1
    return m


def key_night(owner, path, day=0.0, night=1.0):
    gb.keys(owner, path, [(0, day, "CONSTANT"), (gb.F(NIGHT_T), night, "CONSTANT")], interp="CONSTANT")


_CTL = {}


def night_ctl():
    """An empty whose ["on"] is 0 by day, 1 by night: for gb.glow_mat."""
    if "c" not in _CTL:
        c = gb.empty("city.night.ctl", (0, 0, -5))
        c["on"] = 1.0
        key_night(c, '["on"]')
        _CTL["c"] = c
    return _CTL["c"]


class NB:
    """Terse shader-node building: math on sockets or floats."""

    def __init__(self, nt):
        self.nt = nt

    def n(self, kind, **props):
        node = self.nt.nodes.new(kind)
        for k, v in props.items():
            setattr(node, k, v)
        return node

    def link(self, a, sock):
        if isinstance(a, (int, float)):
            sock.default_value = a
        elif isinstance(a, tuple):
            sock.default_value = a if len(a) == len(sock.default_value) else (*a, 1.0)
        else:
            self.nt.links.new(a, sock)

    def m(self, op, a, b=0.0, clamp=False):
        node = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        self.link(a, node.inputs[0])
        self.link(b, node.inputs[1])
        return node.outputs[0]

    def add(self, a, b):
        return self.m("ADD", a, b)

    def sub(self, a, b):
        return self.m("SUBTRACT", a, b)

    def mul(self, a, b):
        return self.m("MULTIPLY", a, b)

    def div(self, a, b):
        return self.m("DIVIDE", a, b)

    def gt(self, a, b):
        return self.m("GREATER_THAN", a, b)

    def lt(self, a, b):
        return self.m("LESS_THAN", a, b)

    def band(self, x, lo, hi):
        return self.mul(self.gt(x, lo), self.lt(x, hi))

    def lerp(self, t, a, b):  # floats/sockets
        return self.add(a, self.mul(t, self.sub(b, a)))

    def sep(self, vec):
        s = self.n("ShaderNodeSeparateXYZ")
        self.link(vec, s.inputs[0])
        return s.outputs[0], s.outputs[1], s.outputs[2]

    def comb(self, x, y, z):
        c = self.n("ShaderNodeCombineXYZ")
        for i, a in enumerate((x, y, z)):
            self.link(a, c.inputs[i])
        return c.outputs[0]

    def attr(self, name):
        a = self.n("ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name=name)
        return self.sep(a.outputs["Vector"])

    def mix(self, fac, a, b):
        node = self.n("ShaderNodeMix", data_type="RGBA")
        self.link(fac, node.inputs[0])
        self.link(a, node.inputs[6])
        self.link(b, node.inputs[7])
        return node.outputs[2]

    def cmul(self, a, b):
        node = self.n("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
        node.inputs[0].default_value = 1.0
        self.link(a, node.inputs[6])
        self.link(b, node.inputs[7])
        return node.outputs[2]

    def white(self, vec):
        w = self.n("ShaderNodeTexWhiteNoise", noise_dimensions="3D")
        self.link(vec, w.inputs["Vector"])
        r2, r3, r4 = self.sep(w.outputs["Color"])
        return w.outputs["Value"], r2, r3, r4

    def noise(self, vec, scale, detail=2.0):
        t = self.n("ShaderNodeTexNoise")
        self.link(vec, t.inputs["Vector"])
        t.inputs["Scale"].default_value, t.inputs["Detail"].default_value = scale, detail
        return t.outputs["Fac"]

    def value(self, name, v):
        node = self.n("ShaderNodeValue", name=name, label=name)
        node.outputs[0].default_value = v
        return node.outputs[0]


# ---------------------------------------------------------------- the facade shader

_FACADE = {}


def facade_mat():
    """One material for every background building. Per-face attributes (set by Blocks):
    fa = (u0, bay, floor height)  fb = (ground-floor top, building top, seed)  fc = (lit fraction, window margin,
    storefront)  fd = (brick, glass tower, trim tone)  wall = wall colour (linear)."""
    if "m" in _FACADE:
        return _FACADE["m"]
    m = bpy.data.materials.new("city.facade")
    m.use_nodes = True
    nt = m.node_tree
    B = NB(nt)
    bsdf = nt.nodes["Principled BSDF"]
    out = nt.nodes["Material Output"]
    geo = B.n("ShaderNodeNewGeometry")
    px, py, pz = B.sep(geo.outputs["Position"])
    nx, ny, nz = B.sep(geo.outputs["Normal"])
    u0, bay, fl = B.attr("fa")
    gf, top, seed = B.attr("fb")
    # face attributes reach the shader barycentrically interpolated, a bit off in the last place; White Noise hashes
    # the float's bits, so everything it is fed is rounded to whole numbers first
    seed = B.m("ROUND", seed)
    litf, wm, shop = B.attr("fc")
    brick, glassy, tone = B.attr("fd")
    wall_a = B.n("ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name="wall")
    wall = wall_a.outputs["Vector"]
    night = B.value("night", 1.0)
    ax, ay = B.m("ROUND", B.m("ABSOLUTE", nx)), B.m("ROUND", B.m("ABSOLUTE", ny))
    uabs = B.add(B.mul(px, ay), B.mul(py, ax))
    u = B.sub(uabs, u0)
    cu = B.div(u, bay)
    iu = B.m("FLOOR", cu)
    fu = B.sub(cu, iu)
    vz = B.div(B.sub(pz, gf), fl)
    iv = B.m("FLOOR", vz)
    fv = B.sub(vz, iv)
    roof = B.gt(nz, 0.5)
    wallside = B.sub(1.0, roof)
    upper = B.mul(B.mul(B.gt(pz, gf), B.lt(pz, B.sub(top, 1.35))), wallside)
    vlo = B.lerp(glassy, 0.28, 0.06)
    vhi = B.lerp(glassy, 0.86, 0.94)
    win = B.mul(upper, B.mul(B.band(fu, wm, B.sub(1.0, wm)), B.band(fv, vlo, vhi)))
    frm = B.mul(upper, B.mul(B.band(fu, B.sub(wm, 0.04), B.add(B.sub(1.0, wm), 0.04)),
                             B.band(fv, B.sub(vlo, 0.03), B.add(vhi, 0.03))))
    frm = B.mul(B.sub(frm, win), B.sub(1.0, glassy))
    sill = B.mul(upper, B.mul(B.band(fu, B.sub(wm, 0.07), B.add(B.sub(1.0, wm), 0.07)),
                              B.band(fv, B.sub(vlo, 0.08), B.sub(vlo, 0.03))))
    sill = B.mul(sill, B.sub(1.0, glassy))
    # per window: lit or dark, warm or cool, blind part way down, brightness
    # rounded: White Noise hashes the float's bits, and interpolated normals are only nearly +-1
    face_k = B.m("ROUND", B.add(B.mul(B.m("ROUND", nx), 31.0), B.mul(B.m("ROUND", ny), 17.0)))
    r1, r2, r3, r4 = B.white(B.comb(B.add(iu, face_k), iv, seed))
    lit = B.lt(r1, litf)
    blinded = B.lt(r4, 0.4)
    level = B.add(0.42, B.mul(r2, 0.42))
    covered = B.mul(blinded, B.gt(fv, level))
    glow_k = B.mul(lit, B.sub(1.0, B.mul(covered, 0.7)))
    glow_k = B.mul(glow_k, B.add(0.35, B.mul(r3, 0.65)))
    warm = B.mix(r2, lin3("#ffd38a"), lin3("#ffb066"))
    wcol = B.mix(B.lt(r3, 0.1), warm, lin3("#d6e4ff"))
    wcol = B.mix(covered, wcol, lin3("#f0d9a8"))
    # the ground floor: storefronts on street faces (2 bays each)
    su = B.div(u, B.mul(bay, 2.0))
    isu = B.m("FLOOR", su)
    fs = B.sub(su, isu)
    gnd = B.mul(B.mul(B.lt(pz, gf), wallside), shop)
    s1, s2, s3, s4 = B.white(B.comb(B.add(isu, face_k), 777.0, seed))
    glass = B.mul(gnd, B.mul(B.band(fs, 0.08, 0.92), B.band(pz, 0.5, B.sub(gf, 1.15))))
    signb = B.mul(gnd, B.mul(B.band(fs, 0.03, 0.97), B.band(pz, B.sub(gf, 1.0), B.sub(gf, 0.3))))
    shut = B.lt(s1, 0.5)
    litshop = B.gt(s1, 0.66)
    ramp = B.n("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    signcols = ["#d9cfb4", "#3d5a4a", "#2e3b57", "#b9973f", "#e6e1d3", "#4d6a73", "#6b5a45", "#c8c0a8"]
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.0, gb.lin(signcols[0])
    els[1].position, els[1].color = 1.0 / len(signcols), gb.lin(signcols[1])
    for k, c in enumerate(signcols[2:], 2):
        e = els.new(k / len(signcols))
        e.color = gb.lin(c)
    B.link(s2, ramp.inputs[0])
    signcol = ramp.outputs[0]
    stripes = B.add(0.8, B.mul(B.m("SINE", B.mul(pz, 42.0)), 0.12))
    shutcol = B.cmul(lin3("#7d867d"), B.comb(stripes, stripes, stripes))
    shopglow = B.mix(B.lt(s3, 0.35), lin3("#ffd9a0"), lin3("#e8f1ff"))
    # wall colour: brick or paint, varied, trims and sills, parapet coping and a cornice band
    pos2 = B.comb(uabs, pz, 0.0)
    bt = B.n("ShaderNodeTexBrick")
    B.link(pos2, bt.inputs["Vector"])
    B.link(wall, bt.inputs["Color1"])
    B.link(B.cmul(wall, (0.78, 0.74, 0.72)), bt.inputs["Color2"])
    bt.inputs["Mortar"].default_value = (*lin3("#5c574f"), 1.0)
    bt.inputs["Scale"].default_value = 1.0
    bt.inputs["Mortar Size"].default_value = 0.012
    bt.inputs["Brick Width"].default_value = 0.23
    bt.inputs["Row Height"].default_value = 0.075
    base = B.mix(brick, wall, bt.outputs["Color"])
    var = B.add(0.82, B.mul(B.noise(geo.outputs["Position"], 0.25, 3.0), 0.36))
    base = B.cmul(base, B.comb(var, var, var))
    trim = B.mix(tone, B.cmul(wall, (0.35, 0.35, 0.35)), lin3("#cfc8b6"))
    cornice = B.mul(wallside, B.band(pz, B.sub(top, 1.15), B.sub(top, 0.8)))
    coping = B.mul(wallside, B.band(pz, B.sub(top, 0.16), B.add(top, 1.0)))
    base = B.mix(B.add(cornice, frm), base, trim)
    base = B.mix(B.add(sill, coping), base, lin3("#8f897d"))
    # glass tower: spandrels between the window bands, mullions
    base = B.mix(B.mul(glassy, wallside), base, B.mix(B.gt(pz, gf), base, lin3("#3c4249")))
    glasscol = B.mix(glassy, lin3("#0b0e12"), lin3("#16202b"))
    base = B.mix(win, base, glasscol)
    # storefronts
    base = B.mix(B.mul(gnd, B.sub(1.0, B.add(glass, signb))), base, B.cmul(base, (0.8, 0.8, 0.8)))
    base = B.mix(glass, base, B.mix(shut, lin3("#0d0f12"), shutcol))
    base = B.mix(signb, base, signcol)
    rr, _, _, _ = B.white(B.comb(seed, 5.0, 5.0))  # tar, gravel or a pale membrane, per building
    roofcol = B.mix(B.gt(rr, 0.62), B.mix(rr, lin3("#4a4743"), lin3("#6e6a63")), lin3("#9a978f"))
    roofcol = B.cmul(roofcol, B.comb(var, var, var))
    base = B.mix(roof, base, roofcol)
    B.link(base, bsdf.inputs["Base Color"])
    rough = B.sub(0.88, B.mul(B.add(win, B.mul(glass, B.sub(1.0, shut))), 0.74))
    B.link(rough, bsdf.inputs["Roughness"])
    # emission: lit windows, lit shops and their sign boxes, by night only
    e_win = B.mul(win, glow_k)
    e_shop = B.mul(B.mul(glass, B.sub(1.0, shut)), litshop)
    e_sign = B.mul(B.mul(signb, litshop), 0.3)
    ec = B.mix(B.gt(e_shop, 0.5), B.cmul(wcol, B.comb(e_win, e_win, e_win)), shopglow)
    ec = B.mix(B.gt(e_sign, 0.1), ec, B.cmul(signcol, (0.6, 0.6, 0.6)))
    estr = B.mul(B.add(B.add(e_win, B.mul(e_shop, 0.9)), e_sign), B.mul(night, gb.LOOK["lights"]["window_emit"] * 1.1))
    ecs = B.n("ShaderNodeVectorMath", operation="SCALE")
    B.link(ec, ecs.inputs[0])
    B.link(estr, ecs.inputs["Scale"])
    amb = B.n("ShaderNodeVectorMath", operation="MULTIPLY")  # the stand-in moon (FAKE_MOON)
    B.link(base, amb.inputs[0])
    k = B.mul(B.mul(night, FAKE_MOON), B.add(0.1, B.mul(roof, 0.22)))
    B.link(B.cmul(B.comb(k, k, k), (0.55, 0.66, 1.0)), amb.inputs[1])
    tot = B.n("ShaderNodeVectorMath", operation="ADD")
    B.link(ecs.outputs[0], tot.inputs[0])
    B.link(amb.outputs[0], tot.inputs[1])
    B.link(tot.outputs[0], bsdf.inputs["Emission Color"])
    # distance: far buildings fade into the haze (the world volume stops at 120 m)
    cam = B.n("ShaderNodeCameraData")
    dist = cam.outputs["View Distance"]
    fog = B.sub(1.0, B.m("EXPONENT", B.mul(B.m("MAXIMUM", B.sub(dist, 60.0), 0.0), -1.0 / 420.0)))
    fog = B.mul(fog, 0.85)
    B.link(B.sub(1.0, B.mul(fog, 0.75)), bsdf.inputs["Emission Strength"])
    haze = B.n("ShaderNodeEmission")
    hz = B.mix(night, (0.47, 0.6, 0.8), (0.055, 0.032, 0.02))
    B.link(hz, haze.inputs["Color"])
    haze.inputs["Strength"].default_value = 1.0
    mix = B.n("ShaderNodeMixShader")
    B.link(fog, mix.inputs[0])
    nt.links.new(bsdf.outputs[0], mix.inputs[1])
    nt.links.new(haze.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    key_night(nt, 'nodes["night"].outputs[0].default_value')
    gb.grime(m, amt=0.45, streak=0.8, damp=0.6)
    _FACADE["m"] = m
    return m


# ---------------------------------------------------------------- buildings

class Blocks:
    """Building boxes (no bottoms) with the facade shader's per-face attributes, merged per group."""

    def __init__(self, name):
        self.name = name
        self.v, self.f, self.attrs = [], [], {k: [] for k in ("fa", "fb", "fc", "fd", "wall")}
        self.roofs = []  # (x0, x1, y0, y1, top) for rooftop clutter
        self.fe = []  # fire escapes: (x, y, turn)

    def add(self, x0, x1, y0, y1, h, style, sides, z0=0.0, roof=True):
        """sides: {'N'|'S'|'E'|'W': 'front'|'rear'|'party'}; style: bay, fl, gf, lit, wm, brick, glassy, tone, wall,
        seed."""
        base = len(self.v)
        self.v += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, h), (x1, y0, h), (x1, y1, h),
                   (x0, y1, h)]
        faces = {"S": (0, 1, 5, 4), "E": (1, 2, 6, 5), "N": (2, 3, 7, 6), "W": (3, 0, 4, 7)}
        for side, fc in faces.items():
            kind = sides.get(side, "party")
            if side in "NS":
                a, w = x0, x1 - x0
            else:
                a, w = y0, y1 - y0
            bay = w / max(1, round(w / style["bay"]))
            gfz = style["gf"] if kind == "front" else (style.get("gf_rear", 1.0))
            self.f.append(tuple(base + i for i in fc))
            self.attrs["fa"].append((a, bay, style["fl"]))
            self.attrs["fb"].append((gfz, h, float(int(style["seed"] * 10) + {"N": 0, "S": 1, "E": 2, "W": 3}[side] * 1000)))
            wm = style["wm"] if kind != "party" else 0.5
            self.attrs["fc"].append((style["lit"] if kind != "party" else 0.0, wm, 1.0 if kind == "front" and
                                     style.get("shops", True) else 0.0))
            self.attrs["fd"].append((style["brick"], style["glassy"], style["tone"]))
            self.attrs["wall"].append(style["wall"])
        if roof:
            self.f.append(tuple(base + i for i in (4, 5, 6, 7)))
            for k in self.attrs:
                self.attrs[k].append(self.attrs[k][-1])
        self.roofs.append((x0, x1, y0, y1, h))

    def done(self):
        if not self.f:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.v, [], self.f)
        for k, vals in self.attrs.items():
            a = me.attributes.new(k, "FLOAT_VECTOR", "FACE")
            a.data.foreach_set("vector", [c for t in vals for c in t])
        me.materials.append(facade_mat())
        me.update()
        return gb.link(bpy.data.objects.new(self.name, me))


def style(rng, kind="low", wall=None):
    if kind == "glass":
        return dict(bay=1.5, fl=3.8, gf=5.0, lit=rng.uniform(0.12, 0.3), wm=0.04, brick=0.0, glassy=1.0,
                    tone=0.0, wall=lin3(rng.choice(PAL["concrete"])), seed=rng.uniform(0, 100), shops=False, gf_rear=5.0)
    if kind == "tower":
        return dict(bay=rng.uniform(1.5, 2.1), fl=rng.uniform(3.3, 3.7), gf=6.0, lit=rng.uniform(0.15, 0.35),
                    wm=rng.uniform(0.2, 0.3), brick=0.0, glassy=0.0, tone=float(rng.random() < 0.5),
                    wall=lin3(rng.choice(PAL["concrete"] + PAL["paint"][:4])), seed=rng.uniform(0, 100), shops=False,
                    gf_rear=6.0)
    is_brick = rng.random() < 0.38
    w = wall or rng.choice(PAL["brick"] if is_brick else PAL["paint"] + PAL["concrete"])
    return dict(bay=rng.uniform(1.9, 2.9), fl=rng.uniform(3.0, 3.4), gf=rng.uniform(4.0, 4.6),
                lit=rng.uniform(0.3, 0.6), wm=rng.uniform(0.18, 0.3), brick=1.0 if is_brick else 0.0, glassy=0.0,
                tone=float(rng.random() < 0.55), wall=lin3(w), seed=rng.uniform(0, 100), gf_rear=1.2)


def split(a, b, rng, wmin, wmax, first=None):
    """Lot boundaries from a to b (either direction): widths wmin..wmax, the first optionally fixed."""
    out, x, sgn = [], a, 1 if b > a else -1
    while abs(b - x) > 1e-6:
        w = first if (first and not out) else rng.uniform(wmin, wmax)
        if abs(b - x) - w < wmin:
            w = abs(b - x)
        out.append((x, x + sgn * w))
        x += sgn * w
    return [(min(p, q), max(p, q)) for p, q in out]


def height(rng, x, y):
    d = math.hypot(x - 5, y)
    if d < 80:
        return rng.choice((9.5, 10.5, 12.0, 12.5, 13.5, 15.0, 16.5, 18.0, 20.0))
    if d < 160:
        return rng.uniform(10, 26) if rng.random() < 0.8 else rng.uniform(26, 40)
    return rng.uniform(14, 34) if rng.random() < 0.75 else rng.uniform(34, 60)


def city_block(G, rng, x0, x1, y0, y1, sw, corner=None):
    """A block: buildings round its edges inset by its sidewalks sw = (W, E, S, N), a low fill in the middle.
    corner: {'NE'|'SE'|'NW'|'SW': (width along the N/S row, depth)} fixes that corner lot (the corner.far boxes)."""
    bx0, bx1, by0, by1 = x0 + sw[0], x1 - sw[1], y0 + sw[2], y1 - sw[3]
    far = math.hypot((x0 + x1) / 2, (y0 + y1) / 2) > 170
    wmin, wmax = (14, 30) if far else (6, 13)
    corner = corner or {}
    dN = corner.get("NE", corner.get("NW", (0, 0)))[1] or rng.uniform(13, 19)
    dS = corner.get("SE", corner.get("SW", (0, 0)))[1] or rng.uniform(13, 19)
    dN, dS = min(dN, (by1 - by0) / 2), min(dS, (by1 - by0) / 2)
    dW, dE = min(rng.uniform(13, 19), (bx1 - bx0) / 2), min(rng.uniform(13, 19), (bx1 - bx0) / 2)
    for row, (ya, yb), front in (("N", (by1 - dN, by1), "N"), ("S", (by0, by0 + dS), "S")):
        key = "NE" if row == "N" else "SE"
        keyw = "NW" if row == "N" else "SW"
        if key in corner:
            lots = split(bx1, bx0, rng, wmin, wmax, first=corner[key][0])
        elif keyw in corner:
            lots = split(bx0, bx1, rng, wmin, wmax, first=corner[keyw][0])
        else:
            lots = split(bx0, bx1, rng, wmin, wmax)
        for a, b in lots:
            sides = {front: "front", "S" if front == "N" else "N": "rear"}
            if abs(a - bx0) < 1e-6:
                sides["W"] = "front"
            if abs(b - bx1) < 1e-6:
                sides["E"] = "front"
            G.add(a, b, ya, yb, height(rng, (a + b) / 2, (ya + yb) / 2), style(rng), sides)
    for side, (xa, xb) in (("W", (bx0, bx0 + dW)), ("E", (bx1 - dE, bx1))):
        if by1 - dN - (by0 + dS) < 3:
            continue
        for a, b in split(by1 - dN, by0 + dS, rng, wmin, wmax):
            G.add(xa, xb, a, b, height(rng, (xa + xb) / 2, (a + b) / 2), style(rng),
                  {side: "front", "E" if side == "W" else "W": "rear"})
    ix0, ix1, iy0, iy1 = bx0 + dW, bx1 - dE, by0 + dS, by1 - dN
    if ix1 - ix0 > 4 and iy1 - iy0 > 4:  # yards, sheds and backs: low, roofs only from above
        G.add(ix0 + 1, ix1 - 1, iy0 + 1, iy1 - 1, rng.uniform(4, 8), style(rng), {})


# ---------------------------------------------------------------- ground: sidewalks, far ground

def slab(Bt, x0, x1, y0, y1, curbs=True):
    """A sidewalk slab (z 0..0.15) with a curb on each edge; past 70 m a plain concrete (the textured one with gum and
    cracks costs more than it shows that far off)."""
    far = math.hypot(min(abs(x0), abs(x1)) if x0 * x1 > 0 else 0, min(abs(y0), abs(y1)) if y0 * y1 > 0 else 0) > 70
    Bt["walk"].box(((x0 + x1) / 2, (y0 + y1) / 2, 0.075), (x1 - x0, y1 - y0, 0.15), mi=1 if far else 0)
    if curbs:
        # each curb's outer face 6 mm proud of the slab's side (flush, the two flickered)
        for c, s in ((((x0 + x1) / 2, y0 + 0.067), (x1 - x0 + 0.012, 0.146)),
                     (((x0 + x1) / 2, y1 - 0.067), (x1 - x0 + 0.012, 0.146)),
                     ((x0 + 0.067, (y0 + y1) / 2), (0.146, y1 - y0 + 0.012)),
                     ((x1 - 0.067, (y0 + y1) / 2), (0.146, y1 - y0 + 0.012))):
            Bt["curb"].box((c[0], c[1], 0.08), (s[0], s[1], 0.162), mi=0)


def ground(S):
    import block
    walk = Batch("city.sidewalks", [block.M("sidewalk"), mat("farwalk", "#5f5d58", grime=0.5)])
    curb = Batch("city.curbs", [block.M("curb")])
    Bt = {"walk": walk, "curb": curb}
    # the hero blocks' new edges (none overlaps block.street()'s sidewalks: x -33..45, y +-6..+-10)
    for r in ((-36, -33, -47, -6), (-33, -30, -22, -10), (45, 48, -47, -6), (42, 45, -22, -10), (-36, 48, -50, -47),
              (-36, -33, 6, 47), (-33, -32.5, 10, 28), (-10, -6.25, 10, 14), (45, 48, 6, 47), (43, 45, 10, 22.3),
              (-36, 48, 47, 50)):
        slab(Bt, *r, curbs=r not in ((-33, -30, -22, -10), (42, 45, -22, -10), (-33, -32.5, 10, 28),
                                    (-10, -6.25, 10, 14), (43, 45, 10, 22.3)))
    for (x0, x1, y0, y1) in cells():
        if (x0, x1, y0, y1) in (HERO_S, HERO_N):
            continue
        if math.hypot((x0 + x1) / 2, (y0 + y1) / 2) < 260:
            slab(Bt, x0, x1, y0, y1)
    walk.done()
    curb.done()
    # past the block's 200 m ground: one big plane of plain dark asphalt
    m = mat("farground", "#2a2b2e", grime=0.3, rough=0.6)
    gb.box("city.farground", (0, 0, -0.03), (3000, 3000, 0.04), m)
    # the alley behind the south row: patched, darker asphalt
    gb.box("city.alley", (6, -24, 0.004), (84, 4, 0.008), mat("alley", "#24231f", grime=0.6, rough=0.7))


def cells():
    xs = [BOUND[0]] + [v for r in XR for v in r] + [BOUND[1]]
    ys = [BOUND[2]] + [v for r in YR for v in r] + [BOUND[3]]
    out = []
    for i in range(0, len(xs), 2):
        for j in range(0, len(ys), 2):
            out.append((xs[i], xs[i + 1], ys[j], ys[j + 1]))
    return out


# ---------------------------------------------------------------- the hero blocks' backs and neighbours

def hero_blocks(rng):
    G = Blocks("city.bld.hero")
    # behind the south row: across the alley (y -26), lots facing the south street (y -47)
    lots = split(-33.0, 45.0, rng, 6, 12)
    for k, (a, b) in enumerate(lots):
        sides = {"N": "rear", "S": "front"}
        if k == 0:
            sides["W"] = "front"
        if k == len(lots) - 1:
            sides["E"] = "front"
        h = rng.choice((9.5, 11.0, 12.5, 14.0, 16.0, 19.0))
        G.add(a, b, -47.0, -26.0, h, style(rng), sides)
        if h >= 12.5 and b - a >= 6.5 and k % 2:  # fire escapes on the backs, over the alley
            G.fe.append(((a + b) / 2 + 0.9, -26.0, 0.0))
    # behind the park and the cemetery's back wall (y 27.45): rears face the park, fronts the north street
    for k, (a, b) in enumerate(split(-33.0, -9.4, rng, 6, 10)):
        sides = {"S": "rear", "N": "front"}
        if k == 0:
            sides["W"] = "front"
        h = rng.choice((12.5, 14.0, 15.5, 17.0)) if k % 2 else rng.choice((11.0, 12.5))
        st = style(rng)  # the park's fill light falls on these: darker walls, so they stay night
        if st["brick"] < 0.5:
            st["wall"] = tuple(c * 0.55 for c in st["wall"])
        G.add(a, b, 28.0, 47.0, h, st, sides)
        if h >= 12.5 and b - a >= 6.5:  # fire escapes on the backs, over the cemetery
            G.fe.append(((a + b) / 2 - 0.9, 28.0, math.pi))
    # wedged between the park and the tower: a low two-storey shop, front to the street (low, so the tower's west
    # face keeps the park's light)
    st = style(rng, wall="#5e6a68")
    st.update(gf=3.6, lit=0.5)
    G.add(-9.4, -6.4, 14.0, 28.0, 7.2, st, {"S": "front", "W": "rear"})
    G.add(-9.4, -6.4, 28.0, 47.0, 12.5, style(rng), {"N": "front", "S": "rear"})
    # behind the tower (its back is y 30): low and mid-rise, leaving a service lane
    for a, b in split(-6.4, 24.4, rng, 7, 12):
        G.add(a, b, 32.5, 47.0, rng.uniform(12, 24), style(rng), {"N": "front", "S": "rear"})
    # behind and beside the north shops
    lots = split(24.4, 45.0, rng, 6, 11)
    for k, (a, b) in enumerate(lots):
        sides = {"S": "rear", "N": "front"}
        if k == len(lots) - 1:
            sides["E"] = "front"
        G.add(a, b, 22.3, 47.0, rng.choice((10.5, 12.0, 13.5, 15.0, 18.0)), style(rng), sides)
    return G


def corner_style(rng, wall, brick):
    s = style(rng)
    s.update(wall=lin3(wall), brick=brick, gf=4.4, lit=0.5, bay=2.3, wm=0.24, tone=1.0)
    return s


def grid_blocks(rng):
    """Every other block of the grid, one object per block (so Eevee can cull)."""
    groups = []
    for (x0, x1, y0, y1) in cells():
        if (x0, x1, y0, y1) in (HERO_S, HERO_N):
            continue
        G = Blocks(f"city.bld.{x0:.0f}.{y0:.0f}")
        sw = [3.0, 3.0, 3.0, 3.0]
        if y1 == -6.0:
            sw[3] = 4.0
        if y0 == 6.0:
            sw[2] = 4.0
        corner = None
        if (x0, x1, y0, y1) == (-120.0, -43.0, -50.0, -6.0):
            corner = {"NE": (12.0, 14.0)}  # corner.far: x -58..-46, y -24..-10
        if (x0, x1, y0, y1) == (-120.0, -43.0, 6.0, 50.0):
            corner = {"SE": (12.0, 16.0)}  # corner.far.n: x -58..-46, y 10..26
        city_block(G, rng, x0, x1, y0, y1, sw, corner)
        groups.append(G)
    return groups


def fix_corners(groups):
    """The two corner lots across the cross street: given the corner boxes' looks and shopfronts of their own (the x =
    -46 face below 4.4 m is plain wall here, for the modelled storefronts and grunge.py's posters)."""
    for G in groups:
        for i, (x0, x1, y0, y1, h) in enumerate(G.roofs):
            for want, wall, brick, hh in (((-58, -46, -24, -10), "#6f7a84", 0.0, 15.0),
                                          ((-58, -46, 10, 26), "#6e4335", 1.0, 16.5)):
                if all(abs(p - q) < 0.01 for p, q in zip((x0, x1, y0, y1), want)):
                    fi = i * 5  # faces S, E, N, W, roof per building
                    G.v[i * 8 + 4: i * 8 + 8] = [(p[0], p[1], hh) for p in G.v[i * 8 + 4: i * 8 + 8]]
                    G.roofs[i] = (x0, x1, y0, y1, hh)
                    for k in range(5):
                        fa, fb, fc, fd = (G.attrs[n][fi + k] for n in ("fa", "fb", "fc", "fd"))
                        G.attrs["fb"][fi + k] = (4.4, hh, fb[2])
                        G.attrs["fc"][fi + k] = (0.5, 0.24 if fc[1] < 0.5 else 0.5, 0.0)
                        G.attrs["fd"][fi + k] = (brick, 0.0, 1.0)
                        G.attrs["wall"][fi + k] = lin3(wall)


# ---------------------------------------------------------------- the skyline

def skyline(rng):
    G = Blocks("city.skyline")
    spots = []
    for _ in range(46):  # downtown, north-east
        spots.append((rng.uniform(170, 520), rng.uniform(140, 560), rng.uniform(55, 175)))
    for _ in range(14):  # north and east, lower
        spots.append((rng.uniform(-150, 160), rng.uniform(260, 520), rng.uniform(40, 95)))
    for _ in range(10):
        spots.append((rng.uniform(280, 520), rng.uniform(-200, 120), rng.uniform(40, 90)))
    for _ in range(10):  # a few in the west and south, so no direction is empty
        a = rng.uniform(math.pi * 0.8, math.pi * 1.7)
        r = rng.uniform(300, 520)
        spots.append((r * math.cos(a), r * math.sin(a), rng.uniform(35, 70)))
    for x, y, h in spots:
        w, d = rng.uniform(18, 40), rng.uniform(18, 40)
        kind = "glass" if rng.random() < 0.4 else "tower"
        st = style(rng, kind)
        allf = {s: "front" for s in "NSEW"}
        G.add(x - w / 2, x + w / 2, y - d / 2, y + d / 2, h, st, allf)
        if rng.random() < 0.55:  # a setback crown
            w2, d2 = w * rng.uniform(0.55, 0.8), d * rng.uniform(0.55, 0.8)
            G.add(x - w2 / 2, x + w2 / 2, y - d2 / 2, y + d2 / 2, h + rng.uniform(8, 25), st, allf, z0=h - 0.5)
    # a low ring of city to the horizon, so the ground never ends in a hard edge
    for k in range(140):
        a = 2 * math.pi * k / 140 + rng.uniform(-0.01, 0.01)
        r = rng.uniform(560, 760)
        x, y = r * math.cos(a), r * math.sin(a)
        w = rng.uniform(25, 45)
        st = style(rng, "tower")
        st["lit"] *= 0.7
        G.add(x - w / 2, x + w / 2, y - w / 2, y + w / 2, rng.uniform(15, 45), st, {s: "front" for s in "NSEW"})
    return G


# ---------------------------------------------------------------- storefronts across the cross street

def storefront(name, c, w, facing, rng, sign, lit=True, shutter=False, awning=None, tags=None):
    """A modelled shopfront on a facade (c = the facade point at ground level, centre of the shop; facing = the
    outward axis '+X', '-Y'...). Proud of the wall by 0.25 m: pilasters, bulkhead, lit or dark window with shelf
    shapes, door, sign band with lettering, optional awning and roll-down shutter."""
    import block
    rot = {"+X": -math.pi / 2, "-X": math.pi / 2, "+Y": 0.0, "-Y": math.pi}[facing]
    root = gb.empty(name, c)
    root.rotation_euler.z = rot
    trim = mat("sf.trim", "#2a2724", grime=0.6)
    dark = mat("sf.dark", "#121212", grime=0.2)
    bt = Batch(f"{name}.frame", [trim, dark, mat("sf.bulk", "#5b5249", grime=0.7)])
    win_w = w - 1.9
    bt.box((-w / 2 + 0.2, 0.12, 2.1), (0.4, 0.25, 4.2))  # pilasters
    bt.box((w / 2 - 0.2, 0.12, 2.1), (0.4, 0.25, 4.2))
    bt.box((-0.75, 0.12, 0.3), (win_w, 0.25, 0.6), mi=2)  # bulkhead
    bt.box((-0.75, 0.12, 3.05), (win_w, 0.25, 0.1))  # transom bar
    bt.box((w / 2 - 0.85, 0.06, 1.25), (1.0, 0.1, 2.5), mi=1)  # door
    bt.box((w / 2 - 1.4, 0.12, 1.5), (0.12, 0.25, 3.0))
    bt.box((0, 0.2, 3.65), (w, 0.4, 0.9))  # the sign band's box
    o = bt.done()
    o.parent = root
    on = night_ctl()
    if shutter:
        sh = gb.box(f"{name}.shutter", (-0.75, 0.2, 1.75), (win_w, 0.06, 2.6), block.M("shutter", metal=0.4, rough=0.5),
                    parent=root)
        if tags:
            import grunge
            grunge.decal(f"{name}.tag", rng.choice(tags), (-0.75 + rng.uniform(-0.5, 0.5), 0.235, 1.3),
                         (min(2.0, win_w - 0.2), 1.0), parent=root, facing="+Y", tilt=rng.uniform(-0.1, 0.1))
    else:
        col = "#ffd9a0" if rng.random() < 0.6 else "#e6f0ff"
        back = gb.plane(f"{name}.back", (-0.75, 0.02, 1.75), (win_w, 2.5),
                        gb.glow_mat(f"city.sf.{name}", col, 1.1 if lit else 0.0, on, "on", base="#1a1816"),
                        parent=root, facing="+Y")
        sb = Batch(f"{name}.stock", [dark, mat("sf.stock", "#8a7a5c", grime=0.2), mat("sf.stock2", "#3f5a6b", grime=0.2)])
        for k in range(3):  # shelves and stock against the light
            z = 0.9 + k * 0.6
            sb.box((-0.75, 0.06, z), (win_w - 0.3, 0.06, 0.03))
            x = -0.75 - win_w / 2 + 0.3
            while x < -0.75 + win_w / 2 - 0.3:
                bw = rng.uniform(0.12, 0.3)
                sb.box((x + bw / 2, 0.07, z + 0.12), (bw, 0.04, rng.uniform(0.12, 0.3)), mi=rng.choice((0, 1, 1, 2)))
                x += bw + rng.uniform(0.02, 0.15)
        s = sb.done()
        s.parent = root
        gb.plane(f"{name}.glass", (-0.75, 0.2, 1.75), (win_w, 2.5), sf_glass(), parent=root, facing="+Y")
    sc = rng.choice(["#d9cfb4", "#2e3b57", "#3d5a4a", "#e6e1d3"])
    ink = "#1b1b1b" if sc in ("#d9cfb4", "#e6e1d3") else "#efe6cf"
    gb.plane(f"{name}.signface", (0, 0.415, 3.65), (w - 0.2, 0.75),  # 15 mm off the band (5 mm flickered far off)
             gb.glow_mat(f"city.sign.{sc}.{lit}", sc, 0.35 if lit else 0.0, on, "on", base=sc), parent=root, facing="+Y")
    gb.text(f"{name}.sign", sign, 0.38 if len(sign) < 12 else 0.28, mat(f"ink{ink}", ink, grime=0.0),
            (0, 0.43, 3.65), facing="+Y", parent=root)
    if awning:
        a = gb.box(f"{name}.awning", (-0.3, 0.76, 3.0), (w - 0.6, 1.4, 0.05), mat(f"awn{awning}", awning, grime=0.5),
                   parent=root)
        a.rotation_euler.x = -0.38
        gb.box(f"{name}.valance", (-0.3, 1.42, 2.62), (w - 0.6, 0.03, 0.3), mat(f"awn{awning}", awning), parent=root)
    return root


def sf_glass():
    """Shop glass: faint and glossy, dithered (cheaper than blended, and these are only seen across the street)."""
    m = bpy.data.materials.get("city.sf.glass")
    if m is None:
        m = gb.mat("city.sf.glass", "#9fb6c4", rough=0.05, alpha=0.15)
        m.surface_render_method = "DITHERED"
    return m


def corners(S, rng, fe):
    """Across the cross street from the corner: the corner.far boxes' replacements get modelled ground floors."""
    for n in ("corner.far", "corner.far.n"):
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = o.hide_viewport = True
    tags = sorted(p.stem for p in (gb.ROOT / "assets" / "gen" / "grunge").glob("tag_*.png"))
    # south-west corner building (x -58..-46, y -24..-10): the x = -46 face carries grunge.py's throw-up and posters at
    # y -17..-10, so its storefront sits south of them
    storefront("city.sf.sw1", (-46.0, -21.2, 0.0), 5.4, "+X", rng, "LAUNDRY", lit=True, awning="#2f4a3a")
    storefront("city.sf.sw2", (-49.2, -10.0, 0.0), 5.4, "+Y", rng, "GROCERY · DELI", lit=True, awning="#2a3550")
    storefront("city.sf.sw3", (-55.0, -10.0, 0.0), 5.6, "+Y", rng, "CHECKS CASHED", lit=False, shutter=True,
               tags=tags)
    # north-west corner (x -58..-46, y 10..26)
    storefront("city.sf.nw1", (-46.0, 13.4, 0.0), 5.6, "+X", rng, "DONUTS", lit=True, awning="#8a7350")
    storefront("city.sf.nw2", (-46.0, 19.6, 0.0), 5.6, "+X", rng, "SHOE REPAIR", lit=False, shutter=True, tags=tags)
    storefront("city.sf.nw3", (-52.0, 10.0, 0.0), 5.8, "-Y", rng, "PHO · NOODLES", lit=True, awning="#3d4f5c")
    # the hotel's blade sign on the south-west corner (an SRO hotel over the shops): warm neon, not red
    on = night_ctl()
    blade = mat("blade", "#1e1d1c", grime=0.4)
    gb.box("city.hotel.blade", (-45.35, -11.6, 8.2), (1.3, 0.22, 5.4), blade)
    for k, ch in enumerate("HOTEL"):
        for sgn in (-1, 1):
            gb.text(f"city.hotel.{k}.{sgn}", ch, 0.75, gb.glow_mat("city.neon.hotel", "#ffe6b0", 9.0, on, "on",
                                                                    base="#4a443a"),
                    (-45.3, -11.6 + sgn * 0.115, 10.3 - k * 1.0), facing="+Y" if sgn > 0 else "-Y")
    gb.box("city.hotel.bracket", (-45.8, -11.6, 10.95), (0.6, 0.08, 0.08), blade)
    # fire escapes on the corner buildings' street faces (grunge.fire_escape's, merged to one mesh each)
    import grunge
    for name, loc, rz in (("city.fe.sw", (-46.0, -15.8, 0.0), -math.pi / 2), ("city.fe.nw", (-46.0, 22.0, 0.0), -math.pi / 2),
                          ("city.fe.nw2", (-50.6, 10.0, 0.0), math.pi)):
        root = gb.empty(name, loc)
        root.rotation_euler.z = rz
        bpy.context.view_layer.update()
        grunge.fire_escape(root, name, rng)
        merge_children(root, name + ".mesh")
    for k, (x, y, rz) in enumerate(fe):
        name = f"city.fe.back{k}"
        root = gb.empty(name, (x, y, 0.0))
        root.rotation_euler.z = rz
        bpy.context.view_layer.update()
        grunge.fire_escape(root, name, rng)
        merge_children(root, name + ".mesh")


def merge_children(root, name):
    """Join root's mesh children into one object (world space), removing them."""
    bm = bmesh.new()
    mats = []
    bpy.context.view_layer.update()
    kids = [o for o in root.children_recursive if o.type == "MESH"]
    for o in kids:
        tmp = o.data.copy()
        tmp.transform(o.matrix_world)
        for p in tmp.polygons:
            m = tmp.materials[p.material_index] if tmp.materials else None
            if m not in mats:
                mats.append(m)
        remap = [mats.index(m) for m in tmp.materials] if tmp.materials else [0]
        for p in tmp.polygons:
            p.material_index = remap[p.material_index]
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    for o in kids:
        bpy.data.objects.remove(o)
    return gb.link(bpy.data.objects.new(name, me))


# ---------------------------------------------------------------- lamps on the far streets

def far_lamps(rng):
    on = night_ctl()
    pole = Batch("city.lamps.poles", [mat("lamppole", "#2c2b29", grime=0.5, metal=0.4, rough=0.6)])
    head = Batch("city.lamps.heads", [gb.glow_mat("city.lamphead", gb.LOOK["palette"]["sodium"], 18.0, on, "on",
                                                  base="#3a3530")])
    pool = Batch("city.lamps.pools", [pool_mat()], uv=True)
    spots = []
    for (a, b) in XR:  # along the north-south roads, both sides, alternating
        for k, y in enumerate(range(-200, 201, 26)):
            if -12 < y < 12:
                continue
            side = 1 if k % 2 else -1
            x = (b + 0.6) if side > 0 else (a - 0.6)
            spots.append((x, y + (13 if side > 0 else 0), -side, 0))
    for (a, b) in YR:
        for k, x in enumerate(range(-200, 211, 26)):
            if b == 6.0 and -46 < x < 58:
                continue  # the block's own lamps
            if any(r0 - 3 < x < r1 + 3 for r0, r1 in XR):
                continue
            side = 1 if k % 2 else -1
            y = (b + 0.6) if side > 0 else (a - 0.6)
            spots.append((x, y, 0, -side))
    real = ((-43.4, -15.0), (-43.4, 17.0))
    for x, y, dx, dy in spots:
        if math.hypot(x, y) > 230 or (dx and abs(y) < 12) or any(math.hypot(x - a, y - b) < 9 for a, b in real):
            continue
        pole.cyl((x, y, 3.0), 0.09, 6.0, n=8)
        hx, hy = x + dx * 1.8, y + dy * 1.8
        pole.box(((x + hx) / 2, (y + hy) / 2, 6.0), (abs(hx - x) + 0.08, abs(hy - y) + 0.08, 0.08))
        head.box((hx, hy, 5.9), (0.5 if dx else 0.3, 0.3 if dx else 0.5, 0.12))
        r = 5.5
        pool.quad([(hx - r, hy - r, 0.17), (hx + r, hy - r, 0.17), (hx + r, hy + r, 0.17), (hx - r, hy + r, 0.17)])
    pole.done()
    head.done()
    pool.done()
    # two real lights on the cross street, over the corner buildings' shopfronts (S01e, S02)
    for k, (px, y) in enumerate(real):
        x = px + 1.7
        ld = bpy.data.lights.new(f"city.lamp{k}.light", "SPOT")
        ld.energy, ld.spot_size, ld.spot_blend = gb.LOOK["lights"]["lamp_w"] * 0.8, math.radians(115), 0.6
        ld.color = lin3(gb.LOOK["palette"]["sodium"])
        ld.use_custom_distance, ld.cutoff_distance = True, 28.0  # its pool only: fewer shadow pages
        lo = gb.link(bpy.data.objects.new(f"city.lamp{k}.light", ld))
        lo.location = (x, y, 5.7)
        key_night(ld, "energy", 0.0, ld.energy)
        gb.cyl(f"city.lamp{k}.pole", (px, y, 3.0), 0.09, 6.0, mat("lamppole", "#2c2b29"))
        gb.box(f"city.lamp{k}.arm", ((px + x) / 2, y, 6.0), (1.7, 0.08, 0.08), mat("lamppole", "#2c2b29"))
        gb.box(f"city.lamp{k}.head", (x, y, 5.9), (0.5, 0.3, 0.12), head.mats[0])


def pool_mat():
    """A soft sodium pool of light on the ground under a far lamp: emission fading out radially, see-through."""
    m = bpy.data.materials.new("city.lamppool")
    m.use_nodes = True
    m.surface_render_method = "DITHERED"
    nt = m.node_tree
    B = NB(nt)
    out = nt.nodes["Material Output"]
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tc = B.n("ShaderNodeTexCoord")
    # the quad's generated coordinates run 0..1; distance from the centre
    d = B.n("ShaderNodeVectorMath", operation="DISTANCE")
    B.link(tc.outputs["UV"], d.inputs[0])
    d.inputs[1].default_value = (0.5, 0.5, 0.0)
    fall = B.m("POWER", B.sub(1.0, B.m("MINIMUM", B.mul(d.outputs["Value"], 2.0), 1.0)), 2.2)
    night = B.value("night", 1.0)
    em = B.n("ShaderNodeEmission")
    em.inputs["Color"].default_value = gb.lin(gb.LOOK["palette"]["sodium"])
    em.inputs["Strength"].default_value = 1.0
    tr = B.n("ShaderNodeBsdfTransparent")
    add = B.n("ShaderNodeAddShader")
    nt.links.new(tr.outputs[0], add.inputs[0])
    sc = B.n("ShaderNodeMixShader")  # emission weight = falloff * night * 0.35, on top of full transparency
    B.link(B.mul(B.mul(fall, night), 0.35), sc.inputs[0])
    zero = B.n("ShaderNodeEmission")
    zero.inputs["Strength"].default_value = 0.0
    nt.links.new(zero.outputs[0], sc.inputs[1])
    nt.links.new(em.outputs[0], sc.inputs[2])
    nt.links.new(sc.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    key_night(nt, 'nodes["night"].outputs[0].default_value')
    return m


# ---------------------------------------------------------------- rooftops

def moonlit(m, hexcol, k=0.12):
    """The stand-in moon (FAKE_MOON) on a plain material: a faint cool self-light in its own colour, by night."""
    if m.get("moonlit") or not FAKE_MOON:
        return m
    b = m.node_tree.nodes["Principled BSDF"]
    c = gb.lin(hexcol)
    b.inputs["Emission Color"].default_value = (c[0] * 0.55, c[1] * 0.66, c[2], 1.0)
    key_night(m.node_tree, 'nodes["Principled BSDF"].inputs["Emission Strength"].default_value', 0.0, k * FAKE_MOON)
    m["moonlit"] = 1
    return m


def rooftop_mats():
    out = []
    for key, hexcol, kw in (("roof.metal", "#8b9094", dict(grime=0.6, metal=0.5, rough=0.5)),  # 0 HVAC, vents, ducts
                            ("roof.dark", "#2c2b2a", dict(grime=0.4, rough=0.8)),  # 1 grilles, tar, door
                            ("roof.wood", "#6a5038", dict(grime=0.7, rough=0.85)),  # 2 water tank staves
                            ("roof.concrete", "#7d786e", dict(grime=0.7)),  # 3 coping, bulkheads
                            ("roof.brick", "#6e4a3c", dict(grime=0.7)),  # 4 chimneys
                            ("roof.steel", "#3a3633", dict(grime=0.6, metal=0.5, rough=0.6)),  # 5 stands, antennas
                            ("roof.sky", "#7f95a3", dict(grime=0.5, rough=0.2))):  # 6 skylight glass
        out.append(moonlit(mat(key, hexcol, **kw), hexcol, 0.3 if key != "roof.metal" else 0.15))
    return out


def clutter(R, rng, x0, x1, y0, y1, z, dense=1.0, front=None):
    """Rooftop things on a roof (x0..x1, y0..y1) at height z, kept back from the front edge `front` ('S' etc.)."""
    m = 0.8
    fx0, fx1, fy0, fy1 = x0 + m, x1 - m, y0 + m, y1 - m
    if front == "N":
        fy1 -= 2.0
    if front == "S":
        fy0 += 2.0
    if fx1 - fx0 < 2 or fy1 - fy0 < 2:
        return

    def spot(w, d):
        return (rng.uniform(fx0 + w / 2, max(fx0 + w / 2, fx1 - w / 2)), rng.uniform(fy0 + d / 2, max(fy0 + d / 2, fy1 - d / 2)))

    area = (fx1 - fx0) * (fy1 - fy0)
    for _ in range(max(1, int(area / 45 * dense))):  # HVAC units: a box with a fan grille on top
        w, d, h = rng.uniform(1.0, 2.2), rng.uniform(0.8, 1.4), rng.uniform(0.7, 1.2)
        x, y = spot(w, d)
        R.box((x, y, z + h / 2), (w, d, h), mi=0)
        R.cyl((x, y, z + h + 0.01), min(w, d) * 0.35, 0.02, mi=1, n=10)
        if rng.random() < 0.5:  # a duct to the roof
            R.box((x, y - d / 2 - 0.6, z + 0.25), (0.35, 1.2, 0.35), mi=0)
    for _ in range(int(rng.uniform(2, 6) * dense)):  # vent pipes with caps
        x, y = spot(0.3, 0.3)
        h = rng.uniform(0.5, 1.4)
        R.cyl((x, y, z + h / 2), 0.07, h, mi=0, n=8)
        R.cyl((x, y, z + h + 0.05), 0.14, 0.1, mi=0, n=8, r2=0.02)
    if rng.random() < 0.5 * dense:  # a stair bulkhead with its door
        w, d, h = 2.4, 3.2, 2.6
        x, y = spot(w, d)
        R.box((x, y, z + h / 2), (w, d, h), mi=3)
        R.box((x, y - d / 2 - 0.02, z + 1.05), (0.9, 0.04, 2.0), mi=1)
        R.box((x, y, z + h + 0.05), (w + 0.2, d + 0.2, 0.1), mi=1)
    if rng.random() < 0.28 * dense:  # a water tank on its stand
        r, h = rng.uniform(1.2, 1.7), rng.uniform(2.2, 3.0)
        x, y = spot(2 * r, 2 * r)
        for a in range(4):
            ang = math.pi / 4 + a * math.pi / 2
            R.box((x + 0.75 * r * math.cos(ang), y + 0.75 * r * math.sin(ang), z + 1.0), (0.15, 0.15, 2.0), mi=5)
        R.box((x, y, z + 2.05), (1.8 * r, 1.8 * r, 0.12), mi=5)
        R.cyl((x, y, z + 2.1 + h / 2), r, h, mi=2, n=16)
        for hz in (0.25, 0.5, 0.75):  # the hoops
            R.cyl((x, y, z + 2.1 + h * hz), r + 0.025, 0.05, mi=5, n=16, caps=False)
        R.cyl((x, y, z + 2.1 + h + 0.4), r + 0.08, 0.8, mi=1, n=16, r2=0.08)
    if rng.random() < 0.4 * dense:  # chimneys
        for _ in range(rng.randint(1, 3)):
            x, y = spot(0.7, 0.7)
            h = rng.uniform(0.9, 2.0)
            R.box((x, y, z + h / 2), (0.6, 0.6, h), mi=4)
            R.box((x, y, z + h + 0.05), (0.7, 0.7, 0.1), mi=3)
    if rng.random() < 0.3 * dense:  # a skylight
        x, y = spot(1.6, 1.2)
        R.box((x, y, z + 0.2), (1.6, 1.2, 0.4), mi=3)
        R.box((x, y, z + 0.42), (1.4, 1.0, 0.06), mi=6)
    if rng.random() < 0.25 * dense:  # an antenna mast
        x, y = spot(0.3, 0.3)
        h = rng.uniform(2.5, 4.5)
        R.cyl((x, y, z + h / 2), 0.03, h, mi=5, n=6)
        for k in range(3):
            R.box((x, y, z + h * (0.6 + 0.13 * k)), (1.2 - 0.3 * k, 0.03, 0.03), mi=5)
    if rng.random() < 0.3 * dense:  # a satellite dish on a short mast
        x, y = spot(0.8, 0.8)
        R.cyl((x, y, z + 0.5), 0.03, 1.0, mi=5, n=6)
        R.cyl((x, y + 0.1, z + 1.1), 0.4, 0.12, mi=0, n=14, r2=0.2,
              rot=Matrix.Rotation(1.1, 4, "X").to_euler())


def block_roofs(rng):
    """The block's own roofs (the south row and the north shops, z 11): parapets of varied heights with coping, a
    cornice along the street, and rooftop clutter. Nothing on the tower."""
    import block
    R = Batch("city.roofs.block", rooftop_mats())
    walls = {"brick": Batch("city.parapet.brick", [block.M("brick")]),
             "stucco": Batch("city.parapet.stucco", [block.M("stucco")]),
             "stucco2": Batch("city.parapet.stucco2", [block.M("stucco2")])}
    trim = Batch("city.cornice", [block.M("trim"), rooftop_mats()[3]])
    rows = [(i, x, -1) for i, (x, _, _) in enumerate(block.SHOPS)] + \
           [(len(block.SHOPS) + k, x, 1) for k, (x, _, _) in enumerate(block.NORTH_SHOPS)]
    for i, x, side in rows:
        wall = "brick" if i % 3 == 0 else "stucco" if i % 3 == 1 else "stucco2"
        fy = 10.0 * side  # the facade plane
        by = fy + side * 12.0  # the back
        ph = rng.choice((0.7, 0.9, 1.1, 1.4, 1.8, 2.2))
        if i == 4:  # the pawn shop: a stepped false front
            ph = 2.6
        y0, y1 = sorted((fy, by))
        t = 0.25
        # front parapet flush with the facade (a continuation of it), sides and back lower
        walls[wall].box((x, fy + side * t / 2, 11 + ph / 2), (6.0, t, ph))
        for sx in (x - 3 + t / 2, x + 3 - t / 2):
            walls[wall].box((sx, (y0 + y1) / 2, 11 + 0.45), (t, 12.0, 0.9))
        walls[wall].box((x, by - side * t / 2, 11 + 0.45), (6.0, t, 0.9))
        # cornice: a projecting band at the roofline, and coping on the parapet
        out = -side  # toward the street
        trim.box((x, fy + out * 0.17, 11.1), (6.0, 0.34, 0.22), mi=0)
        trim.box((x, fy + out * 0.1, 11.3), (6.0, 0.2, 0.12), mi=0)
        for k in range(10):  # brackets (corbels) under the cornice
            trim.box((x - 2.7 + k * 0.6, fy + out * 0.12, 10.9), (0.1, 0.24, 0.2), mi=0)
        trim.box((x, fy + side * t / 2, 11 + ph + 0.05), (6.1, 0.4, 0.1), mi=1)
        # the roof's clutter, kept back from the street edge
        clutter(R, rng, x - 3 + t, x + 3 - t, y0 + t, y1 - t, 11.0, dense=1.3, front="N" if side < 0 else "S")
    for b in walls.values():
        b.done()
    trim.done()
    R.done()
    # tar roofs over the shops (the upper boxes' tops are the bare grey-box material): a dark membrane just above
    tar = moonlit(mat("tar", "#5a5751", grime=0.6, rough=0.9), "#5a5751", 0.3)
    gb.box("city.roof.membrane.s", (6, -16, 11.005), (72, 12, 0.01), tar)
    gb.box("city.roof.membrane.n", (34, 16, 11.005), (18, 12, 0.01), tar)
    # the south row's open undercroft behind the shops' rooms (y -22..-16.3, under the upper storeys), filled
    gb.box("city.backrooms.s", (6, -19.15, 2.1), (72, 5.7, 4.2), block.M("stucco"))
    gb.box("city.backrooms.n", (34, 19.15, 2.1), (18, 5.7, 4.2), block.M("stucco"))


def city_roofs(rng, groups):
    R = Batch("city.roofs.city", rooftop_mats())
    for G in groups:
        for (x0, x1, y0, y1, h) in G.roofs:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if math.hypot(cx, cy) > 110 or h < 6:
                continue
            clutter(R, rng, x0, x1, y0, y1, h, dense=0.65)
            # parapet coping lip all round: a slightly raised dark edge
            for c, s in ((((x0 + x1) / 2, y0 + 0.12), (x1 - x0, 0.24)), (((x0 + x1) / 2, y1 - 0.12), (x1 - x0, 0.24)),
                         ((x0 + 0.12, (y0 + y1) / 2), (0.24, y1 - y0)), ((x1 - 0.12, (y0 + y1) / 2), (0.24, y1 - y0))):
                R.box((c[0], c[1], h + 0.35), (s[0], s[1], 0.7), mi=3, bottom=False)
    R.done()


# ---------------------------------------------------------------- build and sky

def build(S):
    rng = random.Random(SEED)
    ground(S)
    groups = [hero_blocks(rng)] + grid_blocks(rng)
    fix_corners(groups)
    for G in groups:
        G.done()
    skyline(rng).done()
    corners(S, rng, groups[0].fe)
    far_lamps(rng)
    block_roofs(rng)
    city_roofs(rng, groups)
    shadows_near_only()


def shadows_near_only(r=75.0):
    """Far things cast no shadows: none would land where a camera looks, and every light (the moon's sun most) would
    otherwise render them into its shadow maps each motion-blur step. Flat things (sidewalks, ground, paint, pools)
    cast none either."""
    flat = ("city.sidewalks", "city.curbs", "city.farground", "city.alley", "city.lamps.pools", "street.paint",
            "city.roof.membrane.s", "city.roof.membrane.n")
    for o in bpy.data.objects:
        if o.type != "MESH" or not (o.name.startswith(("city.", "car", "street.")) or o.name in flat):
            continue
        if o.name in flat or o.name == "city.skyline":
            o.visible_shadow = False
            continue
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        cx = min(max(5.0, min(p.x for p in bb)), max(p.x for p in bb))  # the bbox's nearest point to the block
        cy = min(max(0.0, min(p.y for p in bb)), max(p.y for p in bb))
        near = math.hypot(cx - 5.0, cy)
        if near > r:
            o.visible_shadow = False

def sky(world):
    """The night's city glow: a Background of its own, warm and dim at the horizon fading to the night blue overhead,
    with a faint low-cloud texture; mixed in over shots.light()'s keyed sky by a factor keyed 0 by day, 1 by night.
    Rays that light the scene see it at a third of its strength, so the shadows stay blue."""
    nt = world.node_tree
    B = NB(nt)
    out = nt.nodes["World Output"]
    bg = nt.nodes["Background"]
    tc = B.n("ShaderNodeTexCoord")
    dx, dy, dz = B.sep(tc.outputs["Generated"])
    # elevation: 0 at the horizon, 1 overhead
    low = B.m("POWER", B.sub(1.0, B.m("MINIMUM", B.m("MAXIMUM", B.div(dz, 0.75), 0.0), 1.0)), 1.8)
    night = gb.lin(gb.LOOK["palette"]["night"])
    top = tuple(c * gb.LOOK["lights"]["night_sky"] for c in night[:3])
    glow = (0.07, 0.04, 0.021)  # a brownish sodium haze in the cloud deck, dim
    # the low cloud: noise in a plane-projected sky (perspective of a cloud deck), stronger near the horizon
    q = B.m("MAXIMUM", B.add(dz, 0.06), 0.02)
    cl = B.noise(B.comb(B.div(dx, q), B.div(dy, q), 0.0), 0.9, 4.0)
    cloud = B.m("MULTIPLY", B.sub(cl, 0.35), 1.8, clamp=True)
    k = B.add(B.mul(low, 0.85), B.mul(B.mul(cloud, B.add(low, 0.25)), 0.35))
    col = B.mix(k, top, glow)
    # below the horizon (only ever seen past the far ground's edge): the haze colour
    col = B.mix(B.lt(dz, 0.0), col, (0.03, 0.022, 0.018))
    bg2 = B.n("ShaderNodeBackground")
    B.link(col, bg2.inputs["Color"])
    bg2.inputs["Strength"].default_value = 1.0
    lp = B.n("ShaderNodeLightPath")
    fac = B.value("cityglow", 1.0)
    f = B.mul(fac, B.add(0.33, B.mul(lp.outputs["Is Camera Ray"], 0.67)))
    mix = B.n("ShaderNodeMixShader")
    B.link(f, mix.inputs[0])
    nt.links.new(bg.outputs[0], mix.inputs[1])
    nt.links.new(bg2.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    key_night(nt, 'nodes["cityglow"].outputs[0].default_value')
