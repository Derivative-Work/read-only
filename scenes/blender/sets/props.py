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
    """S09: the tape, torn into strips and stapled up on his door."""
    o = obj("notice")
    m = mk.MK()
    m.quad((0, 0.001, 0), (0.5, 0.7), img("receipt"), facing="+Y")
    kit.mesh_swap(o, m.mesh("prop.notice"))


def cassette():
    o = obj("cassette")
    m = mk.MK()
    shell, hub = mat("cass.shell", "#2b2d33", rough=0.35), mat("cass.hub", "#e8e8e8", rough=0.4)
    m.box((0, 0, 0), (0.1, 0.013, 0.064), shell, bevel=0.002, seg=1)
    for face, y in (("+Y", 0.0068), ("-Y", -0.0068)):
        m.quad((0, y, 0.006), (0.088, 0.04), img("cassette"), facing=face)
    for s in (-1, 1):
        m.cyl((s * 0.021, 0, -0.004), 0.006, 0.0142, hub, axis="Y", n=12)
    m.box((0, 0, -0.027), (0.06, 0.0135, 0.01), mat("cass.tape", "#4a2e1c"))
    kit.mesh_swap(o, m.mesh("prop.cassette"))


def boombox():
    o = obj("boombox")
    kit.swap(o, "boombox", scale=0.85, offset=(0, 0, -0.15), rot=(0, 0, math.pi))


def magnifier():
    o = obj("magnifier")
    reset_rot(o)
    s = 1.8
    zc = (kit.dims("magnifying_glass_01").z - 0.066) * s
    kit.swap(o, "magnifying_glass_01", scale=s, offset=(0, zc, 0), rot=(math.pi / 2, 0, 0))


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
        m.box(((bx0 + bx1) / 2, 0, (g + clear + 0.1 + H / 2) / 2), (bx1 - bx0, W, H / 2 - g - clear - 0.1), paint,
              bevel=0.03)
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
        if open_side:  # a side door rolled up on the -Y side, the dark hold showing
            m.box((bx0 + 1.6, -W / 2 - 0.005, (g + clear + 0.1 + H / 2) / 2 - 0.1), (1.8, 0.01, 1.9),
                  mat("veh.hold", "#060606", rough=0.9))
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
    for k in range(4):
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
    """S22: generic down arrows (never the site's own colours)."""
    out = [(-0.3, 0.8), (-0.3, 0.0), (-0.6, 0.0), (0.0, -0.8), (0.6, 0.0), (0.3, 0.0), (0.3, 0.8)]
    m = mk.MK()
    m.prism(out, 0.3, mat("arrow", "#e4e7ec", rough=0.35), bevel=0.04)
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
        m.quad((0, 0.002, 0), (0.18, 0.18), img(f"sticky_{k:02d}", 0.7), facing="+Y", rot=(0, r.uniform(-0.12, 0.12), 0))
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
    for s in (-1, 1):  # the roof's two slopes
        ang = math.atan2(0.45, w / 2)
        m.box((s * w / 4 * 1.05, 0, z0 + hw + 0.24), (w / 2 * 1.25, d + 0.2, 0.04), roof, rot=(0, s * ang, 0))
    m.prism([(-0.2, 0.0), (0.2, 0.0), (0.2, 0.38), (0.12, 0.5), (0.0, 0.53), (-0.12, 0.5), (-0.2, 0.38)], 0.02, dark,
            c=(0, -d / 2 - 0.006, z0 + 0.02))
    m.box((0, -d / 2 - 0.015, 0.35), (0.72, 0.02, 0.16), board)  # the sign board behind BOT DEFENSE
    m.lathe([(0.0, z0 + 0.0), (0.12, z0 + 0.0), (0.13, z0 + 0.06), (0.1, z0 + 0.06), (0.1, z0 + 0.02), (0.0, z0 + 0.02)],
            mat("dog.bowl", "#8a9096", metal=0.8, rough=0.35), c=(0.35, -0.85, 0), n=24)  # an empty bowl
    kit.mesh_swap(o, m.mesh("prop.doghouse"))
    blank(obj("doghouse.roof"))
    blank(obj("doghouse.door"))
    sign = obj("doghouse.sign")
    if sign:
        sign.location.y -= 0.02
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
    h = obj("shovel.handle")
    kit.swap(h, "rusted_spade_01", scale=1.15, offset=(0, 0, -0.7))
    blank(obj("shovel.blade"))


def build(S, SP):
    for f in (adding_machine, calendar, envelope, notice, cassette, boombox, magnifier, vehicles, crates, arrows,
              hoses, briefcase, balcony_rail, balcony_light, bell, podium, banner, stickies, funnel, payroll, rubberband, coffin,
              doghouse, lanterns, shovel):
        f()
    brickwall(SP)
    brooms(SP)
    chalk(S, SP)
    shots.inherit_visibility()
