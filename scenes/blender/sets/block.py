"""The block, grey-box (M3): one scene for the whole video (brief, "Sets and characters").

Layout (metres; +X east along the street, +Y north, z up):
  street      y -6..6, x -45..45; one streetcar track down the middle; a cross street west of x = -33 (the corner)
  south row   ten shopfronts facing the street (+Y), x -30..30, 6 m each, front at y = -10, three storeys; the
              eatery (r/Philippines) at x = -27 with its interior, the Dev's shop at x = -21 with its interior
  the corner  the dead payphone at (-31.5, -8.6) facing the street; the streetlight with its coin meter at (-25, -6.6)
  the tower   north side, x -6..24, y 10.5..30, 70 m: glass lobby (throne, screen, doors), balcony with podium and bell
              at z 8, an LED ticker band at z 13-14, a billboard on the roof facing the street
  the park    north side, x -32..-10, y 10.5..27: fence and gate, the shoebox coffin, the BOT DEFENSE doghouse, the
              cemetery behind (the brief's "Memorial headstones" table), the field of 144,926 markers

Grey-box: flat colours, no textures. Shop names follow the brief: community names in plain shop lettering, the Dev's
trade sign, nothing in Reddit's fonts or logo. The eatery is fictional and takes nothing from the real restaurant but
its kind (reference/README.md).
"""
import math

import numpy as np

import gb

C = {  # grey-box colours (sRGB hex)
    "asphalt": "#2a2b2e", "sidewalk": "#6b6964", "curb": "#85827b", "rail": "#9a9a9a",
    "brick": "#6e4a3c", "stucco": "#8a8478", "stucco2": "#7a7f86", "trim": "#3b3936", "glass": "#9fb6c4",
    "shutter": "#8d9094", "sign": "#e9e2cf", "ink": "#1b1b1b", "plywood": "#b08a57", "graffiti1": "#c2457a",
    "graffiti2": "#3f8fc9", "lease": "#d23b2f", "tower": "#4d5a66", "towerglass": "#7fa6c8", "lobby": "#d9d2c2",
    "rack": "#2b2f36", "screen": "#7fd0ff", "ticker": "#55ff7a", "billboard": "#f0f0f0", "dirt": "#4a3a2c",
    "grass": "#3b4a33", "fence": "#2f2f2f", "stone": "#a7a39a", "coffin": "#c9b28a", "doghouse": "#8a5a3a",
    "hoodie": "#2f7f7a", "apron": "#8a5c32", "skin": "#c69c7d", "cape": "#f2efe6", "capetrim": "#8b1e2b",
    "ceohood": "#5a5d63", "vest": "#ff7a1a", "modbody": "#4d5560", "vip": "#7a828c", "gold": "#d8b23a",
    "goodbot": "#b8b0a0", "lantern": "#ffc46b", "silhouette": "#050505", "rec": "#ff2a2a", "neon": "#ff3355",
    "warm": "#ffcf8a", "window": "#ffd9a0", "eatery_wall": "#c9a43c", "tile": "#9a4e35", "steam": "#b9bec4",
    "tray": "#2f8a3a", "menu": "#1e3b2a", "table": "#7a5636", "chair": "#141414", "plate": "#f4f1ea",
    "phone": "#151515", "phonescreen": "#9ad0ff", "badge": "#f6f6f6", "paper": "#f3f0e6", "tape": "#f7f3e4",
    "streetlamp": "#ffe2a8", "van": "#d8d8d8", "truck": "#e6e6e6", "crate": "#a0784a", "brick_new": "#9a5a44",
}


FINAL = False  # set by the driver: True = the M4 look (textures, stylized figures, sodium light), False = grey-box
TEXMAP = {"asphalt": "asphalt_03", "sidewalk": "concrete_pavement", "brick": "brick_4", "stucco": "concrete_wall_003",
          "stucco2": "blue_plaster_weathered", "shutter": "painted_metal_shutter", "plywood": "plywood",
          "grass": "grass_ground", "dirt": "dry_ground_01", "tile": "brown_floor_tiles",
          "curb": "concrete_pavement",
          "stone": "concrete"}  # the headstones: cast concrete, its roughness map for a worn sheen (the human, M4 v5)
# per-key texture options (gb.tex_mat): the headstones each get their own offset, tilt, scale and tone, and a calmer
# face so the inscriptions read (the human, M4 v6: "hard to read and too clearly have the same texture")
TEXOPT = {"stone": {"vary": (0.35, 0.18), "flat": (0.55, "#8e897f"), "bump": 0.5}}


def M(key, **kw):
    m = gb.tex_mat(key, TEXMAP[key], **TEXOPT.get(key, {})) if FINAL and key in TEXMAP else gb.mat(key, C[key], **kw)
    g = gb.LOOK["grime"]["materials"].get(key)
    if FINAL and g and not m.get("grimed"):  # the human's note on the look test: "make sure it's grungy"
        gb.grime(m, **g)
        m["grimed"] = 1
    return m


def look_colours():
    """The style spec's palette over the grey-box colours (called by the driver for the final look)."""
    P = gb.LOOK["palette"]
    C.update({"streetlamp": P["sodium"], "window": P["community"], "warm": P["community"], "neon": P["rec"],
              "rec": P["rec"], "gold": P["gold"], "vest": P["vest"], "screen": P["screen"], "ticker": P["ticker"],
              "towerglass": P["corporate"], "lantern": P["community"], "sign": "#efe6cf",
              "stone": "#d9d4ca"})  # plain pale stone, untextured, so the inscriptions read


# Every community name on the block is on the list of subreddits that announced they would join the June 2023
# blackout (r/ModCoord's posts, as collected by github.com/bpettis/reddit-blackout-announcements; the copy used is
# listed in reference/sources/blackout_list.tsv).
SHOPS = [  # x centre, sign, kind
    (-27, "r/Philippines", "eatery"),
    (-21, "Third-Party App Repair  est. 2008", "dev"),
    (-15, "r/Cooking", "shop"),
    (-9, "r/Sourdough", "shop"),
    (-3, "PAWN", "pawn"),
    (3, "r/Running", "shop"),
    (9, "r/Knitting", "shop"),
    (15, "r/Gardening", "shop"),
    (21, "r/Woodworking", "shop"),
    (27, "FOR LEASE", "lease"),
    (33, "r/AskHistorians", "shop"),
    (39, "r/Coffee", "shop"),
]
NORTH_SHOPS = [  # facing the street from the north side, east of the tower
    (28, "r/Houseplants", "shop"),
    (34, "r/BoardGames", "shop"),
    (40, "r/Crochet", "shop"),
]
UPPER_SIGNS = [  # painted upper-window signs (second-floor tenants), (shop index, window, name)
    (2, "win01", "r/Embroidery"), (5, "win00", "r/MechanicalKeyboards"), (6, "win12", "r/Quilting"),
    (9, "win11", "r/HomeImprovement"), (10, "win02", "r/Chess"), (12, "win10", "r/Photography"),
]
FRONT = -10.0  # the south row's facade plane
FRONT_Y = FRONT
TOWER_X = (-6.0, 24.0)
TOWER_Y = (10.5, 30.0)
LOBBY_DOOR_X = 9.0


def street(S):
    gb.box("ground", (0, 0, -0.05), (200, 200, 0.1), M("asphalt"))
    gb.box("sidewalk.s", (6, -8, 0.075), (78, 4, 0.15), M("sidewalk"))
    gb.box("sidewalk.n", (6, 8, 0.075), (78, 4, 0.15), M("sidewalk"))
    gb.box("curb.s", (6, -6.05, 0.08), (78, 0.15, 0.16), M("curb"))
    gb.box("curb.n", (6, 6.05, 0.08), (78, 0.15, 0.16), M("curb"))
    for y in (-0.72, 0.72):
        gb.box(f"rail.{y}", (0, y, 0.02), (200, 0.08, 0.04), M("rail", rough=0.3, metal=0.8))
    # the cross street's far side: a plain wall of buildings so the corner reads as a corner
    gb.box("corner.far", (-52, -16, 6), (12, 16, 12), M("stucco2"))
    gb.box("corner.far.n", (-52, 18, 7), (12, 16, 14), M("brick"))
    # sidewalk squares on the south sidewalk (S33 chalks one)
    for i, x in enumerate(np.arange(-32.5, 44, 1.5)):
        gb.box(f"sq.{i}", (x, -8, 0.153), (0.02, 4, 0.006), M("curb"))  # 6 mm proud: at 3 mm they flickered at a distance
    S["chalk_sq"] = (-10.25, -8.75)


def shopfront(S, i, xw, sign, kind, north=False):
    """One shopfront, built in local coordinates around its root (facade centre at ground level, facing local +Y):
    the south row faces the street at y = FRONT; north=True turns it to face the street from y = -FRONT."""
    w, d, h = 6.0, 12.0, 11.0
    x, FRONT = 0.0, 0.0  # local
    root = gb.empty(f"shop{i}", (xw, -FRONT_Y if north else FRONT_Y, 0))
    root.rotation_euler.z = math.pi if north else 0.0
    import bpy
    bpy.context.view_layer.update()
    S.setdefault("shops", []).append(root)
    _gb = gb

    class _P:  # gb with parent=root on every object made here
        def __getattr__(self, name):
            f = getattr(_gb, name)
            if name in ("box", "cyl", "sphere", "plane", "text", "empty"):
                return lambda *a, **k: f(*a, **{**k, "parent": k.get("parent", root)})
            return f
    gb_ = _P()
    wall = M("brick") if i % 3 == 0 else M("stucco") if i % 3 == 1 else M("stucco2")
    # upper storeys: a solid block; ground floor: walls, ceiling and a back wall around a hollow room
    gb_.box(f"shop{i}.upper", (x, FRONT - d / 2, 4.2 + (h - 4.2) / 2), (w, d, h - 4.2), wall)
    gb_.box(f"shop{i}.pierL", (x - w / 2 + 0.2, FRONT - 0.2, 2.1), (0.4, 0.4, 4.2), wall)
    gb_.box(f"shop{i}.pierR", (x + w / 2 - 0.2, FRONT - 0.2, 2.1), (0.4, 0.4, 4.2), wall)
    # between the piers: run across them, its face and theirs were one plane and flickered (S02)
    gb_.box(f"shop{i}.lintel", (x, FRONT - 0.2, 3.7), (w - 0.8, 0.4, 1.0), M("trim"))
    gb_.box(f"shop{i}.back", (x, FRONT - 6.2, 2.1), (w, 0.2, 4.2), M("stucco"))
    # behind the piers and lintel (from FRONT - 0.395): running forward inside them, 5 mm under their faces, they
    # flickered through them from across the street
    gb_.box(f"shop{i}.sideL", (x - w / 2 + 0.055, FRONT - 3.2975, 2.1), (0.1, 5.805, 4.2), M("stucco"))
    gb_.box(f"shop{i}.sideR", (x + w / 2 - 0.055, FRONT - 3.2975, 2.1), (0.1, 5.805, 4.2), M("stucco"))
    gb_.box(f"shop{i}.floor", (x, FRONT - 3.1, 0.155), (w, 6.2, 0.01), M("tile" if kind == "eatery" else "curb"))
    gb_.box(f"shop{i}.sill", (x - 0.8, FRONT - 0.1, 0.3), (3.8, 0.3, 0.6), M("trim"))
    glass = gb_.plane(f"shop{i}.glass", (x - 0.8, FRONT + 0.01, 1.85), (3.8, 2.3),
                     gb.mat("glass_a", C["glass"], rough=0.05, alpha=0.18), facing="+Y")
    db = 0.185 if kind == "dev" else 0.1  # the Dev's: a gap under it for the tape (S08) to run out through
    door = gb_.box(f"shop{i}.door", (x + 1.9, FRONT - 0.05, (db + 2.5) / 2), (1.2, 0.08, 2.5 - db),
                  gb.mat("glass_a", C["glass"], alpha=0.18) if kind == "dev" else M("trim"))
    gb_.box(f"shop{i}.slot", (x + 1.9, FRONT + 0.0, 1.0), (0.35, 0.02, 0.06), M("ink"))
    # the sign band
    gb_.box(f"shop{i}.signband", (x, FRONT + 0.05, 3.7), (5.4, 0.1, 0.8),
           M("lease") if kind == "lease" else M("sign"))
    gb_.text(f"shop{i}.sign", sign, 0.42 if len(sign) < 16 else 0.3, M("sign") if kind == "lease" else M("ink"),
            (x, FRONT + 0.11, 3.7), facing="+Y")
    # upper windows (lit warm or dark; S48: a red REC light in every one)
    wins = []
    for fl, z in enumerate((5.6, 8.6)):
        for k, dx in enumerate((-1.8, 0, 1.8)):
            o = gb_.empty(f"shop{i}.win{fl}{k}.ctl", (x + dx, FRONT, z))
            o["lit"] = 1.0 if (i * 7 + fl * 3 + k) % 4 else 0.0
            gb_.plane(f"shop{i}.win{fl}{k}", (x + dx, FRONT + 0.02, z), (1.2, 1.6),
                     gb.glow_mat(f"win.{i}{fl}{k}", C["window"], gb.LOOK["lights"]["window_emit"] if FINAL else 1.2,
                                 o, "lit", base="#14161a" if FINAL else None), facing="+Y")
            rec = gb_.sphere(f"shop{i}.rec{fl}{k}", (x + dx, FRONT + 0.15, z + 0.4), 0.08, M("rec", emit=12.0))
            wins.append((o, rec))
    S.setdefault("windows", []).append(wins)
    # the roll-down shutter: its origin at the top, hanging down; scale z 0 = up (open), 1 = down (closed)
    sh = gb_.box(f"shop{i}.shutter", (x, FRONT + 0.12, 3.15), (5.2, 0.08, 3.0), M("shutter", metal=0.4, rough=0.5))
    sh.data.transform(__import__("mathutils").Matrix.Translation((0, 0, -1.5)))
    sh.scale.z = 0.0
    S.setdefault("shutters", []).append(sh)
    # neon READ-ONLY sign (S14): on the lintel, off until its shutter slams
    ctl = gb_.empty(f"shop{i}.neon.ctl", (x, FRONT, 0))
    gb_.text(f"shop{i}.neon", "READ-ONLY", 0.34, gb.glow_mat(f"neon.{i}", C["neon"], 14.0, ctl, "on",
                                                       base="#2a2224" if FINAL else None),
            (x, FRONT + 0.2, 4.55), facing="+Y")
    S.setdefault("neon", []).append(ctl)
    # padlock and "UNDER NEW MANAGEMENT" (Hook 2 on), keypad "Log in to continue" (S48)
    lock = gb_.box(f"shop{i}.padlock", (x + 1.2, FRONT + 0.2, 0.35), (0.18, 0.08, 0.22), M("gold", metal=0.8, rough=0.3))
    unm = gb_.text(f"shop{i}.unm", "UNDER NEW\nMANAGEMENT", 0.22, M("lease"), (x - 0.8, FRONT + 0.18, 1.9), facing="+Y")
    # M5: beside the door on the shutter (in the doorway, the doorman stood in front of it), larger, so it reads in
    # the crane
    pad = gb_.box(f"shop{i}.keypad", (x + 0.75, FRONT + 0.2, 1.35), (0.75, 0.06, 0.6), M("phone"))
    padtxt = gb_.text(f"shop{i}.keypad.txt", "Log in to\ncontinue", 0.11, M("screen", emit=5.0),
                     (x + 0.75, FRONT + 0.24, 1.37), facing="+Y")
    S.setdefault("padlocks", []).append([lock, unm])
    S.setdefault("keypads", []).append([pad, padtxt])
    if kind == "lease":
        for k in range(3):
            gb_.box(f"shop{i}.ply{k}", (x - 2 + k * 1.3, FRONT + 0.06, 1.85), (1.25, 0.04, 2.3), M("plywood"))
    if kind == "pawn":
        gb_.box("pawn.led", (x, FRONT + 0.25, 4.6), (2.6, 0.2, 0.6), M("ink"))
        gb_.text("pawn.led.txt", "48:00:00", 0.4, M("rec", emit=8.0), (x, FRONT + 0.36, 4.6), facing="+Y", mono=True)
    if i in (2, 6) and not FINAL:  # graffiti on piers and plywood (the final look has grunge.py's tags instead)
        gb_.plane(f"shop{i}.graf", (x - 2.6, FRONT + 0.01, 1.2), (0.9, 1.1), M("graffiti1" if i == 2 else "graffiti2"),
                 facing="+Y")
    if i == 7:  # scaffolding on the upper storeys
        for k in range(5):
            gb_.box(f"scaf.v{k}", (x - 2.8 + k * 1.4, FRONT + 0.9, 7.5), (0.06, 0.06, 7), M("rail", metal=0.6))
        for z in (4.5, 7.0, 9.5):
            gb_.box(f"scaf.h{z}", (x, FRONT + 0.9, z), (5.8, 0.06, 0.06), M("rail", metal=0.6))
            gb_.box(f"scaf.p{z}", (x, FRONT + 0.9, z - 0.05), (5.8, 0.9, 0.05), M("plywood"))
    # "For Lease" signs in a few upper windows
    if i in (3, 8):
        gb_.plane(f"shop{i}.forlease", (x + 1.8, FRONT + 0.03, 8.6), (1.0, 0.6), M("lease"), facing="+Y")
        gb_.text(f"shop{i}.forlease.t", "FOR LEASE", 0.14, M("sign"), (x + 1.8, FRONT + 0.05, 8.6), facing="+Y")
    # interior light (warm by day in the eatery; the Dev's shop at night)
    lt = gb_.empty(f"shop{i}.light.ctl", (x, FRONT - 3, 3.8))
    lt["on"] = 1.0
    ld = __import__("bpy").data.lights.new(f"shop{i}.light", "AREA")
    ld.energy, ld.size, ld.color = 300, 3.0, gb.lin(C["warm"])[:3]
    lo = gb.link(__import__("bpy").data.objects.new(f"shop{i}.light", ld), root)
    lo.location = (x, FRONT - 3, 4.0)
    S.setdefault("shoplights", []).append(lo)
    S.setdefault("doors", []).append(root.matrix_world @ __import__("mathutils").Vector((1.9, 0.5, 0.16)))
    S.setdefault("shopx", []).append(xw)
    return root


def eatery_interior(S):
    x0 = -27
    gb.box("eat.wallpaint", (x0, FRONT - 6.05, 2.1), (5.8, 0.05, 4.1), M("eatery_wall"))
    gb.box("eat.sidepaint", (x0 - 2.88, FRONT - 3.1, 2.1), (0.04, 6.1, 4.1), M("eatery_wall"))
    # the turo-turo: a steam table of pans behind a sneeze guard, along the back; a menu board above
    gb.box("eat.counter", (x0 + 0.6, FRONT - 5.2, 0.5), (4.0, 0.9, 1.0), M("steam", metal=0.7, rough=0.3))
    for k in range(6):
        gb.box(f"eat.pan{k}", (x0 - 0.9 + k * 0.6, FRONT - 5.2, 1.02), (0.5, 0.35, 0.05),
               M("crate" if k % 2 else "lease"))
    gb.box("eat.guard", (x0 + 0.6, FRONT - 4.8, 1.35), (4.0, 0.02, 0.6), gb.mat("glass_a", C["glass"], alpha=0.18))
    gb.plane("eat.menu", (x0 + 0.6, FRONT - 6.0, 3.0), (4.4, 1.3), M("menu"), facing="+Y")
    gb.text("eat.menu.t", "BREAKFAST ALL DAY  ·  SILOG", 0.16, M("sign"), (x0 + 0.6, FRONT - 5.98, 3.3), facing="+Y")
    for k in range(5):
        gb.plane(f"eat.card{k}", (x0 - 1.0 + k * 0.8, FRONT - 5.98, 2.2), (0.6, 0.45), M("plate"), facing="+Y")
    for k in range(2):
        gb.box(f"eat.tray{k}", (x0 + 2.2, FRONT - 4.6 + k * 0.05, 1.0 + k * 0.03), (0.45, 0.35, 0.02), M("tray"))
    # one line of tables along the west wall, black ladder-back chairs either side
    for k in range(3):
        y = FRONT - 1.0 - k * 1.5
        gb.box(f"eat.table{k}", (x0 - 2.3, y, 0.75), (0.8, 1.1, 0.05), M("table"))
        gb.box(f"eat.tleg{k}", (x0 - 2.3, y, 0.37), (0.08, 0.08, 0.74), M("chair"))
        for s in (-1, 1):
            c = gb.box(f"eat.chair{k}{s}", (x0 - 2.3 + s * 0.65, y, 0.45), (0.42, 0.42, 0.05), M("chair"))
            gb.box(f"eat.chairback{k}{s}", (x0 - 2.3 + s * 0.85, y, 0.85), (0.04, 0.42, 0.8), M("chair"))
    # the breakfast at the window table (S01a-S01d, S49): tray, plate, cup, phone, badge, schedule under the saucer
    tx, ty, tz = x0 - 2.3, FRONT - 1.0, 0.78
    S["table"] = (tx, ty, tz)
    gb.box("eat.mytray", (tx + 0.1, ty - 0.1, tz + 0.01), (0.5, 0.36, 0.015), M("phone"))
    gb.cyl("eat.plate", (tx + 0.1, ty - 0.1, tz + 0.025), 0.12, 0.012, M("plate"))
    gb.box("eat.fish", (tx + 0.08, ty - 0.06, tz + 0.04), (0.15, 0.06, 0.02), M("crate"))
    gb.cyl("eat.cup", (tx + 0.3, ty + 0.05, tz + 0.06), 0.04, 0.1, M("plate"))
    gb.cyl("eat.saucer", (tx - 0.2, ty + 0.12, tz + 0.012), 0.08, 0.008, M("plate"))
    gb.box("eat.schedule", (tx - 0.22, ty + 0.15, tz + 0.006), (0.21, 0.28, 0.002), M("paper"))
    gb.box("eat.badge", (tx - 0.25, ty - 0.18, tz + 0.006), (0.1, 0.065, 0.002), M("badge"))
    gb.text("eat.badge.t", "VISITOR", 0.018, M("ink"), (tx - 0.25, ty - 0.18, tz + 0.008), facing="+Z")
    S["badge_text"] = "eat.badge.t"
    ph = gb.empty("phone", (tx + 0.05, ty - 0.35, tz + 0.25))
    gb.box("phone.body", (0, 0, 0), (0.075, 0.008, 0.155), M("phone"), parent=ph)
    gb.plane("phone.screen", (0, -0.005, 0), (0.068, 0.145), M("phonescreen", emit=2.0), parent=ph, facing="-Y")
    S["phone"] = ph
    # the shutter half down for S49 is the eatery's own shutter (shop 0)


def dev_interior(S):
    x0 = -21
    gb.box("dev.counter", (x0, FRONT - 3.5, 0.5), (3.5, 0.8, 1.0), M("table"))
    for k in range(3):
        gb.box(f"dev.shelf{k}", (x0, FRONT - 5.9, 0.9 + k * 0.8), (5.0, 0.4, 0.04), M("trim"))
        for j in range(8):
            gb.box(f"dev.app{k}{j}", (x0 - 2.1 + j * 0.6, FRONT - 5.85, 1.05 + k * 0.8), (0.35, 0.2, 0.25),
                   M("graffiti2" if (j + k) % 3 == 0 else "sign"))
    gb.box("dev.adder", (x0 + 0.6, FRONT - 3.4, 1.07), (0.35, 0.3, 0.14), M("ceohood"))
    tape = gb.box("dev.tape", (x0 + 0.6, FRONT - 3.2, 1.0), (0.08, 0.01, 0.01), M("tape"))
    S["tape0"] = tape
    cal = gb.empty("dev.calendar", (x0 + 2.86, FRONT - 3.0, 2.2))  # 3 cm off the plaster (-18.11): not in it
    gb.plane("dev.cal.board", (0, 0, 0), (0.6, 0.8), M("paper"), parent=cal, facing="-X")
    S["calendar"] = cal
    gb.text("dev.est", "est. 2008", 0.2, M("ink"), (x0 - 0.8, FRONT + 0.03, 3.38), facing="+Y")


# the handset hangs on its cord from the boot under the housing's left side; a portable cassette recorder is taped to
# the post's street face beside it, wired to a pickup on the handset, the tape in it (the human, M4 v7)
HANDSET_PIVOT = (-31.7, -8.365, 1.13)  # the cord's boot (props.payphone: housing local (-0.2, 0.185, -0.37))
HANDSET_DROP = 0.38  # the handset's centre below the boot
RECORDER = (-31.5, -8.498, 0.92)  # its centre: 19 x 5.5 x 27 cm (a real one at 1.5x, like the tape), back on the post
CASS_REST = (RECORDER[0], RECORDER[1] + 0.0075, RECORDER[2] + 0.035)  # in the recorder's well, label out


def corner(S):
    pp = gb.empty("payphone", (-31.5, -8.6, 0))
    gb.box("payphone.post", (0, 0, 0.9), (0.15, 0.15, 1.8), M("steam", metal=0.7, rough=0.4), parent=pp)
    gb.box("payphone.box", (0, 0.05, 1.5), (0.45, 0.25, 0.7), M("steam", metal=0.7, rough=0.4), parent=pp)
    gb.box("payphone.hood", (0, 0.1, 1.95), (0.6, 0.45, 0.06), M("trim"), parent=pp)
    if FINAL:
        gb.box("payphone.sign", (0, 0.1, 2.08), (0.55, 0.4, 0.18), gb.mat("payphone.sign", "#dfe8f0",
               emit=gb.LOOK["lights"]["payphone_sign"]), parent=pp)
        gb.text("payphone.sign.t", "PHONE", 0.09, gb.mat("payphone.ink", "#1b2a3a"), (0, 0.31, 2.08), facing="+Y",
                parent=pp)
        pl = __import__("bpy").data.lights.new("payphone.light", "POINT")
        pl.energy, pl.color, pl.shadow_soft_size = 40, (0.85, 0.92, 1.0), 0.3
        gb.link(__import__("bpy").data.objects.new("payphone.light", pl)).location = (-31.5, -8.2, 1.9)
    hs = gb.empty("handset", HANDSET_PIVOT)  # its origin at the boot, so it swings from there
    gb.cyl("handset.body", (0, 0, -HANDSET_DROP), 0.035, 0.22, M("ink"), parent=hs)
    gb.cyl("handset.cord", (0, 0, -0.135), 0.006, 0.27, M("ink"), parent=hs)
    rc = gb.empty("recorder", RECORDER)
    gb.box("recorder.body", (0, 0, 0), (0.19, 0.055, 0.27), M("ink"), parent=rc)
    door = gb.empty("recorder.door", (0, 0.0275, -0.0175), parent=rc)  # hinged at the well's bottom edge
    gb.box("recorder.door.glass", (0, 0.001, 0.0525), (0.16, 0.002, 0.105), gb.mat("glass_a", C["glass"], alpha=0.18),
           parent=door)
    ctl = gb.empty("rec.ctl", (0, 0, 0))
    # the REC light on the recorder, its own softer glow: at S03's 0.5 m, the windows' strength (40) blew it out
    gb.sphere("recorder.rec", (0.06, 0.03, 0.098), 0.006, gb.glow_mat("rec.handset", C["rec"], 5.0, ctl, "on"), parent=rc)
    S["handset"], S["rec"], S["recorder_door"] = hs, ctl, door
    cas = gb.box("cassette", CASS_REST, (0.1, 0.015, 0.065), M("ink"))
    S["cassette"] = cas
    # streetlights: the one with the coin meter at the corner, others down the block
    S["lamps"] = []
    for k, (x, y, side) in enumerate([(-25, -6.6, 1), (-5, -6.6, 1), (15, -6.6, 1), (35, -6.6, 1),
                                      (-15, 6.6, -1), (25, 6.6, -1)]):
        gb.cyl(f"lamp{k}.pole", (x, y, 3.0), 0.08, 6.0, M("trim"))
        gb.box(f"lamp{k}.arm", (x, y + side * 1.0, 6.0), (0.1, 2.0, 0.1), M("trim"))
        ctl = gb.empty(f"lamp{k}.ctl", (x, y, 0))
        ctl["on"] = 1.0
        gb.box(f"lamp{k}.head", (x, y + side * 2.0, 5.9), (0.3, 0.6, 0.12),
               gb.glow_mat(f"lamp{k}", C["streetlamp"], 20.0, ctl, "on"))
        ld = __import__("bpy").data.lights.new(f"lamp{k}.light", "SPOT")
        ld.energy, ld.spot_size, ld.color = (gb.LOOK["lights"]["lamp_w"] if FINAL else 1500), math.radians(110), \
            gb.lin(C["streetlamp"])[:3]
        ld.spot_blend = 0.6
        lo = gb.link(__import__("bpy").data.objects.new(f"lamp{k}.light", ld))
        lo.location = (x, y + side * 2.0, 5.7)
        S["lamps"].append((ctl, lo))
    gb.box("meter", (-25, -6.45, 1.2), (0.2, 0.15, 0.35), M("steam", metal=0.6))
    gb.box("boombox", (-21.8, -6.6, 0.3), (0.6, 0.25, 0.3), M("ink"))
    S["boombox"] = "boombox"


def tower(S):
    x0, x1 = TOWER_X
    y0, y1 = TOWER_Y
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    gb.box("tower.upper", (cx, cy, 6 + 32), (x1 - x0, y1 - y0, 64), M("tower", metal=0.3, rough=0.4))
    ctl = gb.empty("tower.ctl", (cx, cy, 0))
    ctl["lit"] = 1.0
    for z in np.arange(10, 68, 3.0):  # window bands, lit all night
        gb.box(f"tower.band{z:.0f}", (cx, y0 - 0.02, z), (x1 - x0 - 0.6, 0.04, 1.6),
               gb.glow_mat("tower.glass", C["towerglass"], 2.5, ctl, "lit"))
    # the lobby: hollow ground floor with a glass front
    gb.box("lobby.back", (cx, y1 - 6, 3), (x1 - x0, 0.3, 6), M("lobby"))
    gb.box("lobby.ceiling", (cx, (y0 + y1 - 6) / 2 + 0.005, 5.945), (x1 - x0 - 0.02, y1 - 6 - y0 - 0.01, 0.09),
           M("lobby"))  # under the tower (z 6), not into it
    gb.box("lobby.floor", (cx, (y0 + y1 - 6) / 2, 0.16), (x1 - x0, y1 - 6 - y0, 0.02), M("lobby", rough=0.2))
    gb.box("lobby.sideW", (x0, (y0 + y1 - 6) / 2, 3), (0.3, y1 - 6 - y0, 6), M("tower"))
    gb.box("lobby.sideE", (x1, (y0 + y1 - 6) / 2, 3), (0.3, y1 - 6 - y0, 6), M("tower"))
    gb.plane("lobby.glass", (cx, y0, 3.0), (x1 - x0 - 0.3, 6.0), gb.mat("glass_lobby", C["glass"], rough=0.02,
                                                                 alpha=0.06 if FINAL else 0.18), facing="-Y")
    lo = __import__("bpy").data.lights.new("lobby.light", "AREA")
    lo.energy, lo.size, lo.color = (gb.LOOK["lights"]["lobby_w"], 12, gb.lin(C["towerglass"])[:3]) if FINAL else \
        (3000, 12, (1, 0.97, 0.9))
    lobj = gb.link(__import__("bpy").data.objects.new("lobby.light", lo))
    lobj.location = (cx, y0 + 6, 5.8)
    if FINAL:  # the lobby furnished: clean, cold and expensive (style spec: the one clean place on the street)
        white, fin = gb.mat("lobby.white", "#eef1f4", rough=0.25), gb.mat("lobby.fin", "#d5dbe2", rough=0.3)
        strip = gb.mat("lobby.strip", "#e6f2ff", emit=8.0)
        for k, x in enumerate(np.arange(x0 + 0.8, x1 - 0.5, 1.2)):  # vertical fins on the back wall, around the screen
            if not LOBBY_DOOR_X - 4.6 < x < LOBBY_DOOR_X + 4.6:
                gb.box(f"lobby.fin{k}", (x, y1 - 6.25, 3.0), (0.12, 0.2, 5.8), fin)
        for y in (y0 + 2.5, y0 + 6.5, y0 + 10.5):  # light strips in the ceiling
            gb.box(f"lobby.strip{y:.0f}", (cx, y, 5.88), (x1 - x0 - 2, 0.12, 0.04), strip)
        for s_ in (-1, 1):  # planters either side of the throne, clipped round
            px = LOBBY_DOOR_X + s_ * 3.4
            gb.box(f"lobby.planter{s_}", (px, y0 + 7.0, 0.5), (0.9, 0.9, 0.7), white)
            gb.sphere(f"lobby.topiary{s_}", (px, y0 + 7.0, 1.35), 0.55, gb.mat("lobby.leaf", "#2c4a35", rough=0.7))
        gb.box("lobby.desk", (LOBBY_DOOR_X + 8.5, y0 + 4.0, 0.55), (4.0, 0.9, 1.1), white)  # reception, unstaffed
        gb.box("lobby.desk.strip", (LOBBY_DOOR_X + 8.5, y0 + 3.54, 0.25), (3.8, 0.02, 0.05), strip)
        for k in range(4):  # the security gates
            gb.box(f"lobby.gate{k}", (LOBBY_DOOR_X - 7.5 + k * 1.1, y0 + 4.0, 0.5), (0.18, 1.2, 1.0), white)
            gb.box(f"lobby.gateglass{k}", (LOBBY_DOOR_X - 6.95 + k * 1.1, y0 + 4.0, 0.7), (0.9, 0.02, 0.6),
                   gb.mat("glass_lobby", C["glass"], rough=0.02, alpha=0.06))
    # the lobby screen on the back wall (S05, S10, S20): one text object whose body changes per shot
    gb.box("lobby.screen", (LOBBY_DOOR_X, y1 - 6.2, 3.6), (8, 0.1, 3.4), M("ink"))
    S["screen_text"] = gb.text("lobby.screen.t", "", 0.9, M("screen", emit=4.0), (LOBBY_DOOR_X, y1 - 6.28, 3.6),
                               facing="-Y")
    # the shelf of "worse copies" (S05)
    for j in range(6):
        gb.box(f"lobby.copy{j}", (LOBBY_DOOR_X - 5 + j * 0.7, y1 - 6.6, 1.2), (0.4, 0.25, 0.3), M("graffiti2"))
    # the server-rack throne (S18)
    for k in range(3):
        gb.box(f"throne.rack{k}", (LOBBY_DOOR_X - 1 + k, y0 + 7.0, 1.1 + (0.4 if k == 1 else 0)),
               (0.9, 0.9, 2.2 + (0.8 if k == 1 else 0)), M("rack", metal=0.4))
    # the seat at a sitting height (its top 0.93, under the CEO's thighs), on a plinth set back from his shins; it
    # floated at knee height before, and his legs and cape went through it (the human, M4 v7)
    gb.box("throne.seat", (LOBBY_DOOR_X, y0 + 6.22, 0.855), (1.2, 0.66, 0.15), M("capetrim"))
    gb.box("throne.plinth", (LOBBY_DOOR_X, y0 + 6.3, 0.475), (1.0, 0.5, 0.61), M("trim"))
    # the doors and the brick wall that grows over them (S24), with its little door (S25)
    gb.box("lobby.doors", (LOBBY_DOOR_X, y0 - 0.05, 1.4), (3.0, 0.1, 2.8), gb.mat("glass_a", C["glass"], alpha=0.18))
    wall = gb.box("brickwall", (LOBBY_DOOR_X, y0 - 0.3, 0.0), (3.6, 0.35, 3.0), M("brick_new"))
    wall.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 1.5)))
    wall.scale.z = 0.0
    S["brickwall"] = wall
    # the little door (S25), hinged at its left edge (origin on the hinge), over a dark opening 8 mm proud of the wall
    ld = gb.box("brickwall.door", (LOBBY_DOOR_X + 0.5, y0 - 0.5, 0.55), (0.6, 0.06, 0.9), M("trim"))
    ld.data.transform(__import__("mathutils").Matrix.Translation((0.3, 0, 0)))
    S["littledoor"] = ld
    S["littlehole"] = gb.box("brickwall.hole", (LOBBY_DOOR_X + 0.8, y0 - 0.478, 0.55), (0.56, 0.01, 0.86), M("ink"))
    # the balcony with podium and bell (S22, S30)
    gb.box("balcony", (LOBBY_DOOR_X, y0 - 1.25, 8.0), (12, 2.5, 0.3), M("lobby"))
    gb.box("balcony.rail", (LOBBY_DOOR_X, y0 - 2.45, 8.6), (12, 0.08, 0.9), M("glass", rough=0.1))
    gb.box("podium", (LOBBY_DOOR_X, y0 - 1.6, 8.7), (0.8, 0.6, 1.1), M("ink"))
    bell = gb.empty("bell", (LOBBY_DOOR_X + 4, y0 - 1.4, 10.2))
    gb.cyl("bell.body", (0, 0, -0.3), 0.35, 0.5, M("gold", metal=0.9, rough=0.3), parent=bell)
    gb.box("bell.frame", (LOBBY_DOOR_X + 4, y0 - 1.4, 9.3), (0.1, 0.1, 1.9), M("trim"))
    S["bell"] = bell
    banner = gb.box("banner", (LOBBY_DOOR_X, y0 - 2.55, 7.85), (5.0, 0.04, 5.0), M("sign"))
    banner.data.transform(__import__("mathutils").Matrix.Translation((0, 0, -2.5)))
    banner.scale.z = 0.0
    S["banner"] = banner
    # the LED ticker band (S30)
    tk = gb.empty("ticker.ctl", (cx, cy, 0))
    for nm, c, s in (("s", (cx, y0 - 0.13), (x1 - x0 + 0.46, 0.2)), ("n", (cx, y1 + 0.13), (x1 - x0 + 0.46, 0.2)),
                     ("w", (x0 - 0.13, cy), (0.2, y1 - y0 + 0.46)), ("e", (x1 + 0.13, cy), (0.2, y1 - y0 + 0.46))):
        gb.box(f"ticker.{nm}", (c[0], c[1], 13.6), (s[0], s[1], 1.2), gb.glow_mat("ticker", C["ticker"], 10.0, tk, "on"))
    S["ticker"] = tk
    # the rooftop billboard (S31, S44)
    # at the roof's front edge: 2 m back, the roof hid it from the street (S31)
    gb.box("billboard.frame", (cx, y0 + 0.6, 76), (24, 0.6, 10), M("trim"))
    for k in (-8, 0, 8):
        gb.box(f"billboard.leg{k}", (cx + k, y0 + 0.6, 70.5), (0.3, 0.3, 1.5), M("trim"))
    gb.plane("billboard.face", (cx, y0 + 0.28, 76), (23, 9), M("billboard", emit=1.5), facing="-Y")
    S["billboard_text"] = gb.text("billboard.t", "", 1.6, M("ink"), (cx, y0 + 0.2, 76), facing="-Y")


TONES = [  # the brief's "Memorial headstones" (shot, inscription)
    ("S39b", "Apollo\nJune 30, 2023"), ("S39b", "rif is fun\nJune 30, 2023"), ("S39b", "Sync for Reddit\nJune 30, 2023"),
    ("S39b", "BaconReader\nJune 30, 2023"), ("S39b", "Boost for Reddit\nJune 30, 2023"),
    ("S39b", "ReddPlanet\nJune 30, 2023"),
    ("S39c", "Pushshift\nMay 2023"), ("S39c", "BotDefense\n2023"),
    ("S39d", "r/IAmA celebrity AMAs\nJuly 2023"), ("S39d", "Mobile moderation\non r/Blind\nJuly 2023"),
    ("S39d", "Search engines\nother than Google\nJuly 2024"), ("S39d", "Wayback Machine\narchiving\nAugust 2025"),
    ("S39e", "RSS feeds\nNovember 13, 2026"), ("S39e", "Public Data API\n2008 – March 2027"),
    ("S39e", "Logged-out Reddit\n2005 –"),
]


def headstone(name, loc, label, size=1.0, m=None):
    root = gb.empty(name, loc)
    if FINAL:  # settled over the years: a small lean, seeded by name so every render matches
        r = __import__("random").Random(name)
        root.rotation_euler = (r.uniform(-0.05, 0.05), r.uniform(-0.04, 0.04), r.uniform(-0.06, 0.06))
    slab = gb.box(f"{name}.slab", (0, 0, 0.55 * size), (0.9 * size, 0.16 * size, 1.1 * size), m or M("stone"),
                  parent=root)
    top = gb.cyl(f"{name}.top", (0, 0, 1.1 * size), 0.45 * size, 0.16 * size, m or M("stone"), parent=root, axis="Y")
    if FINAL:  # one solid with a smooth arched top (the cylinder read as a polygon and covered the upper letters)
        import mk
        r = 0.45 * size
        arc = [(r * math.cos(a), 0.55 * size + r * math.sin(a)) for a in np.linspace(0, math.pi, 48)]
        k = mk.MK()
        k.prism([(-r, -0.55 * size), (r, -0.55 * size)] + arc, 0.16 * size, m or M("stone"))
        slab.data = k.mesh(f"{name}.stone")
        top.data = mk.empty_mesh(f"{name}.top.none")  # not hide_render: the visibility keys would show it again
    if label:
        # big enough to read on a phone (brief, "Memorial headstones"): ~0.15 m capitals on a 0.9 m stone
        ts = 0.12 * size if label.count("\n") > 1 else 0.155 * size
        if not FINAL:
            gb.text(f"{name}.t", label, ts, M("ink"), (0, -0.085 * size, 0.7 * size), facing="-Y", parent=root)
            return root
        # the final look: the letters cut into the face (a boolean), their cut a darker, rougher stone; the line
        # shrunk to fit inside the stone's margins
        import bpy
        t = gb.text(f"{name}.t", label, ts, gb.mat("stone.cut", "#1d1b19", rough=0.95), (0, -0.08 * size, 0.7 * size),
                    facing="-Y", parent=root, extrude=0.005 * size)
        bpy.context.view_layer.update()
        fit = min(1.0, 0.76 * size / max(t.dimensions.x, 1e-6), 0.62 * size / max(t.dimensions.y, 1e-6))
        t.scale = (fit, fit, 1.0)
        bpy.context.view_layer.update()
        me = bpy.data.meshes.new_from_object(t.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        cut = gb.link(bpy.data.objects.new(f"{name}.cut", me), root)
        cut.matrix_parent_inverse = t.matrix_parent_inverse
        cut.location, cut.rotation_euler, cut.scale = t.location, t.rotation_euler, t.scale
        bpy.data.objects.remove(t)
        bo = slab.modifiers.new("engrave", "BOOLEAN")
        bo.operation, bo.solver, bo.object = "DIFFERENCE", "EXACT", cut
        bo.material_mode = "TRANSFER"
        bo.use_self, bo.use_hole_tolerant = True, True  # glyphs overlap and are not always closed
        bpy.context.view_layer.update()  # applied once here: evaluated per frame it quadrupled the render time
        baked = bpy.data.meshes.new_from_object(slab.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        slab.modifiers.remove(bo)
        slab.data = baked
        bpy.data.objects.remove(cut)
    return root


def park(S):
    x0, x1, y0, y1 = -32, -10, 10.5, 27
    # the final look lays parkdress.py's lawn (0.0405 up) over this: its top drops 12 mm under the lawn so they don't z-fight
    gb.box("park.ground", ((x0 + x1) / 2, (y0 + y1) / 2, 0.014 if FINAL else 0.02), (x1 - x0, y1 - y0, 0.028 if FINAL else 0.04),
           M("grass"))
    for x in np.arange(x0, x1 + 0.01, 2.0):  # front fence with a gate gap
        if -22.5 < x < -19.5:
            continue
        gb.box(f"fence.p{x:.0f}", (x, y0, 0.9), (0.06, 0.06, 1.8), M("fence"))
    for sx0, sx1 in ((x0, -22), (-20, x1)):
        for z in (0.5, 1.6):
            gb.box(f"fence.r{sx0}{z}", ((sx0 + sx1) / 2, y0, z), (sx1 - sx0, 0.04, 0.04), M("fence"))
    for x, side in ((x0, "w"), (x1, "e")):
        for z in (0.5, 1.6):
            gb.box(f"fence.{side}{z}", (x, (y0 + y1) / 2, z), (0.04, y1 - y0, 0.04), M("fence"))
    # the shoebox coffin with its tiny robot, on two crates
    gb.box("coffin.stand", (-21, 13.8, 0.3), (0.9, 0.5, 0.6), M("crate"))
    gb.box("coffin", (-21, 13.8, 0.68), (0.7, 0.35, 0.16), M("coffin"))
    gb.box("coffin.bot", (-21, 13.8, 0.78), (0.3, 0.14, 0.06), M("goodbot"))
    S["coffin"] = (-21, 13.8, 0.76)
    notes = []
    for k in range(10):  # "good bot" notes stuck on the coffin (S39a)
        n = gb.box(f"note{k}", (-21.3 + (k % 5) * 0.14, 13.62, 0.66 + (k // 5) * 0.07), (0.1, 0.005, 0.07), M("sign"))
        notes.append(n)
    S["notes"] = notes
    S["stone_goodbot"] = headstone("stone.goodbot", (-21, 15.0, 0.04), "Here lies a good bot.\nIt worked for free.", 0.8)
    # the ban-list headstones behind the coffin (S35): small stones that appear in rows
    S["banstones"] = [headstone(f"ban{k}", (-24.5 + (k % 12) * 0.62, 16.0 + (k // 12) * 0.55, 0.04), "", 0.3)
                      for k in range(48)]
    gb.box("doghouse", (-18.4, 11.6, 0.5), (1.0, 1.1, 1.0), M("doghouse"))
    gb.box("doghouse.roof", (-18.4, 11.6, 1.1), (1.2, 1.3, 0.2), M("trim"))
    gb.box("doghouse.door", (-18.4, 11.04, 0.4), (0.45, 0.02, 0.6), M("ink"))
    gb.text("doghouse.sign", "BOT DEFENSE", 0.11, M("sign"), (-18.4, 11.0, 0.85), facing="-Y")
    # good bots with lanterns along the fence (S34, S37)
    S["goodbots"] = []
    for k in range(8):
        x = -30 + k * 1.2 if k < 6 else -15 + (k - 6) * 1.2
        if FINAL:
            import chars
            root = chars.goodbot(f"goodbot{k}", (x, 11.3, 0.04))
        else:
            root = gb.empty(f"goodbot{k}", (x, 11.3, 0.04))
            gb.box(f"goodbot{k}.body", (0, 0, 0.22), (0.26, 0.2, 0.3), M("goodbot"), parent=root)
            gb.box(f"goodbot{k}.head", (0, 0, 0.47), (0.2, 0.18, 0.16), M("goodbot"), parent=root)
        ctl = gb.empty(f"goodbot{k}.ctl", (0, 0, 0), parent=root)
        ctl["on"] = 1.0
        gb.sphere(f"goodbot{k}.lantern", (0.2, -0.12, 0.35), 0.07, gb.glow_mat(f"lantern{k}", C["lantern"], 25.0, ctl, "on"),
                  parent=root)
        S["goodbots"].append((root, ctl))
    # the cemetery (S39a-S39e): stones per the brief's table
    S["stones"] = {}
    pos = {"S39b": [(-31.0 + k * 1.1, 18.8) for k in range(6)],
           "S39c": [(-28.0, 21.0), (-24.5, 21.5)],
           "S39d": [(-15.6, 19.0), (-14.2, 19.6), (-15.2, 20.6), (-13.6, 21.0)],
           "S39e": [(-15.4, 24.0), (-13.4, 24.0), (-11.6, 25.6)]}
    used = {k: 0 for k in pos}
    for shot, label in TONES:
        x, y = pos[shot][used[shot]]
        used[shot] += 1
        S["stones"].setdefault(shot, []).append(headstone(f"stone.{shot}.{used[shot]}", (x, y, 0.04), label, 1.0))
    for k, (x, y) in enumerate(pos["S39e"][:2]):  # freshly dug plots
        gb.box(f"plot{k}", (x, y - 1.2, 0.12), (0.9, 1.9, 0.2), M("dirt"))
    gb.box("grave.hole", (-11.6, 24.3, 0.045), (0.9, 1.9, 0.01), M("silhouette"))
    gb.box("grave.mound", (-10.7, 24.3, 0.25), (0.6, 1.9, 0.45), M("dirt"))
    sh = gb.empty("shovel", (-10.5, 23.2, 0.0))
    gb.box("shovel.handle", (0, 0, 0.7), (0.04, 0.04, 1.2), M("plywood"), parent=sh)
    gb.box("shovel.blade", (0, 0, 0.1), (0.22, 0.03, 0.28), M("rail", metal=0.8), parent=sh)
    sh.rotation_euler.y = 0.25
    # the field of 144,926 tiny markers (BotDefense's bans), behind its stone: one mesh of small upright plates
    n_side_x, n_side_y = 761, 191  # 145,351 slots; the first 144,926 are used
    xs = np.linspace(-31.2, -17.0, n_side_x)
    ys = np.linspace(22.2, 26.6, n_side_y)
    if FINAL:  # blocks of markers with narrow aisles between, so the field reads as rows from a low camera
        def aisled(a, b, n, per, gap):
            k = np.arange(n)
            blocks = k // per
            nb = blocks.max()
            step = (b - a - nb * gap) / (n - 1)
            return a + k * step + blocks * gap
        xs = aisled(-31.2, -17.0, n_side_x, 64, 0.14)
        ys = aisled(22.2, 26.6, n_side_y, 24, 0.12)
    gx, gy = np.meshgrid(xs, ys)
    gx, gy = gx.ravel()[:144926], gy.ravel()[:144926]
    w, h = 0.008, 0.028
    hh = np.full_like(gx, h)
    lean = np.zeros_like(gx)
    if FINAL:  # so the field reads as markers, not a slab: each a little taller or shorter, nudged and leaning
        rng = np.random.default_rng(144926)
        gx = gx + rng.uniform(-0.006, 0.006, len(gx))
        gy = gy + rng.uniform(-0.008, 0.008, len(gy))
        hh = h * rng.uniform(0.6, 1.5, len(gx))
        w = 0.0045
        lean = rng.uniform(-0.006, 0.006, len(gx))
    v = np.zeros((len(gx) * 4, 3), np.float32)
    v[0::4] = np.c_[gx - w, gy, np.full_like(gx, 0.04)]
    v[1::4] = np.c_[gx + w, gy, np.full_like(gx, 0.04)]
    v[2::4] = np.c_[gx + w + lean, gy, 0.04 + hh]
    v[3::4] = np.c_[gx - w + lean, gy, 0.04 + hh]
    import bpy
    me = bpy.data.meshes.new("markers")
    me.vertices.add(len(v))
    me.vertices.foreach_set("co", v.ravel())
    nf = len(gx)
    me.loops.add(nf * 4)
    me.loops.foreach_set("vertex_index", np.arange(nf * 4, dtype=np.int32))
    me.polygons.add(nf)
    me.polygons.foreach_set("loop_start", np.arange(0, nf * 4, 4, dtype=np.int32))
    me.update(calc_edges=True)
    me.materials.append(gb.mat("markers.final", "#c9c4ba", rough=0.9) if FINAL else M("stone"))
    gb.link(bpy.data.objects.new("markers", me))
    S["park"] = (x0, x1, y0, y1)
    if FINAL:  # moonlight over the park and cemetery: a big, cool, soft area light, so the stones read at night
        import bpy
        ld = bpy.data.lights.new("park.moonfill", "AREA")
        ld.energy, ld.size, ld.color = gb.LOOK["lights"]["park_fill_w"], 18, (0.62, 0.72, 1.0)
        lo = gb.link(bpy.data.objects.new("park.moonfill", ld))
        lo.location, lo.rotation_euler = ((x0 + x1) / 2, 15, 11), (math.radians(-25), 0, 0)


# ---------------------------------------------------------------- characters (stand-ins)

def person(name, loc, body, extra=None, h=1.75, rot_z=0.0, head=None):
    if FINAL:
        import chars
        return chars.person(name, loc, body, extra=extra, h=h, rot_z=rot_z, head=head)
    """A stand-in figure: body cylinder, head, and a jaw box on the face (-Y side) for grey-box lip sync. Faces -Y
    before rot_z."""
    root = gb.empty(name, loc)
    root.rotation_euler.z = rot_z
    gb.cyl(f"{name}.body", (0, 0, h * 0.4), 0.22, h * 0.8, M(body), parent=root)
    hd = gb.sphere(f"{name}.head", (0, 0, h * 0.89), 0.13, M(head or "skin"), parent=root)
    jaw = gb.box(f"{name}.jaw", (0, -0.12, h * 0.85), (0.1, 0.03, 0.08), M("ink"), parent=root)
    jaw.scale.z = 0.05
    for side in (-1, 1):
        gb.cyl(f"{name}.arm{side}", (side * 0.28, 0, h * 0.55), 0.06, h * 0.45, M(body), parent=root)
    if extra:
        extra(root, name)
    root["jaw"] = jaw.name
    return root


def dev(loc, rot_z=0.0, name="dev", pose="stand"):
    if FINAL:
        import chars
        return chars.dev(loc, rot_z=rot_z, name=name, pose=pose)
    def ex(root, n):
        gb.box(f"{n}.apron", (0, -0.21, 0.75), (0.34, 0.03, 0.6), M("apron"), parent=root)
        gb.box(f"{n}.belt", (0, 0, 0.92), (0.48, 0.48, 0.08), M("ink"), parent=root)
        gb.sphere(f"{n}.hood", (0, 0.05, 1.58), 0.16, M("hoodie"), parent=root)
    return person(name, loc, "hoodie", ex, rot_z=rot_z)


def ceo(loc, rot_z=0.0, name="ceo"):
    if FINAL:
        import chars
        return chars.ceo(loc, rot_z=rot_z, name=name)
    def ex(root, n):
        c = gb.cyl(f"{n}.cape", (0, 0.06, 0.8), 0.32, 1.3, M("cape"), parent=root)
        gb.box(f"{n}.capetrim", (0, 0.06, 1.42), (0.62, 0.62, 0.08), M("capetrim"), parent=root)
        gb.sphere(f"{n}.hood", (0, 0.05, 1.58), 0.16, M("ceohood"), parent=root)
    return person(name, loc, "ceohood", ex, rot_z=rot_z)


def mod(loc, k, rot_z=0.0, broom=True, name=None, pose="stand"):
    if FINAL:
        import chars
        return chars.mod(loc, k, rot_z=rot_z, broom=broom, name=name, pose=pose)
    name = name or f"mod{k}"
    if pose == "kneel":  # the grey-box's kneel: sunk to the knees
        loc = (loc[0], loc[1], loc[2] - 0.45)

    def ex(root, n):
        gb.box(f"{n}.vest", (0, 0, 0.95), (0.47, 0.47, 0.5), M("vest"), parent=root)
        gb.text(f"{n}.vest.t", "MOD", 0.1, M("ink"), (0, -0.245, 1.0), facing="-Y", parent=root)
        if broom:
            gb.cyl(f"{n}.broom", (0.35, -0.1, 0.75), 0.02, 1.4, M("plywood"), parent=root)
            gb.box(f"{n}.bristle", (0.35, -0.1, 0.06), (0.35, 0.08, 0.12), M("crate"), parent=root)
    return person(name, loc, "modbody", ex, rot_z=rot_z)


def vip(loc, k, rot_z=0.0, name=None):
    if FINAL:
        import chars
        return chars.vip(loc, k, rot_z=rot_z, name=name)
    name = name or f"vip{k}"
    root = gb.empty(name, loc)
    root.rotation_euler.z = rot_z
    gb.box(f"{name}.body", (0, 0, 0.85), (0.5, 0.32, 1.0), M("vip", metal=0.5, rough=0.4), parent=root)
    gb.box(f"{name}.legs", (0, 0, 0.18), (0.36, 0.22, 0.36), M("vip", metal=0.5, rough=0.4), parent=root)
    gb.box(f"{name}.head", (0, 0, 1.55), (0.32, 0.28, 0.3), M("vip", metal=0.5, rough=0.4), parent=root)
    gb.box(f"{name}.eye", (0, -0.15, 1.58), (0.22, 0.02, 0.05), M("screen", emit=5.0), parent=root)
    gb.box(f"{name}.badge", (0.12, -0.17, 1.1), (0.12, 0.01, 0.08), M("gold", metal=0.8, rough=0.3), parent=root)
    gb.box(f"{name}.case", (0.34, -0.05, 0.45), (0.08, 0.4, 0.3), M("ink"), parent=root)
    return root


def hypeman(loc):
    if FINAL:
        import chars
        return chars.hypeman(loc)
    root = gb.empty("hypeman", loc)
    gb.cyl("hypeman.body", (0, 0, 0.8), 0.24, 1.6, M("silhouette"), parent=root)
    gb.sphere("hypeman.head", (0, 0, 1.7), 0.15, M("silhouette"), parent=root)
    return root


def build():
    S = {}
    street(S)
    for i, (x, sign, kind) in enumerate(SHOPS):
        shopfront(S, i, x, sign, kind)
    for k, (x, sign, kind) in enumerate(NORTH_SHOPS):
        shopfront(S, len(SHOPS) + k, x, sign, kind, north=True)
    import bpy
    bpy.context.view_layer.update()
    for i, win, name in UPPER_SIGNS:
        w = bpy.data.objects[f"shop{i}.{win}"]
        gb.text(f"shop{i}.{win}.sign", name, 0.13 if len(name) < 16 else 0.09, M("ink"), (0, 0.03, -0.5), facing="+Y",
                parent=w)
    S["n_south"] = len(SHOPS)
    if FINAL:
        import grunge
        grunge.build(S, {(i, win) for i, win, _ in UPPER_SIGNS} | {(3, "win12"), (8, "win12")})
    eatery_interior(S)
    dev_interior(S)
    corner(S)
    tower(S)
    park(S)
    if FINAL:  # the detail pass (the human's note on M4: "pretty much all of the scenes need more detail")
        import detail
        detail.run(detail.SET, S)
    return S
