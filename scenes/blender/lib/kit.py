"""The detail pass's model kit: the CC0 models from scripts/fetch_models.py (assets/models/<id>/<id>.gltf), each
imported once and joined into one mesh with its own materials, origin at the bottom centre, +Y the model's back
(Poly Haven models face -Y... or +Y; `yaw` on place() turns them). Every placed copy shares that mesh, so a street's
worth of hydrants costs one mesh.

  place(name, aid, loc, rot_z, scale, parent)   a new object with the model's mesh
  fit(aid, size)                                the uniform scale that fits the model into size (x, y, z), metres
  swap(o, aid, ...)                             a grey-box object takes the model's mesh in place of its box, keeping
                                                its name, animation and visibility keys (the shots stay unchanged)
"""
import math

import bpy
from mathutils import Matrix, Vector

import gb

MODELS = gb.ROOT / "assets" / "models"
_MESH = {}


def load(aid):
    if aid in _MESH:
        return _MESH[aid]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(MODELS / aid / f"{aid}.gltf"))
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new(f"kit.{aid}")
    import bmesh
    bm = bmesh.new()
    mats = []
    for o in meshes:
        tmp = o.data.copy()
        tmp.transform(o.matrix_world)
        base = len(mats)
        for m in tmp.materials:
            mats.append(m)
        for p in tmp.polygons:
            p.material_index += base
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    lo = Vector((min(v.co.x for v in bm.verts), min(v.co.y for v in bm.verts), min(v.co.z for v in bm.verts)))
    hi = Vector((max(v.co.x for v in bm.verts), max(v.co.y for v in bm.verts), max(v.co.z for v in bm.verts)))
    off = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for v in bm.verts:
        v.co -= off
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    for o in new:
        bpy.data.objects.remove(o)
    me["dims"] = list(hi - lo)
    _MESH[aid] = me
    return me


def dims(aid):
    return Vector(load(aid)["dims"])


def fit(aid, size):
    d = dims(aid)
    return min(s / max(c, 1e-6) for s, c in zip(size, d) if s)


def place(name, aid, loc, rot_z=0.0, scale=1.0, parent=None, rot=None):
    o = gb.link(bpy.data.objects.new(name, load(aid)), parent)
    o.location = loc
    o.rotation_euler = rot if rot else (0, 0, rot_z)
    o.scale = (scale,) * 3 if isinstance(scale, (int, float)) else scale
    return o


def swap(o, aid, scale=1.0, offset=(0, 0, 0), rot=(0, 0, 0)):
    """o keeps its object (name, transform, animation, visibility); its mesh becomes the model's, scaled, turned and
    offset in o's own space (the grey-box boxes have their origin at their centre)."""
    me = load(aid).copy()
    me.name = f"{o.name}.kit"
    me.transform(Matrix.Translation(offset) @ Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y")
                 @ Matrix.Rotation(rot[0], 4, "X") @ Matrix.Scale(scale, 4))
    o.data = me
    return o


def mesh_swap(o, me):
    """o takes a mesh built elsewhere (a modelled prop), keeping its object and keys."""
    o.data = me
    return o
