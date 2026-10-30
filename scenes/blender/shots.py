"""M3 shot staging: one camera per shot ID, the stand-ins each shot needs, and the gags keyed from the timing map.

Every shot's time span comes from timing/timing_map.json (the song) and config/bookends.json (pre-roll before the
track, post-roll after it). A camera is keyed by fractions of its shot: [(0, loc, target), (1, loc, target)] moves
linearly through the shot; one key holds still. Stand-ins are made per shot and shown only during it, so each shot
stages its own action without disturbing the others. The gags that need the beat or a word (shutters, downvotes,
lanterns, bell) are keyed to the timing map's beats and words. Overlays (the brief's JS column) are not drawn here:
the assembler burns them in as labelled placeholders.

Grey-box blocking for the M3 gate ("approve framing and timing"); look comes at M4.
"""
import math
import random

import bpy
import numpy as np

import block as B
import gb

TM = gb.TM
F = gb.F


def spans():
    """Shot ID -> (t0, t1) in song seconds, in edit order (pre-roll negative, post-roll past the audio)."""
    out, t = {}, -gb.PRE
    for sid, d in gb.BOOK["preroll"].items():
        out[sid] = (t, t + d)
        t += d
    timed = [s for s in TM["shots"] if s["t"] is not None]
    for s in timed:
        out[s["id"]] = (s["t"], s["end"])
    out["S01d"] = (out["S01d"][0], out["S02"][0])  # the pre-roll's last shot runs to the S01e cut
    t = TM["duration_s"]
    for sid, d in gb.BOOK["postroll"].items():
        out[sid] = (t, t + d)
        t += d
    out.pop("S01e", None)  # the match cut itself: a cut, not a shot with length (S01d -> S02)
    return dict(sorted(out.items(), key=lambda kv: kv[1][0]))


SP = None
CAMS = []  # (frame, camera object)


def cam(sid, keys, lens=35.0, t0=None, t1=None, shake=0.0):
    a, b = SP[sid]
    a = a if t0 is None else t0
    b = b if t1 is None else t1
    name = f"cam.{sid}" + ("" if t0 is None else f".{t0:.2f}")
    c = gb.camera(name, lens)
    tgt = gb.empty(f"{name}.target")
    con = c.constraints.new("TRACK_TO")
    con.target, con.track_axis, con.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
    if len(keys) == 1:
        c.location, tgt.location = keys[0][1], keys[0][2]
    else:
        gb.key_vec(c, "location", [(F(a + fr * (b - a)), loc) for fr, loc, _ in keys], interp="BEZIER")
        gb.key_vec(tgt, "location", [(F(a + fr * (b - a)), t) for fr, _, t in keys], interp="BEZIER")
    if shake:  # handheld: a slow wobble, deterministic
        for i in range(3):
            m = gb.fcurve(c, "location", i).modifiers.new("NOISE")
            m.scale, m.strength, m.phase = 14, shake, 3.1 * i + 1
            m.use_restricted_range = True
            m.frame_start, m.frame_end = F(a), F(b)
    CAMS.append((F(a), c))
    return c


def only(o, sid, t1=None):
    a, b = SP[sid]
    gb.show_between(o, a, b if t1 is None else t1)
    for ch in o.children_recursive:
        gb.show_between(ch, a, b if t1 is None else t1)
    return o


def inherit_visibility():
    """Children made after their parent was keyed (lettering on a truck, an eye on a bot) take its shown span."""
    def vis(o):
        return {fc.data_path: fc for fc in gb.fcurves(o) if fc.data_path in ("hide_render", "hide_viewport")}
    for o in bpy.data.objects:
        if vis(o):
            continue
        p = o.parent
        while p is not None and not vis(p):
            p = p.parent
        if p is None:
            continue
        for path, src in vis(p).items():
            gb.keys(o, path, [(kp.co[0], kp.co[1], "CONSTANT") for kp in src.keyframe_points], interp="CONSTANT")


def during(o, t0, t1):
    gb.show_between(o, t0, t1)
    for ch in o.children_recursive:
        gb.show_between(ch, t0, t1)
    return o


def sing(fig, sid, tag="lead"):
    a, b = SP[sid]
    gb.mouth(bpy.data.objects[fig["jaw"]], a, b, tag)


def walk(o, sid, p0, p1, bob=0.04):
    a, b = SP[sid]
    gb.key_vec(o, "location", [(F(a), p0), (F(b), p1)])
    # a small step bob on every beat
    gb.keys(o, "delta_location", [(F(t), bob if k % 2 else 0.0) for k, t in enumerate(gb.beats_between(a, b))],
            index=2, interp="BEZIER")


# ---------------------------------------------------------------- the light: day (pre-roll), night (the song on)

def light(S, final=False):
    sc = bpy.context.scene
    w = bpy.data.worlds.new("sky")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    sc.world = w
    day, night = (0.55, 0.7, 0.95, 1), (0.012, 0.018, 0.04, 1)
    for i in range(4):
        gb.keys(w.node_tree, 'nodes["Background"].inputs[0].default_value',
                [(0, day[i], "CONSTANT"), (F(0.14), night[i], "CONSTANT")], index=i, interp="CONSTANT")
    gb.keys(w.node_tree, 'nodes["Background"].inputs[1].default_value',
            [(0, 1.0, "CONSTANT"), (F(0.14), 1.0, "CONSTANT")], interp="CONSTANT")
    sun = bpy.data.lights.new("sun", "SUN")
    so = gb.link(bpy.data.objects.new("sun", sun))
    so.rotation_euler = (math.radians(50), 0, math.radians(200))
    gb.keys(sun, "energy", [(0, 4.0, "CONSTANT"), (F(0.14), 0.0, "CONSTANT")], interp="CONSTANT")
    moon = bpy.data.lights.new("moon", "SUN")
    moon.color = (0.6, 0.7, 1.0)
    mo = gb.link(bpy.data.objects.new("moon", moon))
    mo.rotation_euler = (math.radians(55), 0, math.radians(-30))
    moon_e = gb.LOOK["lights"]["moon"] if final else 0.35
    if final:
        moon.color = gb.lin(gb.LOOK["palette"]["night"])[:3]
        moon.color = tuple(0.35 + 0.65 * c / max(moon.color) for c in moon.color)
        night = gb.lin(gb.LOOK["palette"]["night"])
        night = tuple(c * gb.LOOK["lights"]["night_sky"] for c in night[:3]) + (1,)
        for i in range(4):
            gb.keys(w.node_tree, 'nodes["Background"].inputs[0].default_value',
                    [(0, day[i], "CONSTANT"), (F(0.14), night[i], "CONSTANT")], index=i, interp="CONSTANT")
        # the haze, so lamp cones and neon read in the air: in a bounded box, not the world volume (Eevee treats a
        # world volume as infinite, and it swallowed the sun and the moon entirely)
        hm = bpy.data.materials.new("haze")
        hm.use_nodes = True
        nt = hm.node_tree
        nt.nodes.remove(nt.nodes["Principled BSDF"])
        vol = nt.nodes.new("ShaderNodeVolumePrincipled")
        vol.inputs["Density"].default_value = gb.LOOK["haze_density"]
        nt.links.new(vol.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
        gb.box("haze", (0, 0, 30), (300, 300, 60), hm)
        import detail
        detail.sky(w)
    gb.keys(moon, "energy", [(0, 0.0, "CONSTANT"), (F(0.14), moon_e, "CONSTANT")], interp="CONSTANT")
    # by day the street lamps, upper windows and neon are off; the shops' interiors are lit
    for ctl, lo in S["lamps"]:
        gb.keys(ctl, '["on"]', [(0, 0.0, "CONSTANT"), (F(0.14), 1.0, "CONSTANT")], interp="CONSTANT")
        gb.keys(lo.data, "energy", [(0, 0.0, "CONSTANT"), (F(0.14), 1500.0, "CONSTANT")], interp="CONSTANT")


# ---------------------------------------------------------------- the gags

def shutters_slam(S, t0, t1, order, aim=None):
    """Slam the shutters in `order` (shop indices) from t0 to t1; each slam takes 3 frames; each shop's neon lights as
    its shutter lands. Even steps, or with aim=(x0, x1) (the tracking camera's aim moving from x0 to x1 over the shot)
    each shop slams as the aim passes it, so the slams land in frame; shops the aim never reaches go first."""
    n = len(order)
    times = [t0 + (t1 - t0) * (k + 0.5) / n for k in range(n)]
    if aim:
        x0, x1 = aim
        ahead = [i for i in order if not min(x0, x1) <= S["shopx"][i] <= max(x0, x1)]
        times = []
        for i in order:
            if i in ahead:
                f = 0.03 + 0.12 * ahead.index(i) / max(1, len(ahead))
            else:
                f = 0.15 + 0.8 * (S["shopx"][i] - x0) / (x1 - x0)
            times.append(t0 + (t1 - t0) * f)
    for i, t in zip(order, times):
        sh, ne = S["shutters"][i], S["neon"][i]
        S["slam"].setdefault(i, []).append((t, 1.0))
        S["neon_on"].setdefault(i, []).append((t, 1.0))
    return times


def west_last(S):
    """Every shop, east to west, so the eatery (the westmost) comes down last."""
    return sorted(range(len(S["shutters"])), key=lambda i: -S["shopx"][i])


def flush_shutters(S):
    for i, sh in enumerate(S["shutters"]):
        ev = sorted(S["slam"].get(i, []))
        pts = [(0, 0.0)]
        for t, v in ev:
            prev = pts[-1][1]
            pts += [(F(t) - 3, prev), (F(t), v)]
        gb.keys(sh, "scale", pts, index=2)
        ne = S["neon"][i]
        ev = sorted(S["neon_on"].get(i, []))
        pts = [(0, 0.0, "CONSTANT")] + [(F(t), v, "CONSTANT") for t, v in ev]
        gb.keys(ne, '["on"]', pts, interp="CONSTANT")


def stage(S):
    global SP
    SP = spans()
    S["slam"], S["neon_on"] = {}, {}
    sh_x = [x for x, _, _ in B.SHOPS]
    tx, ty, tz = S["table"]

    # ---- pre-roll: the eatery on a sunny morning (S01a-S01d)
    cam("S01a", [(0, (-27, 4, 3.0), (-27, -10, 2.0)), (0.55, (-27, -8.0, 1.8), (-28.6, -11, 1.0)),
                 (1, (-28.2, -9.9, 1.3), (tx, ty, tz))], lens=28)
    for k, (dx, dy) in enumerate(((0.7, -2.6), (-0.4, -3.5), (1.5, -4.3))):  # customers (the busy morning)
        only(B.person(f"cust{k}", (-27 + dx, B.FRONT + dy, 0.16), "stucco2", rot_z=math.pi), "S01a", t1=SP["S01d"][1])
    ph = S["phone"]
    a, b = SP["S01b"]
    gb.key_vec(ph, "location", [(F(a), (tx + 0.05, ty - 0.33, tz + 0.25)), (F(SP["S01c"][0]), (tx + 0.05, ty - 0.33, tz + 0.25)),
                                (F(SP["S01c"][0] + 1.5), (tx + 0.05, ty - 0.45, tz + 0.05)),
                                (F(SP["S01d"][0]), (tx - 0.05, ty - 0.45, tz + 0.2)),
                                (F(SP["S01d"][1] - 0.8), (tx - 0.05, ty - 0.45, tz + 0.2)),
                                (F(SP["S01d"][1] - 0.1), (tx - 0.3, ty - 0.7, tz - 0.3))])
    gb.keys(ph, "rotation_euler", [(F(a), math.radians(-35))], index=0)
    cam("S01b", [(0, (tx + 0.05, ty - 0.46, tz + 0.33), (tx + 0.08, ty - 0.08, tz))], lens=26)
    cam("S01c", [(0, (tx + 0.25, ty - 0.55, tz + 0.45), (tx, ty - 0.1, tz)),
                 (1, (tx - 0.35, ty - 0.4, tz + 0.35), (tx - 0.22, ty + 0.12, tz))], lens=35)
    cam("S01d", [(0, (tx - 0.05, ty - 0.62, tz + 0.32), (tx - 0.05, ty - 0.45, tz + 0.2)),
                 (1, (tx - 0.1, ty - 0.75, tz + 0.4), (tx - 0.2, ty - 0.5, tz + 0.05))], lens=40)

    # lobby screen and rooftop billboard: one text object per shot that shows something
    for sid, body in (("S05", "NEW! OUR OWN APP"), ("S10", "BLACKMAIL"), ("S20", "TRAFFIC  \\_/")):
        only(gb.text(f"screen.{sid}", body, 0.8, B.M("screen", emit=4.0), (B.LOBBY_DOOR_X, 23.72, 3.6), facing="-Y"), sid)
    for sid, body in (("S31", "People found this helpful."), ("S44", "Reply below.  |")):
        only(gb.text(f"billboard.{sid}", body, 3.0 if sid == "S31" else 1.6, B.M("ink"), (9, B.TOWER_Y[0] + 0.2, 76),
                     facing="-Y"), sid)
    for j in range(6):  # the lobby's display of worse copies, by the glass (S05)
        gb.box(f"lobby.front_copy{j}", (-3.5 + j * 0.7, 13.0, 1.0), (0.4, 0.25, 0.3), B.M("graffiti2"))
    gb.box("lobby.front_table", (-1.75, 13.0, 0.45), (4.4, 0.8, 0.7), B.M("trim"))

    # ---- intro (S02-S03): the dead payphone, handset dangling; the REC light
    hs = S["handset"]
    cam("S02", [(0, (-20, 4, 4.0), (-31.5, -8.6, 1.4)), (1, (-27.5, -3.2, 2.2), (-31.5, -8.6, 1.1))], lens=30)
    gb.keys(hs, "rotation_euler", [(F(t), 0.08 * math.sin(t * 2.2)) for t in np.arange(0, 22, 0.5)], index=1,
            interp="BEZIER")
    beat_in = [b for a, b in TM["drum_dropouts"] if b < 12][-1]  # the full beat's entry (0:09.70)
    k_in = (beat_in - SP["S03"][0]) / (SP["S03"][1] - SP["S03"][0])
    cam("S03", [(0, (-31.45, -7.95, 0.95), (-31.5, -8.42, 0.86)), (k_in, (-31.45, -8.1, 0.93), (-31.5, -8.42, 0.86)),
                (1, (-24, 1.5, 3.5), (-22, -9, 2.5))], lens=50)
    rec = []
    for a, b in (SP["S03"], SP["S47"]):
        for t in np.arange(a, b, 0.5):
            rec += [(F(t), 1.0, "CONSTANT"), (F(t + 0.25), 0.15, "CONSTANT")]
    gb.keys(S["rec"], '["on"]', [(0, 0.15, "CONSTANT")] + rec, interp="CONSTANT")

    # ---- verse 1 (S04-S13): the Dev's shop
    d4 = only(B.dev((-19.1, -9.2, 0.16), rot_z=math.pi), "S04")
    walk(d4, "S04", (-19.1, -9.0, 0.16), (-19.1, -9.6, 0.16))
    sing(d4, "S04")
    cam("S04", [(0, (-17.0, -4.5, 1.7), (-19.6, -10, 1.6)), (1, (-17.8, -6.0, 1.7), (-19.6, -10, 1.6))], lens=32)
    d5 = only(B.dev((-23.4, -12.2, 0.16), rot_z=math.radians(160)), "S05")
    cam("S05", [(0, (-23.0, -14.8, 1.7), (0, 16, 2.5)), (1, (-22.8, -13.8, 1.7), (0, 16, 2.5))], lens=35)
    # S06: the envelope through the mail slot; the calendar sheds pages
    env = only(gb.box("envelope", (-19.1, -10.1, 1.0), (0.22, 0.01, 0.12), B.M("paper")), "S06")
    a, b = SP["S06"]
    gb.key_vec(env, "location", [(F(a), (-19.1, -9.9, 1.0)), (F(a + 0.3), (-19.1, -10.3, 1.0)),
                                 (F(a + 0.9), (-19.1, -10.6, 0.18))])
    # the pages go two at a time, 0.3 s apart, so each date holds 7 frames (JUNE 1, 7, 13, 19, 25), then the
    # board's ringed 30 holds to the cut; one camera sees the slot and the calendar, pushing in on the calendar
    for k in range(10):
        pg = only(gb.plane(f"calpage{k}", (-18.14, -13.0, 2.2), (0.6, 0.8), B.M("paper"), facing="-X"), "S06")
        tk = a + 0.55 + (k // 2) * 0.3 + (k % 2) * 0.04
        r = 0.35 + 0.25 * (k % 2)  # off to the door side, clear of the next date, and quickly to the floor
        gb.key_vec(pg, "location", [(F(tk), (-18.14, -13.0, 2.2)), (F(tk + 0.1), (-18.22, -13.0 + r * 0.6, 1.95)),
                                    (F(tk + 0.4), (-18.4, -13.0 + r * 1.6, 0.2))])
        gb.key_vec(pg, "rotation_euler", [(F(tk), (0, 0, 0)), (F(tk + 0.4), (-0.9 - r, 0.15, 0.25))])
    cam("S06", [(0, (-21.3, -14.6, 1.55), (-18.6, -11.6, 1.45)), (0.3, (-21.3, -14.6, 1.55), (-18.6, -11.7, 1.5)),
                (1, (-20.2, -13.75, 1.95), (-18.1, -13.0, 2.15))], lens=26)
    # S07-S08: the adding machine; the tape spews and runs out the door, down the sidewalk and over the tracks
    d7 = only(B.dev((-20.4, -13.9, 0.16), rot_z=math.pi), "S07")
    sing(d7, "S07")
    tape = gb.box("tape.run", (0, 0, 0), (0.08, 1.0, 0.005), B.M("tape"))
    tape.data.transform(__import__("mathutils").Matrix.Translation((0, 0.5, 0)))
    during(tape, SP["S07"][0], SP["S13"][1])
    a7, b8 = SP["S07"][0], SP["S08"][1]
    gb.key_vec(tape, "location", [(F(a7), (-20.4, -13.2, 1.07)), (F(SP["S08"][0]), (-19.1, -10.4, 0.17))])
    gb.keys(tape, "scale", [(F(a7), 0.01), (F(SP["S08"][0]) - 1, 3.0), (F(SP["S08"][0]), 1.0), (F(b8), 14.0)], index=1)
    cam("S07", [(0, (-19.0, -12.4, 1.5), (-20.4, -13.6, 1.0))], lens=30)
    cam("S08", [(0, (-17.5, -9.0, 1.2), (-19.1, -8, 0.2)), (1, (-14.5, 2.5, 3.5), (-19.1, -2, 0.0))], lens=24)
    # S09: the tape stapled to his door as an eviction notice
    only(gb.plane("notice", (-19.1, -9.9, 1.4), (0.5, 0.7), B.M("tape"), facing="+Y"), "S09", t1=SP["S27"][1])
    d9 = only(B.dev((-18.3, -8.8, 0.16), rot_z=math.pi * 0.85), "S09")
    sing(d9, "S09")
    cam("S09", [(0, (-17.3, -6.9, 1.6), (-19.1, -10, 1.4))], lens=35)
    # S10: the tower lobby: a figure on the phone, back to camera; the screen flashes BLACKMAIL
    fig = only(B.ceo((9, 14.0, 0.17), rot_z=math.pi, name="ceo10"), "S10")
    cam("S10", [(0, (9, 4.0, 2.0), (9, 20, 2.5)), (1, (9, 6.0, 2.0), (9, 20, 2.5))], lens=35)
    # S11-S13: the payphone tape
    # S11: he reaches into the handset (1.3 s), pulls the tape and holds it up to us, label out, for the rest of the
    # line (2 s); S12 opens on it held up close, then pulls back as it goes into the boombox and the windows open
    a, b = SP["S11"]
    tm = a + 1.3
    d11 = B.dev((-31.5, -7.85, 0.16), name="dev11", pose="reach")
    gb.show_between(d11, a, tm)
    for ch in d11.children_recursive:
        gb.show_between(ch, a, tm)
    d11h = B.dev((-31.5, -7.85, 0.16), rot_z=math.pi, name="dev11h", pose="hold")  # turned round to show us
    gb.show_between(d11h, tm, b)
    for ch in d11h.children_recursive:
        gb.show_between(ch, tm, b)
    sing(d11, "S11")
    sing(d11h, "S11")
    def held(fig, loc):  # the tape gripped in the raised mitten, its lower edge in the fist, toward the lens (+Y)
        h = bpy.data.objects.get(f"{fig.name}.hand1")
        if h is None:  # grey-box figures have no hands
            return (loc[0] - 0.226, loc[1] + 0.254, loc[2] + 1.745)
        bpy.context.view_layer.update()
        p = h.matrix_world.translation
        return (p.x, p.y + 0.07, p.z + 0.015)
    held11 = held(d11h, (-31.5, -7.85, 0.16))
    d12 = only(B.dev((-22.4, -7.4, 0.16), rot_z=math.pi, name="dev12", pose="hold"), "S12")
    held12 = held(d12, (-22.4, -7.4, 0.16))
    cas = S["cassette"]
    a12, b12 = SP["S12"]
    path = [(F(a), (-31.5, -8.38, 0.88)), (F(a + 0.45), (-31.5, -8.38, 0.88)), (F(tm) - 1, (-31.47, -8.3, 0.98)),
            (F(tm), held11), (F(b) - 1, held11), (F(a12), held12), (F(a12 + 1.5), held12),
            (F(a12 + 1.9), (-21.8, -6.6, 0.5)), (F(SP["S13"][0]), (-21.8, -6.6, 0.5))]
    for i in range(3):  # a cut between S11 and S12 (and a hand-off at tm): constant across those
        gb.keys(cas, "location", [(f, v[i], "CONSTANT" if f in (F(tm) - 1, F(b) - 1) else "BEZIER") for f, v in path],
                index=i, interp="BEZIER")
    c11 = cam("S11", [(0, (-30.6, -7.1, 1.35), (-31.45, -8.35, 0.95)), (0.33, (-30.6, -7.1, 1.35), (-31.45, -8.35, 0.98)),
                      (0.5, (-31.0, -6.3, 1.8), held11), (1, (-31.1, -6.15, 1.82), held11)], lens=40)
    gb.keys(c11.data, "lens", [(F(a), 40.0), (F(tm), 40.0), (F(tm + 0.5), 50.0)], interp="BEZIER")
    sing(d12, "S12")
    a, b = SP["S12"]
    k = 0
    for i in range(len(S["windows"])):  # windows open up and down the block, once the tape's in the boombox
        for (ctl, _), t in zip(S["windows"][i], [a + 1.8 + 0.018 * (i * 6 + j) for j in range(6)]):
            if ctl["lit"] < 0.5:
                gb.keys(ctl, '["lit"]', [(0, 0.0, "CONSTANT"), (F(t), 1.0, "CONSTANT"), (F(SP["S15"][0]), 0.0, "CONSTANT"),
                                         (F(SP["S18"][0]), 1.0, "CONSTANT")], interp="CONSTANT")
    c12 = cam("S12", [(0, (-22.55, -5.85, 1.9), held12), (0.42, (-22.6, -5.6, 1.88), held12),
                      (0.62, (-23.2, -3.0, 1.5), (-21.9, -7.0, 0.8)), (1, (-24.5, 1.0, 1.4), (-21, -9, 4.5))], lens=50)
    gb.keys(c12.data, "lens", [(F(a), 50.0), (F(a + 1.3), 50.0), (F(a + 2.0), 24.0)], interp="BEZIER")
    mg = only(gb.cyl("magnifier", (-24, -6.7, 0.35), 0.12, 0.02, B.M("glass"), axis="Y"), "S13")
    a, b = SP["S13"]
    gb.key_vec(mg, "location", [(F(a), (-26.0, -7.0, 0.35)), (F(b), (-19.0, -7.0, 0.35))])
    only(gb.box("tape.sidewalk", (-22.5, -7.0, 0.16), (9.0, 0.08, 0.004), B.M("tape")), "S13")
    cam("S13", [(0, (-26.5, -5.8, 0.9), (-25.5, -7.0, 0.2)), (1, (-19.5, -5.8, 0.9), (-18.5, -7.0, 0.2))], lens=35)

    # ---- hook 1 (S14-S17): shutters slam east to west, the eatery last; the block goes dark
    a, b = SP["S14"]
    shutters_slam(S, a, b, west_last(S), aim=(20, -30))
    cam("S14", [(0, (30, -2.0, 2.2), (20, -10, 2.4)), (1, (-24, -2.0, 2.2), (-30, -10, 2.4))], lens=24)
    cam("S15", [(0, (-60, 25, 30), (-5, -9, 2)), (1, (-58, 24, 32), (-3, -9, 2))], lens=24)
    off = SP["S15"][0]
    for ctl, lo in S["lamps"]:
        lamp_on = [(0, 0.0, "CONSTANT"), (F(0.14), 1.0, "CONSTANT"), (F(off), 0.0, "CONSTANT"),
                   (F(SP["S17"][0] + 1.8), 1.0, "CONSTANT")]
        gb.keys(ctl, '["on"]', lamp_on, interp="CONSTANT")
        gb.keys(lo.data, "energy", [(f, v * 1500, i) for f, v, i in lamp_on], interp="CONSTANT")
    for lo in S["shoplights"]:
        gb.keys(lo.data, "energy", [(0, 300, "CONSTANT"), (F(off), 0.0, "CONSTANT"), (F(SP["S47"][0]), 60.0, "CONSTANT")],
                interp="CONSTANT")
    for wins in S["windows"]:
        for ctl, _ in wins:
            if ctl.animation_data is None:
                gb.keys(ctl, '["lit"]', [(0, ctl["lit"], "CONSTANT"), (F(off), 0.0, "CONSTANT"),
                                         (F(SP["S18"][0]), ctl["lit"], "CONSTANT")], interp="CONSTANT")
    cam("S16", [(0, (-3.3, -4.0, 4.4), (-3, -10, 4.6)), (1, (-3.2, -6.5, 4.5), (-3, -10, 4.6))], lens=40)
    a, b = SP["S17"]
    for k in range(4):
        m = only(B.mod((-23 + k * 1.6, -2.5 + (k % 2) * 1.5, 0.0), k, rot_z=math.pi / 2), "S17")
        walk(m, "S17", (-23 + k * 1.6, -2.5 + (k % 2) * 1.5, 0.0), (-24.5 + k * 1.6, -2.5 + (k % 2) * 1.5, 0.0))
    only(B.mod((-25, -7.0, 0.16), 9, rot_z=math.pi), "S17")
    lamp0, lo0 = S["lamps"][0]
    fl = [(F(a + 1.2), 1.0), (F(a + 1.35), 0.0), (F(a + 1.5), 1.0), (F(a + 1.6), 0.2), (F(a + 1.8), 1.0)]
    pts = [(0, 0.0, "CONSTANT"), (F(0.14), 1.0, "CONSTANT"), (F(off), 0.0, "CONSTANT")] + \
          [(f, v, "CONSTANT") for f, v in fl]
    gb.keys(lamp0, '["on"]', pts, interp="CONSTANT")
    gb.keys(lo0.data, "energy", [(f, v * 1500, i) for f, v, i in pts], interp="CONSTANT")
    cam("S17", [(0, (-18, 3.5, 2.6), (-25, -6, 1.5)), (1, (-19.5, 2.5, 3.2), (-25, -6.6, 3.5))], lens=28)

    # ---- verse 2 (S18-S25): the CEO
    c18 = only(B.ceo((9, 17.0, 0.95), name="ceo18"), "S18")
    sing(c18, "S18")
    cam("S18", [(0, (9, 1.0, 2.0), (9, 17, 1.9)), (1, (9, 7.5, 2.0), (9, 17, 2.0))], lens=35)
    for k in range(6):
        m = only(B.mod((-2 + k * 1.6, 7.6, -0.45), 20 + k, rot_z=math.pi, broom=True), "S19")
    cam("S19", [(0, (3.0, 1.5, 1.4), (4, 9, 1.0)), (1, (6.0, 1.5, 1.6), (6, 9, 1.0))], lens=28)
    c20 = only(B.ceo((7.5, 16.0, 0.17), name="ceo20"), "S20")
    sing(c20, "S20")
    ball = only(gb.sphere("ball", (8.2, 15.6, 0.3), 0.12, B.M("lease")), "S20")
    gb.keys(ball, "location", [(F(t) + d, z) for t in gb.beats_between(*SP["S20"]) for d, z in ((0, 0.3), (6, 1.1))],
            index=2, interp="BEZIER")
    cam("S20", [(0, (8.5, 4.5, 2.0), (8.5, 20, 2.6))], lens=30)
    a, b = SP["S21"]
    van = only(gb.box("van", (-20, -3.6, 1.1), (5.0, 2.1, 2.2), B.M("van")), "S21")
    gb.text("van.t", "LOCKSMITH", 0.4, B.M("ink"), (0, 1.06, 0.2), facing="+Y", parent=van)
    gb.keys(van, "location", [(F(a), 6.0), (F(a + 1.0), -20.0)], index=0)
    for i in (2, 3, 4):
        S["slam"].setdefault(i, []).append((a + 1.0 + 0.3 * (i - 2), 0.0))
        S["neon_on"].setdefault(i, []).append((a + 1.0 + 0.3 * (i - 2), 0.0))
        only(B.mod((sh_x[i] + 1.9, B.FRONT - 0.4, 0.16), 40 + i, rot_z=math.pi, broom=False, name=f"mannequin{i}"), "S21")
    cam("S21", [(0, (-5, 8.0, 3.2), (-11, -10, 1.4))], lens=24)
    c22 = only(B.ceo((9, 9.4, 8.15), name="ceo22"), "S22")
    sing(c22, "S22")
    dv = gb.words_between(*SP["S22"], word="downvote")
    for k, w in enumerate(dv):
        arr = only(gb.box(f"arrow{k}", (9, 9.4, 14), (1.2, 0.3, 1.6), B.M("lease")), "S22")
        gb.key_vec(arr, "location", [(F(w["start"]) - 6, (8 + k * 1.2, 9.0, 16)), (F(w["start"]), (8.6 + k * 0.6, 9.0, 9.5)),
                                     (F(w["start"]) + 8, (8.6 + k * 0.6, 8.0, 8.4))])
    cam("S22", [(0, (9, -4, 4.5), (9, 9.4, 9.2)), (1, (9, -2.5, 5.0), (9, 9.4, 9.2))], lens=30)
    c23 = only(B.ceo((9, 9.4, 8.15), name="ceo23"), "S23")
    sing(c23, "S23")
    for k, i in enumerate((1, 2, 3, 5)):
        v = only(B.vip((sh_x[i] + 1.9, B.FRONT + 0.7, 0.16), 10 + k, rot_z=math.pi), "S23")
        only(gb.cyl(f"hose{k}", (sh_x[i] + 1.9, B.FRONT + 0.4, 1.0), 0.06, 0.8, B.M("ink"), axis="Y"), "S23")
    cam("S23", [(0, (14, 7.5, 9.8), (-8, -10, 1.0)), (1, (14, 7.0, 10.3), (-14, -10, 1.0))], lens=26)
    c24 = only(B.ceo((10.5, 9.4, 0.16), name="ceo24", rot_z=math.pi), "S24")
    a, b = SP["S24"]
    gb.keys(S["brickwall"], "scale", [(0, 0.0), (F(a), 0.0), (F(b), 1.0)], index=2)
    cam("S24", [(0, (9, 1.0, 1.7), (9, 10.5, 1.6)), (1, (9, 2.5, 1.7), (9, 10.5, 1.6))], lens=30)
    a, b = SP["S25"]
    gb.keys(S["littledoor"], "location", [(0, 10.0 - 0.5 - 0.0), (F(a), 10.0), (F(a + 0.4), 10.0 - 0.6)], index=1)
    gb.show_from(S["littledoor"], SP["S24"][0])  # it belongs to the wall: unseen until the wall goes up
    c25 = only(B.ceo((9.8, 9.3, 0.16), name="ceo25"), "S25")
    v25 = only(B.vip((9.8, 8.0, 0.16), 30, rot_z=math.pi), "S25")
    case = only(gb.box("case25", (9.8, 8.6, 0.9), (0.4, 0.1, 0.3), B.M("ink")), "S25")
    gb.key_vec(case, "location", [(F(a + 0.6), (9.8, 8.4, 0.9)), (F(a + 1.2), (9.8, 9.0, 0.9))])
    cam("S25", [(0, (12.5, 5.5, 1.5), (9.6, 9.5, 0.9))], lens=35)

    # ---- hook 2 (S26): S14-S17's cameras, padlocked and "under new management"; per line of the hook
    lines = [ln for ln in TM["lines"] if ln["section"] == "Hook 2"]
    reuse = [("S14", [(0, (30, -2.0, 2.2), (20, -10, 2.4)), (1, (-24, -2.0, 2.2), (-30, -10, 2.4))], 24),
             ("S15", [(0, (-60, 25, 30), (-5, -9, 2)), (1, (-58, 24, 32), (-3, -9, 2))], 24),
             ("S38", [(0, (-21.5, 7.8, 1.3), (-21, 13, 0.6)), (1, (-19.5, 8.3, 1.1), (-18.4, 11.6, 0.6))], 35),
             ("S39", [(0, (-17.0, 3.5, 1.4), (-18.4, 11, 0.8)), (1, (-15.5, 3.5, 1.4), (-10, 10, 1.2))], 28)]
    starts = [SP["S26"][0]] + [ln["start"] for ln in lines[1:]] + [SP["S26"][1]]
    for (src, keys, lens), t0, t1 in zip(reuse, starts, starts[1:]):
        cam("S26", keys, lens=lens, t0=t0, t1=t1)
    shutters_slam(S, starts[0], starts[1], west_last(S), aim=(20, -30))
    for k in range(3):  # "Now the wolves got a contract": the VIP bots stroll past the doghouse (S39's staging)
        v = during(B.vip((-19 - k * 1.3, 8.0, 0.16), 90 + k, rot_z=math.pi / 2), starts[3], starts[4])
        gb.key_vec(v, "location", [(F(starts[3]), (-19 - k * 1.3, 8.0, 0.16)), (F(starts[4]), (-12 - k * 1.3, 8.0, 0.16))])
    for lock, unm in S["padlocks"]:
        gb.show_from(lock, SP["S26"][0])
        gb.show_between(unm, SP["S26"][0], SP["S33"][1])
    for pad, txt in S["keypads"]:
        gb.show_from(pad, SP["S48"][0])
        gb.show_from(txt, SP["S48"][0])

    # ---- verse 3 (S27-S33)
    d27 = only(B.dev((-26, -8.4, 0.16), rot_z=-math.pi / 2), "S27")
    walk(d27, "S27", (-26, -8.4, 0.16), (-20, -8.4, 0.16), bob=0.08)
    sing(d27, "S27")
    for k in range(6):
        m = only(B.mod((-24 + k * 1.3, -7.0 + (k % 3) * 0.4, 0.16), 50 + k, rot_z=math.pi * (0.4 + 0.1 * k),
                       broom=k % 2 == 0), "S27")
        if k in (1, 4):  # the human-looking bots in the crowd: same vest, a faint blue eye line
            gb.box(f"botmod{k}.eye", (0, -0.13, 1.57), (0.12, 0.01, 0.02), B.M("screen", emit=1.5), parent=m)
    cam("S27", [(0, (-28.5, -7.8, 1.6), (-24, -8.4, 1.6)), (1, (-22.5, -7.8, 1.6), (-18, -8.4, 1.6))], lens=26,
        shake=0.06)
    a, b = SP["S28"]
    truck = only(gb.box("truck28", (0, 2.0, 1.6), (7, 2.5, 3.2), B.M("truck")), "S28")
    for k in range(4):
        cr = only(gb.box(f"crate{k}", (-4 + k * 0.9, -7.5, 0.45), (0.8, 0.8, 0.6), B.M("crate")), "S28")
        gb.text(f"crate{k}.t", "COMMENTS\n2005–2023", 0.1, B.M("ink"), (0, 0.41, 0), facing="+Y", parent=cr)
        tk = a + 0.3 + k * 0.4
        gb.key_vec(cr, "location", [(F(tk), (-4 + k * 0.9, -7.5, 0.45)), (F(tk + 0.4), (-3.4, 0.6, 2.0)),
                                    (F(tk + 0.5), (-2.5 + k * 0.5, 2.0, 1.0))])
    cam("S28", [(0, (-9, -3.0, 2.4), (-2.5, -4.5, 0.8))], lens=24)
    a, b = SP["S29"]
    for nm, x0, x1, y in (("SEARCH", -20, 4.5, 3.5), ("CHAT", -26, -10, 3.5)):
        tr = only(gb.box(f"truck.{nm}", (x0, y, 1.5), (6, 2.4, 3.0), B.M("truck")), "S29")
        gb.text(f"truck.{nm}.t", nm, 0.7, B.M("ink"), (0, 1.21, 0.3), facing="+Y", parent=tr)
        gb.keys(tr, "location", [(F(a), x0), (F(b), x1)], index=0)
    av = only(gb.box("archivevan", (12, 3.5, 1.0), (4.0, 2.0, 2.0), B.M("van")), "S29")
    gb.text("archivevan.t", "ARCHIVE", 0.4, B.M("ink"), (0, 1.01, 0.2), facing="+Y", parent=av)
    gb.keys(av, "location", [(F(a), 12.0), (F(a + 1.0), 12.0), (F(b), 20.0)], index=0)
    only(B.person("bouncer", (11.5, 9.6, 0.16), "ink", rot_z=-math.pi / 2), "S29")
    cam("S29", [(0, (-2, -5.0, 2.5), (6, 8, 1.6))], lens=24)
    c30 = only(B.ceo((12.0, 9.4, 8.15), name="ceo30"), "S30")
    a, b = SP["S30"]
    gb.keys(S["bell"], "rotation_euler", [(F(t) + d, v) for t in gb.beats_between(a, b) for d, v in ((0, 0.4), (8, -0.3))],
            index=0, interp="BEZIER")
    gb.keys(S["banner"], "scale", [(0, 0.0), (F(a + 0.4), 0.0), (F(a + 1.6), 1.0)], index=2)
    gb.keys(S["ticker"], '["on"]', [(0, 0.0, "CONSTANT"), (F(a + 0.4), 1.0, "CONSTANT")], interp="CONSTANT")
    gb.text("banner.t", "IPO", 1.5, B.M("ink"), (B.LOBBY_DOOR_X, 10.5 - 2.6, 5.6), facing="-Y")
    only(bpy.data.objects["banner.t"], "S30", t1=TM["duration_s"])
    cam("S30", [(0, (10, -3.5, 1.8), (12, 9, 10.2)), (1, (9, -5.0, 1.6), (9, 9, 13.0))], lens=24)
    # S31: the notes are on PAWN's shutter (down since S14) at eye height, close enough to read; they hold 1.2 s,
    # peel one at a time 0.22 s apart and arc into the funnel on the truck in the near lane, the camera following;
    # then up to the billboard, zooming in so its line reads
    a, b = SP["S31"]
    rn = random.Random(31)
    mouth = (2.0, -4.6, 4.35)  # over the truck's roof hatch (1 m behind its centre); the truck in the near lane
    for k in range(10):
        p0 = (-4.35 + (k % 5) * 0.68 + rn.uniform(-0.08, 0.08), B.FRONT + 0.175, (2.05 if k < 5 else 1.55) + rn.uniform(-0.07, 0.07))
        n = only(gb.plane(f"sticky{k}", p0, (0.3, 0.3), B.M("sign"), facing="+Y"), "S31")
        tk = a + 1.0 + (k * 7 % 10) * 0.16  # not in reading order
        mid = ((p0[0] + mouth[0]) / 2, (p0[1] + mouth[1]) / 2, max(p0[2], mouth[2]) + 0.5)
        gb.key_vec(n, "location", [(F(tk), p0), (F(tk + 0.15), (p0[0], p0[1] + 0.12, p0[2] + 0.05)),
                                   (F(tk + 0.9), mid), (F(tk + 1.6), mouth), (F(tk + 1.8), (mouth[0], mouth[1], 3.6))],
                   interp="BEZIER")
        gb.key_vec(n, "rotation_euler", [(F(tk), (0, 0, 0)), (F(tk + 0.15), (-0.7, 0, 0)),
                                         (F(tk + 1.6), (-1.4, rn.uniform(-1, 1), rn.uniform(-2, 2)))])
        for i in range(3):
            gb.keys(n, "scale", [(F(tk + 1.6), 1.0), (F(tk + 1.8), 0.0)], index=i)
    only(gb.box("funnel", (mouth[0], mouth[1], 3.6), (1.4, 1.4, 1.2), B.M("rail", metal=0.7)), "S31")
    only(gb.box("truck31", (mouth[0] + 1.0, mouth[1], 1.5), (7, 2.5, 3.0), B.M("truck")), "S31")
    sl = bpy.data.lights.new("S31.notes.light", "SPOT")  # the streetlight's spill on PAWN's shutter, so the notes read
    sl.energy, sl.spot_size, sl.spot_blend, sl.color = 160.0, math.radians(55), 0.6, (1.0, 0.85, 0.65)
    lo = gb.link(bpy.data.objects.new("S31.notes.light", sl))
    lo.location = (-2.4, -6.4, 4.2)
    lo.rotation_euler = (math.radians(50), 0, math.radians(180 + 8))
    only(lo, "S31")
    bb = (9, B.TOWER_Y[0] + 0.2, 76)
    c31 = cam("S31", [(0, (-2.7, -6.3, 1.75), (-3.0, -9.84, 1.8)), (0.36, (-2.75, -6.6, 1.75), (-3.0, -9.84, 1.8)),
                      (0.47, (-1.0, -8.6, 4.6), (mouth[0], mouth[1], 3.9)),  # craning up to look into the funnel
                      (0.66, (-0.9, -8.7, 4.7), (mouth[0], mouth[1], 3.95)), (0.82, (0, -9.0, 4.0), bb),
                      (1, (0, -9.0, 4.0), bb)], lens=32)
    gb.keys(c31.data, "lens", [(F(a), 32.0), (F(a + 0.8 * (b - a)), 32.0), (F(a + 0.9 * (b - a)), 110.0)], interp="BEZIER")
    for k in range(5):
        only(gb.cyl(f"broomstack{k}", (-8 + k * 0.1, -6.3, 0.85), 0.02, 1.4, B.M("plywood")), "S32")
    only(gb.box("payroll", (-7.4, -6.6, 0.17), (0.24, 0.12, 0.01), B.M("crate")), "S32")
    a, b = SP["S32"]
    band = only(gb.cyl("rubberband", (-7.0, -6.7, 0.9), 0.05, 0.005, B.M("lease")), "S32")
    gb.keys(band, "location", [(F(a + 0.2), 0.9), (F(a + 0.6), 0.17)], index=2)
    cam("S32", [(0, (-6.2, -5.4, 0.9), (-7.5, -6.6, 0.3))], lens=35)
    cx, cy = S["chalk_sq"]
    only(gb.text("yourland", "YOUR LAND", 0.18, B.M("sign"), (cx, cy, 0.155), facing="+Z"), "S33")
    d33 = only(B.dev((cx, cy, 0.16)), "S33")
    sing(d33, "S33")
    cam("S33", [(0, (cx, cy + 2.5, 1.6), (cx, cy, 1.0)), (1, (cx, cy + 5, 20), (cx, cy, 0))], lens=28)

    # ---- the Good Bot eulogy (S34-S39e): the pocket park, then the cemetery
    for k, (root, ctl) in enumerate(S["goodbots"]):
        during(root, SP["S34"][0], SP["S39"][1])
    cam("S34", [(0, (-21, 7.0, 2.2), (-21, 13.8, 0.7)), (1, (-21, 8.5, 1.8), (-21, 13.8, 0.7))], lens=30)
    a, b = SP["S35"]
    for k, st in enumerate(S["banstones"]):
        tk = a + 0.2 + k * (b - a - 0.4) / len(S["banstones"])
        during(st, tk, SP["S39e"][1])
    cam("S35", [(0, (-21, 11.5, 1.6), (-21, 16.5, 0.4)), (1, (-21, 10.8, 2.6), (-21, 16.5, 0.4))], lens=28)
    cam("S36", [(0, (-20.3, 14.1, 0.75), (-21, 15.0, 0.6)), (1, (-20.45, 14.3, 0.7), (-21, 15.0, 0.6))], lens=35)
    a, b = SP["S37"]
    for k, (root, ctl) in enumerate(S["goodbots"]):
        tk = a + 0.3 + k * (b - a - 0.5) / len(S["goodbots"])
        gb.keys(ctl, '["on"]', [(0, 1.0, "CONSTANT"), (F(tk), 0.0, "CONSTANT")], interp="CONSTANT")
    cam("S37", [(0, (-31, 8.5, 1.4), (-24, 11.3, 0.4)), (1, (-25, 8.5, 1.4), (-14, 11.3, 0.4))], lens=28)
    cam("S38", [(0, (-21.5, 7.8, 1.3), (-21, 13, 0.6)), (1, (-19.5, 8.3, 1.1), (-18.4, 11.6, 0.6))], lens=35)
    a, b = SP["S39"]
    for k in range(3):
        v = only(B.vip((-22 + k * 1.5, 8.0, 0.16), 60 + k, rot_z=math.pi / 2), "S39")
        walk(v, "S39", (-19 - k * 1.3, 8.0, 0.16), (-12 - k * 1.3, 8.0, 0.16))
    cam("S39", [(0, (-17.0, 3.5, 1.4), (-18.4, 11, 0.8)), (1, (-15.5, 3.5, 1.4), (-10, 10, 1.2))], lens=28)
    a, b = SP["S39a"]
    for k, n in enumerate(S["notes"]):
        during(n, a + 0.15 + k * (b - a - 0.6) / 10, 1e5)
    cam("S39a", [(0, (-21, 12.2, 1.0), (-21, 13.8, 0.7)), (1, (-21, 9.5, 6.0), (-21, 20, 0.5))], lens=30)
    st = S["stones"]
    cam("S39b", [(0, (-31.3, 16.6, 1.3), (-29.7, 18.8, 0.7)), (1, (-28.3, 16.6, 1.3), (-26.5, 18.8, 0.7))], lens=26)
    cam("S39c", [(0, (-28.0, 18.4, 2.4), (-28.0, 21.0, 0.7)), (0.45, (-27.6, 18.4, 2.4), (-28.0, 21.0, 0.7)),
                 (1, (-24.5, 18.6, 2.6), (-24.5, 23.0, 0.3))], lens=26)
    cam("S39d", [(0, (-17.5, 17.0, 1.6), (-14.6, 20.2, 0.7)), (1, (-16.5, 16.6, 1.5), (-14.6, 20.2, 0.7))], lens=30)
    cam("S39e", [(0, (-17.0, 21.0, 1.6), (-14.4, 23.4, 0.4)), (1, (-11.6, 21.3, 1.7), (-11.6, 25.2, 0.4))], lens=30)
    # S40 is the rewind (F): the assembler builds it from earlier frames; this camera only holds S39e's last view
    cam("S40", [(0, (-11.6, 21.3, 1.7), (-11.6, 25.2, 0.4))], lens=30)

    # ---- verse 4 (S41-S45): back on the corner, the reveal
    for sid in ("S41", "S42", "S43"):
        r = only(B.dev((-29.5, -7.4, 0.16), rot_z=math.radians(200), name=f"rapper.{sid}"), sid)
        sing(r, sid)
    cam("S41", [(0, (-24, 0, 2.2), (-29.5, -7.4, 1.4)), (1, (-25, -2, 1.9), (-29.5, -7.4, 1.4))], lens=30)
    cam("S42", [(0, (-27.6, -4.4, 1.6), (-29.5, -7.4, 1.4))], lens=40)
    cam("S43", [(0, (-28.9, -6.3, 1.6), (-29.5, -7.4, 1.58)), (1, (-29.0, -6.5, 1.6), (-29.5, -7.4, 1.58))], lens=50)
    cam("S44", [(0, (9, -30, 30), (9, 12.5, 76)), (1, (9, -26, 32), (9, 12.5, 76))], lens=45)
    hm = only(B.hypeman((sh_x[6] + 1.9, B.FRONT - 0.3, 0.16)), "S45")
    S["slam"].setdefault(6, []).extend([(SP["S45"][0] - 0.05, 0.0), (SP["S45"][1], 1.0)])
    gb.hide_between(bpy.data.objects["shop6.door"], *SP["S45"])
    bl = bpy.data.lights.new("hype.back", "AREA")
    bl.energy, bl.size, bl.color = 400, 1.5, (1.0, 0.85, 0.6)
    blo = only(gb.link(bpy.data.objects.new("hype.back", bl)), "S45")
    blo.location, blo.rotation_euler = (sh_x[6] + 1.9, B.FRONT - 2.5, 1.5), (math.radians(-90), 0, 0)
    cam("S45", [(0, (sh_x[6] + 1.5, -5.5, 1.5), (sh_x[6] + 1.9, -10, 1.3))], lens=40)

    # ---- outro (S47-S48b): the payphone; the crane over a block of doormen, keypads and REC lights; the open grave
    cam("S47", [(0, (-30.6, -7.4, 1.3), (-31.5, -8.42, 0.9)), (1, (-30.9, -7.7, 1.1), (-31.5, -8.42, 0.9))], lens=40)
    a, b = SP["S48"]
    for k, door in enumerate(S["doors"]):
        north = k >= len(B.SHOPS)
        only(B.vip(tuple(door), 70 + k, rot_z=0.0 if north else math.pi), "S48")
    for wins in S["windows"]:
        for ctl, rec in wins:
            gb.show_from(rec, a)
    for wins in S["windows"]:
        for ctl, rec in wins:
            gb.show_between(rec, a, 1e5)
    cam("S48", [(0, (-29.5, -3.5, 1.8), (-31.5, -8.6, 1.2)), (0.2, (-26, 0, 6), (-20, -10, 3)),
                (0.55, (-8, 2, 14), (5, -10, 4)), (0.8, (-14, 5, 16), (-14, 10, 2)), (1, (-21, 4.0, 14), (-21, 18, 0))],
        lens=24)
    cam("S48a", [(0, (-11.6, 21.6, 1.6), (-11.6, 25.0, 0.5))], lens=35)
    # S48b (the login prompt) and S50 (the end card) are code-drawn cards (JS): the assembler draws placeholders
    cam("S48b", [(0, (-11.6, 21.6, 1.6), (-11.6, 25.0, 0.5))], lens=35)

    # ---- the closing bookend (S49): the eatery's table at night, the shutter half down, the badge EXPIRED
    a, b = SP["S49"]
    S["slam"].setdefault(0, []).append((a - 0.1, 0.5))
    exp = gb.text("eat.badge.expired", "EXPIRED", 0.018, B.M("lease"), (tx - 0.25, ty - 0.18, tz + 0.009), facing="+Z")
    during(exp, a, 1e5)
    during(bpy.data.objects[S["badge_text"]], -1e5, a)
    gb.key_vec(ph, "location", [(F(a - 0.1), (tx + 0.05, ty - 0.3, tz + 0.012))])
    gb.keys(ph, "rotation_euler", [(F(a - 0.1), math.radians(-90))], index=0)
    cam("S49", [(0, (tx + 0.5, ty - 1.0, tz + 0.7), (tx - 0.05, ty - 0.15, tz)),
                (1, (tx + 0.3, ty - 0.75, tz + 0.55), (tx - 0.05, ty - 0.15, tz))], lens=35)
    cam("S50", [(0, (0, 0, -50), (0, 0, -60))], lens=35)  # black: the end card is drawn by the assembler

    flush_shutters(S)
    inherit_visibility()
    for c in [c for _, c in CAMS]:
        c.data.dof.use_dof = False
    sc = bpy.context.scene
    for f, c in sorted(CAMS, key=lambda fc: fc[0]):
        mk = sc.timeline_markers.new(c.name, frame=f)
        mk.camera = c
    sc.camera = CAMS[0][1]
    return SP
