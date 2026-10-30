"""A procedural mesh builder for the detail pass's modelled props (sets/props.py): many parts, each with its own
material, built into one bmesh and written to one mesh. Every part takes a centre and an optional rotation (radians,
XYZ); sizes are full sizes, metres.

  m = MK(); m.box(...); m.cyl(...); m.lathe(...); m.tube(...); me = m.mesh("name")
"""
import math

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

import gb


def _mat4(c=(0, 0, 0), rot=(0, 0, 0), s=(1, 1, 1)):
    return Matrix.Translation(c) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*s, 1))


class MK:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.verify()
        self.mats = []

    def _mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _finish(self, verts, m, smooth=False, faces=None):
        if faces is None:
            faces = {f for v in verts for f in v.link_faces}
        mi = self._mi(m)
        for f in faces:
            f.material_index = mi
            f.smooth = smooth
        return faces

    def _bevel(self, vs, m, bevel, seg, smooth):
        faces = {f for v in vs for f in v.link_faces}
        if bevel:
            edges = list({e for v in vs for e in v.link_edges})
            r2 = bmesh.ops.bevel(self.bm, geom=edges + list(vs), offset=bevel, segments=seg, profile=0.5,
                                 affect="EDGES", clamp_overlap=True)
            faces = {f for f in faces if f.is_valid} | set(r2["faces"])
        return self._finish(None, m, smooth or bevel > 0, faces=faces)

    def box(self, c, s, m, rot=(0, 0, 0), bevel=0.0, seg=2, smooth=False):
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=_mat4(c, rot, s))
        vs = r["verts"]
        return self._bevel(vs, m, bevel, seg, smooth)

    def cyl(self, c, r, h, m, axis="Z", n=24, r2=None, rot=None, smooth=True, caps=True):
        rot = rot or {"Z": (0, 0, 0), "X": (0, math.pi / 2, 0), "Y": (math.pi / 2, 0, 0)}[axis]
        res = bmesh.ops.create_cone(self.bm, cap_ends=caps, cap_tris=False, segments=n, radius1=r,
                                    radius2=r if r2 is None else r2, depth=h, matrix=_mat4(c, rot))
        faces = self._finish(res["verts"], m, smooth)
        if smooth:  # flat caps on a smooth side
            for f in faces:
                if len(f.verts) > 4:
                    f.smooth = False
        return faces

    def sphere(self, c, r, m, s=(1, 1, 1), rot=(0, 0, 0), u=16, v=10):
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=u, v_segments=v, radius=r, matrix=_mat4(c, rot, s))
        return self._finish(res["verts"], m, True)

    def torus(self, c, R, r, m, rot=(0, 0, 0), n=24, k=8, arc=2 * math.pi):
        M4 = _mat4(c, rot)
        full = arc >= 2 * math.pi - 1e-6
        rings = n if full else n + 1
        rows = []
        for i in range(rings):
            a = arc * i / n
            ring = []
            for j in range(k):
                b = 2 * math.pi * j / k
                p = Vector(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
                ring.append(self.bm.verts.new(M4 @ p))
            rows.append(ring)
        for i in range(n):
            a_, b_ = rows[i], rows[(i + 1) % rings]
            for j in range(k):
                self.bm.faces.new((a_[j], a_[(j + 1) % k], b_[(j + 1) % k], b_[j]))
        return self._finish([v for row in rows for v in row], m, True)

    def lathe(self, prof, m, c=(0, 0, 0), rot=(0, 0, 0), n=32, smooth=True):
        """A surface of revolution about local Z: prof is [(radius, z), ...] from one end to the other."""
        M4 = _mat4(c, rot)
        rows = [[self.bm.verts.new(M4 @ Vector((r * math.cos(2 * math.pi * j / n), r * math.sin(2 * math.pi * j / n), z)))
                 for j in range(n)] for r, z in prof]
        for a_, b_ in zip(rows, rows[1:]):
            for j in range(n):
                self.bm.faces.new((a_[j], a_[(j + 1) % n], b_[(j + 1) % n], b_[j]))
        return self._finish([v for row in rows for v in row], m, smooth)

    def tube(self, pts, r, m, k=10, rib=0.0, rib_n=0):
        """A tube along a polyline (r, or a ribbed hose: rib_n ribs of depth rib over its length)."""
        pts = [Vector(p) for p in pts]
        # resample evenly
        L = [0.0]
        for a, b in zip(pts, pts[1:]):
            L.append(L[-1] + (b - a).length)
        n = max(8, rib_n * 2 if rib_n else int(L[-1] / 0.03))
        samp = []
        for i in range(n + 1):
            t = L[-1] * i / n
            j = max(0, min(len(pts) - 2, next((q for q in range(len(L) - 1) if L[q + 1] >= t), len(pts) - 2)))
            u = (t - L[j]) / max(1e-9, L[j + 1] - L[j])
            samp.append(pts[j].lerp(pts[j + 1], u))
        rows = []
        up = Vector((0, 0, 1))
        for i, p in enumerate(samp):
            tan = (samp[min(i + 1, n)] - samp[max(i - 1, 0)]).normalized()
            if abs(tan.dot(up)) > 0.95:
                up = Vector((1, 0, 0))
            x = tan.cross(up).normalized()
            y = x.cross(tan).normalized()
            rr = r + (rib * (1 if i % 2 else -1) if rib_n else 0.0)
            rows.append([self.bm.verts.new(p + rr * (math.cos(2 * math.pi * j / k) * x + math.sin(2 * math.pi * j / k) * y))
                         for j in range(k)])
        for a_, b_ in zip(rows, rows[1:]):
            for j in range(k):
                self.bm.faces.new((a_[j], a_[(j + 1) % k], b_[(j + 1) % k], b_[j]))
        return self._finish([v for row in rows for v in row], m, True)

    def prism(self, outline, depth, m, c=(0, 0, 0), rot=(0, 0, 0), bevel=0.0):
        """An outline [(x, z), ...] (counter-clockwise seen from -Y) extruded along Y by depth, centred."""
        M4 = _mat4(c, rot)
        f = [self.bm.verts.new(M4 @ Vector((x, -depth / 2, z))) for x, z in outline]
        b = [self.bm.verts.new(M4 @ Vector((x, depth / 2, z))) for x, z in outline]
        nf = len(outline)
        faces = [self.bm.faces.new(f), self.bm.faces.new(list(reversed(b)))]
        for j in range(nf):
            faces.append(self.bm.faces.new((f[j], b[j], b[(j + 1) % nf], f[(j + 1) % nf])))
        return self._bevel(f + b, m, bevel, 2, False)

    def quad(self, c, size, m, facing="-Y", rot=(0, 0, 0), flip_u=False):
        """A UV-mapped rectangle (a printed surface): seen from its facing side, UV (0,0) is bottom left."""
        w, h = size[0] / 2, size[1] / 2
        corners = {"-Y": [(-w, 0, -h), (w, 0, -h), (w, 0, h), (-w, 0, h)],
                   "+Y": [(w, 0, -h), (-w, 0, -h), (-w, 0, h), (w, 0, h)],
                   "+X": [(0, -w, -h), (0, w, -h), (0, w, h), (0, -w, h)],
                   "-X": [(0, w, -h), (0, -w, -h), (0, -w, h), (0, w, h)],
                   "+Z": [(-w, -h, 0), (w, -h, 0), (w, h, 0), (-w, h, 0)]}[facing]
        M4 = _mat4(c, rot)
        vs = [self.bm.verts.new(M4 @ Vector(p)) for p in corners]
        f = self.bm.faces.new(vs)
        for loop, uv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
            loop[self.uv].uv = (1 - uv[0], uv[1]) if flip_u else uv
        return self._finish(vs, m)

    def mesh(self, name):
        me = bpy.data.meshes.new(name)
        self.bm.normal_update()
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        return me


def img_mat(name, path, rough=0.8, alpha=False, emit=0.0):
    """A material showing an image on the UV-mapped quads."""
    if name in gb._MATS:
        return gb._MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(path), check_existing=True)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if alpha:
        m.surface_render_method = "DITHERED"
        nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    if emit:
        nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    gb._MATS[name] = m
    return m


def empty_mesh(name):
    return bpy.data.meshes.new(name)
