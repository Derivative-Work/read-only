"""Detail pass: the pocket park and the cemetery behind it (see detail.py). The final look only.

A real, slightly neglected city pocket park at night, with an old cemetery behind it (S34-S39e):
  ground     a lumpy lawn over block.park()'s flat plane: grass and packed dirt mixed by a worn-ness mask (the paths,
             the trampled ground round the coffin and the fresh plots, bare patches under the trees); short grass on
             the lawn, long tufts along the fences, walls and stones; decomposed-granite pebbles on the paths
  iron       pickets with spear finials, a bottom rail and post caps on block.park()'s rail-and-post fence (none in
             front of the doghouse: lost years ago, a few stubs and one bent picket in the grass, so S38 reads its
             sign);
             gate posts and the two leaves folded back open; an old railing on a kerb, with a gate hanging open, between
             the park and the east plots
  green      shaggy hedges (a dark core under leaf cards) behind the good bots' row and along the fences, CC0 shrubs
             and grass clumps, three CC0 trees thinned to late-autumn (and a quarter of the file's 1.9 M leaf triangles)
  furniture  two cast-iron benches, a bin, one dim park lamp (the only light added: the moon fill already exists)
  cemetery   an old brick boundary wall with coping and piers (west, back, east); weathered blank stones (and a few
             with worn-away lettering) round the edges, an obelisk and an urn; the fresh plots as real earth mounds,
             the open grave with a dirt lip, boards and its spoil heap
  leaves     more dead leaves, drifted against the walls, fences and stones

Kept clear: every inscribed stone and its camera (S39b-S39e), the coffin and the good-bot stone (S34-S36), the lantern
row along the fence (S37), the doghouse (S38), the sidewalk (S39) and the field of 144,926 markers (S39c). The extra
stones carry no readable text. Nothing here moves an existing object. Seeded, so every render matches.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

import gb
import kit

SEED = 20261031
X0, X1, Y0, Y1 = -32.0, -10.0, 10.5, 27.0
FIELD = (-31.2, -17.0, 22.2, 26.6)  # the 144,926 markers (block.park)
GATE = (-22.0, -20.0)
DOG_GAP = (-19.75, -17.8)  # no pickets: S38 reads the doghouse's sign through the fence
STONES = [(-31.0 + k * 1.1, 18.8) for k in range(6)] + [(-28.0, 21.0), (-24.5, 21.5)] + \
    [(-15.6, 19.0), (-14.2, 19.6), (-15.2, 20.6), (-13.6, 21.0)] + [(-15.4, 24.0), (-13.4, 24.0), (-11.6, 25.6)]
PLOTS = [(-15.4, 22.8), (-13.4, 22.8)]
HOLE = (-11.6, 24.3)
SPOIL = (-10.65, 24.3)
COFFIN = (-21.0, 13.8)
TREES = [(-28.6, 14.7, 1.35, 2.3), (-12.3, 15.5, 1.25, 4.4), (-31.1, 20.7, 1.45, 0.4)]  # trunk x, y, scale, turn
BENCHES = [(-31.0, 14.3, 0.0), (-11.0, 13.6, math.pi)]  # x, y, facing (0: faces +X)
LAMP = (-25.2, 13.3)
# the paths: (points, width)
PATHS = [([(-21.0, 10.0), (-21.0, 12.6)], 1.5),
         ([(-20.3, 12.6), (-17.6, 13.4), (-15.3, 15.0), (-13.2, 16.8), (-12.3, 18.1), (-12.6, 19.8), (-13.6, 21.4)],
          1.0),
         ([(-21.7, 12.6), (-24.4, 13.4), (-26.8, 14.8), (-28.3, 16.4), (-28.6, 17.8)], 1.0),
         ([(-31.4, 17.9), (-25.0, 17.9)], 0.9)]


# ---------------------------------------------------------------- materials

def tex(key, tex_id, scale, tint=None, rough=1.0, attr=False):
    """gb.tex_mat with its own scale and tint (box-projected in object space; every object here sits at the origin,
    so that is world space); attr=True multiplies the base colour by the mesh's "col" attribute (per-piece
    variation)."""
    name = f"park.{key}"
    if name in gb._MATS:
        return gb._MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    mp = _proj(nt, scale)
    d = _img(nt, mp, tex_id, "diff", False)
    col = d.outputs["Color"]
    for mul in ([gb.lin(tint)] if tint else []) + (["attr"] if attr else []):
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(col, mix.inputs["A"])
        if mul == "attr":
            a = nt.nodes.new("ShaderNodeAttribute")
            a.attribute_name = "col"
            nt.links.new(a.outputs["Color"], mix.inputs["B"])
        else:
            mix.inputs["B"].default_value = mul
        col = mix.outputs["Result"]
    nt.links.new(col, b.inputs["Base Color"])
    r = _img(nt, mp, tex_id, "rough", True)
    mm = nt.nodes.new("ShaderNodeMath")
    mm.operation = "MULTIPLY"
    mm.inputs[1].default_value = rough
    nt.links.new(r.outputs["Color"], mm.inputs[0])
    nt.links.new(mm.outputs[0], b.inputs["Roughness"])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(_img(nt, mp, tex_id, "nor", True).outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    gb._MATS[name] = m
    return m


def _proj(nt, scale):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / scale,) * 3
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    return mp


def _img(nt, mp, tex_id, mapname, noncolor):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(str(gb.TEX / tex_id / f"{mapname}.jpg"), check_existing=True)
    if noncolor:
        n.image.colorspace_settings.name = "Non-Color"
    n.projection, n.projection_blend = "BOX", 0.25
    nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
    return n


def attr_mat(key, rough=0.7, bump=0.0, bump_scale=30.0, up=False):
    """Base colour from the mesh's "col" attribute (grass blades, leaves, pebbles, hedges)."""
    name = f"park.{key}"
    if name in gb._MATS:
        return gb._MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    a = nt.nodes.new("ShaderNodeAttribute")
    a.attribute_name = "col"
    col = a.outputs["Color"]
    if bump:  # leafy: a broken noise darkens the gaps and bumps the surface
        n = nt.nodes.new("ShaderNodeTexVoronoi")
        n.inputs["Scale"].default_value = bump_scale
        g = nt.nodes.new("ShaderNodeNewGeometry")
        nt.links.new(g.outputs["Position"], n.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        nt.links.new(n.outputs["Distance"], mr.inputs["Value"])
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.0, 0.6
        mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 1.0, 0.35
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(col, mix.inputs["A"])
        nt.links.new(mr.outputs["Result"], mix.inputs["B"])
        col = mix.outputs["Result"]
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        nt.links.new(n.outputs["Distance"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(col, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if up:  # thin blades lit like the ground they grow from, not edge-on
        nv = nt.nodes.new("ShaderNodeCombineXYZ")
        nv.inputs["Z"].default_value = 1.0
        nt.links.new(nv.outputs[0], b.inputs["Normal"])
        b.inputs["Specular IOR Level"].default_value = 0.15
    gb._MATS[name] = m
    return m


def terrain_mat():
    """The lawn: the CC0 grass and dry-ground textures mixed by the mesh's "bare" attribute, broken up by noise."""
    name = "park.terrain"
    if name in gb._MATS:
        return gb._MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes.new, nt.links.new
    b = nt.nodes["Principled BSDF"]
    mpg = _proj(nt, 2.5)
    gd, gn = _img(nt, mpg, "grass_ground", "diff", False), _img(nt, mpg, "grass_ground", "nor", True)
    a = N("ShaderNodeAttribute")
    a.attribute_name = "bare"
    noi = N("ShaderNodeTexNoise")
    noi.inputs["Scale"].default_value, noi.inputs["Detail"].default_value = 3.0, 8.0
    g = N("ShaderNodeNewGeometry")
    L(g.outputs["Position"], noi.inputs["Vector"])
    add = N("ShaderNodeMath")
    add.operation = "ADD"
    L(a.outputs["Fac"], add.inputs[0])
    sub = N("ShaderNodeMath")
    sub.operation = "SUBTRACT"
    L(noi.outputs["Fac"], sub.inputs[0])
    sub.inputs[1].default_value = 0.5
    L(sub.outputs[0], add.inputs[1])
    fac = N("ShaderNodeMapRange")
    L(add.outputs[0], fac.inputs["Value"])
    fac.inputs["From Min"].default_value, fac.inputs["From Max"].default_value = 0.35, 0.65

    def tint(sock, hexcol):
        mx = N("ShaderNodeMix")
        mx.data_type, mx.blend_type = "RGBA", "MULTIPLY"
        mx.inputs["Factor"].default_value = 1.0
        L(sock, mx.inputs["A"])
        mx.inputs["B"].default_value = gb.lin(hexcol)
        return mx.outputs["Result"]
    mix = N("ShaderNodeMix")
    mix.data_type = "RGBA"
    L(fac.outputs["Result"], mix.inputs["Factor"])
    L(tint(gd.outputs["Color"], "#8a9a78"), mix.inputs[6])
    # packed earth and decomposed granite: two browns broken by noise, fine grit in the bump (no texture's cracks)
    dn1 = N("ShaderNodeTexNoise")
    dn1.inputs["Scale"].default_value, dn1.inputs["Detail"].default_value = 9.0, 10.0
    L(g.outputs["Position"], dn1.inputs["Vector"])
    dmix = N("ShaderNodeMix")
    dmix.data_type = "RGBA"
    dr = N("ShaderNodeMapRange")
    L(dn1.outputs["Fac"], dr.inputs["Value"])
    dr.inputs["From Min"].default_value, dr.inputs["From Max"].default_value = 0.3, 0.7
    L(dr.outputs["Result"], dmix.inputs["Factor"])
    dmix.inputs[6].default_value = gb.lin("#352a20")
    dmix.inputs[7].default_value = gb.lin("#5e4f3e")
    L(dmix.outputs[2], mix.inputs[7])
    L(mix.outputs[2], b.inputs["Base Color"])
    nmix = N("ShaderNodeMix")
    nmix.data_type = "RGBA"
    L(fac.outputs["Result"], nmix.inputs["Factor"])
    L(gn.outputs["Color"], nmix.inputs[6])
    nmix.inputs[7].default_value = (0.5, 0.5, 1.0, 1.0)
    nm = N("ShaderNodeNormalMap")
    L(nmix.outputs[2], nm.inputs["Color"])
    grit = N("ShaderNodeTexVoronoi")
    grit.inputs["Scale"].default_value = 140.0
    L(g.outputs["Position"], grit.inputs["Vector"])
    bp = N("ShaderNodeBump")
    L(fac.outputs["Result"], bp.inputs["Strength"])
    bp.inputs["Distance"].default_value = 0.004
    L(grit.outputs["Distance"], bp.inputs["Height"])
    L(nm.outputs["Normal"], bp.inputs["Normal"])
    L(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.92
    gb._MATS[name] = m
    return m


def earth_mat():
    """Freshly dug earth: dark, damp browns broken by noise, crumbly in the bump (procedural: the CC0 dry-ground
    texture's cracks read as paving on a heap), times the mesh's "col" (the pit's walls fade to black)."""
    name = "park.earth"
    if name in gb._MATS:
        return gb._MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes.new, nt.links.new
    b = nt.nodes["Principled BSDF"]
    g = N("ShaderNodeNewGeometry")
    n1 = N("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value, n1.inputs["Detail"].default_value = 6.0, 12.0
    L(g.outputs["Position"], n1.inputs["Vector"])
    mr = N("ShaderNodeMapRange")
    L(n1.outputs["Fac"], mr.inputs["Value"])
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.3, 0.7
    mix = N("ShaderNodeMix")
    mix.data_type = "RGBA"
    L(mr.outputs["Result"], mix.inputs["Factor"])
    mix.inputs[6].default_value = gb.lin("#2a2019")
    mix.inputs[7].default_value = gb.lin("#4f3f31")
    a = N("ShaderNodeAttribute")
    a.attribute_name = "col"
    mul = N("ShaderNodeMix")
    mul.data_type, mul.blend_type = "RGBA", "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    L(mix.outputs[2], mul.inputs["A"])
    L(a.outputs["Color"], mul.inputs["B"])
    L(mul.outputs["Result"], b.inputs["Base Color"])
    vo = N("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 35.0
    L(g.outputs["Position"], vo.inputs["Vector"])
    n2 = N("ShaderNodeTexNoise")
    n2.inputs["Scale"].default_value, n2.inputs["Detail"].default_value = 60.0, 4.0
    L(g.outputs["Position"], n2.inputs["Vector"])
    hsum = N("ShaderNodeMath")
    hsum.operation = "ADD"
    L(vo.outputs["Distance"], hsum.inputs[0])
    L(n2.outputs["Fac"], hsum.inputs[1])
    bp = N("ShaderNodeBump")
    bp.inputs["Strength"].default_value, bp.inputs["Distance"].default_value = 0.6, 0.01
    L(hsum.outputs[0], bp.inputs["Height"])
    L(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.88
    b.inputs["Specular IOR Level"].default_value = 0.3
    gb._MATS[name] = m
    return m


# ---------------------------------------------------------------- geometry

def _bm_template(fn):
    bm = bmesh.new()
    fn(bm)
    v = np.array([x.co[:] for x in bm.verts], np.float32)
    faces = [[x.index for x in f.verts] for f in bm.faces]
    bm.free()
    return v, faces


T_CUBE = _bm_template(lambda bm: bmesh.ops.create_cube(bm, size=1.0))
T_ICO1 = _bm_template(lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0))
T_ICO2 = _bm_template(lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0))
T_CYL8 = _bm_template(lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=1, radius2=1, depth=1))
T_CYL12 = _bm_template(lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=1, radius2=1, depth=1))
T_CONE4 = _bm_template(lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=1, radius2=0, depth=1))
T_UVS = _bm_template(lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0))


def extruded(outline, depth):
    """An outline in the XZ plane (x, z), counter-clockwise seen from -Y, extruded along Y (depth, centred)."""
    n = len(outline)
    o = np.asarray(outline, np.float32)
    v = np.zeros((2 * n, 3), np.float32)
    v[:n, 0], v[:n, 1], v[:n, 2] = o[:, 0], -depth / 2, o[:, 1]
    v[n:, 0], v[n:, 1], v[n:, 2] = o[:, 0], depth / 2, o[:, 1]
    faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
    faces += [[(i + 1) % n, i, n + i, n + (i + 1) % n] for i in range(n)]
    return v, faces


class Geo:
    """Many pieces merged into one mesh: per-face material index, per-vertex colour ("col")."""

    def __init__(self):
        self.V, self.F, self.MI, self.C, self.n = [], [], [], [], 0

    def add(self, tpl, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), mi=0, col=(1, 1, 1, 1), mtx=None):
        v, faces = tpl
        if mtx is None:
            mtx = Matrix.LocRotScale(Vector(loc), Euler(rot), Vector(scale if not isinstance(scale, (int, float))
                                                                       else (scale,) * 3))
        M = np.array(mtx, np.float32)
        vv = v @ M[:3, :3].T + M[:3, 3]
        self.V.append(vv)
        self.F += [[i + self.n for i in f] for f in faces]
        self.MI += [mi] * len(faces)
        self.C.append(np.tile(np.asarray(col, np.float32), (len(v), 1)))
        self.n += len(v)

    def raw(self, v, faces, mi=0, col=None):
        """Vertices (N,3) and faces (lists of local indices); col (N,4) or one colour."""
        v = np.asarray(v, np.float32)
        self.V.append(v)
        self.F += [[i + self.n for i in f] for f in faces]
        self.MI += [mi] * len(faces)
        c = np.ones((len(v), 4), np.float32) if col is None else np.asarray(col, np.float32)
        self.C.append(c if c.ndim == 2 else np.tile(c, (len(v), 1)))
        self.n += len(v)

    def obj(self, name, mats, smooth=False):
        if not self.V:
            return None
        return mesh_obj(name, np.vstack(self.V), self.F, mats, np.vstack(self.C), np.array(self.MI), smooth)


def mesh_obj(name, V, faces, mats, col=None, mi=None, smooth=False, attr="col"):
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(V))
    me.vertices.foreach_set("co", np.ascontiguousarray(V, np.float32).ravel())
    if isinstance(faces, np.ndarray):  # (M, k) uniform
        lens = np.full(len(faces), faces.shape[1], np.int32)
        flat = faces.ravel().astype(np.int32)
    else:
        lens = np.fromiter((len(f) for f in faces), np.int32, len(faces))
        flat = np.fromiter((i for f in faces for i in f), np.int32, int(lens.sum()))
    me.loops.add(len(flat))
    me.loops.foreach_set("vertex_index", flat)
    me.polygons.add(len(lens))
    me.polygons.foreach_set("loop_start", np.r_[0, np.cumsum(lens)[:-1]].astype(np.int32))
    if mi is not None:
        me.polygons.foreach_set("material_index", np.asarray(mi, np.int32))
    me.polygons.foreach_set("use_smooth", np.full(len(lens), smooth, bool))
    me.update(calc_edges=True)
    me.validate()
    if col is not None:
        ca = me.color_attributes.new(attr, "FLOAT_COLOR", "POINT")
        ca.data.foreach_set("color", np.ascontiguousarray(col, np.float32).ravel())
    for m in mats:
        me.materials.append(m)
    return gb.link(bpy.data.objects.new(name, me))


def fbm(x, y, seed, scale, octaves=3):
    """Seeded value noise (0..1) at world positions, smoothly interpolated."""
    r = np.random.default_rng(seed)
    out, amp, tot = np.zeros_like(x, np.float64), 1.0, 0.0
    for o in range(octaves):
        g = r.random((97, 97))
        fx, fy = x / scale * 2 ** o + 1000, y / scale * 2 ** o + 1000
        ix, iy = np.floor(fx).astype(int), np.floor(fy).astype(int)
        tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a, b = g[ix % 97, iy % 97], g[(ix + 1) % 97, iy % 97]
        c, d = g[ix % 97, (iy + 1) % 97], g[(ix + 1) % 97, (iy + 1) % 97]
        out += amp * ((a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty)
        tot += amp
        amp *= 0.5
    return out / tot


def seg_dist(x, y, pts):
    """Distance from points (arrays) to a polyline."""
    d = np.full_like(x, 1e9, dtype=np.float64)
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        dx, dy = bx - ax, by - ay
        t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
        d = np.minimum(d, np.hypot(x - ax - t * dx, y - ay - t * dy))
    return d


def smooth01(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def bare_at(x, y):
    """How worn the ground is (0 grass .. 1 bare earth) and how long the grass is let grow (0 mown .. 1 long)."""
    bare = np.zeros_like(x, np.float64)
    for pts, w in PATHS:
        bare = np.maximum(bare, smooth01((w / 2 + 0.15 - seg_dist(x, y, pts)) / 0.3))
    bare = np.maximum(bare, smooth01((1.6 - np.hypot(x - COFFIN[0], (y - 13.9) * 1.1)) / 0.5))  # mourners' feet
    bare = np.maximum(bare, 0.85 * smooth01((1.25 - np.hypot((x + 13.4) / 1.5, (y - 23.0) / 1.25)) / 0.3))  # the dig
    bare = np.maximum(bare, 0.9 * smooth01((1.0 - np.hypot((x - HOLE[0]) / 1.3, (y - HOLE[1]) / 1.6)) / 0.3))
    for tx, ty, *_ in TREES:  # dry and shaded under the trees
        bare = np.maximum(bare, 0.75 * smooth01((1.3 - np.hypot(x - tx, y - ty)) / 0.9))
    for bx, by, _ in BENCHES:  # feet in front of the benches
        f = 1 if bx < -20 else -1
        bare = np.maximum(bare, 0.9 * smooth01((0.75 - np.hypot((x - bx - f * 0.7) / 0.6, (y - by) / 1.3)) / 0.3))
    patch = fbm(x, y, SEED + 1, 3.0, 3)  # worn patches (more of them in the cemetery: nobody waters it)
    thr = np.where(y > 18, 0.56, 0.64)
    bare = np.maximum(bare, smooth01((patch - thr) / 0.08) * 0.8)
    fx = (x > FIELD[0] - 0.3) & (x < FIELD[1] + 0.3) & (y > FIELD[2] - 0.3) & (y < FIELD[3] + 0.3)
    bare = np.where(fx, np.maximum(bare, 0.45), bare)
    edge = np.minimum.reduce([x - X0, X1 - x, y - Y0, Y1 - y])
    long_ = smooth01((0.9 - edge) / 0.6)
    long_ = np.maximum(long_, np.where(y > 18, 0.55, 0.0))
    for sx, sy in STONES:
        long_ = np.maximum(long_, smooth01((0.6 - np.hypot(x - sx, (y - sy) * 1.5)) / 0.3))
    return np.clip(bare, 0, 1), np.clip(long_, 0, 1)


# ---------------------------------------------------------------- the ground

def ground(rng):
    step = 0.2
    xs = np.arange(X0, X1 + 1e-6, step)
    ys = np.arange(Y0, Y1 + 1e-6, step)
    gx, gy = np.meshgrid(xs, ys)
    x, y = gx.ravel(), gy.ravel()
    bare, _ = bare_at(x, y)
    lump = fbm(x, y, SEED + 2, 1.6, 3) - 0.5
    z = 0.047 + 0.018 * lump * (1 - bare) - 0.004 * bare
    near = np.zeros_like(x, bool)  # flat where things stand on the ground at 0.04
    near |= (y < 12.0)
    for sx, sy in STONES:
        near |= (np.abs(x - sx) < 0.7) & (np.abs(y - sy) < 0.5)
    near |= (np.abs(x - COFFIN[0]) < 1.0) & (np.abs(y - 14.4) < 1.0)
    near |= (x > -25) & (x < -17.2) & (y > 15.7) & (y < 18.0)  # the ban stones
    z = np.where(near, 0.044, z)
    fx = (x > FIELD[0] - 0.25) & (x < FIELD[1] + 0.25) & (y > FIELD[2] - 0.25) & (y < FIELD[3] + 0.25)
    z = np.where(fx, 0.0405, z)
    V = np.c_[x, y, z]
    nx, ny = len(xs), len(ys)
    i = np.arange(nx - 1)
    j = np.arange(ny - 1)
    I, J = np.meshgrid(i, j)
    a = (J * nx + I).ravel()
    F = np.c_[a, a + 1, a + 1 + nx, a + nx]
    o = mesh_obj("park.lawn", V, F, [terrain_mat()], smooth=True)
    ca = o.data.color_attributes.new("bare", "FLOAT_COLOR", "POINT")
    ca.data.foreach_set("color", np.c_[bare, bare, bare, np.ones_like(bare)].astype(np.float32).ravel())
    return o


def grass(rng):
    """Tufts of blades: a full lawn (the human, M4 v5: "the grass can use more detail"; it was 3% of cells, the
    texture showing through), long and seeding along the fences, walls and stones; short in the marker field (under
    the markers' faces); none on the paths."""
    r = np.random.default_rng(SEED + 3)
    sp = 0.075
    xs = np.arange(X0 + 0.05, X1 - 0.05, sp)
    ys = np.arange(Y0 + 0.08, Y1 - 0.05, sp)
    gx, gy = np.meshgrid(xs, ys)
    x = gx.ravel() + r.uniform(-sp / 2, sp / 2, gx.size)
    y = gy.ravel() + r.uniform(-sp / 2, sp / 2, gx.size)
    bare, long_ = bare_at(x, y)
    clump = fbm(x, y, SEED + 4, 0.7, 2)
    dens = np.minimum(1.0, (1 - bare) ** 2 * (0.3 + 0.5 * long_ + 0.4 * smooth01((clump - 0.55) / 0.15)))
    keep = r.random(x.size) < dens
    fx = (x > FIELD[0] - 0.15) & (x < FIELD[1] + 0.15) & (y > FIELD[2] - 0.15) & (y < FIELD[3] + 0.15)
    keep &= ~(fx & (r.random(x.size) < 0.4))  # thinner among the markers
    for px, py in PLOTS:
        keep &= ~((np.abs(x - px) < 0.65) & (np.abs(y - py) < 1.15))
    keep &= ~((np.abs(x - HOLE[0]) < 0.6) & (np.abs(y - HOLE[1]) < 1.1))
    keep &= ~((np.abs(x - SPOIL[0]) < 0.6) & (np.abs(y - SPOIL[1]) < 1.3))
    keep &= ~((np.abs(x + 18.4) < 0.62) & (np.abs(y - 11.6) < 0.62))  # the doghouse
    keep &= ~((np.abs(x - COFFIN[0]) < 0.5) & (np.abs(y - COFFIN[1]) < 0.3))
    x, y, long_, clump, fx = x[keep], y[keep], long_[keep], clump[keep], fx[keep]
    n = len(x)
    nb = 7  # blades per tuft
    h = (0.05 + 0.06 * r.random(n)) * (1 + 2.6 * long_ * r.uniform(0.5, 1.0, n))
    # the ban stones and the inscribed stones' faces: keep the grass short in front of them
    near_ban = (x > -24.8) & (x < -17.4) & (y > 15.7) & (y < 18.0)
    h = np.where(near_ban, np.minimum(h, 0.07), h)
    h = np.where(fx, np.minimum(h, 0.05), h)  # the marker field: under the markers' faces
    V = np.zeros((n * nb * 3, 3), np.float32)
    C = np.zeros((n * nb * 3, 4), np.float32)
    base_g = np.array(gb.lin("#33452a")[:3])
    dry = np.array(gb.lin("#62603c")[:3])
    brown = np.array(gb.lin("#4c3e2a")[:3])
    t_dry = np.clip(0.1 + 0.55 * long_ * r.random(n) + 0.3 * (clump - 0.5), 0, 1)
    tuft = (1 - t_dry)[:, None] * base_g + t_dry[:, None] * dry
    tuft = np.where((r.random(n) < 0.12)[:, None], brown, tuft) * r.uniform(0.7, 1.15, (n, 1))
    for k in range(nb):
        ang = r.uniform(0, 2 * math.pi, n)
        lean = r.uniform(0.1, 0.55, n)
        bh = h * r.uniform(0.6, 1.0, n)
        w = r.uniform(0.008, 0.016, n)
        ox, oy = r.normal(0, 0.02, n), r.normal(0, 0.02, n)
        cx, cy = x + ox, y + oy
        px, py = -np.sin(ang), np.cos(ang)  # blade width direction
        tipx, tipy = cx + np.cos(ang) * lean * bh, cy + np.sin(ang) * lean * bh
        base = (k * n + np.arange(n)) * 3
        V[base, 0], V[base, 1], V[base, 2] = cx - px * w, cy - py * w, 0.035
        V[base + 1, 0], V[base + 1, 1], V[base + 1, 2] = cx + px * w, cy + py * w, 0.035
        V[base + 2, 0], V[base + 2, 1], V[base + 2, 2] = tipx, tipy, 0.035 + bh
        C[base, :3] = tuft * 0.35
        C[base + 1, :3] = tuft * 0.35
        C[base + 2, :3] = tuft * 0.95
    C[:, 3] = 1
    F = np.arange(len(V), dtype=np.int32).reshape(-1, 3)
    mesh_obj("park.grass", V, F, [attr_mat("grass", 0.75, up=True)], C)


def pebbles(rng):
    """Decomposed granite on the paths: small stones, denser in the middle of the path."""
    r = np.random.default_rng(SEED + 5)
    g = Geo()
    for pts, w in PATHS:
        L = sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))
        for _ in range(int(L * w * 90)):
            k = r.integers(len(pts) - 1)
            (ax, ay), (bx, by) = pts[k], pts[k + 1]
            t = r.random()
            dx, dy = bx - ax, by - ay
            ln = math.hypot(dx, dy)
            off = r.normal(0, w * 0.28)
            x, y = ax + t * dx - dy / ln * off, ay + t * dy + dx / ln * off
            if not (X0 + 0.1 < x < X1 - 0.1 and Y0 + 0.05 < y < Y1):
                continue
            s = r.uniform(0.004, 0.012)
            c = r.uniform(0.3, 0.6) * np.array(gb.lin(r.choice(["#b8ab95", "#8f8577", "#a39280", "#c9bfae"])))
            g.add(T_ICO1, (x, y, 0.042), (r.random() * 3, r.random() * 3, r.random() * 3),
                  (s * r.uniform(0.8, 1.4), s, s * 0.6), col=(*c[:3], 1))
    g.obj("park.pebbles", [attr_mat("pebbles", 0.75)])


# ---------------------------------------------------------------- iron

def iron_mat():
    m = gb.mat("park.iron", "#1a1918", rough=0.55, metal=0.6)
    if not m.get("grimed"):
        gb.grime(m, amt=0.55, damp=0.8)
        m["grimed"] = 1
    return m


def pickets(g, a, b, z0=0.06, top=1.66, spacing=0.14, w=0.02, finial=0.11):
    """Upright bars with spear finials between points a and b (x, y) on the ground."""
    (ax, ay), (bx, by) = a, b
    L = math.hypot(bx - ax, by - ay)
    n = max(1, int(L / spacing))
    ang = math.atan2(by - ay, bx - ax)
    for k in range(n):
        t = (k + 0.5) / n
        x, y = ax + t * (bx - ax), ay + t * (by - ay)
        g.add(T_CUBE, (x, y, (z0 + top) / 2), (0, 0, ang), (w, w, top - z0))
        g.add(T_CONE4, (x, y, top + finial / 2), (0, 0, ang + math.pi / 4), (w * 1.6, w * 1.6, finial))


def rail(g, a, b, z, s=(0.04, 0.025)):
    (ax, ay), (bx, by) = a, b
    L = math.hypot(bx - ax, by - ay)
    g.add(T_CUBE, ((ax + bx) / 2, (ay + by) / 2, z), (0, 0, math.atan2(by - ay, bx - ax)), (L, s[1], s[0]))


def gate_leaf(g, hinge, width, ang, h=1.5):
    """An iron gate leaf hinged at `hinge`, swung to angle `ang` (0 = along +X)."""
    hx, hy = hinge
    dx, dy = math.cos(ang), math.sin(ang)
    end = (hx + dx * width, hy + dy * width)
    for z in (0.15, h - 0.12, h * 0.55):
        rail(g, (hx, hy), end, z, (0.035, 0.03))
    for t in (0.03, width - 0.03):
        g.add(T_CUBE, (hx + dx * t, hy + dy * t, h / 2 + 0.05), (0, 0, ang), (0.035, 0.035, h - 0.1))
    pickets(g, (hx + dx * 0.05, hy + dy * 0.05), (end[0] - dx * 0.05, end[1] - dy * 0.05), 0.15, h - 0.12, 0.12, 0.018,
            0.09)


def fence(rng):
    """block.park()'s fence is posts every 2 m and two rails: pickets with spear finials, a bottom rail, post caps;
    gate posts and the two leaves standing open; posts on the side fences, which had none."""
    g = Geo()
    y = Y0
    for a, b in ((X0, GATE[0]), (GATE[1], X1)):
        rail(g, (a, y), (b, y), 0.12)
    # the run between the gate and the doghouse lost its pickets years ago (so S38's camera reads BOT DEFENSE
    # through the rails): a few snapped-off stubs, and one bent picket lying in the grass
    for a, b in ((X0, GATE[0]), (GATE[1], DOG_GAP[0]), (DOG_GAP[1], X1)):
        pickets(g, (a, y), (b, y))
    for x, h in ((-19.55, 0.32), (-19.1, 0.18), (-18.3, 0.26), (-17.9, 0.12)):
        g.add(T_CUBE, (x, y, 0.06 + h / 2), (0, 0, 0), (0.02, 0.02, h))
    g.add(T_CUBE, (-18.9, y + 0.45, 0.07), (0.0, 1.45, 0.5), (0.02, 0.02, 1.6))
    for x in (X0, X1):
        pickets(g, (x, Y0), (x, Y1))
        rail(g, (x, Y0), (x, Y1), 0.12)
        for yy in np.arange(Y0 + 2, Y1, 2.0):
            g.add(T_CUBE, (x, yy, 0.9), (0, 0, 0), (0.06, 0.06, 1.8))
    for x in list(np.arange(X0, X1 + 0.01, 2.0)) + [X0, X1]:  # caps on every front post (and the corners)
        if GATE[0] - 0.5 < x < GATE[1] + 0.5:
            continue
        g.add(T_UVS, (x, y, 1.84), scale=(0.05, 0.05, 0.05))
        g.add(T_CUBE, (x, y, 0.03), scale=(0.1, 0.1, 0.06))
    for x in (X0, X1):
        for yy in np.arange(Y0 + 2, Y1, 2.0):
            g.add(T_UVS, (x, yy, 1.84), scale=(0.05, 0.05, 0.05))
    for x in GATE:  # gate posts, square, with ball caps
        g.add(T_CUBE, (x, y, 1.0), scale=(0.11, 0.11, 2.0))
        g.add(T_CUBE, (x, y, 2.02), scale=(0.15, 0.15, 0.04))
        g.add(T_UVS, (x, y, 2.11), scale=(0.08, 0.08, 0.08))
    gate_leaf(g, (GATE[0] + 0.06, y + 0.07), 0.92, math.radians(166))
    gate_leaf(g, (GATE[1] - 0.06, y + 0.07), 0.92, math.radians(180 - 163))
    # the old railing between the park and the east plots, on a stone kerb, with its gate hanging open
    ry = 18.1
    for a, b in ((-11.75, -10.0),):
        pickets(g, (a, ry), (b, ry), 0.2, 1.02, 0.15, 0.018, 0.09)
        rail(g, (a, ry), (b, ry), 0.95)
        rail(g, (a, ry), (b, ry), 0.3)
    gate_leaf(g, (-11.82, ry + 0.04), 0.85, math.radians(180 - 125), 1.1)
    g.obj("park.iron", [iron_mat()])


# ---------------------------------------------------------------- green

def hedge_mat():
    return attr_mat("hedge", 0.8, bump=1.0, bump_scale=60.0)


def hedge(g, r, a, b, h=0.75, depth=0.6, lv=None):
    """A clipped hedge gone shaggy: a dark core of blobs, its surface covered in small leaf cards (lv: a list that
    collects the leaves, built into one mesh by green())."""
    (ax, ay), (bx, by) = a, b
    L = math.hypot(bx - ax, by - ay)
    n = max(2, int(L / 0.16))
    base = np.array(gb.lin("#2c3b21")[:3])
    ux, uy = (bx - ax) / L, (by - ay) / L
    for k in range(n):
        t = (k + r.random()) / n
        for layer in range(3):
            rad = r.uniform(0.13, 0.22) * (depth / 0.6)
            side = r.uniform(-1, 1) * (depth / 2 - rad * 0.6)
            x, y = ax + t * (bx - ax) - uy * side, ay + t * (by - ay) + ux * side
            z = (h - rad * 0.8) * (0.35, 0.7, 1.0)[layer] + r.uniform(-0.08, 0.06)
            c = base * r.uniform(0.6, 1.35) * np.array([r.uniform(0.85, 1.15), 1, r.uniform(0.8, 1.0)])
            if r.random() < 0.15:  # a dead, browned patch
                c = np.array(gb.lin("#4a4026")[:3]) * r.uniform(0.7, 1.1)
            v, f = T_ICO1
            ctr = np.array([x, y, max(z, rad * 0.7)])
            g.raw(v * np.array([rad * 1.1, rad, rad * 0.95]) * 0.92 + ctr, f, col=(*(c * 0.35), 1))
            if lv is not None:  # leaves over the blob's outer surface
                rs = np.random.default_rng(r.randint(0, 10 ** 6))
                d = rs.normal(0, 1, (90, 3))
                d /= np.linalg.norm(d, axis=1)[:, None]
                p = ctr + d * np.array([rad * 1.1, rad, rad * 0.95]) * rs.uniform(0.88, 1.06, (90, 1))
                ok = p[:, 2] > 0.06
                p, d = p[ok], d[ok]
                lv.append((p, np.tile(c, (len(p), 1)) * rs.uniform(0.7, 1.15, (len(p), 1)), d))


def plant_parts(aid):
    """A kit file's separate plants (kit.load joins them), each its own mesh with its origin at its bottom centre."""
    key = f"_parts_{aid}"
    if key in kit._MESH:
        return kit._MESH[key]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(kit.MODELS / aid / f"{aid}.gltf"))
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    out = {}
    for o in new:
        if o.type != "MESH":
            continue
        me = o.data.copy()
        me.transform(o.matrix_world)
        co = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        lo, hi = co.min(0), co.max(0)
        me.transform(Matrix.Translation(Vector((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]))))
        me.name = f"park.{o.name}"
        me["dims"] = list(map(float, hi - lo))
        out[o.name] = me
    for o in new:
        bpy.data.objects.remove(o)
    kit._MESH[key] = out
    return out


def green(rng):
    r = random.Random(SEED + 6)
    g = Geo()
    lv = []
    hedge(g, r, (-31.55, 12.3), (-23.9, 12.3), lv=lv)  # behind the good bots' row
    hedge(g, r, (-16.9, 12.45), (-12.2, 12.45), lv=lv)
    hedge(g, r, (-31.55, 12.9), (-31.55, 13.6), 0.8, lv=lv)
    hedge(g, r, (-31.55, 15.1), (-31.55, 15.5), 0.8, lv=lv)
    hedge(g, r, (-10.5, 12.7), (-10.5, 13.0), 0.8, lv=lv)
    hedge(g, r, (-10.5, 14.2), (-10.5, 17.6), 0.85, lv=lv)
    g.obj("park.hedges", [hedge_mat()], smooth=True)
    P = np.vstack([p for p, _, _ in lv])
    Cc = np.vstack([c for _, c, _ in lv]) * 0.75
    D = np.vstack([d for _, _, d in lv])
    n = len(P)
    rs = np.random.default_rng(SEED + 11)
    # each leaf a small quad lying roughly on the hedge's surface (shingled outward), tilted at random
    Dn = D + rs.normal(0, 0.45, (n, 3))
    Dn /= np.linalg.norm(Dn, axis=1)[:, None]
    a1 = np.cross(Dn, rs.normal(0, 1, (n, 3)))
    a1 /= np.linalg.norm(a1, axis=1)[:, None]
    a2 = np.cross(Dn, a1)
    sz = rs.uniform(0.022, 0.04, (n, 1))
    V = np.zeros((n * 4, 3), np.float32)
    for k, (u, v) in enumerate(((-1, -0.5), (1, -0.5), (1, 0.5), (-1, 0.5))):
        V[k::4] = P + (a1 * u + a2 * v) * sz
    C = np.c_[np.repeat(Cc, 4, axis=0), np.ones(n * 4)]
    mesh_obj("park.hedgeleaves", V, np.arange(n * 4, dtype=np.int32).reshape(-1, 4), [attr_mat("hedgeleaf", 0.6)], C)
    # CC0 shrubs in the corners
    sh = plant_parts("shrub_02")
    names = sorted(sh)
    for k, (x, y, rot, s) in enumerate([(-11.1, 11.75, 0.5, 0.75), (-10.85, 26.3, 2.0, 0.85),
                                         (-31.25, 17.0, 1.0, 0.55), (-16.3, 26.45, 3.6, 0.62)]):
        o = gb.link(bpy.data.objects.new(f"park.shrub{k}", sh[names[k % len(names)]]))
        o.location, o.rotation_euler, o.scale = (x, y, 0.03), (0, 0, rot), (s,) * 3
    # grass clumps and weeds: along the fences, the walls, the old stones and the trees
    gr = plant_parts("grass_medium_01")
    big = sorted(n for n in gr if "large" in n or "tall" in n or "mid" in n)
    wd = plant_parts("weed_plant_02")
    weeds = sorted(wd)
    spots = []
    for _ in range(70):
        side = r.random()
        if side < 0.3:
            spots.append((r.uniform(X0 + 0.1, X1 - 0.1), Y0 + r.uniform(0.1, 0.35)))
        elif side < 0.5:
            spots.append((X0 + r.uniform(0.1, 0.4), r.uniform(Y0 + 0.5, Y1 - 0.3)))
        elif side < 0.65:
            spots.append((X1 - r.uniform(0.1, 0.4), r.uniform(Y0 + 0.5, Y1 - 0.3)))
        else:
            spots.append((r.uniform(X0 + 0.3, X1 - 0.3), Y1 - r.uniform(0.08, 0.3)))
    for tx, ty, *_ in TREES:
        for _ in range(5):
            a = r.uniform(0, 6.28)
            spots.append((tx + math.cos(a) * r.uniform(0.2, 0.5), ty + math.sin(a) * r.uniform(0.2, 0.5)))
    for k, (x, y) in enumerate(spots):
        if FIELD[0] - 0.2 < x < FIELD[1] + 0.2 and FIELD[2] - 0.2 < y < FIELD[3] + 0.2:
            continue
        if Y0 < y < 11.7 and (-30.3 < x < -23.7 or -15.3 < x < -13.5 or -22.6 < x < -17.7):
            continue  # the good bots and the doghouse
        if r.random() < 0.7:
            me = gr[r.choice(big)]
            s = r.uniform(1.4, 2.6)
        else:
            me = wd[r.choice(weeds)]
            s = r.uniform(1.5, 3.0)
        o = gb.link(bpy.data.objects.new(f"park.clump{k}", me))
        o.location, o.rotation_euler, o.scale = (x, y, 0.035), (0, 0, r.uniform(0, 6.28)), (s,) * 3


def thin_tree(aid="tree_small_02", keep=0.22):
    """The CC0 tree with most of its leaves dropped (late autumn, and a quarter of the cost: the file models ~80,000
    leaves, 1.9 M triangles), its leaves dithered rather than blended (cheaper, and they cast shadows)."""
    src = kit.load(aid)
    n = len(src.polygons)
    mi = np.empty(n, np.int32)
    src.polygons.foreach_get("material_index", mi)
    ls = np.empty(n, np.int32)
    src.polygons.foreach_get("loop_start", ls)
    lt = np.empty(n, np.int32)
    src.polygons.foreach_get("loop_total", lt)
    vi = np.empty(len(src.loops), np.int32)
    src.loops.foreach_get("vertex_index", vi)
    leaf_idx = [k for k, m in enumerate(src.materials) if "leaves" in m.name]
    leaf = np.isin(mi, leaf_idx)
    # leaves are stored one after another: a new leaf starts where a polygon's vertices all follow the last ones
    mn, mx = np.minimum.reduceat(vi, ls), np.maximum.reduceat(vi, ls)
    li = np.where(leaf)[0]
    start = np.r_[True, mn[li[1:]] > np.maximum.accumulate(mx[li])[:-1]]
    isl = np.cumsum(start) - 1
    r = np.random.default_rng(SEED + 10)
    keep_isl = r.random(isl.max() + 1) < keep
    K = np.ones(n, bool)
    K[li] = keep_isl[isl]
    loop_keep = np.repeat(K, lt)
    nv = len(src.vertices)
    co = np.empty(nv * 3, np.float32)
    src.vertices.foreach_get("co", co)
    used = np.unique(vi[loop_keep])
    remap = np.full(nv, -1, np.int32)
    remap[used] = np.arange(len(used), dtype=np.int32)
    me = bpy.data.meshes.new(f"park.{aid}.thin")
    me.vertices.add(len(used))
    me.vertices.foreach_set("co", co.reshape(-1, 3)[used].ravel())
    nl = int(loop_keep.sum())
    me.loops.add(nl)
    me.loops.foreach_set("vertex_index", remap[vi[loop_keep]])
    me.polygons.add(int(K.sum()))
    me.polygons.foreach_set("loop_start", np.r_[0, np.cumsum(lt[K])[:-1]].astype(np.int32))
    me.polygons.foreach_set("material_index", mi[K])
    me.polygons.foreach_set("use_smooth", np.ones(int(K.sum()), bool))
    for uv in src.uv_layers:
        a = np.empty(len(src.loops) * 2, np.float32)
        uv.data.foreach_get("uv", a)
        me.uv_layers.new(name=uv.name).data.foreach_set("uv", a.reshape(-1, 2)[loop_keep].ravel())
    me.update(calc_edges=True)
    for m in src.materials:
        if "leaves" in m.name:
            m = m.copy()
            m.name = f"park.{m.name}"
            m.surface_render_method = "DITHERED"
        me.materials.append(m)
    return me


def trees():
    """Three trees: the thinned CC0 tree, each trunk placed (the canopy leans off-centre in the file)."""
    me = thin_tree()
    for k, (tx, ty, s, rot) in enumerate(TREES):
        off = Matrix.Rotation(rot, 3, "Z") @ Vector((0.15, -0.77, 0)) * s
        o = gb.link(bpy.data.objects.new(f"park.tree{k}", me))
        o.location, o.rotation_euler, o.scale = (tx + off.x, ty + off.y, 0.02), (0, 0, rot), (s,) * 3


# ---------------------------------------------------------------- furniture

def furniture(rng):
    g = Geo()  # mi 0 iron, 1 wood, 2 bin
    for k, (bx, by, face) in enumerate(BENCHES):
        M = Matrix.Translation((bx, by, 0.035)) @ Matrix.Rotation(face, 4, "Z")

        def put(tpl, loc, size, mi, rot=(0, 0, 0)):
            g.add(tpl, mi=mi, mtx=M @ Matrix.LocRotScale(Vector(loc), Euler(rot), Vector(size)))
        for sy in (-0.8, 0.8):  # cast-iron ends: legs, seat bracket, back upright, arm
            put(T_CUBE, (0.18, sy, 0.22), (0.05, 0.05, 0.44), 0)
            put(T_CUBE, (-0.17, sy, 0.22), (0.05, 0.05, 0.44), 0)
            put(T_CUBE, (0.0, sy, 0.43), (0.46, 0.05, 0.04), 0)
            put(T_CUBE, (-0.22, sy, 0.66), (0.045, 0.045, 0.5), 0, (0, -0.22, 0))
            put(T_CUBE, (0.02, sy, 0.64), (0.4, 0.045, 0.035), 0)
            put(T_CUBE, (0.2, sy, 0.54), (0.035, 0.035, 0.2), 0)
        for j in range(4):  # seat slats
            put(T_CUBE, (0.16 - j * 0.105, 0, 0.465), (0.085, 1.85, 0.03), 1)
        for j in range(3):  # back slats
            put(T_CUBE, (-0.215 - j * 0.035, 0, 0.6 + j * 0.12), (0.025, 1.85, 0.08), 1, (0, -0.25, 0))
    # a park bin by the east bench: slatted green steel on a post
    bx, by = -11.05, 15.0
    g.add(T_CYL12, (bx, by, 0.5), scale=(0.24, 0.24, 0.62), mi=2)
    g.add(T_CYL12, (bx, by, 0.82), scale=(0.26, 0.26, 0.03), mi=0)
    g.add(T_CUBE, (bx, by, 0.1), scale=(0.07, 0.07, 0.2), mi=0)
    wood = tex("benchwood", "plywood", 0.8, "#6b5a46", 1.0)
    if not wood.get("grimed"):
        gb.grime(wood, amt=0.6)
        wood["grimed"] = 1
    binm = gb.mat("park.bin", "#2e4234", rough=0.6, metal=0.3)
    if not binm.get("grimed"):
        gb.grime(binm, amt=0.7)
        binm["grimed"] = 1
    g.obj("park.furniture", [iron_mat(), wood, binm])
    lamp()


def lamp():
    """One dim park lamp: a cast-iron post with the CC0 lantern on a bracket; its light is the only one added."""
    px, py = LAMP
    g = Geo()
    g.add(T_CYL12, (px, py, 0.25), scale=(0.13, 0.13, 0.42))
    g.add(T_CYL12, (px, py, 0.5), scale=(0.09, 0.09, 0.12))
    g.add(T_CYL12, (px, py, 1.75), scale=(0.055, 0.055, 2.5))
    g.add(T_CYL12, (px, py, 3.02), scale=(0.075, 0.075, 0.06))
    g.add(T_UVS, (px, py, 3.1), scale=(0.07, 0.07, 0.08))
    g.obj("park.lamppost", [iron_mat()])
    d = kit.dims("street_lamp_02")
    face = math.radians(-60)  # the head hangs toward the coffin (east-south-east)
    # the file's bracket meets the wall at y = 0 (its back); its origin (bottom centre) is d.y / 2 in front of that
    back = Matrix.Rotation(face, 3, "Z") @ Vector((0, d.y / 2 + 0.055, 0))
    head = kit.place("park.lamphead", "street_lamp_02", (px - back.x, py - back.y, 2.15), face + math.pi, 0.95)
    P = gb.LOOK["palette"]
    glow = gb.mat("park.lampglow", P["sodium"], rough=0.3, emit=6.0)
    for k, slot in enumerate(head.material_slots):
        if "glass" in (slot.material.name if slot.material else "") or "bulb" in (slot.material.name if slot.material
                                                                              else ""):
            slot.link = "OBJECT"
            slot.material = glow
    bpy.context.view_layer.update()
    # the light at the lantern's glass: the middle of the head's top half, away from the bracket
    bb = [head.matrix_world @ Vector(c) for c in head.bound_box]
    lo = Vector([min(v[i] for v in bb) for i in range(3)])
    hi = Vector([max(v[i] for v in bb) for i in range(3)])
    fwd = Matrix.Rotation(face, 3, "Z") @ Vector((0, -1, 0))
    c = Vector((px, py, 0)) + fwd * (d.y * 0.95 * 0.8)
    ld = bpy.data.lights.new("park.lamp", "POINT")
    ld.energy, ld.color = 160.0, gb.lin(P["sodium"])[:3]
    ld.shadow_soft_size = 0.12
    lo_ = gb.link(bpy.data.objects.new("park.lamp", ld))
    lo_.location = (c.x, c.y, lo.z + (hi.z - lo.z) * 0.6)


# ---------------------------------------------------------------- the cemetery

def wall(rng):
    """The old cemetery's brick boundary wall with a stone coping and piers: west (from the S39b row back), back, and
    east beside the fresh plots. It stands just outside block.park()'s fence line."""
    g = Geo()
    runs = [((-32.27, 17.4), (-32.27, 27.45), 0.85), ((-32.47, 27.25), (-9.55, 27.25), 1.25),
            ((-9.77, 18.0), (-9.77, 27.45), 0.85)]
    for (ax, ay), (bx, by), h in runs:
        cx, cy = (ax + bx) / 2, (ay + by) / 2
        sx = abs(bx - ax) or 0.4
        sy = abs(by - ay) or 0.4
        g.add(T_CUBE, (cx, cy, h / 2), scale=(sx, sy, h), mi=0)
        g.add(T_CUBE, (cx, cy, h + 0.05), scale=(sx + 0.1 if sx > 0.4 else 0.52, sy + 0.1 if sy > 0.4 else 0.52, 0.1),
              mi=1)
        L = max(sx, sy)
        n = int(L / 3.2)
        for k in range(n + 1):
            t = k / n
            x, y = ax + t * (bx - ax), ay + t * (by - ay)
            g.add(T_CUBE, (x, y, (h + 0.25) / 2), scale=(0.58, 0.58, h + 0.25), mi=0)
            g.add(T_CUBE, (x, y, h + 0.3), scale=(0.68, 0.68, 0.1), mi=1)
            g.add(T_CONE4, (x, y, h + 0.43), (0, 0, math.pi / 4), (0.42, 0.42, 0.16), mi=1)
    # the low stone kerb under the old railing at y = 18.1, with its piers
    for a, b in ((-11.75, -9.95),):
        g.add(T_CUBE, ((a + b) / 2, 18.1, 0.1), scale=(b - a, 0.28, 0.16), mi=1)
    for x in (-12.85, -11.75):
        g.add(T_CUBE, (x, 18.1, 0.6), scale=(0.34, 0.34, 1.2), mi=1)
        g.add(T_CUBE, (x, 18.1, 1.24), scale=(0.42, 0.42, 0.08), mi=1)
        g.add(T_UVS, (x, 18.1, 1.38), scale=(0.13, 0.13, 0.13), mi=1)
    brick = tex("wallbrick", "brick_4", 2.0, "#7a6a62", 1.0)
    if not brick.get("grimed"):
        gb.grime(brick, amt=0.9, damp=1.4)
        brick["grimed"] = 1
    g.obj("park.wall", [brick, oldstone_mat()])


def oldstone_mat():
    m = tex("oldstone", "concrete", 1.2, "#8f8b80", 1.0, attr=True)
    if not m.get("grimed"):
        gb.grime(m, amt=1.0, damp=1.6, streak=1.3)
        m["grimed"] = 1
    return m


def _arc(cx, cz, r, a0, a1, n):
    return [(cx + r * math.cos(a), cz + r * math.sin(a)) for a in np.linspace(a0, a1, n)]


def stone_shape(kind, w, h):
    """Outlines (x, z) for the old stones, counter-clockwise from the bottom left."""
    if kind == "round":
        return [(-w / 2, 0), (w / 2, 0)] + _arc(0, h - w / 2, w / 2, 0, math.pi, 9)
    if kind == "gothic":  # a pointed arch
        h0 = h - w * 0.55
        right = [(w / 2 * math.cos(t * math.pi / 2) ** 0.7, h0 + (h - h0) * math.sin(t * math.pi / 2))
                 for t in np.linspace(0, 1, 6)]
        return [(-w / 2, 0), (w / 2, 0)] + right + [(-x, z) for x, z in reversed(right[:-1])]
    if kind == "shoulder":  # square shoulders and a low raised middle
        return [(-w / 2, 0), (w / 2, 0), (w / 2, h * 0.86), (w * 0.32, h * 0.86)] + \
            [(w * 0.32 * math.cos(a), h * 0.86 + h * 0.14 * math.sin(a))
             for a in np.linspace(0.3, math.pi - 0.3, 5)] + \
            [(-w * 0.32, h * 0.86), (-w / 2, h * 0.86)]
    if kind == "broken":  # the top snapped off
        return [(-w / 2, 0), (w / 2, 0), (w / 2, h * 0.55), (w * 0.18, h * 0.42), (-w * 0.05, h * 0.62),
                (-w * 0.3, h * 0.5), (-w / 2, h * 0.68)]
    return [(-w / 2, 0), (w / 2, 0), (w / 2, h), (-w / 2, h)]  # tablet


# x, y, kind, width, height, facing (0 = faces -Y, toward the park), lean
OLD = [
    # the back row, behind the field of markers
    (-30.7, 26.95, "round", 0.62, 0.85, 0.0, 0.06), (-28.0, 26.95, "gothic", 0.55, 1.0, 0.05, -0.03),
    (-26.6, 26.9, "broken", 0.7, 0.9, -0.08, 0.02), (-25.2, 26.95, "shoulder", 0.75, 0.95, 0.0, 0.0),
    (-22.0, 26.95, "round", 0.5, 0.65, 0.1, 0.12), (-20.6, 26.9, "tablet", 0.6, 0.75, -0.04, -0.05),
    (-19.2, 26.95, "round", 0.45, 0.6, 0.0, 0.08), (-17.9, 26.95, "gothic", 0.5, 0.9, 0.08, 0.0),
    # behind and beside the fresh plots
    (-14.5, 26.55, "round", 0.6, 0.8, -0.1, 0.09), (-13.1, 26.6, "shoulder", 0.62, 0.78, 0.06, -0.04),
    (-10.55, 19.4, "round", 0.55, 0.75, -1.45, 0.05), (-10.55, 21.2, "gothic", 0.5, 0.85, -1.6, -0.03),
    # the west edge, beside the field
    (-31.65, 22.8, "round", 0.5, 0.6, 1.57, 0.1), (-31.65, 24.6, "tablet", 0.45, 0.5, 1.5, -0.06),
    (-31.6, 26.2, "broken", 0.5, 0.7, 1.62, 0.0), (-31.55, 19.9, "shoulder", 0.55, 0.7, 1.5, 0.08),
]


def old_stones(rng):
    """The old cemetery: weathered, sunk and leaning blank stones round the edges (a few with lettering worn past
    reading), an obelisk and an urn on the back row, a ledger slab and two kerbed graves."""
    r = random.Random(SEED + 7)
    g = Geo()
    for x, y, kind, w, h, face, lean in OLD:
        d = r.uniform(0.1, 0.15)
        tone = r.uniform(0.62, 0.95)
        moss = r.random() < 0.4
        c = (tone * (0.85 if moss else 1.0), tone * (1.0 if moss else 0.97), tone * (0.75 if moss else 0.92), 1)
        sink = r.uniform(0.02, 0.08)
        M = Matrix.Translation((x, y, 0.04 - sink)) @ Matrix.Rotation(face, 4, "Z") @ Matrix.Rotation(lean, 4, "X") @ \
            Matrix.Rotation(r.uniform(-0.05, 0.05), 4, "Y")
        g.add(extruded(stone_shape(kind, w, h), d), mtx=M, col=c)
        if kind != "broken" and r.random() < 0.6:  # lettering worn past reading: faint shallow lines
            for j in range(r.randint(2, 4)):
                lw = w * r.uniform(0.35, 0.7)
                z = h * 0.68 - j * 0.07
                g.add(T_CUBE, mtx=M @ Matrix.LocRotScale(Vector((r.uniform(-0.03, 0.03), -d / 2 - 0.0015, z)), None,
                                                          Vector((lw, 0.004, 0.022))),
                      col=(c[0] * 0.78, c[1] * 0.78, c[2] * 0.78, 1))
        if kind == "broken":  # the fallen top, in the grass
            g.add(extruded(stone_shape("round", w, h * 0.45), d), mtx=Matrix.Translation((x + 0.25, y - 0.45, 0.05)) @
                  Matrix.Rotation(face + 0.4, 4, "Z") @ Matrix.Rotation(-1.52, 4, "X"), col=c)
    # an obelisk and an urn on the back row: taller shapes over the wall line for the crane reveal (S39a)
    ox, oy = -29.35, 27.0
    for z, s, hgt in ((0.15, 0.7, 0.3), (0.45, 0.55, 0.3), (0.75, 0.42, 0.3)):
        g.add(T_CUBE, (ox, oy, z), scale=(s, s, hgt), col=(0.8, 0.8, 0.76, 1))
    g.add(T_CONE4, (ox, oy, 1.75), (0, 0, math.pi / 4), (0.28, 0.28, 1.7), col=(0.82, 0.82, 0.78, 1))
    ux, uy = -23.6, 27.0
    g.add(T_CUBE, (ux, uy, 0.4), scale=(0.5, 0.5, 0.8), col=(0.75, 0.76, 0.7, 1))
    g.add(T_CUBE, (ux, uy, 0.84), scale=(0.6, 0.6, 0.08), col=(0.75, 0.76, 0.7, 1))
    g.add(T_CYL12, (ux, uy, 0.93), scale=(0.12, 0.12, 0.1), col=(0.75, 0.76, 0.7, 1))
    g.add(T_UVS, (ux, uy, 1.15), scale=(0.2, 0.2, 0.24), col=(0.75, 0.76, 0.7, 1))
    g.add(T_CYL12, (ux, uy, 1.38), scale=(0.13, 0.13, 0.06), col=(0.75, 0.76, 0.7, 1))
    # kerbed old graves (a stone surround round a sunken plot) and a ledger slab, in the east corner behind the plots
    for kx, ky in ((-16.2, 25.6),):
        for sx, sy, w_, d_ in ((0, -0.95, 0.9, 0.1), (0, 0.95, 0.9, 0.1), (-0.45, 0, 0.1, 2.0), (0.45, 0, 0.1, 2.0)):
            g.add(T_CUBE, (kx + sx, ky + sy, 0.08), scale=(w_, d_, 0.12), col=(0.7, 0.72, 0.66, 1))
    g.add(T_CUBE, (-12.9, 26.0, 0.09), (0, 0, 0.04), (0.8, 1.7, 0.12), col=(0.68, 0.68, 0.64, 1))
    o = g.obj("park.oldstones", [oldstone_mat()])
    bv = o.modifiers.new("bevel", "BEVEL")
    bv.width, bv.segments, bv.limit_method = 0.012, 1, "ANGLE"


def mound(g, r, cx, cy, sx, sy, h, cover=None, nx=16, ny=28):
    """A heap of earth: a flat-topped, rounded-rectangle dome (sx, sy half sizes) with lumps and clods; cover (half
    x, half y, top z) is a grey-box box it must bury."""
    us = np.linspace(-1, 1, nx)
    vs = np.linspace(-1, 1, ny)
    U, Vv = np.meshgrid(us, vs)
    rr = (np.abs(U) ** 3 + np.abs(Vv) ** 3) ** (1 / 3)
    rs = np.random.default_rng(r.randint(0, 10 ** 6))
    wob = rs.normal(0, 0.05, U.shape)
    prof = np.clip(1 - np.clip(rr + wob * 0.3, 0, 1) ** 2, 0, 1) ** 0.6
    lump = rs.normal(0, 0.1, U.shape)
    lump = (lump + np.roll(lump, 1, 0) + np.roll(lump, 1, 1) + np.roll(lump, -1, 0)) / 4
    z = 0.036 + h * prof * (1 + lump) * (1 - 0.08 * np.abs(Vv))
    px, py = U * sx, Vv * sy
    if cover:
        inside = (np.abs(px - cover[3]) < cover[0] + 0.1) & (np.abs(py) < cover[1] + 0.1)
        z = np.where(inside, np.maximum(z, cover[2] + 0.025 + 0.02 * rs.random(U.shape)), z)
    z = np.where(rr >= 0.995, 0.036, z)
    V = np.c_[(cx + px).ravel(), (cy + py).ravel(), z.ravel()]
    I, J = np.meshgrid(np.arange(nx - 1), np.arange(ny - 1))
    a = (J * nx + I).ravel()
    F = np.c_[a, a + 1, a + 1 + nx, a + nx].tolist()
    tone = np.clip(0.75 + 0.3 * rs.random(len(V)), 0, 1.2)
    g.raw(V, F, col=np.c_[tone, tone * 0.96, tone * 0.92, np.ones(len(V))])
    for _ in range(int(sx * sy * 30)):  # clods, on the heap and spilled round it
        u, v = r.uniform(-1.1, 1.1), r.uniform(-1.08, 1.08)
        i, j = min(int((v + 1) / 2 * (ny - 1) + 0.5), ny - 1), min(int((u + 1) / 2 * (nx - 1) + 0.5), nx - 1)
        zz = z[max(i, 0), max(j, 0)] if abs(u) <= 1 and abs(v) <= 1 else 0.04
        s_ = r.uniform(0.015, 0.04)
        t = r.uniform(1.0, 1.4)
        g.add(T_ICO1, (cx + u * sx, cy + v * sy, zz + s_ * 0.15), (r.random() * 3, r.random() * 3, 0),
              (s_, s_ * 0.8, s_ * 0.55), col=(t, t * 0.96, t * 0.92, 1))


def graves(rng):
    """The fresh plots as real mounds over block.park()'s boxes; the open grave's walls of dug earth and a board at
    its side; its spoil heap over the grey-box mound."""
    r = random.Random(SEED + 8)
    g = Geo()
    for px, py in PLOTS:
        mound(g, r, px, py, 0.8, 1.3, 0.4, cover=(0.45, 0.95, 0.22, 0.0))
    mound(g, r, SPOIL[0] + 0.05, SPOIL[1], 0.6, 1.4, 0.72, cover=(0.3, 0.95, 0.475, -0.1), nx=18, ny=30)
    # the open grave: a lip of dug earth round block.park()'s black hole, its walls falling to a dark pit (the
    # vertex colour fades to near black at the bottom, so the hole reads deep)
    hx, hy = HOLE
    w, l = 0.45, 0.95
    rings = [(0.0, 0.053, 0.04), (0.0, 0.12, 0.35), (0.0, 0.2, 0.75), (0.07, 0.24, 0.9), (0.2, 0.15, 0.95),
             (0.38, 0.04, 0.95)]  # (outward offset, z, brightness)
    V, C = [], []
    seg = 10
    for off, z, br in rings:
        for side in range(4):
            for k in range(seg):
                t = k / seg
                if side == 0:
                    ux, uy = -1 + 2 * t, -1
                elif side == 1:
                    ux, uy = 1, -1 + 2 * t
                elif side == 2:
                    ux, uy = 1 - 2 * t, 1
                else:
                    ux, uy = -1, 1 - 2 * t
                jz = r.uniform(-0.02, 0.025) if 0.06 < z < 0.2 else 0.0
                jo = r.uniform(-0.03, 0.03) if off > 0 else 0.0
                V.append((hx + ux * (w + off + jo), hy + uy * (l + off + jo), z + jz))
                C.append((br, br * 0.96, br * 0.92, 1))
    n = 4 * seg
    F = [[ri * n + k, ri * n + (k + 1) % n, (ri + 1) * n + (k + 1) % n, (ri + 1) * n + k]
         for ri in range(len(rings) - 1) for k in range(n)]
    g.raw(V, F, col=np.array(C))
    o = g.obj("park.earth", [earth_mat()], smooth=True)
    # a near-black, matte floor a hair over the grey-box hole (which catches the sky like water)
    pit = gb.mat("park.pit", "#030202", rough=1.0)
    pit.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.0
    gb.box("park.pit", (hx, hy, 0.0525), (2 * w, 2 * l, 0.001), pit)
    # a board along the west side, where the mourners stand
    b = Geo()
    b.add(T_CUBE, (hx - w - 0.13, hy + 0.05, 0.255), (0.0, 0.0, 0.012), (0.24, 2.2, 0.03))
    wood = tex("boards", "plywood", 1.0, "#9a8468", 1.0)
    b.obj("park.boards", [wood])
    return o


# ---------------------------------------------------------------- leaves

def leaves(rng):
    """More dead leaves: drifted against the walls, the fences, the hedges and the stones' feet, and under the trees."""
    r = np.random.default_rng(SEED + 9)
    pts = []
    n = 2600
    kind = r.random(n)
    for k in range(n):
        u = kind[k]
        if u < 0.25:
            pts.append((r.uniform(X0 + 0.1, X1 - 0.1), Y1 - abs(r.normal(0, 0.25)) - 0.05))
        elif u < 0.38:
            pts.append((X0 + abs(r.normal(0, 0.3)) + 0.05, r.uniform(Y0, Y1)))
        elif u < 0.5:
            pts.append((X1 - abs(r.normal(0, 0.3)) - 0.05, r.uniform(Y0, Y1)))
        elif u < 0.62:
            pts.append((r.uniform(X0, X1), Y0 + abs(r.normal(0, 0.25)) + 0.06))
        elif u < 0.85:
            tx, ty, *_ = TREES[r.integers(len(TREES))]
            a, d = r.uniform(0, 6.28), abs(r.normal(0, 1.4))
            pts.append((tx + math.cos(a) * d, ty + math.sin(a) * d))
        else:
            sx, sy = STONES[r.integers(len(STONES))]
            pts.append((sx + r.normal(0, 0.45), sy - 0.12 - abs(r.normal(0, 0.15))))
    P = np.array(pts)
    x, y = P[:, 0], P[:, 1]
    ok = (x > X0) & (x < X1) & (y > Y0) & (y < Y1 + 0.05)
    ok &= ~((x > FIELD[0] - 0.1) & (x < FIELD[1] + 0.1) & (y > FIELD[2] - 0.1) & (y < FIELD[3] + 0.1))
    ok &= ~((np.abs(x - HOLE[0]) < 0.5) & (np.abs(y - HOLE[1]) < 1.0))
    x, y = x[ok], y[ok]
    n = len(x)
    ang = r.uniform(0, 6.28, n)
    s = r.uniform(0.03, 0.055, n)
    c, sn = np.cos(ang), np.sin(ang)
    loc = np.array([(-1, -0.6), (1, -0.6), (1, 0.6), (-1, 0.6)])
    V = np.zeros((n * 4, 3), np.float32)
    for k, (u, v) in enumerate(loc):
        V[k::4, 0] = x + (u * c - v * sn) * s
        V[k::4, 1] = y + (u * sn + v * c) * s
        V[k::4, 2] = 0.05 + 0.012 * r.random(n) + (0.006 * u * v)
    cols = np.array([gb.lin(h)[:3] for h in ("#6b4a2a", "#7a5a2e", "#5a3a22", "#8a6a3a", "#4a3a26")])
    C = np.repeat(cols[r.integers(len(cols), size=n)] * r.uniform(0.4, 0.75, (n, 1)), 4, axis=0)
    C = np.c_[C, np.ones(len(C))]
    F = np.arange(n * 4, dtype=np.int32).reshape(-1, 4)
    mesh_obj("park.leaves2", V, F, [attr_mat("leaves", 0.6, up=True)], C)


def build(S):
    import os
    skip = set(os.environ.get("PARK_SKIP", "").split(","))  # test stills only: build without some parts
    for name, fn in (("ground", ground), ("grass", grass), ("pebbles", pebbles), ("fence", fence), ("green", green),
                     ("trees", lambda r: trees()), ("furniture", furniture), ("wall", wall), ("old", old_stones),
                     ("graves", graves), ("leaves", leaves)):
        if name not in skip:
            fn(random.Random(SEED))
