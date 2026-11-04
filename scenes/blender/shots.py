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
from mathutils import Matrix
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


# the tape's run in plan (props.TAPE_PATH's x, y): the S08 camera follows its end. TAPE_S07: how much is out by the
# end of S07 (over the counter edge, onto the floor); TAPE_END: all of it (about 27 m)
TAPE_S07 = 2.6


def _tape_plan():
    import props
    pts, s = [], 0.0
    for (x0, y0, *_), (x1, y1, *_) in zip(props.TAPE_PATH, props.TAPE_PATH[1:]):
        pts.append((s, x0, y0))
        s += math.hypot(x1 - x0, y1 - y0)
    pts.append((s, props.TAPE_PATH[-1][0], props.TAPE_PATH[-1][1]))
    return pts


def tape_at(s):
    pts = _tape_plan()
    for (s0, x0, y0), (s1, x1, y1) in zip(pts, pts[1:]):
        if s <= s1:
            u = (s - s0) / max(s1 - s0, 1e-6)
            return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    return pts[-1][1], pts[-1][2]


TAPE_END = 27.0


def tape_staging(S, SP, ctl):
    """Key how much tape is out (metres along the run, props.tape_run): S07 off the roll from 0.3 s, S08 the rest."""
    a7, b7 = SP["S07"]
    a8, b8 = SP["S08"]
    gb.keys(ctl, '["reveal"]', [(F(a7 + 0.3), 0.0), (F(b7), TAPE_S07), (F(a8 + 0.1), TAPE_S07 + 0.3),
                                (F(b8 - 0.15), S.get("tape_len", TAPE_END) + 0.05)], interp="LINEAR")


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

# the pre-roll's daylight: a dimmer sky fill and a stronger sun, so the morning has shadows and blacks (at sky 1.0,
# sun 4.0 the flat blue fill washed the opener out: the human, "the intro is a little washed out")
DAY_SKY, DAY_SUN, DAY_GLASS = 0.4, 5.5, 0.06


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
            [(0, DAY_SKY, "CONSTANT"), (F(0.14), 1.0, "CONSTANT")], interp="CONSTANT")
    sun = bpy.data.lights.new("sun", "SUN")
    so = gb.link(bpy.data.objects.new("sun", sun))
    so.rotation_euler = (math.radians(50), 0, math.radians(200))
    gb.keys(sun, "energy", [(0, DAY_SUN, "CONSTANT"), (F(0.14), 0.0, "CONSTANT")], interp="CONSTANT")
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
        # by day (the pre-roll) no haze: in the sun it lifted every black (the human: "the intro is a little washed out")
        gb.keys(nt, f'nodes["{vol.name}"].inputs["Density"].default_value',
                [(0, 0.0, "CONSTANT"), (F(0.14), gb.LOOK["haze_density"], "CONSTANT")], interp="CONSTANT")
        import detail
        detail.sky(w)
    # by day the shop glass is clearer: at 0.18 it laid a pale sheet over the push into the eatery (S01a; the human: "the
    # intro is a little washed out"); at night (Act 1, approved) it stays as it was
    ga = bpy.data.materials.get("glass_a")
    if ga and ga.node_tree:
        b = next(n for n in ga.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        a_night = b.inputs["Alpha"].default_value
        gb.keys(ga.node_tree, f'nodes["{b.name}"].inputs["Alpha"].default_value',
                [(0, DAY_GLASS, "CONSTANT"), (F(0.14), a_night, "CONSTANT")], interp="CONSTANT")
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
    # M6: the phone's keys for the opener and for S49 are written together at S49 (gb.keys replaces an F-curve's keys:
    # S49's single key had wiped these, so the phone lay in its S49 pose through the whole opener)
    held = (tx - 0.05, ty - 0.45, tz + 0.2)
    S["phone_loc"] = [(F(a), (tx + 0.05, ty - 0.33, tz + 0.25)), (F(SP["S01c"][0]), (tx + 0.05, ty - 0.33, tz + 0.25)),
                      (F(SP["S01c"][0] + 1.5), (tx + 0.05, ty - 0.45, tz + 0.05)),
                      (F(SP["S01d"][0]), held), (F(SP["S01d"][1] - 0.8), held),
                      (F(SP["S01d"][1] - 0.1), (tx - 0.3, ty - 0.7, tz - 0.3))]
    S["phone_rot"] = [(F(a), math.radians(-35)), (F(SP["S01d"][1] - 0.1), math.radians(-35))]
    # S01b is the phone camera's own view (the camera UI and the photo are the overlay's): the phone is hidden
    for part in ph.children:
        gb.keys(part, "hide_render", [(0, 0.0, "CONSTANT"), (F(a), 1.0, "CONSTANT"), (F(b), 0.0, "CONSTANT")],
                interp="CONSTANT")
    cam("S01b", [(0, (tx + 0.05, ty - 0.46, tz + 0.33), (tx + 0.08, ty - 0.08, tz))], lens=26)
    cam("S01c", [(0, (tx + 0.25, ty - 0.55, tz + 0.45), (tx, ty - 0.1, tz)),
                 (1, (tx - 0.35, ty - 0.4, tz + 0.35), (tx - 0.22, ty + 0.12, tz))], lens=35)
    # S01d: the phone in hand, seen down its screen's normal (the screen faces local -Y; the phone is tilted -35
    # degrees about X), close enough that it fills most of the frame; the hand lowers it to pocket at the end
    n = (0.0, -math.cos(math.radians(35)), math.sin(math.radians(35)))
    eye = tuple(h + 0.42 * k for h, k in zip(held, n))
    cam("S01d", [(0, eye, held), (0.8, (eye[0], eye[1] - 0.02, eye[2] + 0.01), held),
                 (1, (eye[0], eye[1] - 0.05, eye[2] + 0.03), (held[0] - 0.1, held[1] - 0.1, held[2] - 0.12))], lens=40)

    # lobby screen and rooftop billboard: one text object per shot that shows something
    for sid, body in (("S05", "NEW! OUR OWN APP"), ("S10", "HE'S THREATENING US"), ("S20", "TRAFFIC  \\_/")):
        only(gb.text(f"screen.{sid}", body, 0.8, B.M("screen", emit=4.0), (B.LOBBY_DOOR_X, 23.72, 3.6), facing="-Y"), sid)
    for sid, body in (("S31", "People found\nthis helpful."), ("S44", "Reply below.  |")):
        bt = only(gb.text(f"billboard.{sid}", body, 3.0 if sid == "S31" else 1.6, B.M("ink"), (9, B.TOWER_Y[0] + 0.2, 76),
                          facing="-Y"), sid)
        if sid == "S31":  # two lines across 70% of the 23 m face (one line ran edge to edge, stretched out)
            bpy.context.view_layer.update()
            bt.scale = (16.0 / bt.dimensions.x,) * 3
    for j in range(6):  # the lobby's display of worse copies, by the glass (S05)
        gb.box(f"lobby.front_copy{j}", (-3.5 + j * 0.7, 13.0, 1.0), (0.4, 0.25, 0.3), B.M("graffiti2"))
    gb.box("lobby.front_table", (-1.75, 13.0, 0.45), (4.4, 0.8, 0.7), B.M("trim"))

    # ---- intro (S02-S03): the dead payphone, handset dangling; the REC light
    hs = S["handset"]
    cam("S02", [(0, (-20, 4, 4.0), (-31.5, -8.6, 1.4)), (1, (-27.5, -3.2, 2.2), (-31.5, -8.6, 1.1))], lens=30)
    gb.keys(hs, "rotation_euler", [(F(t), 0.04 * math.sin(t * 2.2)) for t in np.arange(0, 22, 0.5)], index=1,
            interp="BEZIER")  # a slow sway from the boot (gentle: the recorder's lead runs to it)
    beat_in = [b for a, b in TM["drum_dropouts"] if b < 12][-1]  # the full beat's entry (0:09.70)
    k_in = (beat_in - SP["S03"][0]) / (SP["S03"][1] - SP["S03"][0])
    # the handset and the recorder taped beside it, then in on the recorder's REC light as the beat comes in
    cam("S03", [(0, (-31.56, -7.8, 1.02), (-31.58, -8.45, 0.94)), (k_in, (-31.5, -7.98, 1.02), (-31.5, -8.47, 0.98)),
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
    # the final look's tape is props.tape_run's ribbon (tape_staging keys how much of it is out): S07 close on the
    # machine as it spews over the counter edge; S08 chases the tape's end out the door, along the sidewalk, over
    # the tracks
    cam("S07", [(0, (-19.55, -12.15, 1.5), (-20.35, -13.05, 1.12)), (1, (-19.5, -11.9, 1.45), (-20.3, -12.7, 0.75))],
        lens=32)
    # S08: from the doorstep as the tape whips out, craning up and back until the whole run shows: along the
    # sidewalk, round the corner and over the tracks (a chase cam blurred it into one more painted line)
    cam("S08", [(0, (-18.3, -8.5, 0.9), (-19.0, -10.3, 0.3)), (0.3, (-19.2, -5.9, 2.6), (-21.5, -8.0, 0.2)),
                (0.65, (-21.0, -3.2, 5.6), (-25.0, -7.4, 0.1)), (1, (-22.6, -1.6, 6.2), (-27.4, -2.6, 0.0))], lens=24)
    # S09: the tape stapled to his door as an eviction notice
    # S09: the tape slapped up on his door (stapled, the total in red marker); he stands aside so it reads
    nt9 = only(gb.plane("notice", (-19.1, -9.9, 1.4), (0.5, 0.7), B.M("tape"), facing="+Y"), "S09", t1=SP["S27"][1])
    a9 = SP["S09"][0]
    for i in range(3):
        gb.keys(nt9, "scale", [(F(a9 + 0.1), 0.0), (F(a9 + 0.25), 1.1), (F(a9 + 0.35), 1.0)], index=i, interp="BEZIER")
    d9 = only(B.dev((-17.95, -9.15, 0.16), rot_z=math.pi * 0.8), "S09")
    sing(d9, "S09")
    cam("S09", [(0, (-18.7, -7.7, 1.55), (-18.9, -10, 1.38)), (1, (-18.75, -7.95, 1.5), (-18.92, -10, 1.38))], lens=35)
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
    rest = B.CASS_REST
    # he flips the recorder's door down, then lifts the tape out of the well
    gb.keys(S["recorder_door"], "rotation_euler", [(0, 0.0), (F(a + 0.15), 0.0), (F(a + 0.42), -1.45)], index=0,
            interp="BEZIER")
    path = [(F(a), rest), (F(a + 0.45), rest), (F(tm) - 1, (rest[0], rest[1] + 0.12, rest[2] + 0.08)),
            (F(tm), held11), (F(b) - 1, held11), (F(a12), held12), (F(a12 + 1.5), held12),
            (F(a12 + 1.9), (-21.8, -6.6, 0.5)), (F(SP["S13"][0]), (-21.8, -6.6, 0.5))]
    for i in range(3):  # a cut between S11 and S12 (and a hand-off at tm): constant across those
        gb.keys(cas, "location", [(f, v[i], "CONSTANT" if f in (F(tm) - 1, F(b) - 1) else "BEZIER") for f, v in path],
                index=i, interp="BEZIER")
    c11 = cam("S11", [(0, (-30.6, -7.1, 1.35), (-31.42, -8.45, 0.95)), (0.33, (-30.6, -7.1, 1.35), (-31.42, -8.45, 0.98)),
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
    # slowly, 2.5 m in the shot, the camera alongside so the printed "0.24 +"s read under the glass
    gb.key_vec(mg, "location", [(F(a + 0.2), (-25.6, -7.72, 0.24)), (F(b - 0.3), (-23.1, -7.72, 0.24))], interp="BEZIER")
    only(gb.box("tape.sidewalk", (-22.5, -7.0, 0.16), (9.0, 0.08, 0.004), B.M("tape")), "S13")
    cam("S13", [(0, (-24.8, -8.55, 0.75), (-25.65, -7.6, 0.17)), (1, (-22.3, -8.55, 0.75), (-23.15, -7.6, 0.17))],
        lens=40)  # from the shop side: the curb's posts were in the way

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
    c18 = only(B.ceo((9, 16.75, 0.17), name="ceo18"), "S18")  # his cape's back clear of the racks (front 17.05)
    sing(c18, "S18")
    cam("S18", [(0, (9, 1.0, 2.0), (9, 17, 1.9)), (1, (9, 7.5, 2.0), (9, 17, 2.0))], lens=35)
    for k in range(6):
        m = only(B.mod((-2 + k * 1.6, 7.6, 0.16), 20 + k, rot_z=math.pi, broom=True, pose="kneel"), "S19")  # on the plaza
    # low, from the side along the row, so the kneel reads (from behind they looked like short people standing)
    cam("S19", [(0, (-5.6, 5.6, 0.95), (3.0, 8.0, 0.65)), (1, (-4.6, 5.4, 1.0), (4.0, 8.0, 0.7))], lens=30)
    c20 = only(B.ceo((7.5, 16.0, 0.17), name="ceo20"), "S20")
    sing(c20, "S20")
    # he dribbles it (the human, M4 v7: "make it look like he's actually dribbling"): the ball hits the floor on each
    # beat; his palm meets it on the way up, rides it down and pushes it off, then rises to meet the next bounce. The
    # arm is its own object, blended to its low pose by a shape key; the mitten and thumb follow the wrist
    import chars
    R, Z0, X0, Y0 = 0.12, 0.17, 7.5, 16.0
    arm = bpy.data.objects.get("ceo20.arm1")
    hi, lo = chars.POSES["dribble"]["arm"][1], chars.DRIBBLE_LOW
    hand_hi, hand_lo = chars.hand_at(hi[1], hi[2]), chars.hand_at(lo[1], lo[2])
    if arm is not None:  # the final look's figures (the grey-box's have no arm objects)
        # the low pose bends this mesh at the shoulder and elbow (two bones, blended over 8 cm at the elbow): the skin
        # modifier adds rings on a longer forearm, so a second skin of the low pose would not line up vertex for vertex
        from mathutils import Vector
        def bone(a, b, a2, b2):
            a, b, a2, b2 = map(Vector, (a, b, a2, b2))
            d, d2 = (b - a).normalized(), (b2 - a2).normalized()
            q, k = d.rotation_difference(d2), (b2 - a2).length / (b - a).length
            def T(v):
                r = v - a
                along = r.dot(d)
                return a2 + q @ (r - along * d) + along * k * d2
            return T, d
        up, _ = bone(hi[0], hi[1], lo[0], lo[1])
        fore, df = bone(hi[1], hi[2], lo[1], lo[2])
        arm.shape_key_add(name="hi")
        low = arm.shape_key_add(name="low")
        for kv in low.data:
            v = Vector(kv.co)
            w = min(1.0, max(0.0, ((v - Vector(hi[1])).dot(df) + 0.04) / 0.08))
            kv.co = up(v) * (1 - w) + fore(v) * w
    def v_at(p):  # the arm, 0 high .. 1 low, over one bounce (p 0 = the ball on the floor)
        if p < 0.45:  # rising to meet it (from the last release at 0.75)
            u = (p + 0.25) / 0.7
            return 0.5 + 0.5 * math.cos(math.pi * min(1.0, u))
        if p < 0.75:  # riding it down and pushing
            u = (p - 0.45) / 0.3
            return 0.5 * u + 0.5 * u * u
        u = (p - 0.75) / 0.7
        return 0.5 + 0.5 * math.cos(math.pi * u)
    def palm(v):  # the palm's underside over the ball (world), and its x, y
        c = [a + (b - a) * v for a, b in zip(hand_hi, hand_lo)]
        return X0 + c[0], Y0 + c[1], Z0 + c[2] - 0.06
    def ball_at(p):
        top_hi, top_lo = palm(0.0)[2], palm(1.0)[2]
        if p < 0.45:  # up off the floor, slowing into his palm
            u = p / 0.45
            z = Z0 + R + (top_hi - 2 * R - Z0) * (1 - (1 - u) ** 2)
            v = 0.0
        elif p < 0.75:
            v = v_at(p)
            z = palm(v)[2] - R
        else:  # pushed off: down to the floor, gathering speed
            u = (p - 0.75) / 0.25
            z = top_lo - R - (top_lo - R - (Z0 + R)) * (0.45 * u + 0.55 * u * u)
            v = 1.0
        x, y, _ = palm(v)
        return x, y, z
    ball = only(gb.sphere("ball", (X0 + hand_hi[0], Y0 + hand_hi[1], Z0 + R), R, B.M("lease")), "S20")
    bt = gb.beats_between(SP["S20"][0] - 1, SP["S20"][1] + 1)
    hand = bpy.data.objects.get("ceo20.hand1")
    thumb = bpy.data.objects.get("ceo20.thumb1")
    for f in range(F(bt[0]), F(bt[-1]) + 1):
        t = f / 24 - 18  # gb.F's inverse
        k = max(i for i, b in enumerate(bt) if b <= t + 1e-9) if t >= bt[0] else 0
        if k >= len(bt) - 1:
            continue
        p = (t - bt[k]) / (bt[k + 1] - bt[k])
        bp = ball_at(p)
        for i in range(3):
            ball.location[i] = bp[i]
            ball.keyframe_insert("location", index=i, frame=f)
        v = v_at(p)
        if arm is not None:
            kb = arm.data.shape_keys.key_blocks["low"]
            kb.value = v
            kb.keyframe_insert("value", frame=f)
        c = [a + (b - a) * v for a, b in zip(hand_hi, hand_lo)]
        for o, off in ((hand, (0, 0, 0)), (thumb, (-0.01, -0.04, 0.015))):
            if o is None:
                continue
            o.location = (c[0] + off[0], c[1] + off[1], c[2] + off[2])
            o.keyframe_insert("location", frame=f)
    cam("S20", [(0, (8.3, 9.6, 1.6), (8.0, 16.5, 1.9)), (1, (8.25, 10.2, 1.6), (8.0, 16.5, 1.9))], lens=30)  # in close
    # enough that the ball and his hand read, the screen's chart over them
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
    # each downvote (two of them) drives a giant arrow tip-first into the balcony floor, one either side of him, where
    # it stays, shuddering: at v5 they fell past along one line and out of frame in a second, and read as one blur
    ARR = [(-1.35, 9.05, 0.12), (1.45, 9.0, -0.1)]  # x off the CEO, y, a lean
    S_ARR, FLOOR = 1.3, 8.15
    for k, w in enumerate(dv):
        dx, y, lean = ARR[k % len(ARR)]
        x = 9 + dx
        arr = only(gb.box(f"arrow{k}", (9, 9.4, 14), (1.2, 0.3, 1.6), B.M("lease")), "S22")
        arr.scale = (S_ARR,) * 3
        zc = FLOOR + 0.8 * S_ARR - 0.12  # the tip 12 cm into the floor
        f0 = F(w["start"])
        gb.key_vec(arr, "location", [(f0 - 6, (x + 0.4 * lean, y, zc + 7.0)), (f0, (x, y, zc)), (f0 + 2, (x, y, zc + 0.04)),
                                     (f0 + 4, (x, y, zc))])
        gb.key_vec(arr, "rotation_euler", [(f0 - 6, (0, lean * 0.5, 0)), (f0, (0, lean, 0)), (f0 + 2, (0.05, lean * 1.6, 0)),
                                           (f0 + 4, (-0.03, lean * 0.8, 0)), (f0 + 6, (0, lean, 0))], interp="BEZIER")
    c22 = cam("S22", [(0, (9, 1.5, 8.9), (9, 9.4, 9.0)), (1, (9, 2.6, 8.9), (9, 9.4, 9.0))], lens=30)
    # the camera shakes as each arrow lands (the human, on the M7 cut: "add camera shake timed with the downvotes
    # landing"): a jolt on the impact frame, then a decaying shudder over half a second; the camera and its target are
    # nudged apart (delta_location: on top of their keys), so the frame both bumps and tips
    impacts = [F(w["start"]) for w in dv]
    rs = random.Random(22)
    jolts = {o: [] for o in ("cam", "tgt")}
    for f0 in impacts:
        for j, amp in enumerate((1.0, -0.75, 0.55, -0.38, 0.25, -0.15, 0.08, -0.03, 0.0)):
            for o, size in (("cam", 0.035), ("tgt", 0.11)):
                jolts[o].append((f0 + j * 1.5, (amp * size * rs.uniform(0.4, 0.9) * (1 if j % 2 else -1),
                                                0.0, -amp * size * rs.uniform(0.8, 1.0))))
    tgt22 = bpy.data.objects["cam.S22.target"]
    for o, ob in (("cam", c22), ("tgt", tgt22)):
        pts = [(impacts[0] - 1, (0.0, 0.0, 0.0))] + jolts[o]
        gb.key_vec(ob, "delta_location", pts, interp="BEZIER")
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
    # S25 (2 s, "so I sold 'em the whole lot"): the CEO has stepped out of the little door, which stands open behind
    # them. Side by side, each turned toward the other and toward the camera (seen side-on, face to face, the bot
    # was cut off at the frame's edge and the exchange didn't read: the human, on the final cut, "face them towards the camera"): the VIP bot holds out the briefcase
    # on its raised arm, the CEO takes it in his left hand and holds out the keys in his right; the bot takes the keys
    # and lowers its arm. Hard stop.
    a, b = SP["S25"]
    gb.keys(S["littledoor"], "rotation_euler", [(F(a) - 1, 0.0, "CONSTANT"), (F(a), -1.9, "CONSTANT")], index=2)
    for o in (S["littledoor"], S["littlehole"]):
        gb.show_from(o, SP["S24"][0])  # they belong to the wall: unseen until the wall goes up
    # the camera is v7's, looking down the sidewalk with the wall on the right and the night street on the left (a
    # frontal camera lost the street and read as daytime: the human, "doesn't convey 'shady night deal'"); they stand
    # across its view, each facing it (PHI) turned TURN toward the other: the bot by the wall, past the little door,
    # the CEO on its arm side (its -x), toward the street
    PHI, TURN, MID = math.pi / 2, 0.6, (10.35, 8.8)
    lat = (math.cos(PHI), math.sin(PHI))
    c25 = only(B.ceo((MID[0] - 0.75 * lat[0], MID[1] - 0.75 * lat[1], 0.16), name="ceo25", rot_z=PHI + TURN), "S25")
    v25 = only(B.vip((MID[0] + 0.75 * lat[0], MID[1] + 0.75 * lat[1], 0.16), 30, rot_z=PHI - TURN), "S25")
    for n in ("vip30.case", "vip30.latch-1", "vip30.latch1"):  # its own case at its side: this one is the deal's
        o = bpy.data.objects.get(n)
        if o:
            o.data = bpy.data.meshes.new(f"{n}.none")
    arm = bpy.data.objects.get("vip30.arm-1")  # the CEO's side
    if arm:  # pivot at the shoulder; raised to hold the case out, lowered once it has the keys
        top = max(v.co.z for v in arm.data.vertices)
        arm.data = arm.data.copy()
        arm.data.transform(__import__("mathutils").Matrix.Translation((0, 0, -top)))
        arm.location.z += top
        gb.keys(arm, "rotation_euler", [(F(a), -1.1), (F(a + 1.45), -1.1), (F(a + 1.85), -0.3)], index=0,
                interp="BEZIER")
    bpy.context.view_layer.update()
    # the shoulder from the bot's own placement (its matrix_world isn't evaluated yet here: it read as the origin)
    from mathutils import Matrix, Vector
    sh = Vector(v25.location) + Matrix.Rotation(v25.rotation_euler.z, 3, "Z") @ Vector(arm.location)
    def vhand(rx):  # the bot's hand (the arm's lower end), for the arm raised rx, turned with the bot
        L = 0.62
        d = Matrix.Rotation(v25.rotation_euler.z, 3, "Z") @ Vector((0.0, L * math.sin(rx), -L * math.cos(rx)))
        return tuple(sh + d)
    hr = bpy.data.objects.get("ceo25.hand1")
    hl = bpy.data.objects.get("ceo25.hand-1")
    pr = hr.matrix_world.translation.copy() if hr else (10.0, 8.88, 1.3)
    pl = hl.matrix_world.translation.copy() if hl else (9.6, 8.92, 1.1)
    up, down = vhand(-1.1), vhand(-0.3)
    case = only(gb.box("case25", (9.8, 8.6, 0.9), (0.4, 0.1, 0.3), B.M("ink")), "S25")
    case.rotation_euler.z = math.pi / 2  # its broad side to the camera, which looks along -x
    gb.key_vec(case, "location", [(F(a), (up[0], up[1], up[2] - 0.17)), (F(a + 0.35), (up[0], up[1], up[2] - 0.17)),
                                  (F(a + 0.8), (pl[0], pl[1], pl[2] - 0.17)), (F(b) + 2, (pl[0], pl[1], pl[2] - 0.17))],
               interp="BEZIER")
    keys25 = only(gb.box("keys25", (0, 0, 0), (0.1, 0.02, 0.2), B.M("gold")), "S25")
    keys25.rotation_euler.z = math.pi / 2  # the ring and keys face-on to the camera
    gb.key_vec(keys25, "location", [(F(a), (pr[0], pr[1], pr[2] - 0.1)), (F(a + 0.85), (pr[0], pr[1], pr[2] - 0.1)),
                                    (F(a + 1.3), (up[0], up[1], up[2] - 0.1)), (F(a + 1.45), (up[0], up[1], up[2] - 0.1)),
                                    (F(a + 1.85), (down[0], down[1], down[2] - 0.1))], interp="BEZIER")
    cam("S25", [(0, (13.9, 8.55, 1.3), (10.35, 8.85, 1.15)), (1, (13.4, 8.6, 1.25), (10.35, 8.85, 1.15))], lens=32)

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
    # S28: the sidewalk auction. The truck at the near curb, its side door rolled up to the sidewalk; a forklift lifts a
    # pallet of four crates (two on two) and drives it into the hold, then backs off; a second lot waits by the sign
    a, b = SP["S28"]
    only(gb.box("truck28", (0, -4.7, 1.6), (7, 2.5, 3.2), B.M("truck")), "S28")  # its -Y side at -5.95, the curb -6.0
    DOOR_X, HOLD_Z, SW = -1.9, 0.64, 0.15  # the door's centre (world x), the hold's floor (props.vehicle's lining), the sidewalk
    y0, y1, y2 = -8.6, -7.05, -7.7  # the forklift's root: start, the pallet all in the hold, backed off
    fl = only(gb.empty("forklift28", (DOOR_X, y0, SW)), "S28")
    gb.box("forklift28.body", (0, 0, 0.6), (1.1, 2.0, 1.2), B.M("vest"), parent=fl)
    car = gb.empty("forklift28.carriage", (0, 1.05, 0.1), parent=fl)
    gb.box("forklift28.forks", (0, 0.5, 0.03), (0.9, 1.0, 0.05), B.M("trim"), parent=car)
    d = b - a  # 3.08 s since it starts a second early (the human's note): the beats as fractions of it, so it slows
    t_hold, t_lift0, t_lift1, t_in, t_set, t_out = a + 0.08 * d, a + 0.1 * d, a + 0.36 * d, a + 0.64 * d, a + 0.7 * d, b
    gb.keys(fl, "location", [(F(a), y0), (F(t_hold), y0), (F(t_in), y1, "LINEAR"), (F(t_set + 0.1), y1),
                             (F(t_out), y2)], index=1, interp="BEZIER")
    lift = HOLD_Z + 0.04 - SW  # forks just over the hold's floor
    gb.keys(car, "location", [(F(t_lift0), 0.1), (F(t_lift1), lift), (F(t_in), lift), (F(t_set), lift - 0.04)], index=2,
            interp="BEZIER")
    # the pallet rides the forks (the same keys, in the world) and stays in the hold when they back out
    pal = only(gb.box("pallet28", (DOOR_X, y0 + 1.55, SW + 0.17), (1.6, 0.9, 0.12), B.M("crate")), "S28")
    py = lambda yr: yr + 1.55
    pz = lambda zc: SW + zc + 0.055 + 0.06  # on the forks' top
    gb.keys(pal, "location", [(F(a), py(y0)), (F(t_hold), py(y0)), (F(t_in), py(y1), "LINEAR"), (F(t_set + 0.1), py(y1))],
            index=1, interp="BEZIER")
    gb.keys(pal, "location", [(F(t_lift0), pz(0.1)), (F(t_lift1), pz(lift)), (F(t_in), pz(lift)),
                              (F(t_set), pz(lift - 0.04))], index=2, interp="BEZIER")
    for k in range(6):  # 0-3 on the pallet; 4-5 the next lot, waiting on the sidewalk
        if k < 4:
            cr = only(gb.box(f"crate{k}", ((k % 2 - 0.5) * 0.8, 0, 0.06 + 0.3 + (k // 2) * 0.6), (0.8, 0.8, 0.6), B.M("crate")),
                      "S28")
            cr.parent = pal
        else:
            cr = only(gb.box(f"crate{k}", (-4.55, -6.55 - (k - 4) * 0.84, SW + 0.3), (0.8, 0.8, 0.6), B.M("crate")), "S28")
        for face, off in (("-X", (-0.41, 0, 0)), ("+X", (0.41, 0, 0)), ("-Y", (0, -0.41, 0)), ("+Y", (0, 0.41, 0))):
            ox, oy, oz = off
            gb.plane(f"crate{k}.lbl{face}", (ox, oy, oz), (0.66, 0.36), B.M("sign"), parent=cr, facing=face)
            gb.text(f"crate{k}.t{face}", "COMMENTS\n2005–2023", 0.115, B.M("ink"),
                    (ox * 1.025, oy * 1.025, oz), facing=face, parent=cr)
    sign = only(gb.empty("auction28", (-3.55, -6.55, SW)), "S28")  # an A-frame board, turned to the camera
    gb.box("auction28.board", (0, 0, 0.55), (0.75, 0.05, 1.1), B.M("sign"), parent=sign)
    gb.text("auction28.t", "SIDEWALK\nAUCTION\nall data\nmust go", 0.12, B.M("ink"), (0, 0.03, 0.62), facing="+Y",
            parent=sign)
    sign.rotation_euler.z = 2.6
    # from the west, close to the shopfronts: further out, the lamp post at (-5, -6.6) stood in front of it all; from
    # the east, the truck hid the pallet
    wl = bpy.data.lights.new("S28.worklight", "SPOT")  # a work light at the hold, so the lot reads in the truck's shadow
    wl.energy, wl.spot_size, wl.spot_blend, wl.color = 260.0, math.radians(70), 0.5, (1.0, 0.92, 0.8)
    wlo = gb.link(bpy.data.objects.new("S28.worklight", wl))
    wlo.location = (DOOR_X - 2.2, -9.6, 3.4)
    wlo.rotation_euler = gb.look_rot(wlo.location, (DOOR_X, -6.6, 1.0))
    only(wlo, "S28")
    cam("S28", [(0, (-5.4, -9.75, 2.8), (-2.0, -6.4, 1.0)), (1, (-5.2, -9.75, 2.9), (-1.8, -6.1, 1.2))], lens=28)
    a, b = SP["S29"]
    # they pull up and stop, so their names read (driving through at 9 m/s, the blur took them): SEARCH at the door
    for nm, x0, x1, t1, y in (("SEARCH", -12, 4.5, a + 1.3, 3.5), ("CHAT", -20, -2.5, a + 1.6, 3.5)):
        tr = only(gb.box(f"truck.{nm}", (x0, y, 1.5), (6, 2.4, 3.0), B.M("truck")), "S29")
        gb.text(f"truck.{nm}.t", nm, 0.85, B.M("ink"), (-1.0, 1.21, 0.35), facing="+Y", parent=tr)  # on the box (x -3..1)
        gb.keys(tr, "location", [(F(a), x0, "LINEAR"), (F(a + 0.4), x0 + (x1 - x0) * 0.35), (F(t1), x1), (F(b), x1)],
                index=0, interp="BEZIER")
    # the human, on the final cut: SEARCH and CHAT "need to be brighter to read on mobile": a soft fill on the trucks'
    # near sides (y 2.3), from above the camera, for S29 only
    fl = bpy.data.lights.new("S29.fill", "AREA")
    fl.shape, fl.size, fl.size_y = "RECTANGLE", 14.0, 3.0
    fl.energy, fl.color = 700.0, (1.0, 0.95, 0.88)
    flo = gb.link(bpy.data.objects.new("S29.fill", fl))
    flo.location = (-1.0, -3.0, 4.5)
    flo.rotation_euler = gb.look_rot(flo.location, (-1.0, 2.3, 1.6))
    only(flo, "S29")
    av = only(gb.box("archivevan", (10, 3.5, 1.0), (4.0, 2.0, 2.0), B.M("van")), "S29")
    gb.text("archivevan.t", "ARCHIVE", 0.4, B.M("ink"), (0, 1.01, 0.2), facing="+Y", parent=av)
    gb.keys(av, "location", [(F(a), 10.0), (F(a + 1.0), 10.0), (F(b), 20.0)], index=0)
    only(B.person("bouncer", (11.5, 9.6, 0.16), "ink", rot_z=-math.pi / 2), "S29")
    # aimed 17 degrees further west than at v5, where CHAT stopped with its name out of frame the whole shot: now
    # CHAT's name (x -4.5) to the bouncer (x 11.5) all in, the archive van turned away at the right
    cam("S29", [(0, (-2, -5.0, 2.5), (1.2, 7.6, 1.6))], lens=24)
    c30 = only(B.ceo((12.0, 9.4, 8.15), name="ceo30"), "S30")
    a, b = SP["S30"]
    gb.keys(S["bell"], "rotation_euler", [(F(t) + d, v) for t in gb.beats_between(a, b) for d, v in ((0, 0.4), (8, -0.3))],
            index=0, interp="BEZIER")
    UNROLL = [(0, 0.0), (F(a + 0.4), 0.0), (F(a + 1.9), 1.0)]  # how much of the banner is out (0..1): 1.5 s (it was
    # 1.2 s, as a stretch; as a roll paying out it reads at 1.5)
    gb.keys(S["banner"], "scale", UNROLL, index=2)
    gb.keys(S["ticker"], '["on"]', [(0, 0.0, "CONSTANT"), (F(a + 0.4), 1.0, "CONSTANT")], interp="CONSTANT")
    # in the sheet's upper half (it was at 5.6, in the frame's bottom fifth, under the captions: the human, on the
    # final cut, "the 'IPO' banner is covered by the closed captions")
    gb.text("banner.t", "IPO", 1.5, B.M("ink"), (B.LOBBY_DOOR_X, 10.5 - 2.6, 6.4), facing="-Y")
    ipo = bpy.data.objects["banner.t"]
    only(ipo, "S30", t1=TM["duration_s"])
    # printed on the banner, revealed as the roll passes it (props.banner_roll): it used to be parented to the banner
    # and squashed with it, so the banner read as a blind stretching, not a roll paying out (the human, on the M7
    # cut: "the 'IPO' doesn't look like it's rolling out"); before that it hung in the air (the human, M4 v6)
    S["banner_unroll"] = UNROLL
    # aimed lower than at v7 (targets z 10.2 and 13.0; now 9.0 and 10.6), so the banner stays above the captions to the end
    cam("S30", [(0, (10, -3.5, 1.8), (12, 9, 9.0)), (1, (9, -5.0, 1.6), (9, 9, 10.6))], lens=24)
    # S31: the notes are on PAWN's shutter (down since S14) at eye height, close enough to read; they hold 1.2 s,
    # peel one at a time 0.22 s apart and arc into the funnel on the truck in the near lane, the camera following;
    # then up to the billboard, zooming in so its line reads
    a, b = SP["S31"]
    rn = random.Random(31)
    UNM_CLEAR = {0: (-0.24, 0.0), 1: (0.0, 0.45)}
    mouth = (2.0, -4.6, 4.35)  # over the truck's roof hatch (1 m behind its centre); the truck in the near lane
    for k in range(10):
        p0 = (-4.35 + (k % 5) * 0.68 + rn.uniform(-0.08, 0.08), B.FRONT + 0.175, (2.05 if k < 5 else 1.55) + rn.uniform(-0.07, 0.07))
        if k in UNM_CLEAR:  # off "UNDER NEW MANAGEMENT" (x -4.33..-3.28, z 1.73..2.07): one above it, one to its side
            p0 = (p0[0] + UNM_CLEAR[k][0], p0[1], p0[2] + UNM_CLEAR[k][1])
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
    # the words in the square's front half, read from the camera (it looks from +Y), the Dev in the back half: at v5
    # they lay under his feet, upside down to us
    yl = only(gb.text("yourland", "YOUR LAND", 0.22, B.M("sign"), (cx, cy + 0.42, 0.155), facing="+Z"), "S33")
    yl.rotation_euler.z += math.pi
    d33 = only(B.dev((cx, cy - 0.3, 0.16)), "S33")
    sing(d33, "S33")
    cam("S33", [(0, (cx, cy + 3.2, 1.7), (cx, cy, 0.75)), (1, (cx, cy + 5, 20), (cx, cy, 0))], lens=28)

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
    # M5: he faces each camera (rot_z 200 turned him 50 degrees off it; S42-S43 are lip-synced): the figure looks
    # down -Y turned by rot_z, so facing the camera at (dx, dy) from him is atan2(dx, -dy)
    for sid, yaw in (("S41", 147), ("S42", 151), ("S43", 154)):
        r = only(B.dev((-29.5, -7.4, 0.16), rot_z=math.radians(yaw), name=f"rapper.{sid}"), sid)
        sing(r, sid)
    cam("S41", [(0, (-24, 0, 2.2), (-29.5, -7.4, 1.4)), (1, (-25, -2, 1.9), (-29.5, -7.4, 1.4))], lens=30)
    cam("S42", [(0, (-27.6, -4.4, 1.6), (-29.5, -7.4, 1.4))], lens=40)
    cam("S43", [(0, (-28.9, -6.3, 1.6), (-29.5, -7.4, 1.58)), (1, (-29.0, -6.5, 1.6), (-29.5, -7.4, 1.58))], lens=50)
    cam("S44", [(0, (9, -30, 30), (9, 12.5, 76)), (1, (9, -26, 32), (9, 12.5, 76))], lens=45)
    # M5: 1.2 m inside the door, on the shop floor (0.3 m in, the photoreal take read him as standing on the sidewalk,
    # so the shutter seemed to come down in front of a man outside it)
    hm = only(B.hypeman((sh_x[6] + 1.9, B.FRONT - 1.2, 0.16)), "S45")
    S["slam"].setdefault(6, []).extend([(SP["S45"][0] - 0.05, 0.0), (SP["S45"][1], 1.0)])
    gb.hide_between(bpy.data.objects["shop6.door"], *SP["S45"])
    bl = bpy.data.lights.new("hype.back", "AREA")
    bl.energy, bl.size, bl.color = 400, 1.5, (1.0, 0.85, 0.6)
    blo = only(gb.link(bpy.data.objects.new("hype.back", bl)), "S45")
    blo.location, blo.rotation_euler = (sh_x[6] + 1.9, B.FRONT - 3.4, 1.5), (math.radians(-90), 0, 0)
    # M5: from x + 1.5 a sidewalk fixture stood 0.85 m in front of the lens, over the doorway; a metre east clears it
    cam("S45", [(0, (sh_x[6] + 2.6, -5.5, 1.5), (sh_x[6] + 1.9, -10, 1.3))], lens=40)

    # ---- outro (S47-S48b): the payphone; the crane over a block of doormen, keypads and REC lights; the open grave
    cam("S47", [(0, (-30.6, -7.4, 1.3), (-31.56, -8.45, 0.88)), (1, (-30.9, -7.7, 1.1), (-31.56, -8.45, 0.88))], lens=40)
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
    gb.key_vec(ph, "location", S["phone_loc"] + [(F(a - 0.1), (tx - 0.27, ty - 0.2, tz + 0.005))])  # M6: on the table by the badge (it lay across the tray's edge)
    gb.keys(ph, "rotation_euler", S["phone_rot"] + [(F(a - 0.1), math.radians(-90))], index=0)
    # M6: from the table to the phone and the badge (from the M3 framing the phone's notice was 70 px wide, unreadable):
    # the push ends close over them
    cam("S49", [(0, (tx + 0.5, ty - 1.0, tz + 0.7), (tx - 0.05, ty - 0.15, tz)),
                (0.35, (tx + 0.3, ty - 0.8, tz + 0.55), (tx - 0.15, ty - 0.17, tz)),
                (1, (tx - 0.16, ty - 0.46, tz + 0.27), (tx - 0.28, ty - 0.13, tz))], lens=35)
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
