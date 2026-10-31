"""Detail pass: interiors (see detail.py). The final look only; called at the end of block.build().

  the Dev's shop   a cramped repair shop running since 2008: a back wall of stocked steel shelves (boxed repair
                   kits and his third-party apps), a workbench under a pegboard, the tool cart, the register, his
                   hand-made signs, a window display of old phones
  the eatery       the turo-turo: six pans of food in the steam table, the chalk menu and numbered dish cards, the
                   rice cooker, a stainless back wall, the line of tables with black ladder-back chairs and condiment
                   caddies, the cooler, the water dispenser, the TV on its bracket, fans, a star garland and a parol
  the pawn shop    glass cases of gold, guitars on the wall, TVs, cameras, clocks, tools, bars inside the window
  the other shops  each its own trade, seen through the glass: counter, shelves and stock, window signs
  the lobby        the throne's racks get faces, status LEDs (never red) and cable bundles; the "worse copies" are a
                   white display of blank boxes; real plants; lounge seating in the east and west thirds; a monitor

Everything in a shop is parented to that shop's root (shop{i}: local +Y is the street, the room runs to local y -6.1,
x -2.9..2.9; the north shops' roots are turned round), merged into a few meshes per room. Lit fixtures in the shops take
their glow from that shop's light (its energy: 300 W lit, 0 dark, 60 at S47), so nothing glows in a dark shop.
Seeded: every render matches. Textures: scripts/gen_detail_interiors.py (assets/gen/detail/interiors/).
"""
import json
import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

import block as B
import gb
import kit

TEX = gb.ROOT / "assets" / "gen" / "detail" / "interiors"
SEED = 20261030
F0 = 0.16  # the shops' floor
_UV = {}


# ---------------------------------------------------------------- materials

def pm(name, hexcol, rough=0.6, metal=0.0, alpha=1.0):
    return gb.mat(f"int.{name}", hexcol, rough=rough, metal=metal, alpha=alpha)


def vc(name, rough=0.6, metal=0.0, bump=0.0):
    """A material whose colour is the mesh's "Col" attribute: one material for a shelf of differently coloured stock."""
    key = f"int.vc.{name}"
    if key in gb._MATS:
        return gb._MATS[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    a = nt.nodes.new("ShaderNodeAttribute")
    a.attribute_name = "Col"
    nt.links.new(a.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if bump:
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = 140.0
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    gb._MATS[key] = m
    return m


def amat(atlas, rough=0.7, light=None, k=0.0, alpha=False):
    """An atlas image on the mesh's UVs; light + k: it also glows, k at the shop light's full 300 W."""
    key = f"int.atlas.{atlas}.{rough}.{light.name if light else ''}.{k}"
    if key in gb._MATS:
        return gb._MATS[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(TEX / f"{atlas}.png"), check_existing=True)
    t.interpolation = "Cubic"
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if light is not None:
        nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
        drive_light(b.inputs["Emission Strength"], light, k)
    gb._MATS[key] = m
    return m


def drive_light(sock, light, k):
    """sock follows the shop's light: k at 300 W, 0 when the shop is dark."""
    d = sock.driver_add("default_value").driver
    d.type = "SCRIPTED"
    v = d.variables.new()
    v.name, v.type = "x", "SINGLE_PROP"
    v.targets[0].id_type = "LIGHT"
    v.targets[0].id = light.data
    v.targets[0].data_path = "energy"
    d.expression = f"x / 300 * {k}"


def lit(name, hexcol, light, k):
    """A fixture's glow (a tube, the cooler, the TV), keyed to its shop's light."""
    key = f"int.lit.{name}"
    if key in gb._MATS:
        return gb._MATS[key]
    m = gb.mat(key, hexcol, rough=0.4)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Color"].default_value = gb.lin(hexcol)
    drive_light(b.inputs["Emission Strength"], light, k)
    return m


def blink(name, hexcol, strength, period, duty, phase):
    """A status LED that blinks on the frame clock (the lobby: lit all night)."""
    m = gb.mat(f"int.led.{name}", hexcol, emit=strength)
    b = m.node_tree.nodes["Principled BSDF"]
    d = b.inputs["Emission Strength"].driver_add("default_value").driver
    d.type = "SCRIPTED"
    d.expression = f"{strength} * (0.25 + 0.75 * (((frame + {phase}) % {period}) < {duty}))"
    return m


def uv(atlas, item):
    if atlas not in _UV:
        _UV[atlas] = json.loads((TEX / f"{atlas}.json").read_text())
    return _UV[atlas][item]


# ---------------------------------------------------------------- geometry

def mtx(loc, rz=0.0, rx=0.0, ry=0.0, s=1.0):
    S = Matrix.Diagonal((*s, 1.0)) if isinstance(s, (tuple, list)) else Matrix.Scale(s, 4)
    return Matrix.Translation(loc) @ Euler((rx, ry, rz)).to_matrix().to_4x4() @ S


BOX_F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]  # front (-Y) is face 2


def box_v(size):
    x, y, z = (s / 2 for s in size)
    return [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z), (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]


def cyl_vf(r, h, n=12, r2=None):
    r2 = r if r2 is None else r2
    v = [(r * math.cos(a), r * math.sin(a), -h / 2) for a in (2 * math.pi * k / n for k in range(n))]
    v += [(r2 * math.cos(a), r2 * math.sin(a), h / 2) for a in (2 * math.pi * k / n for k in range(n))]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i)
                                                                  for i in range(n)]
    return v, f


_ICO = {}


def ico_vf(sub=1):
    if sub not in _ICO:
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
        _ICO[sub] = ([tuple(v.co) for v in bm.verts], [tuple(v.index for v in f.verts) for f in bm.faces])
        bm.free()
    return _ICO[sub]


def torus_vf(R, r, n=16, m=6):
    v, f = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            v.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(n):
        for j in range(m):
            f.append((i * m + j, ((i + 1) % n) * m + j, ((i + 1) % n) * m + (j + 1) % m, i * m + (j + 1) % m))
    return v, f


def star_vf(ro, ri, t, pts=5):
    ring = []
    for k in range(pts * 2):
        a = math.pi / 2 + k * math.pi / pts
        r = ro if k % 2 == 0 else ri
        ring.append((r * math.cos(a), 0.0, r * math.sin(a)))
    n = len(ring)
    v = [(x, -t / 2, z) for x, _, z in ring] + [(x, t / 2, z) for x, _, z in ring]
    f = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))] + [(i, n + i, n + (i + 1) % n, (i + 1) % n)
                                                                  for i in range(n)]
    return v, f


class MB:
    """A merged mesh: many small parts, a few materials, per-corner colour ("Col") and UVs."""

    def __init__(self, name):
        self.name, self.bm, self.mats = name, bmesh.new(), []
        self.uvl = self.bm.loops.layers.uv.new("UVMap")
        self.cl = self.bm.loops.layers.float_color.new("Col")

    def add(self, vf, m, M, col="#ffffff", uvs=None, smooth=False):
        verts, faces = vf
        vs = [self.bm.verts.new(M @ Vector(v)) for v in verts]
        if m not in self.mats:
            self.mats.append(m)
        mi = self.mats.index(m)
        c = gb.lin(col) if isinstance(col, str) else col
        for fi, f in enumerate(faces):
            try:
                face = self.bm.faces.new([vs[i] for i in f])
            except ValueError:
                continue
            face.material_index, face.smooth = mi, smooth
            for li, lp in enumerate(face.loops):
                lp[self.cl] = c
                if uvs:
                    lp[self.uvl].uv = uvs(fi, li)

    def box(self, loc, size, m, rz=0.0, col="#ffffff", rect=None, rx=0.0, ry=0.0):
        """rect: an atlas rect on the front (-Y before rz) face; the other faces take the rect's top-left colour."""
        uvs = None
        if rect:
            u0, v0, u1, v1 = rect[:4]
            fr = ((u0, v0), (u1, v0), (u1, v1), (u0, v1))
            side = (u0 + 0.002, v1 - 0.002)
            uvs = lambda fi, li: fr[li] if fi == 2 else side  # noqa: E731
        self.add((box_v(size), BOX_F), m, mtx(loc, rz, rx, ry), col, uvs)

    def cyl(self, loc, r, h, m, col="#ffffff", n=12, r2=None, rx=0.0, ry=0.0, rz=0.0, smooth=True):
        self.add(cyl_vf(r, h, n, r2), m, mtx(loc, rz, rx, ry), col, smooth=smooth)

    def blob(self, loc, size, m, col="#ffffff", rng=None, sub=1, rz=0.0, rx=0.0, ry=0.0):
        v, f = ico_vf(sub)
        if rng:
            v = [tuple(c * rng.uniform(0.85, 1.12) for c in p) for p in v]
        self.add((v, f), m, mtx(loc, rz, rx, ry, size), col, smooth=True)

    def quad(self, loc, size, m, rect, facing="+Y", rz=None):
        """A sign or poster: the atlas rect on a quad facing `facing` (gb.plane's convention)."""
        w, h = size[0] / 2, size[1] / 2
        v = [(-w, 0, -h), (w, 0, -h), (w, 0, h), (-w, 0, h)]
        rot = {"-Y": 0.0, "+Y": math.pi, "+X": math.pi / 2, "-X": -math.pi / 2}[facing] if rz is None else rz
        u0, v0, u1, v1 = rect[:4]
        fr = ((u0, v0), (u1, v0), (u1, v1), (u0, v1))
        self.add((v, [(0, 1, 2, 3)]), m, mtx(loc, rot), uvs=lambda fi, li: fr[li])

    def tube(self, pts, r, m, col="#202020", n=6):
        """A cable along a polyline."""
        for a, b in zip(pts, pts[1:]):
            a, b = Vector(a), Vector(b)
            d = b - a
            q = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
            self.add(cyl_vf(r, d.length, n), m, Matrix.Translation((a + b) / 2) @ q, col, smooth=True)

    def done(self, parent=None):
        me = bpy.data.meshes.new(self.name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        return gb.link(bpy.data.objects.new(self.name, me), parent)


def hide(o):
    o.hide_render = o.hide_viewport = True


def hide_prefix(*prefixes):
    for o in bpy.data.objects:
        if o.name.startswith(prefixes):
            hide(o)


class Wall:
    """A wall's frame in a room: point(u, d, z) is u metres along it, d out from it; rot faces its stock into the
    room (a kit model's front is -Y)."""

    def __init__(self, origin, along, out):
        self.o, self.a, self.n = Vector((*origin, 0)), Vector((*along, 0)), Vector((*out, 0))
        self.rot = math.atan2(out[1], out[0]) + math.pi / 2

    def p(self, u, d, z):
        q = self.o + self.a * u + self.n * d
        return (q.x, q.y, z)


def room_walls():
    return {"back": Wall((-2.9, -6.1), (1, 0), (0, 1)), "west": Wall((-2.9, -0.4), (0, -1), (1, 0)),
            "east": Wall((2.9, -6.1), (0, 1), (-1, 0))}


def shelving(mb, w, u0, u1, levels, D, wood, col="#7a5a3a", back=None):
    """Wall shelving: uprights, boards at `levels` (their top faces), an optional back panel."""
    n = max(1, round((u1 - u0) / 1.0))
    for k in range(n + 1):
        u = u0 + (u1 - u0) * k / n
        mb.box(w.p(u, D / 2, (F0 + levels[-1]) / 2 + 0.01), (0.03, D, levels[-1] - F0 + 0.02), wood, w.rot, col)
    for z in levels:
        mb.box(w.p((u0 + u1) / 2, D / 2, z - 0.012), (u1 - u0, D, 0.024), wood, w.rot, col)
    if back:
        mb.box(w.p((u0 + u1) / 2, 0.045, (F0 + levels[-1]) / 2), (u1 - u0, 0.02, levels[-1] - F0), wood, w.rot, back)


def fixtures(mb, light, xs, ys, warm="#fff1d6", along_y=False, k=5.0):
    """Ceiling fluorescents: a housing and a diffuser that glows with the shop's light."""
    hous = pm("fixture", "#e8e6e0", 0.5, 0.3)
    tube = lit(f"tube.{light.name}", warm, light, k)
    for x in xs:
        for y in ys:
            sz = (0.24, 1.25, 0.06) if along_y else (1.25, 0.24, 0.06)
            mb.box((x, y, 4.17), sz, hous)
            mb.box((x, y, 4.135), (sz[0] - 0.06, sz[1] - 0.06, 0.012), tube)


def paint(mb, hexcol, name, walls=("back", "west", "east"), grime=0.35, z1=4.19):
    """The room's painted walls, 1.5 cm proud of the shell's (at 5 mm they flickered seen from the street)."""
    m = pm(f"paint.{name}", hexcol, 0.85)
    if not m.get("grimed"):
        gb.grime(m, amt=grime, streak=0.6, damp=0.8)
        m["grimed"] = 1
    if "back" in walls:
        mb.box((0, -6.085, (F0 + z1) / 2), (5.78, 0.01, z1 - F0), m)
    if "west" in walls:
        mb.box((-2.88, -3.25, (F0 + z1) / 2), (0.01, 5.7, z1 - F0), m)
    if "east" in walls:
        mb.box((2.88, -3.25, (F0 + z1) / 2), (0.01, 5.7, z1 - F0), m)
    return m


def window_signs(mb, i, m, xs, z=2.15):
    """The shop's hand-made signs, taped inside the glass, facing the street."""
    rng = random.Random(SEED + i)
    for k, x in enumerate(xs):
        key = f"s{i}_{k}"
        if key not in _UV["shops"]:
            break
        r = uv("shops", key)
        w = 0.62
        mb.add(([(-w / 2, 0, -w / r[4] / 2), (w / 2, 0, -w / r[4] / 2), (w / 2, 0, w / r[4] / 2), (-w / 2, 0, w / r[4] / 2)],
                [(0, 1, 2, 3)]), m, mtx((x, -0.04, z + rng.uniform(-0.15, 0.1)), math.pi, ry=rng.uniform(-0.05, 0.05)),
               uvs=lambda fi, li, r=r: ((r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3]))[li])


_LOD = {}
KEEP = ("potted_plant_01", "potted_plant_02")  # leaf cards: decimating them would tear the leaves


def lod(aid, target=5000):
    """The kit model's mesh, decimated once to about `target` faces for the props seen through a shop window; every
    copy shares it (performance: the interiors add a few million faces otherwise)."""
    me = kit.load(aid)
    n = len(me.polygons)
    if n <= target * 1.3 or aid in KEEP:
        return me
    if aid not in _LOD:
        o = gb.link(bpy.data.objects.new(f"tmp.lod.{aid}", me))
        md = o.modifiers.new("lod", "DECIMATE")
        md.ratio = target / n
        dg = bpy.context.evaluated_depsgraph_get()
        new = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        new.name = f"int.lod.{aid}"
        new["dims"] = me["dims"]
        bpy.data.objects.remove(o)
        _LOD[aid] = new
    return _LOD[aid]


def kp(name, aid, loc, rz=0.0, s=1.0, parent=None, rot=None, target=5000):
    o = gb.link(bpy.data.objects.new(name, lod(aid, target)), parent)
    o.location = loc
    o.rotation_euler = rot if rot else (0, 0, rz)
    o.scale = (s,) * 3 if isinstance(s, (int, float)) else s
    return o


def shop_root(i):
    return bpy.data.objects[f"shop{i}"]


def shop_light(S, i):
    return S["shoplights"][i]


# ---------------------------------------------------------------- the Dev's shop (shop 1)

def dev_shop(S):
    i = 1
    R, L = shop_root(i), shop_light(S, i)
    rng = random.Random(SEED + 101)
    hide_prefix("dev.shelf", "dev.app")
    W = room_walls()
    _ = uv("dev", "app0")
    sign = amat("dev", 0.75)
    stock = amat("dev", 0.45)
    wood = vc("wood", 0.7)
    metal = vc("metal", 0.4, 0.6)
    plast = vc("plastic", 0.45)
    glossy = vc("glossy", 0.25)
    mb = MB("int.dev")
    # the floor: old linoleum (style spec), a rubber mat behind the counter
    mb.box((0, -3.25, F0 + 0.004), (5.78, 5.7, 0.008), gb.tex_mat("int.lino", "old_linoleum_flooring_01"))
    mb.box((0.2, -4.4, F0 + 0.012), (2.6, 0.8, 0.012), plast, col="#1c1c1c")
    paint(mb, "#c9c6ae", "dev", grime=0.45)
    fixtures(mb, L, (-1.2, 1.4), (-2.0, -4.6), k=5.0)
    # the back wall: four steel shelving units, stocked
    levels = [F0 + z for z in (0.13, 0.64, 1.15, 1.65, 2.13)]
    for k, cx in enumerate((-1.15, 0.0, 1.15, 2.3)):
        kp(f"int.dev.shelves{k}", "steel_frame_shelves_01", (cx, -5.84, F0), 0.0, 0.1, R)
        for lv, z in enumerate(levels):
            dev_stock(mb, rng, cx, -5.84, z, lv, stock, plast, glossy, metal, R, k)
    # above the shelves: the clock and the SINCE 2008 card
    kp("int.dev.clock", "wall_clock", (-0.6, -6.08, 3.05), math.pi, 1.0, R)
    r = uv("dev", "since")
    mb.quad((1.3, -6.06, 2.75), (0.55, 0.55 / r[4]), sign, r)
    # the west wall: the workbench under a pegboard of tools
    w = W["west"]
    kp("int.dev.bench", "metal_office_desk", w.p(4.0, 0.48, F0), w.rot, 1.0, R)
    bz = F0 + 0.79
    kp("int.dev.laptop", "classic_laptop", (-2.42, -4.75, bz), w.rot + 0.25, 0.8, R)
    kp("int.dev.board", "circuit_board", (-2.35, -3.85, bz), 0.4, 0.6, R)
    kp("int.dev.meter", "retro_multimeter", (-2.62, -4.1, bz), w.rot - 0.3, 0.9, R)
    kp("int.dev.lamp", "desk_lamp_arm_01", (-2.7, -5.2, bz), w.rot + 0.6, 0.9, R)
    kp("int.dev.screwdrivers", "screwdrivers_02", (-2.1, -4.25, bz), 0.2, 1.0, R)
    kp("int.dev.pliers", "pliers", (-2.15, -3.55, bz + 0.009), 0.0, 1.0, R, rot=(math.pi / 2, 0, 1.1))
    for k in range(6):  # phones open on the bench, mid-repair
        x, y = -2.55 + rng.uniform(-0.15, 0.25), -3.55 - k * 0.08 + rng.uniform(-0.04, 0.04)
        if k % 2:
            mb.box((x, y - 0.45, bz + 0.006), (0.075, 0.155, 0.009), plast, rng.uniform(0, 3), "#2b2f36")
        else:
            mb.box((x, y - 0.4, bz + 0.004), (0.07, 0.15, 0.006), glossy, rng.uniform(0, 3), "#0d0f12")
    r = uv("dev", "pegboard")
    mb.quad(w.p(4.0, 0.045, 1.85), (1.9, 0.95), sign, r, rz=w.rot)
    for k, (aid, u, z, rot) in enumerate((("wooden_hammer_01", 3.3, 1.6, None), ("pliers", 3.55, 1.75, None),
                                          ("pliers", 3.7, 1.75, None), ("handsaw_wood", 4.4, 2.05, None),
                                          ("wooden_hammer_01", 4.9, 1.62, None))):
        kp(f"int.dev.peg{k}", aid, w.p(u, 0.06, z), w.rot + (math.pi / 2 if aid == "handsaw_wood" else 0), 1.0, R)
    for k in range(4):  # cable coils on pegs
        mb.add(torus_vf(0.08, 0.008, 18, 5), plast, mtx(w.p(4.55 + k * 0.17, 0.07, 1.55), w.rot, math.pi / 2),
               ("#151515", "#e8e8e8", "#151515", "#2a4d8f")[k], smooth=True)
    # under the bench: a crate of cables, a bin
    kp("int.dev.crate", "plastic_crate_02", (-2.45, -5.0, F0), w.rot, 0.95, R)
    for k in range(5):
        mb.add(torus_vf(0.1, 0.009, 16, 5), plast, mtx((-2.45 + rng.uniform(-0.12, 0.12), -5.0, F0 + 0.2 + k * 0.02),
                                                      rng.uniform(0, 3), rng.uniform(-0.3, 0.3)),
               rng.choice(("#151515", "#e8e8e8", "#2b2f36")), smooth=True)
    mb.cyl((-2.6, -3.35, F0 + 0.2), 0.16, 0.4, metal, "#6a6d70", r2=0.18)  # the bin
    mb.blob((-2.6, -3.35, F0 + 0.38), (0.12, 0.12, 0.05), plast, "#d8d2c4", rng)
    # the back west corner: boxes of returns
    for k, (x, y, z, s) in enumerate(((-2.45, -5.8, 0, 0.75), (-2.5, -5.75, 0.26, 0.6))):
        kp(f"int.dev.carton{k}", "cardboard_box_01", (x, y, F0 + z), rng.uniform(-0.2, 0.2), s, R)
    # the east wall: the tool cart, the price list, the first dollar, a chair for waiting
    e = W["east"]
    kp("int.dev.cart", "tool_cart", e.p(1.5, 0.39, F0), e.rot, 1.0, R)
    kp("int.dev.toolbox", "metal_toolbox", e.p(1.2, 0.39, F0 + 0.9), e.rot + 0.1, 0.9, R)
    kp("int.dev.chair", "plastic_monobloc_chair_01", e.p(4.1, 0.35, F0), e.rot + 0.2, 0.95, R)
    for nm, u, z, wd in (("prices", 4.4, 1.95, 0.48), ("dollar", 1.7, 1.95, 0.42), ("nosoft", 2.25, 2.85, 0.42)):
        r = uv("dev", nm)
        mb.quad(e.p(u, 0.045, z), (wd, wd / r[4]), sign, r, rz=e.rot)
    # the counter (dev.counter): the register, a glass case of phones, a jar of pens; a sign on its front
    cz = 1.0
    kp("int.dev.register", "CashRegister_01", (-0.3, -3.62, cz), 0.1, 0.72, R)
    gl = pm("caseglass", "#cfe0e8", 0.05, alpha=0.2)
    mb.box((-1.25, -3.45, cz + 0.13), (0.55, 0.35, 0.26), gl)
    for k in range(4):
        mb.box((-1.45 + k * 0.13, -3.45, cz + 0.07), (0.07, 0.03, 0.13), glossy, 0.0,
               ("#0d0f12", "#e8e8e8", "#0d0f12", "#9fb6c4")[k], rx=-0.3)
    mb.cyl((-1.62, -3.75, cz + 0.06), 0.04, 0.12, glossy, "#9fb6c4")
    for k in range(5):
        mb.cyl((-1.62 + rng.uniform(-0.02, 0.02), -3.75 + rng.uniform(-0.02, 0.02), cz + 0.15), 0.004, 0.15, plast,
               rng.choice(("#2a4d8f", "#151515", "#3d6b3a")), n=6, rx=rng.uniform(-0.2, 0.2), ry=rng.uniform(-0.2, 0.2))
    for k in range(3):  # repair tickets, a pad and a spike
        mb.box((0.12 + k * 0.004, -3.3, cz + 0.006 + k * 0.006), (0.1, 0.15, 0.006), plast, 0.2 + k * 0.1,
               ("#f2efe6", "#f4e9b8", "#cfe0f0")[k])
    mb.cyl((0.3, -3.3, cz + 0.08), 0.002, 0.16, metal, "#b0b4b8", n=4)
    for k in range(6):
        mb.box((0.3, -3.3, cz + 0.02 + k * 0.012), (0.08, 0.1, 0.002), plast, k * 0.5, "#f2efe6")
    r = uv("dev", "nosoft")
    mb.quad((-1.0, -3.08, 0.6), (0.4, 0.4 / r[4]), sign, r)
    r = uv("dev", "backsoon")
    mb.quad((1.1, -3.08, 0.62), (0.3, 0.3 / r[4]), sign, r)
    # the window: a riser of old phones on stands, his signs taped to the glass
    mb.box((-0.9, -0.35, 0.6), (3.5, 0.5, 0.06), wood, col="#5a4632")
    mb.box((-0.9, -0.35, 0.36), (3.5, 0.48, 0.42), wood, col="#3a2e24")
    for k in range(12):
        x = -2.5 + k * 0.28
        tab = k % 4 == 3
        sz = (0.17, 0.012, 0.24) if tab else (0.075, 0.009, 0.15)
        mb.box((x, -0.35, 0.63 + 0.015), (0.06, 0.06, 0.03), plast, col="#e8e8e8")
        mb.box((x, -0.33, 0.63 + sz[2] / 2 + 0.02), sz, glossy, math.pi,
               rng.choice(("#0d0f12", "#e8e8e8", "#2b2f36", "#c9ccd1")), rx=0.25)
        r = uv("dev", "phone")
        mb.box((x, -0.325 + 0.008, 0.63 + sz[2] / 2 + 0.024), (sz[0] * 0.88, 0.002, sz[2] * 0.86), stock, math.pi,
               rect=r, rx=0.25)
    backlit = amat("dev", 0.75, L, 0.6)
    for nm, x, z, wd in (("we_fix", -1.7, 2.25, 1.0), ("screen", 0.45, 2.1, 0.62)):
        r = uv("dev", nm)
        mb.quad((x, -0.03, z), (wd, wd / r[4]), backlit, r)
        mb.box((x, -0.04, z), (wd, 0.002, wd / r[4]), plast, 0, "#e8e2d0")  # 9 mm behind the print (3 mm flickered)
    r = uv("dev", "open")
    mb.quad((1.9, -0.12, 1.75), (0.42, 0.21), backlit, r)
    mb.tube([(1.75, -0.12, 1.86), (1.9, -0.12, 2.05), (2.05, -0.12, 1.86)], 0.003, plast, "#e8e2cf", n=4)
    mb.done(R)


def dev_stock(mb, rng, cx, y, z, lv, stock, plast, glossy, metal, R, unit):
    """One shelf of the Dev's stock, facing the street: his apps boxed, repair kits, parts bins, old phones."""
    x0, x1 = cx - 0.5, cx + 0.5
    kind = ("bins", "kits", "apps", "phones", "top")[lv] if unit % 2 == 0 else ("bins", "apps", "kits", "coils", "top")[lv]
    if kind == "apps":
        x = x0 + 0.02
        while x < x1 - 0.13:
            k = rng.randrange(6)
            for d in range(rng.choice((1, 2, 3))):
                mb.box((x + 0.065, y + 0.15 - d * 0.07, z + 0.09), (0.13, 0.055, 0.173), stock, math.pi,
                       rect=uv("dev", f"app{k}"))
            x += 0.14 + rng.uniform(0, 0.02)
    elif kind == "kits":
        x = x0 + 0.02
        while x < x1 - 0.17:
            k = rng.randrange(16)
            for h in range(rng.choice((1, 2, 3))):
                mb.box((x + 0.085, y + 0.12, z + 0.065 + h * 0.128), (0.17, 0.08, 0.127), stock,
                       math.pi + rng.uniform(-0.06, 0.06), rect=uv("dev", f"kit{k}"))
            x += 0.18 + rng.uniform(0, 0.03)
    elif kind == "bins":
        for k in range(4):
            x = x0 + 0.13 + k * 0.245
            col = ("#2a4d8f", "#d9b43c", "#2a4d8f", "#4b4f3a")[(k + unit) % 4]
            mb.box((x, y + 0.02, z + 0.08), (0.22, 0.42, 0.16), plast, 0.0, col)
            mb.box((x, y + 0.231, z + 0.1), (0.15, 0.004, 0.05), plast, 0.0, "#f2efe6")  # the label
            for _ in range(3):
                mb.box((x + rng.uniform(-0.06, 0.06), y + 0.15, z + 0.17), (0.05, 0.02, 0.04), metal,
                       rng.uniform(0, 3), "#b0b4b8")
    elif kind == "phones":
        for k in range(9):  # old phones and tablets, in trade, lying and propped
            x = x0 + 0.06 + k * 0.105
            if k % 3 == 0:
                mb.box((x + 0.03, y + 0.05, z + 0.12), (0.17, 0.012, 0.23), glossy, math.pi,
                       rng.choice(("#0d0f12", "#2b2f36")), rx=0.2)
            else:
                mb.box((x, y + 0.12, z + 0.006), (0.07, 0.14, 0.012), glossy, rng.uniform(-0.2, 0.2),
                       rng.choice(("#0d0f12", "#e8e8e8", "#2b2f36", "#6a6d70", "#2f7f7a")))
        mb.box((cx, y + 0.18, z + 0.03), (0.6, 0.004, 0.06), plast, 0.0, "#f4d23c")  # a price strip
    elif kind == "coils":
        for k in range(7):
            mb.add(torus_vf(0.065, 0.012, 16, 5), plast,
                   mtx((x0 + 0.08 + k * 0.14, y + rng.uniform(-0.05, 0.12), z + 0.012 + (k % 2) * 0.02), rng.uniform(0, 3)),
                   rng.choice(("#151515", "#e8e8e8", "#e8e8e8", "#2a4d8f")), smooth=True)
    else:  # the top: overstock in cartons
        for k in range(2):
            kp(f"int.dev.top{unit}{k}", "cardboard_box_01", (x0 + 0.25 + k * 0.5, y + rng.uniform(-0.05, 0.05), z),
               rng.uniform(-0.3, 0.3), rng.uniform(0.55, 0.7), R)


# ---------------------------------------------------------------- the eatery (shop 0)

DISH = [  # base colours, piece kind, piece colours: the pans along the steam table, west to east (dish cards 1-6)
    (("#3a2414", "#4a2f1c", "#2e1d12"), "chunks", ("#5a3a22", "#3e2716", "#6a4428", "#e9e2c4")),  # adobo (and eggs)
    (("#c9a468", "#d9b778", "#b88c4a"), "noodles", ("#e0c48a", "#d4a860", "#6b8f3a", "#e0913a")),  # pancit
    (("#5a4a24", "#6a5a2a"), "veg", ("#d48a2c", "#5d7a32", "#4a3a5a", "#8a9a40", "#e0b050")),  # pinakbet
    (("#7a5a2c", "#6a4a22"), "fish", ("#b8783a", "#c88a40", "#a8682c")),  # fried bangus
    (("#8a6a3a",), "rolls", ("#c88a3a", "#d89a4a", "#b8782c")),  # lumpia
    (("#8a4a22", "#9a5a2c", "#7a4220"), "cubes", ("#6a3a1e", "#e6c46a", "#e0913a", "#6b8f3a")),  # menudo
]


def food_pan(mb, rng, x, y, z, dish, steel, food):
    """A hotel pan in the steam table (its rim at z), filled: a lumpy, glossy surface heaped in the middle, and pieces."""
    W_, D_ = 0.5, 0.35
    for dx, dy, sx, sy in ((0, D_ / 2, W_, 0.012), (0, -D_ / 2, W_, 0.012), (W_ / 2, 0, 0.012, D_), (-W_ / 2, 0, 0.012, D_)):
        mb.box((x + dx, y + dy, z + 0.005), (sx, sy, 0.03), steel, col="#c8ccd0")
    base, kind, pcs = DISH[dish]
    nx, ny = 11, 8
    verts, faces, cols = [], [], []
    for j in range(ny):
        for i in range(nx):
            u, v = i / (nx - 1), j / (ny - 1)
            edge = min(u, 1 - u, v, 1 - v)
            h = 0.025 * min(1.0, edge * 5) + rng.uniform(-0.006, 0.008)
            verts.append(((u - 0.5) * (W_ - 0.03), (v - 0.5) * (D_ - 0.03), h - 0.01))
    for j in range(ny - 1):
        for i in range(nx - 1):
            faces.append((j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i))
    mb.add((verts, faces), food, mtx((x, y, z - 0.01)), rng.choice(base), smooth=True)
    top = z + 0.012

    def spot():
        return x + rng.uniform(-0.19, 0.19), y + rng.uniform(-0.12, 0.12)
    if kind == "chunks":
        for k in range(22):
            px, py = spot()
            c = pcs[3] if k < 3 else rng.choice(pcs[:3])
            s = (0.03, 0.022, 0.02) if k < 3 else (rng.uniform(0.025, 0.04), rng.uniform(0.02, 0.03), 0.02)
            mb.blob((px, py, top + 0.008), s, food, c, rng, rz=rng.uniform(0, 3))
    elif kind == "noodles":
        for k in range(220):
            px, py = spot()
            mb.cyl((px, py, top + rng.uniform(0, 0.018)), 0.003, rng.uniform(0.03, 0.06), food,
                   pcs[0] if k % 5 else rng.choice(pcs), n=5, rx=math.pi / 2 + rng.uniform(-0.3, 0.3), rz=rng.uniform(0, 3))
        for k in range(14):
            px, py = spot()
            mb.box((px, py, top + 0.012), (0.03, 0.006, 0.004), food, rng.uniform(0, 3), rng.choice(pcs[2:]))
    elif kind == "veg":
        for k in range(26):
            px, py = spot()
            c = rng.choice(pcs)
            if c == pcs[0]:
                mb.box((px, py, top + 0.008), (0.03, 0.03, 0.025), food, rng.uniform(0, 3), c, rx=rng.uniform(-0.3, 0.3))
            else:
                mb.blob((px, py, top + 0.006), (0.025, 0.018, 0.012), food, c, rng, rz=rng.uniform(0, 3))
    elif kind == "fish":
        for k in range(3):  # butterflied milkfish, fried golden
            px, py = x - 0.13 + k * 0.13, y + rng.uniform(-0.02, 0.02)
            mb.blob((px, py, top + 0.008), (0.055, 0.14, 0.014), food, rng.choice(pcs), rng, rz=rng.uniform(-0.2, 0.2))
            mb.add(star_vf(0.03, 0.012, 0.004, 3), food, mtx((px, py - 0.15, top + 0.01), 0, math.pi / 2), pcs[2])
    elif kind == "rolls":
        for k in range(16):
            px = x - 0.18 + (k % 8) * 0.05
            py = y - 0.07 + (k // 8) * 0.13 + rng.uniform(-0.01, 0.01)
            mb.cyl((px, py, top + 0.01 + (k % 3 == 0) * 0.02), 0.016, 0.12, food, rng.choice(pcs), n=8, rx=math.pi / 2,
                   rz=rng.uniform(-0.15, 0.15))
    else:
        for k in range(30):
            px, py = spot()
            mb.box((px, py, top + 0.006), (0.024, 0.024, 0.02), food, rng.uniform(0, 3), rng.choice(pcs),
                   rx=rng.uniform(-0.4, 0.4))
    # a serving spoon in most pans
    if dish != 3:
        a = rng.uniform(-0.4, 0.4)
        mb.blob((x + 0.08, y - 0.05, top + 0.012), (0.04, 0.03, 0.01), steel, "#c8ccd0", rz=a)
        mb.cyl((x + 0.08 + 0.1 * math.sin(a), y + 0.05, top + 0.05), 0.006, 0.22, steel, "#c8ccd0", n=6,
               rx=-1.1, rz=a)


def ladder_chair(mb, loc, rz, m):
    """A black ladder-back chair: four legs, a woven seat, two tall back posts and three slats (front is -Y)."""
    x, y, z = loc
    M = Matrix.Translation(loc) @ Matrix.Rotation(rz, 4, "Z")

    def b(c, s, col="#141414"):
        mb.add((box_v(s), BOX_F), m, M @ Matrix.Translation(c), col)
    for sx in (-0.19, 0.19):
        b((sx, -0.18, 0.23), (0.032, 0.032, 0.46))
        b((sx, 0.18, 0.5), (0.034, 0.034, 1.0))
        b((0, 0, 0.16) if sx < 0 else (0, 0.0, 0.16), (0.36, 0.018, 0.018))
    for sy in (-0.18, 0.18):
        b((0, sy, 0.13), (0.36, 0.018, 0.018))
    b((0, 0, 0.465), (0.42, 0.42, 0.035), "#1d1a16")
    for k in range(3):
        b((0, 0.185, 0.62 + k * 0.13), (0.38, 0.016, 0.06))


def eatery(S):
    i = 0
    R, L = shop_root(i), shop_light(S, i)
    rng = random.Random(SEED + 100)
    hide_prefix("eat.pan", "eat.table", "eat.tleg", "eat.chair", "eat.menu", "eat.card")
    _ = uv("eatery", "menu")
    sign = amat("eatery", 0.8)
    chalk = amat("eatery", 0.9)
    steel = vc("steel", 0.3, 0.85)
    food = vc("food", 0.28, bump=0.15)
    plast = vc("eplastic", 0.45)
    wood = vc("ewood", 0.6)
    black = vc("black", 0.5)
    mb = MB("int.eatery")
    paint(mb, "#c9a43c", "eatery", walls=("east",), grime=0.25)
    fixtures(mb, L, (-1.2, 1.5), (-2.2, -4.4), k=5.5)
    # the steam table (eat.counter, x -1.4..2.6, y -4.75..-5.65, top 1.0): pans of food, a rail for the trays, posts
    for k in range(6):
        food_pan(mb, rng, -0.9 + k * 0.6, -5.2, 1.03, k, steel, food)
    mb.box((0.6, -5.2, 1.002), (4.0, 0.9, 0.004), steel, col="#9a9ea2")
    for dy in (-0.05, 0.05):
        mb.cyl((0.6, -4.55 + dy, 0.97), 0.012, 4.0, steel, "#c8ccd0", n=8, ry=math.pi / 2)
    for x in (-1.38, 0.6, 2.58):
        mb.box((x, -4.8, 1.35), (0.025, 0.025, 0.7), steel, col="#c8ccd0")
    mb.box((0.6, -4.95, 1.66), (4.0, 0.35, 0.012), pm("eguard", "#cfe0e8", 0.05, alpha=0.22))
    for k in range(7):  # front skirt: stainless panels with seams
        mb.box((-1.4 + 0.29 + k * 0.57, -4.745, 0.5), (0.008, 0.006, 0.9), steel, col="#7a7e82")
    # a side stand at the west end: the rice cooker, plates, utensils
    mb.box((-1.72, -5.22, 0.86), (0.55, 0.75, 0.04), steel, col="#c8ccd0")
    for dx in (-0.25, 0.25):
        for dy in (-0.35, 0.35):
            mb.box((-1.72 + dx, -5.22 + dy, 0.51), (0.03, 0.03, 0.7), steel, col="#c8ccd0")
    mb.box((-1.72, -5.22, 0.3), (0.55, 0.75, 0.02), steel, col="#9a9ea2")
    mb.cyl((-1.72, -5.38, 1.04), 0.17, 0.32, plast, "#f2efe6", n=20)
    mb.cyl((-1.72, -5.38, 1.21), 0.165, 0.04, plast, "#d8d4c8", n=20, r2=0.1)
    mb.box((-1.72, -5.2, 0.98), (0.1, 0.06, 0.06), plast, 0, "#5a5d63")
    for k in range(12):
        mb.cyl((-1.75, -4.98, 0.885 + k * 0.012), 0.11, 0.008, plast, "#f4f1ea", n=16)
    for k in range(5):  # green trays stacked
        mb.box((-1.72, -5.2, 0.33 + k * 0.025), (0.45, 0.35, 0.018), plast, 0, "#2f8a3a")
    # the stainless back wall and shelf: stockpots, plates, a ladle rail
    mb.box((0.6, -6.017, 1.0), (4.6, 0.012, 1.7), steel, col="#a8acb0")
    mb.box((0.6, -5.95, 1.62), (4.6, 0.26, 0.025), steel, col="#c8ccd0")
    for k, x in enumerate((-1.3, -0.6, 1.9, 2.5)):
        mb.cyl((x, -5.95, 1.63 + 0.14), 0.15 if k % 2 == 0 else 0.11, 0.28, steel, "#b8bcc0", n=18)
    for k in range(3):
        mb.cyl((0.4 + k * 0.4, -5.95, 1.65), 0.12, 0.05, plast, "#f4f1ea", n=16)
    mb.cyl((0.6, -5.99, 1.42), 0.008, 2.0, steel, "#c8ccd0", n=6, ry=math.pi / 2)
    for k in range(6):
        x = -0.2 + k * 0.3
        mb.cyl((x, -5.985, 1.28), 0.005, 0.28, steel, "#c8ccd0", n=6)
        mb.blob((x, -5.96, 1.13), (0.045, 0.045, 0.02), steel, "#c8ccd0", rx=math.pi / 2)
    # the menu: chalk over the back wall, numbered dish cards under it
    r = uv("eatery", "menu")
    mb.quad((0.6, -6.0, 3.12), (4.4, 4.4 / r[4]), chalk, r)
    for k in range(6):
        r = uv("eatery", f"dish{k}")
        mb.quad((-1.25 + k * 0.75, -6.0, 2.13), (0.5, 0.5 / r[4]), sign, r)
    r = uv("eatery", "cash")
    mb.quad((2.3, -4.735, 0.75), (0.3, 0.3 / r[4]), sign, r)
    # the line of tables (the west wall), real tables and black ladder-back chairs
    for k in range(3):
        y = -1.0 - k * 1.5
        mb.box((-2.3, y, 0.755), (0.8, 1.1, 0.04), wood, col="#7a5636")
        mb.box((-2.3, y, 0.715), (0.7, 1.0, 0.05), wood, col="#5a3e26")
        for dx in (-0.33, 0.33):
            for dy in (-0.48, 0.48):
                mb.box((-2.3 + dx, y + dy, 0.43), (0.035, 0.035, 0.56), black, col="#202020")
        ladder_chair(mb, (-1.62, y + (0.0 if k else 0.15), F0), math.pi / 2 + rng.uniform(-0.12, 0.12), black)
        if k:  # the condiment caddy at the wall end (the breakfast table stays clear)
            cx, cy = -2.58, y + 0.32
            mb.box((cx, cy, 0.79), (0.16, 0.24, 0.015), steel, col="#b8bcc0")
            for j, (col, h) in enumerate((("#2a1408", 0.17), ("#e8e4d4", 0.19), ("#8a5a1c", 0.16))):  # soy, vinegar, patis
                mb.cyl((cx, cy - 0.08 + j * 0.075, 0.8 + h / 2), 0.026, h, plast, col, n=10)
                mb.cyl((cx, cy - 0.08 + j * 0.075, 0.8 + h + 0.015), 0.012, 0.03, plast, "#d8d4c8", n=8)
            mb.box((cx, cy + 0.2, 0.84), (0.1, 0.12, 0.09), steel, col="#c8ccd0")  # napkins
            mb.box((cx, cy + 0.2, 0.895), (0.08, 0.1, 0.02), plast, col="#f6f4ee")
            mb.cyl((cx + 0.1, cy + 0.12, 0.83), 0.018, 0.06, plast, "#e8e4d4", n=8)  # toothpicks
    ladder_chair(mb, (-2.3, -4.88, F0), 0.0 + math.pi, black)  # the far end of the last table
    # the west wall: the clock, a calendar, a framed print
    w = room_walls()["west"]
    kp("int.eat.clock", "wall_clock", w.p(2.1, 0.065, 2.75), w.rot, 1.0, R)
    for nm, u, z, wd in (("calendar", 3.65, 1.75, 0.36), ("landscape", 0.85, 1.85, 0.62)):
        r = uv("eatery", nm)
        mb.quad(w.p(u, 0.06, z), (wd, wd / r[4]), sign, r, rz=w.rot)
    # the east wall: the cooler (glowing with the room), the water dispenser, the drinks sign, a bin, the TV
    e = room_walls()["east"]
    cool = lit("eat.cooler", "#eaf4ff", L, 1.0)
    body = "#e8e8e8"
    mb.box(e.p(3.9, 0.03, F0 + 0.95), (0.7, 0.06, 1.9), plast, e.rot, body)  # an open box: back, sides, top, kick
    for du in (-0.34, 0.34):
        mb.box(e.p(3.9 + du, 0.33, F0 + 0.95), (0.02, 0.62, 1.9), plast, e.rot, body)
    mb.box(e.p(3.9, 0.33, F0 + 1.82), (0.7, 0.62, 0.16), plast, e.rot, body)
    mb.box(e.p(3.9, 0.33, F0 + 0.09), (0.7, 0.62, 0.18), plast, e.rot, "#3a3a3a")
    mb.box(e.p(3.9, 0.065, F0 + 1.0), (0.64, 0.01, 1.55), cool, e.rot)
    for sh in range(5):
        z = F0 + 0.2 + sh * 0.31
        mb.box(e.p(3.9, 0.33, z), (0.66, 0.55, 0.01), steel, e.rot, "#c8ccd0")
        for d, k in ((d, k) for d in (0.25, 0.45) for k in range(7)):
            c = ("#3d6b3a", "#f4d23c", "#e0913a", "#9fc8d8", "#f2efe6")[(k + sh + int(d * 10)) % 5]
            mb.cyl(e.p(3.66 + k * 0.08, d, z + 0.105), 0.028, 0.2, plast, c, n=8)
            mb.cyl(e.p(3.66 + k * 0.08, d, z + 0.225), 0.012, 0.04, plast, "#2b2f36", n=6)
    mb.box(e.p(3.9, 0.635, F0 + 1.0), (0.66, 0.012, 1.62), pm("coolglass", "#dfeaf2", 0.05, alpha=0.12), e.rot)
    mb.box(e.p(4.2, 0.66, F0 + 1.0), (0.025, 0.03, 0.5), steel, e.rot, "#c8ccd0")  # the handle
    mb.box(e.p(3.0, 0.2, F0 + 0.48), (0.32, 0.32, 0.96), plast, e.rot, "#f2efe6")
    mb.cyl(e.p(3.0, 0.2, F0 + 1.18), 0.14, 0.42, pm("bottle", "#a8cce8", 0.1, alpha=0.6), n=16)
    mb.cyl(e.p(5.0, 0.25, F0 + 0.3), 0.2, 0.6, plast, "#4b4f3a", r2=0.22)
    for nm, u, z, wd in (("drinks", 3.9, 2.55, 0.42), ("bus", 5.0, 1.55, 0.44)):
        r = uv("eatery", nm)
        mb.quad(e.p(u, 0.045, z), (wd, wd / r[4]), sign, r, rz=e.rot)
    tv = kp("int.eat.tv", "Television_01", e.p(1.7, 0.45, 2.85), e.rot, 0.8, R)
    tv.rotation_euler.x = 0.0
    mb.box(e.p(1.7, 0.25, 2.8), (0.4, 0.5, 0.03), steel, e.rot, "#3a3a3a")
    mb.box(e.p(1.7, 0.03, 2.75), (0.25, 0.04, 0.25), steel, e.rot, "#3a3a3a")
    tvm = amat("eatery", 0.3, L, 2.5)
    r = uv("eatery", "tv")
    mb.quad(e.p(1.7 + 0.04, 0.45 + 0.19, 2.85 + 0.2), (0.3, 0.24), tvm, r, rz=e.rot)
    # the ceiling: two fans, a paper star garland across the room, a parol in the window
    for k, y in enumerate((-2.0, -4.3)):
        f = kp(f"int.eat.fan{k}", "ceiling_fan", (0.2, y, 4.2 - 0.52), k * 0.6, 1.0, R)
    stars = ("#f4d23c", "#2a4d8f", "#f2efe6", "#3d6b3a", "#9fc8d8", "#e6d4ec")
    for a, b in (((-2.85, -0.6, 3.75), (2.85, -5.8, 3.65)), ((-2.85, -5.8, 3.7), (2.85, -0.6, 3.75))):
        a, b = Vector(a), Vector(b)
        pts = []
        for k in range(23):
            t = k / 22
            p = a.lerp(b, t) - Vector((0, 0, 0.45 * 4 * t * (1 - t)))
            pts.append(tuple(p))
            if 0 < k < 22:
                mb.add(star_vf(0.075, 0.032, 0.004), plast, mtx(p - Vector((0, 0, 0.08)), rng.uniform(0, 3)),
                       stars[k % len(stars)])
        mb.tube(pts, 0.002, plast, "#e8e2cf", n=4)
    px, pz = 0.55, 2.55  # the parol: a star lantern, paper on bamboo, with its tails
    mb.add(star_vf(0.32, 0.14, 0.08), plast, mtx((px, -0.35, pz), math.pi), "#f4d23c")
    mb.add(star_vf(0.2, 0.09, 0.09), plast, mtx((px, -0.35, pz), math.pi), "#f2efe6")
    for k in range(2):
        mb.box((px - 0.08 + k * 0.16, -0.35, pz - 0.55), (0.03, 0.005, 0.5), plast, 0, ("#2a4d8f", "#f4d23c")[k])
    mb.cyl((px, -0.35, pz + 0.95), 0.002, 1.0, plast, "#e8e2cf", n=4)
    # crates stacked in the back west corner
    for k in range(3):
        kp(f"int.eat.crate{k}", "plastic_crate_02", (-2.55 + rng.uniform(-0.03, 0.03), -5.8, F0 + k * 0.255),
           rng.uniform(-0.08, 0.08), 1.0, R)
    mb.done(R)


# ---------------------------------------------------------------- the pawn shop (shop 4)

def pawn(S):
    i = 4
    R, L = shop_root(i), shop_light(S, i)
    rng = random.Random(SEED + 104)
    mb = MB("int.pawn")
    paint(mb, "#9aa0a0", "pawn", grime=0.5)
    fixtures(mb, L, (-1.2, 1.4), (-2.0, -4.4), warm="#f6f7ff", k=6.0)
    wood, metal, plast = vc("pwood", 0.55), vc("pmetal", 0.35, 0.7), vc("pplast", 0.45)
    gold, velvet = pm("gold", "#e2b63b", 0.12, 1.0), pm("velvet", "#1b2238", 0.9)
    silver = pm("silver", "#d8dce0", 0.15, 1.0)
    glass = pm("pglass", "#d8e6ee", 0.03, alpha=0.15)
    caselit = lit("pawn.case", "#fff4e0", L, 12.0)
    _ = uv("shops", "s4_0")
    sign = amat("shops", 0.8)

    def case(cx, cy, length, rz):
        """A jewellery case: a dark wood base, a velvet bed of gold under glass."""
        M = mtx((cx, cy, 0), rz)
        mb.add((box_v((length, 0.6, 0.85)), BOX_F), wood, M @ Matrix.Translation((0, 0, F0 + 0.425)), "#2a2018")
        mb.add((box_v((length - 0.04, 0.56, 0.02)), BOX_F), velvet, M @ Matrix.Translation((0, 0, F0 + 0.86)))
        mb.add((box_v((length - 0.06, 0.02, 0.012)), BOX_F), caselit, M @ Matrix.Translation((0, 0.27, F0 + 1.13)))
        mb.add((box_v((length, 0.6, 0.28)), BOX_F), glass, M @ Matrix.Translation((0, 0, F0 + 1.0)))
        for a, b in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            mb.add((box_v((0.02, 0.02, 0.28)), BOX_F), metal, M @ Matrix.Translation((a * length / 2, b * 0.3, F0 + 1.0)),
                   "#c8ccd0")
        n = int(length / 0.09)
        for k in range(n):  # rings, chains, watches
            u = -length / 2 + 0.06 + k * (length - 0.12) / max(1, n - 1)
            for row in (-0.15, 0.0, 0.15):
                p = M @ Vector((u + rng.uniform(-0.01, 0.01), row, F0 + 0.885))
                kind = rng.random()
                mm = gold if kind < 0.7 else silver
                if kind < 0.35:
                    mb.add(torus_vf(0.02, 0.005, 12, 5), mm, mtx(p + Vector((0, 0, 0.02)), rng.uniform(0, 3), 1.2), smooth=True)
                elif kind < 0.6:
                    for j in range(9):
                        mb.add(torus_vf(0.008, 0.0022, 6, 3), mm, mtx(p + Vector((j * 0.011 - 0.04, 0, 0.003)), 0, (j % 2) * 1.5))
                else:
                    mb.cyl(tuple(p + Vector((0, 0, 0.006))), 0.022, 0.01, mm, n=14)
                    mb.box(tuple(p + Vector((0, 0.03, 0.002))), (0.014, 0.05, 0.003), velvet if kind > 0.8 else mm, rz)
    case(-0.6, -3.6, 3.4, 0.0)
    case(-2.5, -2.0, 1.8, math.pi / 2)
    mb.box((1.7, -3.6, F0 + 0.5), (1.4, 0.6, 1.0), wood, 0.0, "#3a2e24")
    kp("int.pawn.till", "CashRegister_01", (1.6, -3.7, F0 + 1.0), 0.0, 0.8, R)
    # the back wall: guitars, a shelf of TVs and electronics
    for k in range(5):
        x = -2.45 + k * 0.48
        kp(f"int.pawn.guitar{k}", "Ukulele_01", (x, -6.05, 1.55 + (k % 2) * 0.12), math.pi, 2.0, R,
           rot=(0, 0.08 * (k - 2), math.pi))
        mb.box((x, -6.08, 2.68 + (k % 2) * 0.12), (0.03, 0.06, 0.03), metal, 0, "#303030")
    levels = [F0 + z for z in (0.45, 1.05, 1.65, 2.25)]
    bw = room_walls()["back"]
    shelving(mb, bw, 3.4, 5.75, levels, 0.5, wood, "#4a3a2c", back="#3a2e24")
    for k in range(2):
        kp(f"int.pawn.tv{k}", "Television_01", bw.p(3.9 + k * 0.7, 0.26, levels[0]), bw.rot + rng.uniform(-0.1, 0.1), 0.8, R)
    kp("int.pawn.tv2", "Television_01", bw.p(4.3, 0.26, levels[2]), bw.rot, 0.65, R)
    kp("int.pawn.boom", "boombox", bw.p(4.0, 0.25, levels[1]), bw.rot, 0.7, R)
    kp("int.pawn.cam", "Camera_01", bw.p(5.2, 0.25, levels[1]), bw.rot + 0.4, 1.0, R)
    kp("int.pawn.vcam", "vintage_video_camera", bw.p(4.9, 0.25, levels[1]), bw.rot - 0.5, 1.2, R)
    kp("int.pawn.mantel", "mantel_clock_01", bw.p(5.3, 0.25, levels[2]), bw.rot, 1.0, R)
    kp("int.pawn.alarm", "alarm_clock_01", bw.p(3.7, 0.25, levels[3]), bw.rot, 1.0, R)
    kp("int.pawn.alarm2", "alarm_clock_01", bw.p(5.0, 0.25, levels[3]), bw.rot + 0.4, 0.9, R)
    kp("int.pawn.toolbox", "metal_toolbox", bw.p(4.4, 0.25, levels[3]), bw.rot, 0.9, R)
    # the east wall: tools hung on a board, a hand truck; tags on everything
    e = room_walls()["east"]
    mb.box(e.p(4.6, 0.045, 1.8), (1.4, 0.02, 1.1), wood, e.rot, "#7a6040")
    for k, (aid, u, z) in enumerate((("handsaw_wood", 4.3, 2.0), ("wooden_hammer_01", 4.95, 1.55),
                                     ("wooden_hammer_01", 5.15, 1.6), ("handsaw_wood", 4.3, 1.6))):
        kp(f"int.pawn.tool{k}", aid, e.p(u, 0.05, z), e.rot + (math.pi / 2 if aid == "handsaw_wood" else 0), 1.0, R)
    kp("int.pawn.truck", "hand_truck", e.p(2.8, 0.35, F0), e.rot + 0.3, 0.9, R)
    kp("int.pawn.bike_tyre", "old_tyre", e.p(3.6, 0.1, F0), e.rot, 0.95, R)
    # bars inside the window
    bars = vc("bars", 0.5, 0.6)
    for k in range(32):
        mb.box((-2.65 + k * 0.12, -0.16, 1.85), (0.018, 0.018, 2.5), bars, 0, "#1a1a1a")
    for z in (0.7, 1.85, 3.0):
        mb.box((-0.8, -0.16, z), (3.8, 0.012, 0.05), bars, 0, "#1a1a1a")
    window_signs(mb, i, amat("shops", 0.8, L, 0.6), (-2.1, -0.75, 0.55), z=2.3)
    mb.box((-0.8, -0.45, 0.62), (3.4, 0.5, 0.05), wood, 0, "#2a2018")  # the window: a guitar, a clock, a camera
    kp("int.pawn.wguitar", "Ukulele_01", (-2.2, -0.5, 0.64), math.pi, 1.9, R, rot=(-0.25, 0, math.pi))
    kp("int.pawn.wclock", "mantel_clock_01", (-1.0, -0.45, 0.645), math.pi, 1.2, R)
    kp("int.pawn.wcam", "Camera_01", (-0.2, -0.45, 0.645), math.pi + 0.5, 1.1, R)
    kp("int.pawn.wboom", "boombox", (0.6, -0.5, 0.645), math.pi, 0.75, R)
    mb.done(R)


# ---------------------------------------------------------------- the other shops

YARN = ["#6a4c93", "#2f7f7a", "#d9b43c", "#3d6b3a", "#9fc8d8", "#e6d4ec", "#f2efe6", "#e0913a", "#2a4d8f", "#8a6d5a",
        "#c9ccd1", "#5e3b5c", "#a8d8a0"]
BOOKS = ["#4a2f1c", "#2a4d8f", "#3d6b3a", "#6a4c93", "#8a6d5a", "#2b2f36", "#d9b43c", "#5e3b5c", "#c9b88a", "#1f4f4a"]


def stock_shelf(mb, rng, w, u0, u1, z, D, kind, m, R=None, tag=""):
    """One shelf of themed stock along a wall frame."""
    u = u0 + 0.03
    while u < u1 - 0.05:
        if kind == "yarn":
            s = rng.uniform(0.055, 0.07)
            for row in range(2):
                mb.blob(w.p(u + s, D * (0.3 + 0.35 * row), z + s * 0.9), (s, s, s * 0.9), m, rng.choice(YARN), rng)
            u += s * 2.05
        elif kind == "books":
            t, h = rng.uniform(0.025, 0.06), rng.uniform(0.2, 0.3)
            mb.box(w.p(u + t / 2, D * 0.45, z + h / 2), (t, D * 0.8, h), m, w.rot, rng.choice(BOOKS))
            u += t + 0.003
            if rng.random() < 0.04:
                u += 0.12
        elif kind == "loaves":
            s = rng.uniform(0.09, 0.12)
            c = rng.choice(("#b8783a", "#a8682c", "#c88a40", "#8a5428", "#d8a860"))
            if rng.random() < 0.35:  # a batard
                mb.blob(w.p(u + 0.14, D * 0.5, z + 0.05), (0.15, 0.07, 0.055), m, c, rng, rz=w.rot + math.pi / 2)
                u += 0.3
            else:
                mb.blob(w.p(u + s, D * 0.5, z + s * 0.6), (s, s, s * 0.65), m, c, rng)
                u += s * 2.1
        elif kind == "jars":
            r, h = rng.uniform(0.04, 0.06), rng.uniform(0.12, 0.2)
            mb.cyl(w.p(u + r, D * 0.5, z + h / 2), r, h, m, rng.choice(("#d8c8a0", "#8a5428", "#e6c46a", "#3d6b3a",
                                                                        "#f2efe6", "#c9ccd1")), n=12)
            mb.cyl(w.p(u + r, D * 0.5, z + h + 0.012), r * 0.95, 0.024, m, "#c8ccd0", n=12)
            u += r * 2 + 0.02
        elif kind == "bags":  # coffee beans in kraft bags
            mb.box(w.p(u + 0.07, D * 0.5, z + 0.11), (0.13, 0.08, 0.22), m, w.rot, rng.choice(("#b89a6a", "#2b2f36",
                                                                                              "#c9b88a", "#3d6b3a")))
            u += 0.16
        elif kind == "mugs":
            mb.cyl(w.p(u + 0.05, D * 0.5, z + 0.05), 0.045, 0.1, m, rng.choice(("#f2efe6", "#2a4d8f", "#2f7f7a", "#d9b43c")),
                   n=12)
            u += 0.12
        elif kind == "shoes":  # a running shoe on an angled shelf
            c = rng.choice(("#2a4d8f", "#f2efe6", "#3d6b3a", "#6a4c93", "#2b2f36", "#9fc8d8", "#d9b43c"))
            p = w.p(u + 0.1, D * 0.5, z + 0.05)
            mb.box(p, (0.1, 0.28, 0.07), m, w.rot + math.pi / 2, c)
            mb.box((p[0], p[1], p[2] - 0.04), (0.1, 0.29, 0.025), m, w.rot + math.pi / 2, "#f2efe6")
            u += 0.32
        elif kind == "plants":
            p = w.p(u + 0.1, D * 0.5, z)
            r_ = rng.uniform(0.06, 0.09)
            mb.cyl((p[0], p[1], z + r_), r_ * 0.8, r_ * 1.6, m, rng.choice(("#b86a3a", "#a85a30", "#f2efe6", "#2b2f36")),
                   n=10, r2=r_)
            if rng.random() < 0.3:  # a succulent: a rosette of fat leaves
                for j in range(7):
                    a = j * 0.9
                    mb.blob((p[0] + 0.035 * math.cos(a), p[1] + 0.035 * math.sin(a), z + r_ * 2.1 + 0.03), (0.022, 0.05, 0.016),
                            m, "#6a9a6a", rng, rz=a, rx=0.6)
            else:
                for j in range(rng.randint(4, 7)):
                    a = rng.uniform(0, 6.3)
                    mb.blob((p[0] + 0.05 * math.cos(a), p[1] + 0.05 * math.sin(a), z + r_ * 2.2 + rng.uniform(0, 0.14)),
                            (0.05, 0.05, rng.uniform(0.06, 0.13)), m,
                            rng.choice(("#4f8a3a", "#3d7a32", "#6a9a48", "#7aa850")), rng, rx=rng.uniform(-0.5, 0.5))
            u += 0.24
        elif kind == "games":
            k = rng.randrange(12)
            for d in range(3):  # face out, three deep
                mb.box(w.p(u + 0.16, D * 0.8 - d * 0.08, z + 0.113), (0.3, 0.07, 0.225), m,
                       w.rot + rng.uniform(-0.04, 0.04), rect=uv("shops", f"game{(k + d * 5) % 12}"))
            u += 0.33
        elif kind == "seeds":
            for row in range(3):
                mb.box(w.p(u + 0.04, 0.03 + row * 0.005, z + 0.06 + row * 0.12), (0.075, 0.004, 0.11), m, w.rot,
                       rng.choice(("#3d6b3a", "#d9b43c", "#e0913a", "#6a4c93", "#f2efe6", "#9fc8d8")))
            u += 0.09
        else:
            u += 1.0


def stocked_wall(mb, rng, w, u0, u1, levels, D, kind, wood, m, woodcol="#7a5a3a", back=None, R=None, tag=""):
    shelving(mb, w, u0, u1, levels, D, wood, woodcol, back)
    for z in levels[:-1] if kind != "plants" else levels:
        stock_shelf(mb, rng, w, u0, u1, z, D, kind, m, R, tag)


def shop(S, i, kind):
    R, L = shop_root(i), shop_light(S, i)
    rng = random.Random(SEED + 200 + i)
    W = room_walls()
    back, west, east = W["back"], W["west"], W["east"]
    mb = MB(f"int.shop{i}")
    _ = uv("shops", "map")
    sign = amat("shops", 0.8)
    games = amat("shops", 0.5)
    wood, m, soft = vc("swood", 0.65), vc("stock", 0.55), vc("soft", 0.9)
    metal = vc("smetal", 0.35, 0.7)
    lv5 = [F0 + z for z in (0.35, 0.8, 1.25, 1.7, 2.15)]
    tag = f"s{i}"
    if kind == "cooking":
        paint(mb, "#d8cfb8", tag)
        stocked_wall(mb, rng, back, 0.2, 5.6, lv5, 0.4, "jars", wood, m)
        stocked_wall(mb, rng, west, 1.4, 5.6, lv5, 0.35, "jars", wood, m)
        mb.box((0, -3.0, 3.3), (2.0, 0.05, 0.05), metal, 0, "#303030")  # the pot rack
        for k in range(6):
            mb.cyl((-0.8 + k * 0.32, -3.0, 3.6), 0.004, 0.6, metal, "#303030", n=4)
            kp(f"int.{tag}.pan{k}", "brass_pan_01", (-0.8 + k * 0.32, -3.0, 3.25), 0, 1.0, R,
               rot=(math.pi / 2, 0, math.pi / 2 + rng.uniform(-0.2, 0.2)))
        mb.box((1.3, -4.3, F0 + 0.45), (2.2, 0.8, 0.9), wood, 0, "#6a4a30")
        for k in range(3):
            kp(f"int.{tag}.board{k}", "wooden_cutting_board", (0.6 + k * 0.6, -4.3, F0 + 0.9 + k * 0.0), k * 0.3, 1.0, R)
        mb.box((2.85, -3.0, 1.6), (0.02, 0.6, 0.05), metal, 0, "#303030")  # the knife strip
        for k in range(6):
            mb.box((2.83, -3.25 + k * 0.1, 1.48), (0.008, 0.035, 0.26), metal, 0, "#c8ccd0")
        for k in range(4):  # the window: cast iron and copper
            mb.cyl((-2.2 + k * 0.85, -0.45, 0.66), 0.14, 0.04, metal, "#202020", n=20)
            mb.box((-2.2 + k * 0.85, -0.29, 0.67), (0.03, 0.18, 0.02), metal, 0, "#202020")
        kp(f"int.{tag}.wpan", "brass_pan_01", (-1.75, -0.5, 0.64), 0.4, 1.3, R)
    elif kind == "sourdough":
        paint(mb, "#e8dcc0", tag)
        for w, a, b in ((back, 0.3, 5.5), (west, 1.4, 5.6)):
            shelving(mb, w, a, b, lv5, 0.45, wood, "#8a6a4a", back="#6a4a30")
            for z in lv5[:-1]:
                stock_shelf(mb, rng, w, a, b, z, 0.45, "loaves", m)
        for k in range(4):
            kp(f"int.{tag}.basket{k}", "wicker_basket_01", back.p(0.9 + k * 1.3, 0.25, lv5[-1]), 0.0, 1.2, R)
        mb.box((1.3, -4.2, F0 + 0.5), (2.4, 0.7, 1.0), wood, 0, "#6a4a30")  # the counter with a glass case
        mb.box((1.3, -4.2, F0 + 1.13), (2.3, 0.6, 0.26), pm("bglass", "#d8e6ee", 0.03, alpha=0.15))
        for k in range(8):
            kp(f"int.{tag}.cr{k}", "croissant", (0.4 + k * 0.26, -4.15, F0 + 1.01), rng.uniform(-0.3, 0.3), 1.0, R)
        for k in range(3):  # flour sacks
            mb.blob((-1.6 + k * 0.5, -5.3, F0 + 0.28), (0.22, 0.17, 0.3), soft, "#ece4d0", rng)
        for k in range(3):  # the window: loaves in baskets
            kp(f"int.{tag}.wb{k}", "wicker_basket_01", (-2.1 + k * 1.05, -0.45, 0.64), 0.0, 1.3, R)
            for j in range(3):
                mb.blob((-2.2 + k * 1.05 + j * 0.1, -0.45, 0.76), (0.07, 0.07, 0.05), m, "#b8783a", rng)
        kp(f"int.{tag}.buns", "hamburger_buns", (0.9, -0.45, 0.64), 0.0, 1.3, R)
        mb.box((-0.8, -0.45, 0.62), (3.6, 0.5, 0.05), wood, 0, "#6a4a30")
    elif kind == "running":
        paint(mb, "#cfd8d0", tag)
        levels = [F0 + 0.3 + k * 0.38 for k in range(6)]
        for w, a, b in ((back, 0.2, 5.6), (west, 1.4, 5.6)):
            for z in levels:
                mb.box(w.p((a + b) / 2, 0.15, z - 0.01), (b - a, 0.3, 0.02), wood, w.rot, "#e8e8e8")
                stock_shelf(mb, rng, w, a, b, z, 0.3, "shoes", m)
        mb.box((0.5, -3.3, 1.45), (1.6, 0.03, 0.03), metal, 0, "#c8ccd0")  # a rack of shirts
        for k in range(12):
            mb.box((-0.2 + k * 0.125, -3.3, 1.1), (0.02, 0.5, 0.65), soft, 0,
                   rng.choice(("#2a4d8f", "#3d6b3a", "#f4d23c", "#2f7f7a", "#f2efe6", "#6a4c93")))
        for dx in (-0.3, 1.3):
            mb.box((dx, -3.3, F0 + 0.65), (0.03, 0.03, 1.3), metal, 0, "#c8ccd0")
        kp(f"int.{tag}.boots", "rubber_boots", (-1.3, -0.45, 0.64), math.pi, 0.9, R)
        mb.box((-0.8, -0.45, 0.62), (3.6, 0.5, 0.05), wood, 0, "#e8e8e8")
        for k in range(4):  # the window: shoes on risers
            mb.box((0.0 + k * 0.28, -0.45, 0.7 + (k % 2) * 0.08), (0.1, 0.28, 0.07), m, 0.3,
                   ("#2a4d8f", "#f2efe6", "#3d6b3a", "#6a4c93")[k])
        mb.box((1.3, -4.6, F0 + 0.48), (1.6, 0.6, 0.96), wood, 0, "#5a5d63")
        for k in range(6):  # race bibs pinned on the east wall
            mb.box(east.p(1.5 + k * 0.5, 0.045, 2.4 + (k % 2) * 0.3), (0.3, 0.004, 0.22), m, east.rot, "#f2efe6")
            mb.box(east.p(1.5 + k * 0.5, 0.049, 2.42 + (k % 2) * 0.3), (0.2, 0.004, 0.08), m, east.rot, "#2a4d8f")
    elif kind in ("knitting", "crochet"):
        paint(mb, "#e6d8d0" if kind == "knitting" else "#e0e6d8", tag)
        for k in range(4):
            kp(f"int.{tag}.cub{k}", "wooden_display_shelves_01", back.p(0.7 + k * 1.15, 0.2, F0), back.rot + math.pi / 2, 1.0, R)
            for z in (0.05, 0.41, 0.79, 1.16):
                for j in range(3):
                    for q in range(3):
                        mb.blob(back.p(0.32 + k * 1.15 + j * 0.37 + q * 0.06, 0.16, F0 + z + 0.07 + q * 0.03),
                                (0.06, 0.06, 0.055), m, YARN[(k * 3 + j + int(z * 10)) % len(YARN)], rng)
        stocked_wall(mb, rng, west, 1.4, 5.6, lv5, 0.35, "yarn", wood, m)
        if kind == "knitting":
            kp(f"int.{tag}.wheel", "spinning_wheel_01", (-1.8, -0.7, F0), math.pi / 2, 1.0, R)
        else:  # granny-square blankets on the east wall; amigurumi in the window
            for b in range(2):
                for gx in range(6):
                    for gy in range(6):
                        mb.box(east.p(1.6 + b * 2.0 + gx * 0.2, 0.045, 1.4 + gy * 0.2), (0.19, 0.006, 0.19), soft, east.rot,
                               YARN[(gx * 7 + gy * 3 + b) % len(YARN)])
            for k in range(7):
                p = (-2.3 + k * 0.45, -0.45, 0.72)
                c = YARN[(k * 5) % len(YARN)]
                mb.blob(p, (0.07, 0.07, 0.08), soft, c, rng)
                mb.blob((p[0], p[1], p[2] + 0.12), (0.06, 0.06, 0.055), soft, c, rng)
            mb.box((-0.8, -0.45, 0.62), (3.6, 0.5, 0.05), wood, 0, "#8a6a4a")
        for k in range(3):
            kp(f"int.{tag}.bk{k}", "wicker_basket_02", (-0.2 + k * 0.45, -2.6 + (k % 2) * 0.3, F0), k, 1.2, R)
            for j in range(3):
                mb.blob((-0.2 + k * 0.45 + j * 0.05, -2.6 + (k % 2) * 0.3, F0 + 0.2), (0.06, 0.06, 0.06), m,
                        YARN[(k + j * 4) % len(YARN)], rng)
        mb.box((1.2, -4.0, F0 + 0.38), (1.4, 0.8, 0.04), wood, 0, "#7a5a3a")  # the stitch-night table
        for dx in (-0.6, 0.6):
            for dy in (-0.35, 0.35):
                mb.box((1.2 + dx, -4.0 + dy, F0 + 0.18), (0.04, 0.04, 0.36), wood, 0, "#5a4030")
        for k in range(3):
            kp(f"int.{tag}.ch{k}", "plastic_monobloc_chair_01", (0.7 + k * 0.5, -4.7, F0), math.pi + rng.uniform(-0.2, 0.2), 0.9, R)
    elif kind in ("gardening", "houseplants"):
        paint(mb, "#d8e0c8" if kind == "gardening" else "#e8e4d4", tag)
        leaf = ("#4f8a3a", "#3d7a32", "#6a9a48", "#2f6b2a", "#7aa850")
        for t in range(3):  # a tiered bench of potted starts along the back wall
            y, z = -5.85 + t * 0.32, F0 + 0.9 - t * 0.3
            mb.box((-0.9, y, z - 0.02), (3.6, 0.3, 0.04), wood, 0, "#8a6a4a")
            mb.box((-0.9, y + 0.14, (F0 + z) / 2), (3.6, 0.02, z - F0), wood, 0, "#6a4a30")
            for k in range(14):
                x = -2.6 + k * 0.25 + rng.uniform(-0.03, 0.03)
                r_ = rng.uniform(0.06, 0.09)
                mb.cyl((x, y, z + r_), r_ * 0.8, r_ * 1.6, m, rng.choice(("#b86a3a", "#a85a30", "#2b2f36", "#f2efe6")),
                       n=10, r2=r_)
                for j in range(rng.randint(3, 6)):
                    a = rng.uniform(0, 6.3)
                    mb.blob((x + 0.05 * math.cos(a), y + 0.05 * math.sin(a), z + r_ * 2.2 + rng.uniform(0, 0.12)),
                            (0.05, 0.05, rng.uniform(0.06, 0.12)), m, rng.choice(leaf), rng, rx=rng.uniform(-0.5, 0.5))
        kp(f"int.{tag}.big", "potted_plant_02", (-2.3, -3.0, F0), rng.uniform(0, 6), 1.2, R)
        for k in range(4):  # hanging baskets
            x = -2.2 + k * 1.2
            mb.cyl((x, -1.5, 3.55), 0.003, 1.3, m, "#e8e2cf", n=4)
            mb.cyl((x, -1.5, 2.8), 0.15, 0.18, m, "#8a6a40" if kind == "gardening" else "#f2efe6", n=14, r2=0.18)
            for j in range(10):
                a = j * 0.63
                mb.blob((x + 0.16 * math.cos(a), -1.5 + 0.16 * math.sin(a), 2.82 - (j % 4) * 0.08), (0.07, 0.07, 0.14), m,
                        leaf[(j + k) % len(leaf)], rng)
        kp(f"int.{tag}.tall", "potted_plant_02", (2.1, -5.5, F0), rng.uniform(0, 6), 1.5, R)
        stocked_wall(mb, rng, west, 1.2, 5.6, [F0 + 0.5, F0 + 1.05, F0 + 1.6], 0.45, "plants", wood, m, "#8a6a4a", R=R, tag=tag)
        if kind == "gardening":
            for k in range(2):
                kp(f"int.{tag}.planter{k}", "planter_box_01", (-1.6 + k * 1.3, -0.5, F0), math.pi, 1.0, R)
            for k in range(3):
                kp(f"int.{tag}.can{k}", "watering_can_metal_01", (0.6 + k * 0.3, -0.5, F0), 0.4 * k, 1.0, R)
            for k in range(5):  # sacks of soil
                mb.blob((1.6 + (k % 3) * 0.4, -2.2 - (k // 3) * 0.5, F0 + 0.14 + (k // 3) * 0.1), (0.2, 0.3, 0.12), soft,
                        ("#3a2a1c", "#3d6b3a")[k % 2], rng)
            mb.box((2.75, -3.6, 1.2), (0.2, 1.0, 1.4), metal, 0, "#c8ccd0")  # the seed rack
            stock_shelf(mb, rng, Wall((2.65, -3.1), (0, -1), (-1, 0)), 0.0, 1.0, 0.6, 0.0, "seeds", m)
            stock_shelf(mb, rng, Wall((2.65, -3.1), (0, -1), (-1, 0)), 0.0, 1.0, 1.1, 0.0, "seeds", m)
            for k in range(2):  # spades by the counter
                kp(f"int.{tag}.spade{k}", "rusted_spade_01", (2.75, -4.9 + k * 0.2, F0), math.pi / 2, 1.0, R, rot=(0, -0.2, math.pi / 2))
            for k in range(4):  # terracotta pots, stacked
                mb.cyl((2.3, -1.6, F0 + 0.1 + k * 0.08), 0.12, 0.18, m, "#b86a3a", n=14, r2=0.15)
        else:
            for k in range(5):  # the window: full of plants
                kp(f"int.{tag}.w{k}", "potted_plant_04", (-2.3 + k * 0.6, -0.45, 0.64), k, 1.3, R, target=1500)
            mb.box((-0.8, -0.45, 0.62), (3.6, 0.5, 0.05), wood, 0, "#8a6a4a")
            stock_shelf(mb, rng, Wall((-2.7, -2.0), (1, 0), (0, -1)), 0.0, 3.0, F0, 0.4, "plants", m)  # pots on the floor
        mb.box((1.3, -4.3, F0 + 0.45), (1.6, 0.6, 0.9), wood, 0, "#6a4a30")
    elif kind == "woodworking":
        paint(mb, "#d0c8b8", tag)
        mb.box((-0.6, -4.8, F0 + 0.85), (2.6, 0.8, 0.1), wood, 0, "#b08a57")  # the workbench
        for dx in (-1.2, 0.0, 1.2):
            for dy in (-0.32, 0.32):
                mb.box((-0.6 + dx, -4.8 + dy, F0 + 0.4), (0.08, 0.08, 0.8), wood, 0, "#8a6a40")
        mb.box((-0.6, -4.8, F0 + 0.2), (2.4, 0.7, 0.03), wood, 0, "#8a6a40")
        kp(f"int.{tag}.plane", "hand_plane_no4", (-1.3, -4.7, F0 + 0.9), 0.3, 1.0, R)
        kp(f"int.{tag}.hammer", "wooden_hammer_01", (-0.4, -4.6, F0 + 0.91), 0, 1.0, R, rot=(math.pi / 2, 0, 0.6))
        kp(f"int.{tag}.saw", "handsaw_wood", (0.3, -4.8, F0 + 0.91), 0.2, 1.0, R, rot=(0, math.pi / 2, 0.2))
        mb.box((-0.6, -6.06, 2.0), (2.6, 0.02, 1.1), wood, 0, "#9a7a52")  # the tool board
        for k in range(8):
            mb.box((-1.7 + k * 0.3, -6.03, 2.0 + (k % 3) * 0.1), (0.04, 0.03, 0.4 + (k % 3) * 0.1), metal, 0,
                   rng.choice(("#303030", "#8a6a40", "#c8ccd0")))
        for k in range(10):  # the lumber rack on the west wall
            z = 0.6 + (k % 5) * 0.4
            mb.box((-2.7 + (k // 5) * 0.12, -3.3, z), (0.1, 4.2, 0.05 + (k % 3) * 0.02), wood, 0,
                   rng.choice(("#c8a070", "#b08a57", "#8a5a30", "#d8b888")))
        for k in range(3):
            mb.box((-2.75, -1.6 - k * 1.6, 1.4), (0.08, 0.06, 2.4), metal, 0, "#303030")
        for k in range(2):  # sawhorses
            for s in (-1, 1):
                mb.box((0.6 + k * 1.2, -2.6 + s * 0.12, F0 + 0.35), (0.05, 0.05, 0.75), wood, 0, "#b08a57", rx=s * 0.3)
            mb.box((0.6 + k * 1.2, -2.6, F0 + 0.71), (0.8, 0.08, 0.06), wood, 0, "#b08a57")
        mb.box((1.2, -2.6, F0 + 0.76), (1.8, 0.4, 0.03), wood, 0, "#c8a070")
        mb.box((1.4, -3.9, F0 + 0.45), (0.7, 0.7, 0.9), metal, 0, "#4b5560")  # the table saw
        mb.box((1.4, -3.9, F0 + 0.92), (1.0, 0.8, 0.04), metal, 0, "#b8bcc0")
        mb.cyl((1.4, -3.9, F0 + 0.96), 0.12, 0.004, metal, "#d8dce0", n=20, rx=math.pi / 2, rz=math.pi / 2)
        shelving(mb, east, 0.3, 2.2, [F0 + 0.4, F0 + 0.9, F0 + 1.4, F0 + 1.9], 0.35, wood, "#8a6a40")
        for z in (F0 + 0.4, F0 + 0.9, F0 + 1.4):  # what they made: bowls, boxes, a few stools
            for k in range(4):
                p = east.p(0.55 + k * 0.45, 0.17, z)
                if (k + int(z * 10)) % 2:
                    mb.cyl((p[0], p[1], z + 0.04), 0.12, 0.08, m, rng.choice(("#c8a070", "#8a5a30", "#b08a57")), n=16, r2=0.15)
                else:
                    mb.box((p[0], p[1], z + 0.08), (0.25, 0.2, 0.16), m, east.rot, rng.choice(("#c8a070", "#8a5a30", "#b08a57")))
        for k in range(6):  # clamps on the west lumber rack's end
            mb.box((-2.8, -5.7 + k * 0.08, 2.4), (0.04, 0.03, 0.35), metal, 0, ("#2a4d8f", "#d9b43c")[k % 2])
        mb.box((-0.8, -0.45, 0.62), (3.6, 0.5, 0.05), wood, 0, "#8a6a40")
        for k in range(3):  # the window: a stool and boxes they made
            mb.box((-2.0 + k * 0.9, -0.45, 0.75 + k * 0.05), (0.4, 0.3, 0.2 + k * 0.1), wood, 0,
                   ("#c8a070", "#8a5a30", "#b08a57")[k])
        for k in range(30):  # shavings on the floor
            mb.blob((-0.6 + rng.uniform(-1.3, 1.3), -4.2 + rng.uniform(-0.3, 0.4), F0 + 0.01), (0.03, 0.02, 0.008), m,
                    "#d8b888", rng)
    elif kind == "historians":
        paint(mb, "#cfc0a0", tag)
        for w, a, b in ((back, 0.15, 5.65), (west, 1.4, 5.6), (east, 0.15, 3.3)):
            stocked_wall(mb, rng, w, a, b, [F0 + 0.1 + k * 0.38 for k in range(7)], 0.3, "books", wood, m, "#4a3020")
        for k in range(3):
            kp(f"int.{tag}.ency{k}", "book_encyclopedia_set_01", back.p(0.8 + k * 1.9, 0.12, F0 + 0.1 + 6 * 0.38), back.rot,
               1.0, R)
        mb.box((-1.6, -0.6, F0 + 0.5), (0.4, 0.4, 1.0), m, 0, "#e8e4d8")  # the bust on a plinth in the window
        kp(f"int.{tag}.bust", "marble_bust_01", (-1.6, -0.6, F0 + 1.0), math.pi, 1.2, R)
        mb.cyl((0.3, -0.55, 0.85), 0.02, 0.4, metal, "#8a6a40", n=8)  # a globe
        mb.blob((0.3, -0.55, 1.2), (0.17, 0.17, 0.17), m, "#4a7a8a", sub=2)
        mb.box((0.3, -0.55, 0.64), (0.3, 0.3, 0.04), wood, 0, "#4a3020")
        r = uv("shops", "map")
        mb.quad(east.p(4.5, 0.045, 2.1), (1.0, 1.0 / r[4]), sign, r, rz=east.rot)
        mb.box((0.8, -3.2, F0 + 0.75), (1.6, 0.9, 0.05), wood, 0, "#5a3a22")  # the reading table
        for dx in (-0.7, 0.7):
            for dy in (-0.38, 0.38):
                mb.box((0.8 + dx, -3.2 + dy, F0 + 0.37), (0.05, 0.05, 0.74), wood, 0, "#4a3020")
        for k in range(4):
            mb.box((0.4 + k * 0.25, -3.2 + rng.uniform(-0.2, 0.2), F0 + 0.8), (0.18, 0.24, 0.04), m, rng.uniform(-0.4, 0.4),
                   rng.choice(BOOKS))
        mb.box((-0.8, -0.45, 0.62), (1.6, 0.5, 0.05), wood, 0, "#4a3020")
    elif kind == "boardgames":
        paint(mb, "#d8dce8", tag)
        for w, a, b in ((back, 0.15, 5.65), (west, 1.4, 5.6)):
            shelving(mb, w, a, b, [F0 + 0.1 + k * 0.42 for k in range(6)], 0.35, wood, "#6a4a30")
            for k in range(5):
                stock_shelf(mb, rng, w, a, b, F0 + 0.1 + k * 0.42, 0.35, "games", games)
        for k, (x, y) in enumerate(((0.3, -2.6), (1.6, -4.2))):
            mb.box((x, y, F0 + 0.74), (1.2, 0.8, 0.04), wood, 0, "#7a5636")
            for dx in (-0.5, 0.5):
                for dy in (-0.33, 0.33):
                    mb.box((x + dx, y + dy, F0 + 0.36), (0.05, 0.05, 0.72), wood, 0, "#4a3020")
            if k == 0:
                kp(f"int.{tag}.chess", "chess_set", (x - 0.2, y, F0 + 0.76), 0.2, 0.9, R)
            else:
                mb.box((x, y, F0 + 0.77), (0.6, 0.6, 0.01), m, 0.3, "#3d6b3a")
                for j in range(20):
                    mb.cyl((x + rng.uniform(-0.3, 0.3), y + rng.uniform(-0.3, 0.3), F0 + 0.79), 0.015, 0.02, m,
                           rng.choice(YARN), n=8)
            for s in (-1, 1):
                kp(f"int.{tag}.ch{k}{s}", "plastic_monobloc_chair_01", (x, y + s * 0.65, F0), (0 if s > 0 else math.pi), 0.9, R)
        kp(f"int.{tag}.wchess", "chess_set", (-1.6, -0.5, 0.64), 0.4, 0.8, R)
        mb.box((-0.8, -0.45, 0.62), (3.6, 0.5, 0.05), wood, 0, "#6a4a30")
        for k in range(4):
            mb.box((-0.4 + k * 0.4, -0.5, 0.78), (0.3, 0.07, 0.24), games, math.pi + 0.15,
                   rect=uv("shops", f"game{k * 3}"))
    elif kind == "coffee":
        paint(mb, "#d8c8b0", tag)
        kp(f"int.{tag}.cart", "CoffeeCart_01", (-1.2, -4.9, F0), 0.0, 1.0, R)
        stocked_wall(mb, rng, back, 2.9, 5.6, [F0 + 1.2, F0 + 1.6, F0 + 2.0], 0.3, "bags", wood, m)
        stocked_wall(mb, rng, west, 1.4, 3.6, [F0 + 1.2, F0 + 1.6, F0 + 2.0], 0.3, "mugs", wood, m)
        mb.box((1.3, -4.2, F0 + 0.5), (2.0, 0.7, 1.0), wood, 0, "#4a3020")
        mb.box((1.6, -4.25, F0 + 1.2), (0.5, 0.4, 0.4), metal, 0, "#c8ccd0")  # the espresso machine
        mb.box((1.6, -4.03, F0 + 1.1), (0.4, 0.02, 0.06), metal, 0, "#303030")
        kp(f"int.{tag}.tea", "tea_set_01", (-0.5, -2.4, F0 + 0.76), 0.3, 0.8, R)
        mb.cyl((-0.5, -2.4, F0 + 0.74), 0.5, 0.04, wood, "#6a4a30", n=24)
        mb.cyl((-0.5, -2.4, F0 + 0.37), 0.05, 0.72, metal, "#202020", n=8)
        for k in range(4):  # sacks of beans
            mb.blob((-2.3 + (k % 2) * 0.55, -2.2 - (k // 2) * 0.6, F0 + 0.25), (0.25, 0.2, 0.28), soft, "#b89a6a", rng)
        mb.box((-0.8, -0.45, 0.62), (3.6, 0.5, 0.05), wood, 0, "#4a3020")
        for k in range(5):
            mb.cyl((-2.0 + k * 0.5, -0.45, 0.7), 0.045, 0.1, m, ("#f2efe6", "#2a4d8f", "#2f7f7a", "#d9b43c", "#f2efe6")[k])
    else:
        mb.bm.free()
        return
    fixtures(mb, L, (-1.2, 1.4), (-2.0, -4.4), k=5.0)
    window_signs(mb, i, amat("shops", 0.8, L, 0.6), (-2.1, 0.3), z=2.25)
    mb.done(R)


SHOP_KINDS = {2: "cooking", 3: "sourdough", 5: "running", 6: "knitting", 7: "gardening", 8: "woodworking",
              10: "historians", 11: "coffee", 12: "houseplants", 13: "boardgames", 14: "crochet"}


# ---------------------------------------------------------------- the tower lobby

def lobby(S):
    rng = random.Random(SEED + 300)
    hide_prefix("lobby.topiary", "lobby.copy")
    mb = MB("int.lobby")
    _ = uv("lobby", "copy0")
    white = pm("lwhite", "#f2f4f6", 0.12)
    face = vc("rackface", 0.35, 0.6)
    leds = [blink(f"{c}{k}", h, 8.0, p, d, ph) for k, (c, h, p, d, ph) in enumerate(
        (("b", "#3a8cff", 23, 15, 0), ("w", "#e8f4ff", 31, 20, 7), ("g", "#55ff7a", 17, 11, 3), ("b", "#3a8cff", 13, 4, 5),
         ("g", "#55ff7a", 41, 30, 11), ("w", "#e8f4ff", 9, 5, 2)))]
    cable = vc("cable", 0.5)
    # the throne's racks: bezels, server faces with vents and handles, rows of status LEDs, patch cables
    for k in range(3):
        x, h = 8 + k, 2.2 + (0.8 if k == 1 else 0)
        yf = 17.05
        mb.box((x, yf - 0.012, h / 2), (0.9, 0.024, h), face, 0, "#15181c")
        for s in (-1, 1):
            mb.box((x + s * 0.41, yf - 0.03, h / 2), (0.06, 0.03, h - 0.04), face, 0, "#2b3036")
        z = 0.12 if k != 1 else 0.95
        u = 0
        while z < h - 0.12:
            uh = rng.choice((0.044, 0.088, 0.088, 0.132))
            mb.box((x, yf - 0.035, z + uh / 2), (0.76, 0.02, uh - 0.004), face, 0,
                   rng.choice(("#2b3036", "#23272c", "#30353b", "#1c2024")))
            for v in range(int(uh / 0.022)):  # vent slots
                mb.box((x - 0.12, yf - 0.046, z + 0.012 + v * 0.022), (0.36, 0.002, 0.006), face, 0, "#0c0e10")
            for j in range(rng.choice((2, 4, 6, 8))):
                mb.box((x + 0.12 + j * 0.03, yf - 0.047, z + uh / 2), (0.008, 0.004, 0.008), leds[(j + u) % 6])
            mb.box((x - 0.34, yf - 0.05, z + uh / 2), (0.015, 0.02, uh * 0.6), face, 0, "#8a9098")
            if rng.random() < 0.35:  # patch cables looping out of the port panel
                y0 = yf - 0.05
                pts = [(x + 0.32, y0, z + uh / 2), (x + 0.36, y0 - 0.08, z + uh / 2 - 0.1), (x + 0.42, y0 - 0.04, z + uh / 2 - 0.15),
                       (x + 0.44, y0, z + uh / 2 + 0.1)]
                mb.tube(pts, 0.004, cable, rng.choice(("#2a6af0", "#e8e8e8", "#2a6af0", "#3a3f46")), n=5)
            z += uh
            u += 1
        top = h
        for c in range(10):  # loose cables over the top and down the back, a bundle tied at the top edge
            dx = rng.uniform(-0.3, 0.3)
            pts = [(x + dx, 17.1, top), (x + dx * 0.8, 17.3, top + 0.06 + rng.uniform(0, 0.05)),
                   (x + dx * 0.6, 17.75, top + 0.04), (x + dx * 0.6, 18.0, top - 0.15), (x + dx * 0.7, 18.02, 0.3)]
            mb.tube(pts, 0.009, cable, rng.choice(("#1c2024", "#2a6af0", "#3a3f46", "#e8e8e8")), n=6)
    for k in (0, 2):  # cables spill from the tall middle rack's sides onto the side racks: the throne's arms
        sx = -1 if k == 0 else 1
        for c in range(7):
            yy = 17.12 + c * 0.11
            e0 = 9 + sx * 0.46
            pts = [(e0, yy, 2.85 - c * 0.02), (e0 + sx * 0.08, yy, 2.72), (e0 + sx * 0.2, yy, 2.45),
                   (e0 + sx * 0.38, yy, 2.25), (e0 + sx * (0.6 + c * 0.04), yy, 2.23),
                   (e0 + sx * (0.85 + c * 0.03), yy + 0.02, 2.23)]
            mb.tube(pts, 0.011, cable, rng.choice(("#1c2024", "#2a6af0", "#3a3f46", "#2a6af0")), n=6)
    for k in range(3):  # a cable tray along the back of the racks, into the floor
        mb.box((8 + k, 18.05, 1.2), (0.3, 0.06, 2.0 + (0.8 if k == 1 else 0)), face, 0, "#2b3036")
    # the worse copies, on the back wall: a floating white shelf of blank white boxes with a placard
    gloss = amat("lobby", 0.12)
    mb.box((5.85, 23.6, 1.02), (4.3, 0.36, 0.04), white)
    mb.box((5.85, 23.44, 1.0), (4.2, 0.01, 0.01), pm("lstrip", "#e6f2ff", 0.3), 0)
    for j in range(8):
        mb.box((4.05 + j * 0.52, 23.62, 1.04 + 0.2), (0.3, 0.08, 0.4), gloss, 0, rect=uv("lobby", f"copy{j % 6}"))
    r = uv("lobby", "tag")
    mb.quad((5.85, 23.82, 1.85), (1.6, 1.6 / r[4]), gloss, r, facing="-Y")
    # the front display by the glass (S05, from across the street): built here; staged() hides the shots' boxes
    mb.box((-1.75, 13.0, 0.5), (4.4, 0.8, 0.68), white)
    mb.box((-1.75, 12.59, 0.25), (4.3, 0.01, 0.01), pm("lstrip", "#e6f2ff", 0.3))
    acrylic = pm("acrylic", "#eef6ff", 0.02, alpha=0.12)
    for j in range(6):
        x = -3.5 + j * 0.7
        hz = 0.84 + (j % 2) * 0.12
        mb.box((x, 13.0, hz), (0.36, 0.3, (hz - 0.84) * 2 + 0.02), acrylic)
        mb.box((x, 13.0, hz + 0.22 + (j % 2) * 0.0), (0.32, 0.09, 0.42), gloss, 0, rect=uv("lobby", f"copy{j}"))
    mb.quad((-1.75, 12.595, 0.5), (1.6, 1.6 / r[4]), gloss, r, facing="-Y")
    # plants: real ones in the white planters, and in the corners
    for s_ in (-1, 1):
        px = B.LOBBY_DOOR_X + s_ * 3.4
        mb.box((px, 17.5, 0.85), (0.84, 0.84, 0.01), pm("soil", "#1e1812", 0.95))
        kp(f"int.lobby.plant{s_}", "potted_plant_01", (px - 0.065, 17.5, 0.02), 0.0, 1.45)
    for k, (x, y) in enumerate(((-5.2, 23.0), (23.2, 23.0), (14.6, 14.4))):
        mb.cyl((x, y, 0.47), 0.4, 0.62, white, n=24, r2=0.44)
        kp(f"int.lobby.corner{k}", "potted_plant_02", (x - 0.06, y, 0.3), 0.0, 1.3)
    # lounge seating in the west and east thirds, where nothing happens
    rug = pm("rug", "#c8ccd2", 0.95)
    for cx in (-2.5, 20.8):
        mb.box((cx, 19.6, 0.175), (3.4, 2.4, 0.01), rug)
        kp(f"int.lobby.table{cx:.0f}", "modern_coffee_table_01", (cx, 19.6, 0.17), 0.0, 1.0)
        kp(f"int.lobby.chairA{cx:.0f}", "modern_arm_chair_01", (cx - 1.2, 19.6, 0.17), math.pi / 2, 1.0)
        kp(f"int.lobby.chairB{cx:.0f}", "modern_arm_chair_01", (cx + 1.2, 19.6, 0.17), -math.pi / 2, 1.0)
        kp(f"int.lobby.chairC{cx:.0f}", "modern_arm_chair_01", (cx, 20.9, 0.17), math.pi, 1.0)
    # the reception desk: a monitor (facing the empty chair behind it), a keyboard
    dx = B.LOBBY_DOOR_X + 8.5
    scr = pm("monscreen", "#cfe6ff", 0.2)
    scr.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = gb.lin("#cfe6ff")
    scr.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0
    for k, x in enumerate((dx - 0.6, dx + 0.1)):
        mb.box((x, 14.75, 1.42), (0.6, 0.025, 0.36), face, 0, "#1c2024")
        mb.box((x, 14.765, 1.42), (0.56, 0.006, 0.32), scr)
        mb.box((x, 14.72, 1.18), (0.04, 0.04, 0.16), face, 0, "#c8ccd0")
        mb.box((x, 14.75, 1.11), (0.22, 0.16, 0.012), face, 0, "#c8ccd0")
    mb.box((dx - 0.25, 14.95, 1.11), (0.42, 0.13, 0.015), white)
    mb.done()


def staged(S, SP):
    """After shots.stage(): hide the shots' grey-box display of worse copies (lobby.front_copy*, lobby.front_table);
    build() has already put the white display in their place."""
    hide_prefix("lobby.front_copy", "lobby.front_table")


def build(S):
    dev_shop(S)
    eatery(S)
    pawn(S)
    for i, kind in SHOP_KINDS.items():
        shop(S, i, kind)
    lobby(S)
