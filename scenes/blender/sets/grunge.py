"""The grunge pass on the block (M4; the human's note on the look test: "make sure it's grungy"). The final look only:
block.build() calls build(S) when FINAL. The grey-box stays as it was.

The grime is in the architecture and the street, never on the people (brief):
  windows     frames and sills on every upper window; blinds, curtains or foil in many; window AC units
  fire escapes on the brick buildings: two landings, a stair and a drop ladder, black paint gone rusty
  decals      made-up graffiti tags on the shutters (they roll down with them) and the walls; layers of torn
              wheatpaste posters on the piers between shops (scripts/gen_grunge_decals.py)
  the street  litter in the gutters and along the walls (paper, flyers, cans, cups, butts); bag piles at the
              curb; the trolley wire and its span wires; sagging cables along the facades; a utility pole at the corner
              and in the park; dead leaves in the park
  the tower   none of it: its sidewalk stays spotless, the only clean thing on the street (style spec)

Materials take their grime from gb.grime (config/look.json, "grime"). Everything is seeded, so every render matches.
"""
import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

import gb

DECALS = gb.ROOT / "assets" / "gen" / "grunge"
SEED = 20261030
CURTAINS = ["#5e3b5c", "#2f5d4e", "#6b5a2a", "#3a4a6b", "#8a6d5a", "#4b4f3a"]
TOWER_SPAN = (-6.0, 24.0)


def M(key, hexcol, grime=0.5, **kw):
    m = gb.mat(f"grunge.{key}", hexcol, **kw)
    if not m.get("grimed") and grime:
        gb.grime(m, amt=grime)
        m["grimed"] = 1
    return m


def decal_mat(img):
    """An image with alpha on a UV'd quad: the tag or poster, roughened, its paint picking up the street's grime."""
    key = f"decal.{img}"
    if key in gb._MATS:
        return gb._MATS[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    m.surface_render_method = "DITHERED"
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(DECALS / f"{img}.png"), check_existing=True)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.85
    gb.grime(m, amt=0.45, damp=0.6)
    gb._MATS[key] = m
    return m


def decal(name, img, center, size, parent=None, facing="+Y", tilt=0.0):
    """gb.plane's quad, with UVs (its first vertex is bottom left as the viewer sees it)."""
    o = gb.plane(name, center, size, decal_mat(img), parent=parent, facing=facing)
    uv = o.data.uv_layers.new()
    for loop, c in zip(o.data.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[loop.index].uv = c
    if tilt:  # a small turn in the wall's plane
        ax = {"+Y": "Y", "-Y": "Y", "+X": "X", "-X": "X"}[facing]
        o.matrix_basis = o.matrix_basis @ Matrix.Rotation(tilt, 4, ax)
    return o


class Batch:
    """Many small props merged into one mesh per material, so litter costs a handful of objects."""

    def __init__(self, name, m):
        self.name, self.m, self.bm = name, m, bmesh.new()

    def add(self, kind, loc, rot, scale, rng):
        tmp = bmesh.new()
        if kind == "crumple":
            bmesh.ops.create_icosphere(tmp, subdivisions=1, radius=1.0)
            for v in tmp.verts:
                v.co *= rng.uniform(0.65, 1.15)
        elif kind == "sheet":
            bmesh.ops.create_cube(tmp, size=1.0)
            for v in tmp.verts:
                v.co.z *= 0.01
                v.co.z += 0.04 * v.co.x * v.co.y  # a little curl
        elif kind == "cyl":
            bmesh.ops.create_cone(tmp, cap_ends=True, segments=10, radius1=1.0, radius2=1.0, depth=1.0)
        elif kind == "cup":
            bmesh.ops.create_cone(tmp, cap_ends=True, segments=10, radius1=0.7, radius2=1.0, depth=1.0)
        elif kind == "bag":
            bmesh.ops.create_icosphere(tmp, subdivisions=2, radius=1.0)
            for v in tmp.verts:
                v.co *= rng.uniform(0.88, 1.08)
                if v.co.z > 0.75:  # the knot
                    v.co.x *= 0.4
                    v.co.y *= 0.4
                    v.co.z *= 1.15
        elif kind == "cone":
            bmesh.ops.create_cone(tmp, cap_ends=False, segments=5, radius1=1.0, radius2=0.0, depth=1.0)
        mtx = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*scale, 1.0))
        bmesh.ops.transform(tmp, matrix=mtx, verts=tmp.verts)
        me = bpy.data.meshes.new("tmp")
        tmp.to_mesh(me)
        tmp.free()
        self.bm.from_mesh(me)
        bpy.data.meshes.remove(me)

    def done(self, smooth=False):
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        for p in me.polygons:
            p.use_smooth = smooth
        me.materials.append(self.m)
        return gb.link(bpy.data.objects.new(self.name, me))


def windows(S, rng, signs):
    """Frames and sills on every upper window; blinds, curtains, foil and AC units on many. The coverings glow with
    their window (the same "lit" control), so they go dark with it at S15."""
    frame, sill = M("winframe", "#3a3631", 0.5), M("winsill", "#6b665c", 0.6)
    ac, grille = M("ac", "#b9b2a3", 0.7), M("acgrille", "#2a2826", 0.3)
    E = gb.LOOK["lights"]["window_emit"]
    for root in S["shops"]:
        i = int(root.name[4:])
        for fl in (0, 1):
            for k in range(3):
                w = bpy.data.objects[f"shop{i}.win{fl}{k}"]
                ctl = bpy.data.objects[f"{w.name}.ctl"]
                x, _, z = w.location
                for nm, c, s in (("t", (x, 0.05, z + 0.84), (1.4, 0.1, 0.08)), ("l", (x - 0.66, 0.05, z), (0.08, 0.1, 1.7)),
                                 ("r", (x + 0.66, 0.05, z), (0.08, 0.1, 1.7))):
                    gb.box(f"{w.name}.frame{nm}", c, s, frame, parent=root)
                gb.box(f"{w.name}.sill", (x, 0.1, z - 0.86), (1.55, 0.2, 0.08), sill, parent=root)
                if (i, f"win{fl}{k}") in signs or (i == 7):  # sign windows and the scaffold stay as they are
                    continue
                r = rng.random()
                if r < 0.35:  # a blind, pulled part way down
                    h = 1.6 * rng.uniform(0.25, 0.8)
                    gb.plane(f"{w.name}.blind", (x, 0.035, z + 0.8 - h / 2), (1.16, h),
                             gb.glow_mat(f"blind.{i}{fl}{k}", rng.choice(("#e8dcc0", "#d9cfa8", "#cfd2c9")), 0.45 * E,
                                         ctl, "lit", base="#6f6a5c"), parent=root, facing="+Y")
                elif r < 0.65:  # curtains, drawn to the sides
                    col = rng.choice(CURTAINS)
                    for s in (-1, 1):
                        cw = rng.uniform(0.25, 0.42)
                        gb.plane(f"{w.name}.curtain{s}", (x + s * (0.58 - cw / 2), 0.035, z), (cw, 1.6),
                                 gb.glow_mat(f"curtain.{i}{fl}{k}", col, 0.3 * E, ctl, "lit", base=col),
                                 parent=root, facing="+Y")
                elif r < 0.75:  # foil or newspaper over the glass
                    gb.plane(f"{w.name}.foil", (x, 0.035, z), (1.16, 1.56),
                             gb.glow_mat(f"foil.{i}{fl}{k}", "#c9c6bd", 0.12 * E, ctl, "lit", base="#77756f"),
                             parent=root, facing="+Y")
                if rng.random() < 0.22:  # a window AC unit
                    gb.box(f"{w.name}.ac", (x, 0.22, z - 0.55), (0.66, 0.5, 0.42), ac, parent=root)
                    gb.plane(f"{w.name}.acg", (x + 0.08, 0.475, z - 0.55), (0.42, 0.3), grille, parent=root,
                             facing="+Y")


def fire_escape(root, name, rng):
    """Two landings (under the second-row windows and at the roof), a stair between them, a drop ladder."""
    m = M("fe", "#1d1b19", 0.6, metal=0.5, rough=0.6)
    for z in (7.55, 10.55):
        gb.box(f"{name}.deck{z}", (-0.9, 0.55, z), (3.6, 1.0, 0.05), m, parent=root)
        gb.box(f"{name}.rail{z}", (-0.9, 1.05, z + 1.0), (3.6, 0.04, 0.04), m, parent=root)
        gb.box(f"{name}.mid{z}", (-0.9, 1.05, z + 0.5), (3.6, 0.03, 0.03), m, parent=root)
        for s in (-2.7, 0.9):
            gb.box(f"{name}.side{z}{s}", (s, 0.55, z + 1.0), (0.04, 1.0, 0.04), m, parent=root)
            gb.box(f"{name}.bracket{z}{s}", (s, 0.5, z - 0.35), (0.05, 0.05, 0.9), m, parent=root).rotation_euler.x = 0.75
        for k in range(9):
            gb.box(f"{name}.post{z}{k}", (-2.7 + k * 0.45, 1.05, z + 0.5), (0.025, 0.025, 1.0), m, parent=root)
    run = math.hypot(2.4, 3.0)
    for s in (0.2, 0.75):  # the stair's stringers
        st = gb.box(f"{name}.stair{s}", (-0.3, s, 9.05), (run, 0.05, 0.12), m, parent=root)
        st.rotation_euler.y = math.atan2(3.0, 2.4)
    for k in range(10):
        t = (k + 0.5) / 10
        gb.box(f"{name}.tread{k}", (0.9 - 2.4 * t, 0.475, 7.55 + 3.0 * t), (0.22, 0.55, 0.03), m, parent=root)
    for s in (-2.55, -2.15):  # the drop ladder, hanging over the sign
        gb.box(f"{name}.ladder{s}", (s, 1.0, 6.4), (0.04, 0.04, 2.3), m, parent=root)
    for k in range(7):
        gb.box(f"{name}.rung{k}", (-2.35, 1.0, 5.4 + k * 0.32), (0.4, 0.03, 0.03), m, parent=root)


def pier(S, i):
    """The local x of the 0.8 m party-wall pier this shop shares with a neighbour (posters need both halves), or None."""
    north = i >= S["n_south"]
    row = [j for j in range(len(S["shopx"])) if (j >= S["n_south"]) == north]
    xs = {S["shopx"][j] for j in row}
    for local in (3.0, -3.0):
        if S["shopx"][i] + (2 * local if not north else -2 * local) in xs:
            return local
    return None


def decals(S, rng, tags, posters):
    """Tags on most shutters and low on the walls; layered posters on the piers between shops."""
    for i, sh in enumerate(S["shutters"]):
        for k in range(rng.choice((1, 1, 2, 2, 3))):
            # clear of "UNDER NEW MANAGEMENT" (local x -1.8..0.2, z -1.6..-0.9): low along the bottom, or to its right
            if rng.random() < 0.5:
                w = rng.uniform(1.2, 2.0)
                c = (rng.uniform(-2.5 + w / 2, 2.5 - w / 2), rng.uniform(-2.5, -2.2))
            else:
                w = rng.uniform(1.2, 1.9)
                c = (rng.uniform(0.4 + w / 2, 2.55 - w / 2 + 0.3), rng.uniform(-2.2, -1.3))
            decal(f"shop{i}.tag{k}", rng.choice(tags), (c[0], 0.046 + 0.002 * k, c[1]), (w, w / 2), parent=sh,
                  tilt=rng.uniform(-0.12, 0.12))
    for root in S["shops"]:
        i = int(root.name[4:])
        px = pier(S, i)
        if px is None:
            continue
        if rng.random() < 0.5:  # low on a pier, under where the posters go
            decal(f"shop{i}.walltag", rng.choice(tags), (px, 0.013, rng.uniform(0.35, 0.6)), (0.7, 0.35),
                  parent=root, tilt=rng.uniform(-0.15, 0.15))
        for k in range(rng.randint(1, 4)):  # layered posters, each pasted over the last
            decal(f"shop{i}.poster{k}", rng.choice(posters), (px + rng.uniform(-0.1, 0.1), 0.018 + 0.005 * k,
                  rng.uniform(1.2, 2.3)), (0.5, 0.667), parent=root, tilt=rng.uniform(-0.08, 0.08))
    lease = bpy.data.objects.get("shop9")
    if lease:
        for k in range(3):
            decal(f"lease.poster{k}", rng.choice(posters), (-2.3 + k * 1.3 + rng.uniform(-0.2, 0.2), 0.085 + 0.005 * k,
                  rng.uniform(1.4, 2.2)), (0.5, 0.667), parent=lease, tilt=rng.uniform(-0.1, 0.1))
        decal("lease.tag", rng.choice(tags), (-0.8, 0.105, 1.0), (2.4, 1.2), parent=lease)
    # the far corner: a big throw-up and a poster wall
    decal("corner.far.tag", tags[2], (-45.98, -12.0, 1.6), (4.0, 2.0), facing="+X")
    for k in range(6):
        decal(f"corner.far.poster{k}", posters[k % len(posters)], (-45.97 + 0.005 * k, -17.0 + k * 0.45 + rng.uniform(-0.1, 0.1),
              1.6 + rng.uniform(-0.3, 0.3)), (0.5, 0.667), facing="+X", tilt=rng.uniform(-0.08, 0.08))
    for k in range(2):  # flyers taped low on the payphone post, below S03's close-up of the handset
        decal(f"payphone.flyer{k}", rng.choice(posters), (-31.5, -8.52 + 0.005 * k, 0.3 + k * 0.22), (0.14, 0.19),
              facing="+Y", tilt=rng.uniform(-0.2, 0.2))


def litter(rng):
    """Paper, flyers, cans, cups and cigarette butts: thick in the gutters and along the walls, thinner on the
    open sidewalk, none in front of the tower."""
    paper = Batch("litter.paper", M("paper", "#d9d4c4", 0.5))
    paper2 = Batch("litter.paper2", M("paper2", "#b9ad8c", 0.6))
    dark = Batch("litter.dark", M("cans", "#3a3f45", 0.3, metal=0.6, rough=0.4))
    colour = Batch("litter.colour", M("cups", "#7d93a8", 0.4))
    butts = Batch("litter.butts", M("butts", "#d8c7a0", 0.3))

    def spot(side, where):
        x = rng.uniform(-32.5, 44.5)
        if side > 0 and TOWER_SPAN[0] - 1 < x < TOWER_SPAN[1] + 1:
            return None
        if where == "gutter":
            y, z = rng.uniform(5.55, 5.95), 0.0
        elif where == "wall":
            y, z = rng.uniform(9.45, 9.85), 0.15
        else:
            y, z = rng.uniform(6.3, 9.4), 0.15
        return Vector((x, side * y, z))

    plan = [("gutter", 0.5), ("wall", 0.3), ("open", 0.2)]
    for n, fn in ((260, "crumple"), (90, "sheet"), (45, "can"), (30, "cup"), (320, "butt")):
        for _ in range(n):
            where = rng.choices([p[0] for p in plan], [p[1] for p in plan])[0]
            p = spot(rng.choice((-1, 1)), where)
            if p is None:
                continue
            rot = (rng.uniform(0, 6.3), rng.uniform(0, 6.3), rng.uniform(0, 6.3))
            if fn == "crumple":
                r = rng.uniform(0.035, 0.08)
                (paper if rng.random() < 0.6 else paper2).add("crumple", p + Vector((0, 0, r * 0.7)), rot, (r,) * 3, rng)
            elif fn == "sheet":
                b = paper if rng.random() < 0.5 else paper2
                b.add("sheet", p + Vector((0, 0, 0.005)), (0, 0, rot[2]), (0.21, 0.28, 1.0), rng)
            elif fn == "can":
                dark.add("cyl", p + Vector((0, 0, 0.033)), (math.pi / 2, 0, rot[2]), (0.033, 0.033, 0.12), rng)
            elif fn == "cup":
                colour.add("cup", p + Vector((0, 0, 0.04)), (math.pi / 2, 0, rot[2]), (0.04, 0.04, 0.11), rng)
            else:
                butts.add("cyl", p + Vector((0, 0, 0.004)), (math.pi / 2, 0, rot[2]), (0.004, 0.004, 0.03), rng)
    for b in (paper, paper2, dark, colour, butts):
        b.done()


def bags(rng):
    """Piles of black bags at the curb, and flattened boxes against the walls."""
    bag = Batch("bags", M("bag", "#0d0d0f", 0.15, rough=0.28))
    for x, side in ((-12.5, -1), (7.5, -1), (31.0, -1), (30.5, 1), (42.0, 1)):
        for k in range(rng.randint(3, 5)):
            r = rng.uniform(0.28, 0.4)
            p = Vector((x + rng.uniform(-0.7, 0.7), side * rng.uniform(6.4, 6.9), 0.15 + r * 0.7))
            bag.add("bag", p, (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rng.uniform(0, 6.3)), (r, r * 0.9, r * 0.75), rng)
    bag.done(smooth=True)
    card = M("cardboard", "#a07a4e", 0.6)
    for k, x in enumerate((-17.5, 12.2, 36.4)):
        b = gb.box(f"cardboard{k}", (x, -9.62, 0.75), (0.9, 0.04, 1.2), card)
        b.rotation_euler.x = 0.22


def wires(rng):
    """The streetcar's contact wire and span wires, cables sagging along the south facades, two utility poles."""
    wire = M("wire", "#0e0e0e", 0.0, rough=0.5)

    def cable(name, pts, r=0.01):
        cu = bpy.data.curves.new(name, "CURVE")
        cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", r, 1
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for p, q in zip(sp.points, pts):
            p.co = (*q, 1.0)
        cu.materials.append(wire)
        return gb.link(bpy.data.objects.new(name, cu))

    def sag(a, b, d, n=16):
        a, b = Vector(a), Vector(b)
        return [tuple(a.lerp(b, t) - Vector((0, 0, d * 4 * t * (1 - t)))) for t in (k / n for k in range(n + 1))]

    pole = M("pole", "#4a3c2e", 0.5)
    for k, (x, y) in enumerate(((-34.5, -6.4), (-24.0, 9.6))):
        gb.cyl(f"upole{k}", (x, y, 5.0), 0.15, 10.0, pole)
        gb.box(f"upole{k}.xarm", (x, y, 9.3), (0.12, 2.2, 0.12), pole)
        gb.cyl(f"upole{k}.tx", (x + 0.3, y, 8.4), 0.3, 0.9, M("transformer", "#7d8085", 0.6, metal=0.4))
    cable("trolley", [(-60, 0, 5.6), (60, 0, 5.6)], 0.008)
    for x in range(-30, 45, 12):
        north = (-24.0, 9.6, 8.0) if x < -9 else (x, 10.45 if TOWER_SPAN[0] <= x <= TOWER_SPAN[1] else 9.95, 7.2)
        cable(f"span{x}a", sag((x, -9.95, 7.2), (x, 0, 5.65), 0.25), 0.007)
        cable(f"span{x}b", sag((x, 0, 5.65), north, 0.25), 0.007)
    for k, z in enumerate((6.85, 6.95)):  # cables along the south row, held at each party wall
        pts = []
        for x0 in range(-30, 42, 6):
            pts += sag((x0, -9.9 + 0.04 * k, z), (x0 + 6, -9.9 + 0.04 * k, z), rng.uniform(0.15, 0.35), 8)[:-1]
        cable(f"facade.cable{k}", pts, 0.012)
    cable("corner.drop", sag((-34.5, -6.4, 9.0), (-46.0, -9.0, 8.0), 0.6), 0.012)
    cable("corner.drop2", sag((-34.5, -6.4, 8.8), (-30.0, -9.9, 6.9), 0.3), 0.012)


def park_leaves(rng):
    leaves = Batch("park.leaves", M("leaves", "#6b4a2a", 0.2))
    for _ in range(500):
        x, y = rng.uniform(-32, -10), rng.uniform(10.5, 27)
        if rng.random() < 0.4:  # drifted against the front fence and the north gutter
            y = rng.uniform(10.6, 11.2) if rng.random() < 0.6 else rng.uniform(5.55, 5.95)
        z = 0.045 if y > 10 else 0.003
        leaves.add("sheet", (x, y, z), (rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, 6.3)),
                   (0.07, 0.05, 1.0), rng)
    leaves.done()
    weeds = Batch("weeds", M("weeds", "#55603a", 0.2))
    for _ in range(140):  # tufts where the sidewalk meets the walls
        side = rng.choice((-1, 1))
        x = rng.uniform(-32, 44)
        if side > 0 and TOWER_SPAN[0] - 1 < x < TOWER_SPAN[1] + 1:
            continue
        for _ in range(rng.randint(2, 5)):
            p = (x + rng.uniform(-0.08, 0.08), side * rng.uniform(9.8, 9.95), 0.15 + 0.05)
            weeds.add("cone", p, (rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0), (0.02, 0.02, rng.uniform(0.08, 0.2)), rng)
    weeds.done()


def build(S, signs):
    rng = random.Random(SEED)
    tags = sorted(p.stem for p in DECALS.glob("tag_*.png"))
    posters = sorted(p.stem for p in DECALS.glob("poster_*.png"))
    assert tags and posters, "run scripts/gen_grunge_decals.py first"
    bpy.context.view_layer.update()
    windows(S, rng, signs)
    for root in S["shops"]:
        i = int(root.name[4:])
        if i % 3 == 0 and i != 0:  # the brick buildings (not the eatery's, which the opening shots look at)
            fire_escape(root, f"shop{i}.fe", rng)
    decals(S, rng, tags, posters)
    litter(rng)
    bags(rng)
    wires(rng)
    park_leaves(rng)
